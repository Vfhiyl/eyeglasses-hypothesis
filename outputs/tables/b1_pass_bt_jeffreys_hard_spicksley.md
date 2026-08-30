# Pass BT — Jeffreys HARD via Spicksley OCR series (2026-08-06)

## Unlock / method

Same Spicksley loan as Pass BS (`businesshousehol0000unse`). Search-inside + BookReader OCR; later pins use OCR forms **`spectakles` / `specktacles`**, not only `spectacles`.

## Primary pins (FROM-her accounts)

| date | leaf / printed | text |
|--|--|--|
| **1639-10** | leaf 220 / p.175 | «For a paier of spectacles for my self» — **ONSET** |
| **1645** Jun–Aug | leaf 308 / p.263 | «Gave Jane Medowcoort for finding my purce and my silver-plate for my **spectakles**» |
| **1646** Jun–Jul | leaf 316 | «Gave Elinor Hill for finding the silven plate of my **specktacles** at Homcastle» (6d; Hubbard’s lost-spectacles tip = plate-of-spectacles find) |
| **1647-01** | leaf 320 / p.275 | burning glass London 4s (editor = magnifying glass) |
| 1648-06-27 | — | will / accounts end |
| 1650 | — | death terminus (WD); labor ya only |

## Curated impact

| | before (BS) | **BT** |
|--|--|--|
| evidence_year / onset | 1639 | **1639** |
| labor years_after | 11 (soft) | **11 HARD** |
| output pins | 1639;1647 | **1639;1645;1646;1647** (no death tip) |
| hard_dated_series | False | **True** |
| plateau tag | soft | `HARD_PassBT_Spicksley_series_1639_47` |

## Plumbing repair

`b1_roster_census.csv` had drifted to a truncated freeze (60 rows; labor KeyError). Rebuilt via `scripts/20_b1_roster_census_panel.py` (roster **99**). Activity proxy + census Jeffreys patched; remasures:

- **B1-Output** (`B1_SPARQL=0`): n=44, median **6.0**, CI **[3.0, 8.0]**, SESOI+5 **PASS_RAW** — unchanged (Jeffreys still `no_delta`, `n_ctrl_with_works=0`).
- **Primary labor**: Jeffreys ya **4→11**; T still death-capped at 30 → Δ **1.5** unchanged; all-treatments median Δ **1.5**, SESOI+5 FAIL.

## Loan scout (same pass)

| ID | Status |
|--|--|
| Gray `devonhouseholdac0000unse` | borrow **400** / unavailable |
| Dudley `householdaccount0000unse` | **browse_book OK** + token; search-inside + BR `callback=br&page=` |

### Dudley Leicester pin (HOLD — not yet rostered)

Leaf **390** / printed **~373** (Adams ed. household accounts):  
«Paied to Raffe Moore the same day for **iii payre of spectacles** at xijd the payre **to yor Ex: vse**»  
Clustered with **xxx Jan** / early Feb entries; editor note: Leicester Hague Jan **1585/6**. Personal use for Robert Dudley (Q318017). Fulltext only this account hit (+ index). Printed index **287 / 342** not recoverable in OCR (likely mis-index or OCR miss). Death 1588 → sole onset 1586 ⇒ labor ya≈**2** → **HOLD**, do not roster yet.

## Caches

`data/raw/external_mine_2026-08-03_early/pass_bt/`; chrono `b1_jeffreys_joyce_activity_chrono.csv`; Dudley leaves `dudley_leaf_*_clean.txt`, `dudley_spectacles_hits.md`.
