#!/usr/bin/env python3
"""Fetch Studium Parisiense prosopography via public advanced-search API."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

API_BASE = "http://studium-parisiense.univ-paris1.fr/api/prosopography/search/advanced"
ROWS_PER_PAGE = 100
MIN_RECORDS = 25_000
BIN_WIDTH = 10

BASE_BODY = {
    "activityMediane": {"from": None, "to": None},
    "activity": {
        "start": {"from": None, "to": None},
        "end": {"from": None, "to": None},
    },
    "status": [],
    "sexe": [],
    "graph": False,
    "grade": None,
    "discipline": None,
    "name": None,
    "prosopography": [
        {
            "section": None,
            "subSection": None,
            "operator": "AND",
            "matchType": None,
            "value": None,
        }
    ],
}

OUT_CANDIDATES = [
    DATA_RAW / "studium_persons.jsonl",
    ROOT.parent / "download_data" / "studium_persons.jsonl",
]
CHECKPOINT = DATA_RAW / "studium_fetch_checkpoint.json"


def activity_bins() -> list[tuple[int, int]]:
    bins = []
    year = 1100
    while year <= 1690:
        bins.append((year, year + BIN_WIDTH - 1))
        year += BIN_WIDTH
    return bins


def _search_body(year_from: int, year_to: int) -> dict:
    body = json.loads(json.dumps(BASE_BODY))
    body["activityMediane"] = {"from": year_from, "to": year_to}
    return body


def _post_page(body: dict, page: int) -> tuple[list[dict], int | None]:
    url = f"{API_BASE}?page={page}&rows={ROWS_PER_PAGE}"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "eyeglasses-hypothesis/1.0 (research pipeline)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        total = resp.headers.get("X-Total-Count")
        records = json.load(resp)
    return records, int(total) if total else None


def _load_checkpoint() -> set[str]:
    if not CHECKPOINT.exists():
        return set()
    data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    return set(data.get("completed_bins", []))


def _save_checkpoint(completed_bins: set[str]) -> None:
    CHECKPOINT.write_text(
        json.dumps({"completed_bins": sorted(completed_bins)}, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_existing_ids(dest: Path) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    if not dest.exists():
        return by_id
    with dest.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rid = rec.get("_id")
            if rid:
                by_id[rid] = rec
    return by_id


def _write_all(dest: Path, by_id: dict[str, dict]) -> None:
    with dest.open("w", encoding="utf-8") as out:
        for rec in by_id.values():
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _fetch_bin(year_from: int, year_to: int) -> list[dict]:
    body = _search_body(year_from, year_to)
    page = 1
    total_expected: int | None = None
    collected: list[dict] = []

    while True:
        for attempt in range(8):
            try:
                records, total = _post_page(body, page)
                break
            except urllib.error.HTTPError as exc:
                if exc.code in {429, 500, 502, 503, 504} and attempt < 7:
                    wait = min(60, 3 * (2**attempt))
                    label = f"{year_from}-{year_to}"
                    log(
                        f"Studium bin {label} page {page} HTTP {exc.code}, retry in {wait}s",
                        OUTPUT_LOGS / "fetch.log",
                    )
                    time.sleep(wait)
                    continue
                raise
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt < 7:
                    time.sleep(min(30, 2**attempt))
                    continue
                raise

        if total_expected is None and total is not None:
            total_expected = total
            if total_expected == 0:
                return []

        if not records:
            break

        collected.extend(records)
        label = f"{year_from}-{year_to}"
        log(
            f"Studium bin {label} page {page}: +{len(records)} ({len(collected)}/{total_expected or '?'})",
            OUTPUT_LOGS / "fetch.log",
        )

        if len(records) < ROWS_PER_PAGE:
            break
        if total_expected and len(collected) >= total_expected:
            break
        page += 1
        time.sleep(0.35)

    return collected


def fetch_all(dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    by_id = _load_existing_ids(dest)
    completed_bins = _load_checkpoint()

    for year_from, year_to in activity_bins():
        label = f"{year_from}-{year_to}"
        if label in completed_bins:
            continue
        for rec in _fetch_bin(year_from, year_to):
            rid = rec.get("_id")
            if rid:
                by_id[rid] = rec
        completed_bins.add(label)
        _save_checkpoint(completed_bins)
        _write_all(dest, by_id)
        log(f"Studium checkpoint {label}: {len(by_id)} unique total", OUTPUT_LOGS / "fetch.log")

    return len(by_id)


def main() -> None:
    dest = OUT_CANDIDATES[0]
    mirror = OUT_CANDIDATES[1]

    if dest.exists() and dest.stat().st_size > 1_000_000:
        n_lines = sum(1 for _ in dest.open(encoding="utf-8"))
        completed_bins = _load_checkpoint()
        if n_lines >= MIN_RECORDS and len(completed_bins) >= len(activity_bins()):
            log(f"Studium cache hit: {n_lines} records in {dest.name}", OUTPUT_LOGS / "fetch.log")
            if not mirror.exists() or mirror.stat().st_size != dest.stat().st_size:
                mirror.parent.mkdir(parents=True, exist_ok=True)
                mirror.write_bytes(dest.read_bytes())
            return

    n = fetch_all(dest)
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_bytes(dest.read_bytes())
    log(f"Studium fetched {n} unique records -> {dest}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
