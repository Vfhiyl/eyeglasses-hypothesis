#!/usr/bin/env python3
"""Fetch Wikidata intellectuals via proxy — small pages, persist every page.

Design goals:
  - Small scope per request (death-year window × small LIMIT)
  - Persist immediately after each successful page (no all-or-nothing)
  - Resume from progress file; never require one-shot completion
  - TLS + SPARQL via Python stdlib (Let's Encrypt YE1 required); no curl
  - Use only the provided proxy list (env + working_https_proxies_wikidata.txt);
    retry within that list. Does NOT hunt or discover proxies.

Proxies often return SPARQL XML instead of CSV — we parse XML.

Provide proxies separately, e.g.:
  .venv/bin/python scripts/check_https_proxy_cert.py --host query.wikidata.org \\
      --need 3 --sparql-check --out outputs/tables/working_https_proxies_wikidata.txt
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _sparql_xml import is_sparql_xml, sparql_xml_to_dataframe
from _utils import log
from _wikidata_http import post_sparql

DOWNLOAD_DIR = ROOT.parent / "download_data"
OUT = DOWNLOAD_DIR / "wikidata_european_intellectuals.csv"
WIKIDATA_PROXY_FILE = OUTPUT_TABLES / "working_https_proxies_wikidata.txt"

OCCUPATIONS = [
    ("philosopher", "Q4964182"),
    ("theologian", "Q333634"),
    ("mathematician", "Q170790"),
    ("historian", "Q201788"),
    ("scholar", "Q1622272"),
    ("university_teacher", "Q82594"),
    ("professor", "Q121594"),
    ("writer", "Q36180"),
    ("physicist", "Q169470"),
]

# Small pages — prefer many short successes over one big timeout.
PAGE_SIZE = 150
# Half-century death windows keep each SPARQL cheap.
WINDOW_YEARS = 50
DEATH_MIN = 1100
DEATH_MAX = 1850
HTTP_TIMEOUT = 90
PAGE_SLEEP = 1.5
PROXY_FAIL_SLEEP = 0.8
# How many full passes over the provided proxy list per page before giving up.
PAGE_RETRIES = 3


def _windows() -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    y = DEATH_MIN
    while y < DEATH_MAX:
        y1 = min(y + WINDOW_YEARS, DEATH_MAX + 1)
        out.append((y, y1 - 1))  # inclusive death years
        y = y1
    return out


def _sparql_page(wd_id: str, death_lo: int, death_hi: int, offset: int) -> str:
    return f"""
SELECT DISTINCT ?person ?personLabel ?birth ?death ?birthplaceLabel WHERE {{
  ?person wdt:P31 wd:Q5;
          wdt:P106 wd:{wd_id};
          wdt:P570 ?death.
  FILTER(YEAR(?death) >= {death_lo} && YEAR(?death) <= {death_hi})
  OPTIONAL {{ ?person wdt:P569 ?birth. }}
  OPTIONAL {{ ?person wdt:P19 ?birthplace. }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
ORDER BY ?person
LIMIT {PAGE_SIZE}
OFFSET {offset}
"""


def _load_proxy_pool() -> list[str]:
    """Load provided proxies only: HTTPS_PROXY env + working_https_proxies_wikidata.txt."""
    pool: list[str] = []
    env = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    if env:
        pool.append(env.replace("https://", "http://"))
    if WIKIDATA_PROXY_FILE.exists():
        for line in WIKIDATA_PROXY_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                hostport = line.split("\t", 1)[0]
                if ":" in hostport:
                    pool.append(f"http://{hostport}")
    seen: set[str] = set()
    return [p for p in pool if not (p in seen or seen.add(p))]  # type: ignore[func-returns-value]


def _is_valid_csv(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 80:
        return False
    head = path.read_bytes()[:512].lstrip()
    if head.startswith(b"<?xml") or head.startswith(b"<sparql"):
        return False
    first = head.split(b"\n", 1)[0].decode("utf-8", errors="replace").lower()
    return "person" in first and "," in first


def _progress_path(suffix: str) -> Path:
    return DOWNLOAD_DIR / f"wikidata_european_{suffix}.progress.json"


def _load_progress(suffix: str) -> dict:
    p = _progress_path(suffix)
    if not p.exists():
        return {"completed_windows": [], "current": None}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"completed_windows": [], "current": None}


def _save_progress(suffix: str, data: dict) -> None:
    _progress_path(suffix).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _post_sparql(query: str, dest: Path, proxy: str | None) -> bool:
    """Fetch one SPARQL page via Python TLS (YE1 required). No curl."""
    ok, detail = post_sparql(
        query,
        dest,
        proxy=proxy,
        timeout=HTTP_TIMEOUT,
        require_ye1=True,
    )
    if not ok:
        log(f"sparql {dest.name} via {proxy or 'direct'}: {detail}", OUTPUT_LOGS / "fetch.log")
        return False
    complete = is_sparql_xml(dest) and b"</sparql>" in dest.read_bytes()[-512:]
    if complete or _is_valid_csv(dest):
        log(f"sparql OK {dest.name} via {proxy or 'direct'} ({detail})", OUTPUT_LOGS / "fetch.log")
        return True
    log(f"sparql bad body {dest.name} via {proxy or 'direct'}: {detail}", OUTPUT_LOGS / "fetch.log")
    return False


def _download_page(query: str, tmp: Path) -> bool:
    """Try the provided proxy list (with retries). Never hunts for new proxies."""
    pool = _load_proxy_pool()
    if not pool:
        log(
            f"No proxies configured — set https_proxy or fill {WIKIDATA_PROXY_FILE.name}",
            OUTPUT_LOGS / "fetch.log",
        )
        return False
    for attempt in range(1, PAGE_RETRIES + 1):
        for proxy in pool:
            if _post_sparql(query, tmp, proxy):
                return True
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            time.sleep(PROXY_FAIL_SLEEP)
        if attempt < PAGE_RETRIES:
            log(
                f"All provided proxies failed — retry pass {attempt + 1}/{PAGE_RETRIES}",
                OUTPUT_LOGS / "fetch.log",
            )
            # Reload in case the user updated the list while we wait.
            pool = _load_proxy_pool() or pool
            time.sleep(1.0)
    return False


def _read_page(tmp: Path) -> pd.DataFrame | None:
    if _is_valid_csv(tmp):
        return pd.read_csv(tmp)
    if is_sparql_xml(tmp):
        return sparql_xml_to_dataframe(tmp)
    return None


def _persist_page(dest: Path, page_df: pd.DataFrame, occupation: str) -> int:
    """Append page to occupation CSV immediately; return total unique persons."""
    page_df = page_df.copy()
    page_df["occupation"] = occupation
    if dest.exists() and _is_valid_csv(dest):
        old = pd.read_csv(dest)
        out = pd.concat([old, page_df], ignore_index=True)
    else:
        out = page_df
    out = out.drop_duplicates(subset=["person"], keep="first")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dest, index=False)
    return len(out)


def _merge() -> int:
    parts: list[pd.DataFrame] = []
    for suffix, _ in OCCUPATIONS:
        p = DOWNLOAD_DIR / f"wikidata_european_{suffix}.csv"
        if _is_valid_csv(p):
            parts.append(pd.read_csv(p))
    if not parts:
        return 0
    merged = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["person"], keep="first")
    merged.to_csv(OUT, index=False)
    log(f"Merged intellectuals: {len(merged)} rows -> {OUT.name}", OUTPUT_LOGS / "fetch.log")
    return len(merged)


def _fetch_window(
    suffix: str,
    wd_id: str,
    death_lo: int,
    death_hi: int,
    start_offset: int = 0,
) -> bool:
    """Fetch one death-year window; persist every page. Return True if window completed."""
    dest = DOWNLOAD_DIR / f"wikidata_european_{suffix}.csv"
    offset = start_offset
    while True:
        tmp = DOWNLOAD_DIR / f"wikidata_european_{suffix}.{death_lo}_{death_hi}.o{offset}.xml"
        query = _sparql_page(wd_id, death_lo, death_hi, offset)
        if not _download_page(query, tmp):
            prog = _load_progress(suffix)
            prog["current"] = {"death_lo": death_lo, "death_hi": death_hi, "offset": offset}
            _save_progress(suffix, prog)
            log(
                f"{suffix} {death_lo}-{death_hi}: page offset={offset} FAILED (saved progress)",
                OUTPUT_LOGS / "fetch.log",
            )
            return False

        page_df = _read_page(tmp)
        tmp.unlink(missing_ok=True)
        if page_df is None or page_df.empty:
            break

        total = _persist_page(dest, page_df, suffix)
        _merge()
        log(
            f"{suffix} {death_lo}-{death_hi}: +{len(page_df)} (offset={offset}) "
            f"-> {suffix}.csv total={total}",
            OUTPUT_LOGS / "fetch.log",
        )

        prog = _load_progress(suffix)
        prog["current"] = {
            "death_lo": death_lo,
            "death_hi": death_hi,
            "offset": offset + PAGE_SIZE,
        }
        _save_progress(suffix, prog)

        if len(page_df) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        time.sleep(PAGE_SLEEP)

    prog = _load_progress(suffix)
    key = f"{death_lo}-{death_hi}"
    done = list(prog.get("completed_windows") or [])
    if key not in done:
        done.append(key)
    prog["completed_windows"] = done
    prog["current"] = None
    _save_progress(suffix, prog)
    return True


def _fetch_one(
    suffix: str,
    wd_id: str,
    *,
    force: bool = False,
    max_windows: int | None = None,
) -> None:
    dest = DOWNLOAD_DIR / f"wikidata_european_{suffix}.csv"
    if force:
        if dest.exists():
            dest.unlink()
        pp = _progress_path(suffix)
        if pp.exists():
            pp.unlink()

    # Existing full CSV from earlier run, no progress → treat as done (don't re-pull).
    if dest.exists() and _is_valid_csv(dest) and not force:
        prog = _load_progress(suffix)
        if not prog.get("completed_windows") and not prog.get("current"):
            rows = len(pd.read_csv(dest))
            prog = {
                "completed_windows": [f"{lo}-{hi}" for lo, hi in _windows()],
                "current": None,
                "seeded_from_existing_csv": rows,
            }
            _save_progress(suffix, prog)
            log(f"{suffix}: keep existing CSV ({rows} rows); windows marked complete", OUTPUT_LOGS / "fetch.log")
            return
        if set(prog.get("completed_windows") or []) >= {f"{lo}-{hi}" for lo, hi in _windows()}:
            log(f"{suffix}: all windows already complete", OUTPUT_LOGS / "fetch.log")
            return

    pool = _load_proxy_pool()
    log(f"{suffix}: using {len(pool)} provided proxy(ies)", OUTPUT_LOGS / "fetch.log")

    prog = _load_progress(suffix)
    done = set(prog.get("completed_windows") or [])
    windows = _windows()

    # Resume mid-window first if interrupted.
    cur = prog.get("current")
    if cur and not force:
        lo, hi, off = int(cur["death_lo"]), int(cur["death_hi"]), int(cur["offset"])
        log(f"{suffix}: resume window {lo}-{hi} at offset {off}", OUTPUT_LOGS / "fetch.log")
        if not _fetch_window(suffix, wd_id, lo, hi, start_offset=off):
            return
        done = set(_load_progress(suffix).get("completed_windows") or [])

    n_run = 0
    for lo, hi in windows:
        key = f"{lo}-{hi}"
        if key in done:
            continue
        log(f"{suffix}: start window {lo}-{hi}", OUTPUT_LOGS / "fetch.log")
        if not _fetch_window(suffix, wd_id, lo, hi, start_offset=0):
            return  # stop; progress saved — rerun to continue
        n_run += 1
        if max_windows is not None and n_run >= max_windows:
            log(f"{suffix}: stopping after {max_windows} new window(s)", OUTPUT_LOGS / "fetch.log")
            return


def main() -> None:
    global PAGE_SIZE, PAGE_RETRIES

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="Wipe occupation CSV + progress and refetch")
    ap.add_argument("--occupation", default="", help="Only one suffix, e.g. mathematician")
    ap.add_argument(
        "--max-windows",
        type=int,
        default=None,
        help="Stop after N new death-year windows (useful for smoke tests)",
    )
    ap.add_argument("--page-size", type=int, default=None, help=f"Override PAGE_SIZE (default {PAGE_SIZE})")
    ap.add_argument(
        "--page-retries",
        type=int,
        default=None,
        help=f"Full passes over the provided proxy list per page (default {PAGE_RETRIES})",
    )
    args = ap.parse_args()

    if args.page_size:
        PAGE_SIZE = args.page_size
    if args.page_retries is not None:
        PAGE_RETRIES = max(1, args.page_retries)

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    occs = OCCUPATIONS
    if args.occupation:
        occs = [(s, w) for s, w in OCCUPATIONS if s == args.occupation]
        if not occs:
            raise SystemExit(f"Unknown occupation: {args.occupation}")

    for suffix, wd_id in occs:
        _fetch_one(
            suffix,
            wd_id,
            force=args.force,
            max_windows=args.max_windows,
        )
    _merge()


if __name__ == "__main__":
    main()
