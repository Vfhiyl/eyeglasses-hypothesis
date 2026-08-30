#!/usr/bin/env python3
"""Download Persée PDFs via ALTCHA PoW (default: local CONNECT gateway).

Examples:
  python3 scripts/persee_pdf.py --smoke
  python3 scripts/persee_pdf.py \\
    https://www.persee.fr/doc/pharm_0035-2349_1972_num_60_215_7165
  python3 scripts/persee_pdf.py pharm_0035-2349_1972_num_60_215_7165 -o /tmp/x.pdf
  python3 scripts/persee_pdf.py --no-proxy DOC_URL
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _paths import DATA_RAW  # noqa: E402
from _persee_pdf import DEFAULT_PROXY, doc_id_from_url, doc_page_url, download_pdf, smoke  # noqa: E402
from _persee_sparql import log  # noqa: E402

OUT_DIR = DATA_RAW / "persee_pdf"


def main() -> int:
    ap = argparse.ArgumentParser(description="Persée docAsPDF via ALTCHA + gateway")
    ap.add_argument("docs", nargs="*", help="doc URL, docAsPDF URL, or document id")
    ap.add_argument("--smoke", action="store_true", help="challenge+PoW only")
    ap.add_argument("-o", "--output", type=Path, help="output PDF (single doc only)")
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--proxy", default=DEFAULT_PROXY)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument(
        "--insecure",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="TLS verify off (default on for local gateway)",
    )
    ap.add_argument("--cookie", default=None, help="optional extra Cookie header")
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args()

    proxy = None if args.no_proxy else args.proxy
    log(f"proxy={proxy or '(none)'}")

    if args.smoke:
        ok, detail = smoke(proxy=proxy, insecure=args.insecure)
        print(json.dumps({"ok": ok, "detail": detail}, ensure_ascii=False))
        return 0 if ok else 1

    if not args.docs:
        ap.error("need doc URL/id or --smoke")
        return 2

    if args.output is not None and len(args.docs) != 1:
        ap.error("--output only valid with a single document")
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ok_n = 0
    for raw in args.docs:
        page = doc_page_url(raw)
        doc_id = doc_id_from_url(page)
        dest = args.output if args.output is not None else args.out_dir / f"{doc_id}.pdf"
        try:
            path = download_pdf(
                page,
                dest,
                proxy=proxy,
                insecure=args.insecure,
                cookie=args.cookie,
                timeout=args.timeout,
            )
            print(f"OK {path} ({path.stat().st_size} bytes)")
            ok_n += 1
        except Exception as e:
            print(f"FAIL {doc_id}: {e}", file=sys.stderr)
    return 0 if ok_n == len(args.docs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
