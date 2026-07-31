#!/usr/bin/env python3
"""Region-aware rematch for B1 controls + refresh near-work overlays.

Problem: birth±10 + occupation alone pairs Datini with Shen Wansan, Cederni with
Korean clerks, etc. Pre-reg (B1_CONTROL_POOL.md) required macro-region match.

Steps:
  1. SPARQL P27/P19 country for matched-pool QIDs + treatment QIDs
  2. Map to macro region
  3. Rematch: occ bucket + birth±10 + region
  4. Recompute ya45 + reuse P50 years for overlay
  5. Write matches_region / summary / overlay / update verdict note
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
from _paths import DATA_CURATED, OUTPUT_TABLES, OUTPUT_LOGS

CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
CONTROLS = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
P50 = OUTPUT_TABLES / "b1_control_p50_years.csv"
P800 = OUTPUT_TABLES / "b1_control_p800_years.csv"
OUT_REGION = OUTPUT_TABLES / "b1_person_macro_region.csv"
OUT_MATCH = OUTPUT_TABLES / "b1_roster_control_matches_region.csv"
OUT_SUM = OUTPUT_TABLES / "b1_roster_control_summary_region.csv"
OUT_OVERLAY = OUTPUT_TABLES / "b1_roster_control_p50_overlay_region.csv"
OUT_NOTE = OUTPUT_TABLES / "b1_region_rematch_2026-07-31.md"
LOG = OUTPUT_LOGS / "b1_region_rematch.log"

# reuse occ mapping from script 22
TREAT_TO_CTRL = {
    "humanist": ["humanist"],
    "letter_writer": ["humanist"],
    "cleric": ["cleric", "humanist"],
    "ruler_cleric": ["cleric", "ruler", "humanist"],
    "ruler": ["ruler", "humanist"],
    "merchant": ["merchant", "humanist"],
    "clerk": ["clerk", "humanist"],
    "admin": ["clerk", "admin", "humanist"],
    "artisan": ["artisan", "humanist"],
    "other": ["humanist", "other"],
}

# country QID → macro region
COUNTRY_REGION = {
    # Italy & predecessors
    "Q38": "italy",
    "Q172579": "italy",  # Kingdom of Italy
    "Q170174": "italy",  # Papal States
    "Q154849": "italy",  # Republic of Florence
    "Q49485": "italy",  # Republic of Venice
    "Q164987": "italy",  # Duchy of Milan
    "Q165154": "italy",  # Kingdom of Naples
    "Q180393": "italy",  # Republic of Genoa
    "Q679561": "italy",  # Siena
    "Q46587": "italy",  # Mantua
    "Q189148": "italy",  # Ferrara
    "Q80702": "italy",  # Urbino
    # England / Britain
    "Q21": "england",
    "Q145": "england",
    "Q174193": "england",  # United Kingdom of GB and Ireland
    "Q161885": "england",  # Kingdom of England
    "Q230791": "england",  # Kingdom of Great Britain
    # Iberia
    "Q29": "iberia",
    "Q45": "iberia",
    "Q45670": "iberia",  # Kingdom of Portugal
    "Q217196": "iberia",  # Crown of Castile
    "Q199442": "iberia",  # Crown of Aragon
    "Q200314": "iberia",  # Kingdom of Navarre
    # France
    "Q142": "france",
    "Q70972": "france",  # Kingdom of France
    # HRE / German lands / Low Countries (group for matching rulers/merchants)
    "Q183": "hre",
    "Q12548": "hre",  # Holy Roman Empire
    "Q55": "hre",  # Netherlands
    "Q31": "hre",  # Belgium
    "Q39": "hre",  # Switzerland
    "Q40": "hre",  # Austria
    "Q36": "other",  # Poland
    "Q28": "other",  # Hungary
    "Q159": "other",  # Russia
    "Q148": "other",  # China
    "Q884": "other",  # South Korea
    "Q17": "other",  # Japan
}

BIRTH_WINDOW = 10
CHUNK = 20
SLEEP = 3.0
UA = "eyeglasses-hypothesis/b1-region-rematch"


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
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def sparql(query: str, timeout: int = 150) -> dict:
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
        env=os.environ.copy(),
        check=False,
    )
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError((r.stderr or r.stdout or "")[-400:])
    return json.loads(r.stdout)


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
    if c.startswith("strata_cleric") or s == "sparql_cleric":
        return "cleric"
    if c.startswith("strata_admin") or s == "sparql_admin":
        return "admin"
    if source == "v2" or c.startswith("writer_poet"):
        return "humanist"
    occ = c.rsplit("_", 1)[-1] if c.startswith("wd_scholar_") else c
    if occ in {"philosopher", "historian", "writer", "scholar", "professor", "mathematician"}:
        return "humanist"
    if occ == "theologian":
        return "cleric"
    return "other"


def ya45(b: int | None, d: int | None) -> float | None:
    if b is None or d is None or d < b:
        return None
    return float(max(0, (d - b) - 45))


def fetch_countries(qids: list[str]) -> dict[str, list[str]]:
    """qid -> list of country QIDs from P27 and P19→country."""
    out: dict[str, list[str]] = defaultdict(list)
    if OUT_REGION.exists():
        for r in _read(OUT_REGION):
            if r.get("country_qids"):
                out[r["qid"]] = [x for x in r["country_qids"].split(";") if x]

    missing = [q for q in qids if q not in out]
    run = os.environ.get("B1_SPARQL", "1").strip() not in {"0", "false", "no"}
    log(f"region fetch have={len(qids)-len(missing)} missing={len(missing)} run={run}")
    if not run or not missing:
        return dict(out)

    for i in range(0, len(missing), CHUNK):
        chunk = missing[i : i + CHUNK]
        vals = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
SELECT ?person ?country WHERE {{
  VALUES ?person {{ {vals} }}
  {{
    ?person wdt:P27 ?country .
  }} UNION {{
    ?person wdt:P19 ?place .
    ?place wdt:P17 ?country .
  }}
}}
LIMIT 5000
"""
        try:
            data = sparql(query)
            for b in data.get("results", {}).get("bindings", []):
                pid = b["person"]["value"].rsplit("/", 1)[-1]
                cid = b["country"]["value"].rsplit("/", 1)[-1]
                out[pid].append(cid)
            log(f"  chunk {i//CHUNK+1}: {len(chunk)} ok")
        except Exception as e:
            log(f"  chunk FAIL: {e}")
        time.sleep(SLEEP)
    return {q: sorted(set(cs)) for q, cs in out.items()}


def macro_region(country_qids: list[str], fallback: str = "unknown") -> str:
    regions = []
    for c in country_qids:
        if c in COUNTRY_REGION:
            regions.append(COUNTRY_REGION[c])
    if not regions:
        return fallback
    # prefer italy/england/iberia/france/hre over other
    for pref in ("italy", "england", "iberia", "france", "hre"):
        if pref in regions:
            return pref
    return regions[0]


# Controls whose WD P27/P19 mix misassigns macro-region (e.g. Venice-born French careers)
CTRL_REGION_OVERRIDE = {
    "Q234816": "france",  # Christine de Pizan: Venice birth → Italy; adult career France
    "Q160341": "england",  # Edward IV: WD mix can mis-map to france
    "Q239337": "france",  # Philip the Good: WD citizenship often blank/unknown in our fetch
    "Q1379932": "france",  # Gilbert of Montpensier
    "Q1313351": "france",  # Louis II de la Trémoille
    "Q728786": "france",  # Charles of Valois, Duke of Berry (d.1472)
}

# Force occupation bucket when WD scholar cohort under-classifies clerics/rulers
CTRL_BUCKET_OVERRIDE = {
    "Q380652": "cleric",  # Giles of Viterbo (Augustinian cardinal)
    "Q435853": "cleric",  # Thomas Cajetan (Dominican cardinal)
}


# Hand overrides for known treatments without/weak WD citizenship
TREAT_REGION_OVERRIDE = {
    "petrarch": "italy",
    "filelfo": "italy",
    "datini": "italy",
    "alessandra_strozzi": "italy",
    "strozzi_filippo": "italy",
    "ardingelli_bese": "italy",
    "cederni": "italy",
    "ammannati": "italy",
    "tranchedini": "italy",
    "sforza_francesco": "italy",
    "bianca_maria": "italy",
    "gonzaga_ludovico": "italy",
    "barbara_brandenburg": "italy",  # active Mantua
    "policastro": "italy",
    "arduino_baiso": "italy",
    "lorenzo_medici": "italy",
    "leo_x": "italy",
    "sixtus_iv": "italy",
    "pius_ii": "italy",
    "lotto": "italy",
    "maurolico_francesco": "italy",
    "domenichi_ludovico": "italy",
    "spataro_giovanni": "italy",
    "spinelli_benedetto": "italy",
    "pirckheimer": "hre",
    "wolsey": "england",
    "wyatt_henry": "england",
    "henry_viii": "england",
    "azevedo_joao_porto": "iberia",
    "nuno_fernandes": "iberia",
    "neri_mici": "italy",
    "bartholomeus_padua": "italy",
    "nicolas_de_baye": "france",
    "philippe_le_hardi": "france",
    "charles_orleans": "france",
    "rene_ii_lorraine": "france",
}


def main() -> None:
    census = {r["person_id"]: r for r in _read(CENSUS)}
    controls = {c["qid"]: c for c in _read(CONTROLS)}
    onset = [
        r
        for r in census.values()
        if r.get("in_onsetish_treatment") == "True" and _y(r.get("birth_year")) is not None
    ]

    # QIDs to resolve
    treat_q = {}
    for path in (DATA_CURATED / "ilardi_named_wearers.csv", DATA_CURATED / "b1_named_wearers_candidates_new.csv"):
        for r in _read(path):
            q = (r.get("wikidata_qid") or "").strip()
            if q.startswith("Q"):
                treat_q[r["person_id"]] = q

    # Prefer controls already near treatment births to limit SPARQL volume:
    # all controls with birth in [min_t-15, max_t+15]
    births = [_y(r["birth_year"]) for r in onset]
    bmin, bmax = min(x for x in births if x), max(x for x in births if x)
    wear_ctrl = set(treat_q.values())
    for path in (DATA_CURATED / "ilardi_named_wearers.csv", DATA_CURATED / "b1_named_wearers_candidates_new.csv"):
        for r in _read(path):
            q = (r.get("wikidata_qid") or "").strip()
            if q.startswith("Q"):
                wear_ctrl.add(q)
    pool = []
    for q, c in controls.items():
        if q in wear_ctrl or str(c.get("is_known_wearer", "")).lower() in {"true", "1", "yes"}:
            continue
        b, d = _y(c["birth"]), _y(c["death"])
        if b is None or d is None:
            continue
        if b < bmin - 15 or b > bmax + 15:
            continue
        pool.append(q)

    need = set(pool) | set(treat_q.values())
    countries = fetch_countries(sorted(need))

    # write region table
    region_rows = []
    for q in sorted(need):
        cs = countries.get(q, [])
        reg = CTRL_REGION_OVERRIDE.get(q, macro_region(cs))
        region_rows.append(
            {
                "qid": q,
                "country_qids": ";".join(cs),
                "macro_region": reg,
            }
        )
    _write(OUT_REGION, region_rows, ["qid", "country_qids", "macro_region"])
    region_of = {r["qid"]: r["macro_region"] for r in region_rows}

    # build control rows with bucket+region
    ctrl_rows = []
    for q in pool:
        c = controls[q]
        b, d = _y(c["birth"]), _y(c["death"])
        reg = region_of.get(q, "unknown")
        if reg == "unknown":
            continue  # cannot region-match unknowns into primary set
        bk = CTRL_BUCKET_OVERRIDE.get(
            q, control_bucket(c.get("cohort", ""), c.get("source", ""))
        )
        ctrl_rows.append(
            {
                "qid": q,
                "name": c["name"],
                "birth_year": b,
                "death_year": d,
                "bucket": bk,
                "region": reg,
                "years_alive_after_45": ya45(b, d),
            }
        )
    log(f"region-known controls in birth window: {len(ctrl_rows)}")

    # load work years
    p50 = {}
    if P50.exists():
        for r in _read(P50):
            ys = [_y(x) for x in (r.get("years") or "").split(";")]
            p50[r["qid"]] = [y for y in ys if y is not None]
    p800 = {}
    if P800.exists():
        for r in _read(P800):
            ys = [_y(x) for x in (r.get("years") or "").split(";")]
            p800[r["qid"]] = [y for y in ys if y is not None]

    matches = []
    for t in onset:
        tb = _y(t["birth_year"])
        assert tb is not None
        t_bucket = t.get("occupation_bucket") or "other"
        t_region = TREAT_REGION_OVERRIDE.get(
            t["person_id"],
            region_of.get(treat_q.get(t["person_id"], ""), "unknown"),
        )
        pref = TREAT_TO_CTRL.get(t_bucket, ["humanist"])
        primary, relaxed = [pref[0]], pref[1:]
        chosen = []
        match_level = "unmatched"
        for level, buckets, require_region in (
            ("occ+birth+region", primary, True),
            ("occ_relaxed+region", relaxed, True),
            ("occ+birth_anyregion", primary, False),
            ("birth_only_region", None, True),
            ("birth_only", None, False),
        ):
            if buckets == []:
                continue
            cands = []
            for c in ctrl_rows:
                if abs(c["birth_year"] - tb) > BIRTH_WINDOW:
                    continue
                if buckets is not None and c["bucket"] not in buckets:
                    continue
                if require_region and t_region != "unknown" and c["region"] != t_region:
                    continue
                cands.append(c)
            if cands:
                chosen = sorted(cands, key=lambda c: abs(c["birth_year"] - tb))[:12]
                match_level = level
                break
        if not chosen:
            matches.append(
                {
                    "person_id": t["person_id"],
                    "name": t["name"],
                    "birth_year": tb,
                    "occupation_bucket": t_bucket,
                    "macro_region": t_region,
                    "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                    "years_after_evidence_t": t.get("years_after_evidence", ""),
                    "n_matched_controls": 0,
                    "median_years_alive_after_45_c": "",
                    "delta_ya45": "",
                    "match_status": "unmatched",
                    "match_level": "unmatched",
                    "matched_control_qids": "",
                    "control_regions": "",
                }
            )
            continue
        c_ya = [c["years_alive_after_45"] for c in chosen if c["years_alive_after_45"] is not None]
        med = statistics.median(c_ya) if c_ya else None
        t_ya = _f(t.get("years_alive_after_45"))
        delta = (t_ya - med) if (t_ya is not None and med is not None) else None
        matches.append(
            {
                "person_id": t["person_id"],
                "name": t["name"],
                "birth_year": tb,
                "occupation_bucket": t_bucket,
                "macro_region": t_region,
                "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                "years_after_evidence_t": t.get("years_after_evidence", ""),
                "n_matched_controls": len(chosen),
                "median_years_alive_after_45_c": med if med is not None else "",
                "delta_ya45": round(delta, 2) if delta is not None else "",
                "match_status": "matched",
                "match_level": match_level,
                "matched_control_qids": ";".join(c["qid"] for c in chosen),
                "control_regions": ";".join(sorted({c["region"] for c in chosen})),
            }
        )

    _write(
        OUT_MATCH,
        matches,
        [
            "person_id",
            "name",
            "birth_year",
            "occupation_bucket",
            "macro_region",
            "years_alive_after_45_t",
            "years_after_evidence_t",
            "n_matched_controls",
            "median_years_alive_after_45_c",
            "delta_ya45",
            "match_status",
            "match_level",
            "matched_control_qids",
            "control_regions",
        ],
    )

    matched = [m for m in matches if m["match_status"] == "matched"]
    strict = [m for m in matched if "region" in m["match_level"] and "anyregion" not in m["match_level"]]
    deltas = [_f(m["delta_ya45"]) for m in strict]
    deltas_n = [d for d in deltas if d is not None]
    summary = [
        {
            "n_onsetish_with_birth": len(onset),
            "n_matched": len(matched),
            "n_strict_region": len(strict),
            "n_unmatched": sum(1 for m in matches if m["match_status"] != "matched"),
            "match_levels": ";".join(
                f"{k}:{sum(1 for m in matched if m['match_level']==k)}"
                for k in sorted({m["match_level"] for m in matched})
            ),
            "median_delta_ya45_strict_region": statistics.median(deltas_n) if deltas_n else "",
            "sesoi5_strict": (
                "PASS_RAW" if deltas_n and statistics.median(deltas_n) >= 5 else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi15_strict": (
                "PASS_RAW" if deltas_n and statistics.median(deltas_n) >= 15 else "FAIL_OR_UNAVAILABLE"
            ),
            "caveat": "Strict = occ+birth+macro_region (or occ_relaxed+region). WD P27/P19 mapping incomplete.",
        }
    ]
    _write(OUT_SUM, summary, list(summary[0].keys()))
    log(
        f"matched={len(matched)} strict_region={len(strict)} "
        f"med_delta_ya45={summary[0]['median_delta_ya45_strict_region']} levels={summary[0]['match_levels']}"
    )

    # P50/P800 overlay on strict region matches
    overlay = []
    work_deltas = []
    for m in strict:
        t = census[m["person_id"]]
        tb, td = _y(t["birth_year"]), _y(t["death_year"])
        try:
            evid = int(float(t["evidence_year"]))
            ya = float(t["years_after_evidence"])
            t_last = min(evid + ya, td) if td is not None else evid + ya
            t_work = max(0.0, t_last - (tb + 45)) if tb is not None else None
        except (TypeError, ValueError):
            t_work = None
        c_works = []
        for q in m["matched_control_qids"].split(";"):
            if not q:
                continue
            cb = _y(controls[q]["birth"])
            cd = _y(controls[q]["death"])
            ys = p50.get(q) or p800.get(q) or []
            if not ys or cb is None:
                continue
            lo, hi = cb + 15, (cd + 5) if cd else cb + 95
            ys2 = [y for y in ys if lo <= y <= hi]
            if ys2:
                c_works.append(max(0.0, max(ys2) - (cb + 45)))
        med_c = statistics.median(c_works) if c_works else None
        delta = (t_work - med_c) if (t_work is not None and med_c is not None) else None
        if delta is not None:
            work_deltas.append(delta)
        overlay.append(
            {
                "person_id": m["person_id"],
                "macro_region": m["macro_region"],
                "match_level": m["match_level"],
                "t_work_after_45": t_work if t_work is not None else "",
                "n_ctrl_with_works": len(c_works),
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
            "macro_region",
            "match_level",
            "t_work_after_45",
            "n_ctrl_with_works",
            "med_c_work_after_45",
            "delta",
            "years_after_evidence",
        ],
    )
    if work_deltas:
        log(
            f"work overlay n={len(work_deltas)} median={statistics.median(work_deltas)} "
            f"ge5={sum(d>=5 for d in work_deltas)} ge15={sum(d>=15 for d in work_deltas)}"
        )
    else:
        log("work overlay n=0")

    note = f"""# Region-aware rematch (2026-07-31)

## Why

Birth+occupation matching alone produced absurd pairs (e.g. Datini↔Shen Wansan).
Pre-reg required macro-region. This pass enforces it.

## Results

| | |
|--|--|
| Onsetish with birth | {len(onset)} |
| Any match | {len(matched)} |
| **Strict region match** | **{len(strict)}** |
| Unmatched | {summary[0]['n_unmatched']} |
| Match levels | {summary[0]['match_levels']} |
| Median Δ ya45 (strict) | {summary[0]['median_delta_ya45_strict_region']} |
| SESOI +5 / +15 ya45 | {summary[0]['sesoi5_strict']} / {summary[0]['sesoi15_strict']} |
| Work-proxy overlay n | {len(work_deltas)} |
| Work-proxy median Δ | {statistics.median(work_deltas) if work_deltas else 'NA'} |

## Files

- `{OUT_MATCH.name}`
- `{OUT_SUM.name}`
- `{OUT_OVERLAY.name}`
- `{OUT_REGION.name}`

## Read

Region filter shrinks usable contrasts but **raises credibility**. Prefer these tables over non-region matches for any claim language.
"""
    OUT_NOTE.write_text(note)
    log(f"wrote {OUT_NOTE}")


if __name__ == "__main__":
    main()
