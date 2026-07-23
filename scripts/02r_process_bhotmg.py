#!/usr/bin/env python3
"""Process Curtis et al. BHOTMG academic human capital by city (Harvard Dataverse)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

GLASS_COLS = {
    "FirenzeITA": "Florence",
    "VeneziaITA": "Venice",
    "MilanoITA": "Milan",
    "PisaITA": "Pisa",
    "NurnbergDEU": "Nuremberg",
}
CONTROL_COLS = {
    "BolognaITA": "Bologna",
    "ParisFRA": "Paris",
    "OxfordGBR": "Oxford",
    "KolnDEU": "Cologne",
    "PrahaCZE": "Prague",
    "LeipzigDEU": "Leipzig",
    "HeidelbergDEU": "Heidelberg",
    "PadovaITA": "Padua",
}

CANDIDATES = [
    DATA_RAW / "bhotmg" / "extracted" / "total-human-capital-universities-by-city.csv",
    ROOT.parent / "download_data" / "bhotmg" / "extracted" / "total-human-capital-universities-by-city.csv",
    DATA_RAW / "bhotmg" / "total-human-capital-universities-by-city.tab",
    ROOT.parent / "download_data" / "bhotmg" / "file_12053765",
]


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 1000:
            return path
    return None


def melt_city_panel(path: Path) -> pd.DataFrame:
    sep = "\t" if path.suffix == ".tab" or "file_" in path.name else ","
    raw = pd.read_csv(path, sep=sep)
    raw["year"] = pd.to_numeric(raw["year"], errors="coerce")
    raw = raw.dropna(subset=["year"])
    raw = raw[(raw["year"] >= 1200) & (raw["year"] <= 1793)]

    keep = {**GLASS_COLS, **CONTROL_COLS}
    present = {c: label for c, label in keep.items() if c in raw.columns}
    long = raw.melt(id_vars=["year"], value_vars=list(present), var_name="col", value_name="hc")
    long["city"] = long["col"].map(present)
    long["glass_center"] = long["col"].isin(GLASS_COLS)
    long["hc"] = pd.to_numeric(long["hc"], errors="coerce").fillna(0)
    return long


def main() -> None:
    path = _find_file()
    if path is None:
        log("No BHOTMG city human capital file found", OUTPUT_LOGS / "fetch.log")
        return

    long = melt_city_panel(path)
    long.to_csv(DATA_PROCESSED / "bhotmg_city_hc_panel.csv", index=False)

    yearly = (
        long.groupby(["year", "glass_center"], as_index=False)["hc"]
        .sum()
        .rename(columns={"hc": "total_hc"})
    )
    yearly.to_csv(OUTPUT_TABLES / "bhotmg_glass_control_yearly.csv", index=False)

    def period_stats(mask: pd.Series) -> dict:
        sub = long[mask]
        glass = sub[sub["glass_center"]]["hc"].sum()
        ctrl = sub[~sub["glass_center"]]["hc"].sum()
        return {"glass": glass, "control": ctrl, "ratio": glass / ctrl if ctrl else np.nan}

    pre = period_stats(long["year"] < 1300)
    post = period_stats(long["year"] >= 1300)

    # Average annual flow pre/post (years with any activity)
    pre_years = long[long["year"] < 1300]["year"].nunique()
    post_years = long[long["year"] >= 1300]["year"].nunique()

    summary = pd.DataFrame(
        [
            {
                "test": "bhotmg_university_hc_glass_vs_control_1300",
                "glass_hc_pre_1300": round(pre["glass"], 4),
                "glass_hc_post_1300": round(post["glass"], 4),
                "control_hc_pre_1300": round(pre["control"], 4),
                "control_hc_post_1300": round(post["control"], 4),
                "glass_post_pre_ratio": round(post["glass"] / pre["glass"], 4) if pre["glass"] else np.nan,
                "control_post_pre_ratio": round(post["control"] / pre["control"], 4) if pre["control"] else np.nan,
                "glass_over_control_growth": round(
                    (post["glass"] / pre["glass"]) / (post["control"] / pre["control"]), 4
                )
                if pre["glass"] and pre["control"] and post["control"]
                else np.nan,
                "ratio_glass_to_control_pre": round(pre["ratio"], 4),
                "ratio_glass_to_control_post": round(post["ratio"], 4),
                "n_years_pre": pre_years,
                "n_years_post": post_years,
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "bhotmg_summary.csv", index=False)

    log(
        f"BHOTMG: {len(long)} city-years, glass pre/post={pre['glass']:.0f}/{post['glass']:.0f}, "
        f"ratio growth={summary.iloc[0]['glass_over_control_growth']}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
