#!/usr/bin/env python3
"""Download public datasets (OWID, europop, WIAG, Wikidata). Skips existing files."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_LOGS, ROOT
from _utils import log

DOWNLOAD_DIR = ROOT.parent / "download_data"

# (filename, url)
URLS = [
    (
        "manuscript-production-century.csv",
        "https://ourworldindata.org/grapher/manuscript-production-century.csv"
        "?v=1&csvType=full&useColumnShortNames=false",
    ),
    (
        "production-printed-books-half-century.csv",
        "https://ourworldindata.org/grapher/production-printed-books-half-century.csv"
        "?v=1&csvType=full&useColumnShortNames=false",
    ),
    (
        "cross-country-literacy-rates.csv",
        "https://ourworldindata.org/grapher/cross-country-literacy-rates.csv"
        "?v=1&csvType=full&useColumnShortNames=false",
    ),
    (
        "europop.csv",
        "https://cdn.jsdelivr.net/gh/mdlincoln/europop@master/data-raw/europop.csv",
    ),
    (
        "city_coords.csv",
        "https://cdn.jsdelivr.net/gh/mdlincoln/europop@master/data-raw/city_coords.csv",
    ),
    (
        "wiag_bishops_persons.csv",
        "https://wiag-vocab.adw-goe.de/bischof/data?format=csv",
    ),
]

WIKIDATA_QUERY = """
SELECT ?person ?personLabel ?birth ?death ?birthplaceLabel WHERE {
  ?person wdt:P31 wd:Q5;
          wdt:P106/wdt:P279* wd:Q82594;
          wdt:P27/wdt:P30 wd:Q46.
  OPTIONAL { ?person wdt:P569 ?birth. }
  OPTIONAL { ?person wdt:P570 ?death. }
  OPTIONAL { ?person wdt:P19 ?birthplace. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def curl_download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-fsSL", "--max-time", "300", "-o", str(dest), url]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        log(f"Downloaded {dest.name} ({dest.stat().st_size // 1024} KB)", OUTPUT_LOGS / "fetch.log")
        return True
    except subprocess.CalledProcessError as exc:
        log(f"Failed {dest.name}: {exc.stderr.decode()[:200]}", OUTPUT_LOGS / "fetch.log")
        return False


def fetch_wikidata() -> None:
    dest = DOWNLOAD_DIR / "wikidata_european_scholars.csv"
    if dest.exists() and dest.stat().st_size > 50_000:
        return
    import urllib.parse
    import urllib.request

    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": WIKIDATA_QUERY})
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/csv",
            "User-Agent": "eyeglasses-hypothesis/1.0 (research pipeline)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            dest.write_bytes(resp.read())
        log(f"Downloaded {dest.name}", OUTPUT_LOGS / "fetch.log")
    except Exception as exc:
        log(f"Wikidata fetch failed: {exc}", OUTPUT_LOGS / "fetch.log")


def main() -> None:
    for name, url in URLS:
        curl_download(url, DOWNLOAD_DIR / name)
    fetch_wikidata()


if __name__ == "__main__":
    main()
