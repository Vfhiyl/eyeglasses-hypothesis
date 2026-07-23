#!/usr/bin/env python3
"""Summarize curated London customs spectacle import hits (Jenks OA PDFs)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

SRC = ROOT / "data" / "curated" / "london_customs_spectacles.csv"
OUT = DATA_PROCESSED / "london_customs_spectacles.csv"
SUMMARY = OUTPUT_TABLES / "london_customs_spectacles_summary.csv"


def main() -> None:
    if not SRC.exists():
        log(f"Missing {SRC}", OUTPUT_LOGS / "fetch.log")
        return
    df = pd.read_csv(SRC)
    df.to_csv(OUT, index=False)
    pairs = pd.to_numeric(df["pairs_est"], errors="coerce")
    summary = pd.DataFrame(
        [
            {
                "n_entries": len(df),
                "pairs_est_sum": int(pairs.sum(skipna=True)),
                "year_min": int(df["year"].min()),
                "year_max": int(df["year_end"].max()),
                "claim_layer": "spectacle_adoption_evidence",
                "note": (
                    "From Jenks OA PDFs (i–iv sample) + Cobb BHO + Gras 1509; "
                    "confirms Ilardi 1384/1391 and upgrades 1494 cite; "
                    "trade volume evidence not career-year ID"
                ),
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    log(
        f"London customs spectacles: {len(df)} entries, pairs_est_sum={int(pairs.sum(skipna=True))}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
