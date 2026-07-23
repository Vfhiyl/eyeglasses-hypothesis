#!/usr/bin/env python3
"""Process curated Ilardi order/price/trade tables into analysis-ready summaries.

Source: Vincent Ilardi, *Renaissance Vision from Spectacles to Telescopes* (APS, 2007),
extracted from Internet Archive OCR (bub_gb_peIL7hVQUmwC), cross-checked against
Ilardi's published translations of the 1462/1466 Sforza letters (RQ 1976).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

ORDERS = ROOT / "data" / "curated" / "ilardi_orders.csv"
PRICES = ROOT / "data" / "curated" / "ilardi_prices.csv"
TRADE = ROOT / "data" / "curated" / "ilardi_trade_volumes.csv"
MAKERS = ROOT / "data" / "curated" / "ilardi_florence_makers.csv"

OUT_ORDERS = DATA_PROCESSED / "ilardi_orders.csv"
OUT_PRICES = DATA_PROCESSED / "ilardi_prices.csv"
OUT_TRADE = DATA_PROCESSED / "ilardi_trade_volumes.csv"
OUT_SUMMARY = OUTPUT_TABLES / "ilardi_adoption_summary.csv"
OUT_VISION = OUTPUT_TABLES / "ilardi_vision_age_band_summary.csv"
OUT_MAKERS = DATA_PROCESSED / "ilardi_florence_makers.csv"


def main() -> None:
    missing = [p for p in (ORDERS, PRICES, TRADE) if not p.exists()]
    if missing:
        log(f"Missing Ilardi curated files: {missing}", OUTPUT_LOGS / "fetch.log")
        return

    orders = pd.read_csv(ORDERS)
    prices = pd.read_csv(PRICES)
    trade = pd.read_csv(TRADE)
    orders.to_csv(OUT_ORDERS, index=False)
    prices.to_csv(OUT_PRICES, index=False)
    trade.to_csv(OUT_TRADE, index=False)

    # Distinct documented court orders (not line items)
    order_heads = (
        orders.groupby("order_id", as_index=False)
        .agg(
            order_date=("order_date", "first"),
            buyer=("buyer", "first"),
            pairs_total=("pairs_total", "first"),
            confidence=("confidence", "first"),
        )
        .sort_values("order_date")
    )
    documented_pairs = pd.to_numeric(order_heads["pairs_total"], errors="coerce").sum()

    price_pairs = prices[prices["item"] == "spectacles"].copy()
    price_pairs["price_per_pair_soldi"] = pd.to_numeric(
        price_pairs["price_per_pair_soldi"], errors="coerce"
    )

    london = trade[trade["place"] == "London"].copy()
    london["pairs"] = pd.to_numeric(london["pairs"], errors="coerce")

    summary = pd.DataFrame(
        [
            {
                "n_order_documents": len(order_heads),
                "n_order_line_items": len(orders),
                "court_pairs_documented_sum": int(documented_pairs),
                "n_price_observations": int((prices["item"] == "spectacles").sum()),
                "price_per_pair_soldi_min": float(price_pairs["price_per_pair_soldi"].min()),
                "price_per_pair_soldi_max": float(price_pairs["price_per_pair_soldi"].max()),
                "london_import_pairs_sum_known_years": int(london["pairs"].sum()),
                "earliest_order_year": int(str(order_heads["order_date"].iloc[0])[:4]),
                "latest_order_year": int(str(order_heads["order_date"].iloc[-1])[:4]),
                "claim_layer": "spectacle_adoption_evidence",
                "identification": "descriptive_micro_orders_and_trade",
                "note": (
                    "Supports diffusion/affordability/age-grading by 1466; "
                    "does NOT identify scholar career extension. "
                    "CORRECTED: 1466 order is 50 pairs (15+15+10+10) per RQ 1976 p.348; "
                    "not 200 (that was a misread of XV-per-age-band)."
                ),
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    # Age-band / vision-class rollup: micro evidence for age-graded near-work tooling (supports A)
    vision = (
        orders.groupby(["order_id", "vision_class", "age_band"], as_index=False)
        .agg(
            line_qty=("line_qty", "sum"),
            pairs_total=("pairs_total", "first"),
            order_date=("order_date", "first"),
            buyer=("buyer", "first"),
        )
        .sort_values(["order_date", "vision_class"])
    )
    vision["presbyopia_near_flag"] = (
        vision["vision_class"]
        .astype(str)
        .str.contains("near|presbyopia|elderly", case=False, regex=True)
        .astype(int)
    )
    vision.to_csv(OUT_VISION, index=False)

    n_makers = 0
    if MAKERS.exists():
        makers = pd.read_csv(MAKERS)
        makers.to_csv(OUT_MAKERS, index=False)
        n_makers = len(makers)
        summary = summary.copy()
        summary["n_florence_makers_appendix_i"] = n_makers
        summary["florence_makers_year_min"] = int(makers["first_attested_year"].min())
        summary["florence_makers_year_max"] = int(makers["first_attested_year"].max())
        summary.to_csv(OUT_SUMMARY, index=False)

    log(
        f"Ilardi: {len(order_heads)} orders, ~{int(documented_pairs)} court pairs, "
        f"London imports sum={int(london['pairs'].sum())}, makers={n_makers}, "
        f"vision_rows={len(vision)} -> {OUT_SUMMARY.name}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
