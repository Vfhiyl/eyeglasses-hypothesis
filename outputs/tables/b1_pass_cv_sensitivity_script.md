# Pass CV — freeze cleaning sensitivity into pipeline (2026-08-06)

## Judgment

After Pass CU one-shot table: highest ROI is **make sensitivity reproducible** and bind it into claim freeze language — not new mine / not René unlocks.

## Deliverables

1. `scripts/29_b1_cleaning_sensitivity.py` — recomputes labor `dirty_max` / `raw_match` / `full_clean`; records frozen output summary.
2. Regenerates `b1_labor_cleaning_sensitivity.csv` + `b1_cleaning_sensitivity_method.md`.
3. Script 25 method + verdict now **require cite** of the sensitivity table; new check `cleaning_sensitivity_documented=DONE`.

## Confirmed numbers (script 29)

| Labor mode | med | CI | SESOI+5 | +15 |
|------------|----:|----|---------|-----|
| raw_match | 1.05 | crosses 0 | FAIL | FAIL |
| full_clean | 6.0 | [3.5, 9.0] | PASS_RAW | FAIL |

Primary freeze unchanged (no estimand edit).

## Next ROI

Physical densify only; always run `29` before claim write-ups.
