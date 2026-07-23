#!/usr/bin/env python3
"""Run share45 / career-span pre-post-1300 tests on underused scholar panels."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES
from _share45_test import share45_row
from _utils import log

OUT = OUTPUT_TABLES / "alt_scholar_age_ttests.csv"


def _pantheon_tests() -> list[dict]:
    path = DATA_PROCESSED / "pantheon_scholars_europe.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    df = df.dropna(subset=["birthyear", "deathyear"])
    df = df[(df["deathyear"] >= 1100) & (df["deathyear"] < 1700)]
    df["age_at_death"] = df["deathyear"] - df["birthyear"]
    df = df[(df["age_at_death"] >= 20) & (df["age_at_death"] <= 100)]
    pre = df[df["deathyear"] < 1300]["age_at_death"]
    post = df[df["deathyear"] >= 1300]["age_at_death"]
    rows = [
        share45_row(
            test="pantheon_age_at_death_pre_vs_post_1300",
            pre=pre,
            post=post,
            note="Pantheon EU scholar occupations; death-year split; elite fame sample",
        )
    ]
    glass = df[df["glass_center"]]
    ctrl = df[~df["glass_center"]]
    if len(glass) >= 30 and len(ctrl) >= 30:
        rows.append(
            share45_row(
                test="pantheon_glass_birthcity_vs_control_age_at_death",
                pre=ctrl["age_at_death"],
                post=glass["age_at_death"],
                note="Glass-center birthplace vs control; cross-section not DiD",
            )
        )
    return rows


def _wikidata_tests() -> list[dict]:
    path = DATA_PROCESSED / "wikidata_scholars_historical.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    df = df.dropna(subset=["birth_year", "death_year"])
    df["age_at_death"] = df["death_year"] - df["birth_year"]
    df = df[(df["age_at_death"] >= 20) & (df["age_at_death"] <= 100)]
    pre = df[df["death_year"] < 1300]["age_at_death"]
    post = df[df["death_year"] >= 1300]["age_at_death"]
    return [
        share45_row(
            test="wikidata_intellectuals_age_at_death_pre_vs_post_1300",
            pre=pre,
            post=post,
            note="Wikidata European intellectuals (merged occupations, death 1100–1850); death-year split",
        )
    ]


def _stelter_tests() -> list[dict]:
    """Stelter HRE appointments are almost entirely post-1300 — cannot test invention BP.

    Instead test whether later diffusion eras show longer careers / more age-45 coverage
    (experience-premium unlock predicts yes as spectacles become mass goods).
    """
    path = DATA_PROCESSED / "stelter_scholars.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path)
    df = df.dropna(subset=["birth_year", "start_year", "end_year"])
    df = df[(df["end_year"] > df["start_year"]) & (df["end_year"] - df["start_year"] <= 80)]
    df["career_span"] = df["end_year"] - df["start_year"]
    df["age_at_start"] = df["start_year"] - df["birth_year"]
    df = df[(df["age_at_start"] >= 18) & (df["age_at_start"] <= 70)]
    # Dataset has ~0 starts before 1300; restrict to testable window
    df = df[(df["start_year"] >= 1300) & (df["start_year"] < 1600)]
    if len(df) < 100:
        return []

    df["active_at_45"] = (
        (df["birth_year"] + 45).between(df["start_year"], df["end_year"])
    ).astype(float)

    early = df[(df["start_year"] >= 1300) & (df["start_year"] < 1400)]
    late = df[(df["start_year"] >= 1400) & (df["start_year"] < 1500)]
    rows: list[dict] = []
    if len(early) >= 30 and len(late) >= 50:
        rows.append(
            share45_row(
                test="stelter_career_span_1300s_vs_1400s",
                pre=early["career_span"],
                post=late["career_span"],
                threshold=20,
                note="Stelter HRE; 1300s vs 1400s starts; long-span share (thr=20y); spectacles already traded in 14c",
            )
        )
        rows.append(
            share45_row(
                test="stelter_active_at_45_1300s_vs_1400s",
                pre=early["active_at_45"],
                post=late["active_at_45"],
                threshold=1,
                note="Stelter; share of appointments covering age 45; experience-premium predicts rise as glasses diffuse",
            )
        )
    mid = df[(df["start_year"] >= 1400) & (df["start_year"] < 1450)]
    print_era = df[(df["start_year"] >= 1450) & (df["start_year"] < 1500)]
    if len(mid) >= 50 and len(print_era) >= 50:
        rows.append(
            share45_row(
                test="stelter_active_at_45_1400_44_vs_1450_99",
                pre=mid["active_at_45"],
                post=print_era["active_at_45"],
                threshold=1,
                note="Stelter; pre-print vs early-print cohorts; if glasses-not-print drove late careers, 1400-44 should already be high",
            )
        )
    return rows


def main() -> None:
    rows: list[dict] = []
    rows.extend(_pantheon_tests())
    rows.extend(_wikidata_tests())
    rows.extend(_stelter_tests())
    if not rows:
        log("alt_scholar_age_tests: no inputs", OUTPUT_LOGS / "analysis.log")
        return
    pd.DataFrame(rows).to_csv(OUT, index=False)
    log(f"alt_scholar_age_tests: {len(rows)} rows -> {OUT}", OUTPUT_LOGS / "analysis.log")


if __name__ == "__main__":
    main()
