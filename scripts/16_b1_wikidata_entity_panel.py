#!/usr/bin/env python3
"""B1 panel via Wikidata EntityData API (no SPARQL).

For each curated named wearer with a QID, fetch P800 notable works and
P577/P571 dates; summarize before/after documented wear evidence.
Also resolves birth/death when curated blanks exist.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES
from _utils import log

CURATED = DATA_CURATED / "ilardi_named_wearers.csv"
RAW_DIR = DATA_RAW / "wikidata_entity_wearers"
OUT_WORKS = DATA_PROCESSED / "b1_wearer_entity_works.csv"
OUT_PERSON = OUTPUT_TABLES / "b1_wearer_entity_panel.csv"
OUT_TEST = OUTPUT_TABLES / "b1_wearer_entity_ttests.csv"
UA = "eyeglasses-hypothesis/b1-entity (research; github.com/Vfhiyl/eyeglasses-hypothesis)"


def fetch_entity(qid: str, retries: int = 4) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / f"{qid}.json"
    if cache.exists() and cache.stat().st_size > 100:
        return json.loads(cache.read_text())
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    last = ""
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            cache.write_bytes(data)
            return json.loads(data)
        except Exception as e:  # noqa: BLE001
            last = str(e)
            time.sleep(2.0 * attempt)
    raise RuntimeError(f"{qid}: {last}")


def year_from_time(t: str | None) -> int | None:
    if not t or not isinstance(t, str) or len(t) < 5:
        return None
    # +1364-00-00T00:00:00Z
    try:
        return int(t[1:5])
    except ValueError:
        return None


def claim_years(entity: dict, prop: str) -> list[int]:
    out: list[int] = []
    for c in entity.get("claims", {}).get(prop, []):
        snak = c.get("mainsnak", {})
        dv = snak.get("datavalue", {}).get("value")
        if isinstance(dv, dict) and "time" in dv:
            y = year_from_time(dv.get("time"))
            if y:
                out.append(y)
    return out


def p800_work_ids(entity: dict) -> list[str]:
    ids: list[str] = []
    for c in entity.get("claims", {}).get("P800", []):
        snak = c.get("mainsnak", {})
        dv = snak.get("datavalue", {}).get("value")
        if isinstance(dv, dict) and dv.get("id"):
            ids.append(dv["id"])
    return ids


def work_year(work_entity: dict) -> int | None:
    for prop in ("P577", "P571"):
        ys = claim_years(work_entity, prop)
        if ys:
            return ys[0]
    return None


def main() -> None:
    wear = pd.read_csv(CURATED)
    wear = wear[wear["wikidata_qid"].notna() & (wear["wikidata_qid"].astype(str).str.len() > 1)].copy()
    work_rows: list[dict] = []
    person_rows: list[dict] = []

    for _, p in wear.iterrows():
        qid = str(p["wikidata_qid"]).strip()
        try:
            bundle = fetch_entity(qid)
            ent = bundle["entities"][qid]
            time.sleep(0.6)
        except Exception as e:  # noqa: BLE001
            log(f"FAIL person {qid}: {e}", OUTPUT_LOGS / "b1_entity_panel.log")
            person_rows.append(
                {
                    "person_id": p["person_id"],
                    "name": p["name"],
                    "qid": qid,
                    "status": f"fetch_fail:{type(e).__name__}",
                    "n_works": 0,
                }
            )
            continue

        births = claim_years(ent, "P569")
        deaths = claim_years(ent, "P570")
        birth = int(p["birth_year"]) if pd.notna(p.get("birth_year")) else (births[0] if births else None)
        death = int(p["death_year"]) if pd.notna(p.get("death_year")) else (deaths[0] if deaths else None)
        evid_year = int(p["evidence_year"]) if pd.notna(p.get("evidence_year")) else None
        evid_age = (
            int(p["evidence_age"])
            if pd.notna(p.get("evidence_age"))
            else ((evid_year - birth) if (evid_year and birth) else None)
        )

        ages: list[int] = []
        n_before = n_after = 0
        for wid in p800_work_ids(ent):
            try:
                wb = fetch_entity(wid)
                went = wb["entities"][wid]
                time.sleep(0.35)
            except Exception as e:  # noqa: BLE001
                log(f"FAIL work {wid}: {e}", OUTPUT_LOGS / "b1_entity_panel.log")
                continue
            pub = work_year(went)
            if pub is None or birth is None:
                continue
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
                    "qid": qid,
                    "work_qid": wid,
                    "pub_year": pub,
                    "age_at_work": age,
                    "evidence_year": evid_year,
                    "evidence_age": evid_age,
                    "work_after_evidence": after,
                    "confidence": p["confidence"],
                    "evidence_type": p["evidence_type"],
                }
            )

        n = n_before + n_after
        person_rows.append(
            {
                "person_id": p["person_id"],
                "name": p["name"],
                "qid": qid,
                "status": "ok",
                "birth_year": birth,
                "death_year": death,
                "evidence_year": evid_year,
                "evidence_age": evid_age,
                "evidence_type": p["evidence_type"],
                "occupation_class": p["occupation_class"],
                "confidence": p["confidence"],
                "n_works": n,
                "n_before": n_before,
                "n_after": n_after,
                "share_after": round(n_after / n, 4) if n else np.nan,
                "age_first_work": min(ages) if ages else np.nan,
                "age_last_work": max(ages) if ages else np.nan,
                "age_mean_work": round(float(np.mean(ages)), 3) if ages else np.nan,
                "mean_age_delta": (
                    round(float(np.mean(ages)) - evid_age, 3)
                    if ages and evid_age is not None
                    else np.nan
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

    tests = []
    if len(core):
        tests.append(
            {
                "test": "b1_entity_share_p800_after_evidence",
                "metric": "mean_share_after",
                "value": round(float(core["share_after"].mean()), 4),
                "n_persons": len(core),
                "n_works_before": int(core["n_before"].sum()),
                "n_works_after": int(core["n_after"].sum()),
                "decision_rule": "n_core>=5 direction; n_core>=20 B1 claim",
                "b1_status": (
                    "adequate_direction_sample"
                    if len(core) >= 5
                    else "insufficient_hunt_more"
                ),
                "note": "EntityData P800+P577/P571; late-unlock predicts high share_after",
            }
        )
        tests.append(
            {
                "test": "b1_entity_mean_age_delta",
                "metric": "mean_age_delta",
                "value": round(float(core["mean_age_delta"].mean()), 4),
                "n_persons": int(core["mean_age_delta"].notna().sum()),
                "n_works_before": int(core["n_before"].sum()),
                "n_works_after": int(core["n_after"].sum()),
                "decision_rule": "n_core>=5 direction; n_core>=20 B1 claim",
                "b1_status": (
                    "adequate_direction_sample"
                    if len(core) >= 5
                    else "insufficient_hunt_more"
                ),
                "note": "mean(age_at_P800)-evidence_age; negative => works before wear evidence",
            }
        )
    pd.DataFrame(tests).to_csv(OUT_TEST, index=False)
    log(
        f"entity panel persons={len(persons)} works={len(works_df)} core={len(core)}",
        OUTPUT_LOGS / "b1_entity_panel.log",
    )
    print(persons.to_string(index=False))
    if tests:
        print(pd.DataFrame(tests).to_string(index=False))


if __name__ == "__main__":
    main()
