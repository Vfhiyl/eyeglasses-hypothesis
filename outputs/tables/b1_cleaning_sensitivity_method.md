# B1 cleaning sensitivity (audit-corrected, 2026-08-12)

**Script:** `29_b1_cleaning_sensitivity.py` → `b1_labor_cleaning_sensitivity.csv`  
**Date:** 2026-08-12

## Question

Did reverse-lifespan / overlay hygiene *manufacture* SESOI+5?

## Answer

**Yes.** On the pre-restore data (snapshot commit 9d95fa1) the layer moved the
labor median from 2.5 (CI crossing 0, FAIL) to 11.25 with share(Δ>0)=1.0.
A 100% one-sided pair distribution is the fingerprint of per-cell curation
iterated until each Δ flipped positive, not of measurement correction.
The layer is removed from the measurement path; data edits were reverted by
`33_b1_revert_outcome_aware_edits.py` (see `b1_audit_restore_log_2026-08-12.csv`
and `docs/B1_CURATION_AUDIT_2026-08-12.md`).

## Labor arms (recomputed on restored data)

| Mode | n | median Δ | boot 95% CI | share Δ>0 | SESOI+5 | SESOI+15 |
|------|--:|---------:|-------------|----------:|---------|----------|
| dirty_max | 63 | 4.5 | [-1.0, 10.5] | 0.587 | FAIL_OR_UNAVAILABLE | FAIL |
| raw_match | 62 | 2.0 | [-1.5, 8.3] | 0.565 | FAIL_OR_UNAVAILABLE | FAIL |
| overlay_exclude_layer (DEPRECATED) | 60 | 10.0 | [8.3, 11.0] | 0.967 | PASS_RAW | FAIL |
| corrected_primary (script 25) | 60 | 3.0 | [-2.0, 9.0] | 0.583 | FAIL_OR_UNAVAILABLE | FAIL |

## Output (corrected path, script 27)

| Mode | n | median Δ | CI | SESOI+5 | SESOI+15 |
|------|--:|---------:|----|---------|----------|
| corrected_output | 44 | 3.75 | [-2.0, 8.0] | FAIL_OR_UNAVAILABLE | FAIL_OR_UNAVAILABLE |

## Reading

1. `corrected_primary` is the reportable number (symmetric death<45 rule,
   cluster bootstrap, no overlays/excludes).
2. `overlay_exclude_layer` shows what the deprecated hand layer still does on
   restored data; do not cite it as a result.
3. Known-wearer demotions (Locke/Priestley/Burke/Cusa) stay out of every arm
   except `dirty_max` (contamination upper bound).
4. **SESOI+15 FAIL in every arm** — nothing rescues Macfarlane +15.

## Claim language

- Do not claim SESOI+5 direction: corrected labor and output medians sit at
  0 to a few years with CIs crossing 0.
- Any future exclusion rule must be symmetric, outcome-blind, pre-registered.
