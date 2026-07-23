#!/usr/bin/env python3
"""Import Murray Human Accomplishment OSF data (HA.xlsx + Europe regions)."""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

ZIP_CANDIDATES = [
    DATA_RAW / "osfstorage-archive.zip",
    ROOT.parent / "download_data" / "osfstorage-archive.zip",
]
HA_CANDIDATES = [DATA_RAW / "HA.xlsx", DATA_RAW / "osf_ha" / "HA.xlsx"]
EU_CANDIDATES = [
    DATA_RAW / "HA Regions & Subregions, Europe Only.xlsx",
    DATA_RAW / "osf_ha" / "HA Regions & Subregions, Europe Only.xlsx",
]

GLASS_SUBREGIONS = {
    "I.Florence",
    "I.Venice",
    "I.Venet",
    "I.Milan",
    "I.Lomba",
    "I.Pisa",
    "I.Tusca",
}
ITALY_SUBREGIONS = {s for s in GLASS_SUBREGIONS if s.startswith("I.")}


def _ensure_extracted() -> None:
    if any(p.exists() for p in HA_CANDIDATES):
        return
    for zpath in ZIP_CANDIDATES:
        if not zpath.exists():
            continue
        out = DATA_RAW / "osf_ha"
        out.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(out)
        for xlsx in out.glob("*.xlsx"):
            shutil.copy2(xlsx, DATA_RAW / xlsx.name)
        log(f"Extracted OSF HA zip -> {out}", OUTPUT_LOGS / "fetch.log")
        return


def _find_ha() -> Path | None:
    for p in HA_CANDIDATES:
        if p.exists():
            return p
    return None


def _find_eu() -> Path | None:
    for p in EU_CANDIDATES:
        if p.exists():
            return p
    return None


def main() -> None:
    _ensure_extracted()
    ha_path = _find_ha()
    if ha_path is None:
        log("No HA.xlsx found (osfstorage-archive.zip)", OUTPUT_LOGS / "fetch.log")
        return

    ha = pd.read_excel(ha_path, sheet_name="HA")
    ha = ha.rename(
        columns={
            "Serial": "serial",
            "Name": "name",
            "Fl": "fl_year",
            "Birth": "birth_year",
            "Death": "death_year",
            "Inventory": "inventory",
            "ScienceField": "science_field",
            "Index": "index_score",
            "BirthCountry": "birth_country",
            "WorkCountry": "work_country",
            "Ethnicity": "ethnicity",
            "Woman": "woman",
        }
    )
    for c in ("fl_year", "birth_year", "death_year"):
        ha[c] = pd.to_numeric(ha[c], errors="coerce")

    stmm = ha[ha["inventory"] == "Science"].copy()
    stmm["century"] = (stmm["fl_year"] // 100) * 100
    stmm["source"] = "murray_ha_osf"
    stmm.to_csv(DATA_PROCESSED / "ha_science_persons.csv", index=False)

    by_century = (
        stmm.groupby("century", as_index=False)
        .agg(persons=("serial", "count"), mean_index=("index_score", "mean"))
        .sort_values("century")
    )
    by_century.to_csv(DATA_PROCESSED / "ha_science_by_century.csv", index=False)

    by_country = (
        stmm.groupby("work_country", as_index=False)
        .agg(persons=("serial", "count"), mean_fl=("fl_year", "mean"))
        .sort_values("persons", ascending=False)
    )
    by_country.to_csv(DATA_PROCESSED / "ha_science_by_country.csv", index=False)

    eu_path = _find_eu()
    if eu_path is not None:
        eu = pd.read_excel(eu_path, sheet_name=0)
        eu = eu.rename(
            columns={
                "serial": "serial",
                "name": "name",
                "fl": "fl_year",
                "birth": "birth_year",
                "death": "death_year",
                "inventory": "inventory",
                "adultsubregion": "subregion",
                "adultregion": "region",
            }
        )
        eu_sci = eu[eu["inventory"] == "Science"].copy()
        eu_sci["century"] = (eu_sci["fl_year"] // 100) * 100
        eu_sci["glass_subregion"] = eu_sci["subregion"].isin(GLASS_SUBREGIONS)
        eu_sci.to_csv(DATA_PROCESSED / "ha_europe_science_persons.csv", index=False)

        italy = eu_sci[eu_sci["subregion"].astype(str).str.startswith("I.", na=False)]
        glass = eu_sci[eu_sci["glass_subregion"]]
        ctrl = eu_sci[~eu_sci["glass_subregion"]]
        pre = eu_sci[eu_sci["fl_year"] < 1300]
        post = eu_sci[eu_sci["fl_year"] >= 1300]
        summary = pd.DataFrame(
            [
                {
                    "test": "ha_europe_science_pre_vs_post_1300",
                    "n_pre_1300": len(pre),
                    "n_post_1300": len(post),
                    "italy_science_total": len(italy),
                    "glass_subregion_total": len(glass),
                    "control_subregion_total": len(ctrl),
                    "note": "Fl encodes ~age-40 by Murray design; use counts not Fl age",
                }
            ]
        )
        summary.to_csv(DATA_PROCESSED / "ha_science_summary.csv", index=False)

    log(
        f"Human Accomplishment: {len(ha)} persons, {len(stmm)} science -> "
        f"{DATA_PROCESSED / 'ha_science_persons.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
