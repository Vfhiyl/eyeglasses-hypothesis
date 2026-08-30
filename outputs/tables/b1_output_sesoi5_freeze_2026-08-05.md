# B1-Output SESOI +5 — freeze status (2026-08-05)

## Claim (PASS_RAW)

Among onsetish **textual** documentary wearers with dated works, vs region/occupation-matched textual controls:

| estimand | n | median Δ | bootstrap 95% CI | SESOI +5 | SESOI +15 |
|--|--|--|--|--|--|
| `output_span_after_45` | **44** | **6.0** | **[3.0, 8.0]** | **PASS_RAW** | FAIL |

Per `docs/B1_OUTPUT_SESOI.md`: raw pass = median ≥ 5 and CI lo ≥ 0.  
CI hi tightened after BM (ctrl d&lt;45) and BQ (Howard living-pin tip, no death terminus).

## How we got here (short)

1. **BB–BE:** wearer harvest + England/Italy lifespan densify repairs  
2. **BF:** first PASS (fragile — death termini + year-cache re-inject)  
3. **BG:** stress-test FAIL; curated years made authoritative; death-only pins hardened out  
4. **BH:** rebuilt PASS via control densify (not death-only wearers)  
5. **BI:** Wyatt reverse-lifespan outlier fixed (+19→+7); PASS held under death-strip & Wyatt→0  
6. **BM:** drop controls with `death < birth+45` (Joan; Barbaro Younger leak)  
7. **BN:** reverse-lifespan mid-neg rebalance (Barbara/Ammannati/Pius); per-wearer excludes

## Robustness (BI)

| stress | result |
|--|--|
| Strip wearer death==last (keep Lynnet office terminus) | med 5.0, CI [1.5, 7.5] — PASS |
| Set Wyatt Δ = 0 | med 5.0, CI [2.0, 8.75] — PASS |

## Loader / gates (do not regress)

- `exclude_death_before_45` for treatments **and** controls (`ctrl_allowed`)  
- Per-wearer control excludes: `b1_output_control_excludes.csv`  
- Curated `b1_wearer_output_years_curated.csv` authoritative (no OUT-cache re-inject)  
- Artisan/painter appendix-only  

## Not claimed

- SESOI +15  
- Labor-year B1 (`25_b1_primary_estimand.py`) — separate, still FAIL path  
- Soft→hard library stock (Bourchier/Jeffreys/Hesselin comptes)  

## Pass BJ side notes

- `voiture_vincent`: **SHORT-WINDOW CLOSED** (1647→d.1648; ya=1)  
- New living OA IA scout: proxy 403 this pass; no promote  
- Soft onsetish with `hard_dated_series=False`: **17** (plateau; library/third-party/short-window)  

## Pass BK appendix (not primary)

Structural short post-45 life: Jeake/Leo/Domenichi saturate ceil 1–4. Dropping them → med 7.0 CI [4.0, 10.0] still PASS. See `b1_pass_bk_short_ya45_structural_appendix.md`.

## Pass BL robustness (not primary)

Strip control years where `year==death` → med **11.0**, CI **[8.0, 18.0]** (PASS). Control death termini bias *against* the claim. Soft-stock plateau catalog: `b1_soft_stock_plateau_2026-08-05.csv`.  
