# Archivio di Stato di Prato — Fondo Datini (digital)

- Portal: http://datini.archiviodistato.prato.it/
- Search: http://datini.archiviodistato.prato.it/la-ricerca/
- **Note:** old `datini.archiviodistato.firenze.it` 301s away; do not use.
- Access: plain HTTP works **without** the Wikidata proxy (proxy returns 405).

## What we pulled

| Asset | Path / table |
|-------|----------------|
| Busta 721 catalog (246) | `outputs/tables/datini_busta721_catalog.csv` |
| Busta 713 catalog (313) | `outputs/tables/datini_busta713_catalog.csv` |
| Ochiali letter dossier (Ilardi ↔ ASPO) | `outputs/tables/datini_ochiali_letter_dossier.csv` |
| Piaciti Jul–Sep 1400 images | `images/ASPO00076086*` … `76099*` |
| Gaddi Sept 1400 images | `images/ASPO00076013*`, `73932*`, `73933*` |
| Bologna buste **717–720** + extras **1094/1100–1103** (2026-08-22) | `datini_busta717_catalog.csv` etc. |
| Bologna pooled monthly + pre baseline | `datini_bologna_buste717_721_monthly.csv`; `b1_datini_order_episode_monthly_with_pre.csv`; curated pre pins `datini_bologna_pre140007_curated.csv` (n=10) |
| Firenze 713 parallel (suppliers) | `b1_datini_firenze713_parallel_monthly.csv` |
| Dig notes | `outputs/tables/b1_datini_aspo_prebaseline_2026-08-22.md` |
| Datini-co. letter 1400-06-28 images | `images/ASPO00075258_*.jpg` |
| Franklin–Lyons city/year timeline | `franklin_timeline.json` (GitHub docuracy/datini) |

## Key finding

Catalog **free-text does not OCR letter bodies**: `ochiali` → 0 hits; `occhiali` → 1 unrelated 1408 hit.  
Spectacle orders are recovered by **segnatura + Ilardi quotes + image download**.

Primary chain (Datini in Bologna, Venice suppliers, 1400):

1. Piaciti 24 Jul — will supply (`ASPO00076089`)
2. Piaciti 31 Jul — sent 3 pairs (`ASPO00076090`)
3. Piaciti 7 Aug — remake if not fine (`ASPO00076091`)
4. Gaddi 11–18 Sep — “most perfect” / 12 pairs (`ASPO00073932`, `73933`, plus `76013` on 15 Sep)
