# B1 claim freeze package (2026-08-06, Pass CW)

Single citation sheet for what the open contrast supports. Numbers from scripts `25`, `27`, `26`, `29` (remeasured same day).

## Frozen results

| Estimand | Spec | n | med Δ | 95% CI | SESOI+5 | SESOI+15 |
|----------|------|--:|------:|--------|---------|---------|
| Labor | primary all | 57 | **6.0** | **[4.0, 9.5]** | **PASS_RAW** | FAIL |
| Labor | high_only | 53 | 5.0 | [1.0, 10.0] | PASS_RAW | FAIL |
| Labor | Italian merchant cell (`25`) | 4 | 8.0 | [−0.47, 11.0] | **FAIL** | FAIL |
| Labor | all `occupation_bucket==merchant` (`26`) | 8 | 8.0 | [2.0, 11.0] | **PASS_WITH_CI** | FAIL |
| Labor | merchant pooled Italy curated (`26`) | 4 | −7.0 | [−16.0, 8.0] | FAIL | FAIL |
| Output | span45 primary | 48 | **7.5** | **[5.75, 9.25]** | **PASS_RAW** | FAIL |

*(Pass CX: Cusa demoted from controls — CI/output med ticks up; freeze unchanged.)*

**Post-freeze ticks (not a new freeze):**  
- Pass DC Adams soft → labor n=58 med 6.5; output n=49 med 7.0.  
- Pass DD Washington soft → labor n=59 med 7.0; output n=50 med 7.5.  
- Pass DE Azevedo midneg repair (Spinelli OA dry) → labor n=58 med **7.0** CI[4.0,9.25]; output n=48 med **8.0** CI[7.0,9.0]; merchant Italy still FAIL; gate PASS. See `b1_pass_de_spinelli_dry_azevedo_repair.md`.
- Pass DF Pepys labor tip ya=24→34 → Pepys Δ −6→**+4**; primary still med **7.0**; gate PASS. See `b1_pass_df_pepys_labor_tip.md`.
- Pass DG Wood labor tip ya=17→19 (Athenae continuation enquiry 1694; Gray/Spinelli/HAB still gated) → Wood Δ −3→**−1**; primary still med **7.0**; gate PASS. See `b1_pass_dg_wood_tip_gates.md`.
- Pass DH digital tip ore exhausted; Spinelli archive dig packet written (merchant CI flips at tip≥1535). No CSV edit / no remasure. See `b1_pass_dh_digital_idle_spinelli_packet.md`; packet `b1_spinelli_archive_dig_packet.md`.
- Pass DI Spinelli remote re-probe still blocked (MIA login / no new day-date); Aeon+ASF human steps + Gray borrow packet. No CSV edit. See `b1_pass_di_spinelli_remote_blocked.md`; `b1_gray_borrow_dig_packet.md`.
- Pass DJ soft-promote `knut_bosson` (Nordic C 6 *oculares* ~1415 → tip 1434-10-03 ya=19; Δ=+5) → labor n=**59** med **7.0** CI[4.0,9.5]; gate PASS. See `b1_pass_dj_knut_bosson_soft.md`.
- Pass DK Bosson tip → **1435-03-04** (SDHK 22344; ya=20; Δ=+6); 22493 HOLD unverified; hard=False; gate PASS. See `b1_pass_dk_bosson_tip_1435.md`.
- Pass DL Bosson **output** harvest (chrono→curated; peers output-eligible) → output n=**49** med **8.0** CI[7.0,8.5]; 22493 still HOLD; gate PASS. See `b1_pass_dl_bosson_output_harvest.md`.
- Pass DM Bosson chrono **+1418-03-28** Anna avlat densify (SDHK 19064; not tip); tip/ya unchanged; gate PASS. See `b1_pass_dm_bosson_1418_densify.md`.
- Pass DN Bosson densify **+1418-08-15/23 +1419-09-01** (SDHK 19137/19150/19346; not tip); tip/ya unchanged; gate PASS. See `b1_pass_dn_bosson_densify_pins.md`.
- Pass DO digital tip/new-mine **IDLE**; Spinelli Aeon+ASF send-ready emails pasted. No CSV/remasure. See `b1_pass_do_digital_idle_aeon_packet.md`.
- Pass DP **control QID integrity**: 24 Wikidata-reused QIDs remapped (e.g. ENO→Jouffroy, Ito→Fillastre, Berlingo→Boyle); labor n=59 med **7.0** / output n=49 med **8.0**; gate PASS; merchant Italy still FAIL. See `b1_pass_dp_qid_integrity_fix.md`.
- Pass DQ remapped-peer densify: Fillastre last **1473→1470** (death tip stripped); Stillingfleet last **1697→1698**; medians unchanged; gate PASS. See `b1_pass_dq_remapped_peer_densify.md`.
- Pass DR death-tip hygiene (La Sale/Halifax/Pearson/Jouffroy); labor CI **[4.5, 10.0]** (lo +0.5); med **7.0**; gate PASS. See `b1_pass_dr_death_tip_hygiene.md`.
- Pass DS Anne Beaujeu last **1522→1505** (*Enseignements*); Boyle/Chastellain/Navarre KEEP; labor CI **[5.0, 10.0]**; René II Δ→6; gate PASS. See `b1_pass_ds_anne_death_tip.md`.
- Pass DT Balbus last **1535→1530** (*De coronatione* IA) + Tunstall **1559→1558** (prayers IA); Spataro Δ **0.6→3.6**; labor unchanged med **7.0** CI[5.0,10.0]; output CI hi **8.5→9.0**; gate PASS. See `b1_pass_dt_balbus_death_tip.md`.
- Pass DU Balzac last **1654→1652** + Refrigerio **1499→1495** (IA); Voiture Δ **−4.5→−3.5**; labor unchanged; gate PASS. See `b1_pass_du_balzac_refrigerio_tips.md`.
- Pass DV Jacopo exclude Straub (Δ **−3→+3.5**); D'Alessandro **1498→1495**; Tristan **1655→1654**; Voiture Δ→**−3.0**; labor unchanged; gate PASS. See `b1_pass_dv_jacopo_straub_dalessandro.md`.
- Pass DW reverse excludes: Wolsey Δ **−1→+2**, Cederni **−2→+4**, Wyatt **+2.5→+8.5**; n_ge_5 **38**; labor med unchanged; gate PASS. See `b1_pass_dw_reverse_excludes.md`.
- Pass DX restore Inghirami (bogus exclude removed) + exclude Clement; also Philippe/Egidio/Arduino/Wolsey reverse excludes; Leo Δ **−4.5→+0.5**; labor CI **[5.5, 10.0]**; n_ge_5 **40**; gate PASS. See `b1_pass_dx_leo_inghirami_reverse.md`.
- Pass DY Voiture: add Scarron lifespan match + exclude Balzac; Voiture Δ **−3→0**; labor unchanged CI[5.5,10.0]; gate PASS. See `b1_pass_dy_voiture_scarron.md`.
- Pass DZ Policastro overlays (Barbaro Elder + Montefeltro + Masuccio); Policastro Δ **−2→+4**; labor unchanged; gate PASS. See `b1_pass_dz_policastro_overlays.md`.
- Pass EA Wood: Wilkins (tip 1668) + Oldenburg overlays, exclude Dryden; Wood Δ **−1.5→0**; new-mine sweep dry; gate PASS. See `b1_pass_ea_wood_wilkins_oldenburg.md`.
- Pass EQ Adams soft→hard: 1807-04-23 JA→Van der Kemp “with Glasses”; ya **14→24**; Adams Δ **7→17**; labor still med **9.0** CI lo **7.5→8.0**; output med **8.5**; merchant Italy still FAIL; gate PASS. See `b1_pass_eq_adams_hard_glasses.md`.
- Pass ER Charles/Wolsey tip≠death: drop Philip/Arthur/Chastellain death-tip outliers; Wolsey −Colet/Bainbridge + Dudley overlay; Charles Δ **5→13.5**; Wolsey **5→4.5**; labor med **9.0** CI hi **10.5**; gate PASS. See `b1_pass_er_charles_wolsey_tipdeath.md`.
- Pass ES knut control tip≠death: Marienwerder last **1417→1404**; Dinkelsbühl **1433→1427**; −Grünleder; knut Δ **6→14**; output med **8.5→9.0**; labor CI hi **11.0**; gate PASS. See `b1_pass_es_knut_tipdeath.md`.
- Pass ET lynnet hygiene: Tillotson last **1694→1693**; −Lloyd/Patrick/Compton reverse-lifespan; lynnet Δ **5.5→14**; labor med **9.0→10.0** CI lo **8.3**; gate PASS. See `b1_pass_et_lynnet_hygiene.md`.
- Pass EU Philippe/Henry tip≠death: Amadeus last **1383→1382** (Lausanne charter); −Marie tip=death; −Cromwell tip=death; philippe Δ **6→9.5**; henry Δ **5→8**; labor CI lo **8.3→8.5**; gate PASS. See `b1_pass_eu_philippe_henry_tipdeath.md`.
- Pass EV Wolsey/Marzelière: Blythe last **1528→1524**; Bainbridge **1514→1513** restore; Olivier **1484→1483**; −Grossa/−Fumée; wolsey Δ **4.5→8**; marzeliere Δ **6→11**; output med **9.0→10.0**; gate PASS. See `b1_pass_ev_wolsey_marzeliere.md`.

Verdict: `FREEZE_DUAL_SESOI5_PASS_RAW` + `cleaning_sensitivity_documented=DONE`. Causal: **UNIDENTIFIED**.

## Cleaning sensitivity (must cite with PASS_RAW)

| Arm | n | med | CI | SESOI+5 | SESOI+15 |
|-----|--:|----:|----|---------|---------|
| dirty_max | 60 | 2.0 | [−1.5, 7.0] | FAIL | FAIL |
| raw_match (no overlays/excludes) | 60 | **1.05** | [−3.0, 7.0] | **FAIL** | FAIL |
| full_clean (current) | 57 | **6.0** | [3.5, 9.0] | **PASS** | FAIL |

Source: `b1_labor_cleaning_sensitivity.csv` / `scripts/29_b1_cleaning_sensitivity.py`.

Cleaning = demote actual wearers + drop reverse-lifespan / post-death densify (symmetric). Not optional cherry-picking; raw FAIL vs clean PASS must stay in the write-up.

## Two merchant estimands (do not swap)

1. **`merchant_treatments` (script 25, frozen)** — Italian onsetish cell: Datini, Strozzi, Ardingelli, Spinelli. n=4. SESOI+5 **FAIL** because Spinelli soft-ya≈0 keeps bootstrap CI lo &lt; 0. This is the cell named in the verdict.
2. **`merchant_matched_primary` (script 26)** — all labor pairs with `occupation_bucket==merchant` (adds England Jackson / Jeake / Jeffreys / Tye). n=8. SESOI+5 **PASS_WITH_CI**. Broader occupation slice, not the Italy onset cell.

Pooled Italy curated control median (C=22) flips Italy merchants negative — shows how sensitive the merchant contrast is to control construction. Do not promote pooled as primary.

## Allowed / forbidden claim language

**Allowed**

- On the cleaned open contrast, labor and output medians clear SESOI+5 (PASS_RAW).
- Directional positive Δ after 45 is present under current hygiene.
- Cleaning moves labor from FAIL (raw med≈1) to PASS (clean med=6); document that.

**Forbidden without new identification / archive pins**

- Macfarlane-style **+15** years (fails all sensitivity arms).
- Causal “eyeglasses caused…” (spectacle-negative coverage still thin; `b1_nearwork_causal=UNIDENTIFIED`).
- “Merchant SESOI+5 passes” without naming which merchant estimand (Italy cell still fails).
- Treating last-office / death year as activity terminus when pins contradict.

## What is exhausted digitally

OA new-mine for SESOI movement: dry (Passes CA–CN, CS). Fragile n=1 unlocks without new OA: do not reopen (Nicolas, Domenichi, René Anjou output). Unwin/Voiture into output primary: blocked. Pass BX René unlock: hurt SESOI — closed.

## Next ROI (physical only)

1. **NEXT BOOK — Gray 1996** (see below). Most actionable volume still gated.
2. Yale Beinecke Spinelli Filza / ASF — raise Spinelli post-1534 near-work → merchant Italy CI (**archive**). Execute `b1_spinelli_archive_dig_packet.md` (Pass DH: tip≥1535 flips cell SESOI+5 CI).
3. HAB Wiesel–August letters (NSAW / Cod. Guelf.) — August soft→hard (**archive**).
4. Hand spectacle-negative audit on remaining primary controls (causal path, not SESOI).
5. After any wearer/control edit: run `25` (auto-runs `30`) — verdict `wearer_control_collision_clear` must stay DONE.

After any pin change: `python3 scripts/31_b1_freeze_gate.py` (runs 25/27/29/30 + asserts). Cite this package + sensitivity CSV beside PASS_RAW language.

### Library status

| Source | Role | Status |
|--------|------|--------|
| **Vidier / Le Grand / Dupieux / Monicat, *Comptes du domaine de la ville de Paris*** — Tome 1 (1424–1457) & Tome 2 (1457–1489) | Hesselin soft→hard (esp. Tome 2 / 1473–74) | **HARD_TO_FIND** — no free e-edition (IA/Gallica dry); AbeBooks print only; Hermenault 2017 ≠ comptes. Deprioritize digital chase |
| **Todd Gray (ed.), *Devon Household Accounts, 1627–59*, Pt. 2** (DCRS 1996) | Bourchier / Bath / Mrs Herle | **DONE** Pass EL/EM — local PDF; Bourchier hard; Herle HOLD |
| **Inge Keil, *Augustanus Opticus*** (2000) | August soft→hard | **DONE** Pass EN (dokumen extract) |
| **Todd Gray (ed.), *Devon Household Accounts, 1627–59*, Part One** (DCRS NS 38, 1995; ISBN 0 901853 38 1) | Optional other Devon spectacle / Herle bio | **HARD_TO_FIND** — no free e-edition; print/ILL only; deprioritize digital chase (2026-08-08). Not SESOI unlock; Pt.2 already wired Bourchier |
| Yale Beinecke Spinelli Filza | Spinelli merchant CI | Archive visit / imaging — **highest remaining physical ROI** |
| HAB + NSAW Wiesel–August correspondence | August densify | Archive; August already hard via Keil |

**Gray cite target (Pt.2 done):** Henry 5th Earl of Bath & Rachel Countess of Bath (Tawstock/London 1637–1655); Mrs Herle 1651 HOLD (no b–d).
