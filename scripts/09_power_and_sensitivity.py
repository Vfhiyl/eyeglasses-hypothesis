#!/usr/bin/env python3
"""Minimum detectable effects, power notes, and sensitivity specs."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

ALPHA = 0.05
POWER = 0.80


def mde_two_proportions(n1: int, n2: int, p0: float = 0.5) -> float:
    """Approx. MDE for difference in proportions (equal variance, two-sided)."""
    if n1 < 5 or n2 < 5:
        return float("nan")
    z_a = stats.norm.ppf(1 - ALPHA / 2)
    z_b = stats.norm.ppf(POWER)
    se = np.sqrt(p0 * (1 - p0) * (1 / n1 + 1 / n2))
    return float((z_a + z_b) * se)


def mde_welch_means(n1: int, n2: int, sd: float) -> float:
    if n1 < 5 or n2 < 5 or not np.isfinite(sd) or sd <= 0:
        return float("nan")
    z_a = stats.norm.ppf(1 - ALPHA / 2)
    z_b = stats.norm.ppf(POWER)
    se = sd * np.sqrt(1 / n1 + 1 / n2)
    return float((z_a + z_b) * se)


def studium_power_rows(df: pd.DataFrame) -> list[dict]:
    age = df.dropna(subset=["age_at_activity_end"])
    age = age[age["life_date_quality"].isin(["interval_meta", "text_range"])]
    rows = []
    for label, lo_pre, hi_pre, lo_post, hi_post in [
        ("local_85y", 1200, 1285, 1300, 1385),
        ("local_50y", 1250, 1299, 1300, 1349),
        ("long_asymmetric", 1100, 1299, 1300, 1700),
    ]:
        pre = age[(age["anchor_year"] >= lo_pre) & (age["anchor_year"] <= hi_pre)]
        post = age[(age["anchor_year"] >= lo_post) & (age["anchor_year"] <= hi_post)]
        p0 = float((pre["age_at_activity_end"] >= 45).mean()) if len(pre) else 0.5
        rows.append(
            {
                "design": f"studium_share45_{label}",
                "n_pre": len(pre),
                "n_post": len(post),
                "baseline_share45": round(p0, 4) if len(pre) else np.nan,
                "mde_share45_pp": round(mde_two_proportions(len(pre), len(post), p0 or 0.5), 4),
                "window": f"{lo_pre}-{hi_pre} vs {lo_post}-{hi_post}",
            }
        )
    return rows


def age_threshold_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
    age = df.dropna(subset=["age_at_activity_end"])
    age = age[age["life_date_quality"].isin(["interval_meta", "text_range"])]
    pre = age[(age["anchor_year"] >= 1200) & (age["anchor_year"] <= 1285)]
    post = age[(age["anchor_year"] >= 1300) & (age["anchor_year"] <= 1385)]
    rows = []
    for thr in (40, 45, 50):
        for subset_name, sub in [
            ("all", age),
            ("masters", age[age["is_master"]]),
            ("non_students", age[~age["is_student"]]),
        ]:
            pre_s = pre if subset_name == "all" else (
                pre[pre["is_master"]] if subset_name == "masters" else pre[~pre["is_student"]]
            )
            post_s = post if subset_name == "all" else (
                post[post["is_master"]] if subset_name == "masters" else post[~post["is_student"]]
            )
            # re-filter from sub with same windows
            pre_s = sub[(sub["anchor_year"] >= 1200) & (sub["anchor_year"] <= 1285)]
            post_s = sub[(sub["anchor_year"] >= 1300) & (sub["anchor_year"] <= 1385)]
            if len(pre_s) < 5 or len(post_s) < 5:
                z, p = np.nan, np.nan
                dshare = np.nan
            else:
                b_pre = pre_s["age_at_activity_end"] >= thr
                b_post = post_s["age_at_activity_end"] >= thr
                p1, p2 = b_pre.mean(), b_post.mean()
                dshare = float(p2 - p1)
                pool = (b_pre.sum() + b_post.sum()) / (len(pre_s) + len(post_s))
                se = np.sqrt(pool * (1 - pool) * (1 / len(pre_s) + 1 / len(post_s)))
                z = (p2 - p1) / se if se > 0 else np.nan
                p = float(2 * (1 - stats.norm.cdf(abs(z)))) if np.isfinite(z) else np.nan
            rows.append(
                {
                    "subset": subset_name,
                    "age_threshold": thr,
                    "share_pre": round(float((pre_s["age_at_activity_end"] >= thr).mean()), 4)
                    if len(pre_s)
                    else np.nan,
                    "share_post": round(float((post_s["age_at_activity_end"] >= thr).mean()), 4)
                    if len(post_s)
                    else np.nan,
                    "diff": round(dshare, 4) if pd.notna(dshare) else np.nan,
                    "z": round(float(z), 4) if pd.notna(z) else np.nan,
                    "p_value": round(float(p), 6) if pd.notna(p) else np.nan,
                    "n_pre": len(pre_s),
                    "n_post": len(post_s),
                }
            )
    return pd.DataFrame(rows)


def panel_hc_mde() -> dict:
    path = DATA_PROCESSED / "panel_city_century.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    if "hc_observed" in df.columns:
        df = df[df["hc_observed"] == 1]
    df = df[(df["population"].notna()) & (df["population"] > 0)]
    df = df[df["century"].between(1300, 1700)]
    y = df["log_hc_per_100k"].dropna()
    n_g = int((df["glass_center"] == 1).sum())
    n_c = int((df["glass_center"] == 0).sum())
    return {
        "design": "panel_log_hc_glass_vs_control",
        "n_glass_cells": n_g,
        "n_control_cells": n_c,
        "sd_log_hc": round(float(y.std()), 4) if len(y) else np.nan,
        "mde_mean_diff_log_hc": round(mde_welch_means(n_g, n_c, float(y.std()) if len(y) else np.nan), 4),
        "note": "crude two-group MDE ignoring FE/clustering; illustrative only",
    }


def main() -> None:
    rows = []
    studium_path = DATA_PROCESSED / "studium_paris_scholars.csv"
    if studium_path.exists():
        sdf = pd.read_csv(studium_path)
        rows.extend(studium_power_rows(sdf))
        sens = age_threshold_sensitivity(sdf)
        sens.to_csv(OUTPUT_TABLES / "sensitivity_age_thresholds.csv", index=False)
        # status split already in studium_local_window; keep span sensitivity
        span = sdf.dropna(subset=["observed_activity_span_years"])
        for label, lo_pre, hi_pre, lo_post, hi_post in [
            ("local_85y", 1200, 1285, 1300, 1385),
            ("local_50y", 1250, 1299, 1300, 1349),
        ]:
            pre = span[(span["anchor_year"] >= lo_pre) & (span["anchor_year"] <= hi_pre)][
                "observed_activity_span_years"
            ]
            post = span[(span["anchor_year"] >= lo_post) & (span["anchor_year"] <= hi_post)][
                "observed_activity_span_years"
            ]
            if len(pre) >= 5 and len(post) >= 5:
                t, p = stats.ttest_ind(post, pre, equal_var=False)
            else:
                t, p = np.nan, np.nan
            rows.append(
                {
                    "design": f"studium_span_{label}",
                    "n_pre": len(pre),
                    "n_post": len(post),
                    "baseline_share45": np.nan,
                    "mde_share45_pp": round(mde_welch_means(len(pre), len(post), float(pd.concat([pre, post]).std())), 4),
                    "window": f"{lo_pre}-{hi_pre} vs {lo_post}-{hi_post}",
                    "span_diff": round(float(post.mean() - pre.mean()), 4) if len(pre) and len(post) else np.nan,
                    "span_p": round(float(p), 6) if pd.notna(p) else np.nan,
                    "span_t": round(float(t), 4) if pd.notna(t) else np.nan,
                }
            )

    hc = panel_hc_mde()
    if hc:
        rows.append(hc)

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_TABLES / "power_mde_summary.csv", index=False)

    checklist = pd.DataFrame(
        [
            {
                "item": "claim_page_eyeglasses_invention",
                "status": "pending_manual",
                "note": "Fill from Macfarlane & Martin paper copy",
            },
            {
                "item": "claim_page_fifteen_years",
                "status": "pending_manual",
                "note": "Book-review paraphrase exists; original page TBD",
            },
            {
                "item": "slogan_not_steam_but_glasses",
                "status": "not_found_in_publisher_blurb",
                "note": "Treat as secondary viral slogan unless page found",
            },
        ]
    )
    checklist.to_csv(OUTPUT_TABLES / "claim_genealogy_checklist.csv", index=False)

    log(f"Power/sensitivity -> {OUTPUT_TABLES / 'power_mde_summary.csv'}", OUTPUT_LOGS / "analysis.log")


if __name__ == "__main__":
    main()
