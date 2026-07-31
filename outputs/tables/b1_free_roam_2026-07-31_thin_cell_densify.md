# Thin-cell densify: Gonzaga / Barbara / Leo X / Sforza (2026-07-31)

## Decision

Chose **deep densify** of n_ctrl=1 Italy cells over another Latone/Nuno wearer hunt (bios still closed). Italy SPARQL ruler/cleric strata in the birth windows were empty beyond Borso / Memmo.

## Injects

**Italy rulers** (pool + curated + region=`italy`):

| QID | Name | Birth–death | Unlocks |
|-----|------|-------------|---------|
| Q435501 | Federico da Montefeltro | 1422–1482 | Gonzaga / Barbara |
| Q506640 | Sigismondo Malatesta | 1417–1468 | Gonzaga / Barbara |
| Q1125744 | William VIII Montferrat | 1420–1483 | Gonzaga / Barbara |
| Q1348708 | Ercole I d'Este | 1431–1505 | Barbara |
| Q289285 | Filippo Maria Visconti | 1392–1447 | Sforza |
| Q430565 | Gianfrancesco I Gonzaga | 1395–1444 | Sforza |

**Italy clerics** (cohort `strata_cleric` — script now maps this → `cleric`):

| QID | Name | Birth–death |
|-----|------|-------------|
| Q682478 | Jacopo Sadoleto | 1477–1547 |
| Q728931 | Gasparo Contarini | 1483–1542 |
| Q133001 | Paul III | 1468–1549 |
| Q334188 | Pietro Bembo | 1470–1547 |
| Q823002 | Bibbiena | 1470–1520 |
| Q83159 | Clement VII | 1478–1534 |

**Bucket overrides:** Giles of Viterbo / Cajetan (`wd_scholar_*_philosopher` → `cleric`).

**Rejected:** Leonello d'Este (d. age 43) — briefly stole Sforza’s strict match with `use_in_primary=False` / C=0; removed from pool.

## Primary cell sizes

| Treatment | n_ctrl before | after | Δ before → after |
|-----------|--------------:|------:|------------------|
| gonzaga_ludovico | 1 | **4** | 3.0 → **2.0** |
| barbara_brandenburg | 1 | **5** | −1.0 → **−3.0** |
| leo_x | 1 | **9** | −23.0 → **−19.0** |
| sforza_francesco | 7 (relaxed humanist) | **2** (strict ruler) | 2.0 → **13.0** |

Sforza’s jump: strict Italy rulers replace occ_relaxed humanists; shorter-lived Visconti/Gianfrancesco pull med C down (7). Preferred match quality; not a SESOI unlock.

## Overall primary

| | before | after |
|--|--:|--:|
| n pairs | 33 | **33** |
| median Δ | −1.0 | **−1.0** |
| boot CI | [−4, 0.6] | **[−4, 0.6]** |
| SESOI +5 / +15 | FAIL | **FAIL** |

## Code

- `scripts/24_b1_region_rematch.py`: `strata_cleric` → cleric; `CTRL_BUCKET_OVERRIDE` for Giles/Cajetan.
