# Pass EL — Gray primary + Bourchier hard tip / midneg densify (2026-08-07)

## Judgment

User-supplied Todd Gray 1996 Part 2 PDF is the gated IA volume. Highest diggable = pin living spectacle year-stamps → promote Bourchier hard (tip≠death) → repair midneg cell after T drops 22→16. Mrs Herle 1651 pin real but bio termini missing → HOLD.

## Wire

### Bourchier `bourchier_henry_bath` (Q5718416)
| Field | Before (soft) | After |
|-------|---------------|-------|
| Source | Costume Historian secondary | **Primary Gray PDF** Pt.2 London Accounts |
| Onset | 1646 | 1646 (2 pair + case) |
| Tip | soft +8y → death 1654 | **1648** (case + silver glasses changed) |
| ya | 8 | **2** |
| hard | False | **True** |
| T_work_after_45 | 22 | **16** |

Chrono: `data/curated/b1_bourchier_henry_bath_activity_chrono.csv` (1643 pre-onset mend; 1646–48 living series).

### Control densify (post-tip midneg Δ=3.5)
| Change | Detail |
|--------|--------|
| Burton `Q259132` tip-strip | last **1638→1628** (living Anatomy ed; tip≠death 1640); C **16→6**. Bourchier-only peer. |
| Cotton `Q333098` exclude | tip=death 1631 / span45≈15 after T=16; **Bourchier-local only** (Cotton remains for Jeffreys/Howard). |
| Keep | Essex `Q2701696` (C=10), Strafford `Q336091` (C=3), Burton tip-stripped (C=6) |

### Mrs Herle
HOLD: `data/raw/gray_devon_household_1996/mrs_herle_HOLD.md` — 1651 pin real; no promote without birth/death.

### Hygiene fix
Restored truncated `b1_wearer_output_years_curated.csv` from `*.bak_pass_el_20260807` (partial write earlier in EL); Bourchier row re-written with primary Gray source_files.

## Remeasure (`B1_SPARQL=0`)

| Estimand | After EK | After EL |
|----------|----------|----------|
| Labor primary | med 8.5 CI[7.5,10] n_ge_5 **56** | med 8.5 CI[7.5,10] n_ge_5 **56** |
| Bourchier Δ | ~9.5 (soft tip) → tip-only **3.5** | **10.0** (controls densified) |
| Output span | PASS_RAW med 8.5 | PASS_RAW med 8.5 (Bourchier Δ_span **10.0**) |
| Merchant | FAIL lo −0.47 | FAIL lo −0.47 |
| Freeze | PASS | PASS |

## Δ&lt;5 remaining (structural / archive)
| Person | Δ | Why stuck |
|--------|--:|-----------|
| spinelli_benedetto | −0.47 | tip≥1535 archive-only |
| leo_x | 0.5 | T=1 (dies age 46) |
| jeake_samuel | 2.0 | T=2 (dies age 47); Cmed already 0 |

## Backup
- `*.bak_pass_el_20260807` (candidates / census / wearer oy)
- `*.bak_pass_el_ctrl_20260807` (chrono / excludes / activity / census ctrl densify)
