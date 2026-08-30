# Pass BL — control death-strip stress + soft-stock plateau (2026-08-05)

## Decision

**No primary change.** Freeze holds. Two housekeeping/robustness products:

1. Control `death==last` strip sensitivity (symmetric to BG wearer stress)  
2. Soft-stock plateau catalog (17 onsetish, all gated)

## Control death==last strip

Death-year pins on **controls** inflate `C` → **lower** Δ (bias *against* the claim).

| mode | n | median | boot95 CI | SESOI +5 |
|--|--|--|--|--|
| primary freeze (repro) | 44 | **6.0** | **[3.0, 8.75]** | PASS_RAW |
| strip ctrl year if `year==death` | 44 | **11.0** | **[8.0, 18.0]** | PASS_RAW |

- 36/44 cells shift; median shift **+8.0** Δ years  
- Year-union matches `27_b1_output_estimand.py` (P50+P800+curated); freeze Δ repro exact  

**Interpretation:** PASS_RAW is **not** an artifact of control death termini favoring treatment. Those termini make the claim harder; stripping them strengthens the median.

Tables: `b1_output_ctrl_death_strip_sensitivity.csv`, `b1_output_ctrl_death_strip_cells.csv`.

## Soft-stock plateau (17)

| gate class | persons |
|--|--|
| Library | `hesselin_denis`, `bourchier_henry_bath`, `jeffreys_joyce` |
| HARD OA closed | `rene_ii_lorraine`, `arduino_baiso` |
| Short-window | `voiture_vincent` (CLOSED), `wolsey`, `henry_viii` |
| Third-party / low pin | `unwin_mary` |
| ya≈0 / thin | `spinelli_benedetto`, `nuno_fernandes`, 5 ya=0 friars/notaries |
| Output-ok soft labor | `wyatt_henry` |

Catalog: `b1_soft_stock_plateau_2026-08-05.csv`.

## OA scout (this pass)

- OpenAlex: **429** rate limit  
- Gallica SRU: **403** via proxy  
- No new Cleux-bar promote  

## Do not

- Strip control deaths into primary (would loosen estimand without claim rewrite)  
- Reopen library/OA-closed softs without new PDFs  
- Reopen Brittany / Walmysford–Nuno  
