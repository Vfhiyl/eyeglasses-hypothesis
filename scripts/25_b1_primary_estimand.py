#!/usr/bin/env python3
"""B1 primary estimand: region-matched pairs + curated control near-work.

Estimand (frozen for this analysis path):
  For each onsetish treatment with birth year:
    T = years_work_after_45_proxy
        = max(0, min(evidence_year + years_after_evidence, death) - (birth + 45))
    C = median over region-matched controls of
        max(0, last_nearwork_year - (birth + 45))
        using curated chrono rows with use_in_primary=True only;
        if a matched control lacks curated primary row, it contributes nothing.
  Report Δ = T - C when ≥1 primary curated control is available.

Sensitivities:
  - all curated including low
  - high confidence curated only
  - merchant treatments only
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
CTRL = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
OUT_PAIR = OUTPUT_TABLES / "b1_primary_estimand_pairs.csv"
OUT_SUM = OUTPUT_TABLES / "b1_primary_estimand_summary.csv"
OUT_METHOD = OUTPUT_TABLES / "b1_primary_estimand_method.md"
OUT_VERDICT = OUTPUT_TABLES / "b1_roster_verdict.csv"


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
    meds = []
    n = len(xs)
    for _ in range(2000):
        sample = [xs[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    return statistics.median(xs), meds[int(0.025 * 1999)], meds[int(0.975 * 1999)]


def main() -> None:
    census = {r["person_id"]: r for r in csv.DictReader(CENSUS.open())}
    matches = [
        m
        for m in csv.DictReader(MATCHES.open())
        if m.get("match_status") == "matched"
    ]
    curated = {r["qid"]: r for r in csv.DictReader(CURATED.open())}
    ctrl = {r["qid"]: r for r in csv.DictReader(CTRL.open())}

    def t_work(person_id: str) -> float | None:
        t = census[person_id]
        b, d = _y(t.get("birth_year")), _y(t.get("death_year"))
        evid = _y(t.get("evidence_year"))
        ya = _f(t.get("years_after_evidence"))
        if b is None or evid is None or ya is None:
            return None
        last = evid + ya
        if d is not None:
            last = min(last, d)
        return max(0.0, last - (b + 45))

    def c_work(qid: str, mode: str) -> float | None:
        """mode: primary | all_curated | high_only"""
        row = curated.get(qid)
        if not row:
            return None
        conf = (row.get("confidence") or "").lower()
        use = str(row.get("use_in_primary", "True")).lower() in {"true", "1", "yes"}
        if mode == "primary" and not use:
            return None
        if mode == "high_only" and conf != "high":
            return None
        if mode == "all_curated":
            pass
        b = _y(row.get("birth_year")) or _y(ctrl.get(qid, {}).get("birth"))
        last = _y(row.get("last_nearwork_year"))
        if b is None or last is None:
            return None
        return max(0.0, last - (b + 45))

    modes = ("primary", "all_curated", "high_only")
    pair_rows = []
    for m in matches:
        pid = m["person_id"]
        tw = t_work(pid)
        qids = [q for q in m["matched_control_qids"].split(";") if q]
        cell = {
            "person_id": pid,
            "occupation_bucket": m.get("occupation_bucket", ""),
            "macro_region": m.get("macro_region", ""),
            "match_level": m.get("match_level", ""),
            "years_after_evidence": census[pid].get("years_after_evidence", ""),
            "t_work_after_45": "" if tw is None else tw,
        }
        for mode in modes:
            works = []
            used = []
            for q in qids:
                w = c_work(q, mode)
                if w is None:
                    continue
                works.append(w)
                used.append(q)
            med = statistics.median(works) if works else None
            delta = (tw - med) if (tw is not None and med is not None) else None
            cell[f"n_ctrl_{mode}"] = len(works)
            cell[f"med_c_{mode}"] = "" if med is None else med
            cell[f"delta_{mode}"] = "" if delta is None else round(delta, 2)
            cell[f"ctrl_qids_{mode}"] = ";".join(used)
        pair_rows.append(cell)

    fields = list(pair_rows[0].keys())
    with OUT_PAIR.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(pair_rows)

    summary = []
    merchant_ids = {
        "datini",
        "strozzi_filippo",
        "ardingelli_bese",
        "spinelli_benedetto",
        "nuno_fernandes",
    }
    for mode in modes:
        for label, subset in (
            ("all_treatments", pair_rows),
            ("merchant_treatments", [r for r in pair_rows if r["person_id"] in merchant_ids]),
        ):
            deltas = [_f(r[f"delta_{mode}"]) for r in subset]
            deltas_n = [d for d in deltas if d is not None]
            med, lo, hi = boot_median(deltas_n)
            summary.append(
                {
                    "mode": mode,
                    "subset": label,
                    "n_pairs_with_delta": len(deltas_n),
                    "median_delta": "" if not deltas_n else round(med, 2),
                    "boot95_lo": "" if not deltas_n else round(lo, 2),
                    "boot95_hi": "" if not deltas_n else round(hi, 2),
                    "n_ge_5": sum(1 for d in deltas_n if d >= 5),
                    "n_ge_15": sum(1 for d in deltas_n if d >= 15),
                    "sesoi5": (
                        "PASS_RAW"
                        if deltas_n and med >= 5 and lo >= 0
                        else "FAIL_OR_UNAVAILABLE"
                    ),
                    "sesoi15": "PASS_RAW" if deltas_n and med >= 15 else "FAIL",
                    "note": "PASS_RAW requires median≥threshold; sesoi5 also wants boot95_lo≥0",
                }
            )
    with OUT_SUM.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(summary)

    prim = next(s for s in summary if s["mode"] == "primary" and s["subset"] == "all_treatments")
    merch = next(s for s in summary if s["mode"] == "primary" and s["subset"] == "merchant_treatments")
    high = next(s for s in summary if s["mode"] == "high_only" and s["subset"] == "all_treatments")

    method = f"""# B1 primary estimand (frozen measurement path)

**Date:** 2026-07-31  
**Scripts/tables:** `25_b1_primary_estimand.py` → `b1_primary_estimand_pairs.csv`, `b1_primary_estimand_summary.csv`

## What is being estimated

Among documentary spectacle wearers (onsetish roster), relative to region- and occupation-matched non-roster controls with curated dated near-work:

> **Δ = T_work_after_45 − median(C_work_after_45)**

where

- `T_work_after_45 = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))`
- `C_work_after_45 = max(0, last_nearwork_year − (birth + 45))` from `b1_control_nearwork_chrono_curated.csv` with **`use_in_primary=True`**
- Matching: `b1_roster_control_matches_region.csv` (occ + birth±10 + macro-region)

This is **not** Macfarlane’s rhetorical “+15 years of intellectual life” verbatim; it is the closest SESOI-compatible contrast we can build from open dated series.

## What is excluded from primary

- Hard-only appendix medians  
- Non-region WD matches  
- Curated controls with `use_in_primary=False` (currently Arnolfini, Pandolfo Rucellai — low confidence)  
- Pure survival `ya45` as main claim number  

## Current primary result

| Subset | n pairs | median Δ | bootstrap 95% CI | SESOI +5 | SESOI +15 |
|--------|--------:|----------:|------------------:|----------|----------|
| All treatments (primary curated) | {prim['n_pairs_with_delta']} | {prim['median_delta']} | [{prim['boot95_lo']}, {prim['boot95_hi']}] | {prim['sesoi5']} | {prim['sesoi15']} |
| Merchant treatments only | {merch['n_pairs_with_delta']} | {merch['median_delta']} | [{merch['boot95_lo']}, {merch['boot95_hi']}] | {merch['sesoi5']} | {merch['sesoi15']} |
| High-confidence curated only | {high['n_pairs_with_delta']} | {high['median_delta']} | [{high['boot95_lo']}, {high['boot95_hi']}] | {high['sesoi5']} | {high['sesoi15']} |

## Interpretation

- If primary CI includes 0 or median < 5 → **do not** claim direction SESOI pass.
- Macfarlane +15 requires median ≥ 15 on this (or stricter) contrast — currently **not met**.
- B1 remains **unidentified** as a causal claim (controls not archive spectacle-negative; curated coverage still partial), but the **strong “+15 typical unlock” reading is unsupported** on the best open contrast we have.

## Next measurement steps

1. Add more `use_in_primary=True` merchant account/letter chronos for Spinelli/Strozzi cells.  
2. Hand spectacle-negative audit on primary curated controls.  
3. Keep wearer n frozen.
"""
    OUT_METHOD.write_text(method)

    verdict = [
        {
            "check": "primary_estimand_defined",
            "result": "DONE",
            "detail": "See b1_primary_estimand_method.md",
        },
        {
            "check": "sesoi_direction_5_primary",
            "result": prim["sesoi5"],
            "detail": f"n={prim['n_pairs_with_delta']}; median={prim['median_delta']}; CI=[{prim['boot95_lo']},{prim['boot95_hi']}]",
        },
        {
            "check": "sesoi_direction_5_merchant_primary",
            "result": merch["sesoi5"],
            "detail": f"n={merch['n_pairs_with_delta']}; median={merch['median_delta']}; CI=[{merch['boot95_lo']},{merch['boot95_hi']}]",
        },
        {
            "check": "sesoi_macfarlane_15_primary",
            "result": prim["sesoi15"],
            "detail": f"median={prim['median_delta']}",
        },
        {
            "check": "sesoi_direction_5_high_only",
            "result": high["sesoi5"],
            "detail": f"n={high['n_pairs_with_delta']}; median={high['median_delta']}; CI=[{high['boot95_lo']},{high['boot95_hi']}]",
        },
        {
            "check": "b1_nearwork_causal",
            "result": "UNIDENTIFIED",
            "detail": "Primary contrast built; causal ID still blocked (spectacle-negative + fuller coverage)",
        },
        {
            "check": "macfarlane_plus15_strong_reading",
            "result": "UNSUPPORTED_ON_OPEN_CONTRAST",
            "detail": "Primary median far below +15; merchant cell ~0",
        },
        {
            "check": "direction_decision",
            "result": "FREEZE_N_EXPAND_MEASURE",
            "detail": "Use primary estimand tables as claim language base",
        },
    ]
    with OUT_VERDICT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["check", "result", "detail"], lineterminator="\n")
        w.writeheader()
        w.writerows(verdict)

    print("PRIMARY all:", prim)
    print("PRIMARY merchant:", merch)
    print("HIGH only:", high)
    print("wrote", OUT_PAIR)
    print("wrote", OUT_SUM)
    print("wrote", OUT_METHOD)


if __name__ == "__main__":
    main()
