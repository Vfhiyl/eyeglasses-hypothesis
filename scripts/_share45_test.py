"""Shared pre/post-1300 share45 and two-proportion helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def two_proportion_z(n1: int, x1: int, n2: int, x2: int) -> tuple[float, float]:
    if min(n1, n2) <= 0:
        return np.nan, np.nan
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    if p_pool in (0.0, 1.0):
        return np.nan, np.nan
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    return float(z), float(2 * (1 - stats.norm.cdf(abs(z))))


def share45_row(
    *,
    test: str,
    pre: pd.Series,
    post: pd.Series,
    threshold: float = 45,
    note: str = "",
) -> dict:
    pre = pre.dropna()
    post = post.dropna()
    share_pre = float((pre >= threshold).mean()) if len(pre) else np.nan
    share_post = float((post >= threshold).mean()) if len(post) else np.nan
    z, p = two_proportion_z(
        len(pre), int((pre >= threshold).sum()), len(post), int((post >= threshold).sum())
    )
    if len(pre) >= 2 and len(post) >= 2:
        t_stat, p_t = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t_stat, p_t = np.nan, np.nan
    return {
        "test": test,
        "mean_pre_1300": round(float(pre.mean()), 4) if len(pre) else np.nan,
        "mean_post_1300": round(float(post.mean()), 4) if len(post) else np.nan,
        "share45_pre": round(share_pre, 4) if pd.notna(share_pre) else np.nan,
        "share45_post": round(share_post, 4) if pd.notna(share_post) else np.nan,
        "t_stat": round(float(t_stat), 4) if not np.isnan(t_stat) else np.nan,
        "p_value": round(float(p_t), 6) if not np.isnan(p_t) else np.nan,
        "share45_prop_z": round(z, 4) if not np.isnan(z) else np.nan,
        "share45_prop_p": round(p, 6) if not np.isnan(p) else np.nan,
        "n_pre": len(pre),
        "n_post": len(post),
        "note": note,
    }
