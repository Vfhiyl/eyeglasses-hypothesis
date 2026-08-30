#!/usr/bin/env python3
"""CLI for Persée portal fulltext search (www.persee.fr/search/page).

Default proxy: http://127.0.0.1:12309

Examples:
  python3 scripts/persee_search.py --smoke
  python3 scripts/persee_search.py --query Hesselin --pages 3
  python3 scripts/persee_search.py --query 'Cleux OR Cleuz' --pages 2 --out /tmp/cleux.json
  python3 scripts/persee_search.py --no-proxy --query Dollfus --pages 1
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import DATA_RAW  # noqa: E402
from _persee_search import DEFAULT_PROXY, log, search, smoke  # noqa: E402

OUT_DIR = DATA_RAW / "persee_search"


def _slug(q: str) -> str:
    s = "".join(c if c.isalnum() else "_" for c in q.strip())[:80].strip("_")
    return s or "query"


def main() -> int:
    ap = argparse.ArgumentParser(description="Persée www search/page via local gateway")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--query", "-q", help="search query (same as site q=)")
    ap.add_argument("--pages", type=int, default=1, help="number of XHR pages to fetch")
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--ta", default="article", help="type filter (default article)")
    ap.add_argument("--no-total", action="store_true", help="skip full-page total lookup")
    ap.add_argument("--proxy", default=DEFAULT_PROXY)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument(
        "--insecure",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="TLS verify off (default on for local gateway)",
    )
    ap.add_argument("--cookie", default=None, help="optional Cookie header")
    ap.add_argument("--timeout", type=float, default=45.0)
    ap.add_argument("--sleep", type=float, default=0.4, help="pause between pages")
    ap.add_argument("--out", type=Path, help="write JSON")
    args = ap.parse_args()

    proxy = None if args.no_proxy else args.proxy
    log(f"proxy={proxy or '(none)'}")

    if args.smoke:
        ok, detail = smoke(proxy=proxy, insecure=args.insecure)
        print(json.dumps({"ok": ok, "detail": detail}, ensure_ascii=False))
        return 0 if ok else 1

    if not args.query:
        ap.error("need --query or --smoke")
        return 2

    payload = search(
        args.query,
        pages=args.pages,
        start_page=args.start_page,
        ta=args.ta,
        include_total=not args.no_total,
        proxy=proxy,
        insecure=args.insecure,
        cookie=args.cookie,
        timeout=args.timeout,
        sleep_s=args.sleep,
    )
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    out = args.out
    if out is None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / (
            f"{_slug(args.query)}_p{args.start_page}"
            f"-{args.start_page + args.pages - 1}.json"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    log(f"wrote {out} n={payload.get('n_results')} total={payload.get('total')}")

    results = payload.get("results")
    if isinstance(results, list):
        for item in results[:8]:
            if not isinstance(item, dict):
                continue
            print(
                f"- {str(item.get('year', '')):<20} {str(item.get('title', ''))[:90]}\n"
                f"  {item.get('url', '')}\n"
                f"  … {str(item.get('snippet') or '')[:160]}"
            )
    print(f"# total={payload.get('total')} fetched={payload.get('n_results')} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
