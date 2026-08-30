# Free roam: EMLO vocabulary expansion + close letter-path (2026-08-02)

## Decision

Letter-path soft leads after Wood/Lynnet looked dry → **free roam** with new EMLO query vocabulary (not another will densify). Goal: find another living named wearer or formally close the EMLO seam.

## What was mined

Cached under `data/raw/emlo_free_roam_2026-08-02/` (via gateway `127.0.0.1:12309`).

| Query | numFound | Verdict |
|-------|---------:|---------|
| `eyeglasses` / `occhiali` / `besicles` | 0 | empty |
| `"reading glasses"` / `"spectacle maker"` | 0 | empty |
| `"pair of spectacles"` / `spectacles AND buy` | 1 | **Lynnet only** (already promoted) |
| `spectacles AND bought` / `spectacles AND wear` | 0 | empty |
| `lunettes` | 20 | almost all **telescopes** / achromats (18c); 1677 Somerset *lunettes de long vue*; 1684 Justel field glasses — **not** near-work reading glasses |
| `reading glasses` (unquoted) | 936 | Solr OR noise: looking-glasses, optic glasses, cupping glasses; **0** personal reading-wearer in top page |
| `spectacle maker` (unquoted) | 62 | place-name *Maker* (Cornwall), theatrical “spectacle”, book title *Spectacle de la Nature*; optical hit = Cole monoptick (maker) |

## Leftover EMLO `spectacles` dump (n=26) triage

| Lead | Call |
|------|------|
| Wood / Lynnet | already **PROMOTED** |
| Charlett 1707 | still soft-hold (duration *ask*) |
| Charlett 1716 | **CLOSE as personal onset** — anecdote that an old grandfather “can shave without spectacles” |
| Cole 1695 | **CLOSE** — distributes experimental *monoptick spectacles*; maker/experimenter, not ordinary wearer onset |
| Aubrey 1680 | **CLOSE** — sends Pell *Antiquity of Spectacles* extract (historiography) |
| Browne / Hearne / Smith | **CLOSE** — lexical / Redi dissertation on spectacle history |
| Beale→Hooke (~1670s) | soft instrument talk (“glasses for short-sighted people”) — **no named personal onset** |

## Side probe

Gallica SRU `besicles` + `dc.date < 1600` → **1** hit (Thevet cosmography illustration), not a living wearer letter.

## Primary impact

**None.** n stays **39**; median **−2.97**; CI **[−4.0, 2.0]**; SESOI FAIL.

## Next (when continuing)

EMLO English letter seam for living named onset is **closed** for practical purposes. Prefer a *new* mine, e.g.:

1. Italian / Dutch letter corpora beyond already-mined Datini–Medici–Ammannati lanes  
2. Hand spectacle-negative audit on England densify controls (credibility, not n)  
3. Non-EMLO continental catalogs with wearer language (*occhiali da naso*, *besicles*, *brille*) tied to named living persons
