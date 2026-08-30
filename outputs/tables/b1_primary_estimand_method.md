# B1 primary estimand (corrected path, audit 2026-08-12)

**Date:** 2026-08-12 (outcome-aware curation layer removed)  
**Scripts/tables:** `25_b1_primary_estimand.py` → `b1_primary_estimand_pairs.csv`, `b1_primary_estimand_summary.csv`  
**Restore log:** `b1_audit_restore_log_2026-08-12.csv` (via `33_b1_revert_outcome_aware_edits.py`)

## What is being estimated

Among documentary spectacle wearers (onsetish roster), relative to region- and
occupation-matched non-roster controls with curated dated near-work:

> **Δ = T_work_after_45 − median(C_work_after_45)**

- `T_work_after_45 = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))`
- `C_work_after_45 = max(0, last_nearwork_year − (birth + 45))` from
  `b1_control_nearwork_chrono_curated.csv` with `use_in_primary=True`
- Matching: `b1_roster_control_matches_region.csv` (occ + birth±10 + macro-region)

## Corrections applied 2026-08-12 (vs. the pass BC–FI path)

1. **Overlay/exclude layer disabled.** The per-wearer excludes cited the
   control's own span ("reverse lifespan", "post-death densify", "tip=death",
   "pulls Cmed"); the overlays added lifespan-matched short-span controls.
   One-directional and outcome-aware → removed from the measurement path.
2. **Tip-strips reverted** (38 labor rows, 14 output pins): control endpoints
   had been shortened while wearer `*_to_death` endpoints were kept.
3. **Outcome-aware demotions reverted** (9 rows incl. Adam Smith, Borso
   d'Este, Oldenburg). Contamination demotions (documented wearers: Locke,
   Priestley, Burke, Cusa) and pre-pass data-quality demotions stay.
4. **Symmetric eligibility.** Both arms drop death < birth+45; T=0 wearers
   are kept (previously skipped while C=0 controls were kept).
5. **Cluster bootstrap.** Pairs sharing controls resample as one cluster
   (i.i.d. pair bootstrap understated variance; a few controls serve many
   wearers, e.g. the 18th-c England cell).

## Current result (corrected)

| Subset | n pairs (clusters) | median Δ | boot 95% CI | share Δ>0 | SESOI +5 | SESOI +15 |
|--------|-------------------:|---------:|------------:|----------:|----------|-----------|
| All treatments (primary curated) | 60 (42 cl) | 3.0 | [-2.0, 9.0] | 0.583 | FAIL_OR_UNAVAILABLE | FAIL |
| Frozen roster 2026-07-31 only | 34 (26 cl) | 1.0 | [-3.0, 5.6] | 0.5 | FAIL_OR_UNAVAILABLE | FAIL |
| Merchant treatments only | 4 (3 cl) | -3.74 | [-6.5, 0.0] | 0.0 | FAIL_OR_UNAVAILABLE | FAIL |
| High-confidence curated only | 56 (41 cl) | 2.5 | [-3.75, 10.0] | 0.518 | FAIL_OR_UNAVAILABLE | FAIL |

## Interpretation guardrails

- The expanded roster (36 → current) was assembled **after** the 2026-07-31
  wearer-n freeze and includes famous long-lived wearers (Franklin,
  Jefferson, Washington); treat `all_treatments` as exploratory and read
  `frozen_roster_2026_07_31` alongside it.
- Controls are "no spectacle record found", **not** documented non-wearers;
  by the 15th c. spectacles were cheap and widespread. Causal ID remains
  blocked; Δ largely reflects differential documentation density.
- Macfarlane +15 requires median ≥ 15 on this contrast — see summary.
- Historical comparison: 2026-07-31 frozen path Δ=−0.75 [−3.0, 3.3] (n=36);
  pass-era raw_match Δ=2.5 [−0.5, 9.5] (n=62); pass-era outcome-aware
  "full_clean" Δ=11.25 with share(Δ>0)=1.0 — **retracted** (manufactured;
  see `b1_labor_cleaning_sensitivity.csv` and
  `docs/B1_CURATION_AUDIT_2026-08-12.md`).
- **Wearer–control collision (required clear):**
  `30_b1_wearer_control_collision_audit.py` — active collisions must be 0.

## Next measurement steps

1. Symmetric endpoint re-adjudication: decide death-tip validity by one rule
   for BOTH arms (wearer `*_to_death` endpoints vs control death-tips).
2. Documentation-density floor for controls (≥k dated pins) applied
   symmetrically, pre-registered before any further expansion.
3. Wearer-side endpoint audit (years_after_evidence provenance).
