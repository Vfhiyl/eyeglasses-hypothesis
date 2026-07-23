#!/usr/bin/env python3
"""Extract GeoNames cities1000.txt from zip for ISTC name normalization."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

ZIP_CANDIDATES = [
    DATA_RAW / "cities1000.zip",
    ROOT.parent / "download_data" / "cities1000.zip",
]
OUT_TXT = DATA_RAW / "cities1000.txt"
OUT_LOOKUP = DATA_PROCESSED / "geonames_cities1000_lookup.csv"

COLS = [
    "geonameid",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date",
]


def _find_zip() -> Path | None:
    for p in ZIP_CANDIDATES:
        if p.exists():
            return p
    return None


def main() -> None:
    if OUT_TXT.exists() and OUT_TXT.stat().st_size > 1_000_000:
        txt_path = OUT_TXT
    else:
        zpath = _find_zip()
        if zpath is None:
            log("No cities1000.zip found", OUTPUT_LOGS / "fetch.log")
            return
        with zipfile.ZipFile(zpath) as zf:
            zf.extract("cities1000.txt", DATA_RAW)
        txt_path = OUT_TXT
        log(f"Extracted {txt_path.name} ({txt_path.stat().st_size // 1024} KB)", OUTPUT_LOGS / "fetch.log")

    df = pd.read_csv(txt_path, sep="\t", names=COLS, low_memory=False)
    lookup = df[df["feature_class"] == "P"][
        ["geonameid", "name", "asciiname", "country_code", "latitude", "longitude", "population"]
    ].copy()
    lookup.to_csv(OUT_LOOKUP, index=False)
    log(f"GeoNames lookup: {len(lookup)} populated places -> {OUT_LOOKUP}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
