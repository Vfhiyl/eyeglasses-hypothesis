#!/usr/bin/env python3
"""Build adoption timeline from curated primary/secondary spectacle mentions."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CURATED = ROOT / "data" / "curated" / "spectacle_primary_mentions.csv"
ILARDI_SUMMARY = OUTPUT_TABLES / "ilardi_adoption_summary.csv"
OUT_TIMELINE = DATA_PROCESSED / "spectacle_adoption_timeline.csv"
OUT_SUMMARY = OUTPUT_TABLES / "spectacle_adoption_summary.csv"


def main() -> None:
    if not CURATED.exists():
        log(f"Missing {CURATED}", OUTPUT_LOGS / "fetch.log")
        return

    df = pd.read_csv(CURATED)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["year_end"] = pd.to_numeric(df["year_end"], errors="coerce")
    df["year_end"] = df["year_end"].fillna(df["year"])
    df["glass_center"] = df["glass_center"].astype(int)
    df.to_csv(OUT_TIMELINE, index=False)

    pre1300 = df[df["year"] < 1300]
    post1300 = df[df["year"] >= 1300]
    glass = df[df["glass_center"] == 1]
    physical = df[df["mention_type"].isin({"physical_trace", "ownership", "depiction", "bulk_order", "trade_volume", "price"})]

    row = {
        "n_records_total": len(df),
        "n_pre_1300": len(pre1300),
        "n_post_1300": len(post1300),
        "n_glass_center_city": len(glass),
        "n_physical_or_ownership": len(physical),
        "earliest_year": int(df["year"].min()),
        "latest_year_end": int(df["year_end"].max()),
        "claim_layer": "spectacle_adoption_evidence",
        "note": "Curated mentions + Ilardi orders/prices/trade where available; descriptive not ID panel",
    }
    if ILARDI_SUMMARY.exists():
        il = pd.read_csv(ILARDI_SUMMARY).iloc[0]
        row.update(
            {
                "ilardi_court_pairs_documented": int(il["court_pairs_documented_sum"]),
                "ilardi_london_import_pairs_sum": int(il["london_import_pairs_sum_known_years"]),
                "ilardi_price_soldi_min": float(il["price_per_pair_soldi_min"]),
                "ilardi_price_soldi_max": float(il["price_per_pair_soldi_max"]),
                "ilardi_order_docs": int(il["n_order_documents"]),
            }
        )
        row["note"] = (
            f"Ilardi RQ1976-corrected court orders ~{int(il['court_pairs_documented_sum'])} pairs "
            f"(1462:54 + 1466:50 + extras); London customs cited sum "
            f"{int(il['london_import_pairs_sum_known_years'])}; "
            f"Florence prices ~{float(il['price_per_pair_soldi_min']):.2f}-"
            f"{float(il['price_per_pair_soldi_max']):.1f} soldi/pair. "
            "Supports diffusion/affordability/age-grading; not career-year identification."
        )

    summary = pd.DataFrame([row])
    summary.to_csv(OUT_SUMMARY, index=False)
    log(
        f"spectacle_adoption: {len(df)} curated rows, earliest {df['year'].min():.0f} -> {OUT_TIMELINE}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
