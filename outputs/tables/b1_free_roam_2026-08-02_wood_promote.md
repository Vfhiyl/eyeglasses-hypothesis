# Anthony Wood formal promote (2026-08-02)

## Decision

Full authority promote of **Anthony Wood** (`wood_anthony`, Q691873) into the B1 primary estimand path.

## Evidence bar

| Bar | Result |
|-----|--------|
| Living personal-use onset | PASS — diary 1675-03-09 + EMLO self-draft 1676-12-27 |
| Birth / death | PASS — 1632 / 1695 |
| Post-wear near-work chrono | PASS — `b1_wood_anthony_activity_chrono.csv` |
| `years_after_evidence` | **17** (Athenae Oxon. vol. II, 1692-07-18) |
| `hard_dated_series` | True |
| Onsetish | True (`diary_receipt_and_self_draft_letter`) |

## Control densify (blocker cleared)

Pool had **zero** region-known controls in birth±10 of 1632. Injected 12 England humanist peers + curated near-work chronos (`source=densify_2026-08-02_wood`).

Excluded: Pepys (known wearer); Aubrey (EMLO spectacles correspondent); Glanvill / Willughby (die &lt;45); Newton (birth calendar edge for ±10).

## Wood primary cell

| | |
|--|--|
| Match | `occ+birth+region` |
| n_ctrl primary | **12** |
| T_work_after_45 | **15** |
| med C | **21** |
| Δ | **−6.0** |

## Primary freeze update

| | before | after |
|--|-------:|------:|
| n pairs | 37 | **38** |
| median Δ | −2.97 | **−2.99** |
| boot 95% CI | [−4.0, 2.0] | **[−5.0, 2.0]** |
| SESOI +5 / +15 | FAIL | **FAIL** |
| B1 causal ID | UNIDENTIFIED | **UNIDENTIFIED** |

Scripts: `20` → `24` (`B1_SPARQL=0`) → `25` → `26`.
