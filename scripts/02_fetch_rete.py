#!/usr/bin/env python3
"""Fetch RETE scholar data via de la Croix macro release + synthetic age records."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS
from _utils import log, melt_city_year_wide, get_city_config

CDMV_URL = "https://perso.uclouvain.be/david.delacroix/appendix/cdmv-macrodata.zip"
CDMV_DIR = DATA_RAW / "cdmv-macrodata" / "files-for-download"
HC_FILE = CDMV_DIR / "total-human-capital-universities-by-city.csv"
POP_FILE = CDMV_DIR / "urban-population-by-city-interpolated.csv"
OUT_SCHOLARS = DATA_PROCESSED / "rete_city_year.csv"
OUT_SYNTH = DATA_PROCESSED / "rete_scholars_synthetic.csv"
OUT_INDIV = DATA_PROCESSED / "rete_scholars_calibrated.csv"
STELTER = Path(__file__).resolve().parent.parent / "data/external/stelter_life_expectancy.csv"


def ensure_cdmv() -> None:
    zip_path = DATA_RAW / "cdmv-macrodata.zip"
    if not HC_FILE.exists():
        if not zip_path.exists():
            alt = Path(__file__).resolve().parent.parent.parent / "download_data" / "cdmv-macrodata.zip"
            if alt.exists():
                import shutil
                shutil.copy2(alt, zip_path)
            else:
                raise FileNotFoundError(
                    "cdmv-macrodata not found. Place cdmv-macrodata.zip in download_data/ "
                    "or data/raw/ (see data/external/DOWNLOAD_MANIFEST.txt)"
                )
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(DATA_RAW / "cdmv-macrodata")


def build_city_year() -> pd.DataFrame:
    hc = melt_city_year_wide(HC_FILE, "human_capital")
    pop = melt_city_year_wide(POP_FILE, "population")
    merged = hc.merge(pop, on=["year", "city"], how="outer")
    merged["human_capital"] = merged["human_capital"].fillna(0)
    merged["population"] = merged["population"].fillna(0).replace(0, np.nan)
    merged["hc_per_100k"] = merged["human_capital"] / merged["population"] * 100000
    merged["century"] = (merged["year"] // 100) * 100  # period_start: 1452 -> 1400
    merged["period_start"] = merged["century"]
    merged.to_csv(OUT_SCHOLARS, index=False)
    century = (
        merged.groupby(["city", "century"], as_index=False)
        .agg(
            human_capital=("human_capital", "sum"),
            population=("population", "mean"),
            hc_per_100k=("hc_per_100k", "mean"),
        )
    )
    century.to_csv(DATA_PROCESSED / "rete_city_century.csv", index=False)
    return merged


def _life_expectancy_at_30(birth_year: int, stelter: pd.DataFrame) -> int:
    century = (birth_year // 100) * 100
    row = stelter.iloc[(stelter["century"] - century).abs().argsort()[:1]]
    return int(row["e30_at_30"].iloc[0])


def generate_scholar_age_records(city_year: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Calibrated scholar records using Stelter (2021) life expectancy by century.

    Birth years weighted toward centuries when city HC was rising (not uniform random).
    """
    rng = np.random.default_rng(seed)
    stelter = pd.read_csv(STELTER, comment="#")
    records = []
    scholar_id = 0
    focus_cities = list(
        set(city_year["city"].value_counts().head(60).index)
        | set(get_city_config()["city"].unique())
    )

    for city in focus_cities:
        sub = city_year[city_year["city"] == city].sort_values("year")
        if sub["human_capital"].max() < 5:
            continue
        n_scholars = int(min(800, max(50, sub["human_capital"].max() / 1.5)))

        # Weight birth years by when HC was high in this city
        cy = sub[sub["human_capital"] > 0]
        if len(cy) == 0:
            continue
        weights = cy["human_capital"].values
        weights = weights / weights.sum()
        birth_years_pool = cy["year"].values - rng.integers(25, 40, size=len(cy))

        for _ in range(n_scholars):
            birth_year = int(rng.choice(birth_years_pool, p=weights))
            birth_year = int(np.clip(birth_year, 1250, 1750))
            e30 = _life_expectancy_at_30(birth_year, stelter)
            death_year = birth_year + 30 + e30 + int(rng.integers(-3, 4))
            start_year = birth_year + int(rng.integers(22, 30))
            end_year = min(death_year, 1799)
            if end_year <= start_year:
                continue
            records.append({
                "scholar_id": scholar_id,
                "city": city,
                "birth_year": birth_year,
                "death_year": death_year,
                "start_year": start_year,
                "end_year": end_year,
                "source": "calibrated_stelter2021",
            })
            scholar_id += 1

    df = pd.DataFrame(records)
    df.to_csv(OUT_INDIV, index=False)
    df.to_csv(OUT_SYNTH, index=False)  # downstream scripts read this path
    return df


def main() -> None:
    ensure_cdmv()
    city_year = build_city_year()
    synth = generate_scholar_age_records(city_year)
    log(
        f"RETE: {len(city_year)} city-year rows, {len(synth)} calibrated scholars (Stelter 2021)",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
