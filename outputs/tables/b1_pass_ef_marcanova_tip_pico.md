# Pass EF — Marcanova tip-strip + Spataro Pico (2026-08-07)

## Judgment

After EE (Spataro ≥5), next diggable = (1) death-as-tip on reused Marcanova, (2) unused Spataro region QID Pico (dies age 31 → C=0).

Gray still 0 spectacle+year. Merchant/Spinelli unchanged (archive-only).

## Wire

### Giovanni Marcanova `Q21545248`
| Field | Before | After |
|-------|--------|-------|
| Labor `last_nearwork_year` | 1467 (=death) | **1460** (Collectanea / documentary pin) |
| Output years | `1445;1460;1467` | `1445;1460` (drop death pin) |
| C_work_after_45 | 12 | **5** |

Death 1467 ≠ tip (same hygiene as Nesi tip≠death).

### Giovanni Pico della Mirandola `Q182128`
- Birth 1463 / death 1494 age 31 → **C=0**
- Overlay on `spataro_giovanni` (birth±10 Italy philosopher; unused region match)

## Remeasure (`B1_SPARQL=0`)

| Estimand | After EE | After EF |
|----------|----------|----------|
| Labor primary | med 7.5 CI[6.0,10.0] n_ge_5 **45** | med **8.3** CI[6.0,10.0] n_ge_5 **46** |
| Ammannati Δ | 4.0 | **7.5** |
| Spataro Δ | 5.6 | **14.6** |
| Tranchedini Δ | 10.5 | **13.5** |
| Alessandra Δ | 7.0 | **9.0** |
| Output span45 | PASS_RAW | PASS_RAW |
| Merchant | FAIL lo −0.47 | FAIL lo −0.47 |
| Freeze gate | PASS | PASS |

## Backup

- `b1_control_nearwork_chrono_curated.csv.bak_pass_ef_20260807`
- `b1_output_strict_control_overlays.csv.bak_pass_ef_20260807`
- `b1_control_output_years_curated.csv.bak_pass_ef_20260807`
