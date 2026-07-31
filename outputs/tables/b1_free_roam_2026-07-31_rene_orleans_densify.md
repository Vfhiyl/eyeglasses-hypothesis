# Recovery + René densify + Orléans control restore (2026-07-31)

## Decision

1. Finish SPARQL rebuild of wiped `b1_person_macro_region.csv` (blocker from prior pass).
2. Deep-densify **René II** France ruler cell (was stuck on occ_relaxed humanists → Δ −25.5).
3. Restore **Philip the Good** as Orléans control (he had been parked on candidates as living-inventory → excluded from control pool).

## Region rebuild

- `B1_SPARQL=1` rematch completed (~2112 QIDs; some 502/empty-reply chunks skipped).
- Primary recovered from corrupted **n=1** → **n=36**.

## Logged only (not onsetish)

| Person | Why not promoted |
|--------|------------------|
| Philip the Good (Q239337) | Living inventaire / `Y me tarde` estuy — possible heirloom from Philippe le Hardi |
| Jeanne d’Évreux | 1371 testament `veriule` — will path |

Removed both from `b1_named_wearers_candidates_new.csv` so their QIDs stay usable as controls. Philip remains curated `use_in_primary=True` for Orléans.

## René II densify (france rulers, birth ±10 of 1451)

| QID | Control | Birth–death | Primary? |
|-----|---------|-------------|----------|
| Q1379932 | Gilbert of Montpensier | 1443–1496 | True (ya45≈8) |
| Q1313351 | Louis II de la Trémoille | 1460–1525 | True (ya45≈20) |
| Q728786 | Charles of Valois, Duke of Berry | 1446–1472 | False (dies age 25) |

Match level: **occ_relaxed+region → occ+birth+region**.

## Primary deltas (key cells)

| Wearer | Before | After |
|--------|--------|-------|
| Charles d’Orléans | Δ **+14.5** (n_ctrl=4) | Δ **+13.0** (n_ctrl=5, +Philip Good) |
| René II | Δ **−25.5** (Lefèvre/Pèlerin) | Δ **−2.0** (Gilbert/Trémoille) |
| Philippe le Hardi | −0.5 | −0.5 |
| Nicolas de Baye | −12.0 | −12.0 |

## Overall primary

| | |
|--|--|
| n pairs with Δ | **36** |
| median Δ | **−0.75** |
| boot 95% CI | **[−3.0, 3.3]** |
| SESOI +5 / +15 | **FAIL** / **FAIL** |
| Causal B1 | **UNIDENTIFIED** |

Rematch `median Δ ya45` (=6.0) is **not** the frozen primary estimand; do not cite it for SESOI claims.

## Still open

- Latone / Nuno: no hard birth–death for ingest
- Philip the Good: promote only if compte vs nachlass personal onset can be pinned
