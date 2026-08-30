# Pass CO — labor estimand parity (2026-08-06)

## Decision

Output freeze is already SESOI+5 **PASS_RAW** (n=48 med 7.0). OA new-mine remains dry (CN). **Highest ROI = labor primary**, which was still FAIL at med **1.05** CI **[-3.0, 4.5]** because script `25` never applied the Pass BC–CK overlays/excludes that cleaned reverse-lifespan densify on the output side.

## What changed

1. **`scripts/25_b1_primary_estimand.py`**
   - Applies `b1_output_strict_control_overlays.csv` + `b1_output_control_excludes.csv` (same peer set as output).
   - Drops treatments with **death before birth+45** (Bianca Maria, Lorenzo — no post-45 work span).
   - Drops treatments with **T_work_after_45 ≤ 0** (Neri Mici).
2. **Pass CO excludes** (BN/BC-style reverse lifespan; labor parity with existing overlays):
   - Jackson: drop Coutts / Angerstein / Baring → keep Hanbury / Champion / Oliver (**−33 → +5**).
   - Jeake: drop Pitt / Yale / Guy → keep Haistwell / Heathcote (**−26 → +2**).
   - Leo: drop long-lived curial densify → keep Clement VII + Inghirami / Beroaldo (**−19 → 0**).
   - Domenichi / Nicolas / Strozzi / Voiture: same pattern (Strozzi keeps Pigello + existing Piero overlay).
3. Filled Andreae / Buchner birth–death in `b1_control_candidates_v3.csv` from curated chrono (for future rematch).

## Remeasure

| Estimand | n | median Δ | boot 95% CI | SESOI+5 |
|----------|--:|---------:|-------------|---------|
| **Labor primary (before)** | 60 | 1.05 | [-3.0, 4.5] | FAIL |
| **Labor primary (Pass CO)** | **57** | **4.5** | **[2.0, 7.0]** | **FAIL** (med &lt; 5) |
| Output span45 (unchanged) | 48 | 7.0 | [4.0, 8.25] | PASS_RAW |

Labor CI lower bound is now **> 0**; median is one step short of SESOI+5.

## New-mine check

Not reopened for promote: Gray / Keil / HAB / Cleux / Gallica / DDB still library-gated or dry. No new named onset.

## Worst labor cells left

Azevedo −10.5; Pepys −8; Egidio −7; Wood −5; … August still soft (**Δ≈+3** labor) — Keil/HAB physical remains top soft→hard path.

## Next ROI

1. Labor midneg rebalance: Azevedo / Pepys / Egidio (textual peers, not inventing endpoints).
2. Loan: Keil *Augustanus Opticus* + HAB Wiesel–August; Gray 1996.
3. Do **not** unlock Unwin/Voiture into output primary; do **not** use global `output_eligible=False` as a labor filter (drops valid cells).
