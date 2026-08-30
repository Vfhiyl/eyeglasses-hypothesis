# Pass BI — Wyatt outlier rebalance; hold SESOI +5 (2026-08-05)

## Verdict

SESOI +5 remains **PASS_RAW** after correcting Wyatt reverse-lifespan bias.

| | BH | **BI** |
|--|--|--|
| median Δ | 6.0 | **6.0** |
| CI | [3.0, 9.5] | **[3.0, 8.75]** |
| `wyatt_henry` Δ | **+19** | **+7** |
| `domenichi` Δ | −5.5 | **−2.5** |

### Robustness

| stress | median | CI | SESOI +5 |
|--|--|--|--|
| death-strip (keep office) | 5.0 | [1.5, 7.5] | PASS |
| Wyatt Δ → 0 | 5.0 | [2.0, 8.75] | PASS |

## Wyatt issue

BH overlayed Bainbridge/Colet (age@death ≈50–52) against Wyatt (d.1537 @77) → ctrl med 7 vs treat span 26 → Δ=+19 (reverse of Jackson/Jeake bias).

### Fix

- Drop Bainbridge/Colet overlays for Wyatt  
- Unlock Warham (archbishop mid pins)  
- Restore Mair with trimmed years (no 1550 death)  
- Overlay Stokesley + Blythe  
- Harvest LP chrono 1527–1531 (no death 1537)

## Jeake

Δ=−5, ya45=2 — structural short post-45 life; already lifespan-matched. **HOLD**.
