# Pass BR — IA `page_production` mine + Spicksley loan (2026-08-05)

## Tooling

- New: `scripts/ia_page_production_search.py` (cookie embedded; gateway `127.0.0.1:12309`; retries on SSL/EOF).
- Loan helpers under `data/raw/external_mine_2026-08-03_early/pass_br/`.

## Search (30 queries, retries)

Catalog hits that matter:

| id | title | access |
|--|--|--|
| `devonhouseholdac0000unse` | Gray Devon Household Accounts Pt 2 | borrow **unavailable** |
| `businesshousehol0000unse` | Spicksley / Joyce Jeffreys 1638–48 | **loan OK** |
| `householdaccount0000unse` | Dudley Leicester disbursements 1558–61 / 1584–86 | borrow unavailable |
| `householdpaperso0000grba` | Percy 9th Earl Northumberland papers | borrow unavailable |

## OA OCR scanned (no eyewear pins)

Privy purse (Elizabeth of York / Princess Mary / Henry VIII), Norfolk–Surrey household books 1481–90, Derby household books, Percy regulations, Durham bursar book, Stanley papers (only metaphorical “spectacle of…”). **Dry for Cleux-bar.**

## Spicksley unlock status

- `borrow_book` + `create_token` → success; cookies `loan-` / `br-loan-businesshousehol0000unse` written into script.
- Downloaded encrypted LCP EPUB (`…_lcp.epub`, ~1.8MB) + LCP license JSON.
- Plain `_djvu.txt` still **403**.
- Local LCP decrypt with cookie email as passphrase **failed** `key_check` (need Thorium / correct IA email passphrase).
- ACSM fulfillment URL exists but gateway **502** to `lending6.us.archive.org:8080`.

## Primary estimand

Unchanged (no new promote / no soft→hard yet).

## Next ROI

1. Open Spicksley in **Thorium** (passphrase = IA account email) and mine dated spectacle lines for Jeffreys densify / soft→hard.
2. Same loan path if Gray / Dudley become borrowable.
3. Do not reopen Brittany / Walmysford / Digitarq Contos.
