# Control OA near-work densify (2026-07-31)

## Direction

Freeze n-expansion; improve **control near-work** on region-matched pairs (Italian merchants first).

## Curated controls

File: `data/curated/b1_control_nearwork_chrono_curated.csv` (n=10)

| QID | Person | last near-work | years after 45 | conf |
|-----|--------|---------------:|---------------:|------|
| Q10946745 | Andrea Barbarigo | 1449 | 5 | high (accounts 1430–34 + Lane) |
| Q659093 | Benedetto Dei | 1492 | 29 | high (cronica 1473 + letters →1492) |
| Q93113 | Coluccio Salutati | 1406 | 30 | high (chancellor/epistolario) |
| Q1296705 | Giovanni Dondi | 1388 | 13 | medium |
| Q508702 | Filippo Villani | ~1405 | 35 | medium |
| Q3388274 | Pigello Portinari | 1468 | 2 | medium |
| Q708954 | Filippo Strozzi Jr | 1538 | 4 | medium |
| Q55228138 | Gherardo del Ciriagio | ~1470 | 13 | medium |
| Q16586697 | Pandolfo Rucellai | 1497 | 16 | low |
| Q721857 | Giovanni Arnolfini | 1472 | 27 | low |

## Overlay after merge

`b1_roster_control_nearwork_overlay_region.csv`

| | |
|--|--|
| Pairs with any control near-work | **19** |
| Median Δ (T−C) work_after_45 | **4.0** |
| Bootstrap 95% CI (approx) | **[−1.5, 12]** |
| Pairs with ≥1 curated control | **6** |
| Median Δ on that subset | **~1** |

### Merchant cells (the point of this pass)

| treatment | Δ vs curated controls |
|-----------|----------------------:|
| datini | **0** |
| strozzi_filippo | **0** |
| ardingelli_bese | **−13** |
| spinelli_benedetto | **+2** |

## Read

When controls get real mercantile/letter chronologies, the apparent wearer advantage **collapses** toward zero (or negative).  
Earlier WD-only PASS_RAW on +5 does **not** survive this check.

Macfarlane +15: **still fail**.  
B1 causal: **still unidentified** — but the measurement path is now doing the right work.

## Next

1. More high-confidence merchant account/letter series (Portinari letters OA?; Medici bank pubs).  
2. Downgrade/drop low-confidence Arnolfini/Rucellai in sensitivity.  
3. Keep freeze on wearer #35.
