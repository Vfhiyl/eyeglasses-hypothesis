#!/usr/bin/env python3
"""B1 symmetry sensitivities on the corrected labor estimand (2026-08-12).

Closes the residual measurement questions left by the audit
(docs/B1_CURATION_AUDIT_2026-08-12.md §5): wearer endpoint quality and
symmetric data-quality gates. All arms use the corrected rules from
scripts/25 (no overlay/exclude layer, symmetric death<45 drop, T=0 kept,
cluster bootstrap over shared-control components); only the stated gate
differs per arm. Gates are SYMMETRIC (same rule both arms) and
outcome-blind (defined on provenance/density/era, never on delta).

Arms:
  corrected_baseline      — replicates script 25 primary/all_treatments
  hard_series_wearers     — wearers with hard_dated_series=True only
  density_floor_3_sym     — wearer n_dated_activity>=3 AND control n_dated_pins>=3
  drop_todeath_sym        — drop BOTH wearers whose endpoint reaches death
                            (evidence+ya >= death) AND controls whose
                            last_nearwork_year >= death_year
  pre1600_evidence        — evidence_year <= 1600 (medieval/renaissance:
                            the domain of the Macfarlane claim)
  post1600_evidence       — evidence_year > 1600
  pre1600_hard_density    — pre1600 AND hard series AND density floor (both arms)

Outputs:
  outputs/tables/b1_symmetry_sensitivity.csv
  outputs/tables/b1_symmetry_sensitivity_method.md
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
OUT_CSV = OUTPUT_TABLES / "b1_symmetry_sensitivity.csv"
OUT_MD = OUTPUT_TABLES / "b1_symmetry_sensitivity_method.md"


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
    return statistics.median(deltas), meds[int(0.025 * 1999)], meds[int(0.975 * 1999)], k


def main() -> None:
    census = {r["person_id"]: r for r in csv.DictReader(CENSUS.open())}
    matches = {
        m["person_id"]: dict(m)
        for m in csv.DictReader(MATCHES.open())
        if m.get("match_status") == "matched"
    }
    curated = {r["qid"]: r for r in csv.DictReader(CURATED.open())}
    ctrl = {r["qid"]: r for r in csv.DictReader(CTRL.open())}

    def t_last(pid: str) -> float | None:
        t = census[pid]
        b, d = _y(t.get("birth_year")), _y(t.get("death_year"))
        evid, ya = _y(t.get("evidence_year")), _f(t.get("years_after_evidence"))
        if b is None or evid is None or ya is None:
            return None
        last = evid + ya
        if d is not None:
            last = min(last, d)
        return last

    def t_work(pid: str) -> float | None:
        t = census[pid]
        b = _y(t.get("birth_year"))
        last = t_last(pid)
        if b is None or last is None:
            return None
        return max(0.0, last - (b + 45))

    def wearer_todeath(pid: str) -> bool:
        t = census[pid]
        d = _y(t.get("death_year"))
        evid, ya = _y(t.get("evidence_year")), _f(t.get("years_after_evidence"))
        return d is not None and evid is not None and ya is not None and evid + ya >= d

    def ctrl_todeath(qid: str) -> bool:
        row = curated.get(qid) or {}
        d = _y(row.get("death_year"))
        last = _y(row.get("last_nearwork_year"))
        return d is not None and last is not None and last >= d

    def death_before_45(pid: str) -> bool:
        t = census[pid]
        b, d = _y(t.get("birth_year")), _y(t.get("death_year"))
        return b is not None and d is not None and d < b + 45

    def c_work(qid: str, ctrl_gate) -> float | None:
        row = curated.get(qid)
        if not row:
            return None
        if str(row.get("use_in_primary", "True")).lower() not in {"true", "1", "yes"}:
            return None
        if ctrl_gate is not None and not ctrl_gate(qid, row):
            return None
        b = _y(row.get("birth_year")) or _y(ctrl.get(qid, {}).get("birth"))
        d = _y(row.get("death_year")) or _y(ctrl.get(qid, {}).get("death"))
        last = _y(row.get("last_nearwork_year"))
        if b is None or last is None:
            return None
        if d is not None and d < b + 45:
            return None
        return max(0.0, last - (b + 45))

    def run_arm(name: str, wearer_gate=None, ctrl_gate=None) -> dict:
        items: list[tuple[float, frozenset[str]]] = []
        for m in matches.values():
            pid = m["person_id"]
            if pid not in census:
                continue
            if death_before_45(pid):
                continue
            if wearer_gate is not None and not wearer_gate(pid):
                continue
            tw = t_work(pid)
            if tw is None:
                continue
            qids = [q for q in (m.get("matched_control_qids") or "").split(";") if q]
            works, used = [], []
            for q in qids:
                w = c_work(q, ctrl_gate)
                if w is None:
                    continue
                works.append(w)
                used.append(q)
            if not works:
                continue
            items.append((tw - statistics.median(works), frozenset(used)))
        med, lo, hi, k = boot_median_clustered(items)
        deltas = [d for d, _ in items]
        return {
            "arm": name,
            "n_pairs": len(deltas),
            "n_clusters": k,
            "median_delta": "" if not deltas else round(med, 2),
            "boot95_lo": "" if not deltas else round(lo, 2),
            "boot95_hi": "" if not deltas else round(hi, 2),
            "n_ge_5": sum(1 for d in deltas if d >= 5),
            "share_delta_gt_0": (
                "" if not deltas else round(sum(1 for d in deltas if d > 0) / len(deltas), 3)
            ),
            "sesoi5": (
                "PASS_RAW" if deltas and med >= 5 and lo >= 0 else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi15": "PASS_RAW" if deltas and med >= 15 else "FAIL",
        }

    def is_hard(pid: str) -> bool:
        return (census[pid].get("hard_dated_series") or "").strip().lower() == "true"

    def w_density(pid: str) -> bool:
        return (_y(census[pid].get("n_dated_activity")) or 0) >= 3

    def c_density(qid: str, row: dict) -> bool:
        return (_y(row.get("n_dated_pins")) or 0) >= 3

    def pre1600(pid: str) -> bool:
        ev = _y(census[pid].get("evidence_year"))
        return ev is not None and ev <= 1600

    def pre1500(pid: str) -> bool:
        ev = _y(census[pid].get("evidence_year"))
        return ev is not None and ev <= 1500

    arms = [
        run_arm("corrected_baseline"),
        run_arm("hard_series_wearers", wearer_gate=is_hard),
        run_arm(
            "density_floor_3_sym",
            wearer_gate=w_density,
            ctrl_gate=lambda q, r: c_density(q, r),
        ),
        run_arm(
            "drop_todeath_sym",
            wearer_gate=lambda p: not wearer_todeath(p),
            ctrl_gate=lambda q, r: not ctrl_todeath(q),
        ),
        run_arm("pre1500_evidence_invention_era", wearer_gate=pre1500),
        run_arm("pre1600_evidence", wearer_gate=pre1600),
        run_arm("post1600_evidence", wearer_gate=lambda p: not pre1600(p)),
        run_arm(
            "pre1600_hard_density",
            wearer_gate=lambda p: pre1600(p) and is_hard(p) and w_density(p),
            ctrl_gate=lambda q, r: c_density(q, r),
        ),
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(arms[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(arms)

    def li(a: dict) -> str:
        return (
            f"| {a['arm']} | {a['n_pairs']} ({a['n_clusters']}) | {a['median_delta']} "
            f"| [{a['boot95_lo']}, {a['boot95_hi']}] | {a['share_delta_gt_0']} "
            f"| {a['sesoi5']} | {a['sesoi15']} |"
        )

    md = "\n".join(
        [
            "# B1 symmetry sensitivities (corrected estimand)",
            "",
            "**Date:** 2026-08-12  ",
            "**Script:** `34_b1_symmetry_sensitivities.py` → `b1_symmetry_sensitivity.csv`",
            "",
            "All gates are symmetric (same rule both arms) and outcome-blind",
            "(provenance / pin density / era; never the delta). Base rules =",
            "corrected script 25 path.",
            "",
            "| Arm | n (clusters) | median Δ | boot 95% CI | share Δ>0 | SESOI+5 | +15 |",
            "|-----|-------------:|---------:|-------------|----------:|---------|-----|",
            *[li(a) for a in arms],
            "",
            "## Reading",
            "",
            "1. `drop_todeath_sym` answers the wearer-endpoint audit question: when",
            "   every to-death endpoint is dropped on BOTH sides, does the",
            "   direction survive?",
            "2. `pre1600_evidence` is the domain of the Macfarlane claim; the",
            "   post-1600 arm (Franklin/Jefferson era) is out-of-domain and was",
            "   added to the roster after the 2026-07-31 freeze.",
            "   `pre1500_evidence_invention_era` is the first two centuries after",
            "   invention (~1286): the tightest claim domain, and also the window",
            "   where the wear-vs-no-record contrast is least saturated (bulk",
            "   cheap exports from mid-15th c. contaminate later control pools).",
            "   Era strata must never be pooled into one headline median: era",
            "   correlates with adoption saturation AND archive density, so the",
            "   pooled number mixes different estimands.",
            "3. `pre1600_hard_density` is the strictest defensible subset:",
            "   in-domain, hard-dated, density-floored both sides.",
            "4. No arm may be quoted alone as a verdict; this table exists to show",
            "   the corrected result is (or is not) an artifact of endpoint",
            "   conventions, archive density, or era mixing.",
            "",
        ]
    )
    OUT_MD.write_text(md, encoding="utf-8")
    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    for a in arms:
        print(
            f"{a['arm']:22s} n={a['n_pairs']:3d} ({a['n_clusters']:2d} cl) "
            f"med={a['median_delta']} CI=[{a['boot95_lo']},{a['boot95_hi']}] "
            f"share>0={a['share_delta_gt_0']} {a['sesoi5']}/{a['sesoi15']}"
        )


if __name__ == "__main__":
    main()
