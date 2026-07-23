#!/usr/bin/env python3
"""Process Wikidata age-at-notable-work into pre/post-1300 + robustness tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES
from _utils import log

SRC = DATA_RAW / "wikidata_age_at_work" / "age_at_work_all.json"
OUT_PANEL = DATA_PROCESSED / "wikidata_age_at_work.csv"
OUT_TEST = OUTPUT_TABLES / "age_at_work_ttests.csv"
OUT_HALF = OUTPUT_TABLES / "age_at_work_by_halfcentury.csv"

# Same glass-center birthplace set as Pantheon processor
GLASS_CITY_NAMES = {
    "florence",
    "firenze",
    "venice",
    "venezia",
    "milan",
    "milano",
    "murano",
    "pisa",
    "nuremberg",
    "nürnberg",
}


def _ttest_row(name: str, pre: pd.Series, post: pd.Series, note: str) -> dict:
    pre, post = pre.dropna(), post.dropna()
    if len(pre) >= 2 and len(post) >= 2:
        t, p = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t, p = np.nan, np.nan
    share_pre_45 = float((pre >= 45).mean()) if len(pre) else np.nan
    share_post_45 = float((post >= 45).mean()) if len(post) else np.nan
    return {
        "test": name,
        "mean_pre": round(float(pre.mean()), 4) if len(pre) else np.nan,
        "mean_post": round(float(post.mean()), 4) if len(post) else np.nan,
        "median_pre": round(float(pre.median()), 4) if len(pre) else np.nan,
        "median_post": round(float(post.median()), 4) if len(post) else np.nan,
        "share_age45plus_pre": round(share_pre_45, 4) if pd.notna(share_pre_45) else np.nan,
        "share_age45plus_post": round(share_post_45, 4) if pd.notna(share_post_45) else np.nan,
        "mean_diff_post_minus_pre": round(float(post.mean() - pre.mean()), 4)
        if len(pre) and len(post)
        else np.nan,
        "t_stat": round(float(t), 4) if pd.notna(t) else np.nan,
        "p_value": round(float(p), 6) if pd.notna(p) else np.nan,
        "n_pre": len(pre),
        "n_post": len(post),
        "note": note,
    }


def _qid(uri: str) -> str:
    return str(uri).rstrip("/").split("/")[-1]


def _attach_birthplace(earliest: pd.DataFrame) -> pd.DataFrame:
    """Join birthplace / glass_center from Pantheon + Wikidata + optional P19 dump."""
    out = earliest.copy()
    out["qid"] = out["person"].map(_qid)
    out["bplace_name"] = pd.NA
    out["glass_center"] = False

    pantheon_path = DATA_PROCESSED / "pantheon_persons_europe.csv"
    if pantheon_path.exists():
        p = pd.read_csv(pantheon_path, usecols=["wd_id", "bplace_name", "glass_center"])
        p["qid"] = p["wd_id"].astype(str)
        p = p.drop_duplicates("qid")
        out = out.merge(
            p[["qid", "bplace_name", "glass_center"]].rename(
                columns={"bplace_name": "bplace_pantheon", "glass_center": "glass_pantheon"}
            ),
            on="qid",
            how="left",
        )
        out["bplace_name"] = out["bplace_pantheon"].combine_first(out["bplace_name"])
        out["glass_center"] = out["glass_pantheon"].fillna(False).astype(bool)
        out = out.drop(columns=[c for c in ("bplace_pantheon", "glass_pantheon") if c in out.columns])

    wd_path = DATA_PROCESSED / "wikidata_scholars_historical.csv"
    if wd_path.exists():
        w = pd.read_csv(wd_path, usecols=["person_uri", "birthplace"])
        w["qid"] = w["person_uri"].map(_qid)
        w = w.drop_duplicates("qid")
        out = out.merge(w[["qid", "birthplace"]], on="qid", how="left")
        out["bplace_name"] = out["bplace_name"].combine_first(out["birthplace"])
        out = out.drop(columns=["birthplace"])

    p19_path = DATA_RAW / "wikidata_age_at_work" / "birthplaces.json"
    glass_qids = {"Q2044", "Q641", "Q490", "Q13375", "Q2090", "Q168602"}
    if p19_path.exists():
        bp = pd.DataFrame(json.loads(p19_path.read_text(encoding="utf-8")))
        if len(bp):
            bp["qid"] = bp["person"].map(_qid)
            bp = bp.drop_duplicates("qid")
            bp["glass_p19"] = bp["place_qid"].isin(glass_qids)
            out = out.merge(bp[["qid", "place_qid", "glass_p19"]], on="qid", how="left")
            out["glass_center"] = out["glass_center"].fillna(False).astype(bool) | out[
                "glass_p19"
            ].fillna(False).astype(bool)
            out = out.drop(columns=[c for c in ("glass_p19",) if c in out.columns])

    # Fill glass_center from name match when Pantheon miss
    low = out["bplace_name"].astype(str).str.lower()
    name_glass = low.isin(GLASS_CITY_NAMES)
    out["glass_center"] = out["glass_center"].fillna(False).astype(bool) | name_glass
    return out


def main() -> None:
    if not SRC.exists():
        log(f"Missing {SRC}; run 01e_fetch_age_at_work.py", OUTPUT_LOGS / "analysis.log")
        return
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    df = pd.DataFrame(rows)
    df = df[(df["age_at_work"] >= 15) & (df["age_at_work"] <= 90)]
    earliest = df.sort_values("pub_year").groupby("person", as_index=False).first()
    latest = df.sort_values("pub_year").groupby("person", as_index=False).last()
    earliest = _attach_birthplace(earliest)
    latest = _attach_birthplace(latest)
    earliest.to_csv(OUT_PANEL, index=False)

    tests: list[dict] = []
    pre_e = earliest[earliest["birth_year"] < 1280]["age_at_work"]
    post_e = earliest[earliest["birth_year"] >= 1280]["age_at_work"]
    tests.append(
        _ttest_row(
            "age_at_first_notable_work_birth_pre_vs_post_1280",
            pre_e,
            post_e,
            "Wikidata P800+P577; earliest notable work age; birth split 1280",
        )
    )
    pre_l = latest[latest["birth_year"] < 1280]["age_at_work"]
    post_l = latest[latest["birth_year"] >= 1280]["age_at_work"]
    tests.append(
        _ttest_row(
            "age_at_last_notable_work_birth_pre_vs_post_1280",
            pre_l,
            post_l,
            "Wikidata; latest listed notable work age; experience-premium predicts rise",
        )
    )
    pre_w = earliest[(earliest["birth_year"] >= 1200) & (earliest["birth_year"] < 1280)]["age_at_work"]
    post_w = earliest[(earliest["birth_year"] >= 1280) & (earliest["birth_year"] < 1360)]["age_at_work"]
    tests.append(
        _ttest_row(
            "age_at_first_notable_work_local_window_1200_1360",
            pre_w,
            post_w,
            "Local birth window ± around spectacles; reduces era composition confounding",
        )
    )

    # Glass-center born: if experience-premium unlock is geographically mediated by supply,
    # glass-center cohorts should show *larger* age rise post-1280 than controls.
    # Test: within post-1280, glass vs control mean age (B predicts glass older).
    post1280 = earliest[earliest["birth_year"] >= 1280]
    glass_post = post1280[post1280["glass_center"]]["age_at_work"]
    ctrl_post = post1280[~post1280["glass_center"]]["age_at_work"]
    tests.append(
        _ttest_row(
            "age_at_first_work_glass_vs_control_birth_ge1280",
            ctrl_post,
            glass_post,
            "Post-1280 births: glass-center birthplace vs others; B predicts glass older "
            f"(n_glass={len(glass_post)}, n_ctrl={len(ctrl_post)})",
        )
    )
    # Diff-in-diff style: (glass post−pre) vs (control post−pre) via interaction contrast
    # Approximated as t-test of age among glass born 1280–1500 vs glass born <1280
    glass = earliest[earliest["glass_center"]]
    g_pre = glass[glass["birth_year"] < 1280]["age_at_work"]
    g_post = glass[(glass["birth_year"] >= 1280) & (glass["birth_year"] < 1500)]["age_at_work"]
    tests.append(
        _ttest_row(
            "age_at_first_work_glass_birth_pre_vs_post_1280",
            g_pre,
            g_post,
            "Glass-center births only; experience-premium predicts age rise after spectacles",
        )
    )
    # Drop extreme medieval monastic ages: birth 1150–1550 only
    mid = earliest[(earliest["birth_year"] >= 1150) & (earliest["birth_year"] < 1550)]
    tests.append(
        _ttest_row(
            "age_at_first_work_birth_1150_1550_split_1280",
            mid[mid["birth_year"] < 1280]["age_at_work"],
            mid[mid["birth_year"] >= 1280]["age_at_work"],
            "Trimmed birth window 1150–1550 to reduce deep-medieval composition bias",
        )
    )

    pd.DataFrame(tests).to_csv(OUT_TEST, index=False)

    # Half-century descriptive series (earliest work age)
    earliest["half_century"] = (earliest["birth_year"] // 50) * 50
    half = (
        earliest.groupby("half_century", as_index=False)
        .agg(
            n=("age_at_work", "size"),
            mean_age=("age_at_work", "mean"),
            median_age=("age_at_work", "median"),
            share45=("age_at_work", lambda s: float((s >= 45).mean())),
        )
        .round(4)
    )
    half.to_csv(OUT_HALF, index=False)

    log(
        f"age_at_work: panel={len(earliest)} persons, tests={len(tests)}, "
        f"glass_matched={int(earliest['glass_center'].sum())} -> {OUT_TEST}",
        OUTPUT_LOGS / "analysis.log",
    )
    print(pd.DataFrame(tests).to_string(index=False))
    print(half.to_string(index=False))


if __name__ == "__main__":
    main()
