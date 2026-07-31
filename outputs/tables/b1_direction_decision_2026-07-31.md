# B1 direction decision (2026-07-31)

## Judgment

**Matching n is no longer the bottleneck.** Onsetish 34; primary occ-matched 29; control pool ~2341.  
Further name-hunting / control-stratum expansion has **low ROI** for identification.

**Bottleneck = measurement of near-work on both sides of matched pairs**, especially controls.

## Freeze (adopted)

| Stop prioritizing | Do instead |
|-------------------|------------|
| Hard n hunting as main goal | Keep hard as appendix only |
| Growing roster / control n | Measure the existing 29 matched pairs |
| More SPARQL strata for its own sake | Letter/account chronologies + spectacle-negative audits |

## Done this pass

### 1. P50 near-work densify (`scripts/23_b1_control_p50_nearwork.py`)

Matched-control SPARQL: author-of (P50) → dated works.

| | |
|--|--|
| Controls with sane P50 years | 34 / 343 |
| Pairs with Δ | **13** |
| Median Δ work_after_45 | **9.5** |
| Bootstrap 95% CI | **[5.5, 16.0]** |
| Δ≥5 / ≥15 | 10 / 5 |
| n_ctrl≥3 subset median (CI) | 10.0 ([5.5, 38.0]) |

**Read:** CI excludes 0 and clears direction SESOI **+5** on this WD proxy (**PASS_RAW**). Median **9.5** does **not** clear Macfarlane **+15** (CI upper touches 16 but point estimate fails).  
Still **not** B1 identification: WD pubs ≠ letter near-work; controls not archive-verified non-wearers; n=13 thin.

### 2. Spectacle-negative spotcheck (strict)

`b1_control_spectacle_negative_spotcheck.csv` — 40 random matched controls vs Ilardi OCR; distinctive surname tokens ≥6 chars.

- Strict name∩glass window hits: **5/40** (mostly false friends / shared tokens)
- No-hit **87.5%** ≠ proof of non-wear  
- Auto OCR co-occurrence is **not** a reliable negative test; human reading still required.

## Verdict snapshot

See `b1_roster_verdict.csv`:

- ya45 contrasts: fail +5/+15  
- P800/P50 work proxies: PASS_RAW on +5; FAIL on +15  
- B1 near-work causal: **UNIDENTIFIED**  
- Direction: **FREEZE_N_EXPAND_MEASURE**

## Next worth doing (ordered)

1. **Human/OA letter chronologies** for 3–5 closest controls of the ~16 treatments still without P50 coverage (or all 29 at lower depth).  
2. Hand-audit the 5 OCR “hits” + a 20-control random sample for true spectacle mentions.  
3. Do **not** chase wearer #35 or another thousand WD controls unless measurement for current pairs is stuck.
