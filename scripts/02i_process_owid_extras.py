#!/usr/bin/env python3
"""Process additional OWID exports: printed books and literacy."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

EUROPE_PRINT = [
    "Belgium",
    "France",
    "Germany",
    "Great Britain",
    "Ireland",
    "Italy",
    "Netherlands",
    "Spain",
    "Switzerland",
    "Sweden",
    "Poland",
]


def _read(name: str) -> pd.DataFrame | None:
    for p in (DATA_RAW / name, ROOT.parent / "download_data" / name):
        if p.exists():
            return pd.read_csv(p)
    return None


def main() -> None:
    books = _read("production-printed-books-half-century.csv")
    if books is not None:
        books = books.rename(
            columns={
                "Entity": "entity",
                "Code": "code",
                "Year": "year",
                "Production of printed books per half century": "books",
            }
        )
        books["books"] = pd.to_numeric(books["books"], errors="coerce").fillna(0)
        books.to_csv(DATA_PROCESSED / "printed_books_region_halfcentury.csv", index=False)
        west = books[books["entity"].isin(EUROPE_PRINT)]
        agg = west.groupby("year", as_index=False)["books"].sum()
        agg["entity"] = "Europe_West"
        agg.to_csv(DATA_PROCESSED / "printed_books_europe_halfcentury.csv", index=False)

    lit = _read("cross-country-literacy-rates.csv")
    if lit is not None:
        lit = lit.rename(
            columns={"Entity": "entity", "Code": "code", "Year": "year", "Literacy rate": "literacy"}
        )
        lit["literacy"] = pd.to_numeric(lit["literacy"], errors="coerce")
        lit.to_csv(DATA_PROCESSED / "literacy_country_year.csv", index=False)
        eu = lit[lit["entity"].isin(["Italy", "France", "Germany", "United Kingdom", "Netherlands", "Spain"])]
        eu.to_csv(DATA_PROCESSED / "literacy_europe_major.csv", index=False)

    log("OWID extras processed", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
