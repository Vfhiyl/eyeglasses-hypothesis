# B1 mine prospects — Pass DF (2026-08-06)

Post–Pass DE (dual SESOI5 PASS_RAW; labor med 7.0 / output med 8.0; Italian merchant FAIL; Adams+Washington soft done; Gray paused; Keil HARD_TO_FIND; Azevedo Δ fixed to +1). Roster collision vs `b1_named_wearers_candidates_new.csv` + `ilardi_named_wearers.csv` + `b1_roster_census.csv` (**104** unique `person_id`). **No measurement CSV edits; no promotes.**

Worst labor midnegs (primary pairs): `pepys_samuel` −6 · `leo_x` −4.5 · `voiture_vincent` −4.5 · `jacopo_magnia_friar` −3 · `wood_anthony` −3.

---

## Ranked options (A–D)

| Rank | Option | Diggable now? | Verdict |
|------|--------|---------------|---------|
| **1** | **D — Pepys labor tip-up** (wire Pass BG chrono into census `years_after`) | **Yes** | **Best next dig** — flips worst midneg without BN manufacturing |
| 2 | C — Gray gate / OA stitch | Confirm only | **Still gated** (IA printdisabled; restitch undated; no new stitch path) |
| 3 | B — NEW OA living wearer ≠ late-18c Anglo Founders | No ore | Soft plateau + Pass DE/CN dry; inventories/sellers excluded |
| 4 | A — BN-style Pepys midneg exclude | **No (illegitimate)** | Reverse-lifespan already cleaned; remaining C age-matched |

---

## ★ Best next dig — D (Pepys labor years_after tip-up)

**Not** a control exclude. Labor `T` still ends at Memoires **1690** while output already hardened to documentary **1700**.

### Evidence of the lag

| Layer | Last near-work pin | Source |
|-------|-------------------|--------|
| Census / labor | `years_after_evidence=24` → tip **1690** | `b1_roster_census.csv` note: “to Memoires 1690” |
| Chrono (already curated) | Christ's Hospital letters **1698-07-11**, **1699-03-07**; library catalogue Michaelmas **1700** | `b1_pepys_samuel_activity_chrono.csv` |
| Output | same 1698/1699/1700 pins; death 1703 dropped | Pass BG; `b1_wearer_output_years_curated.csv` |

Labor formula (`scripts/25_b1_primary_estimand.py`):

`T = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))`

| Census tip | last | T (b=1633) | vs C med 18 | Δ |
|------------|------|------------|-------------|---|
| Current ya=24 | 1690 | **12** | 18 | **−6** |
| Tip to 1698 letter | 1698 | 20 | 18 | +2 |
| Tip to 1699 letter | 1699 | 21 | 18 | +3 |
| Tip to catalogue 1700 | 1700 | **22** | 18 | **+4** |

### Dig checklist (next work session — do not invent dates)

1. Raise `pepys_samuel` census / activity-proxy `years_after_evidence` from **24 → 34** (1666 → 1700), citing existing chrono rows (Wing/RMG/OTA + Magdalene catalogue).
2. Keep death **1703 ≠** labor terminus (Pass BG already dropped death tip on output).
3. Re-run primary estimand only after census tip; expect Pepys Δ −6 → ~+4; do not touch control excludes for this cell.
4. Optional parallel: same hygiene glance at `wood_anthony` (−3) — shared England cluster, but Wood tip already tracks chrono; not the same lag.

### Why this beats A–C

- Diggable **without** Yale/HAB/Gray borrow.
- Uses pins already accepted for output SESOI.
- Directly repairs the **worst** labor midneg with wearer densify, not control pruning.

---

## A — BN-style Pepys reverse-lifespan repair — REJECT

Pass CP already dropped Wren / Ray / Sprat (`b1_output_control_excludes.csv`: d.@78–91 vs Pepys d.@70 T=12).

**Remaining primary controls** (from `b1_primary_estimand_pairs.csv`):

| Control | d@ | span45 | ya45 (last−b−45) | vs Pepys d.@70 |
|---------|----|--------|------------------|----------------|
| Savile | 62 | 17 | 17 | −8 |
| Bunyan | 60 | 15 | 15 | −10 |
| Boyle | 64 | 19 | 19 | −6 |
| Stillingfleet | 64 | 19 | 17 | −6 |
| Sydenham | 65 | 20 | 17 | −5 |
| Hooke | 68 | 23 | 20 | −2 |
| Dryden | 69 | 24 | 24 | −1 |
| Temple | 71 | 26 | 22 | **+1** |

- **Zero** controls with d@ > Pepys+3; only Temple +1 year.
- Median C ya45 = **18** matches primary `med_c_primary`.
- Midneg = **Pepys short T (census tip 1690)**, not reverse-lifespan / post-death densify inflation in C.
- Further BN excludes would manufacture Δ (contradicts Pass CU cleaning-sensitivity honesty bar).

**Verdict:** A is **not** a legitimate BN repair. Prefer D tip-up.

---

## B — NEW OA living wearer (15–17c Italy/France/HRE/England; not inventory/seller)

**Result: DRY for diggable-now ore** (this pass = roster + soft-stock audit; no new Cleux-bar pin cleared).

| Closed / crowded | Why |
|------------------|-----|
| Adams + Washington soft | Late-18c Anglo Founders — do not add more without new spectacle reaffirm |
| Soft plateau (`b1_soft_stock_plateau_2026-08-05.csv`) | Hesselin OA-closed; Bourchier/Herle Gray-gated; René HOLD; Voiture SHORT_WINDOW; Spinelli ya≈0 archive; YA0 friars |
| Pass CN / DE mines | Gallica/DDB dry; Italian merchant false friends only |
| Explicit skips | Cleux · Walmysford/Nuno · Digitarq Contos/Jaques · Jeffreys HARD · Huygens · Unwin/Voiture unlock · inventories `ya=0` · sellers |

Other midnegs **not** fixable by new-mine this pass:
- `leo_x` −4.5: structural short ya45 (d.@46 T=1); reverse-lifespan peers already stripped (Pass CO).
- `voiture_vincent` −4.5: SHORT_WINDOW_CLOSED; Unwin/Voiture unlock forbidden.
- `jacopo_magnia_friar` −3: `years_after=0` single pin; no OA densify path without archive.

---

## C — Confirm Gray still gated / any new OA stitch path

| Check | Status | Evidence |
|-------|--------|----------|
| IA `devonhouseholdac0000unse` | **STILL GATED** | `meta_gray.json`: `access-restricted-item=true`, `printdisabled` |
| Pass DD restitch | **No year-stamped spectacle body** | `pass_dd_gray_restitch/gray_restitch_hits.csv`: spectacle rows year field empty or volume-range **1627** only; undated “for my Lord” lines |
| Mrs Herle p.159 | **Body absent** | Index/Costume Historian 1651 pin stands; restitch Herle hits = household-children noise, not spectacle line |
| Local djvu cache | Useless | `gray_devon_bath_djvu.txt` = 7 lines |
| Library queue | Unchanged | `b1_library_hunt_queue.md`: Gray **PAUSED**; Keil ILL-only |

**No new OA stitch path.** Merge/borrow still required before Bourchier year-stamp or Herle soft.

---

## Explicit global skips (this pass)

Cleux · Walmysford/Nuno · Digitarq Contos/Jaques · Jeffreys HARD · Huygens · René densify HOLD · Dudley HOLD · Unwin/Voiture unlock · Pass BX René · inventories `years_after=0` · Keil PDF chase · more Adams/Washington soft→hard without new spectacle reaffirm · Spinelli Yale/ASF visit (unavailable) · Pepys BN further excludes · death/last-office termini.

---

## Recommended next work session

1. **Dig D:** ~~Tip `pepys_samuel` labor `years_after_evidence` 24 → **34**~~ **DONE Pass DF** — Δ −6→+4; see `b1_pass_df_pepys_labor_tip.md`.
2. Archive Spinelli / Gray merge / HAB when available.
2. When Gray merge/borrow lands → Bourchier dates + Mrs Herle soft (C).
3. Merchant Italy CI still needs **Yale/ASF Spinelli** (not diggable this session).
4. Do **not** promote anyone from this note; do **not** BN-exclude Pepys peers.
