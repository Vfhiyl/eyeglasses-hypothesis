# B1 next HARD hunt — path triage (post-Barbara n=15 → toward ≥20)

**Date:** 2026-07-24  
**Panel now:** hard dated series **n=15** (Barbara Brandeburgo promoted via Hofmann 1881 OA). Soft still: `policastro` (+18 survival, thin mid), `wyatt_henry`/`wolsey` (+3), `nuno_fernandes` (+1).  
**Death-inventory wearers:** CLOSED (`years_after=0`).  
**Do not:** Wikidata proxy gateway; Ammannati Tomo I/II.

**This-pass hard ingest?** **None.** No new person crossed the multi-point OA near-work bar.

Chrono / panel unchanged: `b1_activity_proxy_panel.csv` still lists 15 `hard=True` rows; soft rows unchanged.

---

## Verdict — ranked OPEN paths

| Rank | Path | Status after this pass | Hard upside |
|------|------|------------------------|-------------|
| **1** | **Santoro 1948 *Gli uffici* p.617** (photo/scan) + adjacent Vigevano castellan rows | Still **blocked / not OA**; no OA quote of p.617 recovered (IA/Hathi/Persée/Gallica/GB quota empty). Notre Dame microfilm exists (“request scan”) — human path. | At best **one** mid-career day-date (1467-05-28) with shelfmark; **alone not enough** to promote Policastro. Needed with #2 or more mid points. |
| **2** | **ASM Carteggio interno Pavia cart.757** (+ Vigevano castellan files 1461–1477) | Archive on-site; Ilardi/Covini already used for 1460/1461 ochiali letters. | **Highest density upside** for Policastro FROM-him missives. Best shot at hard + mid fill. |
| **3** | **Roveda 1992** in Chittolini *Metamorfosi* p.71 | Copyright Franco Angeli; not OA. | May quote 1478 petition date/shelfmark — late pin only. |
| **4** | **LBC missive registri after n.9 / post-wear Reg.9** | **Exhausted for Policastro.** See below. | **None** for mid-career densify. |
| **5** | Other Ilardi high/medium not yet hard | Arduino / Sforza **skip** (short +3/+4). Magnia friars / Bartholomeus / Neri Mici **no OA post-wear series**. Barbaro **low** wear + OA dispatches **pre**-wear. | No OA hard candidate this pass. |
| **6** | Blocked mss already flagged | Santoro; Tordi 2 Bese; Vangelista fol.162r | Human photo/transcription only. |

**Best remaining agent-actionable OA lane:** thin. Next agent ROI is low unless a new OA letter edition appears; **human library/ASM** is the real Policastro unlock.

---

## Path detail

### A. LBC missives AFTER n.9 / post-wear Reg.9 (Policastro)

**Project scope:** *La memoria degli Sforza* = **first 16 registers of Francesco I only** (site: missives present **1400–1469**). **No Galeazzo-era (1466+) digitization** → the often-cited **1467-05-28** nomination cannot appear as LBC primary fulltext.

**Registro n.9** (1450–1469, 257 docs) is the *only* register with late dates. Policastro-named titles:

| Doc | Date | Role |
|-----|------|------|
| 9.2 … 9.204 | 1452 → **1460-04-28** | Pre-wear castellan licenses (already in `lbc_missive_9_policastro_bundle.txt`) |
| 9.223–9.257 | **1461-01-01 → 1464-07-18** | Post-wear dates exist, but **titles name no Policastro / Viglevani / Vigevano castellan** |

**Fulltext scrape this pass:** attempted Reg.9 docs **9.223–9.257** → `data/raw/policastro/lbc_post9/` — **local urllib failed** on all URLs (`SSL: WRONG_VERSION_NUMBER`; refetch with default SSL context also **ok=0**). Files are ERROR stubs, **not** verified fulltext. **Title-index scan** (Reg.9 page via browser fetch) is the basis for “no Policastro in post-wear titles.”

**Site search** `/missive/ricerca/?q=…` → “La pagina non è al momento disponibile.” Year-filter GET did not return a filtered result list (form likely needs interactive POST); **title index of Reg.9 is sufficient** to close the post-wear Policastro lane.

**Conclusion:** LBC cannot densify Policastro **1461–1477**. Path **closed** for hard promotion.

### B. Santoro 1948 p.617 OA quote hunt

- Edition: Caterina Santoro, *Gli uffici del dominio sforzesco (1450–1500)*, Milano Bestetti/Treccani 1948; **~300 numbered copies**.
- LBC footnotes (Reg.9 Policastro docs) repeatedly cite **lettera di nomina 1467-05-28** via **Santoro p.617** — still the **only** mid-career day-date, **secondary only**.
- OA fulltext / page quote: **not found** (IA, Persée = review only BEC 1948, no GB usable snippet this pass; prior `gbooks*.json` = API 429).
- Microfilm holding noted (e.g. Notre Dame) — **request chapter scan** is the unlock, not agent scraping.

Even if p.617 is obtained: expect **one** nomination/reconfirmation line + maybe neighboring castellans — **still need more mid points** before `hard=True`.

### C. Other Ilardi high/medium wearers (OA corpora)

| person_id | Why not hard this pass |
|-----------|-------------------------|
| `arduino_baiso` | Wear 1451, death ~1454 → **+3y max**; user skip. Milanesi *Buonarroti* 1869 letter is onset, not a post-wear series; Treccani DBI paywall/no body. |
| `sforza_francesco` | Wear 1462, death 1466 → **+4y**; user skip. |
| `jacopo_magnia_friar` / `egidio_piacenza` | Age-band orders in Della Stufa *Ricordi* 1488–89 only. OA Meli 2009 / Michele da Figline editions are **ambassador** trails, **not** friar near-work after wear. Identity too thin. |
| `bartholomeus_padua` | Single 1318 court self-report; no further named career OA. |
| `neri_mici` | 1329 theft ownership; young; not wear-onset near-work series. |
| `barbaro_zaccaria` | Roster **low** confidence (Manni cite; Ilardi cannot locate letter). Corazzol *Dispacci* 1471–73 = **pre**-1476 wear window; 1994 print **not OA**. Wikipedia offices to 1492 ≠ OA dated near-work series. **Do not promote.** |
| `wyatt_henry` / `wolsey` | Already soft **+3**; dense window too short. |
| `nuno_fernandes` | Soft **+1** nickname only (Rau 1971). |

Death-inventory closed (stapeldon / magnavia / orsi / henry_viii probate): no post-evidence labor series.

### D. New OA letter editions for named wearers

No new OA critical letter edition surfaced this pass that (a) names an Ilardi wearer with medium+ wear confidence and (b) supplies **multiple dated post-wear FROM-them / near-work** points spanning enough years.

Barbara’s Hofmann path is **done** (already hard). Antenhofer 2013 remains copyright optional densify for Barbara only (not a new n).

---

## Soft panel — unchanged

| person_id | years_after | hard? | Blocker |
|-----------|------------:|-------|---------|
| policastro | 18 | False | Mid-career OA near-work missing (LBC exhausted; Santoro/Roveda/ASM human) |
| wyatt_henry | 3 | False | Short dense window |
| wolsey | 3 | False | Short to death |
| nuno_fernandes | 1 | False | Nickname ≠ near-work |

---

## Recommended next actions (human / later agent)

1. **Scan Santoro 1948 pp.615–620** (Vigevano castellanie) — confirm 1467 text + any other Policastro dates.  
2. **ASM:** Pavia **757** and castellan series **1461–1477** for letters **from** Policastro.  
3. Optional: Roveda 1992 p.71 petition shelfmark.  
4. Keep blocked: Tordi 2 / Vangelista fol.162r (not reopened here).  
5. Agent: watch for **new OA** letter editions only; **do not** re-scrape LBC for Policastro mid-career.

---

## Files written this pass

| Path | What |
|------|------|
| `data/raw/policastro/lbc_post9/9_*.html` | Reg.9 docs 223–257 HTML (post-wear window; **no Policastro**) |
| `outputs/tables/b1_next_hard_hunt_notes.md` | This note |
| `outputs/tables/b1_hunt_status_2026-07-24g.csv` | Status snapshot |

**hard n remains 15.**
