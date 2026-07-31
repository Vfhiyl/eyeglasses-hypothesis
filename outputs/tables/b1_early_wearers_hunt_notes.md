# B1 early-wearers hunt — `neri_mici` / `bartholomeus_padua` (+ Barbaro order check)

**Date:** 2026-07-24  
**Goal:** Promote Ilardi **medium** early wearers into hard dated near-work series (hard n=15 → ≥20).  
**Verdict:** **Neither hard-ingestible.** No OA multi-point post-wear near-work series. Panel unchanged (`b1_activity_proxy_panel.csv` still **15** `hard=True`).  
**Also:** `barbaro_zaccaria` Dispacci vs Manni letter = **wrong order** for hard; **do not** hard-ingest (low wear confidence).

---

## Summary

| person_id | wear/evidence pin | birth / death | post-evidence OA dated near-work? | hard? |
|-----------|-------------------|---------------|-----------------------------------|-------|
| `neri_mici` | 1329-08-11 Mercanzia theft complaint (`unum par ochialium`) | **Unknown** (roster `birth≈1300` is heuristic only → age≈29) | **No** — single act; no later notarial/civic OA series | **No** |
| `bartholomeus_padua` | Padua 1318 court self-report needing `oculariis de vitro vel cristallo` | **Unknown** (elderly: *propter senectutem*) | **No** — single testimony; identity otherwise unidentified | **No** |
| `barbaro_zaccaria` | Manni cites Gori letter **1476-06-26** (unlocated; **low**) | 1422/3–1492 (Q55225296) | Dispacci **1471–73** = **before** alleged wear; later offices not OA hard series | **No** (low + wrong order) |

---

## 1) `neri_mici` — Ser Neri Mici da Bibbiena

### Evidence pin (local OA)

| Item | Detail |
|------|--------|
| **Act** | 1329-08-11, Florence — Ser Nerinus Mici (OCR: “Ser Nerins Miei”) da Bibbiena complains to Mercanzia official |
| **Facts** | Goods bought in Florence in August, robbed at Borgo Ghiaceti (Diacceto) en route to Bibbiena; inventory includes **`unum par ochialium`** among haberdashery |
| **Archive** | ASF Mercanzia … f.110 (Davidsohn: StAF/StAP Mercanzia) |
| **OA text** | Davidsohn, *Forschungen zur Geschichte von Florenz* III (1901) **nr.955**, p.190 — local: `data/raw/davidsohn/` (`README.md`, `bub_gb_BIhMAAAAMAAJ_djvu.txt`); extract `outputs/tables/davidsohn_nr955_spectacles.csv` |
| **Secondary** | Rosen 1956 Part II p.204 n.278 (calls him “merchant”); Davidsohn *Geschichte* IV/2 p.18 (“Notar von Bibbiena… Brille beraubt”) without further bio — local OCR `data/raw/orsi/davidsohn-geschichte-von-florenz-v-4-2_djvu.txt` |

### Birth / death

- **No** dated birth, death, testament, or age statement in Davidsohn nr.955 or in the full Forschungen III OCR name scan.
- Roster `birth_year≈1300` / `evidence_age≈29` is a **project heuristic** (young for personal-use presbyopia), **not** an archival pin.
- Title **Ser** + secondary “Notar aus Bibbiena” → notary; complaint itself is ownership/transport of a purchased pair, **not** a wear-onset / vision self-report.

### Post-1329 dated acts (OA hunt)

| Channel | Result |
|---------|--------|
| Forschungen III full OCR | **Only** nr.955 names him. Index “Bibbiena 956” points to the **next** regesto (Bartolus Andreae / Venosa) — **not** a second Neri act. |
| Geschichte IV/2 | One anonymous “Notar von Bibbiena” spectacles robbery line; **no** later named career. Anmerkungen are a **separate Heft** (not in the IV/2 OCR volume). |
| Rosen / Ilardi / Florence glasses OA (Conspicilla 2023) | Repeat 1329 theft only; no career densify. |
| Opera del Duomo / Duomo MPIWG name hits | Unrelated later “Neri” notaries — **not** Mici da Bibbiena. |
| Web / IA person search | No QID; no OA notarial protocol edition for Ser Neri Mici after 1329. |

### Hard-ingest?

**No.**

1. Evidence is **ownership in a theft complaint**, not dated near-work wear-onset.  
2. Even if treated as wear, there is **only one** dated point (1329) — no multi-point post-evidence labor series.  
3. Birth/death unknown → cannot even bound survival years from OA.

---

## 2) `bartholomeus_padua` — Magister Bartholomeus (Padua, 1318)

### Evidence pin

Ilardi 2007 ch.2 (local OCR `data/raw/ilardi/Renaissance_Vision_djvu_ocr.txt`):

> At Padua in 1318 the son of a notary pleaded that because of his advanced age he needed his glass or crystal spectacles (*oculariis de vitro vel cristallo*) for a second look in order to authenticate a document in a Dominican monastery, which had been drafted by his late father.

Latin (Ilardi n.11, quoting Zecchin):

> *Magister Bartholomeus, ipso viso, apparuit turbatus, dicens quod ipsum cum suis oculariis de vitro vel cristallo revidere volebat, quia propter senectutem non ita bene videbat ut videre consueverat*

**Source chain:** Zecchin, “Cronologia vetraria,” *Vetro e vetrai* **I, p.15** — **not OA** (IA search for Zecchin Cronologia / *Vetro e vetrai* / the Latin quote → **0 usable fulltext** this pass). Albertotti 1924 OA PDF checked — **no** Padua 1318 Bartholomeus passage.

### Identity

| What we know | What we do **not** know |
|--------------|-------------------------|
| Forename + title: **Magister Bartholomeus** | Surname / patronymic beyond “son of a notary” (Ilardi paraphrase) |
| Place/year: Padua **1318** | Birth, death, guild, university chair, parish |
| Self-report: needs spectacles for re-reading a document (*senectutem*) | Any second dated act naming the same man |
| Context: Dominican monastery document drafted by late father | Shelfmark / edition of the underlying Padua court act (Gloria *Codice diplomatico padovano* OA stops at 11th c. — irrelevant) |

**Not** identifiable with later “Bartolino da Padova” (composer fl. 1365–1405) or other Magister Bartholomeus hits.

### Post-1318 dated acts

**None recovered in OA.** No career chrono, no second court act, no notarial protocol edition that continues this person after the spectacles plea. Kohl *Padua Under the Carrara* is borrow-only on IA and is not used here as a dated near-work series for this anonymous magister.

### Hard-ingest?

**No.** Single 1318 self-report; person remains a **one-document** early diffusion witness, not a multi-year post-wear near-work panel row.

---

## 3) Quick check — `barbaro_zaccaria` (Manni 1476 vs Dispacci 1471–73)

| Piece | Date | Role for hard? |
|-------|------|----------------|
| Corazzol ed., *Dispacci di Zaccaria Barbaro* (Naples) | **1471-11-01 → 1473-09-07** | Dated diplomatic near-work — but **before** alleged wear letter |
| Manni, *Degli occhiali da naso* (1738) p.79 — Gori collection letter thanking Filippo Strozzi for **12** Florentine pairs | **1476-06-26** | Wear/order pin — **low**: Ilardi cannot locate letter; authenticity uncertain (roster `confidence=low`) |
| Wikipedia / King career sketch | Offices into 1480s–1492 | Secondary office list ≠ OA FROM-him letter/chrono; **not** used to hard-ingest |

**Order problem:** Published Dispacci end **~3 years before** the Manni wear letter. Using them as “post-wear activity” would reverse chronology. Later activity (Mantua/Milan 1476, Padua podestà 1478–79, Rome 1480–81, etc.) exists in secondary bios, but:

1. Wear evidence remains **low** / unrecovered.  
2. User rule: **do not hard-ingest low-confidence Barbaro.**  
3. Corazzol 1994 print is **not OA**.

**→ No hard promotion.**

Local Manni OCR confirms cite only (no letter text): `data/raw/manni/degliocchialidan00mann_djvu.txt` (Zaccaria Barbaro → Filippo Strozzi, 26 June 1476).

---

## Panel / files

| Action | Status |
|--------|--------|
| Ingest into `b1_activity_proxy_panel.csv` | **None** |
| Chrono CSVs for Neri / Bartholomeus | **Not created** (insufficient points) |
| This note | `outputs/tables/b1_early_wearers_hunt_notes.md` |

**hard n remains 15.**
