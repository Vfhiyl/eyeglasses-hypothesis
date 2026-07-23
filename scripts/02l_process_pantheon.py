#!/usr/bin/env python3
"""Process Pantheon 2.0 person dataset (person_2025_update.csv.bz2)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log, normalize_city

CANDIDATES = [
    DATA_RAW / "person_2025_update.csv.bz2",
    DATA_RAW / "pantheon_2025.csv.bz2",
    ROOT.parent / "download_data" / "person_2025_update.csv.bz2",
]

EUROPE_COUNTRIES = {
    "Italy",
    "France",
    "Germany",
    "United Kingdom",
    "Spain",
    "Netherlands",
    "Austria",
    "Switzerland",
    "Belgium",
    "Poland",
    "Portugal",
    "Czech Republic",
    "Hungary",
    "Sweden",
    "Denmark",
    "Ireland",
    "Greece",
}

SCHOLAR_OCCUPATIONS = {
    "PHILOSOPHER",
    "PHYSICIST",
    "MATHEMATICIAN",
    "CHEMIST",
    "BIOLOGIST",
    "ASTRONOMER",
    "INVENTOR",
    "ACADEMIC",
    "ECONOMIST",
    "HISTORIAN",
}

GLASS_CITY_NAMES = {
    "florence",
    "firenze",
    "venice",
    "venezia",
    "milan",
    "milano",
    "murano",
    "pisa",
    "nuremberg",
    "nürnberg",
}


def _find_file() -> Path | None:
    for p in CANDIDATES:
        if p.exists():
            return p
    return None


def _canonical_city(name: str) -> str:
    if pd.isna(name) or not str(name).strip():
        return ""
    low = str(name).strip().lower()
    if low in GLASS_CITY_NAMES:
        return normalize_city(str(name).strip().title())
    return normalize_city(str(name).strip())


def main() -> None:
    path = _find_file()
    if path is None:
        log("No Pantheon person_2025_update.csv.bz2 found", OUTPUT_LOGS / "fetch.log")
        return

    df = pd.read_csv(path, compression="bz2" if str(path).endswith(".bz2") else None, low_memory=False)
    df["birthyear"] = pd.to_numeric(df["birthyear"], errors="coerce")
    df["deathyear"] = pd.to_numeric(df["deathyear"], errors="coerce")
    df["city"] = df["bplace_name"].map(_canonical_city)
    df["glass_center"] = df["bplace_name"].astype(str).str.lower().isin(GLASS_CITY_NAMES)
    df.to_csv(DATA_PROCESSED / "pantheon_persons_all.csv", index=False)

    eu = df[df["bplace_country"].isin(EUROPE_COUNTRIES)].copy()
    eu.to_csv(DATA_PROCESSED / "pantheon_persons_europe.csv", index=False)

    scholars = eu[eu["occupation"].isin(SCHOLAR_OCCUPATIONS)].copy()
    scholars = scholars[scholars["deathyear"].between(1100, 1900, inclusive="both")]
    scholars["century"] = (scholars["deathyear"] // 100) * 100
    scholars["age_at_death"] = scholars["deathyear"] - scholars["birthyear"]
    scholars.to_csv(DATA_PROCESSED / "pantheon_scholars_europe.csv", index=False)

    by_century = (
        scholars.groupby("century", as_index=False)
        .agg(persons=("id", "count"), share_45plus=("age_at_death", lambda s: (s >= 45).mean()))
        .sort_values("century")
    )
    by_century.to_csv(DATA_PROCESSED / "pantheon_scholars_by_century.csv", index=False)

    glass = scholars[scholars["glass_center"]]
    ctrl = scholars[~scholars["glass_center"]]
    pre = scholars[scholars["deathyear"] < 1300]
    post = scholars[scholars["deathyear"] >= 1300]
    summary = pd.DataFrame(
        [
            {
                "europe_persons": len(eu),
                "scholar_persons": len(scholars),
                "glass_city_scholars": len(glass),
                "control_scholars": len(ctrl),
                "pre_1300_scholars": len(pre),
                "post_1300_scholars": len(post),
            }
        ]
    )
    summary.to_csv(DATA_PROCESSED / "pantheon_summary.csv", index=False)

    log(
        f"Pantheon: {len(df)} persons, {len(scholars)} EU scholars -> "
        f"{DATA_PROCESSED / 'pantheon_scholars_europe.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
