# Digitarq free roam layer-2 (2026-08-01)

Not “whole Digitarq done” — this pass pushed past simple keyword totals into **date-filter attempts, Ilardi-orbit names, lexical variants, false-friend audits, and Moser page OCR**.

## What changed vs layer-1

| Probe | Result |
|-------|--------|
| `POST /api/docs/advancedSearch` with UI-like `filters.searchTerm/dateInitial/dateFinal` | **Ignores filters** → dumps ~7.48M docs (unusable). Date facet still **client-side only**. |
| Ilardi Portugal names (`Latone`, `Nuno Fernandes`, `Guidetti`, `Vaschi`) | Hits exist; **none** are Cambini spectacle clients with óculos text. Latone→1625 marriage unrelated; Nuno→Chancelaria namesakes / later TSO; Guidetti→Lisbon canons 1515–20. |
| `lunetas` 1412 `PT/TT/CC/2/1/9` | **False friend**: *Castelo da Luneta* (toponym), not spectacles. |
| Lexical (`oculista`, `armações`, `vidros de óculos`, `um/hum par`, `comprou óculos`) | 14–16c wearer phrasing **absent** in titles; inventários with óculos start **18c**. |
| True spectacle titles ≤1600 in merged catalog | Still the **Jaques maker orbit** + one new office buy (below). |
| Moser processo pp.1–6(+8–10) | Tesseract unusable; **LLM vision** read cover: *Jaques mousser oculista / official d'oculos*, Lisboa prison delivery 18 Mar 1562; testimony “o outro dos oculos”. See `moser_1562_sample/VISION_READ_m0001-0006.md`. |

## New soft (not ingest)

### Royal Contos office buy — 1539

- `PT/TT/CC/2/227/00107` (uuid `dc5e49475b7141d9bf014b5527f57bd3`)
- Mandado: pay 10 040 rs to buy **tinteiros, bolsas e óculos com suas caixas** for the *contador-mor*, his *escrivão*, and **20 oficiais** of the Contos.
- **Workplace bulk spectacles** — strengthens Portuguese institutional use mid-16c; **no named personal wearer + birth/death** → do **not** promote to B1 treatment.

### Confirmed maker cluster (still not wearers)

- Jaques / Jacques Moser / Jaques Moses (1552–62) — unchanged from layer-1.
- Moser age-40 pin remains best bio; occupation *oficial de óculos*.

## Hard B1 ingest

**None.**

## Honest remainder of the mine

1. **Undigitized / unindexed bodies** — most 15c wills & letters never put `óculos` in the unit title.  
2. **Paleography** — Moser 40pp and Contos quitação images need human/better HTR, not tesseract.  
3. **Working advanced date API** — reverse-engineer real request (current body shape is wrong) or use browser UI export.  
4. **Other mines** — PARES `anteojos`; ASPO Datini image-by-segnatura; English probate.

Artifacts: `data/raw/digitarq_free_roam/layer2_name_hits.csv`, Moser sample under `moser_1562_sample/`, prior `oculos_catalog.csv`.

## Continue after reconnect (vision)

- **m0012** locks bio: age ~40 (b.≈1522), wife **Isabel Bernardez**, officio **fazer oculos**, literate French resident Lisboa.
- **m0019** fiança header again: *frances q faz oculos*.
- 1539 Contos mandado: **0 digitized files** (catalog-only; no image download).
- Still **no B1 wearer ingest**. Notes: `moser_1562_sample/VISION_READ_continue.md`.
