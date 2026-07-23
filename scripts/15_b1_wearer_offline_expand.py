#!/usr/bin/env python3
"""B1 evidence hunt (offline): expand named-wearer × dated-work panel from local Wikidata cache.

Does not require live SPARQL. Uses curated Ilardi wearers + data/processed/wikidata_age_at_work.csv.
Goal: raise n_persons with dated works toward decision threshold (≥5 adequate; ≥20 target).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS
from _utils import log

CURATED = DATA_CURATED / "ilardi_named_wearers.csv"
WORKS = DATA_PROCESSED / "wikidata_age_at_work.csv"


def main() -> None:
    wear = pd.read_csv(CURATED)
    wear = wear[wear["wikidata_qid"].notna() & (wear["wikidata_qid"].astype(str).str.len() > 0)].copy()
    wear["qid"] = wear["wikidata_qid"].astype(str).str.strip()

    if not WORKS.exists():
        log(f"Missing {WORKS}; skip B1 offline expand", OUTPUT_LOGS / "analysis.log")
        return
    w = pd.read_csv(WORKS)
    w["qid"] = w["qid"].astype(str)

    rows = []
    for _, p in wear.iterrows():
        sub = w[w["qid"] == p["qid"]]
        if sub.empty:
            rows.append(
                {
                    "person_id": p["person_id"],
                    "name": p["name"],
                    "qid": p["qid"],
                    "evidence_year": p["evidence_year"],
                    "evidence_age": p["evidence_age"],
                    "confidence": p["confidence"],
                    "n_dated_works": 0,
                    "n_before": 0,
                    "n_after": 0,
                    "share_after": np.nan,
                    "mean_work_age": np.nan,
                    "mean_age_delta": np.nan,
                    "status": "no_p800_p577_in_cache_hunt_sparql",
                }
            )
            continue
        ages = sub["age_at_work"].astype(float)
        ey = float(p["evidence_year"])
        birth = float(p["birth_year"]) if pd.notna(p["birth_year"]) else np.nan
        # work year ≈ birth + age
        work_years = birth + ages if np.isfinite(birth) else sub["pub_year"].astype(float)
        before = (work_years < ey).sum()
        after = (work_years >= ey).sum()
        n = before + after
        mean_work_age = float(ages.mean())
        eage = float(p["evidence_age"]) if pd.notna(p["evidence_age"]) else np.nan
        rows.append(
            {
                "person_id": p["person_id"],
                "name": p["name"],
                "qid": p["qid"],
                "evidence_year": p["evidence_year"],
                "evidence_age": p["evidence_age"],
                "confidence": p["confidence"],
                "n_dated_works": int(n),
                "n_before": int(before),
                "n_after": int(after),
                "share_after": round(after / n, 4) if n else np.nan,
                "mean_work_age": round(mean_work_age, 3),
                "mean_age_delta": round(mean_work_age - eage, 3) if np.isfinite(eage) else np.nan,
                "status": "linked_offline",
            }
        )

    panel = pd.DataFrame(rows)
    panel.to_csv(OUTPUT_TABLES / "b1_wearer_offline_panel.csv", index=False)

    linked = panel[panel["n_dated_works"] > 0]
    # Prefer high/medium confidence for summary test
    core = linked[linked["confidence"].isin(["high", "medium"])]
    summary = {
        "n_curated_with_qid": len(wear),
        "n_linked_dated_works": len(linked),
        "n_core_high_medium": len(core),
        "mean_share_after": round(float(core["share_after"].mean()), 4) if len(core) else np.nan,
        "mean_age_delta": round(float(core["mean_age_delta"].mean()), 4) if len(core) else np.nan,
        "total_works_before": int(core["n_before"].sum()) if len(core) else 0,
        "total_works_after": int(core["n_after"].sum()) if len(core) else 0,
        "decision_rule": "n_core>=5 adequate_direction; n_core>=20 target_for_B1_claim",
        "b1_status": (
            "adequate_direction_sample"
            if len(core) >= 5
            else "insufficient_hunt_more_names_or_sparql"
        ),
        "note": (
            "Offline expand from P800 cache; still curated notables not complete works. "
            "Direction only; B1 career-years still need wear×span panel."
        ),
    }
    pd.DataFrame([summary]).to_csv(OUTPUT_TABLES / "b1_wearer_offline_summary.csv", index=False)

    # Update micro ttests if we now have more persons than live SPARQL run
    if len(core) >= 1:
        pd.DataFrame(
            [
                {
                    "test": "b1_offline_share_notable_works_after_evidence",
                    "metric": "mean_share_after",
                    "value": summary["mean_share_after"],
                    "p_value": np.nan,
                    "n_persons": len(core),
                    "n_works_before": summary["total_works_before"],
                    "n_works_after": summary["total_works_after"],
                    "note": summary["note"] + f"; status={summary['b1_status']}",
                },
                {
                    "test": "b1_offline_mean_work_age_minus_evidence_age",
                    "metric": "mean_age_delta",
                    "value": summary["mean_age_delta"],
                    "p_value": np.nan,
                    "n_persons": len(core),
                    "n_works_before": summary["total_works_before"],
                    "n_works_after": summary["total_works_after"],
                    "note": summary["note"],
                },
            ]
        ).to_csv(OUTPUT_TABLES / "b1_wearer_offline_ttests.csv", index=False)

    log(
        f"B1 offline: linked={len(linked)}/{len(wear)} core={len(core)} -> {OUTPUT_TABLES}",
        OUTPUT_LOGS / "analysis.log",
    )


if __name__ == "__main__":
    main()
