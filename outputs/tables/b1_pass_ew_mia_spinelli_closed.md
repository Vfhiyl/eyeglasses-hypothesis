# Pass EW — MIA Spinelli path closed; Yale Aeon is the unlock (2026-08-07)

## Judgment

Dual SESOI+5 freeze already **PASS**. The only named scientific FAIL left is **Italian merchant cell** CI lo (Spinelli soft tip **1534-08-13**, ya≈0). That unlock is **tip≥1535** from one of the other three Alessandro→Capitano Marradi originals (or ASF minutes of same).

**Do not keep scraping MIA for this tip.** Remote OA + logged-in MIA are exhausted for Benedetto / Capitano di Marradi day-dates.

## What this pass did

1. **Closed MIA Volume 181 UI path** (user verified): uploads=0; browse = no numbered/unnumbered images (private or absent).
2. **Wired `docs-mdp`** = volume-page “Documents related to this Volume” advanced search; pulled **all 61** MdP 181 DEs → `data/raw/mia_spinelli/docs_mdp_181_all.json`. **0** Spinelli / Marradi / Capitano di Marradi recipients.
3. **Fixed word search** (`owner=amccoyliam`, `searchType=DE_SYNOPSIS|DE_TRANSCRIPTION`; response key `data.docs`).
4. **Word hunt:**
   - `Spinelli` synopsis **26** / transcription **33** — all other Spinellis (Isabella, Giovanni Battista, Tommaso di Benedetto 1640s, etc.). **0** Benedetto / Capitano di Marradi.
   - `Benedetto Spinelli` synopsis → **0**.
   - `Marradi` synopsis **4** / transcription **15** — Cosimo-era or undated; **0** Alessandro→Spinelli 1534–36.
   - Exact `"Capitano di Marradi"` / `"occhi di vetro"` → **0**.
5. **Volume-find 118:** only MIA hit with years is **1627** (volumeId 944). Alessandro-era Robey “filza 118” is **not** a separate browseable volume named 118 in MIA (minutes live as **181** / volumeId **51**; Varini 1535-08-14 = doc **112**).
6. Soft→hard lottery (Washington post-1783 spectacle; Founders/Mount Vernon HTTP blocked this pass; public secondary sources only restate 1783) — **no new pin**. Knut SDHK 22493 still captcha-gated.

**No census edit / no remasure** (no new dated tip).

## Highest ROI next (human)

**You:** send the ready Yale Beinecke Aeon / email in `b1_spinelli_archive_dig_packet.md` (§ Ready-to-send Aeon).

| Priority | Ask |
|----------|-----|
| **P0** | GEN MSS 109 **Box 131 file 2713** — all four Alessandro→Capitano Marradi Spinelli originals; every day-date |
| P1 | Filza 164 Box 128 folder 2630 (Dalla Rocha Marradi 1534–35 shelf range — day-dates only) |
| P2 | Filza 164 Box 129 fols 2684–86 Mattea wear neighbors for FROM-Benedetto ≥1535 |

Any calendar tip **≥1535-01-01** flips merchant Italy SESOI+5 CI under current n=4 bootstrap (Spinelli may stay soft).

Fallback: ASF email in same packet (MdP 118 fols + resolve 181/87v).

## Explicit non-next

- Re-browse MdP 181 images in MIA
- Tip from Varini 1535 or generic Alessandro 1535 minutes
- Tip = death 1547 / last-office
- New Cleux-bar OA wearer lottery (queue empty for high ROI)
- Vidier *Comptes* e-chase (HARD_TO_FIND)

## Script

`scripts/32_mia_search.py`: `docs-mdp`, word `--type DE_SYNOPSIS|DE_TRANSCRIPTION`, `MIA_ACCOUNT` / `user/me`.
