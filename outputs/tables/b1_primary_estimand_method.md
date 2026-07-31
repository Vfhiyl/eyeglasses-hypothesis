# B1 primary estimand (frozen measurement path)

**Date:** 2026-07-31  
**Scripts/tables:** `25_b1_primary_estimand.py` → `b1_primary_estimand_pairs.csv`, `b1_primary_estimand_summary.csv`

## What is being estimated

Among documentary spectacle wearers (onsetish roster), relative to region- and occupation-matched non-roster controls with curated dated near-work:

> **Δ = T_work_after_45 − median(C_work_after_45)**

where

- `T_work_after_45 = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))`
- `C_work_after_45 = max(0, last_nearwork_year − (birth + 45))` from `b1_control_nearwork_chrono_curated.csv` with **`use_in_primary=True`**
- Matching: `b1_roster_control_matches_region.csv` (occ + birth±10 + macro-region)

This is **not** Macfarlane’s rhetorical “+15 years of intellectual life” verbatim; it is the closest SESOI-compatible contrast we can build from open dated series.

## What is excluded from primary

- Hard-only appendix medians  
- Non-region WD matches  
- Curated controls with `use_in_primary=False` (currently Arnolfini, Pandolfo Rucellai — low confidence)  
- Pure survival `ya45` as main claim number  

## Current primary result

| Subset | n pairs | median Δ | bootstrap 95% CI | SESOI +5 | SESOI +15 |
|--------|--------:|----------:|------------------:|----------|----------|
| All treatments (primary curated) | 36 | -0.75 | [-3.0, 3.3] | FAIL_OR_UNAVAILABLE | FAIL |
| Merchant treatments only | 4 | -1.5 | [-9.47, 0.5] | FAIL_OR_UNAVAILABLE | FAIL |
| High-confidence curated only | 31 | -2.0 | [-5.0, 3.0] | FAIL_OR_UNAVAILABLE | FAIL |

## Interpretation

- If primary CI includes 0 or median < 5 → **do not** claim direction SESOI pass.
- Macfarlane +15 requires median ≥ 15 on this (or stricter) contrast — currently **not met**.
- B1 remains **unidentified** as a causal claim (controls not archive spectacle-negative; curated coverage still partial), but the **strong “+15 typical unlock” reading is unsupported** on the best open contrast we have.

## Next measurement steps

1. Add more `use_in_primary=True` merchant account/letter chronos for Spinelli/Strozzi cells.  
2. Hand spectacle-negative audit on primary curated controls.  
3. Keep wearer n frozen.
