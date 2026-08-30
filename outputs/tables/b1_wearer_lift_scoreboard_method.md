# Wearer lift scoreboard (R1 portfolio)

**Date:** 2026-08-22  
**Script:** `38_b1_wearer_lift_scoreboard.py`

Whole-roster 0–100 scores so mid/low tiers stay visible. Strict-sharp
≥5 remains aspirational; soft and thin lifts are in-scope.

## Rubric

| Band | Criteria |
|------|----------|
| 95–100 | Broken/unfit-return + same-person dated stream |
| 85–94 | Broken/order with confound or network-not-hand stream |
| 70–84 | Soft episode coded (self-report / soft order / multi-order) |
| 55–69 | Hard post-wear series on roster, no R1 episode row |
| 40–54 | Soft stock / thin pins / hard=False with chrono |
| 20–39 | YA≈0 / inventory-only / single pin |
| 0–19 | Unmeasured / no local chrono |

**Rows:** 203 (full roster). **With episode:** 60.

## Band counts

| Band | n |
|------|--:|
| 95-100 | 2 |
| 85-94 | 2 |
| 70-84 | 54 |
| 55-69 | 0 |
| 40-54 | 11 |
| 20-39 | 121 |
| 0-19 | 13 |

## Wave 1 soft promotions (2026-08-22)

Eight mid-tier people with local chronos → `SOFT_ORDER` / `SOFT_SELF_REPORT`
episode rows (do **not** count toward ≥5 strict-sharp):
barbara_brandenburg, strozzi_filippo, lorenzo_medici, gonzaga_ludovico,
albrecht_prussia, policastro, maurolico_francesco, philippe_le_hardi.

## Wave 3 mid-tier lifts (2026-08-28)

Eight more 55–69 people with local chronos → `SOFT_ORDER` / `SOFT_SELF_REPORT`:
ammannati, rene_anjou, bianca_maria, azevedo_joao_porto,
ardingelli_bese, charles_orleans, nicolas_de_baye, tranchedini.

## Wave 4 mid-tier lifts (2026-08-28)

Sixteen more 55–69 people → `SOFT_*` via `b1_wave4_soft_episodes.csv`.

## Wave 5 (2026-08-28)

Nine more SOFT_* via `b1_wave5_soft_episodes.csv`; plus 0–19 CLOSED floors.

## Wave 17 (2026-08-30)

Six SOFT_* via `b1_wave17_soft_episodes.csv` (existing local chronos);
eight hard=False chronos from dated post-wear works/offices;
plus Chardin ingested with 1775–77 Heymann pins (lands ≥40).

## Wave 2 thin tier

See `b1_lift_thin_tier_2026-08-22.md` — documented CLOSED/PIN floors for YA0/soft-stock.

## Top 15 by score

| score | person_id | episode | verdict |
|------:|-----------|---------|---------|
| 97 | cederni | cederni_1454_return | ANALYZABLE_NOW |
| 97 | spataro_giovanni | spataro_1532_return | ANALYZABLE_NOW |
| 88 | datini | datini_1400_order | ANALYZABLE_NOW |
| 88 | knut_bosson | bosson_1415_broken | ANALYZABLE_NOW |
| 76 | adams_john | adams_1783_selfreport | SOFT_SELF_REPORT |
| 76 | albrecht_prussia | albrecht_1542_order | SOFT_ORDER |
| 76 | alessandra_strozzi | alessandra_1465_selfreport | ANALYZABLE_NOW |
| 76 | ammannati | ammannati_1473_order | SOFT_ORDER |
| 76 | ardingelli_bese | ardingelli_1451_purchase | SOFT_ORDER |
| 76 | august_brunswick_wolfenbuettel | august_1630_order | SOFT_ORDER |
| 76 | azevedo_joao_porto | azevedo_1476_order | SOFT_ORDER |
| 76 | barbara_brandenburg | barbara_1466_order | SOFT_ORDER |
| 76 | bianca_maria | bianca_maria_1462_use | SOFT_SELF_REPORT |
| 76 | blundell_nicholas | blundell_1722_selfreport | SOFT_SELF_REPORT |
| 76 | bourchier_henry_bath | bourchier_1646_purchase | SOFT_ORDER |
