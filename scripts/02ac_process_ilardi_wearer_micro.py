#!/usr/bin/env python3
"""Micro panel: Ilardi-named spectacle wearers × Wikidata notable-work ages.

Experience-premium unlock predicts major works concentrate AFTER documented
wear/onset (late-career unlock). Near-work continuation predicts the opposite
or no late shift — wear mostly after peak output.

Uses curated birth/death as authority; Wikidata supplies P800+P577 when present.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, OUTPUT_LOGS, OUTPUT_TABLES
from _utils import log

CURATED = DATA_CURATED / "ilardi_named_wearers.csv"
OUT_WORKS = DATA_PROCESSED / "ilardi_wearer_notable_works.csv"
OUT_PERSON = DATA_PROCESSED / "ilardi_wearer_age_summary.csv"
OUT_TABLE = OUTPUT_TABLES / "ilardi_wearer_micro_panel.csv"
OUT_TEST = OUTPUT_TABLES / "ilardi_wearer_micro_ttests.csv"

BIRTH_QUERY = """
SELECT ?birthYear ?deathYear WHERE {{
  OPTIONAL {{ wd:{qid} wdt:P569 ?birth . BIND(YEAR(?birth) AS ?birthYear) }}
  OPTIONAL {{ wd:{qid} wdt:P570 ?death . BIND(YEAR(?death) AS ?deathYear) }}
}}
LIMIT 5
"""

WORKS_QUERY = """
SELECT ?work ?pubYear WHERE {{
  wd:{qid} wdt:P800 ?work .
  OPTIONAL {{
    ?work wdt:P577 ?pub .
    BIND(YEAR(?pub) AS ?y577)
  }}
  OPTIONAL {{
    ?work wdt:P571 ?inc .
    BIND(YEAR(?inc) AS ?y571)
  }}
  BIND(COALESCE(?y577, ?y571) AS ?pubYear)
}}
LIMIT 100
"""


def _proxy() -> str | None:
    return os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:12309"


def sparql_json(query: str, *, timeout: int = 90) -> dict:
    env = os.environ.copy()
    proxy = _proxy()
    if proxy:
        env["https_proxy"] = proxy
        env["HTTPS_PROXY"] = proxy
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
            "User-Agent: eyeglasses-hypothesis/1.6 (ilardi-wearer-micro)",
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


def _first_int(bindings: list[dict], key: str) -> int | None:
    for b in bindings:
        v = b.get(key, {})
        if isinstance(v, dict) and v.get("value") not in (None, ""):
            try:
                return int(float(v["value"]))
            except ValueError:
                continue
    return None


def fetch_birth_death(qid: str) -> tuple[int | None, int | None]:
    data = sparql_json(BIRTH_QUERY.format(qid=qid))
    bindings = data.get("results", {}).get("bindings", [])
    return _first_int(bindings, "birthYear"), _first_int(bindings, "deathYear")


def fetch_works(qid: str) -> list[tuple[str, int | None]]:
    data = sparql_json(WORKS_QUERY.format(qid=qid))
    out: list[tuple[str, int | None]] = []
    for b in data.get("results", {}).get("bindings", []):
        work = b.get("work", {}).get("value", "")
        pub = b.get("pubYear", {}).get("value")
        pub_i = int(float(pub)) if pub not in (None, "") else None
        if work:
            out.append((work, pub_i))
    return out


def pick_birth(curated_birth, wd_birth) -> int | None:
    """Prefer curated; accept WD only if historically plausible for this panel."""
    if curated_birth is not None and not (isinstance(curated_birth, float) and np.isnan(curated_birth)):
        return int(curated_birth)
    if wd_birth is not None and 1100 <= wd_birth <= 1600:
        return wd_birth
    return None


def main() -> None:
    curated = pd.read_csv(CURATED)
    work_rows: list[dict] = []
    person_rows: list[dict] = []

    for _, p in curated.iterrows():
        qid = str(p.get("wikidata_qid") or "").strip()
        if not qid or qid.lower() == "nan":
            person_rows.append(
                {
                    "person_id": p["person_id"],
                    "name": p["name"],
                    "wikidata_qid": "",
                    "status": "no_qid",
                    "n_works": 0,
                }
            )
            continue

        try:
            wd_birth, wd_death = fetch_birth_death(qid)
            works = fetch_works(qid)
            log(
                f"fetched {qid} birth={wd_birth} works={len(works)}",
                OUTPUT_LOGS / "ilardi_wearer_micro.log",
            )
        except Exception as e:
            log(f"FAIL {qid}: {e}", OUTPUT_LOGS / "ilardi_wearer_micro.log")
            person_rows.append(
                {
                    "person_id": p["person_id"],
                    "name": p["name"],
                    "wikidata_qid": qid,
                    "status": f"fetch_fail:{type(e).__name__}",
                    "n_works": 0,
                }
            )
            continue

        birth = pick_birth(p.get("birth_year"), wd_birth)
        death = (
            int(p["death_year"])
            if pd.notna(p.get("death_year"))
            else (wd_death if wd_death and 1100 <= wd_death <= 1700 else None)
        )
        evid_year = int(p["evidence_year"]) if pd.notna(p["evidence_year"]) else None
        evid_age = (evid_year - birth) if (birth is not None and evid_year is not None) else None
        if evid_age is None and pd.notna(p.get("evidence_age")):
            evid_age = int(p["evidence_age"])

        ages: list[int] = []
        n_before = n_after = 0
        seen = set()
        for work, pub in works:
            if pub is None or birth is None:
                continue
            key = (work, pub)
            if key in seen:
                continue
            seen.add(key)
            age = pub - birth
            if age < 10 or age > 95:
                continue
            after = bool(evid_age is not None and age >= evid_age)
            if after:
                n_after += 1
            else:
                n_before += 1
            ages.append(age)
            work_rows.append(
                {
                    "person_id": p["person_id"],
                    "name": p["name"],
                    "wikidata_qid": qid,
                    "birth_year": birth,
                    "death_year": death,
                    "evidence_year": evid_year,
                    "evidence_age": evid_age,
                    "evidence_type": p["evidence_type"],
                    "occupation_class": p["occupation_class"],
                    "confidence": p["confidence"],
                    "work": work,
                    "pub_year": pub,
                    "age_at_work": age,
                    "work_after_evidence": after,
                }
            )

        person_rows.append(
            {
                "person_id": p["person_id"],
                "name": p["name"],
                "wikidata_qid": qid,
                "status": "ok",
                "birth_year": birth,
                "death_year": death,
                "evidence_year": evid_year,
                "evidence_age": evid_age,
                "evidence_type": p["evidence_type"],
                "occupation_class": p["occupation_class"],
                "confidence": p["confidence"],
                "n_works": len(ages),
                "age_first_work": min(ages) if ages else np.nan,
                "age_last_work": max(ages) if ages else np.nan,
                "age_mean_work": float(np.mean(ages)) if ages else np.nan,
                "n_works_before_evidence": n_before,
                "n_works_after_evidence": n_after,
                "share_works_after_evidence": (
                    n_after / (n_before + n_after) if (n_before + n_after) else np.nan
                ),
            }
        )

    works_df = pd.DataFrame(work_rows)
    persons = pd.DataFrame(person_rows)
    works_df.to_csv(OUT_WORKS, index=False)
    persons.to_csv(OUT_PERSON, index=False)

    core = persons[
        (persons["status"] == "ok")
        & (persons["confidence"].isin(["high", "medium"]))
        & (persons["n_works"] > 0)
        & (~persons["evidence_type"].astype(str).str.contains("literary_depiction", na=False))
    ].copy()
    core.to_csv(OUT_TABLE, index=False)

    test_rows = []
    if len(core):
        shares = core["share_works_after_evidence"].dropna()
        mean_share = float(shares.mean()) if len(shares) else np.nan
        deltas = (core["age_mean_work"] - core["evidence_age"]).dropna()
        mean_delta = float(deltas.mean()) if len(deltas) else np.nan
        test_rows.append(
            {
                "test": "ilardi_wearer_share_notable_works_after_evidence",
                "metric": "mean_share_after",
                "value": round(mean_share, 4) if pd.notna(mean_share) else np.nan,
                "p_value": np.nan,
                "n_persons": len(core),
                "n_works_before": int(core["n_works_before_evidence"].sum()),
                "n_works_after": int(core["n_works_after_evidence"].sum()),
                "note": (
                    "Share of Wikidata P800 works dated at/after documented wear/ownership evidence; "
                    "B predicts high share (late unlock); A predicts low"
                ),
            }
        )
        test_rows.append(
            {
                "test": "ilardi_wearer_mean_work_age_minus_evidence_age",
                "metric": "mean_age_delta",
                "value": round(mean_delta, 4) if pd.notna(mean_delta) else np.nan,
                "p_value": np.nan,
                "n_persons": int(deltas.shape[0]),
                "n_works_before": int(core["n_works_before_evidence"].sum()),
                "n_works_after": int(core["n_works_after_evidence"].sum()),
                "note": (
                    "Mean(age_at_P800) - evidence_age; negative => notable works earlier than wear onset"
                ),
            }
        )
    pd.DataFrame(test_rows).to_csv(OUT_TEST, index=False)
    log(
        f"wearer micro: persons={len(persons)} works={len(works_df)} core={len(core)} -> {OUT_TABLE}",
        OUTPUT_LOGS / "ilardi_wearer_micro.log",
    )
    print(persons.to_string(index=False))
    if test_rows:
        print(pd.DataFrame(test_rows).to_string(index=False))
    else:
        print("No core persons with P800 works yet.")


if __name__ == "__main__":
    main()
