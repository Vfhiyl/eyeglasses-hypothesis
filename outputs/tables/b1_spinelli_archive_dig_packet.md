# B1 Spinelli archive dig packet (Pass DH, 2026-08-06)

Action sheet for the **only** remaining scientific unlock of Italian merchant SESOI+5 CI (`merchant_treatments` still **FAIL**). Digital OA for Benedetto post-1534 is exhausted (Pass DE/DG/DH). **No invented dates; last-office ≠ death; do not tip to 1547.**

## Why this packet (science)

Italian merchant cell (`datini`, `ardingelli_bese`, `strozzi_filippo`, `spinelli_benedetto`):

| Wearer | Δ now | Role |
|--------|------:|------|
| Datini | +8.5 | locked |
| Ardingelli | +7.5 | locked |
| Strozzi | +11.0 | locked |
| **Spinelli** | **−0.47** | soft ya≈0.03; drives CI lo |

Spinelli: b=1483, onset=1534-08-13, d=1547; T = tip_year − 1528; C med=6.5.

| Tip year | ya | T | Spinelli Δ | Merchant med | Approx boot CI lo | SESOI+5 |
|----------|---:|--:|-----------:|-------------:|------------------:|---------|
| 1534 (now) | 0.03 | 6.03 | **−0.47** | 8.0 | **−0.47** | **FAIL** |
| **1535** | 1 | 7 | **+0.5** | 8.0 | **~+0.5** | **PASS** |
| 1536 | 2 | 8 | +1.5 | 8.0 | ~+1.5 | PASS |
| 1539 | 5 | 11 | +4.5 | 8.0 | ~+4.5 | PASS |
| 1540 | 6 | 12 | +5.5 | 8.0 | ~+5.5 | PASS |

**Correction vs Pass DE note:** dating even **one** calendar tip into **1535** (Δ≥+0.5) is enough to flip merchant SESOI+5 CI under current n=4 bootstrap — even while Spinelli stays **soft**. Hard promote (~+5y multi-point FROM-him) is a separate bar and still needs Yale/ASF densify.

Primary dual SESOI5 freeze already PASS_RAW; this packet targets the **named FAIL cell**, not the freeze medians.

---

## Already recovered (do not re-dig as “new”)

| Pin | Date | Role | Cite |
|-----|------|------|------|
| Mattea → Benedetto wear | **1534-08-13** | onset (*al buio* / *paio d'ochi di vetro*) | Ilardi 2007 ch.3 n.106; Yale Beinecke Spinelli **Filza 164** box **129** fols **2684–86** |
| Alessandro → Capitano Marradi Spinelli | **1534-08-24** | TO-him office (+11d) | Robey 2012 fig.4.1; Yale box **131** file **2713** |
| Robey: **four** originals in same Yale file | undated OA except 08-24 | TO-him | Robey n.5: BRBML Spinelli Family Papers I, box 131 file 2713 |
| Minutes of all four | Feb 1534 – Jan 1536 window | Sangallo copy | Robey body + n.4/n.6 |

Local OCR: `data/raw/external_mine_2026-08-03_early/pass_ay/robey_glory_infamy.txt` (+ PDF sibling).

---

## Dig targets (ordered)

### 1 — Highest leverage / cheapest: date the other three Marradi letters

**Goal:** any day-date ≥ **1535-01-01** → tip≥1535 → merchant CI PASS (still soft OK).

| Repo | Cote | Action |
|------|------|--------|
| **Yale Beinecke** | Spinelli Family Papers I, **box 131, file 2713** | Image/transcribe **all four** Alessandro→Capitano Marradi Spinelli originals; record each day-date + address. |
| **ASF** | MdP **filza 118** fols **87v–88r; 93v; 93v–94r; 98r** (Robey n.6) | Pull Sangallo minutes for same four; extract dates / recipient lists. |
| **ASF** | MdP **volume 181** fol **87v** (Robey fig.4.3 caption) | **Resolve 118 vs 181** cote clash on-site (renumber / parallel copy?). Do not invent which is “right” from OA. |

**Remote fallback (login):** MIA/MAP https://mia.medici.org/ — Robey already cites MAP Doc. for MdP 118 (e.g. n.2: filza 118 fol.235, **1535-08-14** Varini). Search Spinelli / Marradi / Capitano in MdP 118–181. Free register; agent-blocked previously.

**Honesty:** semestral Marradi post alone ≠ hard series; TO-him letters are densify pins for **tip year**, not Cleux-bar FROM-him hard promote.

### 2 — Hard / multi-year path: FROM-Benedetto + contado offices

| Repo | Target | Rule |
|------|--------|------|
| Yale Beinecke | Finding aid `archives.yale.edu/repositories/11/resources/11076` — person `Spinelli, Benedetto, 1483-1547` | FROM-him letters **1535–1545**; Filza **164** context around Mattea wear. **Not** Beinecke MS 850 / Tomasso *Liber Taxarum* 1436 (wrong person). |
| ASF / Archivi Toscana | Cosimo-era capitano/podestà contado claims | Recover **dated** commissions only; secondary undated asserts are leads, not pins. |
| Brown Online Tratte | `SPINELLI`×`BENEDETTO` | Cached **0** — do not invent Tratte pins. |

Hard bar (unchanged): multi-point post-wear series toward ~+5y; death **1547 ≠ tip**.

### 3 — After any real tip change

```bash
export B1_SPARQL=0
python3 scripts/31_b1_freeze_gate.py
```

Update census/panel ya only from dated pins; cite this packet + chrono row.

---

## Explicit skips

| Skip | Why |
|------|-----|
| Re-read Robey PDF for new OA day-dates | Only 1534-08-24 is OA-explicit |
| IA `BeineckeMS850_47` | Tomasso 1436 — false friend |
| Jacks & Caferro *Spinelli of Florence* | Quattrocento Tommaso generation |
| Tomaso di Benedetto podestà S. Gimignano **1565** | Son, post-1547 |
| Tip = death 1547 / last-office alone | Forbidden |
| leo/voiture/jacopo BN manufacturing | Closed |
| Gray restitch / Keil PDF | Still gated; lower priority than this packet |

---

## Visit checklist (print / request)

- [ ] Beinecke: request Spinelli Family Papers I **box 131 file 2713** (all four Alessandro letters)
- [ ] Beinecke: Filza **164** / box **129** fols 2684–86 (Mattea wear context) + any FROM-Benedetto 1535+
- [ ] ASF: MdP **118** fols 87v–88r, 93v, 93v–94r, 98r
- [ ] ASF: MdP **181** around 87v (cote resolve)
- [ ] Photograph recto/verso + any docket dates; note Florentine vs modern year if ambiguous
- [ ] Log pins into `outputs/tables/b1_spinelli_*_chrono.csv` (create on first pin) before census edit

## Expected session outcomes

| Outcome | Effect |
|---------|--------|
| Any tip ≥1535 | Merchant Italy SESOI+5 likely **PASS**; Spinelli may stay soft |
| Tip ≥1539–40 + multi-point FROM | Soft→hard candidate; larger Δ |
| Only more 1534 dates | ya stays ~0; merchant still FAIL — still valuable negative |

---

## Pass DI remote re-probe (2026-08-06) — STILL BLOCKED

Agent re-ran the cheap remote half of Dig target §1. **Zero new day-dates.** Do not re-dig these OA paths next session.

| Probe | Status | Detail |
|-------|--------|--------|
| Robey OCR deeper | **DRY** | Only OA Marradi day-date remains **1534-08-24**; other three originals still undated in thesis text |
| MIA/MAP | **LOGIN WALL** | `https://mia.medici.org/` → `/Mia/LoginUser.do`; guest UI commented out; free register is **human** |
| Beinecke FA / Digital Collections | **NO IMAGES of 2713** | GEN MSS 109 open for research; box 131/file 2713 not free-digitized for day-reading |
| ASF online inventario | **VOLUME-LEVEL ONLY** | Del Piazzo S/17 sommario; carteggi deferred to MIA — no folio dates remote |

**Finding-aid lead (not a pin):** Archives at Yale Marradi search → Filza **164**:

- *Dalla Rocha, Francesco. 5 letters; Marradi. 10pp., **1534 Jul–Oct***
- *Dalla Rocha, ----. 3 letters; Marradi. 6pp., **1534-35*** (Box **128**, Folder **2630**)

Shelf ranges may hide ≥1535 day-dates. **Photograph/transcribe before any ya edit.** Do **not** tip from “1534–35” alone.

### Pass EW (2026-08-07) — MIA logged-in closed

| Probe | Status | Detail |
|-------|--------|--------|
| MdP 181 browse images | **EMPTY** | numbered + unnumbered: none / private |
| `docs-mdp 181 --all` | **61 DEs, 0 tip** | no Spinelli / Marradi / Capitano di Marradi |
| word Spinelli / Marradi / Benedetto Spinelli | **DRY for tip** | other Spinellis only; Capitano di Marradi exact = 0 |
| volume-find 118 | **wrong century** | only dated hit 1627 (id 944); Alessandro minutes = vol **181** |

**Do not re-open MIA for Spinelli tip.** Human next = Aeon § below / ASF email.

---

## Concrete next human steps (Pass DI)

### 1 — Cheapest remote-but-human: Yale Aeon digitization

1. Create Yale Special Collections (**Aeon**) account: https://library.yale.edu/find-request-and-use/use/using-special-collections  
2. Digitize guide: https://library.yale.edu/find-request-and-use/use/using-special-collections/request-digitization  
3. In Archives at Yale, **Request → Request Digitization** (PDF) for:

| Priority | Call | Container | What to extract |
|----------|------|-----------|-----------------|
| **P0** | GEN MSS 109 | **Box 131, file 2713** | All **four** Alessandro→Capitano Marradi Spinelli originals — **every day-date + address docket** |
| **P1** | GEN MSS 109 Filza 164 | Box **128** folder **2630** (+ Jul–Oct Marradi Dalla Rocha sibling) | Day-dates only; TO-him densify if addressed to Capitano/Benedetto |
| **P2** | Filza 164 / box **129** fols **2684–86** | Mattea wear context | Confirm onset; scan neighbors for FROM-Benedetto **1535+** |

**Aeon Notes field (paste):**  
`Need day-dates (recto/verso + dockets) for all Alessandro de' Medici letters to Capitano di Marradi Spinelli in box 131 file 2713 (Robey 2012 figs 4.1–4.2). Also day-dates on Filza 164 Marradi Dalla Rocha letters (incl. folder 2630). Florentine vs modern year if ambiguous. Research: merchant SESOI tip≥1535.`

Fallback contact: `beinecke.library@yale.edu` — cite GEN MSS 109 / box 131 / 2713.

#### Ready-to-send Aeon / Beinecke email (Pass DO)

**To:** `beinecke.library@yale.edu`  
**Subject:** Digitization request — GEN MSS 109 Spinelli, box 131 file 2713 (day-dates)

```
Hello Beinecke Special Collections,

I request PDF digitization (or reading-room imaging) of materials in
GEN MSS 109, Spinelli Family Papers I, for a dated-pin research project
on Benedetto di Guaspare Spinelli (1483–1547).

Priority 0
- Box 131, file 2713 — all Alessandro de' Medici letters to the Capitano
  di Marradi Spinelli (Robey 2012 cites four originals in this file; only
  1534-08-24 is published with a day-date). Please image recto/verso and
  any docket dates for every letter in the file.

Priority 1
- Filza 164 / Box 128, folder 2630 — Dalla Rocha Marradi letters marked
  1534–35 in the finding aid (day-dates only; do not rely on shelf ranges).
- Sibling Filza 164 Marradi Dalla Rocha Jul–Oct 1534 if adjacent.

Priority 2
- Filza 164 / Box 129, fols. 2684–86 — Mattea Spinelli → Benedetto
  (wear letter 1534-08-13) and immediate neighbors for any FROM-Benedetto
  items dated 1535 or later.

Needed from each image: calendar day-date (Florentine vs modern year if
ambiguous), sender, addressee. Purpose: confirm whether any tip year is
≥1535 (merchant activity panel). I can use Aeon Request Digitization if
that is preferred over email.

Thank you,
[NAME]
[AFFILIATION / EMAIL]
```

**Aeon Notes field (short paste, unchanged):**  
`Need day-dates (recto/verso + dockets) for all Alessandro de' Medici letters to Capitano di Marradi Spinelli in box 131 file 2713 (Robey 2012 figs 4.1–4.2). Also day-dates on Filza 164 Marradi Dalla Rocha letters (incl. folder 2630). Florentine vs modern year if ambiguous. Research: merchant SESOI tip≥1535.`

### 2 — Human MIA register (ASF minutes without Florence trip)

1. Register at https://mia.medici.org/ → *Register here* (`/Mia/user/RegisterUser.do`).  
2. Search: `Spinelli`, `Marradi`, `Capitano`, MdP **118**, MdP **181**.  
3. Pull / screenshot any Doc. with day-date ≥ **1535-01-01** addressed to Capitano Marradi Spinelli (or Benedetto).  
4. Known MAP cite already OA (not a Spinelli tip): MdP 118 fol.235, **1535-08-14** Varini (Robey n.2) — **wrong recipient**; useful only as MdP 118 coverage proof.

### 3 — ASF on-site / reproduction

Email `as-fi@cultura.gov.it` (PEC `as-fi@pec.cultura.gov.it`; tel +39 055 263201):

> Richiesta consultazione/riproduzione: ASF Mediceo del Principato **filza 118** cc. **87v–88r, 93v, 93v–94r, 98r** (minute lettere Alessandro → Capitano di Marradi Spinelli; cfr. Robey 2012). Verificare anche **vol./filza 181** c. **87v** (divergenza di segnatura Robey fig.4.3 vs n.6). Serve data completa di ciascuna lettera.

Sala: resolve **118 vs 181** on the shelf; photograph recto/verso + recipient lists.

#### Ready-to-send ASF email (Pass DO)

**To:** `as-fi@cultura.gov.it` (PEC: `as-fi@pec.cultura.gov.it`)  
**Subject:** Richiesta consultazione/riproduzione — MdP filza 118 / 181 (Spinelli–Marradi)

```
Gentili funzionari,

chiedo consultazione e, se possibile, riproduzione digitale delle seguenti
unità dell’Archivio di Stato di Firenze, Mediceo del Principato:

1) Filza 118, carte 87v–88r; 93v; 93v–94r; 98r — minute di lettere di
   Alessandro de’ Medici al Capitano di Marradi Spinelli (cfr. Robey,
   Glory and Infamy, 2012, n.6).
2) Verifica della segnatura parallela / alternativa: volume o filza 181,
   c. 87v (divergenza fig.4.3 vs n.6 in Robey).

Obiettivo della ricerca: recuperare la data completa di ciascuna lettera
(giorno-mese-anno; stile fiorentino se indicato) e il destinatario.
Non mi servono trascrizioni complete se le immagini sono leggibili.

Cordiali saluti,
[NOME]
[AFFILIAZIONE / EMAIL / TELEFONO]
```

### 4 — After any real day-date ≥1535

- Log into `outputs/tables/b1_spinelli_*_chrono.csv` (create on first pin) with exact cote + quote.  
- **Do not invent; parent wires** census `ya` / remasure (`B1_SPARQL=0 python3 scripts/31_b1_freeze_gate.py`).  
- Death **1547** and last-office alone remain forbidden tips.
