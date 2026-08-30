# Region-aware rematch (2026-07-31)

## Why

Birth+occupation matching alone produced absurd pairs (e.g. Datini↔Shen Wansan).
Pre-reg required macro-region. This pass enforces it.

## Results

| | |
|--|--|
| Onsetish with birth | 69 |
| Any match | 68 |
| **Strict region match** | **67** |
| Unmatched | 1 |
| Match levels | birth_only:1;occ+birth+region:65;occ_relaxed+region:2 |
| Median Δ ya45 (strict) | 8.5 |
| SESOI +5 / +15 ya45 | PASS_RAW / FAIL_OR_UNAVAILABLE |
| Work-proxy overlay n | 21 |
| Work-proxy median Δ | 6.0 |

## Files

- `b1_roster_control_matches_region.csv`
- `b1_roster_control_summary_region.csv`
- `b1_roster_control_p50_overlay_region.csv`
- `b1_person_macro_region.csv`

## Read

Region filter shrinks usable contrasts but **raises credibility**. Prefer these tables over non-region matches for any claim language.
