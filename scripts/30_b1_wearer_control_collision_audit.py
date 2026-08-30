#!/usr/bin/env python3
"""Wearer–control collision audit (Pass CX/CY).

Flags named wearers still marked usable as spectacle-negative controls.

Match modes:
1. exact_qid — wearer wikidata_qid == control qid
2. name_lifespan — normalized name tokens equal, or strong fuzzy
   (birth±2, death±5 when both known, shared token length≥5)

Active = labor use_in_primary OR output_eligible.
Writes CSV/MD; returns active collision rows for verdict wiring.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEARERS = ROOT / "data/curated/b1_named_wearers_candidates_new.csv"
CHRONO = ROOT / "data/curated/b1_control_nearwork_chrono_curated.csv"
ELIG = ROOT / "data/curated/b1_control_output_eligibility.csv"
OUT = ROOT / "outputs/tables/b1_wearer_control_collision_audit.csv"
OUT_MD = ROOT / "outputs/tables/b1_wearer_control_collision_audit.md"

_STOP = {
    "of",
    "the",
    "de",
    "di",
    "da",
    "del",
    "della",
    "van",
    "von",
    "and",
    "pope",
    "saint",
    "st",
    "le",
    "la",
    "du",
    "des",
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "jr",
    "sr",
    "younger",
    "elder",
    "king",
    "duke",
    "count",
    "lord",
    "sir",
    "cardinal",
    "bishop",
}

# Given names ≥5 letters must not alone drive name_lifespan hits
# (Pass DD: George Washington ≠ George Romney Q371280).
_GIVEN_NAME = {
    "george",
    "william",
    "thomas",
    "charles",
    "robert",
    "richard",
    "edward",
    "francis",
    "philip",
    "pierre",
    "nicolas",
    "francesco",
    "giovanni",
    "antonio",
    "elizabeth",
    "catherine",
    "margaret",
    "henry",
    "james",
    "joseph",
    "samuel",
    "benjamin",
    "alexander",
    "frederick",
    "albert",
    "louis",
    "marie",
    "maria",
}


def _truthy(v: str | None) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes"}


def _yi(v: str | None) -> int | None:
    try:
        return int(str(v).strip()) if v not in (None, "") else None
    except ValueError:
        return None


def _norm_tokens(name: str | None) -> list[str]:
    s = re.sub(r"\([^)]*\)", "", name or "")
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)
    )
    s = s.lower()
    s = re.sub(r"[^a-z\s]", " ", s)
    return [t for t in s.split() if t and t not in _STOP and len(t) > 2]


def run_audit() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return (active_collisions, inactive_alias_notes)."""
    chrono = {r["qid"]: r for r in csv.DictReader(CHRONO.open(encoding="utf-8"))}
    elig = {r["qid"]: r for r in csv.DictReader(ELIG.open(encoding="utf-8"))}
    wearers = list(csv.DictReader(WEARERS.open(encoding="utf-8")))

    active: list[dict[str, str]] = []
    inactive: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(
        bucket: list[dict[str, str]],
        *,
        pid: str,
        wname: str,
        wqid: str,
        cq: str,
        cname: str,
        et: str,
        labor: bool,
        output: bool,
        mode: str,
    ) -> None:
        key = (pid, cq, mode)
        if key in seen:
            return
        seen.add(key)
        bucket.append(
            {
                "wearer_person_id": pid,
                "wearer_name": wname,
                "wearer_qid": wqid,
                "control_qid": cq,
                "control_name": cname,
                "evidence_type": et,
                "labor_use_in_primary": str(labor),
                "output_eligible": str(output),
                "match_mode": mode,
                "severity": (
                    "COLLISION_ACTIVE_CONTROL"
                    if (labor or output)
                    else "INACTIVE_ALIAS_NOTED"
                ),
            }
        )

    for w in wearers:
        pid = w.get("person_id") or ""
        wname = w.get("name") or ""
        wqid = (w.get("wikidata_qid") or w.get("qid") or "").strip()
        et = w.get("evidence_type") or ""
        wb, wd = _yi(w.get("birth_year")), _yi(w.get("death_year"))
        wtok = _norm_tokens(wname)
        wkey = " ".join(sorted(wtok))

        # 1) exact QID
        if wqid.startswith("Q"):
            c = chrono.get(wqid)
            e = elig.get(wqid)
            if c or e:
                labor = bool(c) and _truthy((c or {}).get("use_in_primary"))
                output = bool(e) and _truthy((e or {}).get("output_eligible"))
                cname = (c or e or {}).get("name") or ""
                bucket = active if (labor or output) else inactive
                add(
                    bucket,
                    pid=pid,
                    wname=wname,
                    wqid=wqid,
                    cq=wqid,
                    cname=cname,
                    et=et,
                    labor=labor,
                    output=output,
                    mode="exact_qid",
                )

        # 2) name / lifespan (including cross-QID same person)
        for cq, c in chrono.items():
            if wqid and cq == wqid:
                continue
            ctok = _norm_tokens(c.get("name"))
            ckey = " ".join(sorted(ctok))
            cb, cd = _yi(c.get("birth_year")), _yi(c.get("death_year"))
            exact_name = bool(wkey) and wkey == ckey
            strong = False
            if wb is not None and cb is not None and abs(wb - cb) <= 2:
                death_ok = True
                if wd is not None and cd is not None:
                    death_ok = abs(wd - cd) <= 5
                # Prefer surname-like overlap: drop common given names; require
                # ≥1 shared non-given token (len≥5) or ≥2 shared tokens total.
                shared = set(wtok) & set(ctok)
                inter = {t for t in shared if len(t) >= 5 and t not in _GIVEN_NAME}
                strong = death_ok and (bool(inter) or len(shared) >= 2)
            if not exact_name and not strong:
                continue
            e = elig.get(cq)
            labor = _truthy(c.get("use_in_primary"))
            output = bool(e) and _truthy(e.get("output_eligible"))
            mode = "name_exact" if exact_name else "name_lifespan"
            bucket = active if (labor or output) else inactive
            add(
                bucket,
                pid=pid,
                wname=wname,
                wqid=wqid,
                cq=cq,
                cname=c.get("name") or "",
                et=et,
                labor=labor,
                output=output,
                mode=mode,
            )

    return active, inactive


def write_outputs(
    active: list[dict[str, str]], inactive: list[dict[str, str]]
) -> None:
    fields = [
        "wearer_person_id",
        "wearer_name",
        "wearer_qid",
        "control_qid",
        "control_name",
        "evidence_type",
        "labor_use_in_primary",
        "output_eligible",
        "match_mode",
        "severity",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(active + inactive)

    lines = [
        "# B1 wearer–control collision audit",
        "",
        "Active = named wearer still `use_in_primary` or `output_eligible` as control.",
        "Match modes: `exact_qid`, `name_exact`, `name_lifespan`.",
        "",
        f"**Active collisions:** {len(active)}",
        f"**Inactive aliases noted:** {len(inactive)}",
        "",
    ]
    if active:
        lines += [
            "## Active (must be 0)",
            "",
            "| person_id | control_qid | mode | labor | output |",
            "|-----------|-------------|------|-------|--------|",
        ]
        for r in active:
            lines.append(
                f"| {r['wearer_person_id']} | {r['control_qid']} | {r['match_mode']} | "
                f"{r['labor_use_in_primary']} | {r['output_eligible']} |"
            )
        lines.append("")
    else:
        lines.append("No active collisions.")
        lines.append("")
    if inactive:
        lines += [
            "## Inactive aliases (informational)",
            "",
            "| person_id | wearer_qid | control_qid | mode |",
            "|-----------|------------|-------------|------|",
        ]
        for r in inactive:
            lines.append(
                f"| {r['wearer_person_id']} | {r['wearer_qid']} | {r['control_qid']} | "
                f"{r['match_mode']} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    active, inactive = run_audit()
    write_outputs(active, inactive)
    print("wrote", OUT)
    print("wrote", OUT_MD)
    print("active_collisions", len(active))
    print("inactive_aliases", len(inactive))
    for r in active:
        print(" ACTIVE", r["wearer_person_id"], r["control_qid"], r["match_mode"])
    for r in inactive:
        print(" note", r["wearer_person_id"], r["control_qid"], r["match_mode"])


if __name__ == "__main__":
    main()
