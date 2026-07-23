#!/usr/bin/env python3
"""Fetch RETE individual scholars via Shiny foundPersons DataTables API."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
import urllib3

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CONFIG, DATA_RAW, OUTPUT_LOGS
from _rete_shiny_fetch import api_cfg
from _utils import log, normalize_city

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

OUT_RAW = DATA_RAW / "rete_scholars_individual.csv"
CHECKPOINT = DATA_RAW / "rete_scholars_api_checkpoint.json"
OUT_JSONL = DATA_RAW / "rete_scholars_api_pages.jsonl"

COLUMNS = [
    (0, " "),
    (1, "PKey"),
    (2, "PName"),
    (3, "FirstName"),
    (4, "AlternativeName"),
    (5, "BirthPlace"),
    (6, "DeathPlace"),
    (7, "YearBorn"),
    (8, "YearDied"),
    (9, "Wikipedia"),
    (10, "VIAF"),
]

FIELD_NAMES = [
    "row_id",
    "pkey",
    "pname",
    "first_name",
    "alt_name",
    "birth_place",
    "death_place",
    "birth_year",
    "death_year",
    "wikipedia",
    "viaf",
]


def _cfg() -> dict:
    return api_cfg()


def _build_body(draw: int, start: int, length: int) -> str:
    parts = [
        f"draw={draw}",
        f"start={start}",
        f"length={length}",
        "search[value]=",
        "search[regex]=false",
        "search[caseInsensitive]=true",
        "search[smart]=true",
        "escape=false",
    ]
    for i, (data_idx, name) in enumerate(COLUMNS):
        parts += [
            f"columns[{i}][data]={data_idx}",
            f"columns[{i}][name]={name}",
            f"columns[{i}][searchable]=true",
            f"columns[{i}][orderable]=false",
            f"columns[{i}][search][value]=",
            f"columns[{i}][search][regex]=false",
        ]
    return "&".join(parts)


def _strip_html(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    text = str(val)
    if text in ("NA", "nan", "None"):
        return ""
    m = re.search(r"href=['\"]([^'\"]+)['\"]", text)
    return m.group(1) if m else text


def _looks_like_place(val: str) -> bool:
    return bool(re.search(r"[A-Z]{3}$", str(val).strip()))


def _place_to_city(place: str) -> str:
    if not place or place in ("NA", "nan"):
        return ""
    base = re.sub(r"[A-Z]{3}$", "", str(place).strip())
    return normalize_city(base)


def _rows_to_df(rows: list[list]) -> pd.DataFrame:
    records = []
    for row in rows:
        rec = {FIELD_NAMES[i]: row[i] if i < len(row) else None for i in range(len(FIELD_NAMES))}
        rec["birth_year"] = pd.to_numeric(rec.get("birth_year"), errors="coerce")
        rec["death_year"] = pd.to_numeric(rec.get("death_year"), errors="coerce")
        rec["wikipedia"] = _strip_html(rec.get("wikipedia"))
        rec["viaf"] = _strip_html(rec.get("viaf"))
        rec["city"] = _place_to_city(str(rec.get("birth_place") or ""))
        rec["name"] = rec.get("alt_name") or ""
        if not rec["name"] or rec["name"] in ("NA", "nan"):
            fn = rec.get("first_name") or ""
            rec["name"] = fn if fn and not _looks_like_place(fn) else (rec.get("pname") or "")
        if rec["name"] in ("NA", "nan"):
            rec["name"] = ""
        records.append(rec)
    return pd.DataFrame(records)


def _load_checkpoint() -> int:
    if CHECKPOINT.exists():
        return int(json.loads(CHECKPOINT.read_text()).get("next_start", 0))
    return 0


def _save_checkpoint(next_start: int, total: int) -> None:
    CHECKPOINT.write_text(json.dumps({"next_start": next_start, "records_total": total}, indent=2))


def fetch_page(session: requests.Session, url: str, draw: int, start: int, length: int) -> dict:
    r = session.post(
        url,
        data=_build_body(draw, start, length),
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def main() -> None:
    cfg = _cfg()
    session_id = cfg.get("session_id", "").strip()
    nonce = cfg.get("nonce", "").strip()
    if not session_id:
        raise ValueError("rete_api.yaml: set session_id (from browser curl URL)")

    base = cfg.get("base_url", "https://shiny-lidam.sipr.ucl.ac.be/scholars1").rstrip("/")
    page_size = int(cfg.get("page_size", 100))
    sleep_s = float(cfg.get("sleep_seconds", 0.3))
    max_pages = int(__import__("os").environ.get("RETE_MAX_PAGES", "0"))

    nonce_q = f"&nonce={nonce}" if nonce else ""
    url = f"{base}/session/{session_id}/dataobj/foundPersons?w={nonce_q}"

    http = requests.Session()
    http.verify = False

    start = _load_checkpoint()
    draw = start // page_size + 1
    all_frames: list[pd.DataFrame] = []

    if OUT_RAW.exists() and start > 0:
        existing = pd.read_csv(OUT_RAW, low_memory=False)
        all_frames.append(existing)
        log(f"Resume from offset {start} ({len(existing)} rows on disk)", OUTPUT_LOGS / "fetch.log")

    probe = fetch_page(http, url, draw, start, page_size)
    total = int(probe.get("recordsTotal", 0))
    if total == 0:
        raise RuntimeError("API returned 0 records — session expired? Update config/rete_api.yaml")

    log(f"RETE API: {total} scholars, page_size={page_size}, start={start}", OUTPUT_LOGS / "fetch.log")

    pages_done = 0
    while start < total:
        payload = probe if pages_done == 0 else fetch_page(http, url, draw, start, page_size)
        rows = payload.get("data") or []
        if not rows:
            log(f"Empty page at start={start} — session may have expired", OUTPUT_LOGS / "fetch.log")
            break

        df = _rows_to_df(rows)
        all_frames.append(df)

        with OUT_JSONL.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"start": start, "n": len(rows)}) + "\n")

        start += len(rows)
        draw += 1
        pages_done += 1
        _save_checkpoint(start, total)

        if pages_done % 20 == 0 or start >= total:
            out = pd.concat(all_frames, ignore_index=True)
            out.drop_duplicates(subset=["pkey"], keep="last").to_csv(OUT_RAW, index=False)
            log(f"  saved {len(out)} rows ({start}/{total})", OUTPUT_LOGS / "fetch.log")

        if max_pages and pages_done >= max_pages:
            log(f"Stopped at RETE_MAX_PAGES={max_pages}", OUTPUT_LOGS / "fetch.log")
            break

        if start < total:
            time.sleep(sleep_s)

    if all_frames:
        out = pd.concat(all_frames, ignore_index=True).drop_duplicates(subset=["pkey"], keep="last")
        out.to_csv(OUT_RAW, index=False)
        log(f"RETE API done: {len(out)} scholars -> {OUT_RAW}", OUTPUT_LOGS / "fetch.log")
        if start >= total:
            CHECKPOINT.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
