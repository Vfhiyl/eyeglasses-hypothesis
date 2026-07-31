# B1 free roam — Digitarq CSJEX + CVSEPRT densify (2026-07-30 evening)

## Session constraints

- Local proxy flaky (intermittent **502**); Digitarq still reachable in bursts via `https_proxy=127.0.0.1:12309` + `curl -k`.
- RPD file-list APIs often **401**; published viewers may still open in browser.
- IA: no OA hit for Cardoso *Brotéria* 187 (2018). UP Falcão handle fetch SSL-failed this pass.

## Pivot: Xabregas = post-resign residence

Azevedo resigns Porto **1495-10-23**, lives as **donato** at **Convento de São João Evangelista de Xabregas** until **1517-07-27** (~+22y after wear, +22y after resign). Convent cartório is the right *place* to densify late-life near-work (if any).

### Fund unlocked

| Ref | Title | uuid |
|-----|-------|------|
| **`PT/TT/CSJEX`** | Convento de São João Evangelista de Xabregas (ANTT) | `422dcc6b93fc4153988c55a82c5f8521` |

Catalogued **113/148** hits → `data/raw/azevedo_porto/digitarq/csjex_catalog.tsv`.

Name search `Azevedo CSJEX` / `donato Xabregas` → **no** bishop hit (donato hit is 1823 Franciscan). Must browse by date/shelf.

### CSJEX units overlapping 1476–1517

| Pri | Ref | Dates | Notes | Digitized? | uuid |
|-----|-----|-------|-------|------------|------|
| **A** | `…/8/L12` Livro 13º capelas/prazos | **1452–1726** | spans full wear→death | **yes (144 files)** | `0c3f5490e382414ba56806dd835fa90b` |
| **A** | `…/A/2/M02` Maço 2 (S. João Rio Maior) | **1456–1524** | covers donato years | **yes (2 files)** | `6574b99318dd4bfda70f845f045f0f42` |
| **B** | `…/8/L03` Livro 3º capelas/prazos | **1495–1700** | starts resign year | no | `1eb36c401a834e668cb0cd04d924f34e` |
| **B** | `…/A/4/M14` Maço 14 (S. Pedro Alenquer) | 1494–1667 | Falcão/Pina cite zone | child digitized | parent `584673dde12e…` |
| — | `…/A/4/M14/000001` Doação D. Leonor | **1494-03-27** | autograph queen; 3 images | **yes** | `162c54f636df49f7a65ded68350370a2` |
| — | `…/6/M17/000036` Privilégio D. João II | **1490-01-12** | signed king; seal | no | `28baec5cfd154ea5a7a0f85572e23d63` |

**Caveat:** these are *convent* property/privilege docs, not “bishop’s desk work.” Useful only if a folio names Azevedo as actor/witness/donato doing near tasks.

### Digitized chronicle (background)

- `PT/TT/MSLIV/0796` *Novo Memorial…* (Paulo de Portalegre on Lóios), dates from 1468, **154 images** — may mention notable donatos; not checked folio-by-folio. uuid `bf9ca6e491b743b889f5f14f13563166`.

## CVSEPRT imaged inventory (from prior pages)

Earliest *useful* digitized copy-volume remains:

- **`PT/ADPRT/MON/CVSEPRT/002/0043`** (1535–), **1078 files**, copies of **livro 51** + sentenças — uuid `0411458…` / RPD `1440421`.

Other imaged UIs are mostly 17th–18th c. (see prior digitarq note).

Proxy could not open fileViewer this evening (502). Browser path still recommended.

## Parallel OA

- UMinho thesis on Cabido Porto *pergaminhos* is **14th-c** (to 1406) — wrong century for Azevedo.
- Falcão 2016 PhD (Lóios) OA at UP: confirms **ANTT CSJEX** as generalate cartório; cites ADP Santo Elói Compêndio **K/19/6-5** (our Digitarq unit is **K/19/6-57** old quota — same family, different UI).
- Cabido Sé Porto fund code still **not** resolved in Digitarq (`CAB/SEPRT` empty).

## B1 status

| Lead | Status |
|------|--------|
| CVSEPRT early undigitized (004/0072, 0064, Prazos 51) | Still need ADP visit / image order |
| CVSEPRT `002/0043` images | Best remote for 1480 copy text — **user browser** |
| **CSJEX** (Xabregas) | **New** post-1495 archive unlocked; browse L12 / M02 / L03 for “Azevedo” / donato |
| Name search | Still useless |
| Hard ingest | Still no dated FROM-him near-work pin |

## Next actions

1. Browser: open CSJEX L12 viewer + CVSEPRT 002/0043; Ctrl-F / visual scan for *Azevedo*, *bispo*, *Porto*, *donato*.
2. When proxy stable: `details` children of CSJEX/8 and CSJEX/13 (Prazos series 1437–).
3. Hunt Digitarq fund for **Cabido da Sé do Porto** (ADP) — better for episcopal acts 1476–1495 than Santo Elói.
4. Keep soft; do not hard-ingest.

## Key URLs

- CSJEX fund: https://digitarq.arquivos.pt/documentDetails/422dcc6b93fc4153988c55a82c5f8521  
- Capelas L12 (144 imgs): https://digitarq.arquivos.pt/documentDetails/0c3f5490e382414ba56806dd835fa90b  
- Maço 2 (digitized): https://digitarq.arquivos.pt/documentDetails/6574b99318dd4bfda70f845f045f0f42  
- Livro 3º (from 1495): https://digitarq.arquivos.pt/documentDetails/1eb36c401a834e668cb0cd04d924f34e  
- Memorial Lóios: https://digitarq.arquivos.pt/documentDetails/bf9ca6e491b743b889f5f14f13563166  
