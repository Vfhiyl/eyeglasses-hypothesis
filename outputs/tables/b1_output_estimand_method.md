# B1-Output estimand (corrected path, audit 2026-08-12)

**Date:** 2026-08-12 — outcome-aware overlay/exclude layer removed; dropped
death-tip pins restored (`b1_audit_restore_log_2026-08-12.csv`). The pass-era
output SESOI+5 PASS_RAW is **retracted** (see `docs/B1_CURATION_AUDIT_2026-08-12.md`).  
**Script:** `27_b1_output_estimand.py`  
**SESOI doc:** `docs/B1_OUTPUT_SESOI.md`

## Estimand

Among onsetish **textual** documentary wearers with dated works, relative to
region/occupation-matched **textual-authorship** controls:

> **Δ = T_output_span_after_45 − median(C_output_span_after_45)**

`output_span_after_45 = max(0, max(years≥birth+45) − (birth+45))` (0 if no post-45 years but has works).

Missing works ⇒ excluded from Δ (not coded as zero).  
Artisan/painter wearers and `output_eligible=False` controls are out of primary SESOI.

## Current primary result

| | |
|--|--|
| Treatments with dated works | 62 / 66 |
| Primary pairs with Δ | 44 |
| Median Δ (span years) | 3.75 |
| Bootstrap 95% CI | [-2.0, 8.0] |
| share Δ>0 | 0.545 |
| SESOI +5 | FAIL_OR_UNAVAILABLE |
| SESOI +15 | FAIL_OR_UNAVAILABLE |
| Count Δ median (n_works after 45) | 2.0 |

## Caveats

1. P50/P800 is a thin proxy for “important output” (catalog bias; painters/clerics undercount).
2. n_pairs may be <<20 → SESOI verdict is **provisional** until densify / bibliography expands coverage.
3. Post-evidence span is reported per wearer but not used in primary Δ (controls lack onset).
4. Labor-year B1 remains separate (`25_b1_primary_estimand.py`).

## Next densify

1. SPARQL refresh for empty-QID wearers after QID fill.
2. Hand chronology for high-value letter producers without P50 (e.g. Strozzi letters).
3. P800-only sensitivity when n_p800 grows.
