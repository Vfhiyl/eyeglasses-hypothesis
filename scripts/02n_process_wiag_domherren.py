#!/usr/bin/env python3
"""Process WIAG cathedral canons (Domherren) CSV."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "wiag_domherren_persons.csv",
    ROOT.parent / "download_data" / "wiag_domherren_persons.csv",
    ROOT.parent / "download_data" / "WIAG-Domherren-DB (1).csv",
    ROOT.parent / "download_data" / "WIAG-Domherren-DB.csv",
]

GLASS_CITY_KEYWORDS = (
    "floren",
    "firenze",
    "venez",
    "vened",
    "mailand",
    "milan",
    "pisa",
    "murano",
    "nürnberg",
    "nurnberg",
    "nuremberg",
    "norimber",
)


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 10_000:
            return path
    return None


def parse_year(value) -> float | None:
    if pd.isna(value):
        return None
    match = re.search(r"\b(1[0-9]{3}|2[0-9]{3})\b", str(value))
    return float(match.group(1)) if match else None


def is_glass_center_location(text: str) -> bool:
    if pd.isna(text):
        return False
    low = str(text).lower()
    return any(k in low for k in GLASS_CITY_KEYWORDS)


def is_domherr_title(title: str) -> bool:
    if pd.isna(title):
        return False
    low = str(title).lower()
    return "domherr" in low or "canon" in low or "canonic" in low


def main() -> None:
    path = _find_file()
    if path is None:
        log("No WIAG Domherren CSV found", OUTPUT_LOGS / "fetch.log")
        return

    raw = pd.read_csv(path, sep="\t", low_memory=False)
    rows = []
    for _, person in raw.iterrows():
        birth = pd.to_numeric(person.get("dateOfBirth"), errors="coerce")
        death = pd.to_numeric(person.get("dateOfDeath"), errors="coerce")
        for i in range(57):
            title_col = f"offices.{i}.title"
            if title_col not in person.index or pd.isna(person.get(title_col)):
                continue
            title = str(person.get(title_col))
            if not is_domherr_title(title):
                continue
            office_year = parse_year(person.get(f"offices.{i}.dateBegin"))
            if office_year is None:
                continue
            institution = person.get(f"offices.{i}.institution", "")
            diocese = person.get(f"offices.{i}.diocese", "")
            location = f"{institution} {diocese}".strip()
            rows.append(
                {
                    "wiag_id": person.get("wiagId"),
                    "name": f"{person.get('givenname', '')} {person.get('familyname', '')}".strip(),
                    "birth_year": birth,
                    "death_year": death,
                    "office_year": office_year,
                    "office_title": title,
                    "institution": institution,
                    "diocese": diocese,
                    "glass_center_location": is_glass_center_location(location),
                    "source": "wiag_domherren",
                }
            )

    offices = pd.DataFrame(rows)
    offices.to_csv(DATA_PROCESSED / "wiag_domherren_offices.csv", index=False)

    first = (
        offices.sort_values("office_year")
        .groupby("wiag_id", as_index=False)
        .first()
    )
    first = first.dropna(subset=["birth_year", "office_year"])
    first = first[(first["office_year"] >= 1200) & (first["office_year"] < 1800)]
    first["age_at_office"] = first["office_year"] - first["birth_year"]
    first = first[(first["age_at_office"] >= 18) & (first["age_at_office"] <= 90)]
    first.to_csv(DATA_PROCESSED / "wiag_domherren_careers.csv", index=False)

    pre = first[first["office_year"] < 1300]["age_at_office"]
    post = first[first["office_year"] >= 1300]["age_at_office"]
    if len(pre) >= 2 and len(post) >= 2:
        t_stat, p_val = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t_stat, p_val = np.nan, np.nan

    ttest = pd.DataFrame(
        [
            {
                "test": "wiag_domherren_age45plus_pre_vs_post_1300",
                "mean_pre_1300": round(pre.mean(), 4) if len(pre) else np.nan,
                "mean_post_1300": round(post.mean(), 4) if len(post) else np.nan,
                "share45_pre": round((pre >= 45).mean(), 4) if len(pre) else np.nan,
                "share45_post": round((post >= 45).mean(), 4) if len(post) else np.nan,
                "t_stat": round(t_stat, 4) if not np.isnan(t_stat) else np.nan,
                "p_value": round(p_val, 6) if not np.isnan(p_val) else np.nan,
                "n_pre": len(pre),
                "n_post": len(post),
                "n_offices_total": len(offices),
                "n_persons_raw": len(raw),
            }
        ]
    )
    ttest.to_csv(OUTPUT_TABLES / "wiag_domherren_age_ttest.csv", index=False)

    log(
        f"WIAG Domherren ({path.name}): {len(raw)} persons, "
        f"{len(offices)} domherr offices, {len(first)} careers with age",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
