#!/usr/bin/env python3
"""Parse Knod (1899) biographical index to Bologna German Nation Acta citations."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

CANDIDATES = [
    DATA_RAW / "deutschestudent00knod_djvu.txt",
    ROOT.parent / "download_data" / "deutschestudent00knod_djvu.txt",
]

ACTA_RE = re.compile(r"(\d{1,3})\s*,\s*(\d{1,3})\.\s*(\d{4})\.")
ENTRY_RE = re.compile(r"^\s*(\d+)\.\s+([A-Za-zÀ-ÿ][^\n]{2,80})$")
CLERGY_RE = re.compile(r"\b(can\.|canonicus|magister|mgr\.|decanus|archidiac)\b", re.I)


def _find_file() -> Path | None:
    for path in CANDIDATES:
        if path.exists() and path.stat().st_size > 100_000:
            return path
    return None


def main() -> None:
    path = _find_file()
    if path is None:
        log("No deutschestudent00knod_djvu.txt found", OUTPUT_LOGS / "fetch.log")
        return

    citations = []
    entries = []
    current_entry = None

    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            entry_match = ENTRY_RE.match(stripped)
            if entry_match and not ACTA_RE.search(stripped):
                current_entry = {
                    "entry_no": int(entry_match.group(1)),
                    "header": entry_match.group(2).strip(),
                }
                entries.append(current_entry)
                continue

            for match in ACTA_RE.finditer(line):
                year = int(match.group(3))
                if not 1289 <= year <= 1562:
                    continue
                clergy = bool(CLERGY_RE.search(line))
                citations.append(
                    {
                        "acta_vol": int(match.group(1)),
                        "acta_page": int(match.group(2)),
                        "year": year,
                        "line": stripped[:300],
                        "clergy_title": clergy,
                        "entry_no": current_entry["entry_no"] if current_entry else np.nan,
                        "entry_header": current_entry["header"] if current_entry else "",
                    }
                )

    cites = pd.DataFrame(citations)
    cites.to_csv(DATA_PROCESSED / "bologna_acta_citations.csv", index=False)

    yearly = cites.groupby("year", as_index=False).agg(
        n_citations=("year", "size"),
        n_clergy=("clergy_title", "sum"),
    )
    yearly["clergy_share"] = yearly["n_clergy"] / yearly["n_citations"].replace(0, np.nan)
    yearly["half_century"] = (yearly["year"] // 50) * 50
    yearly.to_csv(OUTPUT_TABLES / "bologna_yearly_counts.csv", index=False)

    half = (
        yearly.groupby("half_century", as_index=False)
        .agg(n_citations=("n_citations", "sum"), n_clergy=("n_clergy", "sum"))
    )
    half["clergy_share"] = half["n_clergy"] / half["n_citations"].replace(0, np.nan)
    half.to_csv(OUTPUT_TABLES / "bologna_half_century_counts.csv", index=False)

    pre = yearly[yearly["year"] < 1300]
    post = yearly[yearly["year"] >= 1300]
    pre_n = pre["n_citations"].sum()
    post_n = post["n_citations"].sum()
    pre_clergy = pre["n_clergy"].sum()
    post_clergy = post["n_clergy"].sum()

    clergy_share_pre = pre_clergy / pre_n if pre_n else np.nan
    clergy_share_post = post_clergy / post_n if post_n else np.nan

    # First citation year per indexed person (proxy for nation enrollment)
    first_year = (
        cites.dropna(subset=["entry_no"])
        .sort_values("year")
        .groupby("entry_no", as_index=False)
        .first()[["entry_no", "year", "clergy_title"]]
    )
    first_year.to_csv(DATA_PROCESSED / "bologna_first_citation.csv", index=False)

    pre_first = first_year[first_year["year"] < 1300]
    post_first = first_year[first_year["year"] >= 1300]

    summary = pd.DataFrame(
        [
            {
                "test": "bologna_acta_volume_pre_vs_post_1300",
                "n_citations_pre": int(pre_n),
                "n_citations_post": int(post_n),
                "post_pre_ratio": round(post_n / pre_n, 4) if pre_n else np.nan,
                "clergy_share_pre": round(clergy_share_pre, 4),
                "clergy_share_post": round(clergy_share_post, 4),
                "clergy_share_diff_post_minus_pre": round(
                    clergy_share_post - clergy_share_pre, 4
                )
                if not np.isnan(clergy_share_pre) and not np.isnan(clergy_share_post)
                else np.nan,
                "n_persons_indexed": len(entries),
                "n_persons_with_acta_year": len(first_year),
                "n_first_pre_1300": len(pre_first),
                "n_first_post_1300": len(post_first),
            }
        ]
    )
    summary.to_csv(OUTPUT_TABLES / "bologna_summary.csv", index=False)

    log(
        f"Bologna Knod: {len(entries)} index entries, {len(cites)} acta citations, "
        f"pre1300={int(pre_n)} post1300={int(post_n)}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
