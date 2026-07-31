#!/usr/bin/env python3
"""Build B1 control candidate pool v3 from v2 + Wikidata scholars.

Merges writer/poet v2 with stratified scholars (birth 1290–1550, ≤40/decade),
excluding known documentary wearers. Offline — no network.
"""
from __future__ import annotations

import csv
import re
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_PROCESSED, OUTPUT_TABLES

V2 = OUTPUT_TABLES / "b1_control_candidates_v2.csv"
SCHOLARS = DATA_PROCESSED / "wikidata_scholars_historical.csv"
OUT = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
CAP_PER_DECADE = 40
BIRTH_LO, BIRTH_HI = 1290, 1550


def _y(x: str | None) -> int | None:
    if x is None or str(x).strip() == "":
        return None
    try:
        return int(float(x))
    except ValueError:
        return None


def wearer_ids() -> tuple[set[str], set[str]]:
    qids: set[str] = set()
    names: set[str] = set()
    for path in (
        DATA_CURATED / "ilardi_named_wearers.csv",
        DATA_CURATED / "b1_named_wearers_candidates_new.csv",
    ):
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                q = (r.get("wikidata_qid") or "").strip()
                if q.startswith("Q"):
                    qids.add(q)
                n = (r.get("name") or "").strip().lower()
                if n:
                    names.add(n)
    return qids, names


def main() -> None:
    wear_q, wear_names = wearer_ids()
    by_q: dict[str, dict] = {}
    with V2.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            q = r["qid"].strip()
            if q in wear_q:
                continue
            by_q[q] = {
                "qid": q,
                "name": r["name"],
                "birth": r["birth"],
                "death": r["death"],
                "cohort": r.get("cohort", "writer_poet_v2"),
                "is_known_wearer": "False",
                "source": "v2",
            }

    decade_counts: collections.Counter[int] = collections.Counter()
    for r in by_q.values():
        b = _y(r["birth"])
        if b is not None:
            decade_counts[(b // 10) * 10] += 1

    added = 0
    with SCHOLARS.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            b, d = _y(r.get("birth_year")), _y(r.get("death_year"))
            if b is None or d is None or d < b:
                continue
            if b < BIRTH_LO or b > BIRTH_HI:
                continue
            if d - b > 100 or d - b < 20:
                continue
            m = re.search(r"(Q\d+)", r.get("person_uri") or "")
            if not m:
                continue
            qid = m.group(1)
            if qid in wear_q or qid in by_q:
                continue
            name = (r.get("name") or "").strip()
            if not name or name.lower() in wear_names:
                continue
            if name.startswith("Q") and name[1:].isdigit():
                continue
            dec = (b // 10) * 10
            if decade_counts[dec] >= CAP_PER_DECADE:
                continue
            occ = (r.get("occupation") or "scholar").strip() or "scholar"
            by_q[qid] = {
                "qid": qid,
                "name": name,
                "birth": str(b),
                "death": str(d),
                "cohort": f"wd_scholar_{dec}_{occ}",
                "is_known_wearer": "False",
                "source": "wikidata_scholars_historical",
            }
            decade_counts[dec] += 1
            added += 1

    fields = ["qid", "name", "birth", "death", "cohort", "is_known_wearer", "source"]
    rows = sorted(by_q.values(), key=lambda r: (_y(r["birth"]) or 0, r["qid"]))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    bs = [_y(r["birth"]) for r in rows]
    print(f"wrote {OUT} n={len(rows)} added_scholars={added} birth={min(bs)}-{max(bs)}")


if __name__ == "__main__":
    main()
