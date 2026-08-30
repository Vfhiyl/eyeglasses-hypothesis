# Free roam — Digitarq óculos mine (2026-08-01)

Gateway `127.0.0.1:12309`; JWT in `config/digitarq_token.local` (24h).  
True search: `GET /api/docs/search?query=…&fromIndex=0&max=…` (empty `fromIndex` → 422).  
`_next/data/.../search.json` is i18n-only, not results.

## Catalog

| Query | total (API) | notes |
|-------|------------:|-------|
| óculos / oculos | 87 / 80 | mostly modern patents / false friends |
| oculos de vidro | 7 | includes Jaques alvarás |
| fabricante / faz óculos / Jaques óculos | 1–4 | court maker orbit |
| meus óculos | **0** | |
| uns / seus / par de óculos | 5–6 | almost all **18–20c** inventories / modern |
| óculos inventário | 14 | 18–19c Feitos Findos |
| vidros dos olhos | 215 | heavy **Alhos Vedros** toponym noise |
| dos Óculos | 26–35 | nicknames + modern |

Full merge: `data/raw/digitarq_free_roam/oculos_catalog.csv` (n≈318 unique).

## Hard B1 ingest?

**None.**

### Best soft leads (appendix only)

1. **Jacques Moser / Jaques (óculos maker)** — Lisboa 1552–1562  
   - Digitarq `PT/TT/TSO-IL/028/05620`: Inquisition, age **40** (b.≈**1522**), *oficial de óculos*, Rouen → Lisboa.  
   - Alvarás D. Catarina: `PT/TT/CC/1/92/153` (1554), `CC/1/97/121` (1556), plus `CC/2/243/00059` pay **Jaques Moses** 42k rs (1552).  
   - Images downloaded: `data/raw/digitarq_free_roam/jaques_1554|1556/images/` (OCR poor; metadata sufficient).  
   - **Not a wearer pin** — artisan/maker; do not promote.

2. **João Lopes de Elvas, alcunha *O dos Óculos*** — Beja debt 1603  
   - `PT/ADPTG/MON/MSBP/B/008-040/000002`. Nickname only; no birth/death; late edge.

### Closed / noise

- `"meus óculos"` empty in Digitarq metadata search.  
- 14–16c personal-use wills with óculos **not** surfacing in catalog titles.  
- Queen Catarina payments = court commission to maker, not queen self-wear evidence for B1.

## Candidate CSV

Logged low-confidence rows: `jacques_moser`, `joao_lopes_elvas_oculos` in `b1_named_wearers_candidates_new.csv` — **do not promote**.

## Next Digitarq leverage (if reopen)

- Advanced date filter in UI if API supports (not used this pass).  
- Page OCR on Moser processo (40 imgs) only if hunting *artisan* microhistory, not B1 n.  
- PARES/`anteojos` Spain still a different mine.
