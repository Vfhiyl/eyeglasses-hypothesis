#!/usr/bin/env python3
"""Internet Archive page_production search via local CONNECT gateway.

Endpoint:
  https://archive.org/services/search/beta/page_production/

Proxy (default):
  http://127.0.0.1:12309

Examples:
  python3 scripts/ia_page_production_search.py --query '(spectacles AND household)'
  python3 scripts/ia_page_production_search.py \\
    --query 'title:(Devon Household Accounts) OR identifier:devonhouseholdac0000unse' \\
    --hits-per-page 20 --page 1 --out /tmp/ia_hits.json
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import DATA_RAW, OUTPUT_TABLES  # noqa: E402
from _session_local import load_cookie  # noqa: E402

DEFAULT_PROXY = "http://127.0.0.1:12309"
API = "https://archive.org/services/search/beta/page_production/"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
SEC_CH_UA = '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'
OUT_DIR = DATA_RAW / "ia_page_production"
DEFAULT_JSONL = OUTPUT_TABLES / "ia_page_production_hits.jsonl"

IA_COOKIE = load_cookie(env_name="IA_COOKIE", filename="ia_session.local")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def make_opener(proxy: str | None, *, insecure: bool) -> urllib.request.OpenerDirector:
    handlers: list[urllib.request.BaseHandler] = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers)


def make_uid() -> str:
    """IA uid shape from browser: R:…-S:…-P:1-K:h-T:<ms>."""
    ms = int(time.time() * 1000)
    return f"R:eyeglasses-hypothesis-S:local-P:1-K:h-T:{ms}"


def build_url(
    *,
    query: str,
    page: int,
    hits_per_page: int,
    aggregations: bool,
    uid: str,
) -> str:
    client_url = "https://archive.org/search?" + urllib.parse.urlencode({"query": query})
    params = {
        "user_query": query,
        "hits_per_page": str(hits_per_page),
        "page": str(page),
        "aggregations": "true" if aggregations else "false",
        "uid": uid,
        "client_url": client_url,
    }
    return API + "?" + urllib.parse.urlencode(params)


def request_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    cookie: str,
    referer_query: str,
    retries: int = 5,
    retry_sleep: float = 1.2,
) -> dict[str, Any]:
    referer = "https://archive.org/search?" + urllib.parse.urlencode({"query": referer_query})
    last_err: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                "user-agent": UA,
                "sec-ch-ua": SEC_CH_UA,
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "priority": "u=1, i",
                "cookie": cookie,
                "Referer": referer,
            },
        )
        try:
            with opener.open(req, timeout=60) as resp:
                raw = resp.read()
                status = getattr(resp, "status", 200)
            if status >= 400:
                raise urllib.error.HTTPError(url, status, f"HTTP {status}", resp.headers, None)
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise SystemExit(f"unexpected JSON type: {type(data).__name__}")
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:800] if e.fp else ""
            # 429/5xx: retry; 401/403: fail fast (cookie stale)
            if e.code in (401, 403):
                raise SystemExit(f"HTTP {e.code} for {url}\n{body}") from e
            last_err = e
            log(f"HTTP {e.code} attempt {attempt}/{retries}; retrying")
        except (urllib.error.URLError, TimeoutError, ssl.SSLError, ConnectionResetError) as e:
            last_err = e
            log(f"transient {type(e).__name__}: {e}; attempt {attempt}/{retries}")
        except json.JSONDecodeError as e:
            last_err = e
            log(f"bad JSON attempt {attempt}/{retries}: {e}")
        if attempt < retries:
            time.sleep(retry_sleep * attempt)
    raise SystemExit(f"failed after {retries} retries: {last_err}")


def extract_hits(payload: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    body = payload.get("response", {}).get("body", {})
    if not isinstance(body, dict):
        return 0, []
    hits_wrap = body.get("hits", {})
    if not isinstance(hits_wrap, dict):
        return 0, []
    total = int(hits_wrap.get("total") or 0)
    rows = hits_wrap.get("hits") or []
    out: list[dict[str, Any]] = []
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            fields = row.get("fields")
            if isinstance(fields, dict):
                out.append(fields)
            else:
                out.append(row)
    return total, out


def main() -> None:
    ap = argparse.ArgumentParser(description="IA page_production search via gateway proxy")
    ap.add_argument("--query", "-q", required=True, help="IA user_query string")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--pages", type=int, default=1, help="how many pages to fetch from --page")
    ap.add_argument("--hits-per-page", type=int, default=100)
    ap.add_argument("--aggregations", action="store_true")
    ap.add_argument(
        "--proxy",
        default=DEFAULT_PROXY,
        help=f"CONNECT proxy (default {DEFAULT_PROXY}; ignore ambient env)",
    )
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--insecure", action="store_true", help="skip TLS verify (gateway MITM)")
    ap.add_argument("--cookie", default="", help="override config/ia_session.local")
    ap.add_argument("--sleep", type=float, default=0.4)
    ap.add_argument("--retries", type=int, default=6, help="transient SSL/proxy retries per page")
    ap.add_argument("--retry-sleep", type=float, default=1.2)
    ap.add_argument("--out", type=Path, default=None, help="write full last response JSON")
    ap.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL, help="append hit fields JSONL")
    ap.add_argument("--dump-dir", type=Path, default=OUT_DIR, help="per-page raw JSON dump dir")
    args = ap.parse_args()

    cookie = (args.cookie or IA_COOKIE).strip()
    if not cookie:
        raise SystemExit("empty cookie")

    proxy = None if args.no_proxy else args.proxy
    # Gateway often MITMs TLS; default insecure when using local proxy.
    insecure = args.insecure or (proxy is not None and "127.0.0.1" in proxy)
    opener = make_opener(proxy, insecure=insecure)
    log(f"proxy={proxy or '(none)'} query={args.query!r} pages={args.pages}")

    args.dump_dir.mkdir(parents=True, exist_ok=True)
    args.jsonl.parent.mkdir(parents=True, exist_ok=True)

    all_hits: list[dict[str, Any]] = []
    last_payload: dict[str, Any] | None = None
    total = 0

    for i in range(args.pages):
        page = args.page + i
        uid = make_uid()
        url = build_url(
            query=args.query,
            page=page,
            hits_per_page=args.hits_per_page,
            aggregations=args.aggregations,
            uid=uid,
        )
        log(f"GET page={page} hits_per_page={args.hits_per_page}")
        payload = request_json(
            opener,
            url,
            cookie=cookie,
            referer_query=args.query,
            retries=args.retries,
            retry_sleep=args.retry_sleep,
        )
        last_payload = payload
        dump_path = args.dump_dir / f"page_{page:04d}.json"
        dump_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        header = payload.get("response", {}).get("header", {})
        ok = bool(header.get("succeeded")) if isinstance(header, dict) else False
        total, hits = extract_hits(payload)
        log(f"succeeded={ok} total={total} returned={len(hits)} dump={dump_path}")

        with args.jsonl.open("a", encoding="utf-8") as fh:
            for fields in hits:
                rec = {
                    "query": args.query,
                    "page": page,
                    "identifier": fields.get("identifier"),
                    "title": fields.get("title"),
                    "year": fields.get("year"),
                    "mediatype": fields.get("mediatype"),
                    "collection": fields.get("collection"),
                    "fields": fields,
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                all_hits.append(fields)

        if args.pages > 1 and i + 1 < args.pages:
            time.sleep(max(0.0, args.sleep))

    # compact stdout table
    for fields in all_hits[:50]:
        ident = fields.get("identifier", "")
        year = fields.get("year", "")
        title = (fields.get("title") or "")[:90]
        mtype = fields.get("mediatype", "")
        print(f"{year!s:>6}  {mtype:<8}  {ident:<40}  {title}")
    if len(all_hits) > 50:
        print(f"... ({len(all_hits) - 50} more; see {args.jsonl})")

    if args.out and last_payload is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(last_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log(f"wrote {args.out}")

    log(f"done hits_collected={len(all_hits)} catalog_total={total} jsonl={args.jsonl}")


if __name__ == "__main__":
    main()
