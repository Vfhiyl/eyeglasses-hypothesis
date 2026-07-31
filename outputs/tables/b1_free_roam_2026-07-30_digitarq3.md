# B1 free roam — proxy OK + Cabido Sé Porto (2026-07-30 night)

## Proxy status

Confirmed via `https_proxy=127.0.0.1:12309` + `curl -k`:

| Endpoint | Status |
|----------|--------|
| `documentDetails/57506792…` HTML | **200** |
| `api/docs/details/…` | **200** |
| `api/docs/search` | **200** |
| `fileViewer/…` shell | **200** |
| `api/rdigital/thumb?docId=` | **200** JPEG |
| `api/rdigital/dissemination?fileId=<RPD id>` | **200** (returns first page image) |
| `api/rdigital/files/…` / list | **401** or empty `total:0` |

So: catalog + details + first-page image OK; full page-list still needs browser session / auth.

Saved samples: `data/raw/azevedo_porto/digitarq/page0_0043.jpg` (CVSEPRT 002/0043), `page0_l12.jpg` (CSJEX L12).

## Breakthrough: Cabido da Sé do Porto

| | |
|--|--|
| Ref | **`PT/ADPRT/DIO/CABIDO`** |
| Title | Cabido da Sé do Porto |
| Dates | 1120–1913 |
| uuid | `e6d43a79db664eeeb88312a933894afc` |
| Scope | Ecclesiastical admin + finance; *livros dos originais*, sentenças, prazos, padroados, tombos, inquirições… |
| URL | https://digitarq.arquivos.pt/documentDetails/e6d43a79db664eeeb88312a933894afc |

Search claimed **3624** hits; first 200 pages catalogued → `cabido_catalog.tsv`.

### Named post-wear pin (best so far)

**1492** — papal bull explicitly naming the bishop:

- Title: *Bula do Papa Alexandre que concede o poder o **Bispo D. João** possuir a pensão de 20$, imposta nos frutos da igreja de S. Salvador de Árvore.*
- Ref: `PT/ADPRT/DIO/CABIDO/017/1672/00385`
- Shelf: `K/23/3/3-2.1672, fl. 11`
- uuid: `062a3bde82a24ece8284d6da1b63458c`
- Images: **none** online
- URL: https://digitarq.arquivos.pt/documentDetails/062a3bde82a24ece8284d6da1b63458c

Wear evidence 1476-01 → this **1492** ≈ **+16y**. Identity: only João de Azevedo was Bishop of Porto then (to 1495).

**B1 reading:** strong *dated presence / beneficiary* pin; **weak as near-work** (bull grants pension — not proof he was reading/writing). Still densifies post-wear activity trail; do **not** hard-ingest on this alone.

### Other Cabido units in window (no images; Cabido as actor, not necessarily bishop)

| Year | Ref (short) | Title gist |
|------|-------------|------------|
| 1479 | `…/1667/00168` | Instrumento de posse |
| 1488 | `…/1679/00655` | Compra casas Ovar |
| 1492 | several prazos | Azenha Paradela, campo Paranhos, etc. |
| 1494 | `…/1675/00502` | Prazo casal S. João de Pinho |
| 1501+ | later | after resign — less relevant unless ties to him |

## Still open

- Full OCR/browse of digitized CVSEPRT `002/0043` / CSJEX L12 beyond page 0.
- Physical read of **1492 bula** fl. 11 at ADP.
- More Cabido pagination beyond first ~200 of 3624 for other “Bispo D. João” hits 1476–1495.
