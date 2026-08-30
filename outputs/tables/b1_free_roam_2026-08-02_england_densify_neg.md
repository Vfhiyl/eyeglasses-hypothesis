# England densify spectacle-negative audit (2026-08-02)

## Decision

Unfinished hygiene after Wood/Lynnet promote: audit the **18** England densify controls (12 humanist + 6 cleric) for personal-wear contamination.

## Methods

- Ilardi + `b1_named_wearers_candidates_new` QID/name collision
- EMLO spectacles dump (n=26) author/recipient/abstract surname∩spectacle
- Web/EE soft check on high-profile peers (Locke, Boyle, Hooke, …)
- Append rows to `b1_control_spectacle_negative_spotcheck.csv`

## Result

| Control | Call |
|---------|------|
| **John Locke (Q9353)** | **POSITIVE — demoted** |
| Other 17 densify peers | No personal-wear positive in this audit |

### Locke demotion

- Evidence: Electronic Enlightenment doc *lockjoOU0070466a3o* — c. **1701-10-15**, John Churchill supplied Locke “a pair of **green spectacles** in leather frames” (personal receipt while alive).
- Actions: `use_in_primary=False` in curated chrono; `is_known_wearer=True` in control pool (excluded from rematch); soft candidate `locke_john` logged at **low** confidence (late evidence; ya≈3; **not** promoted).
- Caveat: some biographies claim he often read without spectacles late in life; green lenses may be glare aids. Still fails the control “no documentary personal spectacles” bar.

### Non-hits / false friends

- Boyle: ophthalmology tract mentions *cataract spectacles* for patients — not personal wear.
- Ray / Stillingfleet: EMLO surname collisions only (Mapletoft; Smith–Hearne).
- Cole already closed earlier as maker (not in densify set).

## Pipeline after demotion

| | before | after |
|--|-------:|------:|
| Wood n_ctrl / Δ | 12 / −6.0 | **11 / −5.0** |
| Primary n | 39 | **39** |
| Primary median / CI | −2.97 / [−4.0, 2.0] | **unchanged** |
| SESOI | FAIL | **FAIL** |

Scripts: `24` (`B1_SPARQL=0`) → `25`.

## Next

Neg audit for this densify set is **done**. Prefer a new non-EMLO mine next (Italian/Dutch letters or continental catalogs).
