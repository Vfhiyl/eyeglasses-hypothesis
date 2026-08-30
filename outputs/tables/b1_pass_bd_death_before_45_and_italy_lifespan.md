# Pass BD — death-before-45 exclude + Italy lifespan match (2026-08-05)

## Problem

Worst primary Δs were structural short post-45 life, not missing pins:
- `bianca_maria` / `lorenzo_medici` die **@43** → `t_span45` locked at 0
- `leo_x` dies @46 (max span≈1) vs long cardinal fallbacks (cmed 22)
- `domenichi` dies @49 (max span≈4) vs long humanist densify (cmed 16)

## Fix

1. **Code:** `exclude_death_before_45` in `27_b1_output_estimand.py` primary gate.
2. **Leo X:** retire long fallback peers; overlay Bibbiena / Castiglione / Bainbridge (age@death≈50).
3. **Domenichi:** retire Zoppio/Borro/Figliucci/Rasario; add Robortello; keep Grataroli/Visdomini/Tomitano.

## Moves

| person | before | after |
|--------|--------|-------|
| `bianca_maria` | −28 primary | **excluded** |
| `lorenzo_medici` | −11 primary | **excluded** |
| `leo_x` | −21 | **−4** |
| `domenichi_ludovico` | −12 | **−5.5** |

## Primary

n=**44**; median Δ **0.0 → 0.5**; CI **[−2.0, 7.0]**; share Δ>0=**0.5**; SESOI still FAIL.
