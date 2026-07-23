#!/usr/bin/env python3
"""Process ISTC holdings: copies by country and by holding institution."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS
from _utils import build_geonames_city_map, log, normalize_city

HOLDINGS = DATA_RAW / "istc_core_holdings_1.0.csv"
IMPRINTS = DATA_RAW / "istc_core_imprints_1.0.csv"
OUT_COUNTRY = DATA_PROCESSED / "istc_copies_by_country.csv"
OUT_INST = DATA_PROCESSED / "istc_copies_by_institution.csv"
OUT_CITY = DATA_PROCESSED / "istc_imprint_copies_by_city.csv"


def main() -> None:
    if not HOLDINGS.exists():
        log(f"Skip holdings: {HOLDINGS} not found", OUTPUT_LOGS / "fetch.log")
        return

    holdings = pd.read_csv(HOLDINGS, low_memory=False)
    holdings["country_code"] = holdings["country_code"].fillna("??").astype(str)

    by_country = (
        holdings.groupby("country_code", as_index=False)
        .size()
        .rename(columns={"size": "copy_count"})
        .sort_values("copy_count", ascending=False)
    )
    by_country.to_csv(OUT_COUNTRY, index=False)

    inst = holdings.copy()
    inst["holding_institution_name"] = inst["holding_institution_name"].fillna("unknown")
    by_inst = (
        inst.groupby(["country_code", "holding_institution_name"], as_index=False)
        .size()
        .rename(columns={"size": "copy_count"})
        .sort_values("copy_count", ascending=False)
    )
    by_inst.to_csv(OUT_INST, index=False)

    if IMPRINTS.exists():
        imprints = pd.read_csv(
            IMPRINTS,
            usecols=["id_assigned_by", "geonames_id", "imprint_place", "lat", "lon"],
            low_memory=False,
        )
        city_map = build_geonames_city_map(imprints)
        linked = holdings.merge(imprints.drop_duplicates("id_assigned_by"), on="id_assigned_by", how="left")
        linked["city"] = linked["geonames_id"].map(city_map)
        missing = linked["city"].isna() & linked["imprint_place"].notna()
        linked.loc[missing, "city"] = linked.loc[missing, "imprint_place"].map(normalize_city)
        by_city = (
            linked.dropna(subset=["city"])
            .groupby("city", as_index=False)
            .size()
            .rename(columns={"size": "copy_count"})
            .sort_values("copy_count", ascending=False)
        )
        by_city.to_csv(OUT_CITY, index=False)
        log(
            f"Holdings: {len(holdings)} copies -> {len(by_country)} countries, "
            f"{len(by_inst)} institutions, {len(by_city)} imprint cities",
            OUTPUT_LOGS / "fetch.log",
        )
    else:
        log(f"Holdings country/inst only ({len(holdings)} copies)", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
