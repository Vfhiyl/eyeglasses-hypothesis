#!/usr/bin/env python3
"""Process Buringh–van Zanden manuscript production (OWID CSV)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "manuscript-production-century.csv",
    DATA_RAW / "manuscript_production_century.csv",
    ROOT.parent / "download_data" / "manuscript-production-century.csv",
    ROOT.parent / "download_data" / "manuscript_production_century.csv",
]

# Avoid double-counting regional aggregates bundled in the OWID export.
EUROPE_ENTITIES = [
    "Austria",
    "Belgium",
    "Bohemia",
    "British Isles",
    "France",
    "Germany",
    "Iberia",
    "Italy",
    "Netherlands",
    "Switzerland",
]

GLASS_REGIONS = {"Italy"}
CONTROL_REGIONS = {
    "France",
    "Germany",
    "British Isles",
    "Iberia",
    "Netherlands",
    "Belgium",
    "Austria",
    "Bohemia",
    "Switzerland",
}


def _find_file() -> Path | None:
    for p in CANDIDATES:
        if p.exists() and p.stat().st_size > 100:
            return p
    return None


def canonical_century(year: int) -> int:
    """Harmonize OWID year labels (France uses mid-century 1250, Italy uses 1200)."""
    return int(year + 50) if year % 100 == 50 else int(year)


def main() -> None:
    path = _find_file()
    if path is None:
        log("No manuscript-production-century.csv found", OUTPUT_LOGS / "fetch.log")
        return

    raw = pd.read_csv(path)
    raw = raw.rename(
        columns={
            "Entity": "entity",
            "Code": "code",
            "Year": "year",
            "Manuscript production per century": "manuscripts",
        }
    )
    raw["canonical_century"] = raw["year"].map(canonical_century)
    raw["manuscripts"] = pd.to_numeric(raw["manuscripts"], errors="coerce").fillna(0)

    region = raw[raw["entity"].isin(EUROPE_ENTITIES)].copy()
    region.to_csv(DATA_PROCESSED / "manuscript_region_century.csv", index=False)

    europe = (
        region.groupby("canonical_century", as_index=False)["manuscripts"]
        .sum()
        .rename(columns={"canonical_century": "century"})
    )
    europe["entity"] = "Europe_West_excl_CentralEurope"
    europe.to_csv(DATA_PROCESSED / "manuscript_europe_century.csv", index=False)

    growth_rows = []
    for entity, sub in region.groupby("entity"):
        sub = sub.sort_values("canonical_century")
        for c0, c1 in [(1100, 1200), (1200, 1300), (1300, 1400)]:
            v0 = sub.loc[sub["canonical_century"] == c0, "manuscripts"]
            v1 = sub.loc[sub["canonical_century"] == c1, "manuscripts"]
            if v0.empty or v1.empty or v0.iloc[0] <= 0:
                continue
            growth_rows.append(
                {
                    "entity": entity,
                    "from_century": c0,
                    "to_century": c1,
                    "manuscripts_from": int(v0.iloc[0]),
                    "manuscripts_to": int(v1.iloc[0]),
                    "pct_growth": round((v1.iloc[0] / v0.iloc[0] - 1) * 100, 2),
                    "glass_region": entity in GLASS_REGIONS,
                }
            )
    growth = pd.DataFrame(growth_rows)
    growth.to_csv(DATA_PROCESSED / "manuscript_growth.csv", index=False)

    g120130 = growth[growth["to_century"] == 1300]
    if len(g120130) >= 2:
        glass = g120130[g120130["glass_region"]]["pct_growth"]
        ctrl = g120130[~g120130["glass_region"]]["pct_growth"]
        ratio = glass.mean() / ctrl.mean() if len(glass) and ctrl.mean() else np.nan
        summary = pd.DataFrame(
            [
                {
                    "test": "italy_vs_control_growth_1200_1300",
                    "italy_pct_growth": round(glass.mean(), 2) if len(glass) else np.nan,
                    "control_mean_pct_growth": round(ctrl.mean(), 2) if len(ctrl) else np.nan,
                    "ratio_italy_to_control": round(ratio, 3) if not np.isnan(ratio) else np.nan,
                    "n_control_regions": len(ctrl),
                }
            ]
        )
        summary.to_csv(DATA_PROCESSED / "manuscript_glass_summary.csv", index=False)

    log(
        f"Manuscripts: {len(region)} region-century rows, Europe total -> "
        f"{DATA_PROCESSED / 'manuscript_europe_century.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
