# B1 free roam — hard n=19 → 20 hunt (2026-07-31 midday)

**Hard panel unchanged: n=19.** No ingest this pass.

## Goal
Find one more hard-eligible named wearer with OA multi-point post-wear near-work (panel minimum among hard is Alessandra **+5y**; Domenichi-class +9 imprint / letter density OK).

## Paths tried

| Lead | Result |
|------|--------|
| Digitarq `óculos` / Latone / Alfonso Iannis / Nuno | No usable 15c personal-wear densify. `Afonso Anes` hits are King Afonso V false friends. Nuno nickname still soft only. |
| Cambini Portugal orbit (Filippa / Latone / Vaschi / Alfonso Iannis) | Still thin / trade / identity not pinned — already flagged late4. |
| Wyatt LP local OCR post-1530 | Only enfeoff **1531-04-06** + “late treasurer” labels; dense near-work still ends **1530-02** (+3 soft). |
| Yale Spinelli digitization | Filza **163** Tommaso letters digitized (pre-Benedetto wear). **Filza 164** Mattea 1534 occhiali letter **not** found in digital catalog; Beinecke JSON/HTML blocked by bot wall for agent. |
| Brown Tratte `SPINELLI` / `BENEDETTO` | `sqlform.php` returns **No Results found** for SURNAM1=SPINELLI (and Benedetto). Contado capitano/podestà likely outside Tre Maggiori file anyway. |
| Spataro Cavazzoni IIIF (new) | Downloaded Vat.lat.5318 **213r–214v, 240r–243r, 165r–v** → `data/raw/spataro_giovanni/iiif_cavazzoni/`. DigiVatLib lists two Spataro→Cavazzoni letters. **213r** salutation to Marco Antonio; **213v** already on chrono as **1532-09-08** (prior keep). Second block (**240–243**) includes pre-wear copy material (vision OCR inconsistent; no secure post-**1533-10-30** FROM-him date). Pizoni **1537** / Serafino **1538** in TOC are → **Del Lago**, not Spataro. |
| San Petronio tenure 1512–1541 | Institutional continuity only — no OA day-dated payment/act series this pass. Do **not** hard-ingest Spataro on tenure alone. |
| IA metadata `occhiali`+lettere 1400–1600 | 0 hits (catalog, not OCR). Persée search page not useful this pass. |

## Soft / candidate status (unchanged ingest)

| person_id | Status |
|-----------|--------|
| `spataro_giovanni` | Still **not hard** — observed FROM-him through **1533-10-30** (~+1.6y). Cavazzoni densify did not clear +5 bar. |
| `spinelli_benedetto` | Soft densify only; wear 1534; ceiling ~+13 (d.1547). Need Beinecke Filza 164 OA or dated contado office pins. |
| `wyatt_henry` / `wolsey` / `nuno_fernandes` | Soft +3 / +3 / +1. |

## Files written this pass
- `data/raw/spataro_giovanni/iiif_cavazzoni/*.jpg` (+ `crops/`)
- `data/raw/spataro_giovanni/digivat_detail_refresh.html`
- `data/raw/spinelli_benedetto/tratte_*.html`
- This note

## Best next unlocks (ranked)
1. **Human / browser:** Beinecke Filza **164** (Mattea→Benedetto 1534) + any FROM-Benedetto letters **1535–1545** if digitized later; or Jacks–Caferro letter calendar quotes with day-dates.
2. **Human library:** ASM Policastro mid-career (already on blocked list) — still highest mid densify for an *already-hard* person, not new n.
3. **Agent:** watch for new OA letter editions naming Ilardi wearers; optional Digitarq folio-pin of Azevedo 1492 Rebordosa collação (quality only, not +n).
4. Do **not** auto-hard Spataro on San Petronio tenure or Cavazzoni without a dated FROM-him leaf after 1533-10-30.

**hard n remains 19.**
