#!/usr/bin/env python3
"""B1-Output estimand: dated works (P50∪P800) after age 45 vs matched controls.

Writes:
  outputs/tables/b1_wearer_output_years.csv
  outputs/tables/b1_output_estimand_pairs.csv
  outputs/tables/b1_output_estimand_summary.csv
  outputs/tables/b1_output_estimand_method.md

Env:
  B1_SPARQL=0  — skip live densify; use caches + local wearer works only
  https_proxy  — default http://127.0.0.1:12309
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
from _paths import DATA_CURATED, DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
PAIRS_LABOR = OUTPUT_TABLES / "b1_primary_estimand_pairs.csv"
MATCHES = OUTPUT_TABLES / "b1_roster_control_matches_region.csv"
CONTROLS = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
CTRL_P50 = OUTPUT_TABLES / "b1_control_p50_years.csv"
CTRL_P800 = OUTPUT_TABLES / "b1_control_p800_years.csv"
CTRL_CURATED = DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"
CTRL_ELIG = DATA_CURATED / "b1_control_output_eligibility.csv"
CTRL_OUT_YEARS = DATA_CURATED / "b1_control_output_years_curated.csv"
# AUDIT 2026-08-12: overlay/exclude layer removed from the measurement path
# (b1_output_strict_control_overlays.csv / b1_output_control_excludes.csv
# remain on disk as historical record only).
WEARER_WORKS = DATA_PROCESSED / "b1_wearer_p50_p800_works.csv"
WEARER_CURATED = DATA_CURATED / "b1_wearer_output_years_curated.csv"

OUT_WEARER_YEARS = OUTPUT_TABLES / "b1_wearer_output_years.csv"
OUT_PAIR = OUTPUT_TABLES / "b1_output_estimand_pairs.csv"
OUT_SUM = OUTPUT_TABLES / "b1_output_estimand_summary.csv"
OUT_METHOD = OUTPUT_TABLES / "b1_output_estimand_method.md"
LOG = OUTPUT_LOGS / "b1_output_estimand.log"

CHUNK = 12
SLEEP = 3.0
UA = "eyeglasses-hypothesis/b1-output-estimand"
PROXY = (
    os.environ.get("https_proxy")
    or os.environ.get("HTTPS_PROXY")
    or "http://127.0.0.1:12309"
)


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
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def load_years_csv(path: Path) -> dict[str, list[int]]:
    out: dict[str, list[int]] = defaultdict(list)
    for r in _read(path):
        q = (r.get("qid") or "").strip()
        if not q:
            continue
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                out[q].append(y)
    return {q: sorted(set(ys)) for q, ys in out.items()}


def load_local_wearer_years() -> dict[str, list[int]]:
    """Keys: qid or pid:<person_id> -> years from local caches.

    Hand-curated `b1_wearer_output_years_curated.csv` is authoritative for a
    person_id when present (so Pass BG-style death-terminus removals stick;
    prior OUT_WEARER_YEARS cache must not re-inject dropped years).
    """
    by_pid: dict[str, list[int]] = defaultdict(list)
    by_qid: dict[str, list[int]] = defaultdict(list)
    curated_pids: set[str] = set()
    curated_years: dict[str, list[int]] = {}
    for r in _read(WEARER_CURATED):
        pid = (r.get("person_id") or "").strip()
        if not pid:
            continue
        ys: list[int] = []
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                ys.append(y)
        if ys:
            curated_pids.add(pid)
            curated_years[pid] = sorted(set(ys))
    for r in _read(WEARER_WORKS):
        y = _y(r.get("pub_year"))
        if y is None:
            continue
        pid = (r.get("person_id") or "").strip()
        q = (r.get("qid") or "").strip()
        if pid and pid not in curated_pids:
            by_pid[pid].append(y)
        if q.startswith("Q"):
            by_qid[q].append(y)
    # prior run cache (skip person_ids with authoritative curated years)
    for r in _read(OUT_WEARER_YEARS):
        q = (r.get("qid") or "").strip()
        pid = (r.get("person_id") or "").strip()
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is None:
                continue
            if pid and pid not in curated_pids:
                by_pid[pid].append(y)
            if q.startswith("Q"):
                by_qid[q].append(y)
    for pid, ys in curated_years.items():
        by_pid[pid] = list(ys)
    return {
        **{f"pid:{k}": sorted(set(v)) for k, v in by_pid.items()},
        **{k: sorted(set(v)) for k, v in by_qid.items()},
    }


def load_ctrl_meta() -> dict[str, dict[str, int | None]]:
    """qid -> birth/death from candidates, eligibility, or output-years curated."""
    meta: dict[str, dict[str, int | None]] = {}
    for r in _read(CONTROLS):
        q = (r.get("qid") or "").strip()
        if q:
            meta[q] = {"birth": _y(r.get("birth")), "death": _y(r.get("death"))}
    for path in (CTRL_ELIG, CTRL_OUT_YEARS, CTRL_CURATED):
        for r in _read(path):
            q = (r.get("qid") or "").strip()
            if not q:
                continue
            cur = meta.setdefault(q, {"birth": None, "death": None})
            if cur["birth"] is None:
                cur["birth"] = _y(r.get("birth_year"))
            if cur["death"] is None:
                cur["death"] = _y(r.get("death_year"))
    return meta


def load_ctrl_curated_years() -> dict[str, list[int]]:
    """qid -> dated output years (hand pins preferred; else eligible first;last)."""
    eligible: set[str] = set()
    for r in _read(CTRL_ELIG):
        if (r.get("output_eligible") or "").strip().lower() in {"true", "1", "yes"}:
            q = (r.get("qid") or "").strip()
            if q:
                eligible.add(q)
    out: dict[str, list[int]] = {}
    for r in _read(CTRL_OUT_YEARS):
        q = (r.get("qid") or "").strip()
        if not q:
            continue
        if eligible and q not in eligible:
            continue
        ys = []
        for part in (r.get("years") or "").split(";"):
            y = _y(part)
            if y is not None:
                ys.append(y)
        if ys:
            out[q] = sorted(set(ys))
    # endpoint fallback for eligible without hand pins
    for r in _read(CTRL_CURATED):
        if (r.get("use_in_primary") or "").strip().lower() not in {"true", "1", "yes"}:
            continue
        q = (r.get("qid") or "").strip()
        if not q or q in out:
            continue
        if eligible and q not in eligible:
            continue
        first = _y(r.get("first_nearwork_year"))
        last = _y(r.get("last_nearwork_year"))
        ys = [y for y in (first, last) if y is not None]
        if ys:
            out[q] = sorted(set(ys))
    return out


def sparql(query: str, timeout: int = 150) -> dict:
    env = os.environ.copy()
    env["HTTPS_PROXY"] = PROXY
    env["HTTP_PROXY"] = PROXY
    env["https_proxy"] = PROXY
    env["http_proxy"] = PROXY
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


def fetch_work_years(qids: list[str], prop: str) -> dict[str, list[int]]:
    """prop: P50 (author of) or P800 (notable work)."""
    out: dict[str, list[int]] = defaultdict(list)
    if not qids:
        return {}
    for i in range(0, len(qids), CHUNK):
        chunk = qids[i : i + CHUNK]
        vals = " ".join(f"wd:{q}" for q in chunk)
        if prop == "P50":
            link = "?work wdt:P50 ?person ."
        else:
            link = "?person wdt:P800 ?work ."
        query = f"""
SELECT ?person ?y WHERE {{
  VALUES ?person {{ {vals} }}
  {link}
  OPTIONAL {{ ?work wdt:P577 ?pub . BIND(YEAR(?pub) AS ?y577) }}
  OPTIONAL {{ ?work wdt:P571 ?inc . BIND(YEAR(?inc) AS ?y571) }}
  BIND(COALESCE(?y577, ?y571) AS ?y)
  FILTER(BOUND(?y))
}}
LIMIT 8000
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
            log(f"  {prop} chunk {i // CHUNK + 1}: qids={len(chunk)} rows={n}")
        except Exception as e:
            log(f"  {prop} chunk FAIL: {e}")
        time.sleep(SLEEP)
    return {q: sorted(set(ys)) for q, ys in out.items()}


def sane(years: list[int], birth: int | None, death: int | None) -> list[int]:
    if birth is None:
        return []
    lo = birth + 15
    hi = (death + 5) if death is not None else birth + 95
    return [y for y in years if lo <= y <= hi]


def metrics(years: list[int], birth: int, evidence: int | None) -> dict[str, float | int | str]:
    after45 = [y for y in years if y >= birth + 45]
    span45 = max(0, max(after45) - (birth + 45)) if after45 else 0
    n45 = len(after45)
    share45 = (n45 / len(years)) if years else ""
    if evidence is not None:
        after_ev = [y for y in years if y >= evidence]
        span_ev = max(0, max(after_ev) - evidence) if after_ev else 0
        n_ev = len(after_ev)
    else:
        span_ev, n_ev = "", ""
    return {
        "n_works_dated": len(years),
        "first_year": min(years) if years else "",
        "last_year": max(years) if years else "",
        "n_works_after_45": n45,
        "output_span_after_45": span45 if years else "",
        "share_works_after_45": round(share45, 4) if share45 != "" else "",
        "n_works_after_evidence": n_ev,
        "output_span_after_evidence": span_ev,
    }


def boot_median(deltas: list[float], n_boot: int = 2000, seed: int = 42) -> tuple[float, float, float]:
    if not deltas:
        return (float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed)
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
    labor_ids = {r["person_id"] for r in _read(PAIRS_LABOR)}
    matches = {
        m["person_id"]: dict(m)
        for m in _read(MATCHES)
        if m.get("match_status") == "matched" or m.get("matched_control_qids")
    }
    # AUDIT 2026-08-12: the strict overlay / per-wearer exclude layer was
    # outcome-aware (one-directional lifespan/span reasons) and manufactured
    # SESOI+5; it is no longer applied. Files stay on disk as history only.
    controls = {c["qid"]: c for c in _read(CONTROLS)}
    log("outcome-aware overlay/exclude layer: DISABLED (audit 2026-08-12)")

    local = load_local_wearer_years()
    ctrl_p50 = load_years_csv(CTRL_P50)
    ctrl_p800 = load_years_csv(CTRL_P800)
    ctrl_meta = load_ctrl_meta()
    ctrl_curated_years = load_ctrl_curated_years()
    elig_false: set[str] = set()
    elig_true: set[str] = set()
    for r in _read(CTRL_ELIG):
        q = (r.get("qid") or "").strip()
        if not q:
            continue
        if (r.get("output_eligible") or "").strip().lower() in {"true", "1", "yes"}:
            elig_true.add(q)
        else:
            elig_false.add(q)
    log(f"control curated output pins: {len(ctrl_curated_years)}; elig_true={len(elig_true)} elig_false={len(elig_false)}")

    # Visual artisans are appendix-only for textual B1-Output SESOI (Macfarlane brain-work).
    PRIMARY_EXCLUDE_BUCKETS = {"artisan"}
    PRIMARY_EXCLUDE_CLASS_SUBSTR = ("painter", "sculptor", "fresco")

    treat_qids: list[str] = []
    for pid in sorted(labor_ids):
        q = (census.get(pid, {}).get("wikidata_qid") or "").strip()
        if q.startswith("Q"):
            treat_qids.append(q)
    treat_qids = sorted(set(treat_qids))

    wear_p50: dict[str, list[int]] = defaultdict(list)
    wear_p800: dict[str, list[int]] = defaultdict(list)
    for q in treat_qids:
        if q in local:
            wear_p50[q].extend(local[q])

    run_sparql = os.environ.get("B1_SPARQL", "1").strip() not in {"0", "false", "no"}
    log(f"B1-Output: treatments with QID={len(treat_qids)}; SPARQL={run_sparql}; proxy={PROXY}")
    if run_sparql:
        log(f"fetch P50 for all treat QIDs n={len(treat_qids)}")
        for q, ys in fetch_work_years(treat_qids, "P50").items():
            wear_p50[q].extend(ys)
        log(f"fetch P800 for all treat QIDs n={len(treat_qids)}")
        for q, ys in fetch_work_years(treat_qids, "P800").items():
            wear_p800[q].extend(ys)

    wear_p50 = {q: sorted(set(ys)) for q, ys in wear_p50.items()}
    wear_p800 = {q: sorted(set(ys)) for q, ys in wear_p800.items()}

    # Persist wearer year rows
    wear_rows = []
    for pid in sorted(labor_ids):
        c = census[pid]
        q = (c.get("wikidata_qid") or "").strip()
        birth = _y(c.get("birth_year"))
        death = _y(c.get("death_year"))
        ev = _y(c.get("evidence_year"))
        # merge local by person_id; curated years are authoritative when present
        raw_p50 = list(wear_p50.get(q, []))
        raw_p50.extend(local.get(q, []))
        raw_curated = list(local.get(f"pid:{pid}", []))
        raw_p800 = list(wear_p800.get(q, []))
        if raw_curated:
            raw_union = sorted(set(raw_curated))
        else:
            raw_union = sorted(set(raw_p50 + raw_curated + raw_p800))
        union = sane(raw_union, birth, death)
        p50s = sane(raw_p50, birth, death)
        p800s = sane(raw_p800, birth, death)
        n_curated = len(sane(raw_curated, birth, death))
        m = metrics(union, birth, ev) if birth is not None else {
            "n_works_dated": 0,
            "first_year": "",
            "last_year": "",
            "n_works_after_45": 0,
            "output_span_after_45": "",
            "share_works_after_45": "",
            "n_works_after_evidence": "",
            "output_span_after_evidence": "",
        }
        m_p800 = metrics(p800s, birth, ev) if birth is not None and p800s else None
        wear_rows.append(
            {
                "person_id": pid,
                "name": c.get("name", ""),
                "qid": q,
                "birth_year": birth if birth is not None else "",
                "death_year": death if death is not None else "",
                "evidence_year": ev if ev is not None else "",
                "n_p50": len(p50s),
                "n_p800": len(p800s),
                "n_curated_chrono": n_curated,
                "years": ";".join(str(y) for y in union),
                "years_p800": ";".join(str(y) for y in p800s),
                **{k: m[k] for k in m},
                "output_span_after_45_p800": "" if not m_p800 else m_p800["output_span_after_45"],
                "n_works_after_45_p800": "" if not m_p800 else m_p800["n_works_after_45"],
            }
        )
    wear_fields = list(wear_rows[0].keys()) if wear_rows else []
    _write(OUT_WEARER_YEARS, wear_rows, wear_fields)
    n_with = sum(1 for r in wear_rows if int(r.get("n_works_dated") or 0) > 0)
    log(f"wearer years written: {len(wear_rows)}; with dated works={n_with}")

    wear_by_pid = {r["person_id"]: r for r in wear_rows}

    def ctrl_birth_death(qid: str) -> tuple[int | None, int | None]:
        m = ctrl_meta.get(qid, {})
        return m.get("birth"), m.get("death")

    def ctrl_union_years(qid: str) -> list[int]:
        birth, death = ctrl_birth_death(qid)
        raw = sorted(
            set(
                ctrl_p50.get(qid, [])
                + ctrl_p800.get(qid, [])
                + ctrl_curated_years.get(qid, [])
            )
        )
        return sane(raw, birth, death)

    def ctrl_allowed(qid: str) -> bool:
        """Drop visual/admin controls and death-before-45 peers (span locked at 0)."""
        if qid in elig_false:
            return False
        # Symmetric to treatment exclude_death_before_45: a control who dies
        # before age 45 cannot define post-45 output span (artifact span 0
        # deflates C median → inflates Δ).
        birth, death = ctrl_birth_death(qid)
        if birth is not None and death is not None and death < birth + 45:
            return False
        return True

    def ctrl_span(qid: str) -> float | None:
        if not ctrl_allowed(qid):
            return None
        birth, _death = ctrl_birth_death(qid)
        ys = ctrl_union_years(qid)
        if birth is not None and ys:
            return float(metrics(ys, birth, None)["output_span_after_45"])
        return None

    def ctrl_n45(qid: str) -> float | None:
        if not ctrl_allowed(qid):
            return None
        birth, _death = ctrl_birth_death(qid)
        if birth is None:
            return None
        ys = ctrl_union_years(qid)
        if not ys:
            return None
        return float(metrics(ys, birth, None)["n_works_after_45"])

    wear_conf = {
        r["person_id"]: (r.get("confidence") or "").strip().lower()
        for r in _read(WEARER_CURATED)
    }

    def primary_ok(pid: str, bucket: str) -> tuple[bool, str]:
        occ = (census.get(pid, {}).get("occupation_class") or "").lower()
        if bucket in PRIMARY_EXCLUDE_BUCKETS:
            return False, f"exclude_bucket_{bucket}"
        for sub in PRIMARY_EXCLUDE_CLASS_SUBSTR:
            if sub in occ:
                return False, f"exclude_class_{sub}"
        if wear_conf.get(pid) == "low":
            return False, "exclude_coverage_low_pin"
        # output_span_after_45 is undefined when death precedes age 45
        # (treat span locked at 0 vs long-lived controls → pure survival artifact).
        c = census.get(pid, {})
        by = _y(c.get("birth_year"))
        dy = _y(c.get("death_year"))
        if by is not None and dy is not None and dy < by + 45:
            return False, "exclude_death_before_45"
        return True, ""

    pair_rows = []
    for pid in sorted(labor_ids):
        wr = wear_by_pid[pid]
        m = matches.get(pid, {})
        bucket = m.get("occupation_bucket", "") or census.get(pid, {}).get("occupation_bucket", "")
        t_span = _f(wr.get("output_span_after_45"))
        t_n = _f(wr.get("n_works_after_45"))
        has_t = int(wr.get("n_works_dated") or 0) > 0 and t_span is not None
        qids = [q for q in (m.get("matched_control_qids") or "").split(";") if q]
        spans = []
        ns = []
        used = []
        for q in qids:
            s = ctrl_span(q)
            if s is None:
                continue
            spans.append(s)
            ns.append(ctrl_n45(q) or 0.0)
            used.append(q)
        med_s = statistics.median(spans) if spans else None
        med_n = statistics.median(ns) if ns else None
        delta_s = (t_span - med_s) if (has_t and med_s is not None) else None
        delta_n = (t_n - med_n) if (has_t and med_n is not None and t_n is not None) else None
        ok, excl = primary_ok(pid, bucket)
        in_primary = delta_s is not None and ok
        pair_rows.append(
            {
                "person_id": pid,
                "qid": wr.get("qid", ""),
                "occupation_bucket": bucket,
                "macro_region": m.get("macro_region", ""),
                "match_level": m.get("match_level", ""),
                "n_works_dated": wr.get("n_works_dated", ""),
                "t_output_span_after_45": "" if not has_t else t_span,
                "t_n_works_after_45": "" if not has_t else t_n,
                "t_output_span_after_evidence": wr.get("output_span_after_evidence", ""),
                "t_n_works_after_evidence": wr.get("n_works_after_evidence", ""),
                "n_ctrl_with_works": len(spans),
                "med_c_output_span_after_45": "" if med_s is None else med_s,
                "med_c_n_works_after_45": "" if med_n is None else med_n,
                "delta_span": "" if delta_s is None else round(delta_s, 2),
                "delta_n_works": "" if delta_n is None else round(delta_n, 2),
                "ctrl_qids_used": ";".join(used),
                "in_primary_delta": "1" if in_primary else "0",
                "primary_exclude_reason": excl if delta_s is not None and not ok else (
                    "no_delta" if delta_s is None else ""
                ),
            }
        )
    _write(OUT_PAIR, pair_rows, list(pair_rows[0].keys()))

    primary_rows = [r for r in pair_rows if r["in_primary_delta"] == "1"]
    appendix_rows = [r for r in pair_rows if r.get("delta_span") != "" and r["in_primary_delta"] != "1"]
    deltas_n = [_f(r["delta_span"]) for r in primary_rows]
    deltas_n = [d for d in deltas_n if d is not None]
    dn_ok = [_f(r["delta_n_works"]) for r in primary_rows]
    dn_ok = [d for d in dn_ok if d is not None]
    med, lo, hi = boot_median(deltas_n)
    med_n, lo_n, hi_n = boot_median(dn_ok)
    all_d = [_f(r["delta_span"]) for r in pair_rows]
    all_d = [d for d in all_d if d is not None]
    med_a, lo_a, hi_a = boot_median(all_d)

    summary = [
        {
            "estimand": "output_span_after_45",
            "n_pairs_with_delta": len(deltas_n),
            "n_treat_with_works": n_with,
            "median_delta": "" if not deltas_n else round(med, 2),
            "boot95_lo": "" if not deltas_n else round(lo, 2),
            "boot95_hi": "" if not deltas_n else round(hi, 2),
            "n_ge_5": sum(1 for d in deltas_n if d >= 5),
            "n_ge_15": sum(1 for d in deltas_n if d >= 15),
            "share_delta_gt_0": "" if not deltas_n else round(sum(1 for d in deltas_n if d > 0) / len(deltas_n), 3),
            "sesoi5": (
                "PASS_RAW"
                if deltas_n and med >= 5 and lo >= 0
                else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi15": "PASS_RAW" if deltas_n and med >= 15 else "FAIL_OR_UNAVAILABLE",
            "note": "primary=textual brain-work; artisan/painter appendix; elig_false ctrls dropped",
        },
        {
            "estimand": "n_works_after_45",
            "n_pairs_with_delta": len(dn_ok),
            "n_treat_with_works": n_with,
            "median_delta": "" if not dn_ok else round(med_n, 2),
            "boot95_lo": "" if not dn_ok else round(lo_n, 2),
            "boot95_hi": "" if not dn_ok else round(hi_n, 2),
            "n_ge_5": "",
            "n_ge_15": "",
            "share_delta_gt_0": "" if not dn_ok else round(sum(1 for d in dn_ok if d > 0) / len(dn_ok), 3),
            "sesoi5": "N/A_count",
            "sesoi15": "N/A_count",
            "note": "exploratory count delta on primary subset",
        },
        {
            "estimand": "output_span_after_45_appendix_all_deltas",
            "n_pairs_with_delta": len(all_d),
            "n_treat_with_works": n_with,
            "median_delta": "" if not all_d else round(med_a, 2),
            "boot95_lo": "" if not all_d else round(lo_a, 2),
            "boot95_hi": "" if not all_d else round(hi_a, 2),
            "n_ge_5": sum(1 for d in all_d if d >= 5),
            "n_ge_15": sum(1 for d in all_d if d >= 15),
            "share_delta_gt_0": "" if not all_d else round(sum(1 for d in all_d if d > 0) / len(all_d), 3),
            "sesoi5": "APPENDIX_NOT_SESOI",
            "sesoi15": "APPENDIX_NOT_SESOI",
            "note": f"includes excluded visual cells n_excl={len(appendix_rows)}; not for SESOI",
        },
    ]
    _write(OUT_SUM, summary, list(summary[0].keys()))

    prim = summary[0]
    method = f"""# B1-Output estimand (corrected path, audit 2026-08-12)

**Date:** 2026-08-12 — outcome-aware overlay/exclude layer removed; dropped
death-tip pins restored (`b1_audit_restore_log_2026-08-12.csv`). The pass-era
output SESOI+5 PASS_RAW is **retracted** (see `docs/B1_CURATION_AUDIT_2026-08-12.md`).  
**Script:** `27_b1_output_estimand.py`  
**SESOI doc:** `docs/B1_OUTPUT_SESOI.md`

## Estimand

Among onsetish **textual** documentary wearers with dated works, relative to
region/occupation-matched **textual-authorship** controls:

> **Δ = T_output_span_after_45 − median(C_output_span_after_45)**

`output_span_after_45 = max(0, max(years≥birth+45) − (birth+45))` (0 if no post-45 years but has works).

Missing works ⇒ excluded from Δ (not coded as zero).  
Artisan/painter wearers and `output_eligible=False` controls are out of primary SESOI.

## Current primary result

| | |
|--|--|
| Treatments with dated works | {n_with} / {len(labor_ids)} |
| Primary pairs with Δ | {prim['n_pairs_with_delta']} |
| Median Δ (span years) | {prim['median_delta']} |
| Bootstrap 95% CI | [{prim['boot95_lo']}, {prim['boot95_hi']}] |
| share Δ>0 | {prim['share_delta_gt_0']} |
| SESOI +5 | {prim['sesoi5']} |
| SESOI +15 | {prim['sesoi15']} |
| Count Δ median (n_works after 45) | {summary[1]['median_delta']} |

## Caveats

1. P50/P800 is a thin proxy for “important output” (catalog bias; painters/clerics undercount).
2. n_pairs may be <<20 → SESOI verdict is **provisional** until densify / bibliography expands coverage.
3. Post-evidence span is reported per wearer but not used in primary Δ (controls lack onset).
4. Labor-year B1 remains separate (`25_b1_primary_estimand.py`).

## Next densify

1. SPARQL refresh for empty-QID wearers after QID fill.
2. Hand chronology for high-value letter producers without P50 (e.g. Strozzi letters).
3. P800-only sensitivity when n_p800 grows.
"""
    OUT_METHOD.write_text(method, encoding="utf-8")
    log(
        f"SUMMARY span n={prim['n_pairs_with_delta']} med={prim['median_delta']} "
        f"CI=[{prim['boot95_lo']},{prim['boot95_hi']}] "
        f"sesoi5={prim['sesoi5']} sesoi15={prim['sesoi15']}"
    )


if __name__ == "__main__":
    main()
