# Release notes — v4.0.0

## Verdict rewrite (not mush)

- Four-layer verdict: A1 support / A2 credible / B macro unsupported / B1 **hunt** / C civilization debunk / +15 pending pages.
- Anti-fuzzy retained: insufficient → hunt evidence. Softening language alone is not a fix.

## Evidence work shipped

- `claim_fifteen_years_sources.csv` — withdraw “Miller only”.
- `CLAIM_MAP.md`, `B1_EVIDENCE_HUNT.md`.
- Giordano date fix (23 Feb 1305 Florentine = 23 Feb 1306 modern reckoning).
- RCT outcomes split in `config/rct_effects.yaml`.
- Wikidata P800 demoted; `13_wikidata_p800_audit.py` + hand-audit sample (n=80).
- Evidence families (`evidence_by_family.csv`); no n_tests voting.
- `14_equivalence_ci.py` — CI vs SESOI.
- `breakpoint_slope_delta_1290_1450.csv` — formal Δslope bootstrap (HC: 1450 stronger, CI excludes 0).
- `15_b1_wearer_offline_expand.py` — B1 hunt from local cache.

## Reproducibility

- Author self-tested reproducibility only (not independent audit).
- Tag: `v4.0.0`. Zenodo/OSF DOI: add when deposited by maintainer.
- Cite via `CITATION.cff`.

## Still open (do these next)

1. Three print editions for +15-year sentence.
2. Grow B1 core named wearers with dated works to n≥20.
3. EMLO search.
