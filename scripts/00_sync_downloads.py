#!/usr/bin/env python3
"""Copy user-downloaded files from ../download_data/ into data/raw/. No network."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW, OUTPUT_LOGS, ROOT
from _utils import log

DOWNLOAD_DIR = ROOT.parent / "download_data"

FILES = [
    "istc_core_imprints_1.0.csv",
    "istc_core_holdings_1.0.csv",
    "istc_references_1.0.csv",
    "istc_clean_1.0.yaml",
    "Data.xlsx",
    "stelter_scholars_Data.xlsx",
    "geonames_cities1000.txt",
    "cdmv-macrodata.zip",
    "manuscript-production-century.csv",
    "manuscript_production_century.csv",
    "production-printed-books-half-century.csv",
    "cross-country-literacy-rates.csv",
    "europop.csv",
    "city_coords.csv",
    "wiag_bishops_persons.csv",
    "wiag_domherren_persons.csv",
    "wikidata_european_scholars.csv",
    "osfstorage-archive.zip",
    "cities1000.zip",
    "person_2025_update.csv.bz2",
    "pantheon_2025.csv.bz2",
    "deutschestudent00knod_djvu.txt",
    "mmm_data_v2.1.0.zip",
    "leuven_matrikels.tab",
    "utrecht_priests.tab",
    "studium_persons.jsonl",
    "sdbm_florence_1200_1500.csv",
    "sdbm_florence_1200_1500_provenance.csv",
    "sdbm_paris_1200_1500.csv",
    "sdbm_paris_1200_1500_provenance.csv",
    "sdbm_venice_1200_1500.csv",
    "sdbm_venice_1200_1500_provenance.csv",
    "sdbm_milan_1200_1500.csv",
    "sdbm_nuremberg_1200_1500.csv",
    "sdbm_bologna_1200_1500.csv",
    "sdbm_cologne_1200_1500.csv",
    "sdbm_oxford_1200_1500.csv",
]


def sync_file(name: str) -> bool:
    src = DOWNLOAD_DIR / name
    if not src.exists():
        return False
    dst = DATA_RAW / name
    if dst.exists() and dst.stat().st_size == src.stat().st_size:
        return True
    shutil.copy2(src, dst)
    log(f"Synced {name} ({src.stat().st_size // 1024} KB)", OUTPUT_LOGS / "sync.log")
    return True


def sync_rag() -> bool:
    """Copy RAG Daten/ tree into data/raw/rag/."""
    src_dir = DOWNLOAD_DIR / "rag"
    dst_dir = DATA_RAW / "rag"
    if not src_dir.exists():
        return dst_dir.exists()
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in src_dir.glob("*.csv"):
        dst = dst_dir / src.name
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
            copied += 1
    if copied:
        log(f"Synced RAG {copied} csv files -> data/raw/rag/", OUTPUT_LOGS / "sync.log")
    return (dst_dir / "Ereignis.csv").exists()


def sync_tree(src_sub: str, dst_sub: str, pattern: str = "*") -> bool:
    """Copy a subdirectory tree from download_data into data/raw/."""
    src_dir = DOWNLOAD_DIR / src_sub
    dst_dir = DATA_RAW / dst_sub
    if not src_dir.exists():
        return dst_dir.exists()
    dst_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in src_dir.rglob(pattern):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
            copied += 1
    if copied:
        log(f"Synced {src_sub}/ -> data/raw/{dst_sub}/ ({copied} files)", OUTPUT_LOGS / "sync.log")
    return dst_dir.exists()


def sync_domherren() -> bool:
    """Copy user Domherren export to standard raw filename."""
    dst = DATA_RAW / "wiag_domherren_persons.csv"
    for name in (
        "wiag_domherren_persons.csv",
        "WIAG-Domherren-DB (1).csv",
        "WIAG-Domherren-DB.csv",
    ):
        src = DOWNLOAD_DIR / name
        if not src.exists() or src.stat().st_size < 10_000:
            continue
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            return True
        shutil.copy2(src, dst)
        log(f"Synced domherren -> wiag_domherren_persons.csv ({src.stat().st_size // 1024} KB)", OUTPUT_LOGS / "sync.log")
        return True
    return dst.exists()


def sync_sdbm_glob() -> list[str]:
    """Copy any sdbm_*_1200_1500*.csv not already listed in FILES."""
    if not DOWNLOAD_DIR.exists():
        return []
    synced: list[str] = []
    for src in sorted(DOWNLOAD_DIR.glob("sdbm_*_1200_1500*.csv")):
        if sync_file(src.name):
            synced.append(src.name)
    return synced


def main() -> None:
    if not DOWNLOAD_DIR.exists():
        log(f"No download_data dir at {DOWNLOAD_DIR}", OUTPUT_LOGS / "sync.log")
        return
    sync_domherren()
    sync_rag()
    sync_tree("bhotmg/extracted", "bhotmg/extracted")
    sync_tree("bhotmg", "bhotmg", "*.tab")
    synced = [f for f in FILES if sync_file(f)]
    for name in sync_sdbm_glob():
        if name not in synced:
            synced.append(name)
    missing = [f for f in FILES if f not in synced and not (DATA_RAW / f).exists()]
    log(f"Synced {len(synced)} files; still missing: {missing or 'none'}", OUTPUT_LOGS / "sync.log")


if __name__ == "__main__":
    main()
