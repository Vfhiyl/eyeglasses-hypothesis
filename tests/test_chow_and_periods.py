#!/usr/bin/env python3
"""Unit tests for corrected statistical helpers (audit v2)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from importlib import import_module

ts = import_module("04_run_timeseries")


def test_no_break_trend_not_tiny_p():
    rng = np.random.default_rng(0)
    years = np.arange(1200, 1400)
    values = np.exp(0.01 * (years - 1200) + 0.05 * rng.normal(size=len(years)))
    r = ts.chow_trend_test(years, values, bp=1290, window_half=80)
    assert r["p_value"] is not None and not np.isnan(r["p_value"])
    assert r["p_value"] > 0.01, f"false break on pure trend: p={r['p_value']}"


def test_period_start_consistent():
    assert ts.period_start(1452) == 1400
    assert ts.period_start(1299) == 1200
    assert ts.period_start(1300) == 1300


def test_known_level_break_detectable():
    years = np.arange(1200, 1400)
    values = np.where(years < 1290, 10.0, 50.0) * (1 + 0.001 * (years - 1200))
    r = ts.chow_trend_test(years.astype(float), values.astype(float), bp=1290, window_half=80)
    assert r["p_value"] < 0.05, f"missed level break: p={r['p_value']}"


if __name__ == "__main__":
    test_period_start_consistent()
    test_no_break_trend_not_tiny_p()
    test_known_level_break_detectable()
    print("OK: chow / period_start tests passed")
