#!/usr/bin/env python3
"""Tests for Studium parsing and synthesis policy."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name: str, filename: str):
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # Avoid executing main; load module
    spec.loader.exec_module(mod)
    return mod


def test_single_year_not_birth():
    stud = _load("studium", "02v_process_studium.py")
    items = [
        {
            "value": "1122",
            "meta": {"dates": [{"type": "SIMPLE", "date": 1122}]},
        }
    ]
    by, dy, q = stud._parse_life_years(items)
    assert by is None
    assert dy == 1122
    assert q == "single_year_not_birth"


def test_interval_birth_death():
    stud = _load("studium", "02v_process_studium.py")
    items = [
        {
            "value": "1245-1316",
            "meta": {
                "dates": [
                    {
                        "type": "INTERVAL",
                        "startDate": {"type": "SIMPLE", "date": 1245},
                        "endDate": {"type": "SIMPLE", "date": 1316},
                    }
                ]
            },
        }
    ]
    by, dy, q = stud._parse_life_years(items)
    assert by == 1245 and dy == 1316 and q == "interval_meta"


def test_synthesis_never_strong_causal():
    syn = _load("syn", "07_synthesis.py")
    row = syn.classify_evidence(
        {
            "test": "glass_center_on_hc",
            "value": 1.0,
            "p_value": 0.001,
            "note": "",
            "n_pre": 100,
            "tier": "core",
        }
    )
    assert row["supports_strong_causal_claim"] is False
    assert row["direction"] == "consistent"


def test_power_mde_positive():
    pwr = _load("pwr", "09_power_and_sensitivity.py")
    m = pwr.mde_two_proportions(80, 180, 0.85)
    assert m > 0


if __name__ == "__main__":
    test_single_year_not_birth()
    test_interval_birth_death()
    test_synthesis_never_strong_causal()
    test_power_mde_positive()
    print("OK: studium/synthesis/power tests passed")
