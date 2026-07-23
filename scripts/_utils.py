"""Shared utilities for the eyeglasses-hypothesis pipeline."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

from _paths import CONFIG


def load_yaml(name: str) -> dict:
    with open(CONFIG / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


_ALIASES_CACHE: dict | None = None


def _get_aliases() -> dict:
    global _ALIASES_CACHE
    if _ALIASES_CACHE is None:
        base_mapping = {
            "Firenze": "Florence",
            "Venezia": "Venice",
            "Milano": "Milan",
            "Nurnberg": "Nuremberg",
            "Bologna": "Bologna",
            "Paris": "Paris",
            "Oxford": "Oxford",
            "Cambridge": "Cambridge",
            "Koln": "Cologne",
            "Praha": "Prague",
            "Krakow": "Krakow",
            "Salamanca": "Salamanca",
            "Padova": "Padua",
            "Pisa": "Pisa",
            "Roma": "Rome",
            "Torino": "Turin",
            "Lyon": "Lyon",
            "Leiden": "Leiden",
            "Amsterdam": "Amsterdam",
            "Wien": "Vienna",
            "Strasbourg": "Strasbourg",
            "Basel": "Basel",
            "Geneve": "Geneva",
            "Heidelberg": "Heidelberg",
            "Leipzig": "Leipzig",
            "Utrecht": "Utrecht",
            "Groningen": "Groningen",
            "Valencia": "Valencia",
            "Barcelona": "Barcelona",
            "Sevilla": "Seville",
            "Toledo": "Toledo",
            "Valladolid": "Valladolid",
            "Madrid": "Madrid",
            "Lisboa": "Lisbon",
            "Coimbra": "Coimbra",
            "Edinburgh": "Edinburgh",
            "Dublin": "Dublin",
            "London": "London",
            "Munchen": "Munich",
            "Halle": "Halle",
            "Jena": "Jena",
            "Wittenberg": "Wittenberg",
            "Freiburg-im-Breisgau": "Freiburg",
            "Tubingen": "Tubingen",
            "Gottingen": "Gottingen",
            "Uppsala": "Uppsala",
            "Kobenhavn": "Copenhagen",
            "Bruxelles": "Brussels",
            "Leuven": "Leuven",
            "Liege": "Liege",
            "Montpellier": "Montpellier",
            "Toulouse": "Toulouse",
            "Bordeaux": "Bordeaux",
            "Rouen": "Rouen",
            "Caen": "Caen",
            "Dijon": "Dijon",
            "Grenoble": "Grenoble",
            "Ferrara": "Ferrara",
            "Modena": "Modena",
            "Parma": "Parma",
            "Siena": "Siena",
            "Napoli": "Naples",
            "Messina": "Messina",
            "Palermo": "Palermo",
            "Murano": "Murano",
        }
        base_mapping.update(load_yaml("cities.yaml").get("aliases", {}))
        _ALIASES_CACHE = base_mapping
    return _ALIASES_CACHE


def normalize_city(col_name: str) -> str:
    """FirenzeITA -> Florence, VeneziaITA -> Venice."""
    if col_name is None or (isinstance(col_name, float) and pd.isna(col_name)):
        return ""
    base = re.sub(r"[A-Z]{3}$", "", str(col_name))
    return _get_aliases().get(base, base)


def build_geonames_city_map(imprints: pd.DataFrame) -> dict:
    """Most common cleaned place name per geonames_id."""

    def clean(s: str) -> str:
        if pd.isna(s):
            return ""
        text = str(s).strip()
        text = re.sub(r"^\[+", "", text)
        text = re.sub(r"\]+$", "", text)
        return text.split(",")[0].split(";")[0].strip()

    has = imprints[imprints["geonames_id"].notna()].copy()
    has["place_clean"] = has["imprint_place"].map(clean)
    canon = has.groupby("geonames_id")["place_clean"].agg(lambda x: x.value_counts().index[0])
    return {gid: normalize_city(city) for gid, city in canon.items()}


def is_config_glass_city(city: str, glass_names: set[str]) -> bool:
    """Exact match against configured glass centers only."""
    return str(city).lower() in glass_names


def melt_city_year_wide(csv_path: Path, value_name: str) -> pd.DataFrame:
    """Convert de la Croix wide year×city CSV to long format."""
    df = pd.read_csv(csv_path)
    year_col = df.columns[0]
    df = df.rename(columns={year_col: "year"})
    long = df.melt(id_vars="year", var_name="city_raw", value_name=value_name)
    aliases = _get_aliases()
    long["city"] = long["city_raw"].str.replace(r"[A-Z]{3}$", "", regex=True).map(
        lambda x: aliases.get(x, x)
    )
    long["year"] = pd.to_numeric(long["year"], errors="coerce")
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce").fillna(0)
    long = long[long["year"].between(1200, 1799)]
    return long.drop(columns=["city_raw"])


def get_city_config() -> pd.DataFrame:
    cfg = load_yaml("cities.yaml")
    rows = []
    for group, is_glass in [("glass_centers", True), ("control_cities", False)]:
        for c in cfg.get(group, []):
            rows.append(
                {
                    "city": c["city"],
                    "glass_center": is_glass,
                    "has_university": c.get("has_university", False),
                    "university_founded": c.get("university_founded"),
                    "year_first_guild": c.get("year_first_guild"),
                    "year_first_spectacles": c.get("year_first_spectacles"),
                    "region": c.get("region"),
                    "population_1500": c.get("population_1500"),
                }
            )
    return pd.DataFrame(rows)


def log(msg: str, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)
