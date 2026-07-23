#!/usr/bin/env python3
"""Process Utrecht priest ordinations 1505-1518 (IISH / DataverseNL)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "utrecht_priests.tab",
    ROOT.parent / "download_data" / "utrecht_priests.tab",
]

CLERGY_RE = re.compile(r"\b(?:magister|canonicus|decanus|archidiac)\b", re.I)


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 1000:
            return path
    return None


def main() -> None:
    path = _find_file()
    if path is None:
        log("No utrecht_priests.tab found", OUTPUT_LOGS / "fetch.log")
        return

    raw = pd.read_csv(path, sep="\t", low_memory=False)
    priests = raw[raw["Type record"] == "Priesterwijding"].copy()
    priests["year"] = pd.to_datetime(priests["Datum (YMD)"], errors="coerce").dt.year
    priests = priests.dropna(subset=["year"])
    priests["clergy_title"] = priests["Transcriptie"].fillna("").str.contains(CLERGY_RE)
    priests.to_csv(DATA_PROCESSED / "utrecht_priest_ordinations.csv", index=False)

    yearly = (
        priests.groupby("year", as_index=False)
        .agg(n_ordinations=("year", "size"), n_titled=("clergy_title", "sum"))
    )
    yearly["titled_share"] = yearly["n_titled"] / yearly["n_ordinations"].replace(0, np.nan)
    yearly.to_csv(OUTPUT_TABLES / "utrecht_yearly_ordinations.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "test": "utrecht_priest_ordinations_1505_1518",
                "n_ordinations": len(priests),
                "year_min": int(priests["year"].min()),
                "year_max": int(priests["year"].max()),
                "titled_share": round(priests["clergy_title"].mean(), 4),
                "n_unique_places": priests["Locatie"].nunique(),
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "utrecht_summary.csv", index=False)

    log(f"Utrecht priests: {len(priests)} ordinations", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
