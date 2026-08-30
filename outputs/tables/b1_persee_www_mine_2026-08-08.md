# Persée www fulltext mine (2026-08-08)

Client: `scripts/persee_search.py` (gateway default).  
Raw: `data/raw/persee_search/mine_2026-08-08/`.  
Note: boolean `OR` on Persée often returns ~400k+ garbage totals — **use quoted phrases**.  
`/doc/` HTML is shell-only; `docAsPDF` → **403** (Altcha). Mine from **search snippets** + known OA mirrors.

## Verdict

**No new Cleux promote** from this pass. Best yield = **Hesselin career densify pointers** (still no new spectacle pin; HARD remains OA-closed). Lemma lottery mostly modern/noise; two named medieval/early-modern spectacle mentions are death-inventory or secondary CR only.

## Soft/HOLD roster

### Denis Hesselin (soft +32, HARD OA-closed) — **best Persée hit**
Phrase `"Denis Hesselin"` → **29** docs. Snippet career arc (no new lunettes):

| pin | source (Persée) |
|---|---|
| prévôt des marchands **1470–1474** (var. 1470–72) | Romania 1873; BCRH 1927; JDS 1986 |
| then **receveur du Domaine et des aides** Paris | JDS 1986; Médiévales 1986 |
| living courtier under Louis XI (wife’s childbirth; king godfather) | BEC 1850 |
| **Louis XII letter 1499-12-29** in favour of Denis Hesselin (still living) | BEC tables 1849/1859 |
| greffier attribution debate Chronique scandaleuse → “1470–1510” | SHF 1904 |

→ Supports soft terminus toward 1499/1506; **does not** unlock day-dated FROM-him post-1474 comptes (still library-gated). No spectacle lemma in these snippets.

### Cleux / Cleuz (HOLD, no obit)
| hit | note |
|---|---|
| Jones–Guinot *JDS* 2010 I+II | Already mined; Jean de Cleuz enfant de chambre / étrennes cluster |
| Olivier de Cleuz / Cleux, lieutenant Fougères 1435 | Different person; living admin |
| Jean de Cleuz **garde-robier 1441-01-03** (Delort *Fourrures* BEFAR 1978) | Living densify only; still **no death** |
| Toponym / later noblesse Cleuz | Noise |

**No obit** → Cleux-bar unchanged.

### Cusac / Marzelière / Voiture / René II
- `"Thomas Cusac"` ≈ empty; `Cusac` = modern noise.
- `"Marzelière"` = place-name / later Mme; **no** 1433 lunettes re-hit beyond Jones vein.
- Voiture + lunettes = advertising noise; bare `"Vincent Voiture"` = lit history, no new wear pin.
- René II + lunettes = Cross of Lorraine noise; Calmet alliance 1474 already known soft path.

## Lemma veins

| query | total | Cleux-useful? |
|---|---:|---|
| `"paire de lunettes"` | 332 | Mostly modern; Ilardi/Medici 1451 already known |
| `besicles` | 256 | **Retz** secondary (below); sculpture Jérémie Dijon |
| `bericles` | 43 | Gemstone / toponym; **Testamale** death inv. |
| `"lunettes d'or"` | 60 | Literary metaphor |
| `"lunettes clouants"` | 0 | — |

### Named spectacle mentions (not promoted)
1. **Bernard Testamale** (Vic-Fézensac) — *Annales du Midi* 1983: death inventaire *unum stuch cum bericlis* → **death path, years_after=0**, exclude Cleux labor.
2. **Cardinal de Retz** — BEC 2009 CR of *Correspondance*: buys **besicles Dec 1669** (living). b.1613 d.1679 → soft ~+10y **if** primary letter verified. **LEAD only** (not on treatment roster; secondary CR; PDF 403).

### Already-closed secondary
Dollfus 1969 BSNAF séance; Margolin 1975 satire; Pansier histoire des lunettes pointer (BulMo 1901).

## Ops notes
- Prefer: `python3 scripts/persee_search.py -q '"Denis Hesselin"' --pages 3`
- Avoid unquoted `OR` queries.
- Fulltext body needs Altcha PDF path or user-provided OCR — search snippets are the workable ore for now.

## Action
- **No panel / candidates CSV change.**
- Optional later: chase Retz 1669 letter in Pléiade/Correspondance OA; chase Louis XII 1499 Hesselin letter cote from BEC table if hardening soft terminus.
