#!/usr/bin/env python3
"""Import Stelter et al. (2021) scholar appointment data from OSF Data.xlsx."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "stelter_scholars_Data.xlsx",
    DATA_RAW / "Data.xlsx",
    ROOT.parent / "download_data" / "Data.xlsx",
    ROOT.parent / "download_data" / "stelter_scholars_Data.xlsx",
]
OUT = DATA_PROCESSED / "stelter_scholars.csv"
OUT_SYNTH = DATA_PROCESSED / "rete_scholars_synthetic.csv"


def _find_file() -> Path | None:
    for p in CANDIDATES:
        if p.exists() and p.stat().st_size > 10_000:
            return p
    return None


def main() -> None:
    path = _find_file()
    if path is None:
        log("No Stelter Data.xlsx found", OUTPUT_LOGS / "fetch.log")
        return

    df = pd.read_excel(path, sheet_name="Data")
    df = df.rename(
        columns={
            "ID": "scholar_id",
            "Birthyear": "birth_year",
            "Deathyear": "death_year",
            "Appoint_year": "appoint_year",
            "Appoint_Acad": "appoint_acad_year",
            "Appoint_Uni": "appoint_uni_year",
            "Exityear": "exit_year",
            "Med": "is_med",
            "Acad": "is_acad",
            "Uni": "is_uni",
            "Sex": "sex",
            "min_Cat": "quality_category",
            "Birthprecision": "birth_precision",
            "Deathprecision": "death_precision",
        }
    )

    for c in ("birth_year", "death_year", "appoint_year", "exit_year", "appoint_acad_year", "appoint_uni_year"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["start_year"] = df["appoint_year"]
    df.loc[df["start_year"].isna(), "start_year"] = df["birth_year"] + 25
    df["end_year"] = df["exit_year"]
    df.loc[df["end_year"].isna(), "end_year"] = df["death_year"]

    df["source"] = "stelter2021_osf"
    df["region"] = "HRE"  # Holy Roman Empire sample; no city in this file
    df["city"] = ""  # not available — cannot map to glass centers

    df.to_csv(OUT, index=False)

    usable = df.dropna(subset=["birth_year", "start_year", "end_year"])
    usable = usable[usable["end_year"] > usable["start_year"]]
    out_cols = [
        "scholar_id",
        "birth_year",
        "death_year",
        "start_year",
        "end_year",
        "appoint_year",
        "exit_year",
        "is_uni",
        "is_acad",
        "is_med",
        "quality_category",
        "region",
        "city",
        "source",
    ]
    usable[out_cols].to_csv(OUT_SYNTH, index=False)
    log(
        f"Stelter: {len(df)} scholars, {len(usable)} with valid career span -> {OUT_SYNTH}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
