#!/usr/bin/env python3
"""Process RAG (Repertorium Academicum Germanicum) bulk CSV from GitLab."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_PROCESSED, DATA_RAW, OUTPUT_LOGS, OUTPUT_TABLES, ROOT
from _utils import log

RAG_DIR_CANDIDATES = [
    DATA_RAW / "rag",
    ROOT.parent / "download_data" / "rag",
]

CAREER_EVENTS = {
    "0500 Immatrikulation",
    "0500 Promotion",
    "0500 Studium",
    "0600 Professor",
    "0600 Domherr",
    "0600 Kanoniker",
}
BIRTH_EVENT = "0130 Geburt"
DEATH_EVENT = "0200 Tod"

GLASS_PLACE_KEYWORDS = (
    "floren",
    "firenze",
    "venez",
    "vened",
    "mailand",
    "milan",
    "pisa",
    "murano",
    "nürnberg",
    "nurnberg",
    "nuremberg",
    "norimber",
)

CONTROL_PLACE_KEYWORDS = (
    "bologna",
    "paris",
    "oxford",
    "cambridge",
    "köln",
    "cologne",
    "prag",
    "praha",
    "leipzig",
    "heidelberg",
    "basel",
    "erfurt",
)


def _find_rag_dir() -> Path | None:
    for path in RAG_DIR_CANDIDATES:
        if (path / "Ereignis.csv").exists() and (path / "Person.csv").exists():
            return path
    return None


def parse_year(value) -> float | None:
    year = pd.to_numeric(value, errors="coerce")
    if pd.notna(year) and 1200 <= year <= 1800:
        return float(year)
    match = re.search(r"\b(1[0-9]{3}|2[0-9]{3})\b", str(value))
    return float(match.group(1)) if match else None


def place_label(row: pd.Series) -> str:
    for col in (
        "[Datum_Location] Location Reference",
        "[Datum_Location] Institution",
        "[Datum] Location Reference",
    ):
        val = row.get(col)
        if pd.notna(val) and str(val).strip():
            return str(val)
    return ""


def classify_place(text: str) -> str:
    low = text.lower()
    if any(k in low for k in GLASS_PLACE_KEYWORDS):
        return "glass"
    if any(k in low for k in CONTROL_PLACE_KEYWORDS):
        return "control"
    return "other"


def main() -> None:
    rag_dir = _find_rag_dir()
    if rag_dir is None:
        log("No RAG Daten/ folder with Ereignis.csv found", OUTPUT_LOGS / "fetch.log")
        return

    usecols = [
        "ID",
        "Name",
        "Ereignis",
        "[Person_Namensvariante] Person ID",
        "[Datum_Location] Date Start",
        "[Datum_Location] Date End",
        "[Datum_Location] Location Reference",
        "[Datum_Location] Institution",
        "[Datum] Date Start",
        "[Datum] Location Reference",
    ]
    chunks = []
    for chunk in pd.read_csv(rag_dir / "Ereignis.csv", chunksize=100_000, low_memory=False, usecols=usecols):
        sub = chunk[chunk["Ereignis"].isin(CAREER_EVENTS | {BIRTH_EVENT, DEATH_EVENT})]
        chunks.append(sub)
    events = pd.concat(chunks, ignore_index=True)

    events["year"] = events.apply(
        lambda r: parse_year(r.get("[Datum_Location] Date Start")) or parse_year(r.get("[Datum] Date Start")),
        axis=1,
    )
    events["place"] = events.apply(place_label, axis=1)
    events["place_group"] = events["place"].map(classify_place)
    events["person_id"] = events["[Person_Namensvariante] Person ID"]
    events.to_csv(DATA_PROCESSED / "rag_events.csv", index=False)

    careers = events[events["Ereignis"].isin(CAREER_EVENTS)].dropna(subset=["year"])
    careers = careers[(careers["year"] >= 1250) & (careers["year"] <= 1550)]
    careers.to_csv(DATA_PROCESSED / "rag_career_events_1250_1550.csv", index=False)

    # Panel: career events per half-century × place group
    careers["half_century"] = (careers["year"] // 50) * 50
    panel = (
        careers.groupby(["half_century", "place_group", "Ereignis"], as_index=False)
        .size()
        .rename(columns={"size": "n_events"})
    )
    panel.to_csv(OUTPUT_TABLES / "rag_career_panel.csv", index=False)

    # Age at first immatriculation/promotion where birth known
    births = (
        events[events["Ereignis"] == BIRTH_EVENT]
        .dropna(subset=["person_id", "year"])
        .groupby("person_id", as_index=False)["year"]
        .min()
        .rename(columns={"year": "birth_year"})
    )
    first_career = (
        events[events["Ereignis"].isin({"0500 Immatrikulation", "0500 Promotion"})]
        .dropna(subset=["person_id", "year"])
        .sort_values("year")
        .groupby("person_id", as_index=False)
        .first()
        .rename(columns={"year": "career_year"})
    )
    ages = births.merge(first_career[["person_id", "career_year", "place", "place_group"]], on="person_id", how="inner")
    ages["age_at_career"] = ages["career_year"] - ages["birth_year"]
    ages = ages[(ages["age_at_career"] >= 16) & (ages["age_at_career"] <= 90)]
    ages.to_csv(DATA_PROCESSED / "rag_careers_with_age.csv", index=False)

    pre = ages[ages["career_year"] < 1300]["age_at_career"]
    post = ages[ages["career_year"] >= 1300]["age_at_career"]
    if len(pre) >= 2 and len(post) >= 2:
        t_stat, p_val = stats.ttest_ind(post, pre, equal_var=False)
    else:
        t_stat, p_val = np.nan, np.nan

    immat = careers[careers["Ereignis"].isin({"0500 Immatrikulation", "0500 Promotion"})]
    pre_immat = immat[immat["year"] < 1300]
    post_immat = immat[immat["year"] >= 1300]

    summary_rows = [
        {
            "test": "rag_age_at_first_career_pre_vs_post_1300",
            "mean_pre_1300": round(pre.mean(), 4) if len(pre) else np.nan,
            "mean_post_1300": round(post.mean(), 4) if len(post) else np.nan,
            "share45_pre": round((pre >= 45).mean(), 4) if len(pre) else np.nan,
            "share45_post": round((post >= 45).mean(), 4) if len(post) else np.nan,
            "t_stat": round(t_stat, 4) if not np.isnan(t_stat) else np.nan,
            "p_value": round(p_val, 6) if not np.isnan(p_val) else np.nan,
            "n_pre": len(pre),
            "n_post": len(post),
            "n_career_events_1250_1550": len(careers),
            "n_immat_pre_1300": len(pre_immat),
            "n_immat_post_1300": len(post_immat),
        }
    ]
    pd.DataFrame(summary_rows).to_csv(OUTPUT_TABLES / "rag_age_ttest.csv", index=False)

    log(
        f"RAG: {len(events)} events, {len(careers)} careers 1250-1550, "
        f"{len(ages)} with age, pre1300 immat={len(pre_immat)}",
        OUTPUT_LOGS / "fetch.log",
    )


if __name__ == "__main__":
    main()
