# Densify: Domenichi + Henry VIII (2026-08-01)

## Direction

Short OA roam (IA greffier/notaire + SPARQL England) was dry/timeout. Chose **deep densify** of two fragile extreme/thin cells:

1. `domenichi_ludovico` — Δ −17.5, only 2 curated peers among many matched humanists  
2. `henry_viii` — n_ctrl_primary=**1** (Brandon only; Arthur dies young)

## Domenichi (Italy humanist, b.1515)

Added curated chronos for already-matched peers:

| QID | Name | ya45 | primary |
|-----|------|-----:|---------|
| Q3778928 | Grataroli | 7 | True (high) |
| Q104099062 | Visdomini | 12 | True |
| Q21545214 | Rasario | 16 | True |
| Q3742149 | Figliucci | 27 | True |
| Q18945465 | Borro | 33 | True |
| Q19818775 / Q3766049 / Q18945353 | Maioragio / Amico / Gabriele | 0 | **False** (die &lt;45) |

| | before | after |
|--|--:|--:|
| n_ctrl primary | 2 | **7** |
| med C | 21.5 | **16** |
| Δ | −17.5 | **−12** |

## Henry VIII (England ruler, b.1491)

Injected Tudor peers in birth±10:

| QID | Name | ya45 | primary |
|-----|------|-----:|---------|
| Q3990688 | Thomas Manners, Rutland | 6 | True |
| Q5540308 | George Hastings, Huntingdon | 11 | True |
| Q7287908 | Ralph Neville, Westmorland | 7 | True |
| Q518521 | Henry Courtenay, Exeter | 0 | **False** (executed ~40) |

| | before | after |
|--|--:|--:|
| n_ctrl primary | 1 | **4** |
| med C | 16 | **9** |
| Δ | −5 | **+2** |

## Primary panel

| Metric | before | after |
|--------|-------:|------:|
| n pairs | 37 | **37** |
| median Δ | −0.5 | **0.0** |
| boot CI | [−3, 4.5] | **[−3.0, 4.5]** |
| SESOI +5/+15 | FAIL | **FAIL** |

Henry’s move (−5→+2) nudges the median off −0.5; Domenichi densify reduces an outlier but does not flip SESOI.
