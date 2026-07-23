#!/usr/bin/env python3
"""Time series aggregation and trend Chow breakpoint tests (equal local windows)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

BREAKPOINTS = [1290, 1450, 1608]
# Equal half-window (years) on each side for comparable breakpoint tests
WINDOW_HALF = 80


def period_start(year: float | int) -> int:
    """Map calendar year to century start: 1452 -> 1400 (1400-1499)."""
    return int(year) // 100 * 100


def chow_trend_test(
    years: np.ndarray,
    values: np.ndarray,
    bp: int,
    *,
    window_half: int | None = WINDOW_HALF,
    use_log: bool = True,
) -> dict:
    """Proper Chow test for structural break in a linear trend.

    Compares restricted model y ~ time vs unrestricted
    y ~ time * post_break (intercept + slope change).
    Uses equal-length local windows when window_half is set.
    """
    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)
    mask = np.isfinite(years) & np.isfinite(values) & (values > 0 if use_log else True)
    years, values = years[mask], values[mask]

    if window_half is not None:
        lo, hi = bp - window_half, bp + window_half
        w = (years >= lo) & (years < hi)
        years, values = years[w], values[w]

    pre = years < bp
    post = ~pre
    if pre.sum() < 8 or post.sum() < 8:
        return {
            "breakpoint": bp,
            "f_stat": np.nan,
            "p_value": np.nan,
            "n_pre": int(pre.sum()),
            "n_post": int(post.sum()),
            "window_half": window_half,
            "note": "insufficient_local_sample",
        }

    y = np.log(values) if use_log else values
    t = years - bp  # center at breakpoint
    df = pd.DataFrame({"y": y, "t": t, "post": post.astype(int)})

    # Restricted: common intercept and slope
    r_res = smf.ols("y ~ t", data=df).fit()
    # Unrestricted: intercept and slope shift after break
    u_res = smf.ols("y ~ t + post + t:post", data=df).fit()

    rss_r = float(r_res.ssr)
    rss_u = float(u_res.ssr)
    k = 2  # extra parameters in unrestricted (post, t:post)
    n = len(df)
    denom = n - 4  # unrestricted has 4 params
    if denom <= 0 or rss_u <= 0:
        f_stat = np.nan
        p_value = np.nan
    else:
        f_stat = ((rss_r - rss_u) / k) / (rss_u / denom)
        p_value = float(1 - stats.f.cdf(f_stat, k, denom))

    # Slope change (post interaction) as effect of interest
    slope_change = float(u_res.params.get("t:post", np.nan))
    intercept_change = float(u_res.params.get("post", np.nan))

    return {
        "breakpoint": bp,
        "f_stat": round(float(f_stat), 4) if np.isfinite(f_stat) else np.nan,
        "p_value": round(float(p_value), 6) if np.isfinite(p_value) else np.nan,
        "slope_change": round(slope_change, 6) if np.isfinite(slope_change) else np.nan,
        "intercept_change": round(intercept_change, 6) if np.isfinite(intercept_change) else np.nan,
        "mean_pre": round(float(values[pre].mean()), 4),
        "mean_post": round(float(values[post].mean()), 4),
        # Keep pct_change for continuity but mark as descriptive only
        "pct_change": round((values[post].mean() / values[pre].mean() - 1) * 100, 2)
        if values[pre].mean()
        else np.nan,
        "n_pre": int(pre.sum()),
        "n_post": int(post.sum()),
        "window_half": window_half,
        "method": "trend_chow_log_local_window",
    }


def _manuscript_breakpoints() -> None:
    path = DATA_PROCESSED / "manuscript_europe_century.csv"
    if not path.exists():
        return
    ms = pd.read_csv(path).sort_values("century")
    rows = []
    # Century series: use full sample (few points); no local year window
    for bp in BREAKPOINTS:
        r = chow_trend_test(
            ms["century"].values.astype(float),
            ms["manuscripts"].values.astype(float),
            bp,
            window_half=None,
        )
        r["series"] = "manuscripts_europe"
        rows.append(r)
    sub = ms[ms["century"].between(1100, 1400)]
    for c0, c1 in [(1100, 1200), (1200, 1300), (1300, 1400)]:
        v0 = sub.loc[sub["century"] == c0, "manuscripts"]
        v1 = sub.loc[sub["century"] == c1, "manuscripts"]
        if v0.empty or v1.empty or v0.iloc[0] <= 0:
            continue
        rows.append(
            {
                "series": "manuscripts_europe",
                "breakpoint": c1,
                "f_stat": np.nan,
                "p_value": np.nan,
                "mean_pre": float(v0.iloc[0]),
                "mean_post": float(v1.iloc[0]),
                "pct_change": round((v1.iloc[0] / v0.iloc[0] - 1) * 100, 2),
                "n_pre": 1,
                "n_post": 1,
                "note": f"growth_{c0}_{c1}",
                "method": "century_pair_growth_descriptive",
            }
        )
    pd.DataFrame(rows).to_csv(OUTPUT_TABLES / "manuscript_breakpoint_tests.csv", index=False)

    glass_path = DATA_PROCESSED / "manuscript_glass_summary.csv"
    if glass_path.exists():
        pd.read_csv(glass_path).to_csv(OUTPUT_TABLES / "manuscript_glass_summary.csv", index=False)


def _ha_science_breakpoints() -> None:
    path = DATA_PROCESSED / "ha_science_by_century.csv"
    if not path.exists():
        return
    ha = pd.read_csv(path)
    ha = ha[ha["century"].between(1100, 1800)].sort_values("century")
    if len(ha) < 4:
        return
    rows = []
    for bp in BREAKPOINTS:
        r = chow_trend_test(
            ha["century"].values.astype(float),
            ha["persons"].values.astype(float),
            bp,
            window_half=None,
        )
        r["series"] = "ha_science_persons"
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUTPUT_TABLES / "ha_breakpoint_tests.csv", index=False)
    ha.to_csv(OUTPUT_TABLES / "ha_science_by_century.csv", index=False)


def _printed_books_breakpoints() -> None:
    path = DATA_PROCESSED / "printed_books_europe_halfcentury.csv"
    if not path.exists():
        return
    books = pd.read_csv(path).sort_values("year")
    rows = []
    for bp in BREAKPOINTS:
        r = chow_trend_test(
            books["year"].values.astype(float),
            books["books"].values.astype(float),
            bp,
            window_half=None,
        )
        r["series"] = "printed_books_europe"
        rows.append(r)
    pd.DataFrame(rows).to_csv(OUTPUT_TABLES / "printed_books_breakpoint_tests.csv", index=False)


def active_age_analysis() -> pd.DataFrame:
    scholars = pd.read_csv(DATA_PROCESSED / "rete_scholars_synthetic.csv")
    rows = []
    for century in range(1200, 1800, 100):
        mid = century + 50
        active = scholars[(scholars["start_year"] <= mid) & (scholars["end_year"] >= mid)]
        if len(active) < 10:
            continue
        ages = mid - active["birth_year"]
        rows.append(
            {
                "period_start": century,
                "century": century,
                "year": mid,
                "active_scholars": len(active),
                "share_45plus": (ages >= 45).mean(),
            }
        )
    df = pd.DataFrame(rows)
    pre = df[df["century"] < 1300]["share_45plus"]
    post = df[df["century"] >= 1300]["share_45plus"]
    if len(pre) >= 2 and len(post) >= 2:
        t_stat, p_val = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t_stat, p_val = np.nan, np.nan
    ttest_row = pd.DataFrame(
        [
            {
                "test": "active_share_45plus_pre_vs_post_1300",
                "mean_pre_1300": round(pre.mean(), 4) if len(pre) else np.nan,
                "mean_post_1300": round(post.mean(), 4) if len(post) else np.nan,
                "t_stat": round(t_stat, 4) if not np.isnan(t_stat) else np.nan,
                "p_value": round(p_val, 6) if not np.isnan(p_val) else np.nan,
                "n_pre": len(pre),
                "n_post": len(post),
                "note": "synthetic_rete_proxy; century-level shares",
            }
        ]
    )
    ttest_row.to_csv(OUTPUT_TABLES / "active_age_ttest.csv", index=False)
    df.to_csv(OUTPUT_TABLES / "active_age_share.csv", index=False)
    return df


def main() -> None:
    rete_yr = pd.read_csv(DATA_PROCESSED / "rete_city_year.csv")
    europe_hc = rete_yr.groupby("year", as_index=False)["human_capital"].sum()
    europe_hc.to_csv(OUTPUT_TABLES / "scholars_by_year.csv", index=False)
    century_hc = pd.read_csv(DATA_PROCESSED / "rete_city_century.csv")
    century_hc.groupby("century")["human_capital"].sum().reset_index().to_csv(
        OUTPUT_TABLES / "scholars_by_century.csv", index=False
    )

    istc = pd.read_csv(DATA_PROCESSED / "istc_city_year.csv")
    books_yr = istc.groupby("year", as_index=False)["book_count"].sum()
    books_yr.to_csv(OUTPUT_TABLES / "books_by_year.csv", index=False)
    istc.assign(century=istc["year"].map(period_start)).groupby("century")["book_count"].sum().reset_index().to_csv(
        OUTPUT_TABLES / "books_by_century.csv", index=False
    )

    bp_results = []
    for series_name, df, col, year_col in [
        ("human_capital", europe_hc, "human_capital", "year"),
        ("book_count", books_yr, "book_count", "year"),
    ]:
        years = df[year_col].values.astype(float)
        vals = df[col].values.astype(float)
        for bp in BREAKPOINTS:
            r = chow_trend_test(years, vals, bp, window_half=WINDOW_HALF)
            r["series"] = series_name
            bp_results.append(r)
    bp_df = pd.DataFrame(bp_results)
    bp_df.to_csv(OUTPUT_TABLES / "breakpoint_tests.csv", index=False)

    _manuscript_breakpoints()
    _ha_science_breakpoints()
    _printed_books_breakpoints()
    active_age_analysis()
    log(f"Timeseries done (trend Chow, window±{WINDOW_HALF}) -> {OUTPUT_TABLES}", OUTPUT_LOGS / "analysis.log")


if __name__ == "__main__":
    main()
