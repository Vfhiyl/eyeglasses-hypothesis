# B1 free roam — new mine: letters / local corpora / PARES (2026-08-02 evening)

Decision: leave dense 17c English will densify; open **letter-path** + continental catalog filters.

## Verdict

**EMLO spectacles dump** (`data/raw/emlo_spectacles_solr.json`, n=26) is the useful new seam: several **living** wear/purchase mentions (not death inventories). Still soft — not hard-ingested.

## Soft letter-path finds (pre-1720)

| Who | Year | Signal | Why interesting |
|-----|------|--------|-----------------|
| **William Lynnet** (1623–1700), Trinity | **1672** | “Has just been to London to **buy a pair of spectacles**” → John Thornton | Live purchase at ~age 49; potential years_after if later activity measured |
| **Anthony Wood** (recipient; Ant. Wood) | **1676** | Sheldon had Wood’s spectacles “new set” + duplicate; Wood draft: “they **fit me so well** that I shall take care of them as long as I live” | Named living wearer + continued use intent; antiquary/scholar near-work |
| **Arthur Charlett** (“A.C.”), Master Univ. Coll. | **1707** | Gregory will fetch spectacles if Charlett reports **how long he has worn** them | Explicit wear-duration question (onsetish proxy possible) |
| William Cole | 1695 | Had “monoptick spectacles” made / distributed | More maker/experiment than ordinary wearer |

Export: `outputs/tables/emlo_spectacles_pre1720_soft.json`.

## Dead ends this pass

- **PARES** `anteojos` + `fechaDesde=1400&fechaHasta=1600`: filter **ignored** in practice; still dominated by 20c HISMA military *anteojos de tijera*. One soft later hit: **1710** Borja letters — *anteojos para la vista del tío Coloma* (vision spectacles; nephew correspondence). Description `12988743`.
- **IA advancedsearch** early `spectaclys` / “pair of spectacles” 1400–1650: **0** full-text hits (index thin).
- Local printed English wills corpus: only already-logged **John Baret 1463** silver-gilt *spectaclys* (Tymms).
- UK FS Full-Text @1550 already empty earlier tonight.

## Next if continuing this mine

1. Pull full EMLO / Bodleian images or printed Wood *Life & Times* around Dec 1676 for firmer onset.
2. Wikidata/activity series check for Wood / Lynnet / Charlett (letter-path may beat will-path for years_after).
3. Digitarq / Italian letter corpora only if EMLO follow-up stalls.
