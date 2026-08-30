#!/usr/bin/env python3
"""Coverage expansion: B1-Output panel toward n≈40 (not SESOI freeze path).

Relaxes strict textual-only controls and artisan exclusion so the user can
inspect a thicker matched panel. Writes parallel tables; does NOT overwrite
the frozen primary SESOI verdict in docs without explicit note.

Outputs:
  outputs/tables/b1_output_expanded_n40_pairs.csv
  outputs/tables/b1_output_expanded_n40_summary.csv
  outputs/tables/b1_output_expanded_n40_note.md

Also refreshes wearer years via script 27 logic (offline) then expands.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, OUTPUT_TABLES

# First refresh wearer years offline (curated was just expanded).
env = os.environ.copy()
env["B1_SPARQL"] = "0"
subprocess.run(
    [sys.executable, str(Path(__file__).resolve().parent / "27_b1_output_estimand.py")],
    check=False,
    env=env,
)

# Standalone expanded computation
import csv
import random
import statistics
from collections import defaultdict


def _y(x):
    if x is None or str(x).strip() == "":
        return None
    try:
        return int(float(str(x)))
    except ValueError:
        return None


def _f(x):
    if x is None or str(x).strip() == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def _read(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def boot_median(deltas, n_boot=2000, seed=40):
    if not deltas:
        return (float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed)
    meds = []
    n = len(deltas)
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    return (
        statistics.median(deltas),
        meds[int(0.025 * (n_boot - 1))],
        meds[int(0.975 * (n_boot - 1))],
    )


def sane(years, birth, death):
    if birth is None:
        return []
    hi = (death + 5) if death is not None else birth + 95
    return [y for y in years if birth + 15 <= y <= hi]


def span45(years, birth):
    after = [y for y in years if y >= birth + 45]
    if after:
        return float(max(0, max(after) - (birth + 45)))
    return 0.0 if years else None


def main() -> None:
    census = {r["person_id"]: r for r in _read(OUTPUT_TABLES / "b1_roster_census.csv")}
    labor_ids = {r["person_id"] for r in _read(OUTPUT_TABLES / "b1_primary_estimand_pairs.csv")}
    matches = {
        m["person_id"]: m
        for m in _read(OUTPUT_TABLES / "b1_roster_control_matches_region.csv")
        if m.get("matched_control_qids")
    }
    controls = {c["qid"]: c for c in _read(OUTPUT_TABLES / "b1_control_candidates_v3.csv")}
    wear = {r["person_id"]: r for r in _read(OUTPUT_TABLES / "b1_wearer_output_years.csv")}

    p50: dict[str, list[int]] = defaultdict(list)
    p800: dict[str, list[int]] = defaultdict(list)
    for r in _read(OUTPUT_TABLES / "b1_control_p50_years.csv"):
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                p50[r["qid"]].append(y)
    for r in _read(OUTPUT_TABLES / "b1_control_p800_years.csv"):
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                p800[r["qid"]].append(y)

    # ALL primary curated nearwork as coverage fallback (incl. admin/visual)
    curated_years: dict[str, list[int]] = {}
    curated_meta: dict[str, dict] = {}
    for r in _read(DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"):
        primary = (r.get("use_in_primary") or "").lower() in {"true", "1", "yes"}
        coverage_stub = "expand_n40" in (r.get("source_ref") or "") or "COVERAGE STUB" in (
            r.get("notes") or ""
        )
        if not primary and not coverage_stub:
            continue
        q = r["qid"]
        b, d = _y(r.get("birth_year")), _y(r.get("death_year"))
        first, last = _y(r.get("first_nearwork_year")), _y(r.get("last_nearwork_year"))
        ys = [y for y in (first, last) if y is not None]
        if ys:
            curated_years[q] = sorted(set(ys))
            curated_meta[q] = {"birth": b, "death": d, "proxy": r.get("activity_proxy", "")}

    for r in _read(DATA_CURATED / "b1_control_output_years_curated.csv"):
        q = r["qid"]
        ys = [_y(x) for x in (r.get("years") or "").split(";")]
        ys = [y for y in ys if y is not None]
        if ys:
            curated_years[q] = sorted(set(curated_years.get(q, []) + ys))
            curated_meta.setdefault(q, {"birth": _y(r.get("birth_year")), "death": _y(r.get("death_year")), "proxy": "hand_pin"})

    def ctrl_bd(q):
        c = controls.get(q, {})
        b = _y(c.get("birth"))
        d = _y(c.get("death"))
        if b is None and q in curated_meta:
            b = curated_meta[q].get("birth")
        if d is None and q in curated_meta:
            d = curated_meta[q].get("death")
        return b, d

    def ctrl_years(q):
        b, d = ctrl_bd(q)
        raw = sorted(set(p50.get(q, []) + p800.get(q, []) + curated_years.get(q, [])))
        return sane(raw, b, d)

    def ctrl_span(q):
        b, _ = ctrl_bd(q)
        ys = ctrl_years(q)
        if b is None or not ys:
            return None
        return span45(ys, b)

    pair_rows = []
    for pid in sorted(labor_ids):
        c = census[pid]
        wr = wear.get(pid, {})
        m = matches.get(pid, {})
        birth = _y(c.get("birth_year"))
        death = _y(c.get("death_year"))
        # wearer years from refreshed file
        ys = []
        for part in (wr.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                ys.append(y)
        ys = sane(ys, birth, death)
        t = span45(ys, birth) if birth is not None and ys else None
        has_t = t is not None and len(ys) > 0
        spans = []
        used = []
        srcs = []
        for q in (m.get("matched_control_qids") or "").split(";"):
            if not q:
                continue
            s = ctrl_span(q)
            if s is None:
                continue
            spans.append(s)
            used.append(q)
            if q in p50 or q in p800:
                srcs.append("wd")
            else:
                srcs.append("curated")
        med = statistics.median(spans) if spans else None
        delta = (t - med) if (has_t and med is not None) else None
        pair_rows.append(
            {
                "person_id": pid,
                "name": c.get("name", ""),
                "occupation_bucket": c.get("occupation_bucket", ""),
                "occupation_class": c.get("occupation_class", ""),
                "macro_region": m.get("macro_region", ""),
                "n_works_dated": len(ys),
                "t_output_span_after_45": "" if not has_t else t,
                "n_ctrl_with_works": len(spans),
                "med_c_output_span_after_45": "" if med is None else med,
                "delta_span": "" if delta is None else round(delta, 2),
                "ctrl_qids_used": ";".join(used),
                "ctrl_source_mix": ";".join(sorted(set(srcs))),
                "in_expanded_panel": "1" if delta is not None else "0",
                "also_in_strict_primary": "",  # fill below
                "coverage_note": (
                    "expanded: admin/visual curated ctrls allowed; artisan included"
                ),
            }
        )

    strict = {
        r["person_id"]
        for r in _read(OUTPUT_TABLES / "b1_output_estimand_pairs.csv")
        if r.get("in_primary_delta") == "1"
    }
    for r in pair_rows:
        r["also_in_strict_primary"] = "1" if r["person_id"] in strict else "0"

    fields = list(pair_rows[0].keys())
    out_pairs = OUTPUT_TABLES / "b1_output_expanded_n40_pairs.csv"
    _write(out_pairs, pair_rows, fields)

    panel = [r for r in pair_rows if r["in_expanded_panel"] == "1"]
    deltas = [_f(r["delta_span"]) for r in panel]
    deltas = [d for d in deltas if d is not None]
    med, lo, hi = boot_median(deltas)

    summary = [
        {
            "panel": "expanded_coverage_n40",
            "n_pairs": len(deltas),
            "median_delta": "" if not deltas else round(med, 2),
            "boot95_lo": "" if not deltas else round(lo, 2),
            "boot95_hi": "" if not deltas else round(hi, 2),
            "n_ge_5": sum(1 for d in deltas if d >= 5),
            "n_ge_15": sum(1 for d in deltas if d >= 15),
            "share_pos": "" if not deltas else round(sum(1 for d in deltas if d > 0) / len(deltas), 3),
            "n_overlap_strict_primary": sum(1 for r in panel if r["also_in_strict_primary"] == "1"),
            "note": "COVERAGE panel not SESOI freeze; ctrls include admin/visual nearwork",
        }
    ]
    _write(OUTPUT_TABLES / "b1_output_expanded_n40_summary.csv", summary, list(summary[0].keys()))

    # tier table for user inspection
    tiers = []
    for r in sorted(panel, key=lambda x: float(x["delta_span"]), reverse=True):
        tiers.append(
            {
                "person_id": r["person_id"],
                "name": r["name"],
                "bucket": r["occupation_bucket"],
                "n_works": r["n_works_dated"],
                "t_span45": r["t_output_span_after_45"],
                "med_c": r["med_c_output_span_after_45"],
                "delta": r["delta_span"],
                "n_ctrl": r["n_ctrl_with_works"],
                "strict_primary": r["also_in_strict_primary"],
                "ctrl_mix": r["ctrl_source_mix"],
            }
        )
    _write(OUTPUT_TABLES / "b1_output_expanded_n40_roster.csv", tiers, list(tiers[0].keys()) if tiers else [])

    s = summary[0]
    note = f"""# B1-Output expanded coverage panel（目标 n≈40）

**Date:** 2026-08-02  
**目的：** 应要求先凑出约 40 人可看面板；**不是**取代冻结 SESOI 主表（strict n=19）。

## 如何扩到 n={s['n_pairs']}

1. 补佩戴者成果年：chrono 再收成 + Pius II / Wolsey / Leo X 等手针 → `b1_wearer_output_years_curated.csv`  
2. 对照放宽：凡 `use_in_primary` curated nearwork（含行政/绘画）均可进格  
3. 含 artisan/painter（如 Lotto）

## 面板结果（探索，非冻结裁决）

| | |
|--|--|
| n | **{s['n_pairs']}** |
| 中位 Δ | {s['median_delta']} |
| CI | [{s['boot95_lo']}, {s['boot95_hi']}] |
| 与 strict primary 重叠 | {s['n_overlap_strict_primary']} |
| share Δ>0 | {s['share_pos']} |

## 表

- 花名册：`b1_output_expanded_n40_roster.csv`  
- 全对：`b1_output_expanded_n40_pairs.csv`  
- 摘要：`b1_output_expanded_n40_summary.csv`  

## 读法

这是**加厚样本给你看**；质量分层看 `strict_primary` 列（1=进过冻结主表）。  
行政公爵对照会把「成果」定义变松——硬刚完整假说时仍应以 strict / 宏观线为准。
"""
    (OUTPUT_TABLES / "b1_output_expanded_n40_note.md").write_text(note, encoding="utf-8")
    print(
        f"EXPANDED n={s['n_pairs']} med={s['median_delta']} "
        f"CI=[{s['boot95_lo']},{s['boot95_hi']}] overlap_strict={s['n_overlap_strict_primary']}"
    )
    if s["n_pairs"] < 35:
        missing = [r["person_id"] for r in pair_rows if r["in_expanded_panel"] != "1"]
        print("still missing", len(missing), missing)


if __name__ == "__main__":
    main()
