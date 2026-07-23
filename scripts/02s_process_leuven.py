#!/usr/bin/env python3
"""Process Old University of Leuven matriculation database (SODHA 1426-1797)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "leuven_matrikels.tab",
    DATA_RAW / "leuven_matrikels_v2.tab",
    ROOT.parent / "download_data" / "leuven_matrikels.tab",
    ROOT.parent / "download_data" / "leuven_matrikels_v2.tab",
]


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 100_000:
            return path
    return None


def main() -> None:
    path = _find_file()
    if path is None:
        log("No Leuven matrikels file found", OUTPUT_LOGS / "fetch.log")
        return

    df = pd.read_excel(path)
    df["year"] = pd.to_datetime(df["Datum inschrijving"], dayfirst=True, errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df.to_csv(DATA_PROCESSED / "leuven_matriculations.csv", index=False)

    yearly = df.groupby("year", as_index=False).size().rename(columns={"size": "n_enrollments"})
    yearly.to_csv(OUTPUT_TABLES / "leuven_yearly_enrollments.csv", index=False)

    age = df["Cat. leeftijd"].fillna("unknown").astype(str).str.lower()
    df["is_minor"] = age.str.contains("minorennis")
    df["is_major"] = age.str.contains("maiorennis")

    half = df.copy()
    half["half_century"] = (half["year"] // 50) * 50
    age_half = (
        half.groupby("half_century", as_index=False)
        .agg(n=("year", "size"), n_major=("is_major", "sum"), n_minor=("is_minor", "sum"))
    )
    age_half["major_share"] = age_half["n_major"] / age_half["n"].replace(0, np.nan)
    age_half.to_csv(OUTPUT_TABLES / "leuven_half_century_age.csv", index=False)

    pre = yearly[yearly["year"] < 1500]["n_enrollments"].sum()
    post = yearly[yearly["year"] >= 1500]["n_enrollments"].sum()

    summary = pd.DataFrame(
        [
            {
                "test": "leuven_matriculations_volume",
                "n_total": len(df),
                "year_min": int(df["year"].min()),
                "year_max": int(df["year"].max()),
                "n_pre_1500": int(pre),
                "n_post_1500": int(post),
                "major_share_overall": round(df["is_major"].mean(), 4),
                "minor_share_overall": round(df["is_minor"].mean(), 4),
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "leuven_summary.csv", index=False)

    log(f"Leuven: {len(df)} matriculations {int(df['year'].min())}-{int(df['year'].max())}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
