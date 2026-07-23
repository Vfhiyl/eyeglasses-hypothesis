#!/usr/bin/env python3
"""Build city x century analysis panel with coverage flags (no silent zero-fill)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_LOGS
from _utils import get_city_config, log

OUT = DATA_PROCESSED / "panel_city_century.csv"


def main() -> None:
    rete = pd.read_csv(DATA_PROCESSED / "rete_city_century.csv")
    istc = pd.read_csv(DATA_PROCESSED / "istc_city_century.csv")
    cities = get_city_config()

    panel = rete.merge(
        istc.rename(columns={"book_count": "books"}),
        on=["city", "century"],
        how="outer",
        indicator="merge_source",
    )
    panel = panel.merge(cities, on="city", how="left")

    extras_path = DATA_PROCESSED / "cdmv_city_century_extras.csv"
    if extras_path.exists():
        panel = panel.merge(pd.read_csv(extras_path), on=["city", "century"], how="left")

    panel["glass_center"] = panel["glass_center"].fillna(False).astype(int)
    panel["has_university"] = panel["has_university"].fillna(False).astype(int)

    # Coverage: distinguish missing vs structural zero
    panel["hc_observed"] = panel["human_capital"].notna().astype(int)
    panel["books_observed"] = panel["books"].notna().astype(int)
    panel["pop_observed"] = panel["population"].notna().astype(int)

    # Sensitivity fills (explicit); main regressions should filter on *_observed
    panel["human_capital_fill0"] = panel["human_capital"].fillna(0)
    panel["books_fill0"] = panel["books"].fillna(0)
    panel["hc_per_100k_raw"] = panel["hc_per_100k"]
    panel["hc_per_100k_fill0"] = panel["hc_per_100k"].fillna(0)

    # Keep NaN for primary columns used in observed-only specs
    panel["post_1300"] = (panel["century"] >= 1300).astype(int)
    panel["post_1450"] = (panel["century"] >= 1450).astype(int)
    panel["post_1600"] = (panel["century"] >= 1600).astype(int)
    panel["period_start"] = panel["century"]
    panel["log_hc_per_100k"] = np.log1p(panel["hc_per_100k_fill0"])
    panel["log_books"] = np.log1p(panel["books_fill0"])

    panel.to_csv(OUT, index=False)
    log(
        f"Panel: {len(panel)} rows, {panel['city'].nunique()} cities; "
        f"hc_obs={panel['hc_observed'].sum()}, books_obs={panel['books_observed'].sum()} -> {OUT}",
        OUTPUT_LOGS / "build.log",
    )


if __name__ == "__main__":
    main()
