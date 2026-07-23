#!/usr/bin/env python3
"""Enrich age-at-work panel with Wikidata P19 birthplace (glass-center QIDs)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS
from _utils import log

PANEL = DATA_PROCESSED / "wikidata_age_at_work.csv"
OUT_JSON = DATA_RAW / "wikidata_age_at_work" / "birthplaces.json"
OUT_PANEL = DATA_PROCESSED / "wikidata_age_at_work.csv"

# Canonical glass-center birthplace entities
GLASS_QIDS = {
    "Q2044": "Florence",
    "Q641": "Venice",
    "Q490": "Milan",
    "Q13375": "Pisa",
    "Q2090": "Nuremberg",
    "Q168602": "Murano",
    "Q220": "Rome",  # not primary glass, leave False
}


def _qid(uri: str) -> str:
    return str(uri).rstrip("/").split("/")[-1]


def fetch_batch(qids: list[str], proxy: str, timeout: int = 120) -> list[dict]:
    values = " ".join(f"wd:{q}" for q in qids)
    query = f"""
    SELECT ?person ?place WHERE {{
      VALUES ?person {{ {values} }}
      OPTIONAL {{ ?person wdt:P19 ?place }}
    }}
    """
    env = os.environ.copy()
    env["https_proxy"] = proxy
    env["HTTPS_PROXY"] = proxy
    r = subprocess.run(
        [
            "curl",
            "-fsSL",
            "--http1.1",
            "--max-time",
            str(timeout),
            "-H",
            "Accept: application/sparql-results+json",
            "-H",
            "User-Agent: eyeglasses-hypothesis/1.6 (P19 birthplace)",
            "--data-urlencode",
            f"query={query.strip()}",
            "https://query.wikidata.org/sparql",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:] or f"curl {r.returncode}")
    bindings = json.loads(r.stdout).get("results", {}).get("bindings", [])
    rows = []
    for b in bindings:
        person = b.get("person", {}).get("value", "")
        place = b.get("place", {}).get("value", "")
        rows.append({"person": person, "place": place, "place_qid": _qid(place) if place else ""})
    return rows


def main() -> None:
    if not PANEL.exists():
        log(f"Missing {PANEL}; run 02aa first", OUTPUT_LOGS / "fetch.log")
        return
    df = pd.read_csv(PANEL)
    qids = sorted({_qid(p) for p in df["person"].dropna().unique()})
    proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:12309"
    all_rows: list[dict] = []
    batch_size = 80
    for i in range(0, len(qids), batch_size):
        batch = qids[i : i + batch_size]
        try:
            rows = fetch_batch(batch, proxy=proxy)
            all_rows.extend(rows)
            print(f"batch {i // batch_size + 1}: {len(rows)} rows")
        except Exception as e:
            print(f"FAIL batch {i}: {e}")
            log(f"P19 FAIL batch {i}: {e}", OUTPUT_LOGS / "fetch.log")
        time.sleep(0.8)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(all_rows, ensure_ascii=False), encoding="utf-8")

    bp = pd.DataFrame(all_rows).drop_duplicates("person", keep="first")
    bp["place_qid"] = bp["place_qid"].fillna("")
    # Exclude Rome from glass set even if in map
    glass_set = {k for k in GLASS_QIDS if k != "Q220"}
    bp["bplace_qid"] = bp["place_qid"]
    bp["bplace_name_p19"] = bp["place_qid"].map(lambda q: GLASS_QIDS.get(q, q))
    bp["glass_p19"] = bp["place_qid"].isin(glass_set)

    merged = df.merge(bp[["person", "bplace_qid", "bplace_name_p19", "glass_p19"]], on="person", how="left")
    if "bplace_name" in merged.columns:
        merged["bplace_name"] = merged["bplace_name"].combine_first(merged["bplace_name_p19"])
    else:
        merged["bplace_name"] = merged["bplace_name_p19"]
    merged["glass_center"] = (
        merged.get("glass_center", False).fillna(False).astype(bool) | merged["glass_p19"].fillna(False).astype(bool)
    )
    merged.to_csv(OUT_PANEL, index=False)
    print(
        f"persons={len(merged)} with_p19={int(merged['bplace_qid'].notna().sum())} "
        f"glass={int(merged['glass_center'].sum())} -> {OUT_PANEL}"
    )
    log(
        f"P19 enrich: glass={int(merged['glass_center'].sum())}/{len(merged)}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
