#!/usr/bin/env python3
"""Extract spectacle* hits from local Jenks LCA PDF text dumps."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

RAW = ROOT / "data" / "raw" / "london_customs"
OUT_HITS = OUTPUT_TABLES / "jenks_spectacle_text_hits.csv"
PAT = re.compile(r".{0,80}spectacul?\w*.{0,120}", re.I)


def pdf_to_txt(pdf: Path) -> Path:
    txt = pdf.with_suffix(".txt")
    if txt.exists() and txt.stat().st_mtime >= pdf.stat().st_mtime and txt.stat().st_size > 1000:
        return txt
    try:
        subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(txt)],
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        try:
            import pypdf
        except ImportError:
            raise
        reader = pypdf.PdfReader(str(pdf))
        txt.write_text(
            "\n".join((p.extract_text() or "") for p in reader.pages),
            encoding="utf-8",
            errors="replace",
        )
    return txt


def main() -> None:
    rows: list[dict] = []
    pdfs = sorted(RAW.glob("jenks_lca_*.pdf")) + sorted(RAW.glob("jenks_lca_ii_*.pdf"))
    # de-dupe
    seen: set[Path] = set()
    uniq = []
    for p in pdfs:
        if p.resolve() in seen:
            continue
        seen.add(p.resolve())
        uniq.append(p)

    for pdf in uniq:
        try:
            txt = pdf_to_txt(pdf)
        except Exception as e:
            log(f"extract fail {pdf.name}: {e}", OUTPUT_LOGS / "fetch.log")
            continue
        text = txt.read_text(encoding="utf-8", errors="replace")
        # skip index-heavy false positives by requiring quantity-ish neighborhood later
        for i, line in enumerate(text.splitlines(), 1):
            if not re.search(r"spectacul", line, re.I):
                continue
            if re.search(r"^\s*spectacle", line, re.I) and "Precii" not in line and "gros" not in line.lower():
                # glossary/index lines
                if "eye" in line.lower() or re.match(r"^\s*spectacle", line, re.I):
                    if not re.search(r"\d+\s+(gros|dossen|dozen|coffyn)", line, re.I):
                        continue
            m = PAT.search(line)
            rows.append(
                {
                    "volume": pdf.name,
                    "line": i,
                    "snippet": (m.group(0) if m else line).replace("\t", " ").strip()[:220],
                }
            )

    OUT_HITS.parent.mkdir(parents=True, exist_ok=True)
    with OUT_HITS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["volume", "line", "snippet"])
        w.writeheader()
        w.writerows(rows)
    log(f"Jenks spectacle text hits: {len(rows)} -> {OUT_HITS}", OUTPUT_LOGS / "fetch.log")
    print(f"hits={len(rows)} volumes={len(uniq)} -> {OUT_HITS}")


if __name__ == "__main__":
    main()
