# Densify: Wolsey + Ardingelli thin/extreme cells (2026-08-02)

## Decision

Continental letter mines (Dutch / German / Spanish) dry. Deep-densify two high-leverage thin cells:

- `wolsey` (england ruler_cleric): n_ctrl=3, Δ=**−9**
- `ardingelli_bese` (italy merchant): n_ctrl=3, Δ=**−15** (long-lived peer median)

## Ingest

| QID | Name | Bucket | last pin | ya45 | Cell |
|-----|------|--------|--------:|-----:|------|
| Q5534459 | Geoffrey Blythe | cleric | 1528 | 13 | Wolsey |
| Q6259279 | John Stokesley | cleric | 1539 | 19 | Wolsey |
| Q2258968 | Christopher Bainbridge | cleric | 1514 | 5 | Wolsey |
| Q1788686 | Edward Lee | cleric | 1544 | 17 | Wolsey |
| Q299663 | Piero di Cosimo de' Medici | merchant | 1469 | 8 | Ardingelli |

- Appended to `b1_control_candidates_v3.csv` + `b1_control_nearwork_chrono_curated.csv` (`use_in_primary=True`, high).
- `CTRL_REGION_OVERRIDE` in `scripts/24_…` (B1_SPARQL=0 safe).
- Blythe last pin conservative **1528** (King's Hall resignation; diocesan tenure to 1530/31).

## Cell moves

| Wearer | n_ctrl | med C | Δ |
|--------|------:|------:|--:|
| Wolsey | 3→**7** | 21→**17** | −9→**−5** |
| Ardingelli | 3→**4** | 29→**18.5** | −15→**−4.5** |

## Primary (unchanged median)

| Metric | Value |
|--------|------:|
| n pairs | **39** |
| median Δ | **−2.97** |
| boot CI | **[−4.0, 2.0]** |
| merchant median Δ | **−5.74→−3.74** |
| SESOI +5/+15 | **FAIL** |

Panel median stable; extreme negative merchant/Wolsey cells pulled toward zero by better peer length mix. B1 still **UNIDENTIFIED**.
