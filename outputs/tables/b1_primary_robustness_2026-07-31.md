# B1 primary robustness (2026-07-31)

Frozen primary remains script `25`. This note is sensitivity only.

## Specs

| Spec | n | median Δ | 95% CI | +5 | +15 |
|------|--:|----------:|--------|----|-----|
| primary_all | 36 | -0.75 | [-3, 3.3] | FAIL_OR_UNAVAILABLE | FAIL |
| drop_T_eq_0 | 33 | 0 | [-2, 4.5] | FAIL_OR_UNAVAILABLE | FAIL |
| drop_artisan | 34 | -1 | [-3.5, 2] | FAIL_OR_UNAVAILABLE | FAIL |
| drop_T0_and_artisan | 31 | -0.5 | [-3, 2.1] | FAIL_OR_UNAVAILABLE | FAIL |
| merchant_matched_primary | 4 | -1.5 | [-9.47, 0.5] | FAIL_OR_UNAVAILABLE | FAIL |
| merchant_pooled_italy_curated | 4 | -3.5 | [-12.47, 11.5] | FAIL_OR_UNAVAILABLE | FAIL |

Pooled merchantish curated C median = **18.5** (n=8).

## Merchant OA note

Spinelli matched merchants (Balbani, Bernardini, Mattei, Buondelmonti) lack dense OA chronos; no fabricated pins. Strozzi/Ardingelli already use Dei/Barbarigo/Portinari; Arnolfini/Rucellai remain `use_in_primary=False`.

Missing primary deltas after ruler/cleric fill attempt: (none)

