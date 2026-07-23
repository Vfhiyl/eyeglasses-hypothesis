#!/usr/bin/env python3
"""Process SDBM CSV exports (Place or Provenance + Manuscript Date) into panels."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log, normalize_city

DATE_RANGE_RE = re.compile(r"(\d{3,4})\s+to\s+(\d{3,4})", re.IGNORECASE)
FILE_RE = re.compile(
    r"sdbm_([a-z]+)_1200_1500(?:_(?P<field>provenance))?\ .csv$".replace(" ", ""),
    re.IGNORECASE,
)
FILE_RE = re.compile(r"sdbm_([a-z]+)_1200_1500(?:_(provenance))?\.csv$", re.IGNORECASE)

CANDIDATE_DIRS = [ROOT.parent / "download_data", DATA_RAW]

LOCAL_PRE = (1200, 1285)
LOCAL_POST = (1300, 1385)


def _find_exports() -> list[tuple[str, str, Path]]:
    """Return (city, search_field, path) with download_data preferred."""
    by_key: dict[tuple[str, str], Path] = {}
    for d in CANDIDATE_DIRS:
        if not d.exists():
            continue
        for path in sorted(d.glob("sdbm_*_1200_1500*.csv")):
            m = FILE_RE.search(path.name)
            if not m:
                continue
            city = m.group(1).title()
            field = m.group(2) or "place"
            key = (city, field)
            if key not in by_key or d.name == "download_data":
                by_key[key] = path
    return sorted((city, field, p) for (city, field), p in by_key.items())


def _parse_year_range(text: str) -> tuple[int | None, int | None]:
    if not text or pd.isna(text):
        return None, None
    m = DATE_RANGE_RE.search(str(text))
    if not m:
        return None, None
    y0, y1 = int(m.group(1)), int(m.group(2))
    if y0 > y1:
        y0, y1 = y1, y0
    return y0, y1


def process_file(city: str, search_field: str, path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df["search_city"] = city
    df["search_field"] = search_field
    df["source_file"] = path.name
    df["date_start"], df["date_end"] = zip(*df["dates"].map(_parse_year_range))
    df["date_mid"] = (df["date_start"] + df["date_end"]) / 2
    df["century"] = (df["date_mid"] // 100 * 100).astype("Int64")
    df["halfcentury"] = (df["date_mid"] // 50 * 50).astype("Int64")
    df["folios_n"] = pd.to_numeric(df.get("folios"), errors="coerce")
    df["spans_1300"] = (df["date_start"] < 1300) & (df["date_end"] >= 1300)
    df["entirely_pre_1300"] = df["date_end"] <= 1300
    df["entirely_post_1300"] = df["date_start"] >= 1300
    df["city_label"] = normalize_city(city)
    return df


def _local_window_counts(df: pd.DataFrame) -> dict:
    pre = df[(df["date_mid"] >= LOCAL_PRE[0]) & (df["date_mid"] < LOCAL_PRE[1])]
    post = df[(df["date_mid"] >= LOCAL_POST[0]) & (df["date_mid"] < LOCAL_POST[1])]
    n_pre, n_post = len(pre), len(post)
    return {
        "local_pre_1200_1285": n_pre,
        "local_post_1300_1385": n_post,
        "local_post_over_pre": round(n_post / n_pre, 4) if n_pre > 0 else np.nan,
        "local_folios_pre": float(pre["folios_n"].sum()) if len(pre) else np.nan,
        "local_folios_post": float(post["folios_n"].sum()) if len(post) else np.nan,
    }


def main() -> None:
    exports = _find_exports()
    if not exports:
        log("No sdbm_*_1200_1500*.csv found", OUTPUT_LOGS / "fetch.log")
        return

    all_frames: list[pd.DataFrame] = []
    summary_rows: list[dict] = []
    halfcentury_rows: list[dict] = []

    for city, search_field, path in exports:
        df = process_file(city, search_field, path)
        all_frames.append(df)

        parsed = int(df["date_mid"].notna().sum())
        pre = int((df["date_mid"] < 1300).sum())
        post = int((df["date_mid"] >= 1300).sum())
        local = _local_window_counts(df.dropna(subset=["date_mid"]))

        by_half = (
            df.dropna(subset=["halfcentury"])
            .groupby("halfcentury", as_index=False)
            .agg(entries=("id", "count"), folios_sum=("folios_n", "sum"))
            .sort_values("halfcentury")
        )
        for _, r in by_half.iterrows():
            halfcentury_rows.append(
                {
                    "city": city,
                    "search_field": search_field,
                    "halfcentury_start": int(r["halfcentury"]),
                    "entries": int(r["entries"]),
                    "folios_sum": float(r["folios_sum"]) if pd.notna(r["folios_sum"]) else np.nan,
                }
            )

        peak = by_half.sort_values("entries", ascending=False).head(1)
        peak_half = int(peak["halfcentury"].iloc[0]) if len(peak) else np.nan
        peak_n = int(peak["entries"].iloc[0]) if len(peak) else 0

        field_note = "Provenance" if search_field == "provenance" else "Place"
        summary_rows.append(
            {
                "city": city,
                "search_field": search_field,
                "source_file": path.name,
                "n_entries": len(df),
                "n_date_parsed": parsed,
                "n_mid_pre_1300": pre,
                "n_mid_post_1300": post,
                "n_spans_1300_breakpoint": int(df["spans_1300"].sum()),
                "n_entirely_pre_1300": int(df["entirely_pre_1300"].sum()),
                "folios_sum": float(df["folios_n"].sum(skipna=True)),
                "peak_halfcentury": peak_half,
                "peak_entries": peak_n,
                "post_pre_ratio_mid": round(post / pre, 2) if pre > 0 else np.nan,
                **local,
                "note": f"SDBM {field_note}+ManuscriptDate; mid=(start+end)/2",
            }
        )

    combined = pd.concat(all_frames, ignore_index=True)
    combined.to_csv(DATA_PROCESSED / "sdbm_entries_parsed.csv", index=False)

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUTPUT_TABLES / "sdbm_city_summary.csv", index=False)

    halfcentury = pd.DataFrame(halfcentury_rows)
    halfcentury.to_csv(OUTPUT_TABLES / "sdbm_by_halfcentury.csv", index=False)

    # Paris Place vs Provenance comparison
    paris = summary[summary["city"].str.lower() == "paris"].copy()
    if len(paris) >= 2:
        paris.to_csv(OUTPUT_TABLES / "sdbm_paris_place_vs_provenance.csv", index=False)

    pre_post_rows = []
    for _, row in summary.iterrows():
        pre_post_rows.append(
            {
                "test": f"sdbm_{row['city'].lower()}_{row['search_field']}_entries_pre_vs_post_1300",
                "search_field": row["search_field"],
                "n_pre_1300": row["n_mid_pre_1300"],
                "n_post_1300": row["n_mid_post_1300"],
                "local_pre_1200_1285": row.get("local_pre_1200_1285"),
                "local_post_1300_1385": row.get("local_post_1300_1385"),
                "local_post_over_pre": row.get("local_post_over_pre"),
                "note": row["note"],
            }
        )
    pd.DataFrame(pre_post_rows).to_csv(OUTPUT_TABLES / "sdbm_pre_post_summary.csv", index=False)

    log(
        f"SDBM: {len(exports)} export(s), {len(combined)} entries -> "
        f"{OUTPUT_TABLES / 'sdbm_city_summary.csv'}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
