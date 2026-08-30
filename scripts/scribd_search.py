#!/usr/bin/env python3
"""Scribd /search/query JSON search via local CONNECT gateway.

Only knobs that matter at call time: --query and --pages.
Cookie from config/scribd_session.local or env SCRIBD_COOKIE.

  .venv/bin/python scripts/scribd_search.py --query "Cursi Miglio Tordi" --pages 2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _session_local import load_cookie  # noqa: E402

PROXY = "http://127.0.0.1:12309"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/150.0.0.0 Safari/537.36"
)
SEC_CH_UA = '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'
COOKIE = load_cookie(env_name="SCRIBD_COOKIE", filename="scribd_session.local")

TIMEOUT_S = 60.0
SLEEP_BETWEEN_PAGES_S = 0.8
RETRY_MAX = 4
RETRY_BASE_S = 1.5
OUT_PATH = Path("outputs/tables/scribd_search_hits.jsonl")

SCORE_TOKENS: list[tuple[str, int]] = [
    ("ardinghelli", 12),
    ("gianfigliazzi", 10),
    ("quaderno di chassa", 12),
    ("quaderno di cassa", 12),
    ("tordi", 10),
    ("cursi", 8),
    ("miglio", 6),
    ("978-88-6809-080-7", 15),
    ("88-6809-080-7", 15),
    ("accademia tudertina", 6),
    ("scriptoria e biblioteche", 5),
    ("spoleto 2015", 6),
    ("cisam", 4),
    ("metamorfosi di un borgo", 12),
    ("roveda", 8),
    ("policastro", 12),
    ("vigevano", 4),
    ("chittolini", 3),
    ("santoro", 3),
    ("gli uffici del dominio sforzesco", 10),
    ("ilardi", 5),
    ("occhiali", 8),
    ("eyeglasses", 8),
]


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
    )


def search_page(*, query: str, page: int, page_view_id: str) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {"query": query, "page": str(page), "page_view_id": page_view_id}
    )
    url = f"https://www.scribd.com/search/query?{params}"
    referer_q = urllib.parse.urlencode({"query": query, "page": str(page)})
    headers = {
        "accept": "application/json",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": UA,
        "x-requested-with": "XMLHttpRequest",
        "cookie": COOKIE,
        "referer": f"https://www.scribd.com/search?{referer_q}",
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with _opener().open(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read()
            ctype = resp.headers.get("content-type", "")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:400]!r}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error: {e}") from e
    text = raw.decode("utf-8", errors="replace")
    if "application/json" not in ctype and not text.lstrip().startswith("{"):
        raise RuntimeError(f"Non-JSON ctype={ctype!r} head={text[:200]!r}")
    return json.loads(text)


def search_page_retry(
    *,
    query: str,
    page: int,
    page_view_id: str,
    retries: int = RETRY_MAX,
) -> dict[str, Any]:
    """Retry flaky 403 / gateway / non-JSON responses with backoff."""
    last_err: Exception | None = None
    pvid = page_view_id
    attempts = max(1, retries)
    for attempt in range(1, attempts + 1):
        try:
            return search_page(query=query, page=page, page_view_id=pvid)
        except Exception as e:
            last_err = e
            if attempt >= attempts:
                break
            wait = RETRY_BASE_S * (2 ** (attempt - 1))
            print(
                f"page {page} attempt {attempt}/{attempts} failed: {e}; "
                f"retry in {wait:.1f}s",
                file=sys.stderr,
            )
            time.sleep(wait)
            # fresh view id sometimes clears transient WAF/session glitches
            pvid = str(uuid.uuid4())
    assert last_err is not None
    raise last_err


def _as_doc_list(block: Any) -> list[dict[str, Any]]:
    """Scribd nests hits as results.documents.content.documents = [...]."""
    if isinstance(block, list):
        return [x for x in block if isinstance(x, dict) and x.get("title")]
    if not isinstance(block, dict):
        return []
    # direct list under common keys
    for key in ("documents", "docs", "items", "results"):
        inner = block.get(key)
        if isinstance(inner, list):
            return [x for x in inner if isinstance(x, dict) and x.get("title")]
        if isinstance(inner, dict):
            # documents: {content: {documents: [...]}, tracking_data: ...}
            content = inner.get("content")
            if isinstance(content, dict):
                nested = content.get("documents") or content.get("docs") or content.get("items")
                if isinstance(nested, list):
                    return [x for x in nested if isinstance(x, dict) and x.get("title")]
            nested2 = inner.get("documents")
            if isinstance(nested2, list):
                return [x for x in nested2 if isinstance(x, dict) and x.get("title")]
    content = block.get("content")
    if isinstance(content, dict):
        nested = content.get("documents") or content.get("docs") or content.get("items")
        if isinstance(nested, list):
            return [x for x in nested if isinstance(x, dict) and x.get("title")]
    return []


def extract_docs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull document hits only — never browse/category chrome."""
    docs: list[dict[str, Any]] = []
    docs.extend(_as_doc_list(payload.get("results")))
    docs.extend(_as_doc_list(payload.get("top_result")))
    for key in ("documents", "docs", "items"):
        docs.extend(_as_doc_list(payload.get(key)))

    final: list[dict[str, Any]] = []
    seen: set[str] = set()
    for d in docs:
        if d.get("subcategories") is not None or d.get("selection_type") is not None:
            continue
        title = str(d.get("title") or "")
        doc_id = str(d.get("id") or d.get("document_id") or "")
        url = str(d.get("reader_url") or d.get("url") or "")
        if not title:
            continue
        key = doc_id or url or title
        if key in seen:
            continue
        seen.add(key)
        final.append(d)
    return final


def normalize_doc(d: dict[str, Any], *, query: str, page: int) -> dict[str, Any]:
    title = str(d.get("title") or "")
    desc = str(d.get("description") or "")
    doc_id = d.get("id") or d.get("document_id")
    url = d.get("reader_url") or d.get("url")
    if isinstance(url, str) and url.startswith("/"):
        url = "https://www.scribd.com" + url
    if not url and doc_id:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower() or "doc"
        url = f"https://www.scribd.com/document/{doc_id}/{slug}"
    text = f"{title} {desc}".lower()
    hits = [tok for tok, _w in SCORE_TOKENS if tok in text]
    score = sum(w for tok, w in SCORE_TOKENS if tok in text)
    return {
        "query": query,
        "page": page,
        "id": doc_id,
        "title": title,
        "description": desc,
        "url": url,
        "pages": d.get("pageCount") or d.get("page_count") or d.get("pages"),
        "filetype": d.get("type") or d.get("filetype"),
        "b1_score": score,
        "b1_hits": hits,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="Scribd search string")
    ap.add_argument("--pages", type=int, default=2, help="How many result pages")
    ap.add_argument(
        "--retries",
        type=int,
        default=RETRY_MAX,
        help=f"Attempts per page on 403/network/non-JSON (default {RETRY_MAX})",
    )
    args = ap.parse_args()
    if not COOKIE.strip():
        raise SystemExit(
            "Missing Scribd session: set SCRIBD_COOKIE or write config/scribd_session.local"
        )

    query = args.query.strip()
    pages = max(1, args.pages)
    retries = max(1, args.retries)
    page_view_id = str(uuid.uuid4())
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    print(f"proxy={PROXY} query={query!r} pages={pages} retries={retries}")
    for page in range(1, pages + 1):
        try:
            payload = search_page_retry(
                query=query,
                page=page,
                page_view_id=page_view_id,
                retries=retries,
            )
        except Exception as e:
            print(f"page {page} ERROR after {retries} attempts: {e}", file=sys.stderr)
            rows.append({"query": query, "page": page, "error": str(e), "b1_score": -1})
            break
        docs = extract_docs(payload)
        print(f"page {page}: extracted={len(docs)} top_keys={sorted(payload.keys())[:12]}")
        if not docs:
            rows.append(
                {
                    "query": query,
                    "page": page,
                    "note": "no_docs_extracted",
                    "raw_keys": sorted(payload.keys()),
                    "raw_head": json.dumps(payload, ensure_ascii=False)[:1000],
                    "b1_score": 0,
                    "title": "",
                }
            )
        for d in docs:
            norm = normalize_doc(d, query=query, page=page)
            key = str(norm.get("id") or norm.get("url") or norm.get("title"))
            if not key or key in seen:
                continue
            seen.add(key)
            rows.append(norm)
        if page < pages:
            time.sleep(SLEEP_BETWEEN_PAGES_S)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    ranked = sorted(
        (r for r in rows if r.get("title")),
        key=lambda r: (-int(r.get("b1_score") or 0), str(r.get("title"))),
    )
    print("\n=== results (by b1_score) ===")
    for r in ranked[:50]:
        print(
            f"score={r.get('b1_score'):3} | {str(r.get('title'))[:100]!r} | "
            f"{r.get('b1_hits')} | {r.get('url')}"
        )
    if not ranked:
        print("(no titles — see JSONL raw_head / error)")
        for r in rows[:3]:
            print(json.dumps(r, ensure_ascii=False)[:600])
    print(f"\nwrote {OUT_PATH} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
