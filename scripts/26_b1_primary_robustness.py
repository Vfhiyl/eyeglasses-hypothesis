#!/usr/bin/env python3
"""B1 primary robustness + pooled-merchant sensitivity.

Does not change the frozen primary estimand in script 25.
Adds:
  - drop treatments with T_work_after_45 == 0
  - drop artisan treatments
  - merchant pooled: C = median of all use_in_primary curated
    controls tagged merchant_* activity (or strata merchant) in italy
    rather than only matched QIDs (OA-thin Spinelli matches)
"""
from __future__ import annotations

import csv
import random
import statistics
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, OUTPUT_TABLES

PAIRS = OUTPUT_TABLES / "b1_primary_estimand_pairs.csv"
CURATED = DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"
CTRL = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
MATCHES = OUTPUT_TABLES / "b1_roster_control_matches_region.csv"
OUT = OUTPUT_TABLES / "b1_primary_robustness_summary.csv"
OUT_MD = OUTPUT_TABLES / "b1_primary_robustness_2026-07-31.md"


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


def boot_median(xs: list[float], seed: int = 41) -> tuple[float, float, float]:
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


def sesoi(med: float, lo: float) -> tuple[str, str]:
    s5 = "PASS_RAW" if med >= 5 else "FAIL_OR_UNAVAILABLE"
    if med >= 5 and lo >= 0:
        s5 = "PASS_WITH_CI"
    s15 = "PASS_RAW" if med >= 15 else "FAIL"
    return s5, s15


def summarize(label: str, deltas: list[float]) -> dict[str, object]:
    med, lo, hi = boot_median(deltas)
    s5, s15 = sesoi(med, lo) if deltas else ("NA", "NA")
    return {
        "spec": label,
        "n_pairs": len(deltas),
        "median_delta": "" if not deltas else f"{med:.4g}",
        "boot95_lo": "" if not deltas else f"{lo:.4g}",
        "boot95_hi": "" if not deltas else f"{hi:.4g}",
        "n_ge_5": sum(1 for d in deltas if d >= 5),
        "n_ge_15": sum(1 for d in deltas if d >= 15),
        "sesoi5": s5,
        "sesoi15": s15,
    }


def main() -> None:
    pairs = list(csv.DictReader(PAIRS.open()))
    curated = list(csv.DictReader(CURATED.open()))
    ctrl = {r["qid"]: r for r in csv.DictReader(CTRL.open())}
    matches = {r["person_id"]: r for r in csv.DictReader(MATCHES.open())}

    primary = []
    for r in pairs:
        d = _f(r.get("delta_primary"))
        if d is None:
            continue
        primary.append(r | {"delta": d, "t": _f(r.get("t_work_after_45"))})

    rows = []
    rows.append(summarize("primary_all", [r["delta"] for r in primary]))
    rows.append(
        summarize(
            "drop_T_eq_0",
            [r["delta"] for r in primary if (r["t"] or 0) > 0],
        )
    )
    rows.append(
        summarize(
            "drop_artisan",
            [r["delta"] for r in primary if r.get("occupation_bucket") != "artisan"],
        )
    )
    rows.append(
        summarize(
            "drop_T0_and_artisan",
            [
                r["delta"]
                for r in primary
                if (r["t"] or 0) > 0 and r.get("occupation_bucket") != "artisan"
            ],
        )
    )
    rows.append(
        summarize(
            "merchant_matched_primary",
            [r["delta"] for r in primary if r.get("occupation_bucket") == "merchant"],
        )
    )

    # pooled merchant curated in italy
    def c_work(row: dict[str, str]) -> float | None:
        use = str(row.get("use_in_primary", "")).lower() in {"true", "1", "yes"}
        if not use:
            return None
        proxy = (row.get("activity_proxy") or "").lower()
        src = (ctrl.get(row["qid"], {}).get("source") or "").lower()
        merchantish = (
            "merchant" in proxy
            or "bank" in proxy
            or "account" in proxy
            or "patrician" in proxy
            or src == "sparql_merchant"
        )
        if not merchantish:
            return None
        b = _y(row.get("birth_year"))
        last = _y(row.get("last_nearwork_year"))
        if b is None or last is None:
            return None
        return max(0.0, last - (b + 45))

    pooled_cs = []
    for row in curated:
        cw = c_work(row)
        if cw is not None:
            pooled_cs.append(cw)
    pooled_med = statistics.median(pooled_cs) if pooled_cs else None

    merchant_pooled_deltas = []
    for r in pairs:
        if r.get("occupation_bucket") != "merchant":
            continue
        tw = _f(r.get("t_work_after_45"))
        if tw is None or pooled_med is None:
            continue
        # restrict to italy treatments
        m = matches.get(r["person_id"], {})
        if m.get("macro_region") != "italy":
            continue
        merchant_pooled_deltas.append(tw - pooled_med)

    rows.append(
        summarize("merchant_pooled_italy_curated", merchant_pooled_deltas)
        | {
            "note": f"pooled_C_median={pooled_med}; n_curated_merchantish={len(pooled_cs)}"
        }
    )

    # still-missing after this wave
    miss = [r["person_id"] for r in pairs if not r.get("delta_primary")]

    with OUT.open("w", newline="") as f:
        fields = [
            "spec",
            "n_pairs",
            "median_delta",
            "boot95_lo",
            "boot95_hi",
            "n_ge_5",
            "n_ge_15",
            "sesoi5",
            "sesoi15",
            "note",
        ]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)

    lines = [
        "# B1 primary robustness (2026-07-31)",
        "",
        "Frozen primary remains script `25`. This note is sensitivity only.",
        "",
        "## Specs",
        "",
        "| Spec | n | median Δ | 95% CI | +5 | +15 |",
        "|------|--:|----------:|--------|----|-----|",
    ]
    for row in rows:
        lines.append(
            f"| {row['spec']} | {row['n_pairs']} | {row.get('median_delta','')} | "
            f"[{row.get('boot95_lo','')}, {row.get('boot95_hi','')}] | "
            f"{row.get('sesoi5')} | {row.get('sesoi15')} |"
        )
    lines += [
        "",
        f"Pooled merchantish curated C median = **{pooled_med}** (n={len(pooled_cs)}).",
        "",
        "## Merchant OA note",
        "",
        "Spinelli matched merchants (Balbani, Bernardini, Mattei, Buondelmonti) lack dense OA chronos; "
        "no fabricated pins. Strozzi/Ardingelli already use Dei/Barbarigo/Portinari; "
        "Arnolfini/Rucellai remain `use_in_primary=False`.",
        "",
        f"Missing primary deltas after ruler/cleric fill attempt: {miss if miss else '(none)'}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print("wrote", OUT)
    print("wrote", OUT_MD)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
