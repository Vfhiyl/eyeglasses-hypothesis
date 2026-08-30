# Free roam → Denis Hesselin + egidio region fix (2026-07-31)

## Decision

Laborde named-onset leads exhausted → free-roam **Heymann *Lunettes et Lorgnettes de Jadis*** (IA `b2486092x`, already OA under `data/raw/burgundy/`) rather than another Latone/Nuno stall.

## Promoted: Denis Hesselin / Hasselin

| Fact | Source |
|------|--------|
| Office | Prévôt des Marchands de Paris (1470–74); Receveur de la Ville (1474–1500); Receveur des Aides (1474–1506) |
| Birth / death | ~1425 / after 1506 (Pattou LGN *Hesselin.pdf*; death terminus conservatively **1506**) |
| Evidence | Compte Jean Luillier 1473–74: *paire de lunettes clouants* **pour** mondit seigneur Le Prévost (sire Denis Hasselin), *parce qu'il n'en avoit eu que une paize qui n'estoient pas clouants* |
| `years_after` | **32** (soft; hard=False) |
| Bucket / region | `city_receveur_clerk` → clerk / **france** |

Files: `b1_hesselin_denis_chrono.csv`; activity proxy row; candidates row.

## France clerk densify (birth ±10 of 1425)

| QID | Control | Primary ya45 |
|-----|---------|-------------|
| Q3170939 | Jean Bourré | 37 |
| Q288378 | Olivier le Daim | 11 |
| Q42027400 | Jean III Robertet | 17 |
| Q2823945 | Adam Fumée | 19 |
| Q3170994 | Jean Briçonnet | 28 |

Match: **occ+birth+region**, n_ctrl_primary=5. Hesselin Δ **+17**.

## Side fix

`egidio_piacenza` TREAT region **unknown → italy** (Fra Egidio da Piacenza / Florence age-band order). Primary Δ **−26 → +1** (still thin n_ctrl=1).

## Logged only

| Lead | Why not |
|------|---------|
| John Baret of Bury will 1463 (`tymms_wills`): *peyre spectaclys of syluir and ouyr gylt* to Davn John Ixnyng | Will gift to third party; Ixnyng birth unknown; will path |
| Latone / Nuno | Still no hard birth–death |

## Primary

| | before | after |
|--|--:|--:|
| n pairs | 36 | **37** |
| median Δ | −0.75 | **0.0** |
| boot CI | [−3.0, 3.3] | **[−2.5, 2.1]** |
| n≥15 | 2 | **3** |
| SESOI +5 / +15 | FAIL | **FAIL** |
| Causal B1 | UNIDENTIFIED | **UNIDENTIFIED** |
