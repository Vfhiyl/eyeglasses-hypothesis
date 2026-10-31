#!/usr/bin/env python3
"""B1 route R1: registry of within-person spectacle episodes (2026-08-12).

An "episode" is a sharply dated spectacle event (order / broken / returned /
documented failure) around which the same person's dated work stream can be
compared — the person is their own control. This registry codes every
candidate found in the current corpus, what local material supports it, and
a first-pass read where a dated series exists locally.

Feasibility verdicts:
  ANALYZABLE_NOW   — anchor + dated series both local
  SOFT_ORDER / SOFT_SELF_REPORT / SOFT_MULTI_ORDER — coded soft R1
                     (portfolio lifts; do not fully count toward ≥5 sharp)
  ANCHOR_ONLY      — anchor documented; series needs external mining
  NEGATIVE_CASE    — documented correction failure (essential to keep)
  NEEDS_MINING     — anchor known from literature; sources not local

Upgrade condition (DATA_ROADMAP): >=5 sharp episodes with series before the
B1 direction verdict may be reopened. Soft order/self-report rows raise the
portfolio mid-tier but are not sharp-bar increments.

Outputs:
  outputs/tables/b1_episode_registry.csv
  outputs/tables/b1_episode_registry_method.md
  outputs/tables/b1_datini_order_episode_monthly.csv (first-pass read)
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES

DATINI_MONTHLY = OUTPUT_TABLES / "datini_bologna_busta721_monthly.csv"
OUT_CSV = OUTPUT_TABLES / "b1_episode_registry.csv"
OUT_MD = OUTPUT_TABLES / "b1_episode_registry_method.md"
OUT_DATINI = OUTPUT_TABLES / "b1_datini_order_episode_monthly.csv"
WAVE4_CSV = OUTPUT_TABLES / "b1_wave4_soft_episodes.csv"
WAVE5_CSV = OUTPUT_TABLES / "b1_wave5_soft_episodes.csv"
WAVE6_CSV = OUTPUT_TABLES / "b1_wave6_soft_episodes.csv"
REG_FIELDS = (
    "episode_id",
    "person",
    "anchor",
    "type",
    "work_stream",
    "local_material",
    "verdict",
    "first_pass",
    "limitations",
)

EPISODES = [
    {
        "episode_id": "datini_1400_order",
        "person": "Francesco Datini (b.1335, d.1410; age 65 at episode)",
        "anchor": "1400-Q3 spectacle order letters (Piaciti/Gaddi, ASPO F.721/713; images local)",
        "type": "order",
        "work_stream": "letters to Datini Bologna branch (buste 718–721 pooled monthly)",
        "local_material": "data/raw/datini_prato (order images + search dumps); "
        "outputs/tables/datini_bologna_busta721_monthly.csv; "
        "buste 718–720 catalogs + datini_bologna_buste718_721_monthly.csv "
        "(ASPO harvest 2026-08-22); b1_datini_order_episode_monthly_with_pre.csv",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "721-only: order Q ~14/mo, post ~16/mo. Pooled 718–721: "
        "pre 1400-01..06 n=7 (~1.2/mo); order Q n=187 (~62/mo); post ~57/mo — "
        "baseline exists but thin; July surge = traffic/filing not ochiali DiD",
        "limitations": "counts are letters TO Bologna branch (network, not Datini "
        "hand); curated pre-order Bologna-dest n=10 too thin for strict DiD "
        "(see datini_bologna_pre140007_curated.csv); ASPO dig 2026-08-22 hit "
        "ceiling — use Firenze 713 only as supplier parallel",
    },
    {
        "episode_id": "alessandra_1465_selfreport",
        "person": "Alessandra Strozzi (b.1406, d.1471; age 59)",
        "anchor": "1465 self-report of spectacle use in letter",
        "type": "self_report (soft anchor — use, not deprivation)",
        "work_stream": "complete Guasti 1877 letter corpus (67 dated letters)",
        "local_material": "outputs/tables/b1_alessandra_letter_chrono.csv",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "letter rate 2.5/yr (1455-64) -> 4.0/yr (1465-71); "
        "series continues to death (b1_within_person_rates.csv)",
        "limitations": "soft anchor (no deprivation window); editorial "
        "survival bias; rate is letters, not hours",
    },
    {
        "episode_id": "spataro_1532_return",
        "person": "Giovanni Spataro (b.1458, d.1541; age 74)",
        "anchor": "1532-03-13 ochiali request letter; 1532-04-05 returns Venetian "
        "spectacles as unfit ('non sono boni per me') — BAV Vat.lat.5318, images local",
        "type": "order + documented_failure_of_one_pair",
        "work_stream": "Spataro→Aaron/Del Lago dated letters (Blackburn 1991 Order "
        "of Letters + local Vat.lat.5318/CMBM chrono)",
        "local_material": "data/raw/spataro_giovanni; outputs/tables/"
        "b1_spataro_giovanni_chrono.csv; outputs/tables/"
        "b1_spataro_letter_rates_from_toc.csv (2026-08-21)",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "FROM-him letters/yr (ToC+local): 1529=12, 1531=7, 1532=10 "
        "(incl. request+unfit return), 1533=10; series ends 1533-10-30. Continuity "
        "through bad-pair window — not a work-stoppage trough",
        "limitations": "rates from published letter calendar + local folio verify, "
        "not full-text word counts; unfit return ≠ clean deprivation; corpus tip "
        "closed at 1533-10-30 (Blackburn)",
    },
    {
        "episode_id": "lotto_1544_55_orders",
        "person": "Lorenzo Lotto (b.1480, d.1556; ages ~64–72 at purchases)",
        "anchor": "multiple dated ochiali purchases in Libro di spese diverse "
        "(De Carolis EUT 2017): 1544 distance pairs + case; unmarked pair; "
        "1552 Loreto three pairs; 1552 May three pairs w/ knives",
        "type": "soft_multi_order (purchases, not broken/return)",
        "work_stream": "continuous PER L'ARTE / household expense stream in same "
        "account book (1540–1556)",
        "local_material": "data/raw/lotto_libro/Lorenzo_Lotto_openstarts.pdf "
        "(= Downloads/Lorenzo_Lotto.pdf SHA-identical); ochiali_pages/ PNGs; "
        "outputs/tables/b1_lotto_ochiali_pins.csv",
        "verdict": "SOFT_MULTI_ORDER",
        "first_pass": "1544: cassa repair + doi para da veder luntano (DISTANCE — "
        "separate class); later unmarked pair and 1552 multi-pair Loreto/Ancona "
        "orders while art expenses continue",
        "limitations": "purchase≠wear onset; distance pairs wrong for near-work "
        "B1; no single sharp deprivation window; artisan not scholar labor",
    },
    {
        "episode_id": "bosson_1415_broken",
        "person": "Knut Bosson, Bishop of Linkoping (b.1360, d.1436; age 55)",
        "anchor": "1415 letter about broken spectacles, requesting replacement "
        "(Hildebrand C6 / Basel letter)",
        "type": "broken (sharpest deprivation anchor in the roster)",
        "work_stream": "episcopal charters — SDHK open dataset (44,264 regests; "
        "CC BY 4.0), data/raw/sdhk/sdhk_2411.csv downloaded 2026-08-12",
        "local_material": "full SDHK register local; scripts/37 → "
        "b1_bosson_sdhk_yearly.csv",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "pre-episode 1405-14: 5.8 charters/yr; 1415: trough (2); "
        "1416-25: 2.8/yr; last decade 1426-36 (ages 66-76): 4.9/yr to death. "
        "Late-life continuation clear; the 1415-18 dip is confounded by his "
        "attendance at the Council of Constance (absence abroad), so the "
        "deprivation read is blocked at annual resolution",
        "limitations": "regest-level chancery documentation, not autograph "
        "near-work; Constance confound 1414-18 remains — monthly SDHK "
        "(b1_bosson_sdhk_monthly_1413_1420.csv) shows issuer activity in "
        "1414-H1 then near-zero dated issuer pins in 1415 (abroad), so "
        "sub-annual still cannot separate broken-glasses from absence",
    },
    {
        "episode_id": "cederni_1454_return",
        "person": "Bartolomeo Cederni (b.~1416, d.1482; age ~38 at episode)",
        "anchor": "1454-06-20 personal 6-pair order; 1454-07-05 return of 3 unfit "
        "pairs; 1454-07-12 replacements OK (Caccini letters via Ilardi 2007)",
        "type": "order + documented_unfit_return",
        "work_stream": "embassy-to-Venice paperwork context May–Jul 1454; "
        "later civic offices (Prior 1473, Buonuomo 1478)",
        "local_material": "outputs/tables/b1_cederni_activity_chrono.csv; "
        "b1_cederni_1454_episode_method.md; Ilardi 2007 OCR quotes",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "dated unfit-return arc in <3 weeks while on Venice "
        "embassy; post-wear civic densify to 1478 (+24y). Sharp optical "
        "failure class (with Spataro); FROM-him letter rates unavailable",
        "limitations": "surviving narrative mostly Caccini→Cederni (Corti–Kent "
        "copyright); Cederni outgoing letters mostly lost — no Spataro-grade "
        "FROM-him rate series through the window",
    },
    {
        "episode_id": "arduino_1451_broken",
        "person": "Arduino da Baiso (b.~1385, d.1454; age ~66 at episode)",
        "anchor": "1451-08-25 to Piero de' Medici: one pair broken lenses; others "
        "distance-only; requests thick near pairs (ASF MAP XIV.29; Ilardi)",
        "type": "broken + wrong_prescription_complaint",
        "work_stream": "woodcarver workshop (OA series lacking)",
        "local_material": "Ilardi 2007 OCR; ilardi_named_wearers arduino_baiso; "
        "death ceiling +3y",
        "verdict": "ANCHOR_ONLY",
        "first_pass": "sharp broken/wrong-lens complaint documented; dies 1454 "
        "(+3y) with no OA dated workshop stream",
        "limitations": "HARD OA-CLOSED for post-anchor near-work series; do not "
        "count toward ≥5 sharp bar without new primary workshop dates",
    },
    {
        "episode_id": "filelfo_1456_vitreis",
        "person": "Francesco Filelfo (b.1398, d.1481; age ~58 at episode)",
        "anchor": "1456-05-31 Milan to Donato Acciaioli: remind Bartolomeo Scala "
        "'mihi iam opus esse vitreis oculis' (IA A336151 pp.240-241; multimodal)",
        "type": "order_request / self_need (soft-sharp — not broken/return)",
        "work_stream": "dated FROM-him letters in same early-print Epistolae",
        "local_material": "data/raw/filelfo_epistolae/A336151.pdf; "
        "FILELFO_1456_VITREIS_OCULIS.md; hunt pages; "
        "outputs/tables/b1_filelfo_1456_curated_pins.csv; "
        "b1_filelfo_1456_episode_rates.csv (2026-08-22)",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "1456 curated n=19 letters (15 unique dates); May–Jun "
        "cluster n=9 around 05-31 anchor; pre 1454–55 auto ~39 closings; "
        "post 1457–58 auto ~7 — continuity, not stoppage",
        "limitations": "self-need request ≠ deprivation/unfit return; early-print "
        "survival/selection; auto year counts OCR-noisy (iunias/ianias); rates "
        "are letter closings not hours of near-work",
    },
    {
        "episode_id": "pirckheimer_1520s_orders",
        "person": "Willibald Pirckheimer (b.1470, d.1530)",
        "anchor": "spectacles among study effects (evidence 1520); order letters "
        "reported in later Briefwechsel volumes (Ilardi)",
        "type": "order (anchor date needs pinning)",
        "work_stream": "Briefwechsel dated letters; Allen Erasmus correspondence",
        "local_material": "data/raw/pirckheimer bd1+bd2 full text (to ~1505 only; "
        "spectacle terms absent there — checked 2026-08-12); bd7 ToC; "
        "beck-shop bd7 Inhaltsverzeichnis; bd5 GB preview (Inhalt only) 2026-08-22",
        "verdict": "NEEDS_MINING",
        "first_pass": "bd7 ToC parse (2026-08-12): 58 dated letters in 1528, 66 "
        "in 1529 — very dense correspondence 8-9 years post-evidence, to within "
        "two years of death; post-wear continuation established at volume level",
        "limitations": "HARD_TO_FIND: Willibald Pirckheimers Briefwechsel "
        "(Beck/Reicke–Scheible) bd4–6 needed for order pin are print-only / "
        "copyright; no OA fulltext (IA 0; Heidelberg early vols only; Beck shop "
        "no public Inhalt PDF for bd4–5; GB Bd.5 preview = front matter only, "
        "0 Brille; Persée = footnote citations only). Library/Ilardi quote "
        "still required — do not expect remote dig to unlock",
    },
    {
        "episode_id": "barbara_1466_order",
        "person": "Barbara of Brandenburg, Marchesa of Mantua (b.1422, d.1481; age ~44)",
        "anchor": "1466-09-18 to Federico: order ochiali assai (Ilardi / ASMA)",
        "type": "order",
        "work_stream": "OA FROM-her letter chrono post-order (Nicoud/Hofmann harvest)",
        "local_material": "outputs/tables/b1_barbara_oa_letter_chrono.csv; "
        "b1_barbara_fromher_letter_rates.csv; b1_barbara_1466_episode_method.md",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "FROM-her OA letters: episode 1466 n=1; post n=8 through 1479 "
        "(excludes 1472 envoy). Continuity after the order (ya≈13).",
        "limitations": "order≠deprivation; letter sample is OA subset not complete "
        "chancery; Fantoni regesti still blocked",
    },
    {
        "episode_id": "strozzi_filippo_1464_order",
        "person": "Filippo Strozzi the Elder (b.1428, d.1491; age ~36 at onsetish)",
        "anchor": "1464 (Florentine style 1463) ochiali via mother Alessandra; "
        "later personal-use / gift pairs (Ilardi)",
        "type": "soft_order (via mother then personal practice)",
        "work_stream": "Sepoltuario / bank-career civic densify pins",
        "local_material": "outputs/tables/b1_strozzi_filippo_sepoltuario_chrono.csv; "
        "b1_strozzi_filippo_1464_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=13 birth→1491; post-wear civic/career pins to +25y. "
        "Rates N/A (not a letter-rate corpus)",
        "limitations": "onset via mother order (personal use inferred); stream is "
        "civic/bank activity proxy not autograph near-work hours",
    },
    {
        "episode_id": "lorenzo_medici_1479_selfreport",
        "person": "Lorenzo de' Medici (b.1449, d.1492; age ~30 at self-report)",
        "anchor": "1479 self-report of spectacle use (Ilardi n.94 / Lettere)",
        "type": "soft_self_report",
        "work_stream": "OA Ross 1910 letter sample (strict dated FROM-him)",
        "local_material": "outputs/tables/b1_lorenzo_medici_ross_letter_chrono.csv; "
        "b1_lorenzo_medici_1479_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "Ross chrono n=8 letters 1479-09-11 → 1490-07-28 (+11y). "
        "Continuity pins; modern Lettere edition copyright",
        "limitations": "OA proxy sample not full epistolario; self-report≠order/"
        "deprivation; young age at evidence vs classic presbyopia onset",
    },
    {
        "episode_id": "gonzaga_ludovico_1460_selfreport",
        "person": "Ludovico Gonzaga (b.1412, d.1478; age ~48)",
        "anchor": "1460-02-13 to Lochner: reads letters daily with spectacles; "
        "asks more pairs (Ilardi / Signorini)",
        "type": "soft_self_report (+ ongoing order practice)",
        "work_stream": "spectacle/reading letter pins (Ilardi quotes)",
        "local_material": "outputs/tables/b1_gonzaga_ludovico_spectacle_reading_chrono.csv; "
        "b1_gonzaga_ludovico_1460_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "chrono n=4 pins 1460-02-13 → 1473-03-07 still wearing "
        "(+13y). Continuity pins only; rates N/A",
        "limitations": "thin pin count; chancery/diplomatic full series not local; "
        "self-report with reorder habit, not unfit return",
    },
    {
        "episode_id": "albrecht_1542_order",
        "person": "Albrecht of Prussia (b.1490, d.1568; age ~52)",
        "anchor": "1542 Königsberg→Gdańsk: broken ocularia; order replacement + "
        "identical pairs (Bieganowski / Ostpreussische Folianten)",
        "type": "broken",
        "work_stream": "Voigt 1841 FROM-Herzog letter citations yearly 1534–1567",
        "local_material": "outputs/tables/b1_albrecht_prussia_activity_chrono.csv; "
        "b1_albrecht_voigt_letter_pins.csv; b1_albrecht_voigt_letter_rates.csv; "
        "b1_albrecht_1542_episode_method.md",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "Voigt FROM-Herzog citations: pre-1542 n=7 (1534–41); "
        "1542 n=3; post n=45 through 1567. Continuity through the "
        "broken-replacement year — not a stoppage trough.",
        "limitations": "Voigt 1841 is a published selection of FROM-Herzog letters "
        "(editorial survival), not a complete chancery dump; Folianten "
        "broken-replacement anchor and Briefwechsel stream are different "
        "corpora; annual citation rates, not week-level stoppage DiD",
    },
    {
        "episode_id": "policastro_1460_order",
        "person": "Iacobo de Policastro (fl.1450s–1470s; order 1460)",
        "anchor": "1460 order_request letter (Ilardi); Sforza castellan milieu",
        "type": "order",
        "work_stream": "Belloni FROM-him castellan letters (local chrono + yearly rates)",
        "local_material": "outputs/tables/b1_policastro_activity_chrono.csv; "
        "b1_policastro_fromhim_letter_rates.csv; "
        "b1_policastro_1460_episode_method.md",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "FROM-him letters: pre-1460 n=2; 1460 n=2 (Oct admin + "
        "Dec 12 ochiali order); post n=17 through 1468 (dense 1461–64). "
        "Continuity after the order.",
        "limitations": "Belloni 1997 regesti (many not OA fulltext); stream is "
        "castellan admin missives not scholar letter-hours; order letter "
        "fulltext still Ilardi/Covini",
    },
    {
        "episode_id": "maurolico_1554_selfreport",
        "person": "Francesco Maurolico (b.1494, d.1575; age ~60)",
        "anchor": "1554-05-29 De conspiciliis first-person: uses different "
        "conspicilia for far/near/reading (Ilardi / Maurolico Project)",
        "type": "soft_self_report (treatise)",
        "work_stream": "dated scientific/optical works chrono",
        "local_material": "outputs/tables/b1_maurolico_francesco_chrono.csv; "
        "b1_maurolico_1554_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "chrono n=9 from 1554-05-29 → 1575 (+21y). Continuity of "
        "scholarly output; rates N/A",
        "limitations": "treatise self-report≠dated order/return; publication dates "
        "proxy near-work intensity loosely",
    },
    {
        "episode_id": "philippe_le_hardi_1389_purchase",
        "person": "Philippe le Hardi, Duke of Burgundy (b.1342, d.1404; age ~47)",
        "anchor": "1389-08-14 Paris: estuy à bericles pour luy (Prost §8240)",
        "type": "soft_order (account purchase)",
        "work_stream": "ducal account / itinerary densify pins to death",
        "local_material": "outputs/tables/b1_philippe_le_hardi_chrono.csv; "
        "b1_philippe_le_hardi_1389_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=10 from 1389-08-14 → 1404-04-27 (+14y). Soft + "
        "continuity; rates N/A",
        "limitations": "case purchase implies wear but not lens prescription class; "
        "ruler accounts ≠ scholar letter stream",
    },
    {
        "episode_id": "ammannati_1473_order",
        "person": "Iacopo Ammannati Piccolomini (b.1422, d.1479; age ~51)",
        "anchor": "1473 order/receipt of good near-and-distant spectacles "
        "(Ilardi; letter to Lorenzo de' Medici)",
        "type": "order",
        "work_stream": "Cherubini epistolario dated FROM-him letters (n=741)",
        "local_material": "outputs/tables/b1_ammannati_cherubini_letter_chrono.csv; "
        "b1_within_person_rates.csv; b1_ammannati_1473_episode_method.md",
        "verdict": "ANALYZABLE_NOW",
        "first_pass": "already in b1_within_person_rates: 1463-72 n=386 (38.6/yr) "
        "→ 1473-79 n=315 (45.0/yr) ratio 1.17; last letter 1479 (+6y). Continuity.",
        "limitations": "receipt≠deprivation; editorial survival of cardinal "
        "epistolario; rates are letter closings not hours",
    },
    {
        "episode_id": "rene_anjou_1449_purchase",
        "person": "René of Anjou (b.1409, d.1480; age ~40 at purchase)",
        "anchor": "1449-06-19 Avignon: two pairs of lunettes for the lord "
        "(Lecoy comptes §674)",
        "type": "soft_order (account purchase)",
        "work_stream": "Lecoy FROM-René mandements / lettres de par le roy",
        "local_material": "outputs/tables/b1_rene_anjou_activity_chrono.csv; "
        "b1_rene_anjou_1449_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=15: 1449-06-19 purchase → 1479-08-06 last hard pin "
        "(+30y). Continuity pins; rates N/A",
        "limitations": "princely account purchase; stream is admin acts not "
        "scholar letters; age ~40 is young for classic presbyopia",
    },
    {
        "episode_id": "bianca_maria_1462_use",
        "person": "Bianca Maria Visconti (b.1425, d.1468; age ~37)",
        "anchor": "1462-11-20 Tranchedini: Signori et Madona use young-vision "
        "spectacles (Ilardi / same dispatch as Francesco Sforza)",
        "type": "soft_self_report (third-party use report)",
        "work_stream": "Nicoud 2000 Persée FROM-her letters May–Sep 1468",
        "local_material": "outputs/tables/b1_bianca_maria_letter_chrono.csv; "
        "b1_bianca_maria_nicoud1468_chrono.csv; "
        "b1_bianca_maria_1462_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "Nicoud FROM-her n≈38 in 1468 (+6y after 1462 report). "
        "Continuity of chancery/family letters; rates N/A (sample year dense)",
        "limitations": "wear is third-party not her self-report; coupled with "
        "Sforza in same dispatch; death 1468 caps window",
    },
    {
        "episode_id": "azevedo_1476_order",
        "person": "João de Azevedo, Bishop of Porto (b.~1430, d.1517; age ~46)",
        "anchor": "1476-01-24 Cambini: 12 paia d'occhiali for vescovo di Oporto "
        "(Ilardi n.29)",
        "type": "soft_order (named recipient)",
        "work_stream": "Digitarq FROM-him episcopal acts 1485–1493",
        "local_material": "outputs/tables/b1_azevedo_joao_porto_chrono.csv; "
        "b1_azevedo_1476_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=10: 1476-01-24 order → 1493-06-12 privilege "
        "(+17y). Continuity pins; rates N/A",
        "limitations": "bulk 12-pair order may include gifts; several pins are "
        "presence/beneficiary not near-work; medium confidence",
    },
    {
        "episode_id": "ardingelli_1451_purchase",
        "person": "Bese di Giovanni Ardingelli (b.1408, d.~1476; age ~43)",
        "anchor": "1451-11-06 gilt-silver occhiali in leather case (Tordi 2 / Ilardi)",
        "type": "soft_order (account-book ownership)",
        "work_stream": "signed MSS + Catasto scrivano densify (Lanza–Speranzi)",
        "local_material": "outputs/tables/b1_ardingelli_bese_lanza_speranzi_chrono.csv; "
        "b1_ardingelli_1451_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=14: 1451-11-06 purchase → 1467-02-01 pistole copy "
        "(+16y). Continuity of copyist/scrivano work; rates N/A",
        "limitations": "account ownership≠dated wear onset; Tordi 2 fulltext still "
        "blocked; copyist hours inferred from signed MSS",
    },
    {
        "episode_id": "charles_orleans_1454_purchase",
        "person": "Charles I Duke of Orléans (b.1394, d.1465; age ~60)",
        "anchor": "1454 estuy de lunectes / lunectes de besicle for the duke "
        "(Laborde / Ducs de Bourgogne)",
        "type": "soft_order (account purchase)",
        "work_stream": "Champion Vie FROM-him ordonnances/mandements 1454–1464",
        "local_material": "outputs/tables/b1_charles_orleans_chrono.csv; "
        "b1_charles_orleans_1454_episode_method.md",
        "verdict": "SOFT_ORDER",
        "first_pass": "chrono n=15: 1454 purchase → 1464-05-14 last mandement "
        "(+10y). Continuity pins; rates N/A",
        "limitations": "princely accounts; literary career not letter-rate corpus; "
        "case purchase implies wear",
    },
    {
        "episode_id": "nicolas_de_baye_1416_selfreport",
        "person": "Nicolas de Baye (b.~1364, d.1419; age ~52)",
        "anchor": "1416-11 petition: débilité de ma veue … enregistrer sans "
        "avoir lunettes (Tuetey Journal)",
        "type": "soft_self_report (office petition)",
        "work_stream": "Parlement greffe journal + conseiller present lists",
        "local_material": "outputs/tables/b1_nicolas_de_baye_chrono.csv; "
        "b1_nicolas_de_baye_1416_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "chrono n=12: 1416-11 petition → 1418-03-28 last present "
        "list (+2y). Same-month greffe sessions continue. Rates N/A",
        "limitations": "short window (Burgundian 1418 ends office); petition is "
        "need-to-wear not order/return; greffe is institutional near-work",
    },
    {
        "episode_id": "tranchedini_1462_selfreport",
        "person": "Nicodemo Tranchedini (b.1411, d.1481; age ~51)",
        "anchor": "1462-11-20 to Simonetta: uses da zoveni spectacles "
        "(Ilardi; myopia self-admit)",
        "type": "soft_self_report (+ inventory pairs)",
        "work_stream": "Ferrari memorial / book-list / inventory chrono",
        "local_material": "outputs/tables/b1_tranchedini_ferrari_memorial_chrono.csv; "
        "b1_tranchedini_1462_episode_method.md",
        "verdict": "SOFT_SELF_REPORT",
        "first_pass": "chrono n=30: 1466–1472 memorials; ochiali boxes 1470-07-26 "
        "and 1472-06 (ya≈17 to 1479-class career). Continuity pins; rates N/A",
        "limitations": "stream is inventories/shipments not letter closings; "
        "also Sforza purchasing agent — personal vs court stock mixed",
    },
    {
        "episode_id": "pepys_1666_69_failure",
        "person": "Samuel Pepys (b.1633, d.1703; age 33-36)",
        "anchor": "1666-12 buys green spectacles; 1668 Turlington tube-spectacles; "
        "1669-05-31 ends diary fearing blindness",
        "type": "documented_correction_failure (NEGATIVE CASE)",
        "work_stream": "the diary itself (daily, ends at episode); Admiralty "
        "career continues to 1700 (non-diary near-work)",
        "local_material": "outputs/tables/b1_pepys_samuel_activity_chrono.csv "
        "(event level)",
        "verdict": "NEGATIVE_CASE",
        "first_pass": "correction did NOT rescue the diary stream — essential "
        "counterweight to survivor-biased positive cases",
        "limitations": "his complaint was likely hypermetropia/astigmatism, not "
        "simple presbyopia; later career shows work continued in other forms",
    },
]


def _load_wave_csvs() -> list[dict[str, str]]:
    extra: list[dict[str, str]] = []
    for path in (WAVE4_CSV, WAVE5_CSV, WAVE6_CSV):
        if not path.exists():
            continue
        for r in csv.DictReader(path.open(encoding="utf-8")):
            extra.append({k: r.get(k) or "" for k in REG_FIELDS})
    return extra


def datini_first_pass() -> list[str]:
    rows = list(csv.DictReader(DATINI_MONTHLY.open()))
    seq = [(int(r["year"]), int(r["month"]), int(r["n_letters_to_datini_bologna_in_busta721"])) for r in rows]
    order_win = [n for (y, m, n) in seq if (y, m) <= (1400, 9)]
    after_win = [n for (y, m, n) in seq if (y, m) > (1400, 9)]
    out_rows = [
        {
            "window": "order_quarter_1400_07_09",
            "n_months": len(order_win),
            "letters_per_month_mean": round(statistics.mean(order_win), 2),
            "letters_per_month_median": statistics.median(order_win),
        },
        {
            "window": "post_order_1400_10_1401_09",
            "n_months": len(after_win),
            "letters_per_month_mean": round(statistics.mean(after_win), 2),
            "letters_per_month_median": statistics.median(after_win),
        },
    ]
    with OUT_DATINI.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    return [
        f"order quarter: mean {out_rows[0]['letters_per_month_mean']}/mo",
        f"post-order year: mean {out_rows[1]['letters_per_month_mean']}/mo",
    ]


def main() -> None:
    reads = datini_first_pass()
    episodes = list(EPISODES) + _load_wave_csvs()
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(REG_FIELDS), lineterminator="\n")
        w.writeheader()
        w.writerows(episodes)

    counts: dict[str, int] = {}
    for e in episodes:
        counts[e["verdict"]] = counts.get(e["verdict"], 0) + 1

    md = "\n".join(
        [
            "# B1 episode registry (route R1, within-person natural experiments)",
            "",
            "**Date:** 2026-08-22 (registry refresh)  ",
            "**Script:** `36_b1_episode_registry.py` → `b1_episode_registry.csv`",
            "",
            "| id | type | verdict | first pass |",
            "|----|------|---------|-----------|",
            *[
                f"| {e['episode_id']} | {e['type'].split(' ')[0]} | {e['verdict']} | {e['first_pass'][:80]} |"
                for e in episodes
            ],
            "",
            f"Status: {counts.get('ANALYZABLE_NOW', 0)} analyzable now, "
            f"{counts.get('SOFT_ORDER', 0)} soft order, "
            f"{counts.get('SOFT_SELF_REPORT', 0)} soft self-report, "
            f"{counts.get('SOFT_MULTI_ORDER', 0)} soft multi-order, "
            f"{counts.get('ANCHOR_ONLY', 0)} anchor-only, "
            f"{counts.get('NEEDS_MINING', 0)} need mining, "
            f"{counts.get('NEGATIVE_CASE', 0)} negative case. "
            "Upgrade condition (DATA_ROADMAP R1): >=5 **sharp** episodes with "
            "series (deprivation/unfit/order with clean pre/post) — soft "
            "self-report / soft order / soft multi-order do not fully count "
            "toward that bar. Portfolio mid-tier lifts: "
            "`b1_wearer_lift_scoreboard.csv`.",
            "",
            "## Datini 1400 order — first pass",
            "",
            *[f"- {r}" for r in reads],
            "- Read: branch letter flow steady across the order window; no",
            "  interruption. Weak positive continuity evidence only (letters TO",
            "  the branch; no pre-order baseline in this busta).",
            "",
            "## Spataro 1532 unfit return — first pass (2026-08-21)",
            "",
            "- Letter rates: `b1_spataro_letter_rates_from_toc.csv`.",
            "- Read: correspondence continues through the bad Venetian pair;",
            "  useful as documented optical failure + continuity, not as a",
            "  stoppage DiD.",
            "",
            "## Lotto soft multi-order — first pass (2026-08-21)",
            "",
            "- Pins: `b1_lotto_ochiali_pins.csv` + `data/raw/lotto_libro/ochiali_pages/`.",
            "- 1544 *da veder luntano* pairs are distance-class; keep separate.",
            "",
            "## Filelfo 1456 vitreis — first pass (2026-08-22)",
            "",
            "- Curated pins: `b1_filelfo_1456_curated_pins.csv` (n=19; May–Jun=9).",
            "- Rates: `b1_filelfo_1456_episode_rates.csv`; method note sibling.",
            "- Multimodal: A336151 pp.240–241; OCR *nitreis*/*ianias* corrected.",
            "- Read: soft-sharp self-need + same-season continuity (not deprivation).",
            "",
            "## Wave 1 soft portfolio lifts (2026-08-22)",
            "",
            "- Eight SOFT_ORDER / SOFT_SELF_REPORT rows from existing chronos:",
            "  barbara, strozzi_filippo, lorenzo_medici, gonzaga_ludovico,",
            "  albrecht, policastro, maurolico, philippe_le_hardi.",
            "- Method notes: `b1_<id>_episode_method.md` siblings.",
            "- Do **not** count toward ≥5 strict-sharp.",
            "",
            "## Wave 3 mid-tier lifts (2026-08-28)",
            "",
            "- Eight more 55–69 → SOFT_* rows from existing chronos:",
            "  ammannati, rene_anjou, bianca_maria, azevedo_joao_porto,",
            "  ardingelli_bese, charles_orleans, nicolas_de_baye, tranchedini.",
            "- Ammannati already has letter rates in `b1_within_person_rates.csv`.",
            "- Do **not** count toward ≥5 strict-sharp.",
            "",
            "## Wave 4 mid-tier lifts (2026-08-28)",
            "",
            "- Sixteen more 55–69 → SOFT_* rows from `b1_wave4_soft_episodes.csv`.",
            "- Do **not** count toward ≥5 strict-sharp.",
            "",
            "## Wave 5 (2026-08-28)",
            "",
            "- Nine more SOFT_* rows from `b1_wave5_soft_episodes.csv`.",
            "- Plus 0–19 documented floors in scoreboard `THIN_LIFT_NEXT`.",
            "",
            "## Wave 6 (2026-08-28)",
            "",
            "- Petrarch / Leo X / Spinelli SOFT_* from `b1_wave6_soft_episodes.csv`.",
            "- Remaining 0–19 CLOSED floors in scoreboard.",
            "",
            "## Mining queue (external, in priority order)",
            "",
            "1. Pirckheimer Briefwechsel bd4–6 — HARD_TO_FIND; library/Ilardi only.",
            "2. Further mid-tier soft lifts via scoreboard `lift_next=CANDIDATE`.",
            "3. Thin-tier floors: `b1_lift_thin_tier_2026-08-22.md` (no fantasy OA).",
            "",
        ]
    )
    OUT_MD.write_text(md, encoding="utf-8")
    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("wrote", OUT_DATINI)
    for k, v in counts.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
