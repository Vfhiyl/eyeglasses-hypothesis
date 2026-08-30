# Pass BN — mid-neg reverse-lifespan rebalance (2026-08-05)

## Verdict

SESOI +5 remains **PASS_RAW** after lifespan-matching mid-negative Italy cells (same class of fix as BI Wyatt).

| | BM | **BN** |
|--|--|--|
| median Δ | 6.0 | **6.0** |
| CI | [3.0, 8.5] | **[3.0, 8.5]** |
| `barbara_brandenburg` Δ | −2 | **−1** |
| `ammannati` Δ | −1 | **0** |
| `pius_ii` Δ | −3 | **−1** |

## Issue

Vernia (d.@79) / Landino (d.@74) against Barbara (d.@59) and Ammannati (d.@57); Bessarion (d.@69) against Pius (d.@59) — reverse lifespan bias (long C spans).

## Fix

1. New curated `b1_output_control_excludes.csv` + loader in `27_b1_output_estimand.py` (per-wearer drop; keeps Vernia for Tranchedini, Bessarion for Sforza).  
2. Barbara overlays: drop Vernia/Landino; add Marcanova / Facio / Filetico / Ciriagio.  
3. Ammannati overlays: Marcanova / Facio / Filetico after exclude.  
4. Pius overlays: Filetico / Malermi after Bessarion exclude.

## HOLD

- `philippe_le_hardi` (−4): only two French cohort peers age 55–70 with years (Montreuil/Gerson); Clamanges (d.@74) kept for n≥3. No clean replacement without era mismatch.  
- Jeake/Leo: structural short-ya45 (Pass BK).

## Side effects

Tranchedini / Sforza / Charles Δ unchanged (shared long peers retained where appropriate).
