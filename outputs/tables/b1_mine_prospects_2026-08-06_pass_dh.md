# B1 mine prospects — Pass DH (2026-08-06)

Post–Pass DG (Wood tip **DONE** ya17→19 Δ−3→−1; Pepys DF tip **DONE**; dual SESOI5 **PASS_RAW** labor med **7.0** / output med **8.0**; merchant Italy **FAIL**; Adams/Washington soft done; Gray/Spinelli OA/HAB gated). Roster unchanged; **no measurement CSV edits; no promotes.**

Worst labor midnegs now: `leo_x` **−4.5** · `voiture_vincent` **−4.5** · `jacopo_magnia_friar` **−3** · `policastro` **−2.5** · `cederni` / `egidio_piacenza` **−2** · `wolsey` / `wood_anthony` **−1** · `spinelli_benedetto` **−0.47**.

---

## Ranked options (A–D)

| Rank | Option | Diggable now? | Verdict |
|------|--------|---------------|---------|
| **1** | **C — Confirm still gated / document digital idle** | **Yes** | **★ Pass DH pick** — Pepys/Wood tip ore spent; tip-lag A empty on named midnegs; locks physical-only queue |
| 2 | A — tip-lag repair (`policastro`/`cederni`/`wolsey`/`egidio`) | **No** | Chrono already wired; no Pepys/Wood-style lag (see audit) |
| 3 | A — `leo_x` / `voiture` / `jacopo` midneg | **No (illegitimate)** | Death-ceiling / SHORT_WINDOW / YA0; manufacturing excludes forbidden |
| 4 | B — NEW OA living wearer ≠ late-18c Anglo Founders | **No ore** | Soft plateau + Cleux bar; Founders soft→hard blocked |
| — | D — Spinelli archive dig packet | **DONE Pass DH** | Unblocks physical merchant-CI dig; tip≥1535 flips SESOI+5 CI |
| — | Physical Spinelli (merchant CI) | **Not now** | Highest *scientific* ROI — Yale/ASF only (Pass DE OA dry) |

---

## ★ Best next action — C (digital idle + gate confirm)

England Pepys-style tip hygiene is exhausted (DF Pepys + DG Wood). Pass DH A-audit of the next midneg cluster finds **zero** reverse-lifespan or stale-tip repairs. Remaining Δ moves require either manufacturing excludes or archive/borrow. Formalize digital idle so the next session does not re-dig Gray/Keil/OA midnegs.

### Evidence — still gated

| Gate | Status | Evidence paths |
|------|--------|----------------|
| **Todd Gray 1996** *Devon Household Accounts* Pt.2 | **STILL GATED** | `data/raw/external_mine_2026-08-03_early/pass_cz/meta_devonhouseholdac0000unse.json` → `collection` includes **`printdisabled`**; `outputs/cache/pass_bz/ia_gray.json` → `access-restricted-item=true`. Restitch `data/raw/external_mine_2026-08-03_early/pass_dd_gray_restitch/gray_restitch_hits.csv`: spectacle rows mostly **empty year** or volume-range **1627**; Mrs Herle hits = household-children noise (1645 Pikard), **not** Costume Historian p.159 spectacle line. Queue: `b1_library_hunt_queue.md` Gray **PAUSED**. |
| **Spinelli / Yale–ASF** | **STILL ARCHIVE-ONLY** | `b1_pass_de_spinelli_dry_azevedo_repair.md`: Robey OA day-date stops at Alessandro→Marradi **1534-08-24**; other originals + FROM-Benedetto **1535+** need Yale Beinecke / ASF MdP. Soft ya≈**0.03** → merchant Italy CI still **FAIL** (`b1_primary_estimand_summary.csv` merchant_treatments CI lo **−0.47**). |
| **HAB / NSAW Wiesel↔August** | **STILL GATED** | `outputs/cache/pass_bz/ia_wiesel_hab.json` → `access-restricted-item=true`. Keil *Augustanus Opticus* **HARD_TO_FIND** (`b1_library_hunt_queue.md`) — no Keil PDF chase. |

**No new OA stitch path** for Bourchier year-stamps, Mrs Herle soft, Spinelli multi-year ya, or August hard.

### Digital idle checklist (Pass DH)

1. Do **not** re-restitch Gray OCR fragments or re-PDF-mine Keil.
2. Do **not** BN-exclude leo/voiture/jacopo peers (Clement / Balzac+Tristan).
3. Do **not** tip policastro to death-year 1478 or cederni past Buonuomo 1478.
4. Physical queue order: **Yale Beinecke Spinelli + ASF MdP** → Gray borrow/merge → HAB/NSAW or Keil ILL.
5. After any future pin: `python3 scripts/31_b1_freeze_gate.py` (`b1_freeze_gate_report.md` currently **GATE PASS**).

---

## A — Tip-lag / legitimacy audit (named midnegs)

Criterion: reverse-lifespan/post-death densify **or** stale labor tip vs existing chrono (Pepys/Wood style) — **not** manufacturing excludes. Formula: `T = max(0, min(evidence_year + years_after_evidence, death) − (birth + 45))` (`scripts/25_b1_primary_estimand.py`).

### Tip-lag cluster (user-named)

| person_id | Δ | Census tip | Chrono / curated tip | Lag? | Verdict |
|-----------|---|------------|----------------------|------|---------|
| `policastro` | −2.5 | ya=**17** → calendar tip **1477** (`b1_roster_census.csv`) | Testament **1478-08-25** (+17.7d from wear 1460-12-12); death-in-office **1478-08-26** (`b1_policastro_activity_chrono.csv`; `b1_policastro_belloni_ingest_notes.md`) | **No** | Tip source already = testament; ya=17 is day-floor of +17.7. Raising ya→18 forces tip year **1478 = death year** / last-office=death — **FORBIDDEN**. Not Pepys lag. |
| `cederni` | −2 | ya=**24** → **1478** Buonuomo | Chrono last civic pin Buonuomo **1478-03-15**; burial **1482** (`b1_cederni_activity_chrono.csv`); output curated already drops burial (`data/curated/b1_wearer_output_years_curated.csv`) | **No** | Labor tip already at last office. Death 1482 ≠ tip. |
| `wolsey` | −1 | ya=**3** → **1530** | Soft SHORT_WINDOW gift **1527**→death **1530** (`b1_soft_stock_plateau_2026-08-05.csv`); output pins to fall **1529** | **No** | Already at death ceiling; soft structural. Further C pruning = manufacturing (Pass CB already rebalanced). |
| `egidio_piacenza` | −2 | ya=**0** | Single 1488–89 age-band order; no post-wear series (`b1_roster_census.csv`; soft plateau **YA0_single_pin**) | **No** | Needs ASF della Stufa archive — not diggable-now. |

### Already spent / illegitimate midnegs

| person_id | Δ | Why not A |
|-----------|---|-----------|
| `wood_anthony` | −1 | **DONE Pass DG** — Athenae continuation enquiry **1694-11-11**; death 1695 ≠ tip (`b1_pass_dg_wood_tip_gates.md`; chrono `b1_wood_anthony_activity_chrono.csv`) |
| `leo_x` | −4.5 | Labor at death ceiling 1521; T=1 structural (d.@46). Clement keep = deliberate Medici peer — do **not** manufacture drop |
| `voiture_vincent` | −4.5 | **SHORT_WINDOW_CLOSED**; Unwin/Voiture unlock closed set; do **not** strip Balzac/Tristan |
| `jacopo_magnia_friar` | −3 | YA0 single pin (same della Stufa memo as Egidio) |
| `spinelli_benedetto` | −0.47 | Soft ya≈0.03; OA dry Pass DE — archive only |

**A verdict for Pass DH:** no legitimate diggable-now midneg repair.

---

## B — NEW OA living wearer ≠ late-18c Anglo Founders

**Result: DRY** (reconfirm).

| Closed / crowded | Evidence |
|------------------|----------|
| Adams + Washington soft | Pass DC/DD done; no soft→hard without new spectacle reaffirm |
| Soft plateau | Hesselin OA-closed; Bourchier/Herle Gray-gated; René HOLD; Voiture SHORT_WINDOW; Spinelli ya≈0; YA0 friars (`b1_soft_stock_plateau_2026-08-05.csv`) |
| Prior mines | Pass CN/DE/DF/CG new-mine dry or false friends |
| Cleux bar skips | Cleux · Walmysford/Nuno · Digitarq Contos/Jaques · Jeffreys HARD · Huygens · Dudley HOLD · Pass BX René |

---

## D — Plumbing only if science unlock?

| Candidate | Status | Unblocks science? |
|-----------|--------|-------------------|
| Freeze gate | **PASS** (`b1_freeze_gate_report.md`) | No — already green |
| Wearer–control collision | **0 active** (`b1_wearer_control_collision_audit.md`) | No |
| Claim freeze package hygiene | Current (`b1_claim_freeze_package.md`) | No new pin |
| Merchant Italy CI | FAIL at Spinelli soft ya | Needs Yale/ASF, not CSV plumbing |

**No idle-only D.** Pass DH upgrades D → concrete Spinelli archive packet (`b1_spinelli_archive_dig_packet.md`): tip≥**1535** flips merchant SESOI+5 CI under n=4 bootstrap.

---

## Explicit global skips (this pass)

Cleux · Walmysford/Nuno · Digitarq Contos/Jaques · Jeffreys HARD · Huygens · René densify HOLD · Dudley HOLD · Unwin/Voiture unlock · Pass BX René · inventories `years_after=0` · Keil PDF chase · more Adams/Washington soft→hard without new spectacle reaffirm · leo Clement drop · voiture Balzac/Tristan strip · policastro tip→death-year 1478 · cederni burial 1482 tip · death/last-office termini · manufacturing BN midneg excludes.

---

## Recommended next work session

1. **Execute** `b1_spinelli_archive_dig_packet.md` (Yale box 131/2713 + ASF MdP 118/181; tip≥1535 flips merchant CI).
2. Gates closed digitally: Gray / HAB / Keil — do not re-restitch or PDF-mine.
3. Do **not** BN-exclude leo/voiture/jacopo; do **not** tip policastro to death-year 1478.
4. Dual SESOI5 already **PASS_RAW**; merchant Italy remains the open scientific gap.
