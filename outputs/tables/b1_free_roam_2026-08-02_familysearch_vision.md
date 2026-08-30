# B1 free roam — FamilySearch vision densify (2026-08-02)

Gateway + `scripts/familysearch_film_browse.py` stitch; multimodal vision (not OCR).  
Session refreshed afternoon; `ping` OK.

## Named soft finds (will / inventory path — not primary)

| Who | Date / place | Evidence | ARK / file | Class |
|-----|--------------|----------|------------|-------|
| **Thomas Allerton** | Will 1615-04-25, Chester vintner | “spectacles with the case of brass” → Randall Holme; wife Alice | `3:1:3Q9M-C394-RZPQ` (prior night) | personal bequest |
| **Margaret Nugent** | Will dated **2 Jan 1620**, Manchester widow (Lancs film; FS title said 1631) | **“pair of silver spectacles”** + books / apparel | `3:1:S3HY-6L8S-FWN` → `…_FWN_L11.jpg` | personal bequest |
| **George French** | d. **1633-10-12** Bedford (Devon); inventory St **Keverne**, Cornwall; prized 19 Oct 1633 | Inventory line **“one paire of spectacles”** among apparel | `3:1:S3HY-6R49-9ZJ` → `…_9ZJ_L11.jpg` | inventory ownership |
| **Philip Oldfield** | Inventory label **1616** (Cheshire) | **“Item a paire of Spectacles”** (vj d) then marking iron, **“Item a Herbale”** (v s); also psalter / Latin+English Bibles | `3:1:S3HT-6SRS-P9Y` → `…_P9Y_L11.jpg` | inventory; literate near-work milieu |
| *(unnamed Herts inventory)* | FS title Wills **1642** Hertfordshire | “**two pairs of spectacles**” with looking glass / pens in chamber over gate house | `3:1:3Q9M-CSRJ-2S2L-2` → `…_2S2L-2_L11.jpg` | inventory; need testator name from header page |

## Search notes

- UK ∩ 1600 ∩ `"my spectacles"` → only Allerton (already done).
- `"silver spectacles"` UK → almost all **18–19c**; Nugent is the early silver hit via vision on the Lancs ARK.
- Full-Text year labels can lag true document date (Nugent 1620 vs “Wills 1631”).

## B1 ingest

- **Hard / primary:** none (all terminal ownership; births not recovered).
- Keep as English appendix densify; Nugent (silver) + French (dated death + inventory) are strongest new soft rows if a candidates CSV is wanted later.

## Later evening densify (cont.)

| Who | Date / place | Evidence | ARK | Class |
|-----|--------------|----------|-----|-------|
| **Elizabeth Martindale** | Inventory **1670-11-26**, Bishopton (Durham) | “A book of Common prayer, a **payr of Spectacles** with some old books in **Latine**” | `3:1:S3HY-DY73-6BN` | inventory + Latin books (female) |
| Cheshire 1610 hit (`CSND-T9SB-W`) | Jan ~1600 margin names John Howard / Tho Woodward | Stitch incomplete (white patch); **no clear spectacles** on vision — likely weak Full-Text herbal false lead | same | defer |
| Ely / Stapleford Cambridgeshire inv. 1672-05-04 (Robert ?) | brass-case search | Needs line-level confirm of spectacles vs other brass | `3:1:3Q9M-CS1G-B79P-P` | soft pending |

### Other mines probed

- **PARES `anteojos`**: catalog search works via gateway, but top hits are mostly **19–20c** military *anteojos de tijera* / HISMA invoices / nicknames — **not** a 15–16c wearer mine without tight date filters.
- **Herts film-data** for testator name: still broken (**503** then **307**); page `…2S2L-2` is inventory body only (spectacles + looking glass OK, **no decedent name** on this leaf). Need neighbor frames via `--dgs` from browser Network, or film-data recovery.
- `"two pairs of spectacles"` phrase search: 0 hits (FS query syntax may not like OR).

## Script

Prefer only: `scripts/familysearch_film_browse.py` (`ping` / `session` / `stitch --ark …` / `film` / `list`).

## Herts name resolution (film 008306986)

- Spectacle inventory leaf: `i=642` `3:1:3Q9M-CSRJ-2S2L-2` (FS title year **1642** = film-start label, **not** inventory date).
- Immediate prior will leaf `i=639` `3:1:3Q9M-CSRJ-2S2G-T`: vision reads **Last Will of James Cassell / Castell** (mark), date ~**Oct 1681 or 1691**; endorsement filing code ~`25HW18`. Surname **C** fits this reel (*1642 Chapman … 1707 Carter*).
- Stitched `i=635–637`: earlier packet looks like **John Chapman** will (vision; ~1683) — separate from Cassell — then Cassell at `639` → inventory `641–642` → **Mary Clark** at `643`.
- Status: **soft named candidate** (will-path); parish/occupation still TBD. Not hard-ingest.

### New two-pair Full-Text leads (UK∩1600)

| Hit | ARK | Note |
|-----|-----|------|
| Cheshire Wills **1682** | `3:1:S3HY-DTMS-NX1` (dup `…C39Z-H3QR-X`) | Bible + **two pair of Spectacles** + looking glass |
| Lancashire **1695** | `3:1:S3HT-DWY3-ZBX` | books + two pair |
| Lancashire **1681** | `3:1:S3HY-6XY4-F1Q` | Bibles + two pair |

### Cheshire 1682 named

- **Thomas Smith**, inventory **1682-11-22**, diocese of Chester — header on `3:1:S3HY-DTMS-NX1`; microfilm strip “SMITH, THOMAS / WS / 1682”. Soft; parish TBD; no hard ingest.

## Naming densify (evening decision: finish two-pair leads)

| Who | Date / place | Evidence | ARK | Class |
|-----|--------------|----------|-----|-------|
| **John Harrison** | Inv. **1681-12-23**, Golborne (Winwick), Lancs | Bibles + spectacles (OCR “two pair”; vision **one pair**) | `3:1:S3HY-6XY4-F1Q` | soft; agrarian + Bibles |
| **Bryan Travis** | Inv. **1694-07-28**, Warrington | **bookes** 6s6d + **two pair of spectacles** 6d; estate ~£9 | `3:1:S3HT-DWY3-ZBX` | soft; books+glasses |
| **Thomas Smith** | Inv. **1682-11-22**, Chester diocese | Bible + two pair + looking glass | `3:1:S3HY-DTMS-NX1` | soft (prior) |

UK Full-Text `spectacles` @ year facet **1550**: **0** hits (still empty early band).
Cassell parish: i=638 docket still illegible at L11 — defer.
