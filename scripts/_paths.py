"""Shared paths for the eyeglasses-hypothesis pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
DATA_RAW = ROOT / "data" / "raw"
DATA_CURATED = ROOT / "data" / "curated"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUT_TABLES = ROOT / "outputs" / "tables"
OUTPUT_LOGS = ROOT / "outputs" / "logs"

for d in (DATA_RAW, DATA_CURATED, DATA_PROCESSED, OUTPUT_TABLES, OUTPUT_LOGS):
    d.mkdir(parents=True, exist_ok=True)
