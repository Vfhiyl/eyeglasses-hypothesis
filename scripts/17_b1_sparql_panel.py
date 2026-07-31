#!/usr/bin/env python3
"""B1 panel: batch SPARQL P800 (+ optional merge with prior rows) via https_proxy if set.

Does not start/stop the local gateway — set https_proxy yourself if using it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES
from _utils import log

CURATED = DATA_CURATED / "ilardi_named_wearers.csv"
OUT_WORKS = DATA_PROCESSED / "b1_wearer_entity_works.csv"
OUT_PERSON = OUTPUT_TABLES / "b1_wearer_entity_panel.csv"
OUT_TEST = OUTPUT_TABLES / "b1_wearer_entity_ttests.csv"
RAW = DATA_RAW / "wikidata_entity_wearers"
CHUNK = 8


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
            "User-Agent: eyeglasses-hypothesis/b1-sparql-panel",
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
        raise RuntimeError((r.stderr or r.stdout or f"exit {r.returncode}")[-500:])
    return json.loads(r.stdout)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    wear = pd.read_csv(CURATED)
    qids = sorted({str(q).strip() for q in wear.wikidata_qid.dropna() if str(q).startswith("Q")})
    log(f"qids={len(qids)} https_proxy={os.environ.get('https_proxy')}", OUTPUT_LOGS / "b1_sparql_panel.log")

    bindings: list[dict] = []
    for i in range(0, len(qids), CHUNK):
        chunk = qids[i : i + CHUNK]
        vals = " ".join(f"wd:{q}" for q in chunk)
        query = f"""
SELECT ?person ?work ?pubYear WHERE {{
  VALUES ?person {{ {vals} }}
  ?person wdt:P800 ?work .
  OPTIONAL {{ ?work wdt:P577 ?pub . BIND(YEAR(?pub) AS ?y577) }}
  OPTIONAL {{ ?work wdt:P571 ?inc . BIND(YEAR(?inc) AS ?y571) }}
  BIND(COALESCE(?y577, ?y571) AS ?pubYear)
}}
LIMIT 2000
"""
        for attempt in range(1, 5):
            try:
                data = sparql(query)
                b = data.get("results", {}).get("bindings", [])
                bindings.extend(b)
                (RAW / f"sparql_p800_chunk_{i}.json").write_text(json.dumps(data))
                log(f"chunk {chunk} bindings={len(b)}", OUTPUT_LOGS / "b1_sparql_panel.log")
                break
            except Exception as e:  # noqa: BLE001
                log(f"FAIL chunk {chunk} attempt {attempt}: {e}", OUTPUT_LOGS / "b1_sparql_panel.log")
                time.sleep(3 * attempt)
        time.sleep(1.2)

    rows = []
    for b in bindings:
        person = b.get("person", {}).get("value", "").rsplit("/", 1)[-1]
        work = b.get("work", {}).get("value", "").rsplit("/", 1)[-1]
        pub = b.get("pubYear", {}).get("value")
        rows.append(
            {
                "qid": person,
                "work_qid": work,
                "pub_year": int(float(pub)) if pub not in (None, "") else None,
            }
        )
    wdf = pd.DataFrame(rows).drop_duplicates(subset=["qid", "work_qid", "pub_year"])

    person_rows = []
    work_out = []
    for _, p in wear.iterrows():
        qid = str(p.wikidata_qid).strip() if pd.notna(p.wikidata_qid) else ""
        if not qid.startswith("Q"):
            person_rows.append(
                {
                    "person_id": p.person_id,
                    "name": p["name"],
                    "qid": "",
                    "status": "no_qid",
                    "confidence": p.confidence,
                    "n_works": 0,
                    "n_before": 0,
                    "n_after": 0,
                    "share_after": np.nan,
                    "mean_age_delta": np.nan,
                }
            )
            continue
        birth = int(p.birth_year) if pd.notna(p.birth_year) and str(p.birth_year) != "" else None
        evid_year = int(p.evidence_year) if pd.notna(p.evidence_year) else None
        evid_age = (
            int(float(p.evidence_age))
            if pd.notna(p.evidence_age) and str(p.evidence_age) != ""
            else ((evid_year - birth) if evid_year and birth else None)
        )
        sub = wdf[wdf.qid == qid] if len(wdf) else wdf
        ages: list[int] = []
        n_before = n_after = 0
        for _, w in sub.iterrows():
            if w.pub_year is None or birth is None or (isinstance(w.pub_year, float) and np.isnan(w.pub_year)):
                continue
            pub = int(w.pub_year)
            age = pub - birth
            if age < 10 or age > 95:
                continue
            after = bool(evid_age is not None and age >= evid_age)
            n_after += int(after)
            n_before += int(not after)
            ages.append(age)
            work_out.append(
                {
                    "person_id": p.person_id,
                    "name": p["name"],
                    "qid": qid,
                    "work_qid": w.work_qid,
                    "pub_year": pub,
                    "age_at_work": age,
                    "evidence_year": evid_year,
                    "evidence_age": evid_age,
                    "work_after_evidence": after,
                    "confidence": p.confidence,
                    "evidence_type": p.evidence_type,
                }
            )
        n = n_before + n_after
        person_rows.append(
            {
                "person_id": p.person_id,
                "name": p["name"],
                "qid": qid,
                "status": "ok",
                "birth_year": birth,
                "evidence_year": evid_year,
                "evidence_age": evid_age,
                "evidence_type": p.evidence_type,
                "confidence": p.confidence,
                "n_p800": len(sub),
                "n_works": n,
                "n_before": n_before,
                "n_after": n_after,
                "share_after": round(n_after / n, 4) if n else np.nan,
                "mean_age_delta": (
                    round(float(np.mean(ages)) - evid_age, 3) if ages and evid_age is not None else np.nan
                ),
            }
        )

    pdf = pd.DataFrame(person_rows)
    works = pd.DataFrame(work_out)
    works.to_csv(OUT_WORKS, index=False)
    pdf.to_csv(OUT_PERSON, index=False)
    core = pdf[
        (pdf.status == "ok")
        & (pdf.confidence.isin(["high", "medium"]))
        & (pdf.n_works > 0)
        & (~pdf.evidence_type.astype(str).str.contains("literary_depiction|medical_treatise", na=False))
    ]
    status = (
        "adequate_direction_sample"
        if len(core) >= 5
        else ("insufficient_but_growing" if len(core) else "insufficient")
    )
    tests = [
        {
            "test": "b1_sparql_share_p800_after_evidence",
            "metric": "mean_share_after",
            "value": round(float(core.share_after.mean()), 4) if len(core) else np.nan,
            "n_persons": len(core),
            "n_works_before": int(core.n_before.sum()) if len(core) else 0,
            "n_works_after": int(core.n_after.sum()) if len(core) else 0,
            "b1_status": status,
        }
    ]
    pd.DataFrame(tests).to_csv(OUT_TEST, index=False)
    print(pdf[pdf.n_works > 0].to_string(index=False))
    print("CORE", len(core), status)


if __name__ == "__main__":
    main()
