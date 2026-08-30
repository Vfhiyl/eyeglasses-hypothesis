#!/usr/bin/env python3
"""Knut Bosson episcopal activity series from SDHK (episode R1, 2026-08-12).

Episode: 1415 letter about BROKEN spectacles requesting a replacement
(census anchor; the sharpest deprivation-type anchor in the roster).
Question: does his documented charter activity (Swedish diplomatarium
regests) show interruption or decline around the episode, and does it
continue to old age?

Source: SDHK full dataset CSV (CC BY 4.0, version 2024-11), downloaded
2026-08-12 to data/raw/sdhk/sdhk_2411.csv (49.3 MB, 44,264 charters;
Latin-1, semicolon-separated). Machine web search hits a captcha, but the
whole register is an open downloadable dataset — no session needed.

Matching (checked 2026-08-12): during his episcopate (1391-1436) he is
the only "biskop Knut" of Linköping; regests before 1391 name him
"Knut Bosson" (canon/cantor/dean). Rules:
  * "knut bosson" / "knut boosson" in Summary or Author (any year), OR
  * "biskop knut" / "biscop knut" in Summary within 1391-1436
    (strict variant additionally requires "linkö" in the Summary).
  * issuer_like: Summary STARTS with his name/title (regest convention
    puts the actor first) — proxy for charters he issued vs mere mentions.

Outputs:
  outputs/tables/b1_bosson_sdhk_yearly.csv
  outputs/tables/b1_bosson_episode_method.md
"""
from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW, OUTPUT_TABLES

SDHK = DATA_RAW / "sdhk" / "sdhk_2411.csv"
OUT_CSV = OUTPUT_TABLES / "b1_bosson_sdhk_yearly.csv"
OUT_MD = OUTPUT_TABLES / "b1_bosson_episode_method.md"

BIRTH, DEATH = 1360, 1436
EPISODE = 1415  # broken-spectacles letter
WINDOW_LO, WINDOW_HI = 1387, 1436  # cantor period through death


def main() -> None:
    csv.field_size_limit(10**8)
    yearly: dict[int, dict[str, int]] = defaultdict(
        lambda: {"n_mentions_broad": 0, "n_mentions_strict": 0, "n_issuer_like": 0}
    )
    with SDHK.open(encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            m = re.match(r"(\d{4})", r.get("Date") or "")
            if not m:
                continue
            y = int(m.group(1))
            if not (WINDOW_LO <= y <= WINDOW_HI):
                continue
            s = (r.get("Summary") or "").lower()
            a = (r.get("Author") or "").lower()
            named = "knut bosson" in s or "knut boosson" in s or "knut bosson" in a
            titled = ("biskop knut" in s or "biscop knut" in s) and 1391 <= y <= 1436
            if not (named or titled):
                continue
            strict = named or (titled and ("linkö" in s or "linkö" in a))
            head = s[:30]
            issuer = bool(
                re.match(r"\s*(biskop knut|biscop knut|herr knut bosson|knut bosson)", head)
            )
            yearly[y]["n_mentions_broad"] += 1
            if strict:
                yearly[y]["n_mentions_strict"] += 1
            if issuer:
                yearly[y]["n_issuer_like"] += 1

    rows = []
    for y in range(WINDOW_LO, WINDOW_HI + 1):
        d = yearly.get(y, {"n_mentions_broad": 0, "n_mentions_strict": 0, "n_issuer_like": 0})
        rows.append(
            {
                "year": y,
                "age": y - BIRTH,
                "rel_to_episode": y - EPISODE,
                **d,
            }
        )
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    def win(lo: int, hi: int, key: str) -> tuple[int, float]:
        ys = [r for r in rows if lo <= r["year"] <= hi]
        tot = sum(r[key] for r in ys)
        return tot, round(tot / len(ys), 2) if ys else 0.0

    windows = [
        ("pre_episode_1405_1414", 1405, 1414),
        ("episode_year_1415", 1415, 1415),
        ("post_episode_1416_1425", 1416, 1425),
        ("late_life_1426_1436", 1426, 1436),
    ]
    lines_tbl = []
    for name, lo, hi in windows:
        tb, rb = win(lo, hi, "n_mentions_broad")
        ti, ri = win(lo, hi, "n_issuer_like")
        lines_tbl.append(f"| {name} | {tb} | {rb} | {ti} | {ri} |")

    md = "\n".join(
        [
            "# Knut Bosson broken-spectacles episode (R1) — SDHK charter series",
            "",
            "**Date:** 2026-08-12  ",
            "**Script:** `37_b1_bosson_sdhk_series.py` → `b1_bosson_sdhk_yearly.csv`  ",
            "**Source:** SDHK open dataset 2024-11 (CC BY 4.0), 44,264 charters;",
            "local copy `data/raw/sdhk/sdhk_2411.csv`.",
            "",
            "Episode anchor: 1415 letter about broken spectacles (census; Hildebrand",
            "C6). Bishop of Linköping 1391-1436; died 1436 (age ~76).",
            "",
            "| window | mentions (broad) | /yr | issuer-like | /yr |",
            "|--------|-----------------:|----:|------------:|----:|",
            *lines_tbl,
            "",
            "## Reading",
            "",
            "1. Charter-documented activity CONTINUES after the 1415 broken-",
            "   spectacles letter: dip in 1415-25, then back to ~4.9/yr in his",
            "   last decade (ages 66-76, active to death 1436).",
            "2. **Council of Constance confound:** 1414-1418 he attended the",
            "   Council (the broken-spectacles letter itself travels via Basel).",
            "   The 1415 trough is therefore primarily ABSENCE ABROAD, not",
            "   spectacle deprivation. Annual resolution cannot separate the two;",
            "   the episode supports late-life continuation, NOT a clean",
            "   deprivation test.",
            "3. This is regest-level documentation (mentions + issuer-like starts),",
            "   not autograph near-work; episcopal charters are chancery products.",
            "   It measures continued office activity, not personal reading/writing.",
            "4. Sub-annual resolution would need the printed SD side-series full",
            "   texts (1401-1420, digitized in SDHK full-text).",
            "5. Survival/registration drift across decades affects levels; compare",
            "   windows, not single years.",
            "",
            "Registry impact: episode `bosson_1415_broken` upgrades to",
            "ANALYZABLE_NOW (annual resolution; deprivation read blocked by the",
            "Constance confound — late-life continuation read stands).",
            "",
        ]
    )
    OUT_MD.write_text(md, encoding="utf-8")
    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    for name, lo, hi in windows:
        tb, rb = win(lo, hi, "n_mentions_broad")
        ti, ri = win(lo, hi, "n_issuer_like")
        print(f"{name:28s} broad={tb:3d} ({rb}/yr)  issuer_like={ti:3d} ({ri}/yr)")


if __name__ == "__main__":
    main()
