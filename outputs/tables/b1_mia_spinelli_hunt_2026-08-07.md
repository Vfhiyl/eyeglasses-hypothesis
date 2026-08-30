# MIA Spinelli hunt — first pass (2026-08-07)

Script: `scripts/32_mia_search.py` (cookie in `MIA_COOKIE`; refresh when session dies).  
Cache: `data/raw/mia_spinelli/`.

## How to run

```bash
python3 scripts/32_mia_search.py people Spinelli
python3 scripts/32_mia_search.py docs-person 334 --year-from 1534 --year-to 1536
python3 scripts/32_mia_search.py docs-place Marradi --year-from 1534 --year-to 1540
python3 scripts/32_mia_search.py volume-find 181
python3 scripts/32_mia_search.py document 112
python3 scripts/32_mia_search.py spinelli-hunt
```

## Key IDs

| What | MIA id | Notes |
|------|--------|-------|
| Alessandro de' Medici | people **334** | b.1510 d.1537 |
| Marradi | place **28628** | |
| Spinelli, Benedetto | people **1955** (activeStart 1544) / **30838** | **no linked DEs** in advanced search |
| MdP filza **181** | volumeId **51** | years **1534-02-19 → 1536** — Robey window |
| MdP filza **118** | volumeId **944** | years **1627** — **wrong century** (Ferdinando II) |
| MdP **330** | volumeId **775** | 1537–1546; has Marradi place docs (not Spinelli) |

## Findings

1. **MdP 181 is live in MIA** via Alessandro person search: **68** catalogued DEs dated 1534–1536 (40×1534 + 28×1535).
2. Full pull of those 68 (`alessandro_doc_*.json` + `alessandro_181_scan.json`): **0** hits for `Spinelli` / `Marradi` / `Capitano di Marradi` / `occhi di vetro` in synopsis, recipient, referred people, or transcriptions.
3. Robey’s **1535-08-14 Varini** minute is present as MIA **doc 112** (to Favorino Varini) — proves this is the right minutes series, but Spinelli’s Marradi letters are **not** among the indexed DEs (yet).
4. Place=Marradi 1534–1540: 4 Cosimo-era 1537 letters in MdP 330 (Ulivieri / Corsellini / Fabbroni) — not Spinelli.
5. Word search needs `owner` account object; without it API returns “Owner is empty”. People/place/advanced search work with cookie alone.

## Science implication

MIA unlocks **browsing Alessandro MdP 181 minutes**, but **does not yet hand us a dated Spinelli tip≥1535**.

**Pass EW (2026-08-07) — CLOSED for tip:** UI browse = no images; `docs-mdp 181 --all` = 61 DEs, 0 Spinelli/Marradi/Capitano; word `Spinelli`/`Marradi`/`Benedetto Spinelli` = no Capitano di Marradi / Benedetto tip. Do **not** re-scrape MIA for this tip. Next = Yale Aeon box 131 file 2713 (`b1_pass_ew_mia_spinelli_closed.md`).

Previous next (superseded):

1. ~~In MIA UI: open volume **181** manuscript viewer~~ — done; empty.
2. Yale Beinecke box 131 file 2713 (four originals) — **still highest-leverage remote path for day-dates**.
3. ASF reading-room for MdP 181 / Robey fols if UI images incomplete.

Do **not** tip Spinelli from Varini 1535-08-14 or generic 1535 Alessandro minutes.
