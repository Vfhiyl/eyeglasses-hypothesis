#!/usr/bin/env python3
"""Process extra CDMV city-level series: universities, academies."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS
from _utils import log, melt_city_year_wide

CDMV_DIR = DATA_RAW / "cdmv-macrodata" / "files-for-download"

SERIES = [
    ("number-of-universities-by-city.csv", "n_universities"),
    ("number-of-academies-by-city.csv", "n_academies"),
    ("total-human-capital-academies-by-city.csv", "hc_academies"),
]


def main() -> None:
    frames = []
    for fname, col in SERIES:
        path = CDMV_DIR / fname
        if not path.exists():
            log(f"Skip missing CDMV file: {fname}", OUTPUT_LOGS / "fetch.log")
            continue
        long = melt_city_year_wide(path, col)
        century = long.groupby(["city", "century"], as_index=False)[col].mean()
        frames.append(century)

    if not frames:
        log("No CDMV extra files found", OUTPUT_LOGS / "fetch.log")
        return

    panel = frames[0]
    for f in frames[1:]:
        panel = panel.merge(f, on=["city", "century"], how="outer")

    out = DATA_PROCESSED / "cdmv_city_century_extras.csv"
    panel.to_csv(out, index=False)
    log(f"CDMV extras: {len(panel)} rows -> {out}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
