#!/usr/bin/env python3
"""Revert outcome-aware curation edits from passes BC..FI (audit 2026-08-12).

The 2026-08-06..08-10 passes hand-edited control chronologies in one
direction only (shorten / demote controls whose post-45 span exceeded the
wearer's), which manufactured the labor SESOI+5 PASS_RAW. This script
deterministically reverts the two in-place edit classes:

  1. tip-strips: notes record "Pass XX tip-strip last A->B" (or A→B);
     restore last_nearwork_year to A when the current value is B.
  2. pass-era demotions: use_in_primary=False rows whose stated reason is
     the control's long span / tip=death ("outlier", "continuum") rather
     than contamination or data quality; restore use_in_primary=True.
     Contamination demotions (control was a documented wearer: Locke,
     Priestley, Burke, Cusa, Pius II alias, Rene of Anjou flip) and
     pre-pass data-quality demotions (thin pins, placeholder lifespans,
     dies-young rows from rounds R4/R6/R7) are kept as-is.
  3. output-years strips: dated pins dropped from
     b1_control_output_years_curated.csv (death-year pins); restored from
     the note text / pre-pass .bak snapshots.

Overlay/exclude files (b1_output_strict_control_overlays.csv,
b1_output_control_excludes.csv) are left on disk as historical record;
scripts 25/27 no longer apply them.

Idempotent: rows already tagged AUDIT-RESTORE-2026-08-12 are skipped.
Writes outputs/tables/b1_audit_restore_log_2026-08-12.csv.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_CURATED, OUTPUT_TABLES

CHRONO = DATA_CURATED / "b1_control_nearwork_chrono_curated.csv"
OUT_YEARS = DATA_CURATED / "b1_control_output_years_curated.csv"
OUT_ELIG = DATA_CURATED / "b1_control_output_eligibility.csv"
LOG = OUTPUT_TABLES / "b1_audit_restore_log_2026-08-12.csv"

TAG = "AUDIT-RESTORE-2026-08-12"

STRIP_PAT = re.compile(r"tip.?strip.*?(\d{4})\s*(?:→|->)\s*(\d{4})", re.IGNORECASE)

# Labor chrono: pass-era use_in_primary=False rows whose reason is the
# control's long post-45 span / tip=death (outcome-aware; revert to True).
LABOR_DEMOTIONS_REVERT = {
    "Q1217669": "Pass FF EXCLUDE tip=death outlier (Cicco Simonetta)",
    "Q289285": "Pass FF EXCLUDE tip=death continuum (Filippo Maria Visconti)",
    "Q312304": "Pass FF EXCLUDE tip=death outlier (Alfonso V of Aragon)",
    "Q3388274": "Pass FA EXCLUDE tip=death continuum (Pigello Portinari)",
    "Q3742149": "Pass FC EXCLUDE span outlier (Felice Figliucci)",
    "Q5392534": "Pass FE EXCLUDE tip=death outlier (Ermolao Barbaro the Elder)",
    "Q715054": "Pass FE EXCLUDE tip=death continuum (Borso d'Este)",
    "Q9381": "Pass FB EXCLUDE tip=death outlier (Adam Smith)",
    "Q700422": "Pass FC EXCLUDE tip=death continuum (Henry Oldenburg)",
}

# Output-years file: death-year pins dropped by passes EL/EO/ES/ET (values
# recorded in the row notes; Marienwerder/Dinkelsbuehl cross-checked against
# .bak_pass_es_20260807 which still carries 1417 / 1433).
OUTPUT_PIN_RESTORE = {
    "Q676049": 1694,  # Tillotson — Pass ET dropped death-year 1694
    "Q18917181": 1784,  # Hanbury — Pass EO dropped death tip 1784
    "Q18530776": 1791,  # Champion — Pass EO dropped death tip 1791
    "Q18576880": 1784,  # Oliver — Pass EO dropped death tip 1784
    "Q259132": 1638,  # Burton — Pass EL dropped 1638 tip
    "Q104914": 1417,  # Marienwerder — Pass ES replaced 1417 with 1404
    "Q95506": 1433,  # Dinkelsbuehl — Pass ES replaced 1433 with 1427
    # Born-stripped rows: created during passes with the death-tip already
    # dropped, drop recorded in notes ("drop death tip YYYY").
    "Q18810672": 1709,  # Haistwell — Pass CM dropped death tip 1709
    "Q41784687": 1708,  # Heathcote — Pass CM dropped death tip 1708
    "Q99371": 1638,  # Besoldus — Pass BY dropped death tip
    "Q761023": 1661,  # Buchner — Pass BY dropped death tip 1661
    "Q570021": 1410,  # Bonet — Pass CG dropped death tip 1410
    "Q457915": 1406,  # Deschamps — Pass CG dropped death tip 1406 ("post-Philippe")
    "Q1413816": 1518,  # Beroaldo the Younger — Pass CL dropped death tip 1518
}

# Output eligibility: passes BC/BD/BE/BF/BH/BI set output_eligible=False on
# 37 controls with reasons of the form "<name> long densify (span45~X)
# mismatches <wearer>; retired/replaced" — i.e. the control was removed
# BECAUSE its post-45 span exceeded the wearer's. One row even records
# "Pass BX tried rene_anjou unlock -> med 5->4 SESOI FAIL; reverted".
# Outcome-aware; revert to True. Contamination (CX/CR/CY), structural
# non_textual_or_admin, unclassified-fallback and BM death<45 rows stay.
ELIG_REVERT_PAT = re.compile(r"^Pass (BC|BD|BE|BF|BH|BI):")

# Labor chrono rows created during passes with last_nearwork_year already
# stripped (no arrow notation; drop recorded in notes / death_year column).
LABOR_BORN_STRIPPED = {
    "Q18917181": 1784,  # Hanbury — "drop death tip 1784; keep 1770 living pin"
    "Q18530776": 1791,  # Champion — "drop death tip 1791; keep 1774 living pin"
    "Q18576880": 1784,  # Oliver — "drop death tip 1784; keep 1770 living pin"
    "Q761023": 1661,  # Buchner — "drop death tip. ya45≈14" (death 1661)
    "Q1413816": 1518,  # Beroaldo the Younger — "ya45≈0 (drop death tip)" (death 1518)
}


def _read(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r), list(r.fieldnames or [])


def _write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    log_rows: list[dict] = []

    # --- 1+2: labor chrono ---
    rows, fields = _read(CHRONO)
    n_strip = n_demote = 0
    for r in rows:
        notes = r.get("notes") or ""
        if TAG in notes:
            continue
        joined = " | ".join(str(v) for v in r.values() if v)
        m = STRIP_PAT.search(joined)
        if m:
            orig, stripped = m.group(1), m.group(2)
            if (r.get("last_nearwork_year") or "").strip() == stripped:
                r["last_nearwork_year"] = orig
                r["notes"] = f"{notes} | {TAG}: tip-strip reverted {stripped}->{orig}"
                notes = r["notes"]
                n_strip += 1
                log_rows.append(
                    {
                        "file": CHRONO.name,
                        "qid": r.get("qid", ""),
                        "name": r.get("name", ""),
                        "field": "last_nearwork_year",
                        "old": stripped,
                        "new": orig,
                        "reason": "one-directional tip-strip reverted",
                    }
                )
        q = (r.get("qid") or "").strip()
        if q in LABOR_BORN_STRIPPED:
            target = str(LABOR_BORN_STRIPPED[q])
            cur = (r.get("last_nearwork_year") or "").strip()
            if cur != target:
                r["last_nearwork_year"] = target
                r["notes"] = (
                    f"{r.get('notes') or ''} | {TAG}: born-stripped death tip "
                    f"restored {cur}->{target}"
                )
                n_strip += 1
                log_rows.append(
                    {
                        "file": CHRONO.name,
                        "qid": q,
                        "name": r.get("name", ""),
                        "field": "last_nearwork_year",
                        "old": cur,
                        "new": target,
                        "reason": "born-stripped death tip restored (drop noted at row creation)",
                    }
                )
        if q in LABOR_DEMOTIONS_REVERT:
            use = (r.get("use_in_primary") or "").strip().lower()
            if use in {"false", "0", "no"}:
                r["use_in_primary"] = "True"
                r["notes"] = (
                    f"{r.get('notes') or ''} | {TAG}: outcome-aware demotion reverted "
                    f"({LABOR_DEMOTIONS_REVERT[q]})"
                )
                n_demote += 1
                log_rows.append(
                    {
                        "file": CHRONO.name,
                        "qid": q,
                        "name": r.get("name", ""),
                        "field": "use_in_primary",
                        "old": "False",
                        "new": "True",
                        "reason": LABOR_DEMOTIONS_REVERT[q],
                    }
                )
    _write(CHRONO, rows, fields)
    print(f"labor chrono: tip-strips reverted={n_strip}; demotions reverted={n_demote}")

    # --- 3: output years ---
    rows, fields = _read(OUT_YEARS)
    n_pins = 0
    for r in rows:
        q = (r.get("qid") or "").strip()
        if q not in OUTPUT_PIN_RESTORE:
            continue
        notes = r.get("notes") or ""
        if TAG in notes:
            continue
        year = OUTPUT_PIN_RESTORE[q]
        ys = [int(float(p)) for p in (r.get("years") or "").split(";") if p.strip()]
        if year in ys:
            continue
        old = ";".join(str(y) for y in ys)
        ys = sorted(set(ys + [year]))
        r["years"] = ";".join(str(y) for y in ys)
        r["n_pins"] = str(len(ys))
        r["notes"] = f"{notes} | {TAG}: dropped pin {year} restored"
        n_pins += 1
        log_rows.append(
            {
                "file": OUT_YEARS.name,
                "qid": q,
                "name": r.get("name", ""),
                "field": "years",
                "old": old,
                "new": r["years"],
                "reason": "death-tip pin dropped by pass EL/EO/ES/ET restored",
            }
        )
    _write(OUT_YEARS, rows, fields)
    print(f"output years: pins restored={n_pins}")

    # --- 4: output eligibility ---
    rows, fields = _read(OUT_ELIG)
    n_elig = 0
    for r in rows:
        reason = r.get("eligibility_reason") or ""
        if TAG in reason:
            continue
        use = (r.get("output_eligible") or "").strip().lower()
        if use in {"false", "0", "no"} and ELIG_REVERT_PAT.match(reason):
            r["output_eligible"] = "True"
            r["eligibility_reason"] = (
                f"{reason} | {TAG}: outcome-aware eligibility demotion reverted "
                f"(control retired for long span vs wearer)"
            )
            n_elig += 1
            log_rows.append(
                {
                    "file": OUT_ELIG.name,
                    "qid": r.get("qid", ""),
                    "name": r.get("name", ""),
                    "field": "output_eligible",
                    "old": "False",
                    "new": "True",
                    "reason": reason[:160],
                }
            )
    _write(OUT_ELIG, rows, fields)
    print(f"output eligibility: demotions reverted={n_elig}")

    # Rebuild the full log from TAG markers so repeated runs never lose rows.
    full_log: list[dict] = []
    tag_pat = re.compile(rf"{TAG}: ([^|]+)")
    for path, note_field in ((CHRONO, "notes"), (OUT_YEARS, "notes"), (OUT_ELIG, "eligibility_reason")):
        for r in _read(path)[0]:
            notes = r.get(note_field) or ""
            for m in tag_pat.finditer(notes):
                if path is OUT_ELIG:
                    field = "output_eligible"
                elif path is OUT_YEARS:
                    field = "years"
                elif "demotion" in m.group(1):
                    field = "use_in_primary"
                else:
                    field = "last_nearwork_year"
                full_log.append(
                    {
                        "file": path.name,
                        "qid": r.get("qid", ""),
                        "name": r.get("name", ""),
                        "field": field,
                        "restore": m.group(1).strip(),
                    }
                )
    with LOG.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["file", "qid", "name", "field", "restore"],
            lineterminator="\n",
        )
        w.writeheader()
        w.writerows(full_log)
    print(f"wrote {LOG} ({len(full_log)} rows; this run changed {len(log_rows)})")


if __name__ == "__main__":
    main()
