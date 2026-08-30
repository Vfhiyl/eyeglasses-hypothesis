# William Lynnet formal promote (2026-08-02)

## Decision

Continue letter-path after Wood: promote **William Lynnet** (`lynnet_william`) on the same living-onset + dated post-wear bar.

## Evidence bar

| Bar | Result |
|-----|--------|
| Living personal-use onset | PASS — EMLO self-report 1672-08-07: “has just been to London to **buy a pair of spectacles**” |
| Birth / death | PASS — EMLO 1623–1700 (Trinity archives c.1622–1700; keep EMLO integers) |
| Post-wear near-work chrono | PASS — `b1_lynnet_william_activity_chrono.csv` |
| `years_after_evidence` | **28** (Vice-Master tenure through 1700) |
| `hard_dated_series` | True |
| Onsetish | True (`self_report_letter_purchase` → high) |

### Post-wear pins

| Date | Pin |
|------|-----|
| 1677–1684 | Senior Dean, Trinity |
| 1683 | Senior-fellow testimonial signature (CUL Add.2717.6) |
| 1686–1691 | Senior Dean again |
| 1687-04-19 | Letter to Alexander Akehurst (Trinity O.11a.1/1) |
| 1691–1700 | Vice-Master (Trinity Admissions) |

Sources: EMLO; *Trinity College Admissions* (Ball / Rouse Ball) officer lists vol. II p.371.

## Control densify

England ~1623 **cleric** peers (Tillotson, Patrick, Lloyd Q8014632, Sancroft, Compton, Pearson) + curated near-work. Match → **`occ+birth+region`**, n_ctrl=**6**.

## Lynnet primary cell

| | |
|--|--|
| T_work_after_45 | **32** |
| med C | **30.5** |
| Δ | **+1.5** |

## Primary freeze update

| | after Wood | after Lynnet |
|--|----------:|-------------:|
| n pairs | 38 | **39** |
| median Δ | −2.99 | **−2.97** |
| boot 95% CI | [−5.0, 2.0] | **[−4.0, 2.0]** |
| SESOI +5 / +15 | FAIL | **FAIL** |

## Soft-neg note (Wood densify)

Wood densify QIDs (Locke/Boyle/Hooke/…) not on Ilardi/candidates roster; EMLO spectacles dump has no personal-wear hits for them (substring false-positives only). Full hand archive audit still open.

## Charlett

**Arthur Charlett** remains soft-hold / `exclude_low_confidence`: 1707 letter is a wear-duration *ask*, not dated first-use. Do not promote without firmer onset.
