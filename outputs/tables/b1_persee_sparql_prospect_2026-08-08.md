# Persée SPARQL prospect (2026-08-08)

Endpoint: `https://data.persee.fr/sparql` via local gateway (`scripts/_persee_sparql.py`).
Raw dumps: `data/raw/persee_sparql/`.

## What the graph is

Bibliographic Linked Data (Virtuoso), **not** fulltext OCR:

| class (approx) | n |
|---|---:|
| Manifestation | 2.4M |
| bibo:Document | 2.3M |
| Image | 1.5M |
| persee:Article | 413k |
| foaf:Person | 260k |

Person nodes ≈ modern **authors/authorities** (name, birth/death, owl:sameAs), linked to docs as `dcterms:creator` / `relators:aut`. No usable fulltext/content predicate found for lemma search.

## Roster name search (French soft/HOLD)

| query | Cleux-useful? |
|---|---|
| Denis Hesselin / Hasselin | **No** — modern Hesseling/Hasselin only |
| Cleux / Cleuz | **No** — Cleuziou noise |
| Cusac / Marzelière | **No** |
| Vincent Voiture / Charles d’Orléans / Philippe le Hardi / René d’Anjou / Nicolas de Baye | **No** as historical subjects |
| Marc-Adrien Dollfus | **Yes (already mined)** — séance summary on comptes/lunettes |
| Albert Lecoy de la Marche | Author authority present; Persée docs = CRAI notes, not *Extraits des comptes* edition |
| Alexandre Tuetey | Author authority; *Inventaire Charlotte de Savoie* = death inventory path |

## Title hits for lunettes / opticien

Known/secondary only: Dollfus 1969 BSNAF; Margolin 1975 *Annales* satire; Dreyfus 1989 invention+printing; archaeology Smyrne/antiques; geomorphology “lunettes” (eolian); modern advertising. **No new named living wearer with b–d.**

## Verdict

- SPARQL is a **catalog pointer** for secondary articles by known historians — not a Cleux ore vein.
- Do **not** use for roster-person densify or bericles/lunettes fulltext lottery.
- Residual use: `--person <modern historian>` → list their Persée docs, then open `/doc/` HTML if a title looks like dated comptes citation (Dollfus path already CLOSED).

**Action:** no promote / no panel change. Mark Persée SPARQL as metadata-only CLOSED for outward Cleux scouting.
