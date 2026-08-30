# Pass BU — Gray still gated; eligibility unlock for Jeffreys (2026-08-06)

## Gray probe

`devonhouseholdac0000unse` (Gray Devon Household Accounts Pt 2): browse/borrow both **HTTP 400** unavailable. Bourchier / Mrs Herle remain library-gated.

## Plumbing find

`load_ctrl_curated_years()` only loads hand pins when `qid ∈ elig_true`. Eight curated control rows had **years but no eligibility row**, so they were silently dropped:

| qid | name | densify target |
|--|--|--|
| Q3852414 | Maurice Abbot | jeffreys_joyce |
| Q6555592 | Lionel Cranfield | jeffreys_joyce |
| Q1248124 / Q1451213 / Q334978 | Balzac / Tristan / Chapelain | voiture_vincent |
| Q183266 / Q34190 / Q37160 | Johnson / Fielding / Hume | franklin / richardson |

## Fix

Added `output_eligible=True` rows in `b1_control_output_eligibility.csv` (Pass BU reasons). Remeasure `B1_SPARQL=0`.

## Impact (B1-Output)

| | freeze (pre-BU) | **BU** |
|--|--|--|
| n_pairs_with_delta | 44 | **45** |
| median Δ | 6.0 | **5.0** |
| boot95 CI | [3.0, 8.0] | **[3.0, 8.0]** |
| SESOI+5 | PASS_RAW | **PASS_RAW** |

- **jeffreys_joyce**: n_ctrl 0→2; Δ=**−1.5** (T span45=27 vs C med 28.5); now `in_primary_delta=1`.
- **voiture_vincent**: controls unlock but still `exclude_coverage_low_pin`.
- Franklin / Richardson: extra eligible peers; deltas unchanged (20 / 8).

No new named-wearer evidence this pass. Soft plateau: Jeffreys remains HARD from Pass BT; Bourchier still `LIBRARY_Gray_IA_borrow`.

## Next ROI

1. Gray when borrowable (Bourchier densify + Mrs Herle bio).  
2. Cleux-bar new ore (page_production), not reopening saturated Spicksley/Jeffreys.  
3. Other `no_delta` cells only if curated peers exist but elig-gated.
