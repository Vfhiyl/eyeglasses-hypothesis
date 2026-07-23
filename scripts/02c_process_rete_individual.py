#!/usr/bin/env python3
"""Parse user-downloaded RETE individual scholar CSV (replaces synthetic ages if present)."""
from __future__ import annotations

import sys
from pathlib import Path

import re

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log, normalize_city

CANDIDATES = [
    DATA_RAW / "rete_scholars_individual.csv",
    ROOT.parent / "download_data" / "rete_scholars_individual.csv",
]
OUT = DATA_PROCESSED / "rete_scholars_individual.csv"
OUT_SYNTH = DATA_PROCESSED / "rete_scholars_synthetic.csv"

# Common column aliases in RETE exports
COL_MAP = {
    "pkey": "pkey",
    "pname": "pname",
    "first_name": "first_name",
    "alt_name": "alt_name",
    "birth_place": "birth_place",
    "death_place": "death_place",
    "yearborn": "birth_year",
    "yeardied": "death_year",
    "birth": "birth_year",
    "birthyear": "birth_year",
    "birth_year": "birth_year",
    "death": "death_year",
    "deathyear": "death_year",
    "death_year": "death_year",
    "start": "start_year",
    "startyear": "start_year",
    "start_year": "start_year",
    "end": "end_year",
    "endyear": "end_year",
    "end_year": "end_year",
    "city": "city",
    "place": "city",
    "institution_city": "city",
    "institution": "institution",
    "name": "name",
    "scholar": "name",
}


def _find_file() -> Path | None:
    for p in CANDIDATES:
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        key = c.strip().lower().replace(" ", "_")
        if key in COL_MAP:
            rename[c] = COL_MAP[key]
    return df.rename(columns=rename)


def main() -> None:
    if (DATA_PROCESSED / "stelter_scholars.csv").exists():
        log("Skip 02c: Stelter scholar data takes priority", OUTPUT_LOGS / "fetch.log")
        return

    career_path = DATA_PROCESSED / "rete_scholars_career.csv"
    if career_path.exists() and career_path.stat().st_size > 1000:
        log("Skip 02c: career records from Activities already loaded", OUTPUT_LOGS / "fetch.log")
        return

    path = _find_file()
    if path is None:
        log("No rete_scholars_individual.csv — using synthetic scholars", OUTPUT_LOGS / "fetch.log")
        return

    df = pd.read_csv(path, low_memory=False)
    df = _normalize_columns(df)
    if "birth_year" not in df.columns:
        log(f"RETE individual CSV missing birth_year; have {df.columns.tolist()}", OUTPUT_LOGS / "fetch.log")
        return

    if "city" not in df.columns:
        if "birth_place" in df.columns:
            df["city"] = df["birth_place"].astype(str).map(
                lambda x: normalize_city(re.sub(r"[A-Z]{3}$", "", x)) if x not in ("nan", "NA", "") else ""
            )
        else:
            log("RETE individual: no city/birth_place column", OUTPUT_LOGS / "fetch.log")
            return

    for col in ("birth_year", "death_year", "start_year", "end_year"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["city"] = df["city"].astype(str).map(normalize_city)
    if "start_year" not in df.columns:
        df["start_year"] = df["birth_year"] + 25
    if "end_year" not in df.columns:
        df["end_year"] = df["death_year"]
    df = df[df["city"].astype(str).str.replace("nan", "").str.len() > 0]
    n_with_birth = df["birth_year"].notna().sum()
    df["scholar_id"] = range(len(df))
    df["source"] = "rete_individual_export"

    out_cols = [c for c in ["scholar_id", "name", "city", "institution", "birth_year", "death_year", "start_year", "end_year", "source"] if c in df.columns]
    df[out_cols].to_csv(OUT, index=False)
    df[out_cols].to_csv(OUT_SYNTH, index=False)
    log(f"RETE individual: {len(df)} scholars ({n_with_birth} with birth_year) from {path.name}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
