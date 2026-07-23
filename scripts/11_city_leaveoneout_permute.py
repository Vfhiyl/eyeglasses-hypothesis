#!/usr/bin/env python3
"""Leave-one-out glass centers, permutation placebo, alternate control sets."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import get_city_config, log

N_PERM = 200
SEED = 20260721


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(DATA_PROCESSED / "panel_city_century.csv")
    if "hc_observed" in df.columns:
        df = df[df["hc_observed"] == 1]
    df = df[(df["population"].notna()) & (df["population"] > 0)]
    df = df[df["century"].between(1300, 1700)].copy()
    return df


def fit_glass_coef(df: pd.DataFrame) -> tuple[float, float]:
    if len(df) < 20 or df["glass_center"].nunique() < 2:
        return float("nan"), float("nan")
    try:
        res = smf.ols(
            "log_hc_per_100k ~ glass_center + has_university + C(century) + C(region)",
            data=df,
        ).fit(cov_type="HC1")
        return float(res.params.get("glass_center", np.nan)), float(
            res.pvalues.get("glass_center", np.nan)
        )
    except Exception:
        return float("nan"), float("nan")


def leave_one_out(df: pd.DataFrame) -> pd.DataFrame:
    glass_cities = sorted(df.loc[df["glass_center"] == 1, "city"].dropna().unique())
    rows = []
    base_c, base_p = fit_glass_coef(df)
    rows.append({"spec": "baseline", "dropped_city": "", "coef": base_c, "p_value": base_p})
    for city in glass_cities:
        sub = df[df["city"] != city]
        # also drop if city was only glass label — keep remaining glass flags
        c, p = fit_glass_coef(sub)
        rows.append({"spec": "leave_one_out", "dropped_city": city, "coef": c, "p_value": p})
    return pd.DataFrame(rows)


def permutation_test(df: pd.DataFrame) -> pd.DataFrame:
    """Shuffle glass_center labels across cities (city-level), keep time structure."""
    rng = np.random.default_rng(SEED)
    cities = df[["city", "glass_center"]].drop_duplicates("city")
    labels = cities["glass_center"].to_numpy().copy()
    obs, _ = fit_glass_coef(df)
    nulls = []
    for i in range(N_PERM):
        shuffled = labels.copy()
        rng.shuffle(shuffled)
        map_g = dict(zip(cities["city"], shuffled))
        tmp = df.copy()
        tmp["glass_center"] = tmp["city"].map(map_g).astype(int)
        c, _ = fit_glass_coef(tmp)
        nulls.append(c)
    nulls = np.array(nulls, dtype=float)
    nulls = nulls[np.isfinite(nulls)]
    if len(nulls) and np.isfinite(obs):
        p_two = float(np.mean(np.abs(nulls) >= abs(obs)))
    else:
        p_two = float("nan")
    return pd.DataFrame(
        [
            {
                "observed_coef": obs,
                "n_perm": len(nulls),
                "null_mean": float(np.mean(nulls)) if len(nulls) else np.nan,
                "null_sd": float(np.std(nulls)) if len(nulls) else np.nan,
                "perm_p_two_sided": p_two,
                "note": "city-level label shuffle; associational placebo",
            }
        ]
    )


def alternate_controls(df: pd.DataFrame) -> pd.DataFrame:
    """Compare glass centers vs (a) all non-glass, (b) university-only controls, (c) Italy-only."""
    rows = []
    c, p = fit_glass_coef(df)
    rows.append({"spec": "all_controls", "coef": c, "p_value": p, "n": len(df)})

    uni = df[(df["glass_center"] == 1) | (df["has_university"] == 1)]
    c, p = fit_glass_coef(uni)
    rows.append({"spec": "university_cities_only", "coef": c, "p_value": p, "n": len(uni)})

    italy = df[df["region"] == "Italy"]
    c, p = fit_glass_coef(italy)
    rows.append({"spec": "italy_only", "coef": c, "p_value": p, "n": len(italy)})

    # Drop Florence+Venice as treatment intensity check
    drop_big = df[~df["city"].isin(["Florence", "Venice", "Murano"])]
    c, p = fit_glass_coef(drop_big)
    rows.append({"spec": "drop_florence_venice_murano", "coef": c, "p_value": p, "n": len(drop_big)})
    return pd.DataFrame(rows)


def main() -> None:
    df = load_panel()
    if len(df) < 20:
        log("Panel too small for LOO/permute", OUTPUT_LOGS / "robust.log")
        return
    loo = leave_one_out(df)
    loo.to_csv(OUTPUT_TABLES / "robust_leave_one_out_glass.csv", index=False)
    perm = permutation_test(df)
    perm.to_csv(OUTPUT_TABLES / "robust_glass_permutation.csv", index=False)
    alt = alternate_controls(df)
    alt.to_csv(OUTPUT_TABLES / "robust_alternate_controls.csv", index=False)
    log(
        f"LOO/permute/alt-controls done (n_perm={N_PERM}) -> {OUTPUT_TABLES}",
        OUTPUT_LOGS / "robust.log",
    )


if __name__ == "__main__":
    main()
