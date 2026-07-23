#!/usr/bin/env python3
"""Stream-parse Mapping Manuscript Migrations TTL for place-linked production events."""
from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

ZIP_CANDIDATES = [
    DATA_RAW / "mmm_data_v2.1.0.zip",
    DATA_RAW / "mmm_data_v2.2.0.zip",
    ROOT.parent / "download_data" / "mmm_data_v2.1.0.zip",
    ROOT.parent / "download_data" / "mmm_data_v2.2.0.zip",
]

TTL_FILES = ("mmm_places.ttl", "mmm_bibale.ttl", "mmm_bodley.ttl", "mmm_sdbm.ttl")

GLASS_KEYWORDS = (
    "florence",
    "firenze",
    "venice",
    "venezia",
    "vened",
    "milan",
    "milano",
    "mailand",
    "pisa",
    "murano",
    "nuremberg",
    "nürnberg",
    "nurnberg",
)

CONTROL_KEYWORDS = (
    "bologna",
    "bononia",
    "paris",
    "oxford",
    "cambridge",
    "cologne",
    "köln",
    "prague",
    "praha",
    "leipzig",
    "heidelberg",
    "basel",
    "erfurt",
    "padua",
    "padova",
    "rome",
    "roma",
    "salamanca",
    "krakow",
    "cracow",
)

PLACE_URI_RE = re.compile(r"ecrm:P7_took_place_at\s+(\S+)\s*;")
TIME_URI_RE = re.compile(r"ecrm:P4_has_time-span\s+(\S+)\s*;")
LABEL_RE = re.compile(r'skos:prefLabel\s+"([^"]+)"')
DECADE_RE = re.compile(r"mmms:decade\s+([^;]+);")
SUBJECT_RE = re.compile(r"^(\S+)\s")


def _find_zip() -> Path | None:
    for path in ZIP_CANDIDATES:
        if path.exists() and path.stat().st_size > 1_000_000:
            return path
    return None


def classify_label(label: str) -> str:
    low = label.lower()
    if any(k in low for k in GLASS_KEYWORDS):
        return "glass"
    if any(k in low for k in CONTROL_KEYWORDS):
        return "control"
    return "other"


def iter_blocks(lines):
    block: list[str] = []
    for line in lines:
        if not line.strip():
            if block:
                yield "".join(block)
                block = []
            continue
        block.append(line)
    if block:
        yield "".join(block)


def parse_places(blocks) -> dict[str, dict]:
    places: dict[str, dict] = {}
    for block in blocks:
        if "ecrm:E53_Place" not in block and "a ecrm:E53_Place" not in block:
            continue
        subject = SUBJECT_RE.match(block)
        if not subject:
            continue
        uri = subject.group(1).rstrip(".")
        label_match = LABEL_RE.search(block)
        if not label_match:
            continue
        label = label_match.group(1)
        places[uri] = {"label": label, "place_group": classify_label(label)}
    return places


def parse_decades(block: str) -> list[int]:
    decade_match = DECADE_RE.search(block)
    if not decade_match:
        return []
    return [int(x.strip()) for x in re.split(r",\s*", decade_match.group(1)) if x.strip().isdigit()]


def build_time_cache(zip_path: Path, member: str) -> dict[str, list[int]]:
    cache: dict[str, list[int]] = {}
    for block in iter_blocks(stream_ttl(zip_path, member)):
        if "ecrm:E52_Time-Span" not in block:
            continue
        subject = SUBJECT_RE.match(block)
        if not subject:
            continue
        uri = subject.group(1).rstrip(".")
        decades = parse_decades(block)
        if decades:
            cache[uri] = decades
    return cache


def process_place_events(zip_path: Path, member: str, places: dict, time_cache: dict[str, list[int]]):
    place_total = Counter()
    place_pre1300 = Counter()
    place_post1300 = Counter()
    group_total = Counter()
    group_pre1300 = Counter()
    group_post1300 = Counter()
    century_total = Counter()
    timed_events = 0

    for block in iter_blocks(stream_ttl(zip_path, member)):
        if "P7_took_place_at" not in block:
            continue

        place_match = PLACE_URI_RE.search(block)
        if not place_match:
            continue
        place_uri = place_match.group(1).rstrip(".")

        decades: list[int] = []
        time_match = TIME_URI_RE.search(block)
        if time_match:
            time_uri = time_match.group(1).rstrip(".")
            decades = time_cache.get(time_uri, [])

        label = places.get(place_uri, {}).get("label", place_uri)
        group = places.get(place_uri, {}).get("place_group", classify_label(label))

        place_total[place_uri] += 1
        group_total[group] += 1
        if decades:
            timed_events += 1
            for decade in decades:
                century_total[decade] += 1
            if any(d < 1300 for d in decades):
                place_pre1300[place_uri] += 1
                group_pre1300[group] += 1
            if any(d >= 1300 for d in decades):
                place_post1300[place_uri] += 1
                group_post1300[group] += 1

    return {
        "place_total": place_total,
        "place_pre1300": place_pre1300,
        "place_post1300": place_post1300,
        "group_total": group_total,
        "group_pre1300": group_pre1300,
        "group_post1300": group_post1300,
        "century_total": century_total,
        "timed_events": timed_events,
    }


def stream_ttl(zip_path: Path, member: str):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as handle:
            for raw in handle:
                yield raw.decode("utf-8", errors="replace")


def main() -> None:
    zip_path = _find_zip()
    if zip_path is None:
        log("No mmm_data zip found", OUTPUT_LOGS / "fetch.log")
        return

    with zipfile.ZipFile(zip_path) as zf:
        members = set(zf.namelist())

    place_blocks = list(iter_blocks(stream_ttl(zip_path, "mmm_places.ttl")))
    places = parse_places(place_blocks)
    pd.DataFrame(
        [{"place_uri": k, **v} for k, v in places.items()]
    ).to_csv(DATA_PROCESSED / "mmm_places_lookup.csv", index=False)

    time_cache: dict[str, list[int]] = {}
    place_total = Counter()
    place_pre1300 = Counter()
    place_post1300 = Counter()
    group_total = Counter()
    group_pre1300 = Counter()
    group_post1300 = Counter()
    century_total = Counter()
    timed_events = 0

    for ttl_name in ("mmm_bibale.ttl", "mmm_bodley.ttl", "mmm_sdbm.ttl"):
        if ttl_name not in members:
            continue
        log(f"MMM indexing times in {ttl_name}...", OUTPUT_LOGS / "fetch.log")
        time_cache.update(build_time_cache(zip_path, ttl_name))

    for ttl_name in ("mmm_bibale.ttl", "mmm_bodley.ttl", "mmm_sdbm.ttl"):
        if ttl_name not in members:
            continue
        log(f"MMM streaming {ttl_name}...", OUTPUT_LOGS / "fetch.log")
        stats = process_place_events(zip_path, ttl_name, places, time_cache)
        place_total.update(stats["place_total"])
        place_pre1300.update(stats["place_pre1300"])
        place_post1300.update(stats["place_post1300"])
        group_total.update(stats["group_total"])
        group_pre1300.update(stats["group_pre1300"])
        group_post1300.update(stats["group_post1300"])
        century_total.update(stats["century_total"])
        timed_events += stats["timed_events"]

    rows = []
    for uri, total in place_total.most_common():
        label = places.get(uri, {}).get("label", uri)
        group = places.get(uri, {}).get("place_group", classify_label(label))
        pre = place_pre1300.get(uri, 0)
        post = place_post1300.get(uri, 0)
        rows.append(
            {
                "place_uri": uri,
                "place_label": label,
                "place_group": group,
                "n_events_total": total,
                "n_events_pre1300": pre,
                "n_events_post1300": post,
            }
        )
    place_df = pd.DataFrame(rows)
    place_df.to_csv(OUTPUT_TABLES / "mmm_place_counts.csv", index=False)

    glass_pre = group_pre1300.get("glass", 0)
    glass_post = group_post1300.get("glass", 0)
    ctrl_pre = group_pre1300.get("control", 0)
    ctrl_post = group_post1300.get("control", 0)
    glass_total = group_total.get("glass", 0)
    ctrl_total = group_total.get("control", 0)

    summary = pd.DataFrame(
        [
            {
                "test": "mmm_production_events_glass_vs_control",
                "glass_pre_1300": glass_pre,
                "glass_post_1300": glass_post,
                "control_pre_1300": ctrl_pre,
                "control_post_1300": ctrl_post,
                "glass_total": glass_total,
                "control_total": ctrl_total,
                "glass_share_of_timed_events": round(glass_total / timed_events, 4) if timed_events else np.nan,
                "glass_post_pre_ratio": round(glass_post / glass_pre, 4) if glass_pre else np.nan,
                "control_post_pre_ratio": round(ctrl_post / ctrl_pre, 4) if ctrl_pre else np.nan,
                "glass_growth_over_control": round(
                    (glass_post / glass_pre) / (ctrl_post / ctrl_pre), 4
                )
                if glass_pre and ctrl_pre and ctrl_post
                else np.nan,
                "n_places_mapped": len(places),
                "n_events_with_place": sum(place_total.values()),
                "n_timed_events": timed_events,
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "mmm_summary.csv", index=False)

    pd.DataFrame(
        [{"century_start": k, "n_events": v} for k, v in sorted(century_total.items())]
    ).to_csv(OUTPUT_TABLES / "mmm_century_counts.csv", index=False)

    log(
        f"MMM: {len(places)} places, {sum(place_total.values())} place-tagged events, "
        f"glass pre/post={glass_pre}/{glass_post} control={ctrl_pre}/{ctrl_post}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
