#!/usr/bin/env python3
"""B1 wearer lift scoreboard (portfolio R1, 2026-08-22).

Ranks every roster person 0–100 so mid/low tiers stay visible — not only
strict-sharp episode candidates. Joins roster census × episode registry ×
soft-stock plateau × local chrono CSV presence.

Outputs:
  outputs/tables/b1_wearer_lift_scoreboard.csv
  outputs/tables/b1_wearer_lift_scoreboard_method.md
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import OUTPUT_TABLES

ROSTER = OUTPUT_TABLES / "b1_roster_census.csv"
EPISODES = OUTPUT_TABLES / "b1_episode_registry.csv"
SOFT_STOCK = OUTPUT_TABLES / "b1_soft_stock_plateau_2026-08-05.csv"
WAVE4_CSV = OUTPUT_TABLES / "b1_wave4_soft_episodes.csv"
WAVE5_CSV = OUTPUT_TABLES / "b1_wave5_soft_episodes.csv"
WAVE6_CSV = OUTPUT_TABLES / "b1_wave6_soft_episodes.csv"
WAVE17_CSV = OUTPUT_TABLES / "b1_wave17_soft_episodes.csv"
THIN_NOTE = OUTPUT_TABLES / "b1_lift_thin_tier_2026-08-22.md"
OUT_CSV = OUTPUT_TABLES / "b1_wearer_lift_scoreboard.csv"
OUT_MD = OUTPUT_TABLES / "b1_wearer_lift_scoreboard_method.md"

# episode_id prefix / slug → roster person_id
EPISODE_TO_PERSON: dict[str, str] = {
    "datini_1400_order": "datini",
    "alessandra_1465_selfreport": "alessandra_strozzi",
    "spataro_1532_return": "spataro_giovanni",
    "lotto_1544_55_orders": "lotto",
    "bosson_1415_broken": "knut_bosson",
    "cederni_1454_return": "cederni",
    "arduino_1451_broken": "arduino_baiso",
    "filelfo_1456_vitreis": "filelfo",
    "pirckheimer_1520s_orders": "pirckheimer",
    "pepys_1666_69_failure": "pepys_samuel",
    "barbara_1466_order": "barbara_brandenburg",
    "strozzi_filippo_1464_order": "strozzi_filippo",
    "lorenzo_medici_1479_selfreport": "lorenzo_medici",
    "gonzaga_ludovico_1460_selfreport": "gonzaga_ludovico",
    "albrecht_1542_order": "albrecht_prussia",
    "policastro_1460_order": "policastro",
    "maurolico_1554_selfreport": "maurolico_francesco",
    "philippe_le_hardi_1389_purchase": "philippe_le_hardi",
    "ammannati_1473_order": "ammannati",
    "rene_anjou_1449_purchase": "rene_anjou",
    "bianca_maria_1462_use": "bianca_maria",
    "azevedo_1476_order": "azevedo_joao_porto",
    "ardingelli_1451_purchase": "ardingelli_bese",
    "charles_orleans_1454_purchase": "charles_orleans",
    "nicolas_de_baye_1416_selfreport": "nicolas_de_baye",
    "tranchedini_1462_selfreport": "tranchedini",
}


def _wave_maps() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in (WAVE4_CSV, WAVE5_CSV, WAVE6_CSV, WAVE17_CSV):
        if not path.exists():
            continue
        for r in csv.DictReader(path.open(encoding="utf-8")):
            if r.get("episode_id") and r.get("person_id"):
                out[r["episode_id"]] = r["person_id"]
    return out


EPISODE_TO_PERSON.update(_wave_maps())

# Thin-tier documented floors (Wave 2); applied as lift_next overrides.
THIN_LIFT_NEXT: dict[str, str] = {
    "neri_mici": "CLOSED:YA0 theft complaint 1329; no OA birth–death or post-wear series",
    "bartholomeus_padua": "CLOSED:YA0 court testimony 1318; no multi-point OA post-wear",
    "jacopo_magnia_friar": "CLOSED:YA0 age-band order 1488; no OA densify",
    "egidio_piacenza": "CLOSED:YA0 age-band order 1488; no OA densify",
    "vangelista": "CLOSED:YA0 convent repair purchase 1402; no OA densify",
    "arduino_baiso": "PIN:ANCHOR_ONLY broken 1451-08-25; HARD OA-CLOSED (+3y death)",
    "hesselin_denis": "CLOSED:HARD_OA_CLOSED library comptes; soft stock plateau",
    "baret_john": "CLOSED:YA0 1463 will bequest; death-path ownership only",
    "bernardino": "CLOSED:1444 posthumous relic possession; not dated wear onset",
    "charlett_arthur": "CLOSED:1707 third-party wear-duration ask; not Charlett onset",
    "cleux_jean": "CLOSED:1433 étrennes real; PERMANENT OA-close no birth–death",
    "guy_chauliac": "CLOSED:Chirurgia recommends spectacles; not personal wear",
    "huygens_constantijn": "CLOSED:1612 juvenile myopia/distance bril; wrong B1 near-work class",
    "jacques_moser": "CLOSED:1562 maker self-statement; maker≠personal wear",
    "latone_cambini": "CLOSED:unpinned Cambini orbit; IA exact n=0",
    "sacchetti": "CLOSED:literary depiction of wearers; not self-ownership",
    "barbaro_zaccaria": "CLOSED:1476 Manni/Gori letter unconfirmed; Ilardi cannot locate",
    "bonifazio_ruspi": "CLOSED:1402 Datini gift only; no self-wear report",
    "ruspi_bonifazio": "CLOSED:same Ruspi gift 1402; duplicate id; no self-wear",
    "burke_edmund": "CLOSED:1796 portrait wear; onset unknown; political-metaphor risk",
    "cole_william_bristol": "CLOSED:1695 pinhole monoptick without glass; wrong B1 class",
    "cusac_thomas": "CLOSED:1433 étrennes real; PERMANENT OA-close no obit",
    "joao_lopes_elvas_oculos": "CLOSED:1603 nickname O dos Óculos; nickname≠attested wear",
    "john_carre_york": "CLOSED:YA0 1487 will bequest; death-path ownership only",
    "joris_van_der_paele": "CLOSED:1436 van Eyck portrait only; no documentary wear pin",
    "leonardovinci": "CLOSED:notebook props inferred; not dated personal wear",
    "locke_john": "CLOSED:1701 Churchill supply letter; third-party; late/low",
    "manfredo_parma": "CLOSED:1316 Collectoriae expense attribution uncertain",
    "priestley_joseph": "CLOSED:surviving spectacles artefact; onset year unknown",
    "provost_alain": "CLOSED:1433 étrennes real; PERMANENT OA-close no b–d",
    "rawlins_thomas": "CLOSED:1748 third-party onset; no FROM-him post series",
    "vitko_zuimovic": "CLOSED:1450 theft of case+pair; no OA birth–death",
    "walmysford_william": "CLOSED:1463 debt for spectacles; same-year; no b–d",
    # Wave 9 floors: Wave 7–8 unmeasured rows with already-checked pins
    "akin_frances": "CLOSED:YA0 1756 parish relief pair; no OA b–d",
    "alfonso_iannis": "CLOSED:1466 Cambini 12-pair named client; no OA b–d",
    "allerton_thomas": "CLOSED:YA0 1615 will bequest brass-case pair; death-path",
    "appiani_madre": "CLOSED:1464 two pairs made for Iacopo III's mother; name NN",
    "augustus_saxony": "CLOSED:Münchow luxury Italian glasses; year unpinned",
    "filippa_infante_portugal": "CLOSED:1476 crystal loupe not rivet pair; no OA b–d",
    "herle_mrs": "CLOSED:1651 Gray living purchase; no OA b–d",
    "holme_randall": "CLOSED:1615 Allerton gift recipient; no OA b–d",
    "ixnyng_john": "CLOSED:1463 Baret gift recipient; no OA b–d",
    "nigris_toma": "CLOSED:1527 Lotto portrait only; onset unknown",
    "nugent_margaret": "CLOSED:YA0 1620 will silver spectacles; death-path",
    "piero_frate_fiesole": "CLOSED:1402 convent self-purchase; no OA b–d",
    "rinaldo_de_lo_duca": "CLOSED:1476 Strozzi two-pair recipient; no OA b–d",
    "rook_john": "CLOSED:1686 gift of pair+case; testator unnamed",
    # Wave 10: Dudley (Wave 9 ingest) now has a checked pin + no post-wear series
    "dudley_robert_leicester": "CLOSED:1586 Hague 3-pair living purchase; ya≈2; no multi-point post-wear",
    # Wave 11: Wave 10 unmeasured rows with already-checked pins
    "alsop_thomas": "CLOSED:1701 Hunt gift recipient; no OA b–d",
    "browne_joseph_cheshire": "CLOSED:1805 gift of clothes+spectacles; testator unnamed",
    "cuming_henry": "CLOSED:1828 gift to nephew; testator unnamed",
    "folkes_martin": "CLOSED:c.1720 Hogarth eyeglasses sketch; onset unknown",
    "gilcock_joseph": "CLOSED:1724 Bible+spectacles gift; testator unnamed",
    "hunt_john_chester": "CLOSED:YA0 1701 will my Spectacles; death-path",
    "hutchinson_mary_durham": "CLOSED:YA0 1833 will my Spectacles; death-path",
    "lowe_john_warwick": "CLOSED:1831 left spectacles+case complaint; no OA b–d",
    "reynolds_joshua": "CLOSED:c.1788 self-portrait wear; onset unknown",
    "sankey_catharine": "CLOSED:1838 sibling gift; testator unnamed",
    "senhouse_william": "CLOSED:1487 Carre gift of silver-gilt pair; no post-wear series",
    "walpole_horace": "CLOSED:1757 Scarlett green tint temporary; not durable near-work",
    # Wave 12: Wave 11 unmeasured rows with already-checked pins
    "addison_susannah": "CLOSED:1848 gift of spectacles+account books; testator unnamed",
    "robinson_ellen": "CLOSED:1814 gift recipient; testator unnamed",
    "seabrook_william": "CLOSED:1838 minister gift; testator unnamed",
    "unsworth_alice": "CLOSED:1846 silver-frame gift; testator unnamed",
    "vernon_mary": "CLOSED:1831 apparel+spectacles gift; testator unnamed",
    # Wave 14: Wave 13 unmeasured portrait rows with already-checked pins
    "albertis_gaspare": "CLOSED:1547 Belli portrait long-handle lenses; onset unknown",
    "bening_simon": "CLOSED:1558 V&A self-portrait holds removed glasses; onset unknown",
    "borghini_vincenzo": "CLOSED:1570 Poppi portrait spectacles on table; onset unknown",
    "caetani_francesco": "CLOSED:1661 Sermoneta portrait large concave lenses; onset unknown",
    "capivaccio_girolamo": "CLOSED:1630 Tomasini engraving strings around ears; onset unknown",
    "dolci_carlo": "CLOSED:1674 Uffizi self-portrait holds portrait wearing glasses; onset unknown",
    "giordano_luca": "CLOSED:1688 pince-nez self-portraits; onset unknown",
    "morales_ambrosio": "CLOSED:1590 portrait spectacles over right ear; onset unknown",
    "morigia_paolo": "CLOSED:1596 Galizia portrait holds convex pair; onset unknown",
    "nino_de_guevara": "CLOSED:1600 El Greco strings around ears; onset unknown",
    "pitti_miniato": "CLOSED:1544 Vasari presumed fresco holds eyeglasses; identity/year soft",
    "quevedo_francisco": "CLOSED:1632 Velázquez large-lens portrait; onset unknown",
    "savonarola_michele": "CLOSED:1455 Archiginnasio portrait wears glasses reading; onset unknown",
    # Wave 15: Wave 14 unmeasured <1700 rows with already-checked pins
    "guevara_felipe": "CLOSED:1531 Vermeyen Clark portrait; onset unknown",
    "barbani_giovanni": "CLOSED:1550 Aretino V 510 crystal gift/request; no OA b–d",
    # Wave 16: Wave 15 unmeasured <1700 rows with already-checked pins
    "calasanz_giuseppe": "CLOSED:1648 San Pantaleo relic spectacles; onset unknown",
    "filippo_neri": "CLOSED:1595 Albertotti relic 3 pairs; onset unknown",
    "francesca_romana": "CLOSED:1440 canonization witness wear; no OA post-wear series",
    "gabriel_friar_jerusalem": "CLOSED:YA0 age-band order 1488; no OA densify",
    "giacomo_del_piccio": "CLOSED:1471 Welch fresco brief wears ochiali; programme unexecuted",
    "gil_de_siloe": "CLOSED:1468 Miraflores self-portrait statue wears spectacles; onset unknown",
    "hannus_gallo": "CLOSED:1485 living brilis purchase; trade overlay; no OA b–d",
    "jeanne_evreux": "CLOSED:1371 testament lunette jewel; not rivet pair; no series",
    "oldenbarnevelt": "CLOSED:1619 Museum Rotterdam relic pair; no dated purchase",
    "villon_francois": "CLOSED:1461 Grand Testament literary lunettes; not documentary wear",
}


def _band(score: int) -> str:
    if score >= 95:
        return "95-100"
    if score >= 85:
        return "85-94"
    if score >= 70:
        return "70-84"
    if score >= 55:
        return "55-69"
    if score >= 40:
        return "40-54"
    if score >= 20:
        return "20-39"
    return "0-19"


_CHRONO_ALIASES: dict[str, str] = {
    "barbara_oa_letter_chrono": "barbara_brandenburg",
    "barbara_hofmann_letter_chrono": "barbara_brandenburg",
    "barbara_nicoud1468_chrono": "barbara_brandenburg",
    "bianca_maria_letter_chrono": "bianca_maria",
    "bianca_maria_nicoud1468_chrono": "bianca_maria",
    "alessandra_letter_chrono": "alessandra_strozzi",
    "alessandra_letter_chrono_with_heads": "alessandra_strozzi",
    "ardingelli_bese_lanza_speranzi_chrono": "ardingelli_bese",
    "tranchedini_ferrari_memorial_chrono": "tranchedini",
    "ammannati_cherubini_letter_chrono": "ammannati",
    "ammannati_tomo3_letter_chrono": "ammannati",
    "pirckheimer_allen_erasmus_chrono": "pirckheimer",
    "pirckheimer_bd2_letter_chrono": "pirckheimer",
    "mazzei_letter_chrono": "mazzei",
    "gonzaga_ludovico_spectacle_reading_chrono": "gonzaga_ludovico",
    "lorenzo_medici_ross_letter_chrono": "lorenzo_medici",
    "strozzi_filippo_sepoltuario_chrono": "strozzi_filippo",
    "wyatt_henry_lp_chrono": "wyatt_henry",
    "sforza_francesco_reg9_chrono": "sforza_francesco",
    "cederni_activity_chrono": "cederni",
    "pepys_samuel_activity_chrono": "pepys_samuel",
    "knut_bosson_activity_chrono": "knut_bosson",
}


def _chrono_index() -> dict[str, tuple[int, str]]:
    """person_id → (n_rows, best matching chrono filename)."""
    out: dict[str, tuple[int, str]] = {}
    for p in sorted(OUTPUT_TABLES.glob("b1_*chrono*.csv")):
        if "control_nearwork" in p.name or "snapshot" in p.name:
            continue
        stem = p.name.removeprefix("b1_").removesuffix(".csv")
        if stem in _CHRONO_ALIASES:
            pid = _CHRONO_ALIASES[stem]
        else:
            pid = stem
            for sfx in (
                "_activity_chrono",
                "_letter_chrono",
                "_chrono",
            ):
                if pid.endswith(sfx):
                    pid = pid[: -len(sfx)]
                    break
        try:
            n = max(0, sum(1 for _ in p.open(encoding="utf-8")) - 1)
        except OSError:
            n = 0
        prev = out.get(pid)
        if prev is None or n > prev[0]:
            out[pid] = (n, p.name)
    return out


def _score_episode(ep: dict[str, str]) -> tuple[int, str]:
    verdict = ep.get("verdict") or ""
    typ = (ep.get("type") or "").lower()
    lim = (ep.get("limitations") or "") + " " + (ep.get("work_stream") or "")
    lim_l = lim.lower()

    if verdict == "NEGATIVE_CASE":
        return 72, "coded negative case (portfolio counterweight)"
    if verdict == "NEEDS_MINING":
        return 52, "anchor known; sources HARD_TO_FIND / not local"
    if verdict == "ANCHOR_ONLY":
        return 42, "sharpish anchor; no OA work stream"
    if verdict in ("SOFT_ORDER", "SOFT_SELF_REPORT", "SOFT_MULTI_ORDER"):
        return 76, f"soft episode ({verdict})"
    if verdict == "SOFT_MULTI_ORDER" or "soft_multi" in typ:
        return 74, "soft multi-order"

    sharp = (
        "documented_failure" in typ
        or "documented_unfit" in typ
        or "unfit_return" in typ
        or "order + documented_failure" in typ
        or "order + documented_unfit" in typ
        or (typ.startswith("broken") and "not broken" not in typ)
    )
    soft = any(
        x in typ
        for x in (
            "self_report",
            "self_need",
            "soft_order",
            "soft_self",
            "soft_multi",
            "soft-sharp",
            "soft anchor",
            "vitreis",
        )
    )
    confound = any(
        x in lim_l
        for x in (
            "constance",
            "network, not",
            "network not",
            "letters to ",
            "to bologna",
            "not datini hand",
        )
    )

    if soft and verdict == "ANALYZABLE_NOW":
        return 76, "soft self-report/self-need coded ANALYZABLE_NOW"
    if sharp and verdict == "ANALYZABLE_NOW":
        if confound or "constance" in lim_l:
            return 88, "broken/return with confound or non-hand stream"
        return 97, "unfit-return/broken + same-person stream"
    if "order" in typ and verdict == "ANALYZABLE_NOW":
        if confound or "to datini" in lim_l or "to bologna" in lim_l:
            return 88, "order + network/confound stream"
        return 90, "order + analyzable stream"
    if verdict == "ANALYZABLE_NOW":
        return 85, "analyzable episode (generic)"
    return 50, f"episode verdict {verdict}"


def _score_roster_only(
    r: dict[str, str],
    soft_gate: str | None,
    n_chrono: int,
) -> tuple[int, str]:
    hard = (r.get("hard_dated_series") or "").strip().lower()
    et = (r.get("evidence_type") or "").lower()
    ya_s = (r.get("years_after_evidence") or "").strip()
    try:
        ya = float(ya_s) if ya_s else None
    except ValueError:
        ya = None

    if soft_gate:
        if "YA0" in soft_gate or "SHORT_WINDOW" in soft_gate or "PERMANENT_close" in soft_gate:
            return 28, f"soft-stock {soft_gate[:50]}"
        if "HARD_OA_CLOSED" in soft_gate or "LIBRARY" in soft_gate:
            return 38, f"soft-stock closed {soft_gate[:40]}"
        return 45, f"soft-stock {soft_gate[:50]}"

    if ya == 0.0 or (ya is not None and ya <= 0 and hard == "false"):
        return 28, "YA≈0 / single-pin class"
    if any(x in et for x in ("probate", "death_inventory", "inventory")) and hard != "true":
        return 25, "inventory/probate without hard series"
    if hard == "true":
        # 55–69 from years_after
        bump = 0
        if ya is not None:
            bump = min(14, int(ya // 2))
        score = 55 + bump
        return min(69, score), "hard post-wear series; no R1 episode row yet"
    if hard == "false" and n_chrono > 0:
        return 48, "soft dated pins / hard=False with chrono"
    if n_chrono > 0:
        return 35, "local chrono present; hard flag blank"
    if ya is None and not (r.get("years_after_source") or "").startswith("activity"):
        return 12, "unmeasured / blank years_after"
    return 18, "rostered but thin / unmeasured"


def main() -> None:
    roster = list(csv.DictReader(ROSTER.open(encoding="utf-8")))
    episodes = {
        EPISODE_TO_PERSON[e["episode_id"]]: e
        for e in csv.DictReader(EPISODES.open(encoding="utf-8"))
        if e["episode_id"] in EPISODE_TO_PERSON
    }
    # also accept unmapped by fuzzy prefix
    for e in csv.DictReader(EPISODES.open(encoding="utf-8")):
        eid = e["episode_id"]
        if eid in EPISODE_TO_PERSON:
            continue
        # try person_id = first two underscore tokens if matches roster
        pass

    soft = {
        r["person_id"]: r.get("gate_status") or ""
        for r in csv.DictReader(SOFT_STOCK.open(encoding="utf-8"))
    }
    chronos = _chrono_index()

    rows_out: list[dict[str, str]] = []
    for r in roster:
        pid = r["person_id"]
        ep = episodes.get(pid)
        n_chrono, chrono_file = chronos.get(pid, (0, ""))
        soft_gate = soft.get(pid)

        if ep:
            score, why = _score_episode(ep)
            episode_id = ep["episode_id"]
            verdict = ep["verdict"]
            if score >= 95:
                lift_next = "HOLD:strict-sharp — densify only if cheap"
            elif score >= 85:
                lift_next = "HOLD:half-sharp — no remote dig this pass"
            elif score >= 70:
                lift_next = "HOLD:soft episode coded — optional rate polish"
            elif verdict == "NEEDS_MINING":
                lift_next = "LIBRARY/Ilardi only — stop web dig"
            elif verdict == "ANCHOR_ONLY":
                lift_next = "CLOSED unless new OA workshop/stream"
            else:
                lift_next = "review episode limitations"
        else:
            score, why = _score_roster_only(r, soft_gate, n_chrono)
            episode_id = ""
            verdict = ""
            if pid in THIN_LIFT_NEXT:
                lift_next = THIN_LIFT_NEXT[pid]
            elif score >= 55:
                lift_next = "CANDIDATE:soft R1 row if dated wear+stream local"
            elif score >= 40:
                lift_next = "optional densify pin or document CLOSED"
            elif score >= 20:
                lift_next = "document floor (CLOSED/PIN) — do not chase hard"
            else:
                lift_next = "scout OA chrono or leave unmeasured"

        if pid in THIN_LIFT_NEXT and not ep:
            # documented floor bump into 20–39 / low 40s
            if score < 25:
                score = 30
                why = "thin-tier documented floor (Wave 2)"
            elif score < 40 and "CLOSED" in THIN_LIFT_NEXT[pid]:
                score = max(score, 32)
                why = why + "; thin-tier CLOSED noted"

        rows_out.append(
            {
                "person_id": pid,
                "name": r.get("name") or "",
                "lift_score": str(score),
                "band": _band(score),
                "score_reason": why,
                "episode_id": episode_id,
                "verdict": verdict,
                "evidence_year": r.get("evidence_year") or "",
                "evidence_type": r.get("evidence_type") or "",
                "hard_dated_series": r.get("hard_dated_series") or "",
                "years_after_evidence": r.get("years_after_evidence") or "",
                "n_dated_activity": r.get("n_dated_activity") or "",
                "n_chrono_rows": str(n_chrono),
                "chrono_file": chrono_file,
                "soft_stock_gate": soft_gate or "",
                "lift_next": lift_next if pid not in THIN_LIFT_NEXT or ep else THIN_LIFT_NEXT.get(pid, lift_next),
            }
        )

    # ensure thin overrides win on lift_next
    for row in rows_out:
        if row["person_id"] in THIN_LIFT_NEXT and not row["episode_id"]:
            row["lift_next"] = THIN_LIFT_NEXT[row["person_id"]]

    rows_out.sort(key=lambda x: (-int(x["lift_score"]), x["person_id"]))
    fields = list(rows_out[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)

    bands = Counter(r["band"] for r in rows_out)
    n_ep = sum(1 for r in rows_out if r["episode_id"])
    md = "\n".join(
        [
            "# Wearer lift scoreboard (R1 portfolio)",
            "",
            "**Date:** 2026-08-22  ",
            "**Script:** `38_b1_wearer_lift_scoreboard.py`",
            "",
            "Whole-roster 0–100 scores so mid/low tiers stay visible. Strict-sharp",
            "≥5 remains aspirational; soft and thin lifts are in-scope.",
            "",
            "## Rubric",
            "",
            "| Band | Criteria |",
            "|------|----------|",
            "| 95–100 | Broken/unfit-return + same-person dated stream |",
            "| 85–94 | Broken/order with confound or network-not-hand stream |",
            "| 70–84 | Soft episode coded (self-report / soft order / multi-order) |",
            "| 55–69 | Hard post-wear series on roster, no R1 episode row |",
            "| 40–54 | Soft stock / thin pins / hard=False with chrono |",
            "| 20–39 | YA≈0 / inventory-only / single pin |",
            "| 0–19 | Unmeasured / no local chrono |",
            "",
            f"**Rows:** {len(rows_out)} (full roster). **With episode:** {n_ep}.",
            "",
            "## Band counts",
            "",
            "| Band | n |",
            "|------|--:|",
            *[f"| {b} | {bands.get(b, 0)} |" for b in ("95-100", "85-94", "70-84", "55-69", "40-54", "20-39", "0-19")],
            "",
            "## Wave 1 soft promotions (2026-08-22)",
            "",
            "Eight mid-tier people with local chronos → `SOFT_ORDER` / `SOFT_SELF_REPORT`",
            "episode rows (do **not** count toward ≥5 strict-sharp):",
            "barbara_brandenburg, strozzi_filippo, lorenzo_medici, gonzaga_ludovico,",
            "albrecht_prussia, policastro, maurolico_francesco, philippe_le_hardi.",
            "",
            "## Wave 3 mid-tier lifts (2026-08-28)",
            "",
            "Eight more 55–69 people with local chronos → `SOFT_ORDER` / `SOFT_SELF_REPORT`:",
            "ammannati, rene_anjou, bianca_maria, azevedo_joao_porto,",
            "ardingelli_bese, charles_orleans, nicolas_de_baye, tranchedini.",
            "",
            "## Wave 4 mid-tier lifts (2026-08-28)",
            "",
            "Sixteen more 55–69 people → `SOFT_*` via `b1_wave4_soft_episodes.csv`.",
            "",
            "## Wave 5 (2026-08-28)",
            "",
            "Nine more SOFT_* via `b1_wave5_soft_episodes.csv`; plus 0–19 CLOSED floors.",
            "",
            "## Wave 17 (2026-08-30)",
            "",
            "Six SOFT_* via `b1_wave17_soft_episodes.csv` (existing local chronos);",
            "eight hard=False chronos from dated post-wear works/offices;",
            "plus Chardin ingested with 1775–77 Heymann pins (lands ≥40).",
            "",
            "## Wave 2 thin tier",
            "",
            f"See `{THIN_NOTE.name}` — documented CLOSED/PIN floors for YA0/soft-stock.",
            "",
            "## Top 15 by score",
            "",
            "| score | person_id | episode | verdict |",
            "|------:|-----------|---------|---------|",
            *[
                f"| {r['lift_score']} | {r['person_id']} | {r['episode_id'] or '—'} | {r['verdict'] or '—'} |"
                for r in rows_out[:15]
            ],
            "",
        ]
    )
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"wrote {OUT_CSV} ({len(rows_out)} rows)")
    print(f"wrote {OUT_MD}")
    print("bands:", dict(bands))


if __name__ == "__main__":
    main()
