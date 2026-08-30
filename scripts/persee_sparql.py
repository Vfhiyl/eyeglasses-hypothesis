#!/usr/bin/env python3
"""CLI for Persée SPARQL (data.persee.fr), default via local CONNECT gateway.

Examples:
  python3 scripts/persee_sparql.py --smoke
  python3 scripts/persee_sparql.py --person Hesselin --limit 20
  python3 scripts/persee_sparql.py --query 'SELECT ?p WHERE { ?p a foaf:Person } LIMIT 5'
  python3 scripts/persee_sparql.py --person Dollfus --docs --out /tmp/dollfus.json
  python3 scripts/persee_sparql.py --no-proxy --smoke
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _persee_sparql import (  # noqa: E402
    DEFAULT_PROXY,
    bindings_to_rows,
    documents_for_person_uri,
    log,
    prefix_block,
    query,
    search_persons,
    smoke,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Persée SPARQL via local gateway (default)")
    ap.add_argument("--smoke", action="store_true", help="tiny SELECT (1 AS ?x)")
    ap.add_argument("--person", help="substring search on foaf:Person foaf:name")
    ap.add_argument(
        "--docs",
        action="store_true",
        help="with --person: also pull docs linked to each matched person URI",
    )
    ap.add_argument("--query", help="raw SPARQL SELECT (prefixes optional)")
    ap.add_argument("--query-file", type=Path, help="read SPARQL from file")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--method", choices=("GET", "POST"), default="GET")
    ap.add_argument(
        "--proxy",
        default=DEFAULT_PROXY,
        help=f"CONNECT proxy (default {DEFAULT_PROXY})",
    )
    ap.add_argument("--no-proxy", action="store_true", help="direct connect, ignore --proxy")
    ap.add_argument(
        "--insecure",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="TLS verify off (default on for local gateway)",
    )
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--out", type=Path, help="write JSON result")
    ap.add_argument(
        "--add-prefixes",
        action="store_true",
        help="prepend common PREFIX block to --query / --query-file",
    )
    args = ap.parse_args()

    proxy = None if args.no_proxy else args.proxy
    log(f"proxy={proxy or '(none)'} method={args.method}")

    if args.smoke:
        ok, detail = smoke(proxy=proxy, insecure=args.insecure, method=args.method)
        print(json.dumps({"ok": ok, "detail": detail}, ensure_ascii=False))
        return 0 if ok else 1

    payload: object
    if args.person:
        people = search_persons(
            args.person,
            limit=args.limit,
            proxy=proxy,
            insecure=args.insecure,
            method=args.method,
            timeout=args.timeout,
        )
        out: dict[str, object] = {"person_query": args.person, "people": people}
        if args.docs:
            docs_by: dict[str, list[dict[str, str]]] = {}
            for row in people:
                uri = row.get("person", "")
                if not uri:
                    continue
                docs_by[uri] = documents_for_person_uri(
                    uri,
                    limit=args.limit,
                    proxy=proxy,
                    insecure=args.insecure,
                    method=args.method,
                    timeout=args.timeout,
                )
            out["documents_by_person"] = docs_by
        payload = out
    elif args.query or args.query_file:
        q = args.query or ""
        if args.query_file:
            q = args.query_file.read_text(encoding="utf-8")
        if args.add_prefixes:
            q = prefix_block() + "\n" + q
        raw = query(
            q,
            proxy=proxy,
            insecure=args.insecure,
            method=args.method,
            timeout=args.timeout,
        )
        payload = {"rows": bindings_to_rows(raw), "raw": raw}
    else:
        ap.error("need --smoke, --person, --query, or --query-file")
        return 2

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        log(f"wrote {args.out}")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
