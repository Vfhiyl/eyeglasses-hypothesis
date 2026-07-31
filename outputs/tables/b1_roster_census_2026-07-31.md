# B1 roster census — status (2026-07-31 evening)

## Direction

Hard n≥20 = appendix. Main path = **roster census + controls**.  
Scripts: `20_b1_roster_census_panel.py`, `21_b1_control_pool_v3.py`, `22_b1_roster_occ_match_and_p800.py`

## Consolidated verdict

See `b1_roster_verdict.csv`.

| Check | Result |
|------|--------|
| Onsetish activity coded | **32/32**, median **8.5y**, ≥15 share **0.28** |
| Hard appendix bias | hard median **13** vs ungated **8.5** |
| SESOI +5 on ya45 (birth±10) | **FAIL** (Δ −1) |
| SESOI +5 on ya45 (primary occ+birth, n=20) | **FAIL** (Δ +2.0) |
| SESOI +15 on ya45 | **FAIL** |
| SESOI +5 on P800 work overlay | **PASS_RAW** (median Δ +6.5, n=20; thin) |
| SESOI +15 on P800 work | **FAIL** (4/20 pairs) |
| B1 near-work causal | **UNIDENTIFIED** |

## Matching

| Level | n | Meaning |
|-------|--:|---------|
| occ+birth | 20 | primary bucket (now includes ruler/artisan strata) |
| occ_relaxed | 7 | secondary (merchant/clerk/admin → humanist; merchant SPARQL failed) |
| birth_only | 0 | — |

Control v3 expanded with SPARQL **ruler n≈340** + **artisan n≈214** (`b1_control_strata_extra.csv`); merchant query empty-reply ×3.

## P800 densify

- SPARQL batch over matched controls (1×502); sane dated works ≈ **42** persons
- Overlay: `b1_roster_control_p800_overlay_occ.csv`
- Re-run densify: `B1_SPARQL=1 .venv/bin/python -u scripts/22_b1_roster_occ_match_and_p800.py`

## Next ROI

1. Build merchant/ruler control strata (not only WD philosophers).  
2. Letter/account near-work for controls (not only P800).  
3. Keep hard hunt frozen.
