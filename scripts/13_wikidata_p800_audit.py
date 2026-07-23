#!/usr/bin/env python3
"""Audit Wikidata P800/P577 age-at-work panel: coverage, counts, composition.

Demotes this measure from primary reject evidence: P800 is curated notables,
P577 is publication/issue date — not a complete works chronology.
Outputs exploratory diagnostics only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

SPLIT = 1280
RNG = np.random.default_rng(42)


def main() -> None:
    works = pd.read_csv(DATA_PROCESSED / "wikidata_age_at_work.csv")
    scholars = pd.read_csv(DATA_PROCESSED / "wikidata_scholars_historical.csv")

    # Per-person P800 counts among those with dated works
    per = (
        works.groupby(["qid", "birth_year"], dropna=False)
        .agg(
            n_p800=("work", "count"),
            age_first=("age_at_work", "min"),
            age_last=("age_at_work", "max"),
            glass_center=("glass_center", "max"),
            bplace=("bplace_name", "first"),
        )
        .reset_index()
    )
    per["cohort"] = np.where(per["birth_year"] >= SPLIT, "birth_ge1280", "birth_lt1280")

    # Coverage vs scholars with birth years
    sch = scholars.dropna(subset=["birth_year"]).copy()
    sch["qid"] = sch["person_uri"].astype(str).str.extract(r"(Q\d+)", expand=False)
    sch["cohort"] = np.where(sch["birth_year"] >= SPLIT, "birth_ge1280", "birth_lt1280")
    with_works = set(per["qid"].dropna().astype(str))
    sch["has_p800_dated"] = sch["qid"].isin(with_works)

    cov_rows = []
    for cohort, g in sch.groupby("cohort"):
        cov_rows.append(
            {
                "cohort": cohort,
                "n_scholars_with_birth": len(g),
                "n_with_p800_p577": int(g["has_p800_dated"].sum()),
                "coverage_rate": round(float(g["has_p800_dated"].mean()), 4),
            }
        )
    cov = pd.DataFrame(cov_rows)
    cov.to_csv(OUTPUT_TABLES / "wikidata_p800_coverage.csv", index=False)

    count_summary = (
        per.groupby("cohort")["n_p800"]
        .describe(percentiles=[0.25, 0.5, 0.75])
        .reset_index()
    )
    count_summary.to_csv(OUTPUT_TABLES / "wikidata_p800_counts_by_cohort.csv", index=False)

    # Occupation mix among scholars with birth (crude)
    if "occupation" in sch.columns:
        occ = (
            sch.assign(occ=sch["occupation"].fillna("unknown").astype(str).str.split(",").str[0])
            .groupby(["cohort", "occ"])
            .size()
            .reset_index(name="n")
        )
        occ["share"] = occ.groupby("cohort")["n"].transform(lambda s: s / s.sum())
        occ.to_csv(OUTPUT_TABLES / "wikidata_p800_occupation_mix.csv", index=False)

    # Stratified pilot sample for hand audit (50–100)
    sample_parts = []
    for cohort, g in per.groupby("cohort"):
        n = min(40, len(g))
        sample_parts.append(g.sample(n=n, random_state=42))
    pilot = pd.concat(sample_parts, ignore_index=True)
    pilot["hand_audit_status"] = "pending"
    pilot["hand_audit_notes"] = ""
    pilot.to_csv(OUTPUT_TABLES / "wikidata_p800_hand_audit_sample.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "n_dated_work_rows": len(works),
                "n_persons_with_dated_p800": len(per),
                "median_p800_pre": float(per.loc[per["cohort"] == "birth_lt1280", "n_p800"].median())
                if (per["cohort"] == "birth_lt1280").any()
                else np.nan,
                "median_p800_post": float(per.loc[per["cohort"] == "birth_ge1280", "n_p800"].median())
                if (per["cohort"] == "birth_ge1280").any()
                else np.nan,
                "interpretation": (
                    "exploratory_only; P800 curated notables + P577 publication dates; "
                    "not complete works; not primary reject evidence for B1"
                ),
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "wikidata_p800_audit_summary.csv", index=False)
    log(
        f"P800 audit: persons={len(per)}, pilot={len(pilot)} -> {OUTPUT_TABLES}",
        OUTPUT_LOGS / "analysis.log",
    )


if __name__ == "__main__":
    main()
