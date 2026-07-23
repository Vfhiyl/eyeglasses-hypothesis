#!/usr/bin/env python3
"""Fetch RETE Institutions table (376 rows) via Shiny API."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW
from _rete_shiny_fetch import fetch_datatable

COLUMNS = [" ", "IKey", "IName", "EnglishName", "CreationDate", "EndDate", "Headquarter"]
FIELDS = ["row_id", "ikey", "iname", "english_name", "creation_date", "end_date", "headquarter"]


def main() -> None:
    fetch_datatable(
        dataobj="foundInstitutions",
        out_csv=DATA_RAW / "rete_institutions.csv",
        column_names=COLUMNS,
        field_names=FIELDS,
        dedupe_cols=["ikey"],
    )


if __name__ == "__main__":
    main()
