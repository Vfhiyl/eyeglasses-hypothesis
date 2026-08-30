# Pass CY — expand collision audit + wire into verdict (2026-08-06)

## Judgment

After Pass CX demoted Cusa, the next ROI is **anti-regression plumbing**, not OA mining: catch cross-QID aliases (Cusa’s wrong QID / Pius II Q162600↔Q101437) and freeze the check into `b1_roster_verdict.csv`.

## Changes

1. **`30` expanded** — match modes: `exact_qid`, `name_exact`, `name_lifespan` (birth±2, death±5, shared token ≥5 chars). Reports active collisions + inactive aliases.
2. **`25` wires** `wearer_control_collision_clear` — DONE iff active=0; regenerates audit each primary run.
3. **Pius II control alias** Q101437 added to output eligibility as False (labor already False).

## Result

| Check | Value |
|-------|-------|
| Active collisions | **0** |
| Inactive aliases noted | 6 (Cusa, Pius II alias, Locke, René, Priestley, Burke — all demoted) |
| Labor / output freeze | unchanged (med 6.0 / 7.5; SESOI+5 PASS; +15 FAIL) |

## Next

Physical densify only. Re-run `25` (pulls `30`) after any wearer/control edit.
