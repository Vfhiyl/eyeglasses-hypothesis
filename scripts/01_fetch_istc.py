#!/usr/bin/env python3
"""Fetch and clean ISTC incunabula data (city x year)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log, normalize_city, build_geonames_city_map

ISTC_URLS = [
    "https://zenodo.org/records/14644509/files/istc_core_imprints_1.0.csv?download=1",
    "https://bl.iro.bl.uk/downloads/30c74386-fc34-41b8-a9e5-d27ba96b0625/istc_core_imprints_1.0.csv",
]
LOCAL_CANDIDATES = [
    DATA_RAW / "istc_core_imprints_1.0.csv",
    ROOT.parent / "download_data" / "istc_core_imprints_1.0.csv",
    DATA_RAW / "istc_imprints_raw.csv",
]
SEED = DATA_RAW / "istc_city_year_seed.csv"
PUBLISHED = ROOT / "data/external/istc_city_totals_published.csv"
OUT_RAW = DATA_RAW / "istc_imprints_raw.csv"
OUT_CLEAN = DATA_PROCESSED / "istc_city_year.csv"


def find_local_istc() -> Path | None:
    for path in LOCAL_CANDIDATES:
        if path.exists() and path.stat().st_size > 100_000:
            return path
    return None


def try_download() -> bool:
    try:
        import requests
    except ImportError:
        return False
    for url in ISTC_URLS:
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 100_000:
                OUT_RAW.write_bytes(r.content)
                log(f"Downloaded ISTC from {url}", OUTPUT_LOGS / "fetch.log")
                return True
        except Exception as e:
            log(f"ISTC download failed ({url}): {e}", OUTPUT_LOGS / "fetch.log")
    return False


def _clean_place(raw: str) -> str:
    if pd.isna(raw):
        return ""
    s = str(raw).strip()
    s = re.sub(r"^\[+", "", s)
    s = re.sub(r"\]+$", "", s)
    s = s.split(",")[0].split(";")[0].strip()
    return s


def _extract_year(row: pd.Series) -> float:
    for col in ("date_of_item_single_date", "date_of_item_from", "imprint_date"):
        val = row.get(col)
        if pd.isna(val):
            continue
        text = str(val)
        if text.lower() in ("no date given", "nan", ""):
            continue
        m = re.search(r"(1[34]\d{2}|1500)", text)
        if m:
            return float(m.group(1))
    return float("nan")


def parse_istc_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    log(f"Parsing official ISTC: {len(df)} imprints from {path.name}", OUTPUT_LOGS / "fetch.log")

    if "imprint_place" in df.columns:
        df["place"] = df["imprint_place"].map(_clean_place)
        df["year"] = df.apply(_extract_year, axis=1)
        if "geonames_id" in df.columns:
            city_map = build_geonames_city_map(df)
            df["city"] = df["geonames_id"].map(city_map)
            missing = df["city"].isna()
            df.loc[missing, "city"] = df.loc[missing, "place"].map(
                lambda x: normalize_city(x) if x else x
            )
        else:
            df["city"] = df["place"].map(lambda x: normalize_city(x) if x else x)
    else:
        cols = {c.lower(): c for c in df.columns}
        place_col = next((cols[k] for k in cols if "place" in k), None)
        date_col = next(
            (cols[k] for k in cols if k in ("date_of_item_single_date", "imprint_date")),
            next((cols[k] for k in cols if "date" in k), None),
        )
        if not place_col or not date_col:
            raise ValueError(f"Cannot find place/date columns in {df.columns.tolist()}")
        df = df.rename(columns={place_col: "place", date_col: "year"})
        df["year"] = pd.to_numeric(
            df["year"].astype(str).str.extract(r"(1[34]\d{2}|1500)")[0], errors="coerce"
        )

        df["year"] = pd.to_numeric(
            df["year"].astype(str).str.extract(r"(1[34]\d{2}|1500)")[0], errors="coerce"
        )
        df["city"] = df["place"].map(lambda x: normalize_city(x) if x else x)

    out = df[["city", "year"]].copy()
    out = out[out["city"].astype(str).str.len() > 0]
    out = out.dropna(subset=["year"])
    out = out[out["year"].between(1450, 1500)]

    if "geonames_id" in df.columns:
        city_map = build_geonames_city_map(df)
        pd.DataFrame([
            {"geonames_id": gid, "city": city} for gid, city in city_map.items()
        ]).to_csv(DATA_PROCESSED / "istc_geonames_city_map.csv", index=False)

    agg = out.groupby(["city", "year"], as_index=False).size()
    agg = agg.rename(columns={"size": "book_count"})
    agg["source"] = "istc_official_2025"
    log(
        f"ISTC aggregated: {agg['book_count'].sum():.0f} editions, "
        f"{agg['city'].nunique()} cities, years {int(agg['year'].min())}-{int(agg['year'].max())}",
        OUTPUT_LOGS / "fetch.log",
    )
    return agg


def load_published_totals() -> pd.DataFrame:
    totals = pd.read_csv(PUBLISHED, comment="#").drop_duplicates(subset=["city"])
    rows = []
    for _, r in totals.iterrows():
        for year in range(1470, 1501):
            frac = (year - 1469) / 31
            rows.append({
                "city": r["city"],
                "year": year,
                "book_count": max(1, int(r["total_incunabula"] * frac / 31)),
                "source": "istc_published_totals",
            })
    log(f"Built ISTC proxy from {len(totals)} published city totals", OUTPUT_LOGS / "fetch.log")
    return pd.DataFrame(rows)


def main() -> None:
    clean = None
    local = find_local_istc()
    if local:
        try:
            clean = parse_istc_raw(local)
            if local != OUT_RAW:
                import shutil
                shutil.copy2(local, OUT_RAW)
        except Exception as e:
            log(f"Local ISTC parse failed: {e}", OUTPUT_LOGS / "fetch.log")

    if clean is None and not local:
        import os
        if os.environ.get("ALLOW_NETWORK_DOWNLOAD", "").lower() in ("1", "true", "yes"):
            if try_download() and OUT_RAW.exists():
                try:
                    clean = parse_istc_raw(OUT_RAW)
                except Exception as e:
                    log(f"Downloaded ISTC parse failed: {e}", OUTPUT_LOGS / "fetch.log")
        else:
            log("Skipping network download (set ALLOW_NETWORK_DOWNLOAD=1 to enable)", OUTPUT_LOGS / "fetch.log")

    if clean is None and PUBLISHED.exists():
        clean = load_published_totals()
    elif clean is None and SEED.exists():
        clean = pd.read_csv(SEED)
        log("Using ISTC seed fallback", OUTPUT_LOGS / "fetch.log")
    elif clean is None:
        raise FileNotFoundError("No ISTC source available")

    clean.to_csv(OUT_CLEAN, index=False)
    by_century = clean.copy()
    # period_start: 1452 -> 1400 (1400-1499). Do NOT use +100 end-label.
    by_century["century"] = (by_century["year"] // 100) * 100
    by_century["period_start"] = by_century["century"]
    by_century.groupby(["city", "century"], as_index=False)["book_count"].sum().to_csv(
        DATA_PROCESSED / "istc_city_century.csv", index=False
    )
    log(f"ISTC clean: {len(clean)} rows -> {OUT_CLEAN}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
