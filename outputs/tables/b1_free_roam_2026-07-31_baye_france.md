# Free roam → Nicolas de Baye + France cell (2026-07-31)

## Decision

Chose **free web hunt** over Latone/Nuno stall. Strongest new birth-dated self-wearer: **Nicolas de Baye**. Built missing **france** macro-region cell rather than leaving him candidate-only.

## Baye — promoted onsetish (soft)

| Fact | Source |
|------|--------|
| Birth ~1364 / death 1419-05-09 | WD Q3340895 |
| Greffier du Parlement de Paris | Journal span 1400–1416 (Tuetey) |
| Self-report **1416-11**: needs *lunettes* to *enregistrer* | Tuetey *Journal* (IA `journaldenicolas02bayeuoft` / `journaldenicola01bayegoog`) |
| Post-onset | Conseiller clerc **1417**; Burgundian proscription **1418**; death **1419** |
| `years_after_evidence` | **2** (to 1418 office end; not survival to death) |
| hard | **False** (short window) |

Quote (petition): *«estoie-je aucunement débilité de ma veue et ne povoie pas bien enregistrer sans avoir lunettes»*.

Files: `b1_nicolas_de_baye_chrono.csv`; raw OCR under `data/raw/french/`.

## France cell

- Treatment override: `nicolas_de_baye` → `france`
- Match: **occ_relaxed+region** (clerk → humanist France)
- Curated controls (+5 primary): Christine de Pizan, Gerson, Clamanges, Jean Fusoris, Laurent de Premierfait
- Fix: Christine WD P19 Venice → was macro=`italy`; `CTRL_REGION_OVERRIDE["Q234816"]=france`

## Also fixed this pass

- **Henry VIII** had fallen out of onsetish (Ilardi `probate_inventory` blocked candidates patch). Restored: Ilardi → `purchase_personal_use` 1545 + activity soft +2y.

## Primary after ingest

| | before densify note | after Baye+H8 restore |
|--|--:|--:|
| n pairs | 32 | **33** |
| median Δ | −1.0 | **−1.0** |
| boot CI | [−3, 1.3] | **[−4, 0.6]** |
| Baye Δ | — | **−12** (T=9 vs med C=21) |
| SESOI +5 / +15 | FAIL | **FAIL** (upper CI tighter) |

Baye’s large negative Δ is expected: short soft post-onset vs long French humanist careers. Does **not** move the SESOI story; strengthens exclusion of +5/+15 on the open contrast.

## Still open

Latone / Nuno Fernandes bios; more French *clerk* (not only humanist-relaxed) controls if SPARQL strata improve.
