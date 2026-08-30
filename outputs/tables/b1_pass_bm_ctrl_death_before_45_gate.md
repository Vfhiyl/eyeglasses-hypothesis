# Pass BM — control death-before-45 gate (2026-08-05)

## Verdict

SESOI +5 remains **PASS_RAW** after dropping controls who die before age 45 (symmetric to treatment gate).

| | pre-BM (BJ freeze) | **BM** |
|--|--|--|
| n | 44 | **44** |
| median Δ | 6.0 | **6.0** |
| CI | [3.0, 8.75] | **[3.0, 8.5]** |
| share>0 | 0.705 | **0.705** |
| SESOI +5 | PASS_RAW | **PASS_RAW** |

## Leak found

Two primary control links had `death < birth+45` → forced `output_span_after_45 = 0`, deflating C median (bias *for* the claim):

| control | age@death | wearer | effect of drop |
|--|--|--|--|
| Joan of Valois `Q917090` | 30 | `philippe_le_hardi` | C 20→21; Δ **−3→−4** |
| Ermolao Barbaro Younger `Q1236821` | 40 | `spataro_giovanni` | C 24→30; Δ **+14→+8** |

Barbaro was already `use_in_primary=False` on the labor nearwork chrono, but still leaked into output via match QIDs (no `output_eligible=False` row).

## Fix

1. `ctrl_allowed()` in `27_b1_output_estimand.py`: reject `death < birth+45`  
2. Eligibility: `Q917090` and `Q1236821` → `output_eligible=False` (Pass BM notes)

## Not done

- `exclude_ctrl_death_before_50` — would FAIL SESOI (med 4); too aggressive vs lifespan-matched Leo/Jeake peers  
- Soft→hard library stock still gated; OA scout not re-opened this pass  
