# B1 free roam — Digitarq CVSEPRT unlock (2026-07-30)

## Access

- Live API via local proxy (`https_proxy=127.0.0.1:12309`, curl `-k`):  
  `GET https://digitarq.arquivos.pt/api/docs/search?query=…&fromIndex=&max=10`  
  `GET https://digitarq.arquivos.pt/api/docs/details/<uuid>`
- Raw dumps: `data/raw/azevedo_porto/digitarq/` (pages, details, `cvseprt_catalog.tsv`)
- Catalogued **75/102** CVSEPRT hits via pagination (API `max` effectively 10).

## Fund unlocked

| Level | Ref | Title | uuid |
|-------|-----|-------|------|
| F | `PT/ADPRT/MON/CVSEPRT` | Convento de Santo Elói – Porto (1422–1834) | `2c3476b1c06b43db8bce22f1adf9e0ab` |

Fund scope: economic activity — prazos, sentenças, tombos, forais, **compêndio do cartório**, etc. (ADP Porto / ADPRT).

## Best units for Azevedo window (wear 1476 → resign 1495 / d.1517)

None are *from* João de Azevedo; all are **convent** cartório. Goal = dated near-work *about/involving* the bishopric or acts in his years.

| Priority | Ref | Dates | Title | Shelf | Digitized? | uuid |
|----------|-----|-------|-------|-------|------------|------|
| **A** | `…/004/0072` | **1422–1564** | Livro n.º 5 e 6 das sentenças | K/25/7/3–517 | no | `5b938df87d6942ba8f2400907e67a4ac` |
| **A** | `…/004/0064` | **1448–1731** | Livro 5.º das sentenças | K/25/7/2–513 | no | `6f6313a5641649659c9e1c5a81b4c90e` |
| **B** | `…/001/0049` | **1480–1779** | Prazos, n.º 51 | K/25/7/2–512 | no | `1b9906f1b0de4861bf7d1300234319be` |
| **B** | `…/002/0038` | **1490–1728** | Registos de prazos e outros títulos | K/25/7/2–509 | no | `55f7c21b100d45a4bba98bb03c4c592a` |
| **B** | `…/003` (SR) | **1490–1779** | Registos de padroado | — | no | `42a625a0899042c4b047b4f5f23808b8` |
| **C** | `…/001/0008` | **1495-07-19–1722** | Registos, n.º 9 | K/12/1/5–16 (old K/19/7–50) | no | `6cb25e03f02b4307a7f0fb50d900f48f` |
| — | `…/004/0015` | 1510–1671 | (user’s first hit) | K/19/7–55 | no | `5750679261bc44d7b6fa76fe7992228c` |

**A-tier** spans the full episcopate (indices at front of both sentenças books).  
**B-tier** starts inside post-wear (+4y / +14y).  
**C** starts **1495-07-19** ≈ resign window (Eubel resign 1495-10-23).

### Digitized workaround

- `…/002/0043` (1535–1774), **1078 files**, shelf **K/19/6–26**: includes **copies of livro 51** and sentenças 13 & 1.  
  uuid `0411458db88448f5b433cb70bae3d12d` — OA path to *some* early prazo material without ADP visit.

## Falcão shelf resolved

- Cite **K/19/6–57** = old quota of **`…/007/0087` Compêndio do cartório** (1641), uuid `3b86765d30aa4871a41b2bcd91f65190`.  
- Now **K/12/1/5–9**. No images.  
- 17th-c handbook: foundation, foros, inventories; **list of convent prelates from 1490** (convent superiors ≠ Bishop of Porto). Secondary at best for B1.

## Name searches (noise)

- `Azevedo` / `João de Azevedo` → modern ANTT Coutinho etc.; no 15th-c Porto bishop hit in top results.
- Actors `Azevedo` → thousands of unrelated persons/firms.
- `bispo do Porto` → 20th-c diocesan.
- Do **not** rely on name search; use shelf/date browsing of CVSEPRT.

## B1 status

- Digitarq blocker for **finding** CVSEPRT: **cleared**.
- Hard ingest still blocked: no OA folio naming the bishop’s post-1476 near-work; best books undigitized.
- Next: (1) OA browse images of `002/0043` for copied 1480 prazos; (2) on-site/ADP order for **004/0072** & **004/0064** indices; (3) keep Azevedo soft until a dated pin exists.

## Key URLs

- Fund: https://digitarq.arquivos.pt/documentDetails/2c3476b1c06b43db8bce22f1adf9e0ab  
- Sentenças 5+6: https://digitarq.arquivos.pt/documentDetails/5b938df87d6942ba8f2400907e67a4ac  
- Prazos 51: https://digitarq.arquivos.pt/documentDetails/1b9906f1b0de4861bf7d1300234319be  
- Digitized copies vol.: https://digitarq.arquivos.pt/documentDetails/0411458db88448f5b433cb70bae3d12d  
- Compêndio (K/19/6–57): https://digitarq.arquivos.pt/documentDetails/3b86765d30aa4871a41b2bcd91f65190

## Digitized volume viewer

- Doc `002/0043` has published RPD id **1440421** (created 2025-12-15).
- Viewer (try): https://digitarq.arquivos.pt/fileViewer/0411458db88448f5b433cb70bae3d12d?isRepresentation=true
- RPD file-list API returned 401 Unauthorized from this proxy session; browser login may still open images.
- Desc: includes copies of **livro 51** and sentenças 13 & 1 — best remote shot at 1480-era prazo text.
