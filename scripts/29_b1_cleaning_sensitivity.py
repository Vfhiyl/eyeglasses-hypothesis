#!/usr/bin/env python3
"""B1 cleaning sensitivity — does control hygiene manufacture SESOI+5?

AUDIT ANSWER (2026-08-12): YES. The pass-era "full_clean" layer (overlays +
per-wearer excludes + one-directional tip-strips) moved the labor median
from 2.5 (CI crossing 0, FAIL) to 11.25 with share(delta>0)=1.0 (PASS_RAW).
That layer was outcome-aware and has been removed from the measurement path
(see docs/B1_CURATION_AUDIT_2026-08-12.md; data restored by script 33).

Arms recomputed on the RESTORED data (historical pass-era numbers live in
snapshot commit 9d95fa1):
  dirty_max              — raw region matches; force use_in_primary on all chronos
  raw_match              — raw matches only; no overlays/excludes; demotions respected
  overlay_exclude_layer  — DEPRECATED: re-applies the outcome-aware overlay/
                           exclude layer + pass-era asymmetric skips on the
                           restored chronos, to show what the layer does
  corrected_primary      — passthrough of script 25 corrected summary
                           (symmetric death<45, cluster bootstrap)

Outputs:
  outputs/tables/b1_labor_cleaning_sensitivity.csv
  outputs/tables/b1_cleaning_sensitivity_method.md
"""
from __future__ import annotations

import csv
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, OUTPUT_TABLES

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
MATCHES = OUTPUT_TABLES / "b1_roster_control_matches_region.csv"
CURATED = DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"
CTRL_OVERLAYS = DATA_CURATED / "b1_output_strict_control_overlays.csv"
CTRL_EXCLUDES = DATA_CURATED / "b1_output_control_excludes.csv"
OUT_SUM = OUTPUT_TABLES / "b1_output_estimand_summary.csv"
PRIM_SUM = OUTPUT_TABLES / "b1_primary_estimand_summary.csv"
OUT_CSV = OUTPUT_TABLES / "b1_labor_cleaning_sensitivity.csv"
OUT_MD = OUTPUT_TABLES / "b1_cleaning_sensitivity_method.md"


def _y(x: object) -> int | None:
    if x is None or str(x).strip() == "":
        return None
    try:
        return int(float(str(x)))
    except ValueError:
        return None


def _f(x: object) -> float | None:
    if x is None or str(x).strip() == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def boot_median(xs: list[float], seed: int = 31) -> tuple[float, float, float]:
    rng = random.Random(seed)
    if not xs:
        return float("nan"), float("nan"), float("nan")
    meds: list[float] = []
    n = len(xs)
    for _ in range(2000):
        meds.append(statistics.median([xs[rng.randrange(n)] for _ in range(n)]))
    meds.sort()
    return statistics.median(xs), meds[int(0.025 * 1999)], meds[int(0.975 * 1999)]


def main() -> None:
    census = {r["person_id"]: r for r in csv.DictReader(CENSUS.open())}
    matches = {
        r["person_id"]: dict(r)
        for r in csv.DictReader(MATCHES.open())
        if r.get("match_status") == "matched"
    }
    curated = {r["qid"]: r for r in csv.DictReader(CURATED.open())}
    excludes: dict[str, set[str]] = {}
    for r in csv.DictReader(CTRL_EXCLUDES.open()):
        excludes.setdefault(r["person_id"], set()).add(r["control_qid"])
    overlays: dict[str, list[str]] = {}
    for r in csv.DictReader(CTRL_OVERLAYS.open()):
        overlays.setdefault(r["person_id"], []).append(r["extra_control_qid"])

    def t_work(pid: str) -> float | None:
        t = census[pid]
        b, evid, ya = _y(t.get("birth_year")), _y(t.get("evidence_year")), _f(
            t.get("years_after_evidence")
        )
        if b is None or evid is None or ya is None:
            return None
        last = evid + ya
        d = _y(t.get("death_year"))
        if d is not None:
            last = min(last, d)
        return max(0.0, last - (b + 45))

    def c_work(qid: str, force_use: bool) -> float | None:
        row = curated.get(qid)
        if not row:
            return None
        use = str(row.get("use_in_primary", "True")).lower() in {"true", "1", "yes"}
        if not force_use and not use:
            return None
        b, last = _y(row.get("birth_year")), _y(row.get("last_nearwork_year"))
        if b is None or last is None:
            return None
        return max(0.0, last - (b + 45))

    def run_labor(mode: str) -> dict[str, object]:
        deltas: list[float] = []
        skip_d45 = 0
        skip_t0 = 0
        for pid, m in matches.items():
            if pid not in census:
                continue
            bi, di = _y(census[pid].get("birth_year")), _y(census[pid].get("death_year"))
            if mode == "overlay_exclude_layer" and bi is not None and di is not None and di < bi + 45:
                skip_d45 += 1
                continue
            tw = t_work(pid)
            if tw is None:
                continue
            if mode == "overlay_exclude_layer" and tw <= 0:
                skip_t0 += 1
                continue
            qids = [q for q in (m.get("matched_control_qids") or "").split(";") if q]
            if mode == "overlay_exclude_layer":
                for q in overlays.get(pid, []):
                    if q not in qids:
                        qids.append(q)
                qids = [q for q in qids if q not in excludes.get(pid, set())]
            force = mode == "dirty_max"
            cs = [cw for q in qids if (cw := c_work(q, force_use=force)) is not None]
            if not cs:
                continue
            deltas.append(tw - statistics.median(cs))
        med, lo, hi = boot_median(deltas)
        sesoi5 = (
            "PASS_RAW"
            if deltas and med >= 5 and lo >= 0
            else "FAIL_OR_UNAVAILABLE"
        )
        sesoi15 = "PASS_RAW" if deltas and med >= 15 else "FAIL"
        return {
            "estimand": "labor_work_after_45",
            "mode": mode,
            "n_pairs": len(deltas),
            "median_delta": "" if not deltas else round(med, 2),
            "boot95_lo": "" if not deltas else round(lo, 2),
            "boot95_hi": "" if not deltas else round(hi, 2),
            "sesoi5": sesoi5,
            "sesoi15": sesoi15,
            "n_ge_5": sum(1 for d in deltas if d >= 5),
            "share_delta_gt_0": (
                "" if not deltas else round(sum(1 for d in deltas if d > 0) / len(deltas), 3)
            ),
            "note": (
                f"DEPRECATED outcome-aware layer on restored data; "
                f"skip_death_before_45={skip_d45}; skip_T<=0={skip_t0}"
                if mode == "overlay_exclude_layer"
                else "no overlays/excludes; demotions respected"
                if mode == "raw_match"
                else "force use_in_primary on all chronos (contamination upper bound)"
            ),
        }

    rows = [
        run_labor("dirty_max"),
        run_labor("raw_match"),
        run_labor("overlay_exclude_layer"),
    ]

    # Corrected primary passthrough (script 25: symmetric rules, cluster boot).
    for r in csv.DictReader(PRIM_SUM.open()):
        if r.get("mode") != "primary" or r.get("subset") != "all_treatments":
            continue
        rows.append(
            {
                "estimand": "labor_work_after_45",
                "mode": "corrected_primary",
                "n_pairs": r.get("n_pairs_with_delta", ""),
                "median_delta": r.get("median_delta", ""),
                "boot95_lo": r.get("boot95_lo", ""),
                "boot95_hi": r.get("boot95_hi", ""),
                "sesoi5": r.get("sesoi5", ""),
                "sesoi15": r.get("sesoi15", ""),
                "n_ge_5": r.get("n_ge_5", ""),
                "share_delta_gt_0": r.get("share_delta_gt_0", ""),
                "note": "from b1_primary_estimand_summary.csv (script 25 corrected path)",
            }
        )

    # Output span passthrough (script 27 corrected path).
    for r in csv.DictReader(OUT_SUM.open()):
        if r.get("estimand") != "output_span_after_45":
            continue
        rows.append(
            {
                "estimand": "output_span_after_45",
                "mode": "corrected_output",
                "n_pairs": r.get("n_pairs_with_delta", ""),
                "median_delta": r.get("median_delta", ""),
                "boot95_lo": r.get("boot95_lo", ""),
                "boot95_hi": r.get("boot95_hi", ""),
                "sesoi5": r.get("sesoi5", ""),
                "sesoi15": r.get("sesoi15", ""),
                "n_ge_5": r.get("n_ge_5", ""),
                "share_delta_gt_0": r.get("share_delta_gt_0", ""),
                "note": "from b1_output_estimand_summary.csv (script 27 corrected path)",
            }
        )

    fields = list(rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    lab = {r["mode"]: r for r in rows if r["estimand"] == "labor_work_after_45"}
    out = next(r for r in rows if r["estimand"] == "output_span_after_45")

    def li(mode: str, label: str) -> str:
        r = lab[mode]
        return (
            f"| {label} | {r['n_pairs']} | {r['median_delta']} "
            f"| [{r['boot95_lo']}, {r['boot95_hi']}] | {r['share_delta_gt_0']} "
            f"| {r['sesoi5']} | {r['sesoi15']} |"
        )

    md = f"""# B1 cleaning sensitivity (audit-corrected, 2026-08-12)

**Script:** `29_b1_cleaning_sensitivity.py` → `b1_labor_cleaning_sensitivity.csv`  
**Date:** 2026-08-12

## Question

Did reverse-lifespan / overlay hygiene *manufacture* SESOI+5?

## Answer

**Yes.** On the pre-restore data (snapshot commit 9d95fa1) the layer moved the
labor median from 2.5 (CI crossing 0, FAIL) to 11.25 with share(Δ>0)=1.0.
A 100% one-sided pair distribution is the fingerprint of per-cell curation
iterated until each Δ flipped positive, not of measurement correction.
The layer is removed from the measurement path; data edits were reverted by
`33_b1_revert_outcome_aware_edits.py` (see `b1_audit_restore_log_2026-08-12.csv`
and `docs/B1_CURATION_AUDIT_2026-08-12.md`).

## Labor arms (recomputed on restored data)

| Mode | n | median Δ | boot 95% CI | share Δ>0 | SESOI+5 | SESOI+15 |
|------|--:|---------:|-------------|----------:|---------|----------|
{li('dirty_max', 'dirty_max')}
{li('raw_match', 'raw_match')}
{li('overlay_exclude_layer', 'overlay_exclude_layer (DEPRECATED)')}
{li('corrected_primary', 'corrected_primary (script 25)')}

## Output (corrected path, script 27)

| Mode | n | median Δ | CI | SESOI+5 | SESOI+15 |
|------|--:|---------:|----|---------|----------|
| corrected_output | {out['n_pairs']} | {out['median_delta']} | [{out['boot95_lo']}, {out['boot95_hi']}] | {out['sesoi5']} | {out['sesoi15']} |

## Reading

1. `corrected_primary` is the reportable number (symmetric death<45 rule,
   cluster bootstrap, no overlays/excludes).
2. `overlay_exclude_layer` shows what the deprecated hand layer still does on
   restored data; do not cite it as a result.
3. Known-wearer demotions (Locke/Priestley/Burke/Cusa) stay out of every arm
   except `dirty_max` (contamination upper bound).
4. **SESOI+15 FAIL in every arm** — nothing rescues Macfarlane +15.

## Claim language

- Do not claim SESOI+5 direction: corrected labor and output medians sit at
  0 to a few years with CIs crossing 0.
- Any future exclusion rule must be symmetric, outcome-blind, pre-registered.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    for r in rows:
        print(
            f"{r['estimand']:22s} {r['mode']:18s} n={r['n_pairs']} "
            f"med={r['median_delta']} CI=[{r['boot95_lo']},{r['boot95_hi']}] "
            f"{r['sesoi5']} / {r['sesoi15']}"
        )


if __name__ == "__main__":
    main()
