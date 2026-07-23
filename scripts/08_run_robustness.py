#!/usr/bin/env python3
"""Robustness checks (exploratory / associational; not causal DiD)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import get_city_config, is_config_glass_city, log


def breakpoint_comparison() -> pd.DataFrame:
    """Compare trend-Chow F/p at equal local windows (from 04_run_timeseries)."""
    bp = pd.read_csv(OUTPUT_TABLES / "breakpoint_tests.csv")
    hc = bp[bp["series"] == "human_capital"].copy()
    rows = []
    for _, r in hc.iterrows():
        rows.append(
            {
                "breakpoint": r["breakpoint"],
                "f_stat": r["f_stat"],
                "p_value": r["p_value"],
                "slope_change": r.get("slope_change", np.nan),
                "pct_change": r.get("pct_change", np.nan),
                "mean_pre": r.get("mean_pre", np.nan),
                "mean_post": r.get("mean_post", np.nan),
                "window_half": r.get("window_half", np.nan),
                "method": r.get("method", ""),
            }
        )
    df = pd.DataFrame(rows)
    if len(df) >= 2 and "slope_change" in df.columns:
        r1290 = df[df["breakpoint"] == 1290]
        r1450 = df[df["breakpoint"] == 1450]
        if len(r1290) and len(r1450):
            # Prefer |slope_change| or f_stat under equal windows — not raw pct_change
            s1290 = abs(float(r1290["slope_change"].iloc[0])) if pd.notna(r1290["slope_change"].iloc[0]) else np.nan
            s1450 = abs(float(r1450["slope_change"].iloc[0])) if pd.notna(r1450["slope_change"].iloc[0]) else np.nan
            df["note"] = ""
            if pd.notna(s1290) and pd.notna(s1450):
                df.loc[df["breakpoint"] == 1290, "note"] = (
                    "weaker_slope_change_than_1450" if s1290 < s1450 else "stronger_slope_change_than_1450"
                )
            else:
                df.loc[df["breakpoint"] == 1290, "note"] = "comparison_inconclusive"
    df.to_csv(OUTPUT_TABLES / "robust_breakpoint_comparison.csv", index=False)
    return df


def within_italy_regression() -> None:
    panel = pd.read_csv(DATA_PROCESSED / "panel_city_century.csv")
    italy = panel[panel["region"] == "Italy"].copy()
    italy = italy[italy["century"].between(1300, 1700)]
    if "hc_observed" in italy.columns:
        italy = italy[italy["hc_observed"] == 1]
    italy = italy[(italy["population"].notna()) & (italy["population"] > 0)]
    if len(italy) < 15:
        log("Within-Italy: insufficient data", OUTPUT_LOGS / "robust.log")
        return
    result = smf.ols(
        "log_hc_per_100k ~ glass_center + has_university + C(century)",
        data=italy,
    ).fit(cov_type="HC1")
    with open(OUTPUT_TABLES / "robust_within_italy.txt", "w") as f:
        f.write("Associational within-Italy; not causal.\n\n")
        f.write(result.summary().as_text())
    pd.DataFrame(
        {
            "variable": result.params.index,
            "coef": result.params.values,
            "p_value": result.pvalues.values,
        }
    ).to_csv(OUTPUT_TABLES / "robust_within_italy_coefs.csv", index=False)


def pre_trend_test() -> pd.DataFrame:
    cy = pd.read_csv(DATA_PROCESSED / "rete_city_year.csv")
    cities = get_city_config()
    cy = cy.merge(cities[["city", "glass_center"]], on="city", how="left")
    cy = cy[cy["year"].between(1200, 1299)]
    cy["glass_center"] = cy["glass_center"].fillna(False).astype(int)

    rows = []
    for city in cy["city"].unique():
        sub = cy[cy["city"] == city].sort_values("year")
        if len(sub) < 50:
            continue
        slope, _, _, p, _ = stats.linregress(sub["year"], sub["human_capital"])
        rows.append(
            {
                "city": city,
                "glass_center": sub["glass_center"].iloc[0],
                "hc_growth_slope": slope,
                "mean_hc": sub["human_capital"].mean(),
            }
        )
    df = pd.DataFrame(rows)
    glass = df[df["glass_center"] == 1]["hc_growth_slope"]
    ctrl = df[df["glass_center"] == 0]["hc_growth_slope"]
    if len(glass) >= 2 and len(ctrl) >= 2:
        t, p = stats.ttest_ind(glass, ctrl, equal_var=False)
        test = pd.DataFrame(
            [
                {
                    "test": "pre1300_hc_growth_glass_vs_control",
                    "mean_glass_slope": glass.mean(),
                    "mean_control_slope": ctrl.mean(),
                    "t_stat": t,
                    "p_value": p,
                    "parallel_pretrends": p > 0.05,
                    "note": "non_rejection_is_not_support",
                }
            ]
        )
        test.to_csv(OUTPUT_TABLES / "robust_pretrend_test.csv", index=False)
    df.to_csv(OUTPUT_TABLES / "robust_pretrend_slopes.csv", index=False)
    return df


def exclude_top_glass_robustness() -> None:
    panel = pd.read_csv(DATA_PROCESSED / "panel_city_century.csv")
    panel = panel[~panel["city"].isin(["Florence", "Venice", "Murano"])]
    if "hc_observed" in panel.columns:
        panel = panel[panel["hc_observed"] == 1]
    panel = panel[(panel["population"].notna()) & (panel["population"] > 0)]
    panel = panel[panel["century"].between(1300, 1700)]
    if len(panel) < 20:
        return
    result = smf.ols(
        "log_hc_per_100k ~ glass_center + has_university + C(century) + C(region)",
        data=panel,
    ).fit(cov_type="HC1")
    pd.DataFrame(
        {
            "variable": result.params.index,
            "coef": result.params.values,
            "p_value": result.pvalues.values,
        }
    ).to_csv(OUTPUT_TABLES / "robust_exclude_florence_venice_coefs.csv", index=False)


def glass_timing_exploratory() -> None:
    """Exploratory event-time association — NOT staggered DiD / TWFE claim."""
    panel = pd.read_csv(DATA_PROCESSED / "panel_city_century.csv")
    panel["treat_year"] = panel["year_first_spectacles"].fillna(panel["year_first_guild"])
    panel = panel[panel["treat_year"].notna() | (panel["glass_center"] == 0)]
    panel["post_treat"] = (panel["century"] >= panel["treat_year"].fillna(9999)).astype(int)
    panel["treated"] = panel["glass_center"].fillna(0).astype(int)
    if "hc_observed" in panel.columns:
        panel = panel[panel["hc_observed"] == 1]
    panel = panel[(panel["population"].notna()) & (panel["population"] > 0)]
    panel = panel[panel["century"].between(1300, 1700)]

    # City FE absorbs treated; interaction is the object of interest
    result = smf.ols(
        "log_hc_per_100k ~ treated:post_treat + has_university + C(city) + C(century)",
        data=panel,
    ).fit(cov_type="HC1")
    with open(OUTPUT_TABLES / "robust_glass_timing_did.txt", "w") as f:
        f.write(
            "EXPLORATORY only — not Callaway-Sant'Anna / Sun-Abraham staggered DiD.\n"
            "Coarse century treatment timing; few treated cities.\n\n"
        )
        f.write(result.summary().as_text())
    pd.DataFrame(
        {
            "variable": result.params.index,
            "coef": result.params.values,
            "p_value": result.pvalues.values,
        }
    ).to_csv(OUTPUT_TABLES / "robust_glass_timing_did_coefs.csv", index=False)


def istc_glass_vs_control() -> None:
    istc_path = DATA_PROCESSED / "istc_city_century.csv"
    cities = get_city_config()
    glass_names = {c.lower() for c in cities[cities["glass_center"]]["city"]}

    if istc_path.exists():
        istc = pd.read_csv(istc_path)
        # period_start 1400 = 1400-1499
        istc15 = istc[istc["century"] == 1400].groupby("city")["book_count"].sum().reset_index()
        if istc15.empty:
            istc15 = istc[istc["century"].isin([1400, 1500])].groupby("city")["book_count"].sum().reset_index()
        istc15["glass_center"] = istc15["city"].map(lambda c: is_config_glass_city(c, glass_names))
        source = "istc_official_2025_period_start_1400"
    else:
        totals = pd.read_csv(
            Path(__file__).resolve().parent.parent / "data/external/istc_city_totals_published.csv",
            comment="#",
        )
        istc15 = totals.drop_duplicates(subset=["city"]).rename(columns={"total_incunabula": "book_count"})
        istc15["glass_center"] = istc15["glass_center"].astype(bool)
        source = "published_totals"

    glass = istc15[istc15["glass_center"]]["book_count"]
    ctrl = istc15[~istc15["glass_center"]]["book_count"]
    t, p = stats.ttest_ind(glass, ctrl, equal_var=False)
    ratio = glass.mean() / ctrl.mean() if ctrl.mean() else np.nan
    pd.DataFrame(
        [
            {
                "test": "istc_glass_vs_control",
                "source": source,
                "mean_glass": glass.mean(),
                "mean_control": ctrl.mean(),
                "ratio_glass_to_control": ratio,
                "t_stat": t,
                "p_value": p,
                "n_glass": len(glass),
                "n_control": len(ctrl),
                "total_glass_editions": glass.sum(),
                "total_control_editions": ctrl.sum(),
                "note": "cross_section_associational_not_did",
            }
        ]
    ).to_csv(OUTPUT_TABLES / "robust_istc_glass_vs_control.csv", index=False)


def main() -> None:
    breakpoint_comparison()
    within_italy_regression()
    pre_trend_test()
    exclude_top_glass_robustness()
    glass_timing_exploratory()
    istc_glass_vs_control()
    log("Robustness checks complete", OUTPUT_LOGS / "robust.log")


if __name__ == "__main__":
    main()
