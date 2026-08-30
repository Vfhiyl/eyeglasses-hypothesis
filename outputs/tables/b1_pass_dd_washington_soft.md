# Pass DD — ROI pick: Washington soft (Gray/Spinelli gated)

## Judgment

| Candidate next step | Verdict |
|---------------------|---------|
| Gray fragment restitch | Still undated account lines; Herle body not in fragments → **wait merge** |
| Spinelli Filza / HAB Wiesel–August | **No free OA** dated pins (reconfirmed) |
| New OA mine scout | **George Washington 1783** — Adams-class living self-wear |

Chose **Washington densify → soft ingest** over waiting on library/archive.

## Dig

| Date | Role | Pin |
|------|------|-----|
| 1783-01-10 | commission | GW→Tilghman sample lenses to Rittenhouse (ARI/Hektoen quote) |
| 1783-02-16 | **ONSET** | GW→Rittenhouse: “The Spectacles suit my Eyes extremely well” ([Founders](https://founders.archives.gov/documents/Washington/99-01-02-10654)) |
| 1783-03-15 | wear densify | Newburgh Address spectacles (Shaw eyewitness) |
| 1787-09-17 | output | Constitutional Convention |
| 1796-09-19 | ya terminus | Farewell Address — **not** death 1799 |
| 1799-12-14 | survival only | death |

Soft (`hard=False`): no post-1783 spectacle reaffirm. Chrono: `b1_washington_george_activity_chrono.csv`. Region: england Anglo densify.

## Plumbing

Collision audit false-positive: `George Washington` ↔ control **George Romney** (Q371280) via given-name `george` + birth±2. Hardened `scripts/30_…`: drop common given names from `name_lifespan` intersection. Active collisions → 0. Romney remains a valid artisan control for Peale.

## Remeasure (`B1_SPARQL=0`)

| Estimand | After Adams (DC) | After Washington (DD) |
|----------|------------------|------------------------|
| Labor | n=58 med 6.5 CI[4.0,9.5] | n=**59** med **7.0** CI[4.0,9.5] PASS_RAW |
| Output span45 | n=49 med 7.0 CI[6.0,9.0] | n=**50** med **7.5** CI[6.0,8.75] PASS_RAW |
| Washington labor Δ | — | **+8.0** (T=19, C med=11) |
| Italian merchant | FAIL | unchanged |
| Freeze gate | PASS | **PASS** |

+15 still FAIL. Causal still UNIDENTIFIED.

## Cache / notes

- Scout: `b1_mine_prospects_2026-08-06_pass_dd.md` ([scout agent](ccf34469-4fff-4b3c-9de7-090fe9bd5331))
- Gray restitch dump: `pass_dd_gray_restitch/gray_restitch_hits.csv` (still no year unlock)
- Sources: `pass_dd_washington/`

## Next ROI

1. Gray merge → Bourchier dates + Mrs Herle  
2. Archive Spinelli / HAB (merchant CI / August hard)  
3. Washington soft→hard only if later spectacle reaffirm  
