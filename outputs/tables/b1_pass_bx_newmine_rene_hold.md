# Pass BX — new-mine dry; René Anjou densify HOLD (2026-08-06)

## New-mine / Gray

| vein | result |
|--|--|
| Gray IA | still gated (browse/borrow 400 / advancedsearch SSL EOF) |
| Costume Historian | **HTTP 403** |
| Gallica SRU | **HTTP 403** |
| Google Books API | **HTTP 429** |
| IA page_production (Herle/Bourchier; lunettes René; "pair of spectacles") | junk hits or **dry** |
| IA advancedsearch texts 1400–1800 Cleux phrase | **0** |
| Dudley Leicester OCR re-scan | sole personal pin 1585/6; ya≈2 → **HOLD** (no second pin) |

**No new Cleux-bar named wearer.** Mrs Herle still Gray-library-gated.

## Plumbing trials (not kept)

### Joris / Spinelli / Henry — skip

| cell | why left alone |
|--|--|
| `joris_van_der_paele` | wearer pin confidence **low** (portrait-only) → would hit `exclude_coverage_low_pin` even after Flanders peer unlock |
| `spinelli_benedetto` | labor still TO-him; matched merchants OA-thin / `non_textual_or_admin` |
| `henry_viii` | output years 1521;1527 are pre-45 → T span 0; structural short window; Elyot alone would add ≈Δ−1 |

### René Anjou densify — tried, reverted

Already in primary with **n_ctrl=1** (Jouffroy) and inflated Δ=**+10**. Overlays for Chastellain / Fillastre already existed but `output_eligible=False` (Pass BH Charles mismatch).

| step | result |
|--|--|
| Flip elig True + `charles_orleans` excludes (preserve BH) | René n=3; Δ **+10→+1**; Hesselin gains Chastellain (Δ 18→17); Charles unchanged |
| Remeasure | n=47, med **5.0→4.0**, CI [1.5, 8.0], SESOI+5 **FAIL** |
| Revert | elig back False; charles excludes removed; freeze restored |

**HOLD:** do not densify René Anjou’s literary peers until other positive primary mass offsets the artifact correction (or claim rewrite accepts lower median).

Short-ya45 (Jeake/Leo/Domenichi) already documented in Pass BK — **not** moved into primary.

## Remeasure (`B1_SPARQL=0`)

| | Pass BW | **BX** |
|--|--|--|
| n | 47 | **47** |
| median Δ | 5.0 | **5.0** |
| boot95 CI | [2.0, 8.0] | **[2.0, 8.0]** |
| SESOI+5 | PASS_RAW | **PASS_RAW** |

## Next ROI

1. **Gray 1996** when borrowable — Bourchier labor + Mrs Herle bio.  
2. New Cleux-bar ore outside IA/Gallica 403 zone (library OCR / local PDFs).  
3. Keep René Anjou thin-peer HOLD; Spinelli/Dudley HOLD; do not reopen Brittany / Walmysford / Digitarq Contos / Jeffreys Spicksley.
