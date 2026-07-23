#!/usr/bin/env python3
"""Fetch RETE Activities (scholar×institution appointments) via Shiny API."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW
from _rete_shiny_fetch import fetch_datatable

COLUMNS = [
    " ",
    "PKey",
    "IKey",
    "Field",
    "Beginning",
    "End",
    "DateApprox",
    "SKey1",
    "SKey2",
    "SKey3",
    "SKey4",
    "SKey5",
    "note",
    "WeakLink",
]
FIELDS = [
    "row_id",
    "pkey",
    "ikey",
    "field",
    "beginning",
    "end",
    "date_approx",
    "skey1",
    "skey2",
    "skey3",
    "skey4",
    "skey5",
    "note",
    "weak_link",
]


def main() -> None:
    fetch_datatable(
        dataobj="foundActivities",
        out_csv=DATA_RAW / "rete_activities.csv",
        column_names=COLUMNS,
        field_names=FIELDS,
        dedupe_cols=["pkey", "ikey", "beginning", "end", "field"],
    )


if __name__ == "__main__":
    main()
