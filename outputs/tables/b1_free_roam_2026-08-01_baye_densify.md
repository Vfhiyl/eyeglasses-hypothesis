# Free roam → Baye densify (2026-08-01)

## Direction chosen

OA named-onset scan (Manni / French / Florence) yielded **no new birth-dated personal-use wearers**. Chose **deep densify** of thin/extreme France clerk cell `nicolas_de_baye` (was `occ_relaxed` with humanists).

## Ingest / match changes

| Action | Detail |
|--------|--------|
| `CTRL_BUCKET_OVERRIDE` | Jean Fusoris `Q3172160` → **clerk** |
| Inject + curated | Jean de Montreuil `Q1237886` (1354–1418; royal secretary) |
| Inject + curated | Jean Jouvenel des Ursins `Q1685601` (1360–1431; Parlement avocat) |
| Region | both → **france** |

## Baye cell

| | before | after |
|--|--:|--:|
| match_level | `occ_relaxed` (+ humanists) | **`occ+birth+region`** |
| n_ctrl primary | 1–2 | **3** (Fusoris; Jouvenel; Montreuil) |
| med C ya45 | ~21 | **26** |
| Δ primary | ~−12 | **−17** |

Long-lived Parlement/clerk peers make Baye **more negative** — expected; match quality upgraded.

## Portrait-only log (not promoted)

**Canon Joris van der Paele** (`joris_van_der_paele`, ~1370–1443): van Eyck 1436 portrait with spectacles. JHNA: painting is the **only** evidence. Logged in candidates as `portrait_spectacles_only`; **`onsetish=False`**.

## Recovery note

A bad rewrite briefly wiped `b1_control_nearwork_chrono_curated.csv`. Restored from git HEAD + transcript Shell appends (→124 rows). Snapshot: `outputs/tables/b1_control_nearwork_chrono_curated.snapshot_2026-08-01.csv`.

## Primary after this pass

| Metric | Value |
|--------|------:|
| n pairs with Δ | **37** |
| median Δ | **−0.5** |
| boot CI | **[−3.0, 4.5]** |
| SESOI +5 / +15 | **FAIL** |
| Causal B1 | **UNIDENTIFIED** |

Densify moved one cell’s match quality; **panel median unchanged**.
