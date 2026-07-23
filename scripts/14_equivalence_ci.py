#!/usr/bin/env python3
"""CI / SESOI / TOST-style equivalence notes for core null results.

Anti-fuzzy: nonsignificant ≠ reject. Report CI width vs predeclared SESOI;
if CI excludes SESOI band → can support 'no historically meaningful effect';
if CI spans large effects → imprecise / hunt more data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

# Smallest effect sizes of interest (predeclared for v4)
SESOI_SHARE45 = 0.05  # 5 pp rise in 45+ share
SESOI_GLASS_ACTIVE = 0.05  # 5 pp active-share advantage


def prop_diff_ci(n1: int, x1: float, n2: int, x2: float, alpha: float = 0.05) -> tuple[float, float, float]:
    """Difference p2-p1 with Wald CI (post - pre)."""
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z = stats.norm.ppf(1 - alpha / 2)
    return float(diff), float(diff - z * se), float(diff + z * se)


def tost_equiv(diff: float, lo: float, hi: float, sesoi: float) -> str:
    """Two one-sided style label using CI entirely inside (-sesoi, +sesoi)."""
    if lo > -sesoi and hi < sesoi:
        return "equivalent_within_sesoi"
    if hi < -sesoi or lo > sesoi:
        return "incompatible_with_zero_or_small"
    return "imprecise_ci_spans_sesoi"


def main() -> None:
    rows = []

    # Studium share45 from existing ttest table + rebuild counts if scholars present
    studium_path = DATA_PROCESSED / "studium_paris_scholars.csv"
    if studium_path.exists():
        df = pd.read_csv(studium_path)
        age = df.dropna(subset=["age_at_activity_end"])
        if "life_date_quality" in age.columns:
            age = age[age["life_date_quality"].isin(["interval_meta", "text_range"])]
        pre = age[(age["anchor_year"] >= 1200) & (age["anchor_year"] <= 1285)]
        post = age[(age["anchor_year"] >= 1300) & (age["anchor_year"] <= 1385)]
        if len(pre) >= 10 and len(post) >= 10:
            x1 = int((pre["age_at_activity_end"] >= 45).sum())
            x2 = int((post["age_at_activity_end"] >= 45).sum())
            diff, lo, hi = prop_diff_ci(len(pre), x1, len(post), x2)
            rows.append(
                {
                    "test": "studium_share45_pre_vs_post_1300",
                    "claim_map": "B2",
                    "estimate": round(diff, 4),
                    "ci95_lo": round(lo, 4),
                    "ci95_hi": round(hi, 4),
                    "sesoi": SESOI_SHARE45,
                    "equivalence_label": tost_equiv(diff, lo, hi, SESOI_SHARE45),
                    "n_pre": len(pre),
                    "n_post": len(post),
                    "note": "Wald CI on share45 post-pre; null≠reject",
                }
            )

    coef_path = OUTPUT_TABLES / "regression_model1_active_share_coefs.csv"
    if coef_path.exists():
        c = pd.read_csv(coef_path)
        g = c[c["variable"] == "glass_center"]
        if not g.empty:
            coef = float(g["coef"].iloc[0])
            se = float(g["std_err"].iloc[0])
            lo, hi = coef - 1.96 * se, coef + 1.96 * se
            rows.append(
                {
                    "test": "glass_center_effect_model1",
                    "claim_map": "B4",
                    "estimate": round(coef, 4),
                    "ci95_lo": round(lo, 4),
                    "ci95_hi": round(hi, 4),
                    "sesoi": SESOI_GLASS_ACTIVE,
                    "equivalence_label": tost_equiv(coef, lo, hi, SESOI_GLASS_ACTIVE),
                    "n_pre": np.nan,
                    "n_post": np.nan,
                    "note": "Model1 active share; weakens B4 only; not B1",
                }
            )

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_TABLES / "equivalence_ci_summary.csv", index=False)
    log(f"Equivalence/CI rows={len(out)} -> {OUTPUT_TABLES / 'equivalence_ci_summary.csv'}", OUTPUT_LOGS / "analysis.log")


if __name__ == "__main__":
    main()
