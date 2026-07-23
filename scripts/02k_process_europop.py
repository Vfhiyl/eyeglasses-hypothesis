#!/usr/bin/env python3
"""Process De Vries europop city populations (1500-1800)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

GLASS_CITIES = {
    "Firenze",
    "Florence",
    "Venezia",
    "Venice",
    "Pisa",
    "Milano",
    "Milan",
    "Nürnberg",
    "Nuremberg",
}


def _read(name: str) -> pd.DataFrame | None:
    for p in (DATA_RAW / name, ROOT.parent / "download_data" / name):
        if p.exists():
            return pd.read_csv(p)
    return None


def main() -> None:
    pop = _read("europop.csv")
    if pop is None:
        log("No europop.csv", OUTPUT_LOGS / "fetch.log")
        return

    pop = pop.rename(columns={"city": "city", "region": "region", "year": "year", "population": "population"})
    pop["population"] = pd.to_numeric(pop["population"], errors="coerce")
    pop["glass_center"] = pop["city"].isin(GLASS_CITIES)
    pop.to_csv(DATA_PROCESSED / "europop_city_year.csv", index=False)

    coords = _read("city_coords.csv")
    if coords is not None:
        coords.to_csv(DATA_PROCESSED / "europop_city_coords.csv", index=False)

    log(f"Europop: {len(pop)} city-year rows", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
