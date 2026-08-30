# Pass DP — control QID integrity fix (2026-08-06)

## Judgment

User: archive **emails low ROI**. Re-triaged away from Spinelli Aeon.

Digital new-mine / vocab re-pick / HOLD unlocks (Belluga, Vitko, Vangelista, Ståhl, Spataro tip, 5th Italian merchant) all **dry**. Midneg tip-lag still empty.

While auditing unreviwed controls, found **Wikidata QID reuse**: curated overlay/chrono QIDs now point at opera companies, athletes, novels, ships, communes — not the intended historical peers. Highest diggable science = **fix identity integrity**, not another OA person hunt.

## Scout (dry, logged)

| Track | Result |
|-------|--------|
| Czech/HU/Ottoman/Croatian/Greek vocab mines | OA/IA noise; 0 Cleux-bar living |
| Belluga apotecari birth | Still ≠ jurist Q6072225; MedCat SPA |
| Vangelista / Farulli termini | IA 0; Alvin/DiVA dry |
| Spataro post-1533 | Corpus closed; San Petronio PDF 403 |
| 5th Italian merchant wearer | Ilardi trade-stock / literary only |

## Integrity audit

Batch `wbgetentities` on **292** primary-use control QIDs → **24** hard mismatches (P31≠human and/or birth/name clash). False-friend name variants kept (Tomeo/Thomaeus; Bonet/Bovet).

Remap file: `data/raw/external_mine_2026-08-03_early/pass_dp/qid_remap.json` (24 pairs).

Examples:

| Old QID (now) | Intended person | New QID |
|---------------|-----------------|---------|
| Q1342882 English National Opera | Jean Jouffroy | Q592641 |
| Q3123685 Sachiko Ito | Guillaume Fillastre | Q1388943 |
| Q103514 Berlingo | Robert Boyle | Q43393 |
| Q180353 Chingaari (film) | Robert Hooke | Q46830 |
| Q561567 “244” dab | Georges Chastellain | Q957427 |
| Q333922 (drift) | John Pearson (bishop) | Q676560 |

Touched curated + match tables (backups `*.bak_qidfix_*` / `*.bak_qidfix2_*`).

## Remeasure (`B1_SPARQL=0` freeze gate)

| Estimand | n | med Δ | CI | SESOI+5 |
|----------|--:|------:|----|---------|
| Labor primary | **59** | **7.0** | **[4.0, 9.5]** | **PASS_RAW** |
| Labor high_only | 53 | **7.5** | [4.5, 10.0] | PASS_RAW |
| Output span45 | **49** | **8.0** | **[7.0, 8.5]** | **PASS_RAW** |
| Merchant Italy | 4 | 8.0 | [−0.47, 11.0] | **FAIL** |

`GATE PASS`. Collision active=0. Medians unchanged vs DN (as expected — bad QIDs often lacked usable chrono years; identity now correct for future densify).

## Next ROI (email still deprioritized)

1. Optional: densify remapped peers’ near-work pins under **correct** QIDs (Boyle/Hooke/Chastellain etc.) if chrono was thin placeholder.  
2. New-mine OA: still plateau — only lottery vocab seams or physical Gray.  
3. Merchant Italy CI: still needs tip≥1535 pin (not email-churn).  
4. Do **not** re-probe Belluga/Vitko/22493 Europeana as primary.
