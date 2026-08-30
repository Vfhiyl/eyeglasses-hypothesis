#!/usr/bin/env python3
"""B1 primary estimand: region-matched pairs + curated control near-work.

CORRECTED PATH (audit 2026-08-12). The 2026-08-06..08-10 passes applied an
outcome-aware hand layer (per-wearer control excludes citing the control's
long span, lifespan-matched short overlays, one-directional tip-strips)
which manufactured SESOI+5 PASS_RAW (median delta jumped 2.5 -> 11.5 with
share(delta>0)=1.0). This script no longer applies that layer:

  * b1_output_strict_control_overlays.csv / b1_output_control_excludes.csv
    are NOT read (kept on disk as historical record only).
  * Curated chronologies were restored by 33_b1_revert_outcome_aware_edits.py
    (tip-strips reverted, outcome-aware demotions re-enabled).

Estimand (unchanged formula):
  For each onsetish treatment with birth year:
    T = years_work_after_45_proxy
        = max(0, min(evidence_year + years_after_evidence, death) - (birth + 45))
    C = median over region-matched controls of
        max(0, last_nearwork_year - (birth + 45))
        using curated chrono rows with use_in_primary=True only.
  Report delta = T - C when >=1 primary curated control is available.

Symmetric eligibility (replaces the pass-era asymmetric skips):
  * BOTH arms drop persons with known death < birth + 45 (no post-45 window).
  * T = 0 treatments are KEPT (they were skipped in the pass-era path while
    C = 0 controls were kept; zeros now count on both sides).

Uncertainty: cluster bootstrap. Pairs sharing any control are resampled as
one cluster (the previous pair-i.i.d. bootstrap understated variance when a
handful of controls served many wearers).

Subsets:
  * all_treatments        — full current roster (includes post-freeze expansion)
  * frozen_roster_2026_07_31 — wearers already in the 2026-07-31 frozen pairs
    (the roster expansion happened after the freeze declaration)
  * merchant_treatments   — merchant wearers
Sensitivity modes: primary / all_curated / high_only (as before).
"""
from __future__ import annotations

import csv
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, OUTPUT_TABLES
from importlib import import_module

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
MATCHES = OUTPUT_TABLES / "b1_roster_control_matches_region.csv"
CURATED = DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"
CTRL = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
OUT_PAIR = OUTPUT_TABLES / "b1_primary_estimand_pairs.csv"
OUT_SUM = OUTPUT_TABLES / "b1_primary_estimand_summary.csv"
OUT_METHOD = OUTPUT_TABLES / "b1_primary_estimand_method.md"
OUT_VERDICT = OUTPUT_TABLES / "b1_roster_verdict.csv"

# person_ids present in the 2026-07-31 frozen pairs table (HEAD@0094d57);
# the wearer-n freeze declared there was violated by the expansion passes,
# so the frozen subset is reported separately.
FROZEN_ROSTER_2026_07_31 = {
    "neri_mici", "petrarch", "philippe_le_hardi", "datini", "nicolas_de_baye",
    "ardingelli_bese", "arduino_baiso", "cederni", "charles_orleans", "filelfo",
    "gonzaga_ludovico", "policastro", "pius_ii", "bianca_maria",
    "sforza_francesco", "tranchedini", "strozzi_filippo", "alessandra_strozzi",
    "barbara_brandenburg", "ammannati", "azevedo_joao_porto", "lorenzo_medici",
    "sixtus_iv", "egidio_piacenza", "jacopo_magnia_friar", "rene_ii_lorraine",
    "leo_x", "pirckheimer", "wolsey", "wyatt_henry", "spataro_giovanni",
    "spinelli_benedetto", "lotto", "henry_viii", "maurolico_francesco",
    "domenichi_ludovico",
}

MERCHANT_IDS = {
    "datini",
    "strozzi_filippo",
    "ardingelli_bese",
    "spinelli_benedetto",
    "nuno_fernandes",
}


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


def cluster_pairs(items: list[tuple[float, frozenset[str]]]) -> list[list[float]]:
    """Union-find clustering: pairs sharing any control qid form one cluster."""
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    owner: dict[str, int] = {}
    for i, (_, qids) in enumerate(items):
        for q in qids:
            if q in owner:
                union(owner[q], i)
            else:
                owner[q] = i
    groups: dict[int, list[float]] = {}
    for i, (delta, _) in enumerate(items):
        groups.setdefault(find(i), []).append(delta)
    return list(groups.values())


def boot_median_clustered(
    items: list[tuple[float, frozenset[str]]], seed: int = 31
) -> tuple[float, float, float, int]:
    """Median + cluster-bootstrap 95% CI. Returns (median, lo, hi, n_clusters)."""
    if not items:
        return float("nan"), float("nan"), float("nan"), 0
    deltas = [d for d, _ in items]
    clusters = cluster_pairs(items)
    rng = random.Random(seed)
    meds: list[float] = []
    k = len(clusters)
    for _ in range(2000):
        sample: list[float] = []
        for _ in range(k):
            sample.extend(clusters[rng.randrange(k)])
        meds.append(statistics.median(sample))
    meds.sort()
    return (
        statistics.median(deltas),
        meds[int(0.025 * 1999)],
        meds[int(0.975 * 1999)],
        k,
    )


def main() -> None:
    census = {r["person_id"]: r for r in csv.DictReader(CENSUS.open())}
    matches = {
        m["person_id"]: dict(m)
        for m in csv.DictReader(MATCHES.open())
        if m.get("match_status") == "matched"
    }
    print("outcome-aware overlay/exclude layer: DISABLED (audit 2026-08-12)")
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
        b = _y(row.get("birth_year")) or _y(ctrl.get(qid, {}).get("birth"))
        d = _y(row.get("death_year")) or _y(ctrl.get(qid, {}).get("death"))
        last = _y(row.get("last_nearwork_year"))
        if b is None or last is None:
            return None
        # Symmetric with the treatment-side death_before_45 skip.
        if d is not None and d < b + 45:
            return None
        return max(0.0, last - (b + 45))

    def death_before_45(person_id: str) -> bool:
        t = census[person_id]
        b, d = _y(t.get("birth_year")), _y(t.get("death_year"))
        return b is not None and d is not None and d < b + 45

    modes = ("primary", "all_curated", "high_only")
    pair_rows = []
    skipped_d45 = 0
    n_t_zero = 0
    for m in matches.values():
        pid = m["person_id"]
        if pid not in census:
            continue
        if death_before_45(pid):
            skipped_d45 += 1
            continue
        tw = t_work(pid)
        if tw is not None and tw <= 0:
            n_t_zero += 1  # kept (pass-era path skipped these; C=0 stays too)
        qids = [q for q in (m.get("matched_control_qids") or "").split(";") if q]
        cell = {
            "person_id": pid,
            "occupation_bucket": m.get("occupation_bucket", "")
            or census[pid].get("occupation_bucket", ""),
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
    print(f"skipped death_before_45={skipped_d45}; T_work=0 kept={n_t_zero}")

    fields = list(pair_rows[0].keys())
    with OUT_PAIR.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(pair_rows)

    summary = []
    for mode in modes:
        for label, subset in (
            ("all_treatments", pair_rows),
            (
                "frozen_roster_2026_07_31",
                [r for r in pair_rows if r["person_id"] in FROZEN_ROSTER_2026_07_31],
            ),
            ("merchant_treatments", [r for r in pair_rows if r["person_id"] in MERCHANT_IDS]),
        ):
            items: list[tuple[float, frozenset[str]]] = []
            for r in subset:
                d = _f(r[f"delta_{mode}"])
                if d is None:
                    continue
                items.append((d, frozenset((r[f"ctrl_qids_{mode}"] or "").split(";"))))
            med, lo, hi, k = boot_median_clustered(items)
            deltas_n = [d for d, _ in items]
            summary.append(
                {
                    "mode": mode,
                    "subset": label,
                    "n_pairs_with_delta": len(deltas_n),
                    "n_clusters": k,
                    "median_delta": "" if not deltas_n else round(med, 2),
                    "boot95_lo": "" if not deltas_n else round(lo, 2),
                    "boot95_hi": "" if not deltas_n else round(hi, 2),
                    "n_ge_5": sum(1 for d in deltas_n if d >= 5),
                    "n_ge_15": sum(1 for d in deltas_n if d >= 15),
                    "share_delta_gt_0": (
                        ""
                        if not deltas_n
                        else round(sum(1 for d in deltas_n if d > 0) / len(deltas_n), 3)
                    ),
                    "sesoi5": (
                        "PASS_RAW"
                        if deltas_n and med >= 5 and lo >= 0
                        else "FAIL_OR_UNAVAILABLE"
                    ),
                    "sesoi15": "PASS_RAW" if deltas_n and med >= 15 else "FAIL",
                    "note": (
                        "cluster bootstrap over shared-control components; "
                        "PASS_RAW requires median>=threshold and boot95_lo>=0 (sesoi5)"
                    ),
                }
            )
    with OUT_SUM.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(summary)

    def pick(mode: str, subset: str) -> dict:
        return next(s for s in summary if s["mode"] == mode and s["subset"] == subset)

    prim = pick("primary", "all_treatments")
    froz = pick("primary", "frozen_roster_2026_07_31")
    merch = pick("primary", "merchant_treatments")
    high = pick("high_only", "all_treatments")

    audit30 = import_module("30_b1_wearer_control_collision_audit")
    collision_active, collision_alias = audit30.run_audit()
    audit30.write_outputs(collision_active, collision_alias)
    n_collision = len(collision_active)
    n_alias = len(collision_alias)

    def row_md(s: dict, label: str) -> str:
        return (
            f"| {label} | {s['n_pairs_with_delta']} ({s['n_clusters']} cl) "
            f"| {s['median_delta']} | [{s['boot95_lo']}, {s['boot95_hi']}] "
            f"| {s['share_delta_gt_0']} | {s['sesoi5']} | {s['sesoi15']} |"
        )

    method = f"""# B1 primary estimand (corrected path, audit 2026-08-12)

**Date:** 2026-08-12 (outcome-aware curation layer removed)  
**Scripts/tables:** `25_b1_primary_estimand.py` → `b1_primary_estimand_pairs.csv`, `b1_primary_estimand_summary.csv`  
**Restore log:** `b1_audit_restore_log_2026-08-12.csv` (via `33_b1_revert_outcome_aware_edits.py`)

## What is being estimated

Among documentary spectacle wearers (onsetish roster), relative to region- and
occupation-matched non-roster controls with curated dated near-work:

> **Δ = T_work_after_45 − median(C_work_after_45)**

- `T_work_after_45 = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))`
- `C_work_after_45 = max(0, last_nearwork_year − (birth + 45))` from
  `b1_control_nearwork_chrono_curated.csv` with `use_in_primary=True`
- Matching: `b1_roster_control_matches_region.csv` (occ + birth±10 + macro-region)

## Corrections applied 2026-08-12 (vs. the pass BC–FI path)

1. **Overlay/exclude layer disabled.** The per-wearer excludes cited the
   control's own span ("reverse lifespan", "post-death densify", "tip=death",
   "pulls Cmed"); the overlays added lifespan-matched short-span controls.
   One-directional and outcome-aware → removed from the measurement path.
2. **Tip-strips reverted** (38 labor rows, 14 output pins): control endpoints
   had been shortened while wearer `*_to_death` endpoints were kept.
3. **Outcome-aware demotions reverted** (9 rows incl. Adam Smith, Borso
   d'Este, Oldenburg). Contamination demotions (documented wearers: Locke,
   Priestley, Burke, Cusa) and pre-pass data-quality demotions stay.
4. **Symmetric eligibility.** Both arms drop death < birth+45; T=0 wearers
   are kept (previously skipped while C=0 controls were kept).
5. **Cluster bootstrap.** Pairs sharing controls resample as one cluster
   (i.i.d. pair bootstrap understated variance; a few controls serve many
   wearers, e.g. the 18th-c England cell).

## Current result (corrected)

| Subset | n pairs (clusters) | median Δ | boot 95% CI | share Δ>0 | SESOI +5 | SESOI +15 |
|--------|-------------------:|---------:|------------:|----------:|----------|-----------|
{row_md(prim, 'All treatments (primary curated)')}
{row_md(froz, 'Frozen roster 2026-07-31 only')}
{row_md(merch, 'Merchant treatments only')}
{row_md(high, 'High-confidence curated only')}

## Interpretation guardrails

- The expanded roster (36 → current) was assembled **after** the 2026-07-31
  wearer-n freeze and includes famous long-lived wearers (Franklin,
  Jefferson, Washington); treat `all_treatments` as exploratory and read
  `frozen_roster_2026_07_31` alongside it.
- Controls are "no spectacle record found", **not** documented non-wearers;
  by the 15th c. spectacles were cheap and widespread. Causal ID remains
  blocked; Δ largely reflects differential documentation density.
- Macfarlane +15 requires median ≥ 15 on this contrast — see summary.
- Historical comparison: 2026-07-31 frozen path Δ=−0.75 [−3.0, 3.3] (n=36);
  pass-era raw_match Δ=2.5 [−0.5, 9.5] (n=62); pass-era outcome-aware
  "full_clean" Δ=11.25 with share(Δ>0)=1.0 — **retracted** (manufactured;
  see `b1_labor_cleaning_sensitivity.csv` and
  `docs/B1_CURATION_AUDIT_2026-08-12.md`).
- **Wearer–control collision (required clear):**
  `30_b1_wearer_control_collision_audit.py` — active collisions must be 0.

## Next measurement steps

1. Symmetric endpoint re-adjudication: decide death-tip validity by one rule
   for BOTH arms (wearer `*_to_death` endpoints vs control death-tips).
2. Documentation-density floor for controls (≥k dated pins) applied
   symmetrically, pre-registered before any further expansion.
3. Wearer-side endpoint audit (years_after_evidence provenance).
"""
    OUT_METHOD.write_text(method)

    verdict = [
        {
            "check": "primary_estimand_defined",
            "result": "DONE",
            "detail": "Corrected path 2026-08-12; see b1_primary_estimand_method.md",
        },
        {
            "check": "outcome_aware_layer_removed",
            "result": "DONE",
            "detail": (
                "overlays/excludes disabled; 38+14 tip-strips reverted; 9 demotions "
                "reverted; see b1_audit_restore_log_2026-08-12.csv"
            ),
        },
        {
            "check": "sesoi_direction_5_primary",
            "result": prim["sesoi5"],
            "detail": (
                f"n={prim['n_pairs_with_delta']} (clusters={prim['n_clusters']}); "
                f"median={prim['median_delta']}; CI=[{prim['boot95_lo']},{prim['boot95_hi']}]"
            ),
        },
        {
            "check": "sesoi_direction_5_frozen_roster",
            "result": froz["sesoi5"],
            "detail": (
                f"n={froz['n_pairs_with_delta']} (clusters={froz['n_clusters']}); "
                f"median={froz['median_delta']}; CI=[{froz['boot95_lo']},{froz['boot95_hi']}]"
            ),
        },
        {
            "check": "sesoi_direction_5_merchant_primary",
            "result": merch["sesoi5"],
            "detail": (
                f"n={merch['n_pairs_with_delta']}; median={merch['median_delta']}; "
                f"CI=[{merch['boot95_lo']},{merch['boot95_hi']}]"
            ),
        },
        {
            "check": "sesoi_macfarlane_15_primary",
            "result": prim["sesoi15"],
            "detail": f"median={prim['median_delta']}",
        },
        {
            "check": "sesoi_direction_5_high_only",
            "result": high["sesoi5"],
            "detail": (
                f"n={high['n_pairs_with_delta']}; median={high['median_delta']}; "
                f"CI=[{high['boot95_lo']},{high['boot95_hi']}]"
            ),
        },
        {
            "check": "b1_nearwork_causal",
            "result": "UNIDENTIFIED",
            "detail": (
                "Controls are 'no spectacle record found', not documented non-wearers; "
                "delta largely reflects documentation density"
            ),
        },
        {
            "check": "pass_era_sesoi5_pass_raw",
            "result": "RETRACTED",
            "detail": (
                "2026-08-06..08-10 labor/output SESOI+5 PASS_RAW was manufactured by "
                "outcome-aware curation (raw 2.5 FAIL vs clean 11.25 PASS, share>0=1.0); "
                "see docs/B1_CURATION_AUDIT_2026-08-12.md"
            ),
        },
        {
            "check": "wearer_n_freeze_2026_07_31",
            "result": "VIOLATED_BY_PASSES",
            "detail": (
                "Roster expanded 36->61 after freeze declaration; frozen subset "
                "reported separately in summary"
            ),
        },
        {
            "check": "wearer_control_collision_clear",
            "result": "DONE" if n_collision == 0 else "FAIL",
            "detail": (
                f"scripts/30_b1_wearer_control_collision_audit.py → "
                f"active={n_collision}; inactive_aliases={n_alias}; must stay 0 active"
            ),
        },
    ]
    with OUT_VERDICT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["check", "result", "detail"], lineterminator="\n")
        w.writeheader()
        w.writerows(verdict)

    print("PRIMARY all:", prim)
    print("PRIMARY frozen36:", froz)
    print("PRIMARY merchant:", merch)
    print("HIGH only:", high)
    print("wrote", OUT_PAIR)
    print("wrote", OUT_SUM)
    print("wrote", OUT_METHOD)


if __name__ == "__main__":
    main()
