# Ilardi source provenance

## What we captured
- OCR text: `data/raw/ilardi/Renaissance_Vision_djvu_ocr.txt`
  - Source: Internet Archive `bub_gb_peIL7hVQUmwC` (Ilardi, *Renaissance Vision from Spectacles to Telescopes*, APS 2007)
  - Downloaded 2026-07-23 via `archive.org/download/.../bub_gb_peIL7hVQUmwC_djvu.txt`
- Structured extracts (human-curated from OCR + Ilardi's own English translations):
  - `data/curated/ilardi_orders.csv` — Sforza court orders 1462–1466 (age / vision grades)
  - `data/curated/ilardi_prices.csv` — Florence/Prato unit prices
  - `data/curated/ilardi_trade_volumes.csv` — London customs imports + court totals

## What we could NOT get automatically
- JSTOR PDF of Ilardi RQ 1976 (HTTP 403)
- High-resolution scans of ASM/BNF letter facsimiles (figures in book; not machine-tabulated)
- Appendix II monastery sale line-by-line table (OCR garbled; only cash totals usable)

## Processing
```bash
.venv/bin/python scripts/02y_process_ilardi_orders.py
```
