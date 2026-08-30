# B1 primary robustness (2026-07-31)

Frozen primary remains script `25`. This note is sensitivity only.

## Specs

| Spec | n | median Δ | 95% CI | +5 | +15 |
|------|--:|----------:|--------|----|-----|
| primary_all | 59 | 10 | [8.5, 11.5] | PASS_WITH_CI | FAIL |
| drop_T_eq_0 | 59 | 10 | [8.5, 11.5] | PASS_WITH_CI | FAIL |
| drop_artisan | 56 | 10 | [8.3, 11] | PASS_WITH_CI | FAIL |
| drop_T0_and_artisan | 56 | 10 | [8.3, 11] | PASS_WITH_CI | FAIL |
| merchant_matched_primary | 8 | 8.75 | [2, 11] | PASS_WITH_CI | FAIL |
| merchant_pooled_italy_curated | 4 | -7 | [-15.97, 8] | FAIL_OR_UNAVAILABLE | FAIL |

Pooled merchantish curated C median = **22.0** (n=30).

## Merchant OA note

Spinelli matched merchants (Balbani, Bernardini, Mattei, Buondelmonti) lack dense OA chronos; no fabricated pins. Strozzi/Ardingelli already use Dei/Barbarigo/Portinari; Arnolfini/Rucellai remain `use_in_primary=False`.

Missing primary deltas after ruler/cleric fill attempt: ['joris_van_der_paele', 'domenichi_ludovico', 'jacques_moser', 'burke_edmund', 'priestley_joseph']

