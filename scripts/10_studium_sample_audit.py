#!/usr/bin/env python3
"""Stratified random Studium sample + automated consistency audit.

Produces a review sheet for human verification. Automated flags estimate
misclassification risk; they are not a substitute for page-level reading.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_TABLES, OUTPUT_LOGS, ROOT
from _utils import log

N_SAMPLE = 300
SEED = 20260721
JSONL_CANDIDATES = [
    DATA_RAW / "studium_persons.jsonl",
    ROOT.parent / "download_data" / "studium_persons.jsonl",
]


def _find_jsonl() -> Path | None:
    for p in JSONL_CANDIDATES:
        if p.exists() and p.stat().st_size > 100_000:
            return p
    return None


def auto_flags(row: pd.Series) -> list[str]:
    flags: list[str] = []
    q = row.get("life_date_quality")
    by, dy = row.get("birth_year"), row.get("death_year")
    age = row.get("age_at_activity_end")
    span = row.get("observed_activity_span_years")
    a0, a1 = row.get("activity_start"), row.get("activity_end")

    if q == "single_year_not_birth" and pd.notna(by):
        flags.append("ERROR_single_year_used_as_birth")
    if q == "single_year_not_birth":
        flags.append("INFO_single_year_death_or_floruit_only")
    if pd.notna(by) and pd.notna(dy) and float(by) > float(dy):
        flags.append("ERROR_birth_after_death")
    if pd.notna(age) and (float(age) < 10 or float(age) > 110):
        flags.append("WARN_implausible_age")
    if pd.notna(span) and float(span) > 80:
        flags.append("WARN_very_long_observed_span")
    if pd.notna(a0) and pd.notna(a1) and float(a0) > float(a1):
        flags.append("ERROR_activity_start_after_end")
    if pd.notna(by) and pd.notna(a0) and float(a0) < float(by):
        flags.append("WARN_activity_before_birth")
    if q in ("multi_year_uncertain", "unparsed") and pd.notna(age):
        flags.append("WARN_age_from_uncertain_life")
    if row.get("is_master") and row.get("is_student"):
        flags.append("WARN_status_both_master_and_student")
    return flags


def load_raw_snippets(ids: set[str], jsonl: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    with jsonl.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            rid = str(rec.get("_id", ""))
            if rid not in ids:
                continue
            identity = rec.get("identity") or {}
            snippet = {
                "datesOfLife": identity.get("datesOfLife"),
                "datesOfActivity": identity.get("datesOfActivity"),
                "activityMediane": identity.get("activityMediane"),
                "status": identity.get("status"),
            }
            out[rid] = json.dumps(snippet, ensure_ascii=False)[:2000]
            if len(out) >= len(ids):
                break
    return out


def main() -> None:
    path = DATA_PROCESSED / "studium_paris_scholars.csv"
    if not path.exists():
        log("No studium_paris_scholars.csv", OUTPUT_LOGS / "fetch.log")
        return
    df = pd.read_csv(path)
    df["studium_id"] = df["studium_id"].astype(str)

    # Stratify: life quality × era bucket
    df["era"] = pd.cut(
        df["anchor_year"],
        bins=[1099, 1299, 1385, 1500, 1701],
        labels=["pre1300", "1300_1385", "1386_1500", "post1500"],
    )
    strata = df.dropna(subset=["era"]).groupby(["life_date_quality", "era"], observed=True)
    parts = []
    rng = np.random.default_rng(SEED)
    # Aim ~N_SAMPLE with proportional allocation, min 5 per non-empty stratum
    total = len(df)
    for (q, era), g in strata:
        n = max(5, int(round(N_SAMPLE * len(g) / total)))
        n = min(n, len(g))
        idx = rng.choice(g.index.to_numpy(), size=n, replace=False)
        parts.append(df.loc[idx])
    sample = pd.concat(parts).drop_duplicates(subset=["studium_id"])
    if len(sample) > N_SAMPLE:
        sample = sample.sample(n=N_SAMPLE, random_state=SEED)
    sample = sample.copy()
    sample["auto_flags"] = sample.apply(lambda r: ";".join(auto_flags(r)), axis=1)
    sample["needs_human_review"] = sample["auto_flags"].str.contains("ERROR|WARN", regex=True)
    sample["human_ok"] = ""  # fill manually: ok / birth_misread / death_only / etc.
    sample["human_notes"] = ""

    jsonl = _find_jsonl()
    if jsonl:
        snippets = load_raw_snippets(set(sample["studium_id"]), jsonl)
        sample["raw_identity_snippet"] = sample["studium_id"].map(snippets)
    else:
        sample["raw_identity_snippet"] = ""

    out_cols = [
        "studium_id",
        "reference",
        "status",
        "is_master",
        "is_student",
        "life_date_quality",
        "birth_year",
        "death_year",
        "activity_start",
        "activity_end",
        "anchor_year",
        "observed_activity_span_years",
        "age_at_activity_end",
        "era",
        "auto_flags",
        "needs_human_review",
        "human_ok",
        "human_notes",
        "raw_identity_snippet",
    ]
    sample[out_cols].to_csv(OUTPUT_TABLES / "studium_sample_audit.csv", index=False)

    # Automated rate summary on FULL file (measurement process audit)
    full_flags = df.apply(auto_flags, axis=1)
    flag_counts: dict[str, int] = {}
    for fl in full_flags:
        for f in fl:
            flag_counts[f] = flag_counts.get(f, 0) + 1
    summary = pd.DataFrame(
        [
            {
                "n_scholars": len(df),
                "n_audit_sample": len(sample),
                "sample_share_needs_review": round(float(sample["needs_human_review"].mean()), 4),
                "n_with_trusted_life": int(
                    df["life_date_quality"].isin(["interval_meta", "text_range"]).sum()
                ),
                "n_single_year_not_birth": int((df["life_date_quality"] == "single_year_not_birth").sum()),
                "n_age_available_trusted": int(
                    df[
                        df["life_date_quality"].isin(["interval_meta", "text_range"])
                        & df["age_at_activity_end"].notna()
                    ].shape[0]
                ),
                "share_birth_filled": round(float(df["birth_year"].notna().mean()), 4),
            }
        ]
    )
    for k, v in sorted(flag_counts.items()):
        summary[f"flag_{k}"] = v
    summary.to_csv(OUTPUT_TABLES / "studium_audit_summary.csv", index=False)

    log(
        f"Studium audit sample n={len(sample)}; trusted life ages="
        f"{summary['n_age_available_trusted'].iloc[0]} -> {OUTPUT_TABLES}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
