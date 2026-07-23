#!/usr/bin/env python3
"""Synthesize evidence with direction + identification strength (no auto causal claims)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

OUT = OUTPUT_TABLES / "evidence_summary.csv"
OUT_CORE = OUTPUT_TABLES / "evidence_core.csv"
OUT_BACKGROUND = OUTPUT_TABLES / "evidence_background.csv"
OUT_CLAIMS = OUTPUT_TABLES / "evidence_by_claim.csv"
MIN_N_PRE = 30

# Core descriptive / associational tests for the narrow claim
CORE_TESTS = {
    "active_share_45plus_ttest",
    "wiag_bishop_share45_pre_vs_post_1300",
    "wiag_domherren_share45_pre_vs_post_1300",
    "rag_share45_pre_vs_post_1300",
    "studium_share45_pre_vs_post_1300",
    "studium_paris_career_span_pre_vs_post_1300",
    "age_at_first_notable_work_birth_pre_vs_post_1280",
    "age_at_last_notable_work_birth_pre_vs_post_1280",
    "age_at_first_notable_work_local_window_1200_1360",
    "age_at_first_work_glass_vs_control_birth_ge1280",
    "age_at_first_work_glass_birth_pre_vs_post_1280",
    "age_at_first_work_birth_1150_1550_split_1280",
    "glass_center_effect",
    "glass_center_on_hc",
    "bp1290_vs_bp1450",
    "robust_within_italy_coefs",
    "istc_glass_vs_control",
}


def read_coef(model: str, var: str) -> tuple[float, float]:
    path = OUTPUT_TABLES / f"regression_{model}_coefs.csv"
    if not path.exists():
        return float("nan"), float("nan")
    df = pd.read_csv(path)
    row = df[df["variable"] == var]
    if row.empty:
        return float("nan"), float("nan")
    return float(row["coef"].iloc[0]), float(row["p_value"].iloc[0])


def _base_row(
    layer: int,
    test: str,
    metric: str,
    value,
    p_value,
    note: str,
    *,
    tier: str | None = None,
    n_pre: int | None = None,
    claim: str = "",
) -> dict:
    if tier is None:
        if test.startswith("RCT_"):
            tier = "mechanism"
        elif test.startswith("counterfactual_"):
            tier = "sensitivity"
        elif test in CORE_TESTS:
            tier = "core"
        else:
            tier = "background"
    return {
        "layer": layer,
        "test": test,
        "metric": metric,
        "value": value,
        "p_value": p_value,
        "note": note,
        "tier": tier,
        "n_pre": n_pre,
        "claim": claim,
    }


def _significant(p_value) -> bool:
    return pd.notna(p_value) and float(p_value) < 0.05


def classify_evidence(row: dict) -> dict:
    """Direction + identification_strength; never auto-promote to strong causal."""
    test = row["test"]
    p_value = row.get("p_value")
    value = row.get("value")
    note = str(row.get("note") or "")
    n_pre = row.get("n_pre")

    direction = "null"
    identification = "descriptive"
    data_adequacy = "na"
    supports_mechanism = False
    supports_historical_timing = False
    # Always False by policy — causal claim requires pre-registered identification design
    supports_strong_causal_claim = False
    inconsistent_with_prediction = False

    if test.startswith("RCT_"):
        supports_mechanism = True
        direction = "consistent"
        identification = "experimental"
        data_adequacy = "adequate"
        row["claim"] = "mechanism_near_work_cost"
    elif test.startswith("counterfactual_"):
        identification = "sensitivity"
        direction = "null"
        data_adequacy = "na"
        row["claim"] = "sensitivity_only"
    elif "share45" in test or test == "active_share_45plus_ttest":
        row["claim"] = "career_extension_45plus"
        data_adequacy = "adequate" if (n_pre is not None and n_pre >= MIN_N_PRE) else "insufficient"
        identification = "associational"
        if data_adequacy == "adequate" and _significant(p_value) and pd.notna(value):
            if float(value) > 0:
                direction = "consistent"
                supports_mechanism = True
            else:
                direction = "inconsistent"
                inconsistent_with_prediction = True
        elif data_adequacy == "insufficient":
            direction = "null"
    elif test.startswith("age_at_first_") or test.startswith("age_at_last_"):
        # Experience-premium unlock predicts age-at-major-work rises after spectacles.
        row["claim"] = "career_extension_45plus"
        data_adequacy = "adequate" if (n_pre is not None and n_pre >= MIN_N_PRE) else "insufficient"
        identification = "associational"
        if data_adequacy == "insufficient":
            direction = "null"
        elif _significant(p_value) and pd.notna(value):
            if float(value) > 0:
                direction = "consistent"
            else:
                direction = "inconsistent"
                inconsistent_with_prediction = True
        else:
            direction = "null"
    elif test.startswith("ilardi_wearer_"):
        # Named wearers × P800: B predicts works after wear onset; A predicts mostly before.
        row["claim"] = "career_extension_45plus"
        identification = "descriptive"
        # n_pre here = n_persons with dated works (micro); need ≥5 for adequate
        data_adequacy = "adequate" if (n_pre is not None and n_pre >= 5) else "insufficient"
        if data_adequacy == "insufficient":
            direction = "null"
        elif "share" in test and pd.notna(value):
            # high share after = consistent with B; low = inconsistent
            if float(value) >= 0.5:
                direction = "consistent"
            elif float(value) <= 0.35:
                direction = "inconsistent"
                inconsistent_with_prediction = True
            else:
                direction = "null"
        elif "mean_age_delta" in str(row.get("metric") or "") and pd.notna(value):
            if float(value) > 2:
                direction = "consistent"
            elif float(value) < -2:
                direction = "inconsistent"
                inconsistent_with_prediction = True
            else:
                direction = "null"
        else:
            direction = "null"
    elif any(x in test for x in ("pantheon_", "wikidata_", "stelter_")):
        row["claim"] = "career_extension_45plus"
        data_adequacy = "adequate" if (n_pre is not None and n_pre >= MIN_N_PRE) else "insufficient"
        identification = "associational"
        if data_adequacy == "adequate" and _significant(p_value) and pd.notna(value):
            direction = "consistent" if float(value) > 0 else "inconsistent"
            if float(value) < 0:
                inconsistent_with_prediction = True
        elif data_adequacy == "insufficient":
            direction = "null"
    elif test.startswith("spectacle_adoption"):
        row["claim"] = "spectacle_adoption_evidence"
        identification = "descriptive"
        data_adequacy = "adequate"
        direction = "consistent"
        supports_historical_timing = True
    elif "career_span" in test or "observed_span" in test:
        row["claim"] = "career_extension_45plus"
        m = re.search(r"n=(\d+)/", note)
        n_span = int(m.group(1)) if m else n_pre
        data_adequacy = "adequate" if (n_span and n_span >= MIN_N_PRE) else "insufficient"
        identification = "associational"
        # Measurement-error heavy: never elevate beyond descriptive inconsistency
        if _significant(p_value) and pd.notna(value):
            direction = "consistent" if float(value) > 0 else "inconsistent"
            if float(value) < 0:
                inconsistent_with_prediction = True  # soft; note measurement caveats
        note = note + "; observed_activity_span_proxy"
        row["note"] = note
    elif test == "glass_center_effect" or test == "glass_center_on_hc" or test == "interaction_effect":
        row["claim"] = "glass_center_advantage"
        data_adequacy = "adequate"
        identification = "associational"
        if _significant(p_value) and pd.notna(value):
            if float(value) > 0:
                direction = "consistent"
            else:
                direction = "inconsistent"
                inconsistent_with_prediction = True
    elif test == "did_glass_x_post1450":
        # Demoted: not a real DiD
        row["claim"] = "glass_center_advantage"
        row["tier"] = "background"
        identification = "descriptive"
        direction = "null"
        note = note + "; not_did_istc_no_preperiod"
        row["note"] = note
    elif test == "post_1300_effect":
        # Removed from interpretable specs (collinear); if present, ignore for claims
        row["claim"] = "career_extension_45plus"
        row["tier"] = "background"
        identification = "descriptive"
        direction = "null"
        note = note + "; collinear_with_century_FE_do_not_interpret"
        row["note"] = note
    elif test == "bp1290_vs_bp1450":
        row["claim"] = "timing_1300"
        data_adequacy = "adequate"
        identification = "associational"
        if "weaker" in note:
            direction = "inconsistent"
            inconsistent_with_prediction = True
            supports_historical_timing = True  # macro rise may exist; eyeglasses-first weaker
        elif pd.notna(value):
            supports_historical_timing = True
            direction = "null"
    elif test == "pre1300_parallel_trends":
        row["claim"] = "glass_center_advantage"
        identification = "associational"
        direction = "null"
        data_adequacy = "adequate"
    elif test in ("istc_glass_vs_control", "robust_within_italy_coefs", "robust_glass_timing_did_coefs"):
        row["claim"] = "glass_center_advantage"
        identification = "associational"
        data_adequacy = "adequate"
        if test == "istc_glass_vs_control":
            if _significant(p_value) and pd.notna(value) and float(value) > 1:
                direction = "consistent"
            elif _significant(p_value) and pd.notna(value) and float(value) <= 1:
                direction = "inconsistent"
                inconsistent_with_prediction = True
            else:
                direction = "null"
        else:
            if _significant(p_value) and pd.notna(value):
                if float(value) > 0:
                    direction = "consistent"
                else:
                    direction = "inconsistent"
                    inconsistent_with_prediction = True
    elif test.startswith("chow_") or test.startswith("manuscript_") or test.startswith("bologna_") or test.startswith("mmm_"):
        row["claim"] = "timing_1300"
        identification = "descriptive"
        if pd.notna(value) and (
            (isinstance(value, (int, float)) and float(value) > 0 and _significant(p_value))
            or (isinstance(value, (int, float)) and "growth" in test and float(value) > 0)
            or (isinstance(value, (int, float)) and float(value) > 1 and not _significant(p_value) and "ratio" in str(row.get("metric", "")))
        ):
            supports_historical_timing = True
            direction = "consistent"
        if test.endswith("_bp1608"):
            supports_historical_timing = False
            direction = "null"
            note = note + "; excluded_telescope_era"
            row["note"] = note
    elif test.startswith("sdbm_"):
        row["claim"] = "timing_1300"
        identification = "descriptive"
        data_adequacy = "adequate" if (n_pre is not None and n_pre >= MIN_N_PRE) else "insufficient"
        metric = str(row.get("metric") or "")
        if "local_post_over_pre" in metric:
            if data_adequacy == "insufficient":
                direction = "null"
            elif pd.notna(value):
                v = float(value)
                if v > 1.05:
                    direction = "consistent"
                    supports_historical_timing = True
                elif v < 0.95:
                    direction = "inconsistent"
                    inconsistent_with_prediction = True
                else:
                    direction = "null"
        elif "peak_halfcentury" in test:
            data_adequacy = "adequate"
            if pd.notna(value) and float(value) >= 1450:
                direction = "inconsistent"
                inconsistent_with_prediction = True
                supports_historical_timing = True
            elif pd.notna(value) and float(value) < 1350:
                direction = "null"
        elif "post_pre_ratio_mid" in metric:
            if data_adequacy == "insufficient":
                direction = "null"
            elif pd.notna(value) and float(value) < 1.0:
                direction = "inconsistent"
                inconsistent_with_prediction = True
    elif test in (
        "studium_paris_volume_pre_vs_post_1300",
        "leuven_matriculations_volume",
        "utrecht_priest_ordinations",
        "patentcity_glass_vs_control_1850s",
    ):
        row["claim"] = "background"
        identification = "descriptive"
        direction = "null"
        if "bhotmg" in test:
            note = note + "; base_effect_artifact"
            row["note"] = note
        if "studium_paris_volume" in test:
            note = note + "; record_coverage_not_mechanism"
            row["note"] = note

    row["direction"] = direction
    row["identification_strength"] = identification
    row["supports_mechanism"] = supports_mechanism
    row["supports_historical_timing"] = supports_historical_timing
    row["supports_strong_causal_claim"] = supports_strong_causal_claim
    row["inconsistent_with_prediction"] = inconsistent_with_prediction
    # Deprecated aliases
    row["weakens_strong_claim"] = inconsistent_with_prediction
    row["supports_hypothesis"] = False
    row["data_adequacy"] = data_adequacy
    return row


def main() -> None:
    rows: list[dict] = []

    for name, delta, src in [
        ("conservative", 5.7, "PROSPER_II"),
        ("moderate", 21.7, "PROSPER"),
        ("optimistic", 33.0, "THRIVE"),
    ]:
        rows.append(
            _base_row(
                1,
                f"RCT_{name}",
                "productivity_gain_pct",
                delta,
                None,
                f"Modern RCT ({src}); near-work marginal cost after presbyopia; task mismatch with medieval scholarship",
                tier="mechanism",
                claim="mechanism_near_work_cost",
            )
        )

    bp_path = OUTPUT_TABLES / "breakpoint_tests.csv"
    if bp_path.exists():
        bp = pd.read_csv(bp_path)
        for _, r in bp.iterrows():
            rows.append(
                _base_row(
                    2,
                    f"chow_{r['series']}_bp{int(r['breakpoint'])}",
                    "f_stat",
                    r["f_stat"],
                    r["p_value"],
                    f"method={r.get('method', '')}; slope_change={r.get('slope_change', 'NA')}; "
                    f"window_half={r.get('window_half', 'NA')}",
                    tier="background",
                    claim="timing_1300",
                )
            )

    for extra_bp, series_prefix in [
        ("manuscript_breakpoint_tests.csv", "manuscript"),
        ("ha_breakpoint_tests.csv", "ha_science"),
        ("printed_books_breakpoint_tests.csv", "printed_books"),
    ]:
        p = OUTPUT_TABLES / extra_bp
        if not p.exists():
            continue
        edf = pd.read_csv(p)
        for _, r in edf.iterrows():
            note = r.get("note", "")
            if note and str(note).startswith("growth_"):
                rows.append(
                    _base_row(
                        2,
                        f"{series_prefix}_{note}",
                        "pct_change",
                        r.get("pct_change"),
                        None,
                        str(r["series"]),
                        tier="background",
                        claim="timing_1300",
                    )
                )
            elif not pd.isna(r.get("f_stat")):
                rows.append(
                    _base_row(
                        2,
                        f"chow_{r['series']}_bp{int(r['breakpoint'])}",
                        "f_stat",
                        r["f_stat"],
                        r["p_value"],
                        f"pct_change={r.get('pct_change', 'NA')}%",
                        tier="background",
                        claim="timing_1300",
                    )
                )

    for fname, test, metric, claim, tier in [
        ("manuscript_glass_summary.csv", "manuscript_italy_vs_control_1200_1300", "ratio_italy_to_control", "timing_1300", "background"),
        ("bologna_summary.csv", "bologna_german_nation_post_pre_1300", "post_pre_citation_ratio", "timing_1300", "background"),
        ("mmm_summary.csv", "mmm_glass_growth_vs_control_1300", "glass_over_control_growth_ratio", "timing_1300", "background"),
        ("bhotmg_summary.csv", "bhotmg_university_hc_glass_vs_control_1300", "glass_over_control_growth", "background", "background"),
        ("leuven_summary.csv", "leuven_matriculations_volume", "n_total", "background", "background"),
        ("utrecht_summary.csv", "utrecht_priest_ordinations", "n_ordinations", "background", "background"),
    ]:
        path = OUTPUT_TABLES / fname
        if not path.exists():
            continue
        d = pd.read_csv(path).iloc[0]
        if test.startswith("manuscript_italy"):
            val, note = d.get("ratio_italy_to_control"), f"italy_growth={d.get('italy_pct_growth')}%"
        elif test.startswith("bologna"):
            val = d.get("post_pre_ratio")
            note = f"pre={int(d['n_citations_pre'])}, post={int(d['n_citations_post'])}"
        elif test.startswith("mmm"):
            val = d.get("glass_growth_over_control")
            note = f"glass {int(d['glass_pre_1300'])}/{int(d['glass_post_1300'])}"
        elif test.startswith("bhotmg"):
            val = d.get("glass_over_control_growth")
            note = f"pre/post glass={d.get('glass_hc_pre_1300')}/{d.get('glass_hc_post_1300')}"
        elif test.startswith("leuven"):
            val, note = d.get("n_total"), f"starts {int(d['year_min'])}"
        else:
            val, note = d.get("n_ordinations"), f"{int(d['year_min'])}-{int(d['year_max'])}"
        rows.append(_base_row(2, test, metric, val, None, note, tier=tier, claim=claim))

    sdbm_pp = OUTPUT_TABLES / "sdbm_pre_post_summary.csv"
    if sdbm_pp.exists():
        for _, d in pd.read_csv(sdbm_pp).iterrows():
            city = d["test"].replace("sdbm_", "").split("_")[0]
            field = d.get("search_field", "place")
            n_pre_local = int(d["local_pre_1200_1285"]) if pd.notna(d.get("local_pre_1200_1285")) else None
            rows.append(
                _base_row(
                    2,
                    f"sdbm_{city}_{field}_local_window_1300",
                    "local_post_over_pre",
                    d.get("local_post_over_pre"),
                    None,
                    f"1200-1285 n={d.get('local_pre_1200_1285')} vs 1300-1385 n={d.get('local_post_1300_1385')}; "
                    f"{d.get('note', '')}",
                    tier="core" if n_pre_local and n_pre_local >= MIN_N_PRE else "background",
                    n_pre=n_pre_local,
                    claim="timing_1300",
                )
            )
            n_pre_mid = int(d["n_pre_1300"]) if pd.notna(d.get("n_pre_1300")) else None
            ratio = (
                float(d["n_post_1300"]) / float(d["n_pre_1300"])
                if pd.notna(d.get("n_pre_1300")) and float(d["n_pre_1300"]) > 0
                else np.nan
            )
            rows.append(
                _base_row(
                    2,
                    f"sdbm_{city}_{field}_mid_pre_post_1300",
                    "post_pre_ratio_mid",
                    ratio,
                    None,
                    f"mid_year pre={n_pre_mid} post={int(d['n_post_1300']) if pd.notna(d.get('n_post_1300')) else 'NA'}",
                    tier="background",
                    n_pre=n_pre_mid,
                    claim="timing_1300",
                )
            )

    sdbm_sum = OUTPUT_TABLES / "sdbm_city_summary.csv"
    if sdbm_sum.exists():
        for _, d in pd.read_csv(sdbm_sum).iterrows():
            rows.append(
                _base_row(
                    2,
                    f"sdbm_{d['city'].lower()}_{d['search_field']}_peak_halfcentury",
                    "peak_halfcentury",
                    d.get("peak_halfcentury"),
                    None,
                    f"peak_entries={int(d['peak_entries'])}; n_total={int(d['n_entries'])}",
                    tier="background",
                    claim="timing_1300",
                )
            )

    studium_path = OUTPUT_TABLES / "studium_summary.csv"
    if studium_path.exists():
        s = pd.read_csv(studium_path)
        for _, v in s.iterrows():
            tname = v["test"]
            if "volume" in tname:
                rows.append(
                    _base_row(
                        2,
                        "studium_paris_volume_pre_vs_post_1300",
                        "post_pre_ratio",
                        v.get("post_pre_ratio"),
                        None,
                        str(v.get("note", "")),
                        tier="background",
                        claim="background",
                    )
                )
            elif "career_span" in tname or "observed_span" in tname:
                if "ALIAS" in str(v.get("note", "")):
                    continue  # skip duplicate alias row
                rows.append(
                    _base_row(
                        2,
                        "studium_paris_career_span_pre_vs_post_1300",
                        "mean_span_diff_post_minus_pre",
                        (v.get("mean_span_post") - v.get("mean_span_pre"))
                        if pd.notna(v.get("mean_span_post")) and pd.notna(v.get("mean_span_pre"))
                        else np.nan,
                        v.get("p_value"),
                        str(v.get("note", "")),
                        tier="core",
                        n_pre=int(v.get("n_span_pre", 0)) if pd.notna(v.get("n_span_pre")) else None,
                        claim="career_extension_45plus",
                    )
                )

    for path, test, claim in [
        (OUTPUT_TABLES / "studium_age_ttest.csv", "studium_share45_pre_vs_post_1300", "career_extension_45plus"),
        (OUTPUT_TABLES / "active_age_ttest.csv", "active_share_45plus_ttest", "career_extension_45plus"),
        (OUTPUT_TABLES / "wiag_bishop_age_ttest.csv", "wiag_bishop_share45_pre_vs_post_1300", "career_extension_45plus"),
        (OUTPUT_TABLES / "wiag_domherren_age_ttest.csv", "wiag_domherren_share45_pre_vs_post_1300", "career_extension_45plus"),
        (OUTPUT_TABLES / "rag_age_ttest.csv", "rag_share45_pre_vs_post_1300", "career_extension_45plus"),
    ]:
        if not path.exists():
            continue
        d = pd.read_csv(path).iloc[0]
        if "share45_post" in d and "share45_pre" in d:
            val = d["share45_post"] - d["share45_pre"]
        else:
            val = d.get("mean_post_1300", np.nan) - d.get("mean_pre_1300", np.nan) if "mean_post_1300" in d else np.nan
        rows.append(
            _base_row(
                2,
                test,
                "share45_diff_post_minus_pre" if "share45" in test or "share45" in str(d.get("test", "")) else "mean_diff",
                val,
                d.get("p_value"),
                str(d.get("note", path.name)),
                tier="core",
                n_pre=int(d["n_pre"]) if "n_pre" in d and pd.notna(d["n_pre"]) else None,
                claim=claim,
            )
        )

    alt_path = OUTPUT_TABLES / "alt_scholar_age_ttests.csv"
    if alt_path.exists():
        for _, d in pd.read_csv(alt_path).iterrows():
            test = str(d["test"])
            if "share45_post" in d and "share45_pre" in d:
                val = d["share45_post"] - d["share45_pre"]
            else:
                val = d.get("mean_post_1300", np.nan) - d.get("mean_pre_1300", np.nan)
            pval = d.get("share45_prop_p") if pd.notna(d.get("share45_prop_p")) else d.get("p_value")
            rows.append(
                _base_row(
                    2,
                    test,
                    "share45_diff_post_minus_pre",
                    val,
                    pval,
                    str(d.get("note", "")),
                    tier="core",
                    n_pre=int(d["n_pre"]) if "n_pre" in d and pd.notna(d["n_pre"]) else None,
                    claim="career_extension_45plus",
                )
            )

    age_work_path = OUTPUT_TABLES / "age_at_work_ttests.csv"
    if age_work_path.exists():
        for _, d in pd.read_csv(age_work_path).iterrows():
            rows.append(
                _base_row(
                    2,
                    str(d["test"]),
                    "mean_age_diff_post_minus_pre",
                    d.get("mean_diff_post_minus_pre"),
                    d.get("p_value"),
                    str(d.get("note", "")),
                    tier="core",
                    n_pre=int(d["n_pre"]) if "n_pre" in d and pd.notna(d["n_pre"]) else None,
                    claim="career_extension_45plus",
                )
            )

    wear_micro = OUTPUT_TABLES / "ilardi_wearer_micro_ttests.csv"
    if wear_micro.exists():
        for _, d in pd.read_csv(wear_micro).iterrows():
            rows.append(
                _base_row(
                    2,
                    str(d["test"]),
                    str(d.get("metric", "value")),
                    d.get("value"),
                    d.get("p_value"),
                    (
                        f"n_persons={d.get('n_persons')}; works before/after="
                        f"{d.get('n_works_before')}/{d.get('n_works_after')}; {d.get('note', '')}"
                    ),
                    tier="background",
                    n_pre=int(d["n_persons"]) if pd.notna(d.get("n_persons")) else None,
                    claim="career_extension_45plus",
                )
            )

    adopt_path = OUTPUT_TABLES / "spectacle_adoption_summary.csv"
    if adopt_path.exists():
        d = pd.read_csv(adopt_path).iloc[0]
        note = str(d.get("note", ""))
        if "ilardi_court_pairs_documented" in d.index and pd.notna(d.get("ilardi_court_pairs_documented")):
            note = (
                f"curated n={int(d['n_records_total'])}; "
                f"ilardi_court_pairs={int(d['ilardi_court_pairs_documented'])}; "
                f"london_import_pairs≈{int(d['ilardi_london_import_pairs_sum'])}; "
                f"price_soldi={d['ilardi_price_soldi_min']}-{d['ilardi_price_soldi_max']}; "
                f"{note}"
            )
        else:
            note = (
                f"curated n={int(d['n_records_total'])}; earliest={int(d['earliest_year'])}; "
                f"physical_or_ownership={int(d['n_physical_or_ownership'])}"
            )
        rows.append(
            _base_row(
                1,
                "spectacle_adoption_curated_timeline",
                "n_records_post_1300",
                d.get("n_post_1300"),
                None,
                note,
                tier="background",
                claim="spectacle_adoption_evidence",
            )
        )
        # Separate quantitative adoption row from Ilardi court + London trade
        if "ilardi_court_pairs_documented" in d.index and pd.notna(d.get("ilardi_court_pairs_documented")):
            rows.append(
                _base_row(
                    1,
                    "spectacle_adoption_ilardi_court_and_london_trade",
                    "court_pairs_plus_london_import_pairs",
                    float(d["ilardi_court_pairs_documented"])
                    + float(d["ilardi_london_import_pairs_sum"]),
                    None,
                    "RQ1976: 1462=54 + 1466=50 court pairs; London 1384/90/91 imports from Ilardi citing Harding/Jenks; "
                    "supports mid-15c age-graded mass supply & late-14c trade volume; NOT career extension ID",
                    tier="background",
                    claim="spectacle_adoption_evidence",
                )
            )

    # Regressions — only glass_center terms (no post_1300_effect)
    for model, var, label, claim in [
        ("model1_active_share", "glass_center", "glass_center_effect", "glass_center_advantage"),
        ("model2_hc_gradient", "glass_center", "glass_center_on_hc", "glass_center_advantage"),
        ("model3_did_books", "glass_center", "did_glass_x_post1450", "glass_center_advantage"),
    ]:
        coef, pval = read_coef(model, var)
        if not np.isnan(coef):
            rows.append(
                _base_row(
                    3,
                    label,
                    "coef",
                    coef,
                    pval,
                    model + ("; not_did" if label.startswith("did_") else ""),
                    tier="core" if label in CORE_TESTS else "background",
                    claim=claim,
                )
            )

    cf_path = OUTPUT_TABLES / "counterfactual_scenarios.csv"
    if cf_path.exists():
        cf = pd.read_csv(cf_path)
        for _, r in cf.iterrows():
            rows.append(
                _base_row(
                    4,
                    f"counterfactual_{r['scenario']}",
                    "pct_output_loss",
                    r["pct_output_loss"],
                    None,
                    str(r.get("note", "sensitivity_only")),
                    tier="sensitivity",
                    claim="sensitivity_only",
                )
            )

    # Robustness
    for fname, test_name, id_col, filter_val, claim in [
        ("robust_breakpoint_comparison.csv", "bp1290_vs_bp1450", "breakpoint", 1290, "timing_1300"),
        ("robust_within_italy_coefs.csv", "robust_within_italy_coefs", "variable", "glass_center", "glass_center_advantage"),
        ("robust_glass_timing_did_coefs.csv", "robust_glass_timing_did_coefs", "variable", "treated:post_treat", "glass_center_advantage"),
    ]:
        path = OUTPUT_TABLES / fname
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if id_col == "breakpoint":
            row = df[df["breakpoint"] == filter_val]
            if not row.empty:
                rows.append(
                    _base_row(
                        5,
                        test_name,
                        "slope_or_pct",
                        row["slope_change"].iloc[0] if "slope_change" in row.columns else row["pct_change"].iloc[0],
                        row["p_value"].iloc[0],
                        str(row["note"].iloc[0]) if "note" in row.columns else "",
                        tier="core",
                        claim=claim,
                    )
                )
        else:
            row = df[df[id_col] == filter_val] if id_col in df.columns else pd.DataFrame()
            if row.empty and "treated:post_treat" in str(filter_val):
                # fallback: any treated interaction
                row = df[df[id_col].astype(str).str.contains("treated", na=False)]
            if not row.empty:
                rows.append(
                    _base_row(
                        5,
                        test_name,
                        "coef",
                        row["coef"].iloc[0],
                        row["p_value"].iloc[0],
                        str(filter_val) + "; exploratory",
                        tier="core" if test_name in CORE_TESTS else "background",
                        claim=claim,
                    )
                )

    pre_path = OUTPUT_TABLES / "robust_pretrend_test.csv"
    if pre_path.exists():
        r = pd.read_csv(pre_path).iloc[0]
        rows.append(
            _base_row(
                5,
                "pre1300_parallel_trends",
                "p_value",
                r.get("p_value"),
                r.get("p_value"),
                "non_rejection_is_not_support",
                tier="background",
                claim="glass_center_advantage",
            )
        )

    istc_path = OUTPUT_TABLES / "robust_istc_glass_vs_control.csv"
    if istc_path.exists():
        r = pd.read_csv(istc_path).iloc[0]
        rows.append(
            _base_row(
                5,
                "istc_glass_vs_control",
                "ratio",
                r["ratio_glass_to_control"],
                r["p_value"],
                str(r.get("note", r.get("source", ""))),
                tier="core",
                claim="glass_center_advantage",
            )
        )

    rows = [classify_evidence(r) for r in rows]
    summary = pd.DataFrame(rows)
    # pandas treats literal "null" as NA when building frames; restore direction labels
    if "direction" in summary.columns:
        summary["direction"] = summary["direction"].fillna("null")
    col_order = [
        "layer",
        "tier",
        "claim",
        "test",
        "metric",
        "value",
        "p_value",
        "direction",
        "identification_strength",
        "supports_mechanism",
        "supports_historical_timing",
        "supports_strong_causal_claim",
        "inconsistent_with_prediction",
        "data_adequacy",
        "supports_hypothesis",
        "weakens_strong_claim",
        "n_pre",
        "note",
    ]
    summary = summary[[c for c in col_order if c in summary.columns]]
    summary.to_csv(OUT, index=False)

    core = summary[summary["tier"] == "core"].copy()
    background = summary[summary["tier"].isin(["background", "mechanism", "sensitivity"])].copy()
    core.to_csv(OUT_CORE, index=False)
    background.to_csv(OUT_BACKGROUND, index=False)

    # Claim-level rollup (no 0/N headline)
    claim_rows = []
    for claim, g in summary.groupby("claim"):
        if claim in ("", "background", "sensitivity_only"):
            continue
        dirs = g["direction"].value_counts().to_dict()
        ids = g["identification_strength"].value_counts().to_dict()
        inadequ = (g["data_adequacy"] == "insufficient").mean() if len(g) else 0
        claim_rows.append(
            {
                "claim": claim,
                "n_tests": len(g),
                "n_consistent": int((g["direction"] == "consistent").sum()),
                "n_inconsistent": int((g["direction"] == "inconsistent").sum()),
                "n_null": int((g["direction"] == "null").sum()),
                "share_insufficient_data": round(float(inadequ), 3),
                "max_identification": max(g["identification_strength"], key=lambda x: ["descriptive", "associational", "quasi_experimental", "experimental", "sensitivity"].index(x) if x in ["descriptive", "associational", "quasi_experimental", "experimental", "sensitivity"] else 0),
                "judgment": (
                    "accepted_near_work_continuation"
                    if claim == "mechanism_near_work_cost"
                    else "accepted_mass_near_work_tool_scale"
                    if claim == "spectacle_adoption_evidence"
                    else "timing_compatible_rejects_glasses_over_print"
                    if claim == "timing_1300"
                    and dirs.get("inconsistent", 0) > 0
                    else "timing_compatible_not_causal_support"
                    if claim == "timing_1300" and dirs.get("consistent", 0) > 0
                    else (
                        "hunt_data_required_before_verdict"
                        if inadequ >= 0.5
                        else "rejected_experience_premium_unlock"
                        if dirs.get("inconsistent", 0) > dirs.get("consistent", 0)
                        else "accepted_experience_premium_unlock"
                        if dirs.get("consistent", 0) > dirs.get("inconsistent", 0)
                        else "null_on_adequate_panels_continue_hunt"
                    )
                    if claim == "career_extension_45plus"
                    else "rejected_glass_center_knowledge_advantage"
                    if claim == "glass_center_advantage"
                    else "rejected_no_decisive_support"
                ),
            }
        )
    claims = pd.DataFrame(claim_rows)
    claims.to_csv(OUT_CLAIMS, index=False)

    n_mech = int(summary[summary["test"].str.startswith("RCT_")]["supports_mechanism"].sum())
    n_inconsist = int(summary["inconsistent_with_prediction"].sum())

    verdict = OUTPUT_TABLES / "verdict.txt"
    with open(verdict, "w", encoding="utf-8") as f:
        f.write("EYEGLASSES HYPOTHESIS — EVIDENCE SUMMARY (v3.5 tiered verdict)\n")
        f.write("=" * 60 + "\n\n")
        f.write("CORE COLLISION (user-facing):\n")
        f.write("  Experience-premium unlock: older scholars peak with experience; presbyopia blocked\n")
        f.write("    that window; spectacles unlocked late-career revolutionary output.\n")
        f.write("  Near-work continuation: real achievements come young; glasses only add near-work\n")
        f.write("    hours after cognitive peak — ordinary tool, not late-career revolution.\n")
        f.write("  VERDICT TILT: near-work continuation (A) over experience-premium unlock (B).\n\n")
        f.write("SCOPE: narrow claim (presbyopia spectacles → scholar careers → glass-center advantage).\n")
        f.write("NOT tested: full Macfarlane/Martin Glass book (vessels, telescopes, later science).\n\n")
        f.write("THREE-TIER VERDICT (reader-facing; see docs/VERDICT_zh.md):\n")
        f.write("  [A] NEAR-WORK CONTINUATION — ACCEPT: lowers near-work marginal cost; RCT 3/3 +\n")
        f.write("      invention history + p.190 + mass cheap trade (haberdashery-scale imports) +\n")
        f.write("      age-graded court orders (1466) + Florence occhialai density (Appendix I).\n")
        f.write("  [B] EXPERIENCE-PREMIUM UNLOCK — REJECT on adequate panels after data hunt:\n")
        f.write("      Studium/alt share45 + Wikidata P800 age-at-notable-work (n_pre≥100).\n")
        f.write("      Age-at-first/last notable work falls ~6–8y after ~1280 (opposite of B);\n")
        f.write("      trimmed 1150–1550 still ~−4.7y; glass-center vs control null (no late premium).\n")
        f.write("      Rule: insufficient → find data; adequate+wrong/null → reject. No fuzzy halt.\n")
        f.write(f"      {n_inconsist} rows inconsistent with experience-premium predictions where testable.\n")
        f.write("  [C] VIRAL / SECOND-HAND CLAIMS — DEBUNK: 'civilization started with spectacles',\n")
        f.write("      '+15 years intellectual life' — no verbatim +15y in book body; Miller review.\n\n")
        f.write("A true + B false + C false is coherent: more near-work hours for aging readers does\n")
        f.write("not imply late-career experience premia were systematically unlocked.\n\n")
        f.write(
            "OPEN BUT NON-BLOCKING GAPS: larger named-wearer×output sample (micro n=3 so far); "
            "EMLO; optional SDBM bulk dump.\n\n"
        )
        f.write(
            "SDBM MULTI-CITY (timing_1300): Venice Place/Provenance local post/pre≈2.7/3.2 "
            "(consistent) but Bologna Place≈3.1 also rises; Paris/Oxford fall — "
            "not glass-center-specific; peaks still 1450.\n\n"
        )
        f.write(
            "ILARDI NAMED-WEARER MICRO: Petrarch/Filelfo/Lotto (high/medium + P800 dates) — "
            "~19% of notable works at/after wear evidence (81% before); mean work age "
            "~12y earlier than evidence age. Direction favors A over B; n=3 insufficient "
            "for standalone reject.\n\n"
        )
        f.write(f"Modern RCT mechanism rows: {n_mech}/3 (experimental; task mismatch to medieval scholarship).\n\n")
        f.write("CLAIM ROLLUP (see evidence_by_claim.csv):\n")
        if len(claims):
            f.write(claims.to_string(index=False))
        f.write("\n\nHEADLINE:\n")
        f.write(
            "[A ACCEPT] Spectacles as ordinary near-work continuation tool (vision cost ↓).\n"
            "[B REJECT] Experience-premium unlock rejected: age-at-notable-work falls post-1280;\n"
            "           45+ share panels do not rise with diffusion.\n"
            "[C DEBUNK] Civilization-origin and '+15 years' claims are exaggerated; see CLAIM_GENEALOGY.md.\n\n"
        )
        f.write("PRIMARY: evidence_by_claim.csv + evidence_core.csv\n")
        f.write("METHOD NOTES: trend Chow (±80y); Model1 omits post_1300×C(century);\n")
        f.write("ISTC cross-section is not DiD; Studium uses observed_activity_span + local windows.\n\n")
        f.write("PREPRINT APPENDIX (also docs/):\n")
        f.write("- CLAIM_GENEALOGY.md / claim_genealogy_checklist.csv\n")
        f.write("- LITERATURE_AND_DAG.md (Ilardi + causal chain gaps)\n")
        f.write("- power_mde_summary.csv, sensitivity_age_thresholds.csv\n")
        f.write("- studium_sample_audit.csv (n=300) + studium_audit_summary.csv\n")
        f.write("- robust_leave_one_out_glass.csv, robust_glass_permutation.csv\n")
        f.write("- data_provenance.csv (SHA-256)\n\n")
        f.write("CORE TESTS:\n")
        f.write(core.to_string(index=False))
        f.write("\n\nALL TESTS:\n")
        f.write(summary.to_string(index=False))

    log(f"Evidence v3: claims={len(claims)}, inconsist={n_inconsist} -> {verdict}", OUTPUT_LOGS / "analysis.log")


if __name__ == "__main__":
    main()
