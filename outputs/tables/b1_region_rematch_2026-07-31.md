# Region-aware rematch (2026-07-31)

## Why

Birth+occupation matching alone produced absurd pairs (e.g. Datini↔Shen Wansan).
Pre-reg required macro-region. This pass enforces it.

## Results

| | |
|--|--|
| Onsetish with birth | 36 |
| Any match | 36 |
| **Strict region match** | **36** |
| Unmatched | 0 |
| Match levels | occ+birth+region:31;occ_relaxed+region:5 |
| Median Δ ya45 (strict) | 6.0 |
| SESOI +5 / +15 ya45 | PASS_RAW / FAIL_OR_UNAVAILABLE |
| Work-proxy overlay n | 17 |
| Work-proxy median Δ | 11.0 |

## Files

- `b1_roster_control_matches_region.csv`
- `b1_roster_control_summary_region.csv`
- `b1_roster_control_p50_overlay_region.csv`
- `b1_person_macro_region.csv`

## Read

Region filter shrinks usable contrasts but **raises credibility**. Prefer these tables over non-region matches for any claim language.
