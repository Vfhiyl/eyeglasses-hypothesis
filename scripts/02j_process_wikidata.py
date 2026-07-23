#!/usr/bin/env python3
"""Filter Wikidata European university-teacher export to historical subset."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "wikidata_european_intellectuals.csv",
    ROOT.parent / "download_data" / "wikidata_european_intellectuals.csv",
]
PART_GLOB_DIRS = [DATA_RAW, ROOT.parent / "download_data"]


def _load_merged() -> pd.DataFrame | None:
    for p in CANDIDATES:
        if p.exists() and p.stat().st_size > 10_000:
            return pd.read_csv(p)
    parts: list[pd.DataFrame] = []
    for d in PART_GLOB_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.glob("wikidata_european_*.csv")):
            if p.name in ("wikidata_european_intellectuals.csv", "wikidata_european_scholars.csv"):
                continue
            if p.stat().st_size > 1000:
                try:
                    parts.append(pd.read_csv(p, on_bad_lines="skip"))
                except Exception as exc:
                    log(f"Skip {p.name}: {exc}", OUTPUT_LOGS / "fetch.log")
    if not parts:
        legacy = ROOT.parent / "download_data" / "wikidata_european_scholars.csv"
        if legacy.exists():
            return pd.read_csv(legacy)
        return None
    return pd.concat(parts, ignore_index=True).drop_duplicates(subset=["person"], keep="first")


def _parse_year(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True).dt.year


def main() -> None:
    df = _load_merged()
    if df is None:
        log("No wikidata european CSVs", OUTPUT_LOGS / "fetch.log")
        return
    df = df.rename(
        columns={
            "person": "person_uri",
            "personLabel": "name",
            "birth": "birth_raw",
            "death": "death_raw",
            "birthplaceLabel": "birthplace",
        }
    )
    df["birth_year"] = _parse_year(df["birth_raw"])
    df["death_year"] = _parse_year(df["death_raw"])
    hist = df[df["death_year"].between(1100, 1850, inclusive="both")].copy()
    hist["century"] = (hist["death_year"] // 100) * 100
    hist["source"] = "wikidata_european_intellectuals_merged"
    hist.to_csv(DATA_PROCESSED / "wikidata_scholars_historical.csv", index=False)

    by_century = hist.groupby("century", as_index=False).size().rename(columns={"size": "persons"})
    by_century.to_csv(DATA_PROCESSED / "wikidata_scholars_by_century.csv", index=False)

    log(
        f"Wikidata: {len(df)} total, {len(hist)} historical (death 1100-1850)",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
