"""Shared Shiny DataTables fetcher for RETE (foundPersons / foundActivities / …)."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd
import requests
import urllib3
import yaml

from _paths import CONFIG, DATA_RAW, OUTPUT_LOGS
from _utils import load_yaml, log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def api_cfg() -> dict:
    cfg = load_yaml("rete_api.yaml")
    local = CONFIG / "rete_api.local.yaml"
    if local.exists():
        with open(local, encoding="utf-8") as f:
            overlay = yaml.safe_load(f) or {}
        cfg.update({k: v for k, v in overlay.items() if v not in (None, "")})
    cfg["session_id"] = os.environ.get("RETE_SESSION_ID", cfg.get("session_id", ""))
    cfg["nonce"] = os.environ.get("RETE_NONCE", cfg.get("nonce", ""))
    return cfg


def build_body(draw: int, start: int, length: int, column_names: list[str]) -> str:
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
    for i, name in enumerate(column_names):
        parts += [
            f"columns[{i}][data]={i % max(len(column_names), 1)}",
            f"columns[{i}][name]={name}",
            f"columns[{i}][searchable]=true",
            f"columns[{i}][orderable]=false",
            f"columns[{i}][search][value]=",
            f"columns[{i}][search][regex]=false",
        ]
    return "&".join(parts)


def fetch_page(
    http: requests.Session,
    url: str,
    draw: int,
    start: int,
    length: int,
    column_names: list[str],
) -> dict:
    r = http.post(
        url,
        data=build_body(draw, start, length, column_names),
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def rows_to_df(rows: list[list], field_names: list[str]) -> pd.DataFrame:
    records = []
    for row in rows:
        rec = {field_names[i]: row[i] if i < len(row) else None for i in range(len(field_names))}
        records.append(rec)
    return pd.DataFrame(records)


def fetch_datatable(
    *,
    dataobj: str,
    out_csv: Path,
    column_names: list[str],
    field_names: list[str],
    dedupe_cols: list[str] | None = None,
    checkpoint_path: Path | None = None,
) -> pd.DataFrame:
    cfg = api_cfg()
    session_id = str(cfg.get("session_id", "")).strip()
    if not session_id:
        raise ValueError("config/rete_api.yaml: set session_id from browser curl")

    base = str(cfg.get("base_url", "https://shiny-lidam.sipr.ucl.ac.be/scholars1")).rstrip("/")
    nonce = str(cfg.get("nonce", "")).strip()
    page_size = int(cfg.get("page_size", 100))
    sleep_s = float(cfg.get("sleep_seconds", 0.3))
    max_pages = int(os.environ.get("RETE_MAX_PAGES", "0"))

    nonce_q = f"&nonce={nonce}" if nonce else ""
    url = f"{base}/session/{session_id}/dataobj/{dataobj}?w={nonce_q}"

    ckpt = checkpoint_path or DATA_RAW / f"rete_api_{dataobj}_checkpoint.json"
    http = requests.Session()
    http.verify = False

    start = 0
    if ckpt.exists():
        start = int(json.loads(ckpt.read_text()).get("next_start", 0))

    draw = start // page_size + 1
    frames: list[pd.DataFrame] = []
    if out_csv.exists() and start > 0:
        frames.append(pd.read_csv(out_csv, low_memory=False))

    probe = fetch_page(http, url, draw, start, page_size, column_names)
    total = int(probe.get("recordsTotal", 0))
    if total == 0:
        raise RuntimeError(
            f"{dataobj}: 0 records — session expired? Update config/rete_api.yaml"
        )

    log(f"RETE {dataobj}: {total} rows, start={start}", OUTPUT_LOGS / "fetch.log")
    pages_done = 0
    while start < total:
        payload = probe if pages_done == 0 else fetch_page(
            http, url, draw, start, page_size, column_names
        )
        rows = payload.get("data") or []
        if not rows:
            log(f"{dataobj}: empty page at {start}", OUTPUT_LOGS / "fetch.log")
            break

        frames.append(rows_to_df(rows, field_names))
        start += len(rows)
        draw += 1
        pages_done += 1
        ckpt.write_text(json.dumps({"next_start": start, "records_total": total}, indent=2))

        if pages_done % 20 == 0 or start >= total:
            out = pd.concat(frames, ignore_index=True)
            if dedupe_cols:
                out = out.drop_duplicates(subset=dedupe_cols, keep="last")
            out.to_csv(out_csv, index=False)
            log(f"  {dataobj}: saved {len(out)} ({start}/{total})", OUTPUT_LOGS / "fetch.log")

        if max_pages and pages_done >= max_pages:
            break
        if start < total:
            time.sleep(sleep_s)

    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    if dedupe_cols:
        out = out.drop_duplicates(subset=dedupe_cols, keep="last")
    out.to_csv(out_csv, index=False)
    log(f"RETE {dataobj} done: {len(out)} -> {out_csv}", OUTPUT_LOGS / "fetch.log")
    if start >= total:
        ckpt.unlink(missing_ok=True)
    return out
