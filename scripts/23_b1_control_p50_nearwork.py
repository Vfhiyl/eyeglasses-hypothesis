#!/usr/bin/env python3
"""Densify control near-work via Wikidata P50 (author-of) dated works.

Why: P800 notable-works coverage is too thin (~50/300 matched controls).
P50→P577 is denser for writers/scholars and closer to 'dated near-work'
than survival (ya45).

Reads occ-matched pairs; writes:
  outputs/tables/b1_control_p50_years.csv
  outputs/tables/b1_roster_control_p50_overlay.csv
  outputs/tables/b1_roster_verdict.csv  (refreshed P50 rows)
  outputs/tables/b1_direction_decision_2026-07-31.md
"""
from __future__ import annotations

import csv
import json
import os
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES, OUTPUT_LOGS

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
MATCHES = OUTPUT_TABLES / "b1_roster_control_matches_occ.csv"
CONTROLS = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
OUT_YEARS = OUTPUT_TABLES / "b1_control_p50_years.csv"
OUT_OVERLAY = OUTPUT_TABLES / "b1_roster_control_p50_overlay.csv"
OUT_VERDICT = OUTPUT_TABLES / "b1_roster_verdict.csv"
OUT_DECISION = OUTPUT_TABLES / "b1_direction_decision_2026-07-31.md"
LOG = OUTPUT_LOGS / "b1_p50_densify.log"

CHUNK = 15
SLEEP = 3.5
UA = "eyeglasses-hypothesis/b1-p50-nearwork"


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


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


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def sparql(query: str, timeout: int = 150) -> dict:
    env = os.environ.copy()
    r = subprocess.run(
        [
            "curl",
            "-fsSL",
            "--http1.1",
            "--max-time",
            str(timeout),
            "-H",
            "Accept: application/sparql-results+json",
            "-H",
            f"User-Agent: {UA}",
            "--data-urlencode",
            f"query={query.strip()}",
            "https://query.wikidata.org/sparql",
        ],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError((r.stderr or r.stdout or f"exit {r.returncode}")[-400:])
    return json.loads(r.stdout)


def fetch_p50_years(qids: list[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = defaultdict(list)
    if OUT_YEARS.exists():
        for r in _read(OUT_YEARS):
            for part in (r.get("years") or "").split(";"):
                y = _y(part)
                if y is not None:
                    out[r["qid"]].append(y)

    missing = [q for q in qids if not out.get(q)]
    log(f"P50 densify have={len(qids)-len(missing)} missing={len(missing)}")
    run = os.environ.get("B1_SPARQL", "1").strip() not in {"0", "false", "no"}
    if not run:
        log("B1_SPARQL=0 — skip network")
        return {q: sorted(set(ys)) for q, ys in out.items()}

    for i in range(0, len(missing), CHUNK):
        chunk = missing[i : i + CHUNK]
        vals = " ".join(f"wd:{q}" for q in chunk)
        # P50 author-of works with publication/inception year
        query = f"""
SELECT ?person ?y WHERE {{
  VALUES ?person {{ {vals} }}
  ?work wdt:P50 ?person .
  OPTIONAL {{ ?work wdt:P577 ?pub . BIND(YEAR(?pub) AS ?y577) }}
  OPTIONAL {{ ?work wdt:P571 ?inc . BIND(YEAR(?inc) AS ?y571) }}
  BIND(COALESCE(?y577, ?y571) AS ?y)
  FILTER(BOUND(?y))
}}
LIMIT 5000
"""
        try:
            data = sparql(query)
            n = 0
            for b in data.get("results", {}).get("bindings", []):
                pid = b["person"]["value"].rsplit("/", 1)[-1]
                y = _y(b.get("y", {}).get("value"))
                if y is not None:
                    out[pid].append(y)
                    n += 1
            log(f"  chunk {i//CHUNK+1}: {len(chunk)} qids rows={n}")
        except Exception as e:
            log(f"  chunk FAIL: {e}")
        time.sleep(SLEEP)
    return {q: sorted(set(ys)) for q, ys in out.items()}


def sane(years: list[int], birth: int | None, death: int | None) -> list[int]:
    if birth is None:
        return []
    lo, hi = birth + 15, (death + 5) if death is not None else birth + 95
    return [y for y in years if lo <= y <= hi]


def work_after_45(years: list[int], birth: int) -> float | None:
    if not years:
        return None
    return float(max(0, max(years) - (birth + 45)))


def bootstrap_median(deltas: list[float], n_boot: int = 2000, seed: int = 31) -> tuple[float, float, float]:
    rng = random.Random(seed)
    if not deltas:
        return (float("nan"), float("nan"), float("nan"))
    meds = []
    n = len(deltas)
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    lo = meds[int(0.025 * (n_boot - 1))]
    hi = meds[int(0.975 * (n_boot - 1))]
    return (statistics.median(deltas), lo, hi)


def main() -> None:
    census = {r["person_id"]: r for r in _read(CENSUS)}
    matches = [m for m in _read(MATCHES) if m.get("match_status") == "matched"]
    controls = {c["qid"]: c for c in _read(CONTROLS)}

    need: set[str] = set()
    for m in matches:
        need.update(q for q in m["matched_control_qids"].split(";") if q)
    years_raw = fetch_p50_years(sorted(need))

    # persist sane years
    year_rows = []
    years_by_q: dict[str, list[int]] = {}
    for q in sorted(need):
        c = controls.get(q)
        b, d = (_y(c["birth"]), _y(c["death"])) if c else (None, None)
        ys = sane(years_raw.get(q, []), b, d)
        years_by_q[q] = ys
        year_rows.append(
            {
                "qid": q,
                "n_works_dated": len(ys),
                "first_year": min(ys) if ys else "",
                "last_year": max(ys) if ys else "",
                "years": ";".join(map(str, ys)),
            }
        )
    _write(OUT_YEARS, year_rows, ["qid", "n_works_dated", "first_year", "last_year", "years"])
    log(f"P50 sane>0: {sum(1 for r in year_rows if int(r['n_works_dated'])>0)}/{len(year_rows)}")

    overlay = []
    deltas: list[float] = []
    deltas3: list[float] = []
    for m in matches:
        t = census[m["person_id"]]
        tb, td = _y(t.get("birth_year")), _y(t.get("death_year"))
        try:
            evid = int(float(t["evidence_year"]))
            ya = float(t["years_after_evidence"])
            t_last = evid + ya
            if td is not None:
                t_last = min(t_last, td)
            t_work = max(0.0, t_last - (tb + 45)) if tb is not None else None
        except (TypeError, ValueError):
            t_work = None
        c_works = []
        for q in m["matched_control_qids"].split(";"):
            if not q or q not in controls:
                continue
            cb = _y(controls[q]["birth"])
            ys = years_by_q.get(q, [])
            if not ys or cb is None:
                continue
            w = work_after_45(ys, cb)
            if w is not None:
                c_works.append(w)
        med_c = statistics.median(c_works) if c_works else None
        delta = (t_work - med_c) if (t_work is not None and med_c is not None) else None
        if delta is not None:
            deltas.append(delta)
            if len(c_works) >= 3:
                deltas3.append(delta)
        overlay.append(
            {
                "person_id": m["person_id"],
                "occupation_bucket": m.get("occupation_bucket", ""),
                "match_level": m.get("match_level", ""),
                "t_work_after_45": t_work if t_work is not None else "",
                "n_ctrl_with_p50": len(c_works),
                "med_c_work_after_45": med_c if med_c is not None else "",
                "delta": round(delta, 2) if delta is not None else "",
                "years_after_evidence": t.get("years_after_evidence", ""),
            }
        )
    _write(
        OUT_OVERLAY,
        overlay,
        [
            "person_id",
            "occupation_bucket",
            "match_level",
            "t_work_after_45",
            "n_ctrl_with_p50",
            "med_c_work_after_45",
            "delta",
            "years_after_evidence",
        ],
    )

    med, lo, hi = bootstrap_median(deltas)
    med3, lo3, hi3 = bootstrap_median(deltas3)
    log(
        f"P50 overlay n={len(deltas)} median={med} CI95=[{lo},{hi}] "
        f"ge5={sum(d>=5 for d in deltas)} ge15={sum(d>=15 for d in deltas)}"
    )
    log(
        f"P50 n_ctrl>=3 n={len(deltas3)} median={med3} CI95=[{lo3},{hi3}]"
    )

    # refresh verdict: keep prior rows from file if present, replace P50-related
    prior = {r["check"]: r for r in _read(OUT_VERDICT)} if OUT_VERDICT.exists() else {}

    def row(check: str, result: str, detail: str) -> dict:
        return {"check": check, "result": result, "detail": detail}

    onset = [r for r in census.values() if r.get("in_onsetish_treatment") == "True"]
    ys = [_f(r["years_after_evidence"]) for r in onset if r.get("years_after_source") == "activity_proxy"]
    ys_n = [y for y in ys if y is not None]
    hard = [
        _f(r["years_after_evidence"])
        for r in onset
        if str(r.get("hard_dated_series")).lower() == "true"
    ]
    hard_n = [y for y in hard if y is not None]

    verdict = [
        row(
            "onsetish_activity_coded",
            "DONE",
            f"n={len(ys_n)}/{len(onset)}; median={statistics.median(ys_n) if ys_n else 'NA'}; "
            f"share_ge15={round(sum(y>=15 for y in ys_n)/len(ys_n),3) if ys_n else 'NA'}",
        ),
        row(
            "hard_appendix_bias",
            "DOCUMENTED",
            f"hard_median={statistics.median(hard_n) if hard_n else 'NA'} vs ungated_median="
            f"{statistics.median(ys_n) if ys_n else 'NA'}",
        ),
        prior.get(
            "sesoi_direction_5_ya45_birth",
            row("sesoi_direction_5_ya45_birth", "SEE_PRIOR", "from script 22"),
        ),
        prior.get(
            "sesoi_direction_5_ya45_occ",
            row("sesoi_direction_5_ya45_occ", "SEE_PRIOR", "from script 22"),
        ),
        row("sesoi_macfarlane_15_ya45", "FAIL", "survival proxy below +15"),
        prior.get(
            "sesoi_direction_5_p800_work",
            row("sesoi_direction_5_p800_work", "SEE_PRIOR", "thin P800"),
        ),
        row(
            "sesoi_direction_5_p50_work",
            (
                "PASS_RAW"
                if deltas and med >= 5
                else "FAIL_OR_UNAVAILABLE"
            ),
            f"n={len(deltas)}; median={med}; bootstrap95=[{lo},{hi}]; "
            f"ge5={sum(d>=5 for d in deltas)}; ge15={sum(d>=15 for d in deltas)}; "
            f"ctrl>=3 n={len(deltas3)} median={med3} CI=[{lo3},{hi3}]",
        ),
        row(
            "sesoi_macfarlane_15_p50_work",
            "PASS_RAW" if deltas and med >= 15 else "FAIL",
            f"median={med}; CI95=[{lo},{hi}] — WD author dates ≠ letter near-work",
        ),
        row(
            "b1_nearwork_causal",
            "UNIDENTIFIED",
            "n-expansion frozen; need archive-grade control near-work + spectacle-negative checks",
        ),
        row(
            "direction_decision",
            "FREEZE_N_EXPAND_MEASURE",
            "Stop growing roster/control n as main path; densify matched-pair near-work measurement",
        ),
    ]
    _write(OUT_VERDICT, verdict, ["check", "result", "detail"])

    decision = f"""# B1 direction decision (2026-07-31)

## Judgment

**Matching n is no longer the bottleneck.** Onsetish 34; primary occ-matched 29; control pool ~2341.
Further name-hunting / control-stratum expansion has low ROI for identification.

**Bottleneck = measurement of near-work on both sides of matched pairs**, especially controls.

## Freeze

- Freeze **hard dated series** hunting as main goal (appendix only).
- Freeze **roster/control n expansion** as main goal (unless a named wearer falls in OA lap).
- Main path = densify **dated near-work** for the existing 29 matched treatments and their controls.

## This pass

- SPARQL **P50 author-of → P577/P571** years for matched controls (denser than P800).
- Overlay: `b1_roster_control_p50_overlay.csv`
- Bootstrap 95% CI on median Δ work_after_45.

### P50 result (exploratory)

| | |
|--|--|
| n pairs with Δ | {len(deltas)} |
| median Δ | {med} |
| bootstrap 95% CI | [{lo}, {hi}] |
| pairs with Δ≥5 / ≥15 | {sum(d>=5 for d in deltas)} / {sum(d>=15 for d in deltas)} |
| subset n_ctrl≥3 median (CI) | {med3} ([{lo3}, {hi3}]) |

**Read:** WD publication dates are still a proxy, not letter/account near-work; not archive spectacle-negative.
If CI excludes 0 and median ≥5, that is only **PASS_RAW** on this proxy — not B1 identification.

## Next worth doing

1. For the ~{29 - len(deltas)} treatments lacking control P50 coverage: hand/OA letter chronologies for 3–5 closest controls each (human time / blocked archives).
2. Spectacle-negative check on a random 20 controls (OCR Ilardi + repo).
3. Do **not** prioritize finding wearer #35.
"""
    OUT_DECISION.write_text(decision)
    log(f"wrote {OUT_DECISION}")
    for v in verdict:
        log(f"VERDICT {v['check']}: {v['result']} — {v['detail'][:120]}")


if __name__ == "__main__":
    main()
