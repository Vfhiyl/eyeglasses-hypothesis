#!/usr/bin/env python3
"""Hash key raw/processed inputs for provenance / preprint appendix."""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_TABLES, OUTPUT_LOGS, ROOT
from _utils import log

# path relative to ROOT, license note, source URL
TRACKED = [
    ("data/raw/istc_core_imprints_1.0.csv", "BL ISTC / dataset terms", "https://doi.org/10.23636/k903-md30"),
    ("data/raw/manuscript-production-century.csv", "OWID / underlying Buringh", "https://ourworldindata.org/grapher/manuscript-production-century"),
    ("data/raw/Data.xlsx", "Stelter et al. OSF", "https://osf.io/va93h/"),
    ("data/raw/cdmv-macrodata.zip", "RETE/CDMV authors", "https://perso.uclouvain.be/david.delacroix/"),
    ("data/processed/studium_paris_scholars.csv", "Studium Parisiense API derived", "https://lamop.pantheonsorbonne.fr/"),
    ("data/processed/panel_city_century.csv", "project-derived", "local"),
    ("data/processed/rete_city_year.csv", "RETE macro derived", "local"),
    ("data/processed/istc_city_year.csv", "ISTC derived", "local"),
    ("config/cities.yaml", "project coding (Ilardi-informed)", "local"),
    ("config/rct_effects.yaml", "project coding from RCT papers", "local"),
]


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    rows = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for rel, license_note, source in TRACKED:
        path = ROOT / rel
        digest = sha256_file(path)
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else None,
                "sha256": digest or "",
                "license_or_terms": license_note,
                "source": source,
                "hashed_at_utc": now,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_TABLES / "data_provenance.csv", index=False)
    # human-readable companion
    md = ROOT / "docs" / "DATA_PROVENANCE.md"
    lines = [
        "# Data provenance snapshot",
        "",
        f"Generated: `{now}`",
        "",
        "| path | bytes | sha256 (prefix) | terms |",
        "|------|------:|-----------------|-------|",
    ]
    for r in rows:
        pref = (r["sha256"] or "")[:12]
        lines.append(
            f"| `{r['path']}` | {r['bytes'] or ''} | `{pref}` | {r['license_or_terms']} |"
        )
    lines.append("")
    lines.append("Full hashes: `outputs/tables/data_provenance.csv`.")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"Provenance {len(out)} files -> {OUTPUT_TABLES / 'data_provenance.csv'}", OUTPUT_LOGS / "build.log")


if __name__ == "__main__":
    main()
