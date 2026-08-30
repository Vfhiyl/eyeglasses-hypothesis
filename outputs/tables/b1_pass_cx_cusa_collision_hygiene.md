# Pass CX — Cusa demotion + wearer–control collision hygiene (2026-08-06)

## Judgment

SESOI+5 already frozen; OA mine dry. Highest digital ROI = **causal hygiene**: find named wearers still sitting in the control pool — not dig a new mine.

## Finding

| Issue | Detail |
|-------|--------|
| **Nicholas of Cusa (Q154751)** | Soft wearer `cusanus` already logged (Mantese 1962 *capseta cum ocularis*) but still `use_in_primary=True` densify peer for **pius_ii** / **sforza_francesco** |
| Wrong QID on wearer row | `cusanus` had `wikidata_qid=Q188822` (Asian Development Bank) → fixed to **Q154751** |
| Residual René output elig | `rene_anjou` flipped to treatment but `output_eligible` still True → set False |

## Actions

1. Demote Cusa labor + output eligibility (symmetric with Locke/Priestley/Burke).
2. Fix `cusanus` QID; annotate overlay inert.
3. New script `30_b1_wearer_control_collision_audit.py` → must report **0** collisions.
4. Spotcheck: Cusa POSITIVE/DEMOTED; Fazio/Cinico false-friend CLEAR; Valla/Nogarola CLEAR (web).

## Remeasure

| Estimand | Before | After |
|----------|--------|-------|
| Labor primary | n=57 med **6.0** CI [3.5, 9.0] | n=57 med **6.0** CI **[4.0, 9.5]** PASS_RAW |
| Labor pius_ii Δ | 3.5 (C≈10.5, n=2) | **11.0** (C≈3, n=1) |
| Labor sforza Δ | 6.0 | **7.0** |
| Output span45 | med 7.0 CI [5.0, 8.5] | med **7.5** CI **[5.75, 9.25]** PASS_RAW |
| Merchant Italy cell | FAIL CI lo −0.47 | unchanged FAIL |
| SESOI+15 | FAIL | FAIL |
| Collisions (`30`) | — | **0** |

Cleaning sensitivity: raw still FAIL; full_clean PASS; +15 all FAIL.

## Causal ID

Still **UNIDENTIFIED**. Demotions remove known contamination; remaining controls are not archive-proven spectacle-negative.

## Next ROI

1. Physical: Yale Spinelli / Keil·HAB / Gray.
2. Re-run `30` whenever adding wearers or densify peers.
3. No OA SESOI mine.
