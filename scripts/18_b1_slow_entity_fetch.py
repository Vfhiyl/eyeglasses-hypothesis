#!/usr/bin/env python3
"""Slow EntityData fetch for missing P800 work QIDs.

- Skips already-cached JSON
- Backs off hard on 403/429
- Uses https_proxy from the environment if set (does NOT start the gateway)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, DATA_RAW, OUTPUT_LOGS
from _utils import log

RAW = DATA_RAW / "wikidata_entity_wearers"
UA = "eyeglasses-hypothesis/b1-slow (research; polite)"
LOG = OUTPUT_LOGS / "b1_slow_entity_fetch.log"


def claim_ids(ent: dict, prop: str) -> list[str]:
    out: list[str] = []
    for c in ent.get("claims", {}).get(prop, []):
        dv = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(dv, dict) and dv.get("id"):
            out.append(dv["id"])
    return out


def fetch(qid: str) -> tuple[bool, str]:
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        (RAW / f"{qid}.json").write_bytes(data)
        return True, f"ok {len(data)}"
    except urllib.error.HTTPError as e:
        body = (e.read() or b"")[:180].decode("utf-8", "replace")
        return False, f"HTTP {e.code} {body}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    wear = pd.read_csv(DATA_CURATED / "ilardi_named_wearers.csv")
    needed: set[str] = set()
    for _, p in wear.iterrows():
        q = str(p.wikidata_qid).strip() if pd.notna(p.wikidata_qid) else ""
        if not q.startswith("Q"):
            continue
        path = RAW / f"{q}.json"
        if not path.exists():
            continue
        ent = json.loads(path.read_text())["entities"][q]
        needed.update(claim_ids(ent, "P800"))

    missing = sorted(
        w for w in needed if not (RAW / f"{w}.json").exists() or (RAW / f"{w}.json").stat().st_size < 100
    )
    msg0 = (
        f"proxy={os.environ.get('https_proxy')} P800_works={len(needed)} "
        f"cached={len(needed) - len(missing)} missing={len(missing)}"
    )
    print(msg0, flush=True)
    log(msg0, LOG)

    ok = fail = 0
    delay = 5.0
    for i, wid in enumerate(missing, 1):
        success, detail = fetch(wid)
        if success:
            ok += 1
            delay = max(4.0, delay * 0.92)
            line = f"[{i}/{len(missing)}] {wid} {detail} sleep={delay:.1f}s"
            print(line, flush=True)
            log(line, LOG)
            time.sleep(delay)
        else:
            fail += 1
            if "403" in detail or "Too Many" in detail or "429" in detail:
                delay = min(120.0, max(20.0, delay * 2.0))
            else:
                delay = min(90.0, delay + 3.0)
            line = f"[{i}/{len(missing)}] {wid} FAIL {detail[:140]} backoff={delay:.1f}s"
            print(line, flush=True)
            log(line, LOG)
            time.sleep(delay)

    still = sum(1 for w in needed if not (RAW / f"{w}.json").exists())
    done = f"DONE ok={ok} fail={fail} still_missing={still}"
    print(done, flush=True)
    log(done, LOG)


if __name__ == "__main__":
    main()
