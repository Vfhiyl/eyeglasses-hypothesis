# Pass BG — SESOI +5 death-terminus stress-test (2026-08-05)

## Verdict

**BF `PASS_RAW` does not survive stress-test.** After (1) making curated wearer years authoritative and (2) replacing pivotal death-only termini with documentary pins, primary returns to:

| | |
|--|--|
| n | 44 |
| median Δ | **3.25** |
| bootstrap 95% CI | **[0.0, 8.0]** |
| SESOI +5 | **FAIL_OR_UNAVAILABLE** |
| SESOI +15 | FAIL |

CI lo still ≥0, but median <5.

## Root causes of BF fragility

1. **Death==last pins** on many primary wearers (24/44 before harden). Leave-one-out before harden showed stripping any of `cederni` / `pepys` / `lynnet` / `jackson` / `cowper` / `marzeliere` death termini alone flipped PASS→FAIL.
2. **Cache re-injection bug:** `load_local_wearer_years()` unioned prior `b1_wearer_output_years.csv` with curated years, so removing a death year from curated did not stick.

## Code fix

`27_b1_output_estimand.py`: if a person_id has curated output years, those years are **authoritative** (prior OUT cache and P50/P800 are not merged into the union for that pid).

## Harden (kept)

| person | change |
|--------|--------|
| `pepys_samuel` | Christ's Hospital letters 1698/1699 + library catalogue Michaelmas 1700; drop d.1703 |
| `cowper_william` | Hesketh letter 1798-12-08; drop d.1800 |
| `jackson_ralph` | diary continuum through 1789; drop d.1790 |
| `marzeliere_pierre` | last hard admin 1457 Hedé; drop d.1462 |
| `cederni` | civic last Buonuomo 1478; drop burial 1482 |
| `lynnet_william` | keep 1700 as **Vice-Master office terminus** (not death-only) |

## Implication

Do **not** claim SESOI +5 from BF without caveating death-terminus dependence. Path back to PASS_RAW requires median ≥5 with documentary (non-death) late pins and the curated-authoritative loader.
