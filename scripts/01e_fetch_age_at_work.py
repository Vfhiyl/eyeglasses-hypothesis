#!/usr/bin/env python3
"""Fetch Wikidata age-at-notable-work rows (panel for experience-premium unlock).

Experience-premium unlock predicts age at major works rises after ~1300.
Near-work continuation predicts no systematic late shift.

Uses POST + HTTP/1.1 (GET+labels was hanging / HTTP2-framing under proxy).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW, OUTPUT_LOGS
from _utils import log

OUT_DIR = DATA_RAW / "wikidata_age_at_work"
OUT_DIR.mkdir(parents=True, exist_ok=True)

WINDOWS = [
    (1100, 1200),
    (1200, 1300),
    (1300, 1400),
    (1400, 1500),
    (1500, 1600),
    (1600, 1700),
]

# No label SERVICE: faster and more reliable through proxy.
QUERY = """
SELECT ?person ?birthYear ?work ?pubYear WHERE {{
  ?person wdt:P31 wd:Q5 ;
          wdt:P569 ?birth ;
          wdt:P800 ?work .
  ?work wdt:P577 ?pub .
  BIND(YEAR(?birth) AS ?birthYear)
  BIND(YEAR(?pub) AS ?pubYear)
  FILTER(?birthYear >= {lo} && ?birthYear < {hi})
  FILTER(?pubYear >= ?birthYear && ?pubYear <= ?birthYear + 90)
}}
LIMIT 5000
"""


def fetch_json(query: str, proxy: str, timeout: int = 180, retries: int = 3) -> dict:
    env = os.environ.copy()
    env["https_proxy"] = proxy
    env["HTTPS_PROXY"] = proxy
    last_err = ""
    for attempt in range(1, retries + 1):
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
                "User-Agent: eyeglasses-hypothesis/1.5 (age-at-work research)",
                "--data-urlencode",
                f"query={query.strip()}",
                "https://query.wikidata.org/sparql",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        last_err = (r.stderr or r.stdout or f"curl exit {r.returncode}")[-500:]
        time.sleep(2.0 * attempt)
    raise RuntimeError(last_err)


def main() -> None:
    proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") or "http://127.0.0.1:12309"
    all_rows: list[dict] = []
    for lo, hi in WINDOWS:
        q = QUERY.format(lo=lo, hi=hi)
        out = OUT_DIR / f"age_at_work_{lo}_{hi}.json"
        log(f"SPARQL age-at-work {lo}-{hi} via {proxy} (POST/http1.1)", OUTPUT_LOGS / "fetch.log")
        try:
            data = fetch_json(q, proxy=proxy)
        except Exception as e:
            log(f"FAIL {lo}-{hi}: {e}", OUTPUT_LOGS / "fetch.log")
            print(f"FAIL {lo}-{hi}: {e}")
            continue
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        bindings = data.get("results", {}).get("bindings", [])
        for b in bindings:
            try:
                by = int(float(b["birthYear"]["value"]))
                py = int(float(b["pubYear"]["value"]))
            except Exception:
                continue
            all_rows.append(
                {
                    "person": b.get("person", {}).get("value", ""),
                    "name": "",
                    "birth_year": by,
                    "work": b.get("work", {}).get("value", ""),
                    "work_label": "",
                    "pub_year": py,
                    "age_at_work": py - by,
                }
            )
        print(f"{lo}-{hi}: {len(bindings)} bindings")
        log(f"  got {len(bindings)} bindings ({lo}-{hi})", OUTPUT_LOGS / "fetch.log")
        time.sleep(1.0)

    merged = OUT_DIR / "age_at_work_all.json"
    merged.write_text(json.dumps(all_rows, ensure_ascii=False), encoding="utf-8")
    print(f"rows={len(all_rows)} -> {merged}")
    log(f"age_at_work total rows={len(all_rows)} -> {merged}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
