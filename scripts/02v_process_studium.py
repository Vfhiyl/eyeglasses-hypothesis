#!/usr/bin/env python3
"""Process Studium Parisiense with cautious life/activity parsing."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "studium_persons.jsonl",
    ROOT.parent / "download_data" / "studium_persons.jsonl",
]

YEAR_RE = re.compile(r"\b(1[0-9]{3}|2[0-9]{3})\b")
# Local windows for eyeglasses-era comparison (not 1100-1700 dump)
LOCAL_PRE = (1200, 1285)
LOCAL_POST = (1300, 1385)


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 100_000:
            return path
    return None


def _years_from_meta(item: dict) -> list[int]:
    years: list[int] = []
    for block in item.get("meta", {}).get("dates", []):
        if block.get("type") == "SIMPLE" and block.get("date") is not None:
            years.append(int(block["date"]))
        elif block.get("type") == "INTERVAL":
            for key in ("startDate", "endDate"):
                sub = block.get(key) or {}
                if sub.get("type") == "SIMPLE" and sub.get("date") is not None:
                    years.append(int(sub["date"]))
    if not years:
        for match in YEAR_RE.findall(str(item.get("value", ""))):
            years.append(int(match))
    return [y for y in years if 1100 <= y <= 1700]


def _first_value(section: dict | None, key: str) -> str | None:
    if not section:
        return None
    items = section.get(key) or []
    if not items:
        return None
    val = items[0].get("value")
    if val is None:
        return None
    return str(val).strip() or None


def _year_span(items: list[dict]) -> tuple[int | None, int | None]:
    years: list[int] = []
    for item in items:
        years.extend(_years_from_meta(item))
    if not years:
        return None, None
    return min(years), max(years)


def _parse_life_years(life_items: list[dict]) -> tuple[int | None, int | None, str]:
    """Parse datesOfLife carefully.

    Only assign birth/death when interval meta exists with two endpoints,
    or value text clearly has birth-death pattern. Single year alone is
    marked uncertain (not treated as birth).
    """
    if not life_items:
        return None, None, "missing"

    all_years: list[int] = []
    interval_starts: list[int] = []
    interval_ends: list[int] = []
    for item in life_items:
        for block in item.get("meta", {}).get("dates", []):
            if block.get("type") == "INTERVAL":
                s = (block.get("startDate") or {}).get("date")
                e = (block.get("endDate") or {}).get("date")
                if s is not None:
                    interval_starts.append(int(s))
                if e is not None:
                    interval_ends.append(int(e))
            elif block.get("type") == "SIMPLE" and block.get("date") is not None:
                all_years.append(int(block["date"]))
        all_years.extend(_years_from_meta(item))

    if interval_starts and interval_ends:
        return min(interval_starts), max(interval_ends), "interval_meta"

    # Value like "%1245-1316%"
    for item in life_items:
        text = str(item.get("value", ""))
        pair = re.findall(r"(1[0-9]{3})\s*[-–]\s*(1[0-9]{3})", text)
        if pair:
            a, b = int(pair[0][0]), int(pair[0][1])
            if a < b:
                return a, b, "text_range"

    years = sorted({y for y in all_years if 1100 <= y <= 1700})
    if len(years) >= 2:
        return min(years), max(years), "multi_year_uncertain"
    if len(years) == 1:
        # Do NOT treat single year as birth
        return None, years[0], "single_year_not_birth"
    return None, None, "unparsed"


def flatten_record(rec: dict) -> dict:
    identity = rec.get("identity") or {}
    act_items = identity.get("datesOfActivity") or []
    med_items = identity.get("activityMediane") or []
    life_items = identity.get("datesOfLife") or []

    act_start, act_end = _year_span(act_items)
    med_years: list[int] = []
    for item in med_items:
        med_years.extend(_years_from_meta(item))
    activity_median = int(np.median(med_years)) if med_years else None
    birth_year, death_year, life_quality = _parse_life_years(life_items)

    anchor = activity_median or act_start or act_end
    age_at_act_end = (act_end - birth_year) if act_end and birth_year else None
    # Observed record span — NOT career duration
    observed_activity_span_years = (
        (act_end - act_start) if act_end and act_start and act_end >= act_start else None
    )

    status_raw = _first_value(identity, "status")
    is_master = bool(status_raw and re.search(r"ma[iî]tre", status_raw, re.I))
    is_student = bool(status_raw and re.search(r"tudiant|étudiant", status_raw, re.I))

    return {
        "studium_id": rec.get("_id"),
        "reference": rec.get("reference"),
        "status": status_raw,
        "is_master": is_master,
        "is_student": is_student,
        "birth_year": birth_year,
        "death_year": death_year,
        "life_date_quality": life_quality,
        "activity_start": act_start,
        "activity_end": act_end,
        "activity_median": activity_median,
        "anchor_year": anchor,
        "observed_activity_span_years": observed_activity_span_years,
        "career_span_years": observed_activity_span_years,  # deprecated alias
        "age_at_activity_end": age_at_act_end,
        "active_past_45": bool(age_at_act_end is not None and age_at_act_end >= 45),
    }


def _in_window(df: pd.DataFrame, lo: int, hi: int) -> pd.DataFrame:
    return df[(df["anchor_year"] >= lo) & (df["anchor_year"] <= hi)]


def _proportion_test(pre_bool: pd.Series, post_bool: pd.Series) -> tuple[float, float]:
    """Two-proportion z-test for share45."""
    n1, n2 = len(pre_bool), len(post_bool)
    if n1 < 5 or n2 < 5:
        return np.nan, np.nan
    p1, p2 = pre_bool.mean(), post_bool.mean()
    p_pool = (pre_bool.sum() + post_bool.sum()) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return np.nan, np.nan
    z = (p2 - p1) / se
    p_val = float(2 * (1 - stats.norm.cdf(abs(z))))
    return float(z), p_val


def _window_stats(df: pd.DataFrame, label: str) -> dict:
    pre = _in_window(df, *LOCAL_PRE)
    post = _in_window(df, *LOCAL_POST)

    age_df = df.dropna(subset=["age_at_activity_end"])
    # Only trustworthy life dates for age
    age_df = age_df[age_df["life_date_quality"].isin(["interval_meta", "text_range"])]
    pre_age = _in_window(age_df, *LOCAL_PRE)["age_at_activity_end"]
    post_age = _in_window(age_df, *LOCAL_POST)["age_at_activity_end"]

    share45_pre = (pre_age >= 45).mean() if len(pre_age) else np.nan
    share45_post = (post_age >= 45).mean() if len(post_age) else np.nan
    if len(pre_age) >= 5 and len(post_age) >= 5:
        z_prop, p_prop = _proportion_test(pre_age >= 45, post_age >= 45)
        t_age, p_age = stats.ttest_ind(post_age, pre_age, equal_var=False)
    else:
        z_prop, p_prop, t_age, p_age = np.nan, np.nan, np.nan, np.nan

    span_df = df.dropna(subset=["observed_activity_span_years"])
    pre_span = _in_window(span_df, *LOCAL_PRE)["observed_activity_span_years"]
    post_span = _in_window(span_df, *LOCAL_POST)["observed_activity_span_years"]
    if len(pre_span) >= 5 and len(post_span) >= 5:
        t_span, p_span = stats.ttest_ind(post_span, pre_span, equal_var=False)
    else:
        t_span, p_span = np.nan, np.nan

    return {
        "subset": label,
        "n_pre_local": int(len(pre)),
        "n_post_local": int(len(post)),
        "share45_pre": round(float(share45_pre), 4) if pd.notna(share45_pre) else np.nan,
        "share45_post": round(float(share45_post), 4) if pd.notna(share45_post) else np.nan,
        "share45_prop_z": round(float(z_prop), 4) if pd.notna(z_prop) else np.nan,
        "share45_prop_p": round(float(p_prop), 6) if pd.notna(p_prop) else np.nan,
        "mean_age_pre": round(float(pre_age.mean()), 4) if len(pre_age) else np.nan,
        "mean_age_post": round(float(post_age.mean()), 4) if len(post_age) else np.nan,
        "mean_age_t": round(float(t_age), 4) if pd.notna(t_age) else np.nan,
        "mean_age_p": round(float(p_age), 6) if pd.notna(p_age) else np.nan,
        "n_age_pre": int(len(pre_age)),
        "n_age_post": int(len(post_age)),
        "mean_observed_span_pre": round(float(pre_span.mean()), 4) if len(pre_span) else np.nan,
        "mean_observed_span_post": round(float(post_span.mean()), 4) if len(post_span) else np.nan,
        "span_p": round(float(p_span), 6) if pd.notna(p_span) else np.nan,
        "n_span_pre": int(len(pre_span)),
        "n_span_post": int(len(post_span)),
        "window": f"{LOCAL_PRE[0]}-{LOCAL_PRE[1]} vs {LOCAL_POST[0]}-{LOCAL_POST[1]}",
    }


def main() -> None:
    path = _find_file()
    if path is None:
        log("No studium_persons.jsonl found; run 02u_fetch_studium.py first", OUTPUT_LOGS / "fetch.log")
        return

    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(flatten_record(json.loads(line)))

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["anchor_year"])
    df.to_csv(DATA_PROCESSED / "studium_paris_scholars.csv", index=False)

    yearly = df.groupby("anchor_year", as_index=False).size().rename(columns={"size": "n_scholars"})
    yearly.to_csv(OUTPUT_TABLES / "studium_yearly_counts.csv", index=False)

    # Long-period descriptive volume (background only)
    pre_all = df[df["anchor_year"] < 1300]
    post_all = df[df["anchor_year"] >= 1300]

    subset_rows = [
        _window_stats(df, "all"),
        _window_stats(df[df["is_master"]], "masters"),
        _window_stats(df[df["is_student"]], "students"),
        _window_stats(df[~df["is_student"]], "non_students"),
    ]
    subset_df = pd.DataFrame(subset_rows)
    subset_df.to_csv(OUTPUT_TABLES / "studium_local_window_by_status.csv", index=False)

    all_stats = subset_rows[0]
    summary = pd.DataFrame(
        [
            {
                "test": "studium_paris_volume_pre_vs_post_1300",
                "n_pre_1300": int(len(pre_all)),
                "n_post_1300": int(len(post_all)),
                "post_pre_ratio": round(len(post_all) / len(pre_all), 4) if len(pre_all) else np.nan,
                "note": "long_period_descriptive_not_mechanism",
            },
            {
                "test": "studium_paris_share45_local_window",
                "share45_pre": all_stats["share45_pre"],
                "share45_post": all_stats["share45_post"],
                "n_with_birth_pre": all_stats["n_age_pre"],
                "n_with_birth_post": all_stats["n_age_post"],
                "p_value": all_stats["share45_prop_p"],
                "note": all_stats["window"] + "; proportion_test; life_quality filtered",
            },
            {
                "test": "studium_paris_observed_span_local_window",
                "mean_span_pre": all_stats["mean_observed_span_pre"],
                "mean_span_post": all_stats["mean_observed_span_post"],
                "n_span_pre": all_stats["n_span_pre"],
                "n_span_post": all_stats["n_span_post"],
                "p_value": all_stats["span_p"],
                "note": "observed_activity_span_not_career_duration; " + all_stats["window"],
            },
            # Compatibility aliases for synthesis
            {
                "test": "studium_paris_career_span_pre_vs_post_1300",
                "mean_span_pre": all_stats["mean_observed_span_pre"],
                "mean_span_post": all_stats["mean_observed_span_post"],
                "n_span_pre": all_stats["n_span_pre"],
                "n_span_post": all_stats["n_span_post"],
                "p_value": all_stats["span_p"],
                "note": "ALIAS of observed_activity_span; measurement-error proxy",
            },
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "studium_summary.csv", index=False)

    ttest = pd.DataFrame(
        [
            {
                "test": "studium_share45_pre_vs_post_1300",
                "share45_pre": all_stats["share45_pre"],
                "share45_post": all_stats["share45_post"],
                "mean_pre_1300": all_stats["mean_age_pre"],
                "mean_post_1300": all_stats["mean_age_post"],
                "t_stat": all_stats["mean_age_t"],
                "p_value": all_stats["share45_prop_p"],
                "p_value_mean_age": all_stats["mean_age_p"],
                "n_pre": all_stats["n_age_pre"],
                "n_post": all_stats["n_age_post"],
                "note": "p_value is share45 proportion test; local window; filtered life dates",
            }
        ]
    )
    ttest.to_csv(OUTPUT_TABLES / "studium_age_ttest.csv", index=False)

    log(
        f"Studium: {len(df)} with anchor; local window "
        f"{LOCAL_PRE}-{LOCAL_POST}; age n={all_stats['n_age_pre']}/{all_stats['n_age_post']}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
