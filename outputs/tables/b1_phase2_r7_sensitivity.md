# Phase2 Round 7 — Sensitivity freeze (2026-08-01)

Script: `scripts/26_b1_primary_robustness.py` (does **not** change script 25 estimand).

Re-ran → `b1_primary_robustness_summary.csv` + refreshed `b1_primary_robustness_2026-07-31.md`.

| Spec | n | median Δ | 95% CI | +5 | +15 |
|------|--:|----------:|--------|----|-----|
| primary_all | 37 | −2.97 | [−4, 2] | FAIL | FAIL |
| drop_T_eq_0 | 34 | 0.3 | [−3, 2.5] | FAIL | FAIL |
| drop_artisan | 35 | −3 | [−7, 2] | FAIL | FAIL |
| drop_T0_and_artisan | 32 | −1.485 | [−3.5, 3] | FAIL | FAIL |
| merchant_matched_primary | 4 | −5.735 | [−15, 0] | FAIL | FAIL |
| merchant_pooled_italy_curated | 4 | −9.5 | [−18.47, 5.5] | FAIL | FAIL |

Pooled merchantish C median = **24.5** (n_curated_merchantish=12).

All sensitivity specs remain SESOI FAIL; direction not rescued by dropping T=0 or artisan, nor by merchant pooling.
