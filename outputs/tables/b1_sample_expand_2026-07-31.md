# Sample expansion (2026-07-31)

## Control pool

| Stratum | n (approx) |
|---------|-----------:|
| merchant | 398 |
| ruler | 341 |
| clerk/notary | 307 |
| artisan | 219 |
| admin | 12 |
| prior v2+scholars | ~1089 |
| **v3 total** | **~2341** |

Sources: `b1_control_strata_extra.csv` → merged into `b1_control_candidates_v3.csv`.

## Treatment (onsetish)

| | before | after |
|--|------:|------:|
| onsetish coded | 32 | **34** (+Wyatt, Wolsey from gift→onsetish with soft +3y) |
| with birth matched | 27 | **29** |
| **primary occ+birth** | 20 | **29** (0 relaxed) |

Ungated activity median **7.0y** (was 8.5; more short series included — correct for ungated).

## Matching / SESOI (still)

- ya45 occ Δ median **+1.25** → +5 FAIL  
- P800 work Δ median **+9.5** (n=13) → +5 PASS_RAW, +15 FAIL  
- B1 near-work causal: **UNIDENTIFIED**

## Scripts touched

- `20_b1_roster_census_panel.py` — gift_luxury not auto-excluded; occ buckets  
- `22_b1_roster_occ_match_and_p800.py` — merchant/clerk/admin strata mapping  
