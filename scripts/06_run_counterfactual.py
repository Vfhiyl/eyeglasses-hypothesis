#!/usr/bin/env python3
"""Counterfactual productivity loss simulation using RCT effect sizes."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import load_yaml, log

ONSET_AGE = 40


def compute_loss(scholars: pd.DataFrame, delta: float, scenario: str) -> dict:
    total_active_years = 0.0
    affected_years = 0.0
    lost_output = 0.0
    n_scholars = len(scholars)

    for _, s in scholars.iterrows():
        start_y = int(s["start_year"])
        end_y = int(s["end_year"])
        birth_y = int(s["birth_year"])
        active_years = max(0, end_y - start_y)
        total_active_years += active_years
        for age in range(start_y - birth_y, end_y - birth_y):
            if age >= ONSET_AGE:
                affected_years += 1
                lost_output += delta

    pct_loss = (lost_output / total_active_years * 100) if total_active_years else 0
    return {
        "scenario": scenario,
        "delta": delta,
        "n_scholars": n_scholars,
        "total_active_years": int(total_active_years),
        "affected_years_40plus": int(affected_years),
        "affected_share_pct": round(affected_years / total_active_years * 100, 2) if total_active_years else 0,
        "lost_output_units": round(lost_output, 2),
        "pct_output_loss": round(pct_loss, 2),
    }


def by_century(scholars: pd.DataFrame, delta: float) -> pd.DataFrame:
    rows = []
    for century in range(1300, 1800, 100):
        mid = century + 50
        # Require career already started by mid-century
        sub = scholars[
            (scholars["birth_year"] <= mid - 25)
            & (scholars["start_year"] <= mid)
            & (scholars["end_year"] >= mid)
        ]
        if len(sub) < 10:
            continue
        r = compute_loss(sub, delta, f"century_{century}")
        r["century"] = century
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> None:
    cfg = load_yaml("rct_effects.yaml")
    scholars = pd.read_csv(DATA_PROCESSED / "rete_scholars_synthetic.csv")
    scholars = scholars[scholars["start_year"] >= 1300]

    scenarios = []
    for name, spec in cfg["scenarios"].items():
        r = compute_loss(scholars, spec["delta"], name)
        r["rct_source"] = spec["source"]
        r["note"] = (
            "illustrative_sensitivity_only; assumes uniform presbyopia onset, "
            "identical RCT delta for medieval text work, full compliance"
        )
        scenarios.append(r)

    scen_df = pd.DataFrame(scenarios)
    scen_df.to_csv(OUTPUT_TABLES / "counterfactual_scenarios.csv", index=False)

    moderate_delta = cfg["scenarios"]["moderate"]["delta"]
    by_c = by_century(scholars, moderate_delta)
    by_c.to_csv(OUTPUT_TABLES / "counterfactual_by_century.csv", index=False)

    log(
        f"Counterfactual: {len(scen_df)} scenarios (sensitivity only) -> {OUTPUT_TABLES}",
        OUTPUT_LOGS / "analysis.log",
    )


if __name__ == "__main__":
    main()
