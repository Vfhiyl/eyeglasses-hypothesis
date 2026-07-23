#!/usr/bin/env python3
"""Join Activities + Institutions + Persons → career-based scholar records."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS
from _utils import log, normalize_city

OUT = DATA_PROCESSED / "rete_scholars_career.csv"
OUT_SYNTH = DATA_PROCESSED / "rete_scholars_synthetic.csv"


def _city_from_place(place: str) -> str:
    if not place or str(place) in ("NA", "nan", ""):
        return ""
    return normalize_city(re.sub(r"[A-Z]{3}$", "", str(place).strip()))


def main() -> None:
    if (DATA_PROCESSED / "stelter_scholars.csv").exists():
        log("Skip 02d: Stelter data present", OUTPUT_LOGS / "fetch.log")
        return

    act_path = DATA_RAW / "rete_activities.csv"
    inst_path = DATA_RAW / "rete_institutions.csv"
    pers_path = DATA_RAW / "rete_scholars_individual.csv"

    if not act_path.exists():
        log("Skip 02d: rete_activities.csv not found — run 02a_fetch_rete_activities.py", OUTPUT_LOGS / "fetch.log")
        return

    act = pd.read_csv(act_path, low_memory=False)
    act["beginning"] = pd.to_numeric(act["beginning"], errors="coerce")
    act["end"] = pd.to_numeric(act["end"], errors="coerce")

    if inst_path.exists():
        inst = pd.read_csv(inst_path, low_memory=False)
        inst = inst.rename(columns={"ikey": "ikey", "headquarter": "headquarter"})
        act = act.merge(
            inst[["ikey", "headquarter", "iname", "english_name"]],
            on="ikey",
            how="left",
        )
        act["city"] = act["headquarter"].map(_city_from_place)
    else:
        act["city"] = ""

    if pers_path.exists():
        pers = pd.read_csv(pers_path, low_memory=False)
        pers = pers.rename(columns={"pkey": "pkey"})
        keep = [c for c in ["pkey", "birth_year", "death_year", "name", "birth_place", "death_place"] if c in pers.columns]
        act = act.merge(pers[keep], on="pkey", how="left")

    act = act.rename(columns={"beginning": "start_year", "end": "end_year"})
    act["source"] = "rete_activities"
    act.to_csv(OUT, index=False)

    # One row per scholar×activity; downstream age tests use institution city
    career = act[act["city"].astype(str).str.len() > 0].copy()
    career = career.dropna(subset=["start_year"])
    career["scholar_id"] = range(len(career))
    out_cols = [
        c
        for c in [
            "scholar_id",
            "pkey",
            "ikey",
            "name",
            "city",
            "field",
            "start_year",
            "end_year",
            "birth_year",
            "death_year",
            "weak_link",
            "source",
        ]
        if c in career.columns
    ]
    career[out_cols].to_csv(OUT_SYNTH, index=False)
    log(
        f"RETE career: {len(act)} activities, {career['pkey'].nunique()} scholars, "
        f"{career['city'].nunique()} cities -> {OUT_SYNTH}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
