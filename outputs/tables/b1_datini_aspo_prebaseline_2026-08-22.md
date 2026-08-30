# Datini ASPO continued dig — 2026-08-22 (pass 2)

Portal OK direct. Goal: thicken pre-1400-07 Bologna baseline / FROM-him stream.

## New harvests

| busta | n | note |
|------:|--:|------|
| 717 | 105 | BOLOGNA; span 1396–1401; **almost no 1400-H1** (only 1396–97 pre bits) |
| 1094, 1100–1103 | ~1.5k | mixed; few extra Bologna-dest pre pins |

## Curated pre-order letters **to Bologna** (destinazione=BOLOGNA, before 1400-07-01)

`outputs/tables/datini_bologna_pre140007_curated.csv` — **n=10** (was 7 from 718–721 only):

| date | busta | mittente | from |
|------|------:|----------|------|
| 1400-03-07 | 720 | Bencivenni | Pisa |
| 1400-04-10 | 1103 | Tecchini Tommaso | Maiorca |
| 1400-06-01 | 720 | Agli | Pisa |
| 1400-06-28 | 718 | **Datini Francesco… e Stoldo** | Firenze |
| 1400-06-28 | 720 | Agli | Pisa |
| 1400-06-28 | 1094 | Guazzalotti | Pistoia |
| 1400-06-28 | 1100 | Niccolò di Piero… | Prato |
| 1400-06-29 | 718 | Domenico di Cambio | Firenze |
| 1400-06-29 | 719 | Tecchini Niccolò | Firenze |
| 1400-06-30 | 719 | Tecchini Niccolò | Firenze |

Datini-company letter images saved: `images/ASPO00075258_*.jpg` (business; no ochiali on multimodal skim).

## Query dig (caution)

`query=BOLOGNA` + date ≤1400-06 → hundreds of hits, but **destinazione** mostly Firenze/Pisa/Genova (body mention). True Bologna-dest ⊂ curated list above.

`query=DATINI FRANCESCO` 1400 (500/9381 sampled): company-as-mittente common; **0 to Bologna** in sample.

## Parallel stream: busta 713 → Firenze (same Venice suppliers)

`b1_datini_firenze713_parallel_monthly.csv`:

| window | n | /mo |
|--------|--:|----:|
| 1400-03..06 pre | 74 | 18.5 |
| 1400-07..09 order Q | 24 | 8.0 |
| 1400-10..1401-06 | 83 | 9.2 |

Healthy **pre** density here (Piaciti/Gaddi heavy). Useful for **supplier continuity**, not Bologna-branch wearer DiD. Order quarter is *lower*, not a spike.

## Bologna pooled 717–721 (unchanged story)

pre 1400-H1 still ~7–10 letters; July+ tens/month. July surge = traffic/filing.

## Ceiling / stop rule

Further ASPO busta-prowling unlikely to create a thick Bologna pre-order series. Remaining value:
- multimodal/OCR the 10 curated pre letters only if claiming company near-work (weak);
- treat **713** as supplier-side parallel;
- do **not** promote Datini to strict-sharp on this baseline.
