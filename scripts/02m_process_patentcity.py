#!/usr/bin/env python3
"""Process PatentCity shard(s) — chunked read, city-level patent counts."""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

USECOLS = ["publication_date", "country_code", "loc_city", "is_inv"]

GLASS_CITIES = {
    "florence",
    "firenze",
    "venice",
    "venezia",
    "milan",
    "milano",
    "murano",
    "pisa",
    "nuremberg",
    "nurnberg",
    "nürnberg",
}

CONTROL_CITIES = {
    "paris",
    "bologna",
    "oxford",
    "cambridge",
    "cologne",
    "koln",
    "köln",
    "krakow",
    "kraków",
    "salamanca",
    "prague",
    "praha",
    "london",
}


def _find_shards() -> list[Path]:
    patterns = [
        str(DATA_RAW / "patentcity_v100rc7_*.csv"),
        str(ROOT.parent / "download_data" / "patentcity_v100rc7_*.csv"),
    ]
    files: list[Path] = []
    for pat in patterns:
        files.extend(Path(p) for p in glob.glob(pat))
    return sorted(set(files))


def _bucket_city(raw: str) -> tuple[str, str]:
    if pd.isna(raw):
        return "", "other"
    low = str(raw).strip().lower()
    if low in GLASS_CITIES:
        return low.replace("firenze", "florence").replace("venezia", "venice").replace("milano", "milan"), "glass"
    if low in CONTROL_CITIES:
        return low, "control"
    return "", "other"


def _year_from_pubdate(val) -> int | None:
    if pd.isna(val):
        return None
    text = re.sub(r"\D", "", str(val))
    if len(text) >= 4:
        year = int(text[:4])
        if 1800 <= year <= 2000:
            return year
    return None


def main() -> None:
    shards = _find_shards()
    if not shards:
        log("No patentcity_v100rc7_*.csv shards found", OUTPUT_LOGS / "fetch.log")
        return

    log(f"PatentCity: processing {len(shards)} shard(s)", OUTPUT_LOGS / "fetch.log")
    buckets: dict[tuple[str, str, int], int] = {}

    for shard in shards:
        for chunk in pd.read_csv(shard, usecols=USECOLS, chunksize=250_000, low_memory=False):
            chunk["year"] = chunk["publication_date"].map(_year_from_pubdate)
            chunk = chunk.dropna(subset=["year"])
            mapped = chunk["loc_city"].map(_bucket_city)
            chunk["city_bucket"] = mapped.map(lambda x: x[0])
            chunk["city_group"] = mapped.map(lambda x: x[1])
            chunk = chunk[chunk["city_group"].isin(["glass", "control"])]
            if chunk.empty:
                continue
            chunk["half_century"] = (chunk["year"] // 50) * 50
            grp = (
                chunk.groupby(["city_bucket", "city_group", "half_century"], as_index=False)
                .size()
                .rename(columns={"size": "patents"})
            )
            for row in grp.itertuples(index=False):
                key = (row.city_bucket, row.city_group, int(row.half_century))
                buckets[key] = buckets.get(key, 0) + int(row.patents)

    if not buckets:
        log("PatentCity: no glass/control city matches", OUTPUT_LOGS / "fetch.log")
        return

    rows = [
        {"city": k[0], "city_group": k[1], "half_century": k[2], "patents": v}
        for k, v in sorted(buckets.items())
    ]
    city_year = pd.DataFrame(rows)
    city_year.to_csv(DATA_PROCESSED / "patentcity_city_halfcentury.csv", index=False)

    summary_rows = []
    for period, label in [(1800, "1800-1849"), (1850, "1850-1899"), (1900, "1900-1949")]:
        sub = city_year[city_year["half_century"].between(period, period + 49)]
        glass = sub[sub["city_group"] == "glass"]["patents"].sum()
        ctrl = sub[sub["city_group"] == "control"]["patents"].sum()
        summary_rows.append(
            {
                "period": label,
                "glass_patents": int(glass),
                "control_patents": int(ctrl),
                "ratio_glass_to_control": round(glass / ctrl, 3) if ctrl else None,
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUTPUT_TABLES / "patentcity_glass_summary.csv", index=False)

    total_glass = city_year[city_year["city_group"] == "glass"]["patents"].sum()
    total_ctrl = city_year[city_year["city_group"] == "control"]["patents"].sum()
    log(
        f"PatentCity: glass={total_glass}, control={total_ctrl} "
        f"({len(shards)} shard(s)) -> {OUTPUT_TABLES / 'patentcity_glass_summary.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
