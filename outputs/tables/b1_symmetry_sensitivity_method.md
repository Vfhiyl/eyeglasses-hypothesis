# B1 symmetry sensitivities (corrected estimand)

**Date:** 2026-08-12  
**Script:** `34_b1_symmetry_sensitivities.py` → `b1_symmetry_sensitivity.csv`

All gates are symmetric (same rule both arms) and outcome-blind
(provenance / pin density / era; never the delta). Base rules =
corrected script 25 path.

| Arm | n (clusters) | median Δ | boot 95% CI | share Δ>0 | SESOI+5 | +15 |
|-----|-------------:|---------:|-------------|----------:|---------|-----|
| corrected_baseline | 60 (42) | 3.0 | [-2.0, 9.0] | 0.583 | FAIL_OR_UNAVAILABLE | FAIL |
| hard_series_wearers | 47 (32) | 6.0 | [-2.0, 11.25] | 0.596 | FAIL_OR_UNAVAILABLE | FAIL |
| density_floor_3_sym | 36 (25) | 4.65 | [-9.0, 12.5] | 0.583 | FAIL_OR_UNAVAILABLE | FAIL |
| drop_todeath_sym | 17 (14) | 0.5 | [-9.0, 9.0] | 0.529 | FAIL_OR_UNAVAILABLE | FAIL |
| pre1500_evidence_invention_era | 26 (17) | 1.0 | [-3.0, 9.0] | 0.5 | FAIL_OR_UNAVAILABLE | FAIL |
| pre1600_evidence | 39 (30) | 2.0 | [-2.5, 7.0] | 0.538 | FAIL_OR_UNAVAILABLE | FAIL |
| post1600_evidence | 21 (12) | 8.3 | [-6.0, 14.25] | 0.667 | FAIL_OR_UNAVAILABLE | FAIL |
| pre1600_hard_density | 16 (14) | -6.75 | [-10.5, 8.5] | 0.438 | FAIL_OR_UNAVAILABLE | FAIL |

## Reading

1. `drop_todeath_sym` answers the wearer-endpoint audit question: when
   every to-death endpoint is dropped on BOTH sides, does the
   direction survive?
2. `pre1600_evidence` is the domain of the Macfarlane claim; the
   post-1600 arm (Franklin/Jefferson era) is out-of-domain and was
   added to the roster after the 2026-07-31 freeze.
   `pre1500_evidence_invention_era` is the first two centuries after
   invention (~1286): the tightest claim domain, and also the window
   where the wear-vs-no-record contrast is least saturated (bulk
   cheap exports from mid-15th c. contaminate later control pools).
   Era strata must never be pooled into one headline median: era
   correlates with adoption saturation AND archive density, so the
   pooled number mixes different estimands.
3. `pre1600_hard_density` is the strictest defensible subset:
   in-domain, hard-dated, density-floored both sides.
4. No arm may be quoted alone as a verdict; this table exists to show
   the corrected result is (or is not) an artifact of endpoint
   conventions, archive density, or era mixing.
