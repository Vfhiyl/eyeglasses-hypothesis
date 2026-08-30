# Pass CU — cleaning sensitivity (why PASS_RAW is not “washed into existence”) (2026-08-06)

## Judgment

Highest ROI after CT: **document the cleaning contrast**, not dig dry mines or reopen Pass BX René unlocks (already tried → SESOI hurt).

Question: did reverse-lifespan / overlay hygiene *manufacture* SESOI+5?

## Labor primary — three arms (same roster matches file)

Recomputed 2026-08-06 with `b1_roster_control_matches_region.csv` + current curated chronos.

| Arm | What changes | n | median Δ | boot 95% CI | SESOI+5 | SESOI+15 |
|-----|--------------|--:|---------:|-------------|---------|----------|
| **dirty_max** | Raw matches; force `use_in_primary` on all chronos (re-includes demoted Locke/Priestley/Burke-class contamination) | 60 | 2.0 | [-1.47, 7.0] | FAIL | FAIL |
| **raw_match** | Raw matches only; **no** overlays/excludes; demotions respected | 60 | 1.05 | [-3.0, 7.0] | FAIL | FAIL |
| **full_clean** (current freeze) | Overlays + per-wearer excludes + drop death&lt;45 / T≤0 | 57 | 6.0 | [3.5, 9.0] | PASS_RAW | FAIL |

Table file: `b1_labor_cleaning_sensitivity.csv`.

### Reading

1. **raw_match med ≈ 1.05, CI crosses 0** — reproduces the pre–Pass CO labor story (dirty longevity densify).
2. **full_clean med = 6.0, CI [3.5, 9.0]** — current freeze; hygiene removes survival/post-death bias.
3. **SESOI+15 FAIL in every arm** — cleaning does **not** rescue Macfarlane +15.
4. Demotions of known wearers (Locke/Priestley/Burke) belong in both science and the “raw_match” arm (they stay out); `dirty_max` shows how much worse contamination makes CI.

## Fragile n=1 — no unlock this pass

| Cell | Status |
|------|--------|
| Nicolas | Only Premierfait left after reverse excludes — no honest second peer in pool |
| Domenichi | Only Lando; Maioragio/Amico die before 45 |
| René Anjou (output) | Jouffroy only; Chastellain/Fillastre stay `output_eligible=False` (Pass BX unlock dropped panel med 5→4 — **do not reopen**) |

## Freeze (unchanged — no remasure needed)

| Estimand | n | med | CI | SESOI+5 | SESOI+15 |
|----------|--:|----:|----|---------|----------|
| Labor full_clean | 57 | 6.0 | [3.5, 9.0] | PASS_RAW | FAIL |
| Output | 48 | 7.0 | [5.0, 8.5] | PASS_RAW | FAIL |

## Claim language

- Cleaning is **measurement correction**, not optional cherry-picking of a preferred result.
- Allowed: weak direction PASS_RAW on cleaned open contrast.
- Forbidden: “+15 typical unlock”; causal ID; ignoring the raw_match FAIL arm in methods discussion.

## Next ROI

1. Physical densify (Keil/HAB, Yale Spinelli, Gray).
2. Keep sensitivity table next to any claim write-up.
