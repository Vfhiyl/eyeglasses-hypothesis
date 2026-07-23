#!/usr/bin/env python3
"""Process WIAG Holy Roman Empire bishops (CSV from wiag-vocab.adw-goe.de)."""
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
    DATA_RAW / "wiag_bishops_persons.csv",
    ROOT.parent / "download_data" / "wiag_bishops_persons.csv",
]

ITALY_DIOCESE_KEYWORDS = (
    "aquileia",
    "vened",
    "mailand",
    "milan",
    "floren",
    "pisa",
    "ferrara",
    "padua",
    "padua",
    "verona",
    "bologna",
    "rom",
    "neapel",
    "napl",
)


def _find_file() -> Path | None:
    for p in CANDIDATES:
        if p.exists() and p.stat().st_size > 10_000:
            return p
    return None


def parse_year(value) -> float | None:
    if pd.isna(value):
        return None
    text = str(value)
    match = re.search(r"\b(1[0-9]{3}|2[0-9]{3})\b", text)
    return float(match.group(1)) if match else None


def is_italy_glass_diocese(diocese: str) -> bool:
    if pd.isna(diocese):
        return False
    low = str(diocese).lower()
    return any(k in low for k in ITALY_DIOCESE_KEYWORDS)


def main() -> None:
    path = _find_file()
    if path is None:
        log("No wiag_bishops_persons.csv found", OUTPUT_LOGS / "fetch.log")
        return

    raw = pd.read_csv(path, sep="\t", low_memory=False)
    rows = []
    for _, person in raw.iterrows():
        birth = pd.to_numeric(person.get("dateOfBirth"), errors="coerce")
        death = pd.to_numeric(person.get("dateOfDeath"), errors="coerce")
        for i in range(46):
            title_col = f"offices.{i}.title"
            if title_col not in person.index or pd.isna(person.get(title_col)):
                continue
            office_year = parse_year(person.get(f"offices.{i}.dateBegin"))
            if office_year is None:
                continue
            diocese = person.get(f"offices.{i}.diocese", "")
            rows.append(
                {
                    "wiag_id": person.get("wiagId"),
                    "name": f"{person.get('givenname', '')} {person.get('familyname', '')}".strip(),
                    "birth_year": birth,
                    "death_year": death,
                    "office_year": office_year,
                    "office_title": person.get(title_col),
                    "diocese": diocese,
                    "italy_glass_diocese": is_italy_glass_diocese(diocese),
                    "source": "wiag_bishops",
                }
            )

    offices = pd.DataFrame(rows)
    offices.to_csv(DATA_PROCESSED / "wiag_bishop_offices.csv", index=False)

    # First bishop appointment per person
    first = (
        offices.sort_values("office_year")
        .groupby("wiag_id", as_index=False)
        .first()
    )
    first = first.dropna(subset=["birth_year", "office_year"])
    first = first[(first["office_year"] >= 1200) & (first["office_year"] < 1800)]
    first["age_at_office"] = first["office_year"] - first["birth_year"]
    first = first[(first["age_at_office"] >= 18) & (first["age_at_office"] <= 90)]
    first.to_csv(DATA_PROCESSED / "wiag_bishop_careers.csv", index=False)

    pre = first[first["office_year"] < 1300]["age_at_office"]
    post = first[first["office_year"] >= 1300]["age_at_office"]
    if len(pre) >= 2 and len(post) >= 2:
        t_stat, p_val = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t_stat, p_val = np.nan, np.nan

    ttest = pd.DataFrame(
        [
            {
                "test": "wiag_bishop_age45plus_pre_vs_post_1300",
                "mean_pre_1300": round(pre.mean(), 4) if len(pre) else np.nan,
                "mean_post_1300": round(post.mean(), 4) if len(post) else np.nan,
                "share45_pre": round((pre >= 45).mean(), 4) if len(pre) else np.nan,
                "share45_post": round((post >= 45).mean(), 4) if len(post) else np.nan,
                "t_stat": round(t_stat, 4) if not np.isnan(t_stat) else np.nan,
                "p_value": round(p_val, 6) if not np.isnan(p_val) else np.nan,
                "n_pre": len(pre),
                "n_post": len(post),
            }
        ]
    )
    ttest.to_csv(OUTPUT_TABLES / "wiag_bishop_age_ttest.csv", index=False)

    log(
        f"WIAG: {len(raw)} persons, {len(first)} careers with age -> "
        f"{DATA_PROCESSED / 'wiag_bishop_careers.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
