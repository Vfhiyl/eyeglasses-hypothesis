# Coloma pin attempt → Baye densify (2026-08-02)

## Decision

1. Finish soft PARES *tío Coloma* lead.  
2. If thin, densify extreme France clerk cell `nicolas_de_baye` (Δ=−17).

## Coloma — soft-hold / not promote

| Item | Detail |
|------|--------|
| PARES | `OSUNA,CT.235,D.154-175` (desc `12988743`) |
| Dates | 1710-02-09 → 1710-07-29 |
| Parties | Pascual Francisco de Borja (1653–1716) → son Luis (1673–1740) |
| Catalog | *encargo de unos anteojos para la vista del tío Coloma* |
| Images | **none** on PARES description this session |
| Identity | Wearer remains kinship label only; plausible Coloma–Borja uncles (e.g. Francisco Coloma Pujades y Borja d.1712) **not letter-pinned** |

**Verdict:** third-party vision order, living uncle class — **no CSV ingest**, no promote. Soft-hold until letter names a specific Coloma.

## Baye densify

| Action | Detail |
|--------|--------|
| `CTRL_BUCKET_OVERRIDE` | Laurent de Premierfait `Q679093` → **clerk** (already curated ya45=3; birth pin 1370 within fr.wiki 1360–70) |
| Inject | Gontier Col `Q3110583` — secrétaire du roi / diplomat; birth **ESTIMATED 1355** from «vers 1350/1355»; last 1418; ya45=**18**; medium |
| Region overrides | both → france (`B1_SPARQL=0` safe) |

### Cell

| | before | after |
|--|--:|--:|
| n_ctrl primary | 3 | **5** |
| med C | 26 | **19** |
| Δ | −17 | **−10** |

## Primary

| Metric | Value |
|--------|------:|
| n pairs | **39** |
| median Δ | **−2.97** (unchanged) |
| boot CI | **[−4.0, 2.0]** |
| SESOI +5/+15 | **FAIL** |
