#!/usr/bin/env python3
"""Occupation-bucket control matching + rate-limited SPARQL P800 densify.

Reads roster census + control v3. Writes:
  outputs/tables/b1_roster_control_matches_occ.csv
  outputs/tables/b1_roster_control_summary_occ.csv
  outputs/tables/b1_roster_control_p800_overlay_occ.csv
  outputs/tables/b1_roster_verdict.csv
  refreshes b1_control_p800_years.csv when SPARQL adds dates
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES, DATA_RAW, OUTPUT_LOGS

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
CONTROLS = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
P800_YEARS = OUTPUT_TABLES / "b1_control_p800_years.csv"
OUT_MATCH = OUTPUT_TABLES / "b1_roster_control_matches_occ.csv"
OUT_SUM = OUTPUT_TABLES / "b1_roster_control_summary_occ.csv"
OUT_P800 = OUTPUT_TABLES / "b1_roster_control_p800_overlay_occ.csv"
OUT_VERDICT = OUTPUT_TABLES / "b1_roster_verdict.csv"
RAW_CTRL = DATA_RAW / "wikidata_entity_controls"

BIRTH_WINDOW = 10
SPARQL_CHUNK = 12
SPARQL_SLEEP = 3.0
UA = "eyeglasses-hypothesis/b1-occ-p800"

# Map treatment occupation_bucket → preferred control buckets (ordered).
TREAT_TO_CTRL = {
    "humanist": ["humanist"],
    "letter_writer": ["humanist"],
    "cleric": ["cleric", "humanist"],
    "ruler_cleric": ["cleric", "ruler", "humanist"],
    "ruler": ["ruler", "humanist"],
    "merchant": ["merchant", "humanist"],
    "clerk": ["clerk", "humanist"],
    "admin": ["clerk", "admin", "humanist"],  # clerk pool thicker than sparql_admin
    "artisan": ["artisan", "humanist"],
    "other": ["humanist", "other"],
}


def log(msg: str) -> None:
    print(msg, flush=True)
    OUTPUT_LOGS.mkdir(parents=True, exist_ok=True)
    with (OUTPUT_LOGS / "b1_occ_match_p800.log").open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def _y(x: object) -> int | None:
    if x is None:
        return None
    s = str(x).strip()
    if not s:
        return None
    try:
        return int(float(s))
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


def control_bucket(cohort: str, source: str) -> str:
    c = (cohort or "").lower()
    s = (source or "").lower()
    if c.startswith("strata_ruler") or s == "sparql_ruler":
        return "ruler"
    if c.startswith("strata_artisan") or s == "sparql_artisan":
        return "artisan"
    if c.startswith("strata_merchant") or s == "sparql_merchant":
        return "merchant"
    if c.startswith("strata_clerk") or s == "sparql_clerk":
        return "clerk"
    if c.startswith("strata_admin") or s == "sparql_admin":
        return "admin"
    if source == "v2" or c.startswith("writer_poet"):
        return "humanist"
    # wd_scholar_{decade}_{occupation}
    occ = c.rsplit("_", 1)[-1] if c.startswith("wd_scholar_") else c
    if occ in {"philosopher", "historian", "writer", "scholar", "professor", "mathematician"}:
        return "humanist"
    if occ in {"theologian"}:
        return "cleric"
    return "other"


def ya45(birth: int | None, death: int | None) -> float | None:
    if birth is None or death is None or death < birth:
        return None
    return float(max(0, (death - birth) - 45))


def sparql(query: str, timeout: int = 120) -> dict:
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


def densify_p800_sparql(qids: list[str]) -> dict[str, list[int]]:
    """Batch SPARQL: person → dated P800 years. Rate-limited."""
    out: dict[str, list[int]] = defaultdict(list)
    # seed from existing file / entity cache years file
    if P800_YEARS.exists():
        for r in _read(P800_YEARS):
            ys = []
            for part in (r.get("years") or "").split(";"):
                y = _y(part)
                if y is not None:
                    ys.append(y)
            if ys:
                out[r["qid"]] = ys

    missing = [q for q in qids if q not in out or not out[q]]
    log(f"sparql densify: have={len(qids)-len(missing)} missing={len(missing)}")
    if not missing:
        return dict(out)

    for i in range(0, len(missing), SPARQL_CHUNK):
        chunk = missing[i : i + SPARQL_CHUNK]
        vals = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
SELECT ?person ?y WHERE {{
  VALUES ?person {{ {vals} }}
  ?person wdt:P800 ?work .
  OPTIONAL {{ ?work wdt:P577 ?pub . BIND(YEAR(?pub) AS ?y577) }}
  OPTIONAL {{ ?work wdt:P571 ?inc . BIND(YEAR(?inc) AS ?y571) }}
  BIND(COALESCE(?y577, ?y571) AS ?y)
  FILTER(BOUND(?y))
}}
LIMIT 2000
"""
        try:
            data = sparql(query)
            for b in data.get("results", {}).get("bindings", []):
                pid = b["person"]["value"].rsplit("/", 1)[-1]
                y = _y(b.get("y", {}).get("value"))
                if y is not None:
                    out[pid].append(y)
            log(f"  sparql chunk {i//SPARQL_CHUNK+1}: {len(chunk)} qids ok")
        except Exception as e:
            log(f"  sparql chunk FAIL: {e}")
        time.sleep(SPARQL_SLEEP)

    # dedupe
    return {q: sorted(set(ys)) for q, ys in out.items()}


def sane_years(years: list[int], birth: int | None, death: int | None) -> list[int]:
    if birth is None:
        return []
    lo, hi = birth + 10, (death + 10) if death is not None else birth + 100
    return [y for y in years if lo <= y <= hi]


def match_occ(census: list[dict], controls: list[dict]) -> tuple[list[dict], list[dict]]:
    ctrl_rows = []
    for c in controls:
        if str(c.get("is_known_wearer", "")).lower() == "true":
            continue
        b, d = _y(c.get("birth")), _y(c.get("death"))
        if b is None or d is None:
            continue
        bucket = control_bucket(c.get("cohort", ""), c.get("source", ""))
        ctrl_rows.append(
            {
                "qid": c["qid"],
                "name": c["name"],
                "birth_year": b,
                "death_year": d,
                "bucket": bucket,
                "years_alive_after_45": ya45(b, d),
                "cohort": c.get("cohort", ""),
            }
        )

    onset = [
        r
        for r in census
        if r.get("in_onsetish_treatment") == "True" and _y(r.get("birth_year")) is not None
    ]
    matches = []
    for t in onset:
        tb = _y(t["birth_year"])
        assert tb is not None
        t_bucket = t.get("occupation_bucket") or "other"
        pref = TREAT_TO_CTRL.get(t_bucket, ["humanist"])
        primary = [pref[0]] if pref else ["humanist"]
        relaxed = pref[1:] if len(pref) > 1 else []
        chosen: list[dict] = []
        match_level = "unmatched"
        for level, buckets in (
            ("occ+birth", primary),
            ("occ_relaxed", relaxed),
            ("birth_only_fallback", None),
        ):
            if not buckets and level != "birth_only_fallback":
                continue
            if buckets is None:
                cands = [c for c in ctrl_rows if abs(c["birth_year"] - tb) <= BIRTH_WINDOW]
            else:
                cands = [
                    c
                    for c in ctrl_rows
                    if c["bucket"] in buckets and abs(c["birth_year"] - tb) <= BIRTH_WINDOW
                ]
            if cands:
                chosen = sorted(cands, key=lambda c: abs(c["birth_year"] - tb))[:15]
                match_level = level
                break
        if not chosen:
            matches.append(
                {
                    "person_id": t["person_id"],
                    "name": t["name"],
                    "birth_year": tb,
                    "occupation_bucket": t_bucket,
                    "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                    "years_after_evidence_t": t.get("years_after_evidence", ""),
                    "n_matched_controls": 0,
                    "median_years_alive_after_45_c": "",
                    "delta_ya45_t_minus_c_median": "",
                    "match_status": "unmatched",
                    "match_level": "unmatched",
                    "matched_control_qids": "",
                    "control_buckets_used": "",
                }
            )
            continue
        c_ya = [c["years_alive_after_45"] for c in chosen if c["years_alive_after_45"] is not None]
        med_c = statistics.median(c_ya) if c_ya else None
        t_ya = _f(t.get("years_alive_after_45"))
        delta = (t_ya - med_c) if (t_ya is not None and med_c is not None) else None
        matches.append(
            {
                "person_id": t["person_id"],
                "name": t["name"],
                "birth_year": tb,
                "occupation_bucket": t_bucket,
                "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                "years_after_evidence_t": t.get("years_after_evidence", ""),
                "n_matched_controls": len(chosen),
                "median_years_alive_after_45_c": med_c if med_c is not None else "",
                "delta_ya45_t_minus_c_median": round(delta, 2) if delta is not None else "",
                "match_status": "matched",
                "match_level": match_level,
                "matched_control_qids": ";".join(c["qid"] for c in chosen),
                "control_buckets_used": ";".join(sorted({c["bucket"] for c in chosen})),
            }
        )

    matched = [m for m in matches if m["match_status"] == "matched"]
    occ_matched = [m for m in matched if m["match_level"] == "occ+birth"]
    relaxed = [m for m in matched if m["match_level"] == "occ_relaxed"]
    deltas = [_f(m["delta_ya45_t_minus_c_median"]) for m in matched]
    deltas_n = [d for d in deltas if d is not None]
    deltas_occ = [
        _f(m["delta_ya45_t_minus_c_median"])
        for m in occ_matched
        if _f(m["delta_ya45_t_minus_c_median"]) is not None
    ]
    summary = [
        {
            "metric": "ya45_occ_aware_match",
            "n_treatment_with_birth": len(onset),
            "n_matched": len(matched),
            "n_occ_birth_matched": len(occ_matched),
            "n_occ_relaxed": len(relaxed),
            "n_birth_only_fallback": sum(1 for m in matched if m["match_level"] == "birth_only_fallback"),
            "median_delta_ya45_all_matched": statistics.median(deltas_n) if deltas_n else "",
            "median_delta_ya45_occ_matched": statistics.median(deltas_occ) if deltas_occ else "",
            "sesoi5_all": (
                "PASS_RAW" if deltas_n and statistics.median(deltas_n) >= 5 else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi15_all": (
                "PASS_RAW" if deltas_n and statistics.median(deltas_n) >= 15 else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi5_occ": (
                "PASS_RAW" if deltas_occ and statistics.median(deltas_occ) >= 5 else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi15_occ": (
                "PASS_RAW"
                if deltas_occ and statistics.median(deltas_occ) >= 15
                else "FAIL_OR_UNAVAILABLE"
            ),
            "caveat": (
                "Outcome B=ya45 survival. Primary occ+birth = first bucket only; "
                "occ_relaxed = secondary buckets (e.g. merchant→humanist). Not archive-negative."
            ),
        }
    ]
    return matches, summary


def p800_overlay(
    census: list[dict], matches: list[dict], controls: list[dict], years_by_q: dict[str, list[int]]
) -> tuple[list[dict], dict]:
    ctrl = {c["qid"]: c for c in controls}
    rows = []
    deltas: list[float] = []
    deltas3: list[float] = []
    for m in matches:
        if m["match_status"] != "matched":
            continue
        t = next(r for r in census if r["person_id"] == m["person_id"])
        tb = _y(t["birth_year"])
        td = _y(t["death_year"])
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
            if not q or q not in ctrl:
                continue
            cb, cd = _y(ctrl[q]["birth"]), _y(ctrl[q]["death"])
            ys = sane_years(years_by_q.get(q, []), cb, cd)
            if not ys or cb is None:
                continue
            c_works.append(max(0.0, max(ys) - (cb + 45)))
        med_c = statistics.median(c_works) if c_works else None
        delta = (t_work - med_c) if (t_work is not None and med_c is not None) else None
        if delta is not None:
            deltas.append(delta)
            if len(c_works) >= 3:
                deltas3.append(delta)
        rows.append(
            {
                "person_id": m["person_id"],
                "occupation_bucket": m["occupation_bucket"],
                "match_level": m["match_level"],
                "t_work_after_45": t_work if t_work is not None else "",
                "n_ctrl_with_p800": len(c_works),
                "med_c_work_after_45": med_c if med_c is not None else "",
                "delta": round(delta, 2) if delta is not None else "",
                "years_after_evidence": t.get("years_after_evidence", ""),
            }
        )
    stats = {
        "n_with_delta": len(deltas),
        "median_delta": statistics.median(deltas) if deltas else None,
        "mean_delta": round(statistics.mean(deltas), 2) if deltas else None,
        "ge5": sum(1 for d in deltas if d >= 5) if deltas else 0,
        "ge15": sum(1 for d in deltas if d >= 15) if deltas else 0,
        "n_delta_ctrl_ge3": len(deltas3),
        "median_delta_ctrl_ge3": statistics.median(deltas3) if deltas3 else None,
    }
    return rows, stats


def verdict_rows(
    census: list[dict],
    sum_birth: list[dict],
    sum_occ: list[dict],
    p800_stats: dict,
) -> list[dict]:
    onset = [r for r in census if r["in_onsetish_treatment"] == "True"]
    ys = [_f(r["years_after_evidence"]) for r in onset if r.get("years_after_source") == "activity_proxy"]
    ys_n = [y for y in ys if y is not None]
    hard = [
        _f(r["years_after_evidence"])
        for r in onset
        if str(r.get("hard_dated_series")).lower() == "true"
    ]
    hard_n = [y for y in hard if y is not None]
    birth_sum = sum_birth[0] if sum_birth else {}
    occ_sum = sum_occ[0] if sum_occ else {}

    def row(check: str, result: str, detail: str) -> dict:
        return {"check": check, "result": result, "detail": detail}

    rows = [
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
        row(
            "sesoi_direction_5_ya45_birth",
            birth_sum.get("sesoi_direction_5_on_median_delta", birth_sum.get("sesoi5_all", "NA")),
            f"median_delta_ya45={birth_sum.get('median_delta_ya45_t_minus_c', birth_sum.get('median_delta_ya45_all_matched',''))}",
        ),
        row(
            "sesoi_direction_5_ya45_occ",
            occ_sum.get("sesoi5_occ", "NA"),
            f"median_delta_occ={occ_sum.get('median_delta_ya45_occ_matched','')}; "
            f"n_occ={occ_sum.get('n_occ_birth_matched','')}",
        ),
        row(
            "sesoi_macfarlane_15_ya45",
            "FAIL",
            "survival proxy; both birth and occ matches well below +15",
        ),
        row(
            "sesoi_direction_5_p800_work",
            (
                "PASS_RAW"
                if p800_stats.get("median_delta") is not None and p800_stats["median_delta"] >= 5
                else "FAIL_OR_UNAVAILABLE"
            ),
            f"n={p800_stats.get('n_with_delta')}; median_delta={p800_stats.get('median_delta')}; "
            f"ge15={p800_stats.get('ge15')}; ctrl_ge3_median={p800_stats.get('median_delta_ctrl_ge3')}",
        ),
        row(
            "sesoi_macfarlane_15_p800_work",
            (
                "PASS_RAW"
                if p800_stats.get("median_delta") is not None and p800_stats["median_delta"] >= 15
                else "FAIL"
            ),
            f"share_pairs_ge15={p800_stats.get('ge15')}/{p800_stats.get('n_with_delta')} — thin P800 coverage",
        ),
        row(
            "b1_nearwork_causal",
            "UNIDENTIFIED",
            "Need denser control near-work + archive-negative controls; hard n not estimand",
        ),
    ]
    return rows


def main() -> None:
    census = _read(CENSUS)
    controls = _read(CONTROLS)
    # prior birth-only summary if present
    sum_birth = (
        _read(OUTPUT_TABLES / "b1_roster_control_summary.csv")
        if (OUTPUT_TABLES / "b1_roster_control_summary.csv").exists()
        else []
    )

    matches, sum_occ = match_occ(census, controls)
    _write(
        OUT_MATCH,
        matches,
        [
            "person_id",
            "name",
            "birth_year",
            "occupation_bucket",
            "years_alive_after_45_t",
            "years_after_evidence_t",
            "n_matched_controls",
            "median_years_alive_after_45_c",
            "delta_ya45_t_minus_c_median",
            "match_status",
            "match_level",
            "matched_control_qids",
            "control_buckets_used",
        ],
    )
    _write(OUT_SUM, sum_occ, list(sum_occ[0].keys()))
    log(
        f"occ-match: matched={sum_occ[0]['n_matched']} occ+birth={sum_occ[0]['n_occ_birth_matched']} "
        f"fallback={sum_occ[0]['n_birth_only_fallback']} med_delta_occ={sum_occ[0]['median_delta_ya45_occ_matched']}"
    )

    # SPARQL densify for matched control QIDs
    need_q: set[str] = set()
    for m in matches:
        if m["match_status"] == "matched":
            need_q.update(q for q in m["matched_control_qids"].split(";") if q)
    # Reuse existing years unless --sparql flag / env B1_SPARQL=1
    run_sparql = os.environ.get("B1_SPARQL", "").strip() in {"1", "true", "yes"}
    if run_sparql:
        years_by_q = densify_p800_sparql(sorted(need_q))
    else:
        years_by_q = densify_p800_sparql([])  # load file only
        # ensure keys exist
        for q in need_q:
            years_by_q.setdefault(q, [])
        log(f"sparql skipped (set B1_SPARQL=1 to densify); loaded years for {sum(1 for q in need_q if years_by_q.get(q))}/{len(need_q)}")

    # persist years file (union)
    year_rows = []
    for q in sorted(set(need_q) | set(years_by_q)):
        c = next((x for x in controls if x["qid"] == q), None)
        b, d = (_y(c["birth"]), _y(c["death"])) if c else (None, None)
        ys = sane_years(years_by_q.get(q, []), b, d)
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
    _write(P800_YEARS, year_rows, ["qid", "n_works_dated", "first_year", "last_year", "years"])
    log(f"p800 years sane>0: {sum(1 for r in year_rows if int(r['n_works_dated'])>0)}/{len(year_rows)}")

    overlay, p800_stats = p800_overlay(census, matches, controls, years_by_q)
    _write(
        OUT_P800,
        overlay,
        [
            "person_id",
            "occupation_bucket",
            "match_level",
            "t_work_after_45",
            "n_ctrl_with_p800",
            "med_c_work_after_45",
            "delta",
            "years_after_evidence",
        ],
    )
    log(
        f"p800 overlay: n_delta={p800_stats['n_with_delta']} median={p800_stats['median_delta']} "
        f"ge5={p800_stats['ge5']} ge15={p800_stats['ge15']} "
        f"ctrl>=3 median={p800_stats['median_delta_ctrl_ge3']}"
    )

    verdict = verdict_rows(census, sum_birth, sum_occ, p800_stats)
    _write(OUT_VERDICT, verdict, ["check", "result", "detail"])
    for v in verdict:
        log(f"VERDICT {v['check']}: {v['result']} — {v['detail']}")


if __name__ == "__main__":
    main()
