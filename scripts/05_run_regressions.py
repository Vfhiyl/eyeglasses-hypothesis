#!/usr/bin/env python3
"""Associational regressions (not causal DiD) for glass-center hypothesis."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import get_city_config, log

PANEL = DATA_PROCESSED / "panel_city_century.csv"


def save_summary(result, name: str, note: str = "") -> None:
    path = OUTPUT_TABLES / f"regression_{name}.txt"
    try:
        summary_text = result.summary().as_text()
    except (ValueError, np.linalg.LinAlgError):
        summary_text = str(result.params)
    with open(path, "w", encoding="utf-8") as f:
        if note:
            f.write(note + "\n\n")
        f.write(summary_text)
    coefs = pd.DataFrame(
        {
            "variable": result.params.index,
            "coef": result.params.values,
            "std_err": result.bse.values,
            "p_value": result.pvalues.values,
        }
    )
    coefs.to_csv(OUTPUT_TABLES / f"regression_{name}_coefs.csv", index=False)
    log(f"Saved {path}", OUTPUT_LOGS / "analysis.log")


def model1_active_share() -> None:
    """City-century share 45+ ~ glass_center + century FE.

    NOTE: Does NOT include post_1300 with C(century) — that is perfectly collinear.
    Associational only; synthetic RETE ages.
    """
    scholars = pd.read_csv(DATA_PROCESSED / "rete_scholars_synthetic.csv")
    cities_cfg = get_city_config()
    rows = []
    for century in range(1200, 1800, 100):
        mid = century + 50
        active = scholars[(scholars["start_year"] <= mid) & (scholars["end_year"] >= mid)]
        for city in cities_cfg["city"].unique():
            sub = active[active["city"] == city]
            if len(sub) < 3:
                continue
            ages = mid - sub["birth_year"]
            rows.append(
                {
                    "city": city,
                    "century": century,
                    "period_start": century,
                    "share_45plus": (ages >= 45).mean(),
                    "n_active": len(sub),
                }
            )
    df = pd.DataFrame(rows).merge(cities_cfg, on="city", how="left")
    df["glass_center"] = df["glass_center"].astype(int)
    if len(df) < 15:
        log("Model 1: insufficient data", OUTPUT_LOGS / "analysis.log")
        return
    result = smf.ols(
        "share_45plus ~ glass_center + C(century)",
        data=df,
    ).fit(cov_type="HC1")
    save_summary(
        result,
        "model1_active_share",
        note=(
            "Associational. Formula omits post_1300 (collinear with C(century)). "
            "Synthetic RETE ages; not individual-level binomial GLM."
        ),
    )


def model2_hc_gradient() -> None:
    """HC per capita ~ glass + university + FE; observed coverage only."""
    df = pd.read_csv(PANEL)
    if "hc_observed" in df.columns:
        df = df[df["hc_observed"] == 1]
    df = df[(df["population"].notna()) & (df["population"] > 0)]
    df = df[df["century"].between(1300, 1700)]
    if len(df) < 20:
        log("Model 2: insufficient data", OUTPUT_LOGS / "analysis.log")
        return
    result = smf.ols(
        "log_hc_per_100k ~ glass_center + has_university + C(century) + C(region)",
        data=df,
    ).fit(cov_type="HC1")
    save_summary(
        result,
        "model2_hc_gradient",
        note="Associational city panel; not causal. Observed HC cells only if hc_observed present.",
    )


def model3_istc_cross_section() -> None:
    """15th-c. books ~ glass_center. NOT a DiD (ISTC has no pre-1450 imprint outcomes)."""
    df = pd.read_csv(PANEL)
    # ISTC covers ~1452-1500; period_start 1400 or century 1400/1500 depending on labeling
    if "books_observed" in df.columns:
        df = df[df["books_observed"] == 1]
    else:
        df = df[df["books"] > 0]
    df = df[df["century"].isin([1400, 1500])]
    if len(df) < 10:
        log("Model 3: insufficient book data", OUTPUT_LOGS / "analysis.log")
        return
    result = smf.ols(
        "log_books ~ glass_center + C(region)",
        data=df,
    ).fit(cov_type="HC1")
    save_summary(
        result,
        "model3_did_books",
        note=(
            "NOT DiD. Exploratory 15th-c. cross-section only; ISTC has no pre-1450 period. "
            "Filename kept for pipeline compatibility."
        ),
    )


def main() -> None:
    model1_active_share()
    model2_hc_gradient()
    model3_istc_cross_section()


if __name__ == "__main__":
    main()
