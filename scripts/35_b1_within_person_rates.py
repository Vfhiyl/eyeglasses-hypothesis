#!/usr/bin/env python3
"""B1 within-person letter rates around spectacle evidence (EXPLORATORY).

The pair estimand (script 25) cannot distinguish "lingered a few more
years" from "late-life output burst": its outcome is the last dated
activity year. This script takes the only design that can touch that
question with current data: complete edited letter corpora of documented
wearers, comparing dated-letter rates in the decade before vs after the
spectacle evidence year.

Corpora used (complete editions, one row per dated letter):
  alessandra_strozzi — Guasti 1877 edition chrono (outputs/tables/
                       b1_alessandra_letter_chrono.csv, modern_year)
  ammannati          — Cherubini edition chrono (outputs/tables/
                       b1_ammannati_cherubini_letter_chrono.csv, year)

NOT a causal estimate. Known biases, all material:
  * editorial survival bias (editors preserve late-life letters of famous
    people disproportionately; Guasti's Alessandra corpus is known to be
    denser late),
  * no control series (a non-wearer's rate drift is unknown),
  * rate counts letters, not intellectual quality or near-work hours,
  * evidence year is late (people wear spectacles years before the first
    surviving mention), which shifts genuine pre-wear years into the
    "before" window.
Read as: "does the dated series even continue / thicken after the
spectacle evidence?" — nothing stronger.

Outputs:
  outputs/tables/b1_within_person_rates.csv
  outputs/tables/b1_within_person_rates_method.md
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
OUT_CSV = OUTPUT_TABLES / "b1_within_person_rates.csv"
OUT_MD = OUTPUT_TABLES / "b1_within_person_rates_method.md"

CORPORA = [
    {
        "person_id": "alessandra_strozzi",
        "file": OUTPUT_TABLES / "b1_alessandra_letter_chrono.csv",
        "year_col": "modern_year",
        "corpus": "Guasti 1877 complete letters",
    },
    {
        "person_id": "ammannati",
        "file": OUTPUT_TABLES / "b1_ammannati_cherubini_letter_chrono.csv",
        "year_col": "year",
        "corpus": "Cherubini edition epistolario",
    },
]

WINDOW = 10  # years each side of the evidence year


def _y(x: object) -> int | None:
    if x is None or str(x).strip() == "":
        return None
    try:
        return int(float(str(x)))
    except ValueError:
        return None


def main() -> None:
    census = {r["person_id"]: r for r in csv.DictReader(CENSUS.open())}
    rows = []
    year_lines = []
    for spec in CORPORA:
        pid = spec["person_id"]
        c = census[pid]
        birth, death = _y(c.get("birth_year")), _y(c.get("death_year"))
        evid = _y(c.get("evidence_year"))
        years = []
        for r in csv.DictReader(spec["file"].open()):
            y = _y(r.get(spec["year_col"]))
            if y is None:
                continue
            if birth is not None and y < birth + 15:
                continue
            if death is not None and y > death:
                continue
            years.append(y)
        counts = Counter(years)
        lo_before = evid - WINDOW
        if birth is not None:
            lo_before = max(lo_before, birth + 20)
        hi_after = evid + WINDOW - 1
        if death is not None:
            hi_after = min(hi_after, death)
        before_years = list(range(lo_before, evid))
        after_years = list(range(evid, hi_after + 1))
        n_before = sum(counts.get(y, 0) for y in before_years)
        n_after = sum(counts.get(y, 0) for y in after_years)
        rate_b = n_before / len(before_years) if before_years else None
        rate_a = n_after / len(after_years) if after_years else None
        last_letter = max(years) if years else None
        rows.append(
            {
                "person_id": pid,
                "corpus": spec["corpus"],
                "birth": birth,
                "death": death,
                "evidence_year": evid,
                "n_dated_letters_total": len(years),
                "window_before": f"{lo_before}-{evid - 1}",
                "window_after": f"{evid}-{hi_after}",
                "n_before": n_before,
                "n_after": n_after,
                "rate_before_per_yr": "" if rate_b is None else round(rate_b, 2),
                "rate_after_per_yr": "" if rate_a is None else round(rate_a, 2),
                "rate_ratio_after_before": (
                    "" if not rate_b or rate_a is None else round(rate_a / rate_b, 2)
                ),
                "last_dated_letter_year": last_letter,
                "years_evidence_to_last_letter": (
                    "" if last_letter is None or evid is None else last_letter - evid
                ),
            }
        )
        for y in sorted(set(before_years + after_years)):
            year_lines.append(f"{pid},{y},{counts.get(y, 0)}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    def li(r: dict) -> str:
        return (
            f"| {r['person_id']} | {r['n_dated_letters_total']} | {r['window_before']}"
            f" | {r['window_after']} | {r['rate_before_per_yr']} | {r['rate_after_per_yr']}"
            f" | {r['rate_ratio_after_before']} | {r['years_evidence_to_last_letter']} |"
        )

    md = "\n".join(
        [
            "# B1 within-person letter rates (EXPLORATORY — not a SESOI test)",
            "",
            "**Date:** 2026-08-12  ",
            "**Script:** `35_b1_within_person_rates.py` → `b1_within_person_rates.csv`",
            "",
            "Question probed: after the first surviving spectacle evidence, does the",
            "wearer's dated letter series continue / thicken (\"burst\") or thin out",
            "(\"linger\")? Complete edited corpora only; ±10y windows around the",
            "evidence year, truncated at adulthood and death.",
            "",
            "| person | letters | before win | after win | rate before | rate after | ratio | evid→last letter (y) |",
            "|--------|--------:|-----------|-----------|------------:|-----------:|------:|---------------------:|",
            *[li(r) for r in rows],
            "",
            "Per-year counts: see `b1_within_person_rates_by_year.csv`.",
            "",
            "## Hard caveats (do not skip)",
            "",
            "1. Editorial/survival bias: complete editions still reflect what was",
            "   kept; Alessandra's corpus is known to be denser late in life.",
            "2. No control series — a non-wearer's rate drift over the same ages is",
            "   unknown; aging alone changes letter volume.",
            "3. Rates count letters, not near-work hours or quality; a signature",
            "   equals an essay.",
            "4. Evidence year is late (first surviving mention, not first wear), so",
            "   genuine post-wear years leak into the before window.",
            "5. n=2 persons. This is a design demo showing the data CAN support",
            "   within-person analysis; expansion candidates: Mazzei→Datini corpus",
            "   (130 dated letters; Mazzei's own occhiali self-reports are in the",
            "   letters but he is not yet in the roster census), Ammannati tomo3,",
            "   Lotto's libro di spese, Pepys diary (ends 1669 for eye fears —",
            "   a NEGATIVE within-person case worth coding).",
            "",
            "Verdict impact: none by itself. Use only to scope the future",
            "within-person estimand (pre-registered rate ratio with control",
            "series and editorial-density adjustment).",
            "",
        ]
    )
    OUT_MD.write_text(md, encoding="utf-8")

    by_year = OUTPUT_TABLES / "b1_within_person_rates_by_year.csv"
    by_year.write_text(
        "person_id,year,n_letters\n" + "\n".join(year_lines) + "\n", encoding="utf-8"
    )

    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("wrote", by_year)
    for r in rows:
        print(
            f"{r['person_id']:20s} letters={r['n_dated_letters_total']:4d} "
            f"rate {r['rate_before_per_yr']} -> {r['rate_after_per_yr']} "
            f"(ratio {r['rate_ratio_after_before']}); evid→last {r['years_evidence_to_last_letter']}y"
        )


if __name__ == "__main__":
    main()
