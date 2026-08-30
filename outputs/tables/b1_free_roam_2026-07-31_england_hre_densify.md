# Thin-cell densify: England + Magnia HRE (2026-07-31)

## Decision

Heymann named-onset leads exhausted after Hesselin. Deep-densify **thin England cells** (Henry / Wyatt / Wolsey) and fix **jacopo_magnia** unknown→hre (Germany Franciscan context).

## jacopo_magnia_friar

| | before | after |
|--|--|--|
| region | unknown | **hre** |
| n_ctrl primary | 2 | **5** |
| Δ | +8.5 | **−3.0** |

Bucket overrides: Eyb / Knebel / van der Lake → cleric; curated Johann von Lübeck + Nikolaus Straub.

## England densify

| Wearer | Match | n_ctrl | Δ |
|--------|-------|-------:|--:|
| Henry VIII | occ+birth+region (was relaxed) | 1 (Brandon; Arthur `use_in_primary=False`) | **−5** |
| Henry Wyatt | occ+birth+region | 2 (Dudley + Empson) | **+17** |
| Wolsey | occ+birth+region | 3 (Fisher + Colet + Tunstall) | **−9** |

Also injected (birth-window / `use_in_primary=False` where dies &lt;45): Cromwell, Howard, Henry VII, James IV, Stafford, Arthur.

Region overrides restored curated Scottish scholars (Mair, Lokert) into england cell.

## Logged / skipped

- No new named wearer from Heymann leftovers (Meschinot metaphorical; Jeanne/Charles V inventory paths already closed).
- Latone / Nuno still no birth–death.

## Primary

| | |
|--|--|
| n pairs | **37** |
| median Δ | **−0.5** |
| boot 95% CI | **[−3.0, 4.5]** |
| n≥15 | **4** |
| SESOI +5 / +15 | **FAIL** / **FAIL** |
