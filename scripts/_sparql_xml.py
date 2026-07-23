"""Parse Wikidata SPARQL XML results (proxies often ignore format=csv)."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

NS = {"sr": "http://www.w3.org/2005/sparql-results#"}


def is_sparql_xml(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 80:
        return False
    head = path.read_bytes()[:256].lstrip()
    return head.startswith(b"<?xml") or head.startswith(b"<sparql")


def is_complete_sparql_xml(path: Path) -> bool:
    if not is_sparql_xml(path):
        return False
    tail = path.read_bytes()[-512:]
    return b"</sparql>" in tail or b"</results>" in tail


def sparql_xml_to_dataframe(path: Path) -> pd.DataFrame:
    root = ET.parse(path).getroot()
    vars_ = [v.get("name") for v in root.findall("sr:head/sr:variable", NS)]
    rows: list[dict[str, str]] = []
    for result in root.findall("sr:results/sr:result", NS):
        row: dict[str, str] = {}
        for binding in result.findall("sr:binding", NS):
            name = binding.get("name") or ""
            uri = binding.find("sr:uri", NS)
            lit = binding.find("sr:literal", NS)
            if uri is not None and uri.text:
                row[name] = uri.text
            elif lit is not None and lit.text:
                row[name] = lit.text
        if row:
            rows.append(row)
    if not rows:
        return pd.DataFrame(columns=vars_ or None)
    df = pd.DataFrame(rows)
    for col in vars_:
        if col not in df.columns:
            df[col] = pd.NA
    return df[vars_]


def sparql_xml_to_csv(src: Path, dest: Path) -> bool:
    df = sparql_xml_to_dataframe(src)
    if df.empty:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    return dest.stat().st_size > 200
