#!/usr/bin/env python3
"""Parse Ilardi Appendix I Florence occhialai list from local OCR → curated CSV."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_LOGS, ROOT
from _utils import log

OCR = ROOT / "data" / "raw" / "ilardi" / "Renaissance_Vision_djvu_ocr.txt"
OUT = ROOT / "data" / "curated" / "ilardi_florence_makers.csv"

# Numbered entries: "1. 1413, 28 Oct. Name..." or "5. 1456, lOjan. Name"
ENTRY_RE = re.compile(
    r"(?m)^(\d{1,2})\.\s+(\d{4})(?:,\s*([^\n.]{0,40}))?\.\s+(.+?)(?=\n\d{1,2}\.\s+\d{4}|\nAPPENDIX|\n\d{3}\s*$|\Z)",
    re.DOTALL,
)


def _clean_name(blob: str) -> str:
    line = blob.split("\n")[0]
    # cut at first ASF / archival cue
    for sep in (", ASF", ",ASF", " ASF", ", Catasto", ", Neri", ", ibid"):
        if sep in line:
            line = line.split(sep)[0]
    line = re.sub(r"\s+", " ", line).strip(" ,.;")
    # drop trailing role tags after comma if long
    if "," in line and len(line) > 60:
        line = line.split(",")[0].strip()
    return line[:120]


def main() -> None:
    if not OCR.exists():
        log(f"Missing OCR {OCR}", OUTPUT_LOGS / "fetch.log")
        return
    text = OCR.read_text(encoding="utf-8", errors="replace")
    start = text.find("APPENDIX I")
    end = text.find("APPENDIX II", start + 1)
    if start < 0 or end < 0:
        log("Could not locate APPENDIX I/II bounds", OUTPUT_LOGS / "fetch.log")
        return
    chunk = text[start:end]
    rows = []
    for m in ENTRY_RE.finditer(chunk):
        num, year, date_frag, rest = m.group(1), int(m.group(2)), m.group(3) or "", m.group(4)
        name = _clean_name(rest)
        if not name or len(name) < 3:
            continue
        low = rest.lower()
        rows.append(
            {
                "maker_id": f"florence_occhialaio_{int(num):02d}",
                "list_number": int(num),
                "first_attested_year": year,
                "date_fragment": re.sub(r"\s+", " ", date_frag).strip(),
                "name_raw": name,
                "is_friar": int("friar" in low or "frate" in low or "monaco" in low),
                "mentions_shop": int("botteg" in low or "shop" in low or "apotech" in low),
                "source": "Ilardi 2007 Appendix I pp.253-56 (OCR)",
                "confidence": "medium",
                "notes": "Parsed from Renaissance_Vision_djvu_ocr.txt; OCR name spelling noisy",
            }
        )
    df = pd.DataFrame(rows).drop_duplicates(subset=["list_number"], keep="first")
    df = df.sort_values("list_number")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"makers={len(df)} years={df.first_attested_year.min()}-{df.first_attested_year.max()} -> {OUT}")
    log(f"Ilardi Appendix I makers={len(df)} -> {OUT}", OUTPUT_LOGS / "fetch.log")


if __name__ == "__main__":
    main()
