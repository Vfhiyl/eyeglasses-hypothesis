#!/usr/bin/env python3
"""B1 roster census: all documentary wearers, no hard-length gate + controls.

Estimand shift (2026-07-31):
  Hard dated series (n≥20) is an appendix of reconstructable long trajectories.
  Main B1 coding is the full named-wearer roster with short/zero/censored
  outcomes retained. Controls matched on birth year for outcome B
  (years alive after age 45). Outcome A' = years_after_evidence when measured
  (activity proxy or survival upper bound), never used as an inclusion filter.

Outputs:
  outputs/tables/b1_roster_census.csv
  outputs/tables/b1_roster_census_summary.csv
  outputs/tables/b1_roster_control_matches.csv
  outputs/tables/b1_roster_control_summary.csv
  outputs/tables/b1_treatment_onsetish_roster.csv  (refreshed)
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, OUTPUT_TABLES


def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}")

ILARDI = DATA_CURATED / "ilardi_named_wearers.csv"
CANDIDATES = DATA_CURATED / "b1_named_wearers_candidates_new.csv"
ACTIVITY = OUTPUT_TABLES / "b1_activity_proxy_panel.csv"
CONTROLS = OUTPUT_TABLES / "b1_control_candidates_v3.csv"
CONTROLS_FALLBACK = OUTPUT_TABLES / "b1_control_candidates_v2.csv"
CLEAN_TC = OUTPUT_TABLES / "b1_treatment_control_activity_panel_clean.csv"

OUT_CENSUS = OUTPUT_TABLES / "b1_roster_census.csv"
OUT_CENSUS_SUM = OUTPUT_TABLES / "b1_roster_census_summary.csv"
OUT_MATCHES = OUTPUT_TABLES / "b1_roster_control_matches.csv"
OUT_CTRL_SUM = OUTPUT_TABLES / "b1_roster_control_summary.csv"
OUT_ONSETISH = OUTPUT_TABLES / "b1_treatment_onsetish_roster.csv"

# Evidence types that are ownership-at-death / pure gift / non-wear depiction.
# Kept in census with in_onsetish_treatment=False; years_after often 0 by construction.
DEATH_OR_NON_ONSET = {
    "probate_inventory",
    "death_inventory_ownership",
    "posthumous_relic_possession",
    "will_bequest_ownership",
    "inventory_cases_lenses",
    "notarial_inventory",
    "inventory_escritori_ownership",
    "living_inventory_ownership",  # living inventaire without purchase/self-report onset
    "gift_receipt",
    # gift_receipt_luxury kept in onsetish when personal-use reading is attested
    # (e.g. Wolsey/Wyatt soft series); still not death-path.
    "literary_depiction_author",
    "notebook_mentions_inferred",
    "order_request_letter_unconfirmed",
    "medical_treatise_mention",
}

WEAK_CONFIDENCE = {"low"}

OCC_BUCKET = {
    "humanist_scholar": "humanist",
    "cardinal_humanist": "humanist",
    "humanist_patrician": "humanist",
    "humanist_translator_editor_polygraph": "humanist",
    "diplomat_ambassador_humanist": "humanist",
    "mathematician_abbot_humanist": "humanist",
    "pope_humanist_patron": "ruler_cleric",
    "pope_humanist": "ruler_cleric",
    "pope_ruler": "ruler_cleric",
    "duke_ruler": "ruler",
    "marquis_ruler": "ruler",
    "duchess_ruler": "ruler",
    "marchesa_ruler": "ruler",
    "king_ruler": "ruler",
    "bishop_prelate": "cleric",
    "bishop_statesman": "cleric",
    "bishop": "cleric",
    "prelate_cleric": "cleric",
    "cardinal_philosopher_theologian": "cleric",
    "friar": "cleric",
    "franciscan_friar": "cleric",
    "nun_scribe": "cleric",
    "preacher_saint": "cleric",
    "merchant": "merchant",
    "merchant_banker": "merchant",
    "merchant_burgess": "merchant",
    "merchant_writer": "merchant",
    "portuguese_client": "merchant",
    "cardinal_statesman": "ruler_cleric",
    "treasurer_courtier": "clerk",  # thick clerk/notary control stratum; admin SPARQL thin
    "surgeon_author": "cleric",
    "painter": "artisan",
    "woodcarver_artisan": "artisan",
    "artist_engineer": "artisan",
    "bank_employee_clerk": "clerk",
    "notary": "clerk",
    "notary_family_elderly": "clerk",
    "parlement_greffier_clerk": "clerk",
    "castellan_military_administrator": "admin",
    "gentlewoman_letter_writer": "letter_writer",
    "music_theorist_composer_choirmaster": "humanist",
    "venetian_diplomat_patrician": "humanist",
    "citizen_writer": "clerk",
    "widow": "other",
}


def _f(x: str | None) -> float | None:
    if x is None:
        return None
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _i(x: str | None) -> int | None:
    v = _f(x)
    return int(v) if v is not None else None


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def merge_roster() -> list[dict]:
    """Ilardi primary; candidates fill missing person_ids / patch blank fields."""
    by_id: dict[str, dict] = {}
    for r in _read(ILARDI):
        pid = r["person_id"].strip()
        by_id[pid] = {
            "person_id": pid,
            "name": r.get("name", ""),
            "wikidata_qid": (r.get("wikidata_qid") or "").strip(),
            "birth_year": r.get("birth_year", ""),
            "death_year": r.get("death_year", ""),
            "evidence_year": r.get("evidence_year", ""),
            "evidence_type": r.get("evidence_type", ""),
            "occupation_class": r.get("occupation_class", ""),
            "confidence": (r.get("confidence") or "").strip().lower(),
            "source_ref": r.get("source_ref", ""),
            "notes": r.get("notes", ""),
            "roster_source": "ilardi",
        }
    for r in _read(CANDIDATES):
        pid = r["person_id"].strip()
        if pid in by_id:
            cur = by_id[pid]
            for k in (
                "wikidata_qid",
                "birth_year",
                "death_year",
                "evidence_year",
                "evidence_type",
                "occupation_class",
                "confidence",
                "source_ref",
                "notes",
                "name",
            ):
                if not str(cur.get(k) or "").strip() and str(r.get(k) or "").strip():
                    cur[k] = r[k]
            if cur["roster_source"] == "ilardi":
                cur["roster_source"] = "ilardi+candidates"
            continue
        by_id[pid] = {
            "person_id": pid,
            "name": r.get("name", ""),
            "wikidata_qid": (r.get("wikidata_qid") or "").strip(),
            "birth_year": r.get("birth_year", ""),
            "death_year": r.get("death_year", ""),
            "evidence_year": r.get("evidence_year", ""),
            "evidence_type": r.get("evidence_type", ""),
            "occupation_class": r.get("occupation_class", ""),
            "confidence": (r.get("confidence") or "").strip().lower(),
            "source_ref": r.get("source_ref", ""),
            "notes": r.get("notes", ""),
            "roster_source": "candidates_new",
        }
    return sorted(by_id.values(), key=lambda d: (d.get("evidence_year") or "9999", d["person_id"]))


def classify(row: dict) -> tuple[bool, str]:
    et = (row.get("evidence_type") or "").strip()
    conf = (row.get("confidence") or "").strip().lower()
    if conf in WEAK_CONFIDENCE:
        return False, "exclude_low_confidence"
    if et in DEATH_OR_NON_ONSET:
        return False, f"exclude_{et}"
    if not row.get("evidence_year"):
        return False, "exclude_missing_evidence_year"
    return True, "onsetish_treatment"


def build_census() -> list[dict]:
    activity = {r["person_id"]: r for r in _read(ACTIVITY)}
    rows = merge_roster()
    out: list[dict] = []
    for r in rows:
        in_t, reason = classify(r)
        birth = _i(r.get("birth_year"))
        death = _i(r.get("death_year"))
        evid = _i(r.get("evidence_year"))
        act = activity.get(r["person_id"])
        years_act = _f(act.get("years_after_evidence")) if act else None
        hard = ""
        if act:
            hard = str(act.get("hard_dated_series", "")).strip()
        years_surv = None
        if evid is not None and death is not None and death >= evid:
            years_surv = float(death - evid)

        # Primary years_after_evidence = activity proxy only (includes short soft
        # series). Survival is a separate upper bound — do NOT fill missing
        # activity with death−evidence (inflates Spataro-class cases).
        if years_act is not None:
            years_after = years_act
            years_source = "activity_proxy"
        else:
            years_after = None
            years_source = "unmeasured"

        # Years lived after turning 45: (death − birth) − 45, floored at 0.
        years_alive_after_45 = None
        if birth is not None and death is not None and death >= birth:
            years_alive_after_45 = float(max(0, (death - birth) - 45))

        evidence_age = None
        if birth is not None and evid is not None:
            evidence_age = evid - birth

        occ = (r.get("occupation_class") or "").strip()
        out.append(
            {
                **r,
                "occupation_bucket": OCC_BUCKET.get(occ, "other"),
                "in_onsetish_treatment": str(in_t),
                "inclusion_reason": reason,
                "evidence_age": evidence_age if evidence_age is not None else "",
                "years_after_activity": years_act if years_act is not None else "",
                "years_after_survival": years_surv if years_surv is not None else "",
                "years_after_evidence": years_after if years_after is not None else "",
                "years_after_source": years_source,
                "hard_dated_series": hard,
                "years_alive_after_45": years_alive_after_45
                if years_alive_after_45 is not None
                else "",
                "n_dated_activity": act.get("n_dated", "") if act else "",
                "activity_proxy": act.get("activity_proxy", "") if act else "",
                "activity_note": act.get("note", "") if act else "",
            }
        )
    return out


def summarize_census(census: list[dict]) -> list[dict]:
    def nums(rows: list[dict], key: str) -> list[float]:
        out: list[float] = []
        for r in rows:
            v = _f(r.get(key))
            if v is not None:
                out.append(v)
        return out

    all_rows = census
    onset = [r for r in census if r["in_onsetish_treatment"] == "True"]
    measured = [r for r in onset if r["years_after_source"] != "unmeasured"]
    act_only = [r for r in onset if r["years_after_source"] == "activity_proxy"]
    hard = [r for r in onset if str(r.get("hard_dated_series")).lower() == "true"]

    def pack(label: str, rows: list[dict], key: str = "years_after_evidence") -> dict:
        xs = nums(rows, key)
        row = {
            "subset": label,
            "n": len(rows),
            "n_with_outcome": len(xs),
            "outcome": key,
            "min": "",
            "p25": "",
            "median": "",
            "mean": "",
            "p75": "",
            "max": "",
            "n_ge_5": "",
            "n_ge_15": "",
            "share_ge_5": "",
            "share_ge_15": "",
            "note": "",
        }
        if not xs:
            row["note"] = "no numeric outcomes"
            return row
        xs_s = sorted(xs)
        row.update(
            {
                "min": xs_s[0],
                "p25": xs_s[max(0, len(xs_s) // 4)],
                "median": statistics.median(xs_s),
                "mean": round(statistics.mean(xs_s), 2),
                "p75": xs_s[min(len(xs_s) - 1, (3 * len(xs_s)) // 4)],
                "max": xs_s[-1],
                "n_ge_5": sum(1 for x in xs if x >= 5),
                "n_ge_15": sum(1 for x in xs if x >= 15),
                "share_ge_5": round(sum(1 for x in xs if x >= 5) / len(xs), 3),
                "share_ge_15": round(sum(1 for x in xs if x >= 15) / len(xs), 3),
            }
        )
        return row

    rows = [
        pack("all_documentary_roster", all_rows),
        pack("onsetish_treatment", onset),
        pack("onsetish_with_any_years_after", measured),
        pack("onsetish_activity_proxy_only", act_only),
        pack("onsetish_hard_appendix_only", hard),
        pack("onsetish_years_alive_after_45", onset, "years_alive_after_45"),
    ]
    # Explicit contrast: hard-gated vs ungated activity
    if act_only:
        rows.append(
            {
                **pack("NOTE_hard_gate_bias_check", act_only),
                "note": (
                    "Compare onsetish_activity_proxy_only vs onsetish_hard_appendix_only: "
                    "hard median is conditioned on length≥~5 and must not be the estimand."
                ),
            }
        )
    return rows


def match_controls(census: list[dict], birth_window: int = 10) -> tuple[list[dict], list[dict]]:
    ctrl_path = CONTROLS if CONTROLS.exists() else CONTROLS_FALLBACK
    controls = _read(ctrl_path)
    ctrl_rows: list[dict] = []
    for c in controls:
        if str(c.get("is_known_wearer", "")).lower() == "true":
            continue
        b = _i(c.get("birth"))
        d = _i(c.get("death"))
        if b is None or d is None:
            continue
        ya45 = float(max(0, (d - b) - 45)) if d >= b else None
        if ya45 is None:
            continue
        ctrl_rows.append(
            {
                "qid": c["qid"],
                "name": c["name"],
                "birth_year": b,
                "death_year": d,
                "cohort": c.get("cohort", ""),
                "years_alive_after_45": ya45,
            }
        )

    # Optional WD career overlay from prior clean panel
    clean = {r["qid"]: r for r in _read(CLEAN_TC)} if CLEAN_TC.exists() else {}

    onset = [
        r
        for r in census
        if r["in_onsetish_treatment"] == "True" and _i(r.get("birth_year")) is not None
    ]
    matches: list[dict] = []
    for t in onset:
        tb = _i(t["birth_year"])
        assert tb is not None
        cands = [c for c in ctrl_rows if abs(c["birth_year"] - tb) <= birth_window]
        if not cands:
            matches.append(
                {
                    "person_id": t["person_id"],
                    "name": t["name"],
                    "birth_year": tb,
                    "death_year": t.get("death_year", ""),
                    "occupation_bucket": t["occupation_bucket"],
                    "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                    "years_after_evidence_t": t.get("years_after_evidence", ""),
                    "n_matched_controls": 0,
                    "median_years_alive_after_45_c": "",
                    "delta_ya45_t_minus_c_median": "",
                    "matched_control_qids": "",
                    "match_status": "unmatched_birth_window",
                }
            )
            continue
        c_ya = [c["years_alive_after_45"] for c in cands]
        med_c = statistics.median(c_ya)
        t_ya = _f(t.get("years_alive_after_45"))
        delta = (t_ya - med_c) if t_ya is not None else None
        # Prefer controls that also appear in clean WD panel when available
        qids = [c["qid"] for c in sorted(cands, key=lambda x: abs(x["birth_year"] - tb))[:8]]
        matches.append(
            {
                "person_id": t["person_id"],
                "name": t["name"],
                "birth_year": tb,
                "death_year": t.get("death_year", ""),
                "occupation_bucket": t["occupation_bucket"],
                "years_alive_after_45_t": t.get("years_alive_after_45", ""),
                "years_after_evidence_t": t.get("years_after_evidence", ""),
                "n_matched_controls": len(cands),
                "median_years_alive_after_45_c": med_c,
                "delta_ya45_t_minus_c_median": round(delta, 2) if delta is not None else "",
                "matched_control_qids": ";".join(qids),
                "match_status": "matched",
                "n_controls_with_wd_clean": sum(1 for q in qids if q in clean),
            }
        )

    matched = [m for m in matches if m["match_status"] == "matched"]
    deltas = [_f(m["delta_ya45_t_minus_c_median"]) for m in matched]
    deltas_n = [d for d in deltas if d is not None]
    t_ya45 = [_f(m["years_alive_after_45_t"]) for m in matched]
    t_ya45_n = [x for x in t_ya45 if x is not None]
    # Pool of controls used at least once
    used_q: set[str] = set()
    for m in matched:
        used_q.update(q for q in m["matched_control_qids"].split(";") if q)
    used_ctrl_ya = [c["years_alive_after_45"] for c in ctrl_rows if c["qid"] in used_q]

    summary = [
        {
            "metric": "onsetish_with_birth",
            "n_treatment": len(onset),
            "n_matched_treatment": len(matched),
            "n_unmatched_treatment": len(onset) - len(matched),
            "n_control_pool": len(ctrl_rows),
            "n_controls_used_in_matches": len(used_q),
            "median_ya45_treatment_matched": statistics.median(t_ya45_n) if t_ya45_n else "",
            "median_ya45_controls_used": statistics.median(used_ctrl_ya) if used_ctrl_ya else "",
            "median_delta_ya45_t_minus_c": statistics.median(deltas_n) if deltas_n else "",
            "mean_delta_ya45_t_minus_c": round(statistics.mean(deltas_n), 2) if deltas_n else "",
            "n_delta_ge_5": sum(1 for d in deltas_n if d >= 5) if deltas_n else "",
            "n_delta_ge_15": sum(1 for d in deltas_n if d >= 15) if deltas_n else "",
            "sesoi_direction_5_on_median_delta": (
                "PASS_RAW"
                if deltas_n and statistics.median(deltas_n) >= 5
                else "FAIL_OR_UNAVAILABLE"
            ),
            "sesoi_macfarlane_15_on_median_delta": (
                "PASS_RAW"
                if deltas_n and statistics.median(deltas_n) >= 15
                else "FAIL_OR_UNAVAILABLE"
            ),
            "n20_matched_met": str(len(matched) >= 20),
            "control_pool_file": ctrl_path.name,
            "caveat": (
                "Outcome B = years alive after age 45 (survival proxy), NOT near-work years. "
                "Controls = v3 pool (v2 writers ∪ stratified Wikidata scholars birth 1290–1550); "
                "not archive-verified spectacle-negative. Birth±10 match. "
                "years_after_evidence is treatment-only descriptive (no control analogue). "
                "NOT confirmatory for Macfarlane +15 near-work claim."
            ),
        }
    ]
    return matches, summary


def refresh_onsetish(census: list[dict]) -> None:
    fields = [
        "person_id",
        "name",
        "occupation_class",
        "birth_year",
        "death_year",
        "evidence_year",
        "evidence_type",
        "confidence",
    ]
    rows = [
        {k: r.get(k, "") for k in fields}
        for r in census
        if r["in_onsetish_treatment"] == "True"
    ]
    _write(OUT_ONSETISH, rows, fields)


def main() -> None:
    census = build_census()
    census_fields = [
        "person_id",
        "name",
        "wikidata_qid",
        "birth_year",
        "death_year",
        "evidence_year",
        "evidence_age",
        "evidence_type",
        "occupation_class",
        "occupation_bucket",
        "confidence",
        "roster_source",
        "in_onsetish_treatment",
        "inclusion_reason",
        "years_after_activity",
        "years_after_survival",
        "years_after_evidence",
        "years_after_source",
        "hard_dated_series",
        "years_alive_after_45",
        "n_dated_activity",
        "activity_proxy",
        "source_ref",
        "notes",
        "activity_note",
    ]
    _write(OUT_CENSUS, census, census_fields)
    summ = summarize_census(census)
    _write(OUT_CENSUS_SUM, summ, list(summ[0].keys()))
    matches, ctrl_sum = match_controls(census)
    match_fields = [
        "person_id",
        "name",
        "birth_year",
        "death_year",
        "occupation_bucket",
        "years_alive_after_45_t",
        "years_after_evidence_t",
        "n_matched_controls",
        "median_years_alive_after_45_c",
        "delta_ya45_t_minus_c_median",
        "matched_control_qids",
        "match_status",
        "n_controls_with_wd_clean",
    ]
    _write(OUT_MATCHES, matches, match_fields)
    _write(OUT_CTRL_SUM, ctrl_sum, list(ctrl_sum[0].keys()))
    refresh_onsetish(census)

    onset = [r for r in census if r["in_onsetish_treatment"] == "True"]
    measured = [r for r in onset if r["years_after_source"] != "unmeasured"]
    hard_n = sum(1 for r in onset if str(r.get("hard_dated_series")).lower() == "true")
    log(
        "census",
        f"roster={len(census)} onsetish={len(onset)} measured_years_after={len(measured)} "
        f"hard_appendix={hard_n} matched_controls="
        f"{sum(1 for m in matches if m['match_status']=='matched')}",
    )
    for s in summ:
        if s["subset"] in {
            "onsetish_with_any_years_after",
            "onsetish_activity_proxy_only",
            "onsetish_hard_appendix_only",
        }:
            log(
                "census",
                f"{s['subset']}: n={s['n_with_outcome']} median={s['median']} "
                f"mean={s['mean']} ge5={s['n_ge_5']} ge15={s['n_ge_15']}",
            )
    cs = ctrl_sum[0]
    log(
        "census",
        f"control median Δya45={cs['median_delta_ya45_t_minus_c']} "
        f"sesoi5={cs['sesoi_direction_5_on_median_delta']} "
        f"sesoi15={cs['sesoi_macfarlane_15_on_median_delta']} "
        f"n_matched={cs['n_matched_treatment']}",
    )


if __name__ == "__main__":
    main()
