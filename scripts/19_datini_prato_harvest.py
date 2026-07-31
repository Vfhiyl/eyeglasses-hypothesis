#!/usr/bin/env python3
"""Harvest Datini Prato catalog pages (busta / date filters). No Wikidata proxy."""
from __future__ import annotations

import argparse
import html as H
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "http://datini.archiviodistato.prato.it"


def parse_results(html: str) -> list[dict]:
    rows = []
    for m in re.finditer(
        r'href="(/la-ricerca/imageView/(ASPO\d+)/([^"?]+)\?[^"]*)"', html
    ):
        href = H.unescape(m.group(1))
        aspo, slug = m.group(2), m.group(3)
        chunk = html[max(0, m.start() - 5000) : m.end() + 800]
        plain = re.sub(r"<script[\s\S]*?</script>", " ", chunk, flags=re.I)
        plain = re.sub(r"<[^>]+>", " ", plain)
        plain = re.sub(r"\s+", " ", plain)
        dates = re.findall(r"\((\d{2}/\d{2}/\d{4})\)", plain)
        date = dates[-1] if dates else ""
        cod = re.search(r"codice (\d+)", plain)
        mitt = re.search(
            r"mittente\s+([A-ZÀ-Ú0-9 '\.,]+?)\s+destinatario", plain
        )
        prov = re.search(
            r"provenienza\s+([A-ZÀ-Ú0-9 '\.,]+?)\s+destinazione", plain
        )
        dest = re.search(r"destinazione\s+([A-ZÀ-Ú0-9 '\.,]+?)\s+data", plain)
        seg = re.search(r"busta\s+([\w\.]+),\s*inserto\s+([\w\.]+)", plain)
        rows.append(
            dict(
                aspo_id=aspo,
                slug=slug,
                date=date,
                codice=cod.group(1) if cod else "",
                mittente=mitt.group(1).strip() if mitt else "",
                provenienza=prov.group(1).strip() if prov else "",
                destinazione=dest.group(1).strip() if dest else "",
                busta=seg.group(1) if seg else "",
                inserto=seg.group(2) if seg else "",
                imageView=href,
            )
        )
    seen, out = set(), []
    for r in rows:
        if r["aspo_id"] in seen:
            continue
        seen.add(r["aspo_id"])
        out.append(r)
    return out


def harvest(session: requests.Session, bustaregistro: str, out_csv: Path) -> pd.DataFrame:
    html = session.post(
        BASE + "/la-ricerca/archivio/search",
        data={"query": "", "bustaregistro": bustaregistro},
        timeout=90,
    ).text
    n = int(re.search(r"Esito ricerca\s+(\d+)", html).group(1))
    npages = int(re.search(r"Pagina\s+1\s+di\s+(\d+)", html).group(1))
    print(f"busta {bustaregistro}: n={n} pages={npages}")
    all_rows = parse_results(html)
    for pi in range(1, npages):
        time.sleep(0.5)
        q = {
            "archiveName": "",
            "startPage": pi * 20,
            "query": "",
            "jsonVal": json.dumps(
                {
                    "jsonVal": {
                        "startDate": "",
                        "endDate": "",
                        "fieldDate": "dataNormal",
                        "bustaregistro": bustaregistro,
                    }
                },
                separators=(",", ":"),
            ),
            "orderBy": "",
            "orderType": "asc",
        }
        html = session.get(
            BASE + "/la-ricerca/archivio/search", params=q, timeout=90
        ).text
        rows = parse_results(html)
        print(f"  p{pi} {len(rows)}")
        all_rows.extend(rows)
    df = pd.DataFrame(all_rows).drop_duplicates("aspo_id")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"wrote {len(df)} -> {out_csv}")
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--busta", required=True)
    ap.add_argument(
        "--out",
        default=None,
        help="CSV path (default outputs/tables/datini_busta{N}_catalog.csv)",
    )
    args = ap.parse_args()
    out = Path(args.out or f"outputs/tables/datini_busta{args.busta}_catalog.csv")
    s = requests.Session()
    s.headers["User-Agent"] = "eyeglasses-hypothesis/b1"
    s.get(BASE + "/la-ricerca/", timeout=30)
    harvest(s, args.busta, out)


if __name__ == "__main__":
    main()
