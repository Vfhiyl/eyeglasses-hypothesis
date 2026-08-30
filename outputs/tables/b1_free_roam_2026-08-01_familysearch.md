# B1 free roam — FamilySearch Full-Text (2026-08-01 night)

Gateway `127.0.0.1:12309`; session `config/familysearch_session.local` (gitignored).  
Script: `scripts/familysearch_fulltext_search.py`.

## Method

| Facet | Param |
|-------|--------|
| UK & Ireland | `c.recordPlace1=on&f.recordPlace0=9` |
| Century bucket | `c.recordYear1=on&f.recordYear0=1600` (also 1300/1400/1700) |

Queries run: `spectacles`, `"pair of spectacles"`, `"paire of spectacles"`, `"my spectacles"`, `"spectacles and case"`, `eyeglasses`, `spectaclys` (0), `"peyre of spectacles"` (0), Continental Europe place=5.

Hit dumps: `outputs/tables/familysearch_*.jsonl`.  
Classified shortlist: `outputs/tables/familysearch_b1_shortlist.jsonl`.

## Scale (UK)

| Filter | ≈hits |
|--------|------:|
| spectacles (all) | ~281k (mostly US newspapers) |
| + UK | ~4033 |
| + UK ∩ 1300 | 2 |
| + UK ∩ 1400 | 1 |
| + UK ∩ 1500 | **0** |
| + UK ∩ 1600 | **102** (~87 wills/probate) |
| + UK ∩ 1700 | ≥100 (sampled) |
| `"pair of spectacles"` UK | ≥100 |
| `"my spectacles"` UK | ≥60 |
| eyeglasses UK | modern only |

## Verdict for B1 primary

**No new hard-birth named wearer ready to ingest.**  
Nearly all solid hits are **terminal will / inventory ownership** → `years_after≈0` will-path (same class as Baret / Carre). Useful as English parallel densify / appendix, not SESOI panel unlock.

## Best personal / bequest leads (≤1650)

OCR is noisy; treat names as **soft** until human/vision on the ARK image.

| Year | Place | Signal | ARK | Note |
|------|-------|--------|-----|------|
| **1615** (proved ~1619 folder) | Chester | **Thomas Allerton**, vintner; bequeaths **“my spectacles with the case of brass”** to cousin **Randall Holme(s)** | [3Q9M-C394-RZPQ](https://www.familysearch.org/ark:/61903/3:1:3Q9M-C394-RZPQ) | API OCR misread testator; vision + stitched DZ tiles confirm Allerton. Will dated **1615-04-25**. Still will-path. Stitch: `data/raw/familysearch_fulltext/priority_images/allerton_will_L12_stitched.jpg` |
| **1630/31** | Lancashire | “paire of **Gilber** Spectacles and case” in chest / books | [S3HY-6L8S-FWN](https://www.familysearch.org/ark:/61903/3:1:S3HY-6L8S-FWN) | Personal gear + books |
| **1616** | Cheshire | “pair of spectacles” + **herball** in inventory | [S3HT-6SRS-P9Y](https://www.familysearch.org/ark:/61903/3:1:S3HT-6SRS-P9Y) | Near-work adjacent inventory |
| **1633** | Cornwall (St Levan / “St Leverne”) | “one pair of spectacles” in apparel inventory | [S3HY-6R49-9ZJ](https://www.familysearch.org/ark:/61903/3:1:S3HY-6R49-9ZJ) | Inventory path |
| **1642** | Hertfordshire | “two pair of spectacles” | [3Q9M-CSRJ-2S2L-2](https://www.familysearch.org/ark:/61903/3:1:3Q9M-CSRJ-2S2L-2) | Household inventory |
| **1660** | Cheshire | bequeath spectacles; grandchildren **Richard / Mary Walthall** | [S3HT-XC9R-LV](https://www.familysearch.org/ark:/61903/3:1:S3HT-XC9R-LV) | Named kin (post-1650) |

## Merchant stock (not wearers)

| Year | Signal | ARK |
|------|--------|-----|
| 1626–29 Cheshire | “**Thirtie paire** of spectacles and Cases” | [3Q9M-CSN8-13SX-M](https://www.familysearch.org/ark:/61903/3:1:3Q9M-CSN8-13SX-M) |
| 1665 Cheshire | graded “Spectacles at 3 / 4…” shop stock | multiple |
| 1668–69 Lancs | “dozen of Spectacles” | shop inventories |

## Likely OCR false positives (do not chase as wearers)

| Year | Why reject |
|------|------------|
| London 1388–96 “spectacles” | Latin land/probate OCR junk (`ten spectacles`, `Shops are soley Spectacles`) |
| Norwich wills 1435–44 | Phrase “spectacles are now to plund debt” — not a bequest formula |
| Lorraine 1267–68 | French *spectacles* = public shows / games |

**UK ∩ 1500 century = 0** in Full-Text for `spectacles` — gap is indexing/coverage, not evidence of absence.

## Overlap with curated English will-path

No clear hit on Baret / Carre / Walmysford strings in this dump (`spectaclys` / `peyre` queries empty). FS corpus here is mostly **Chester / Lancashire / Cornwall / Norfolk** diocesan wills, not the printed Tymms / York sets already logged.

## Next (human / browser)

1. Open the six ARKs above → confirm testator name + probate year on the image (vision).  
2. If a named testator has published birth/baptism → soft candidate only; still will-path for primary.  
3. Optional: re-run when session refreshed; expand `"my spectacles"` with `--record-year 1600`.

## Ingest decision

- **Primary / hard:** none  
- **Soft candidates CSV:** defer until ARK vision yields a stable testator identity  
- **Appendix value:** English probate densify — spectacles common in 17c Cheshire/Lancs inventories; personal bequests exist but late for Macfarlane +15 design
