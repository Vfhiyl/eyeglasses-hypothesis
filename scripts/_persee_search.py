"""Persée portal fulltext search (www.persee.fr), default via local CONNECT gateway.

Browser XHR used by the search UI:

  GET https://www.persee.fr/search/page?p={page}&q={query}&ta={type}

Returns an HTML fragment of ``div.doc-result`` cards (snippets + /doc/ links).
Total hit count comes from the full search page:

  GET https://www.persee.fr/search?q={query}&ta={type}

This is **not** the SPARQL endpoint (``data.persee.fr/sparql``).
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from typing import Mapping

from _persee_sparql import DEFAULT_PROXY, log, make_opener, proxy_implies_insecure

SEARCH_PAGE = "https://www.persee.fr/search/page"
SEARCH_HOME = "https://www.persee.fr/search"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
SEC_CH_UA = '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'


def _headers(query: str, *, cookie: str | None = None) -> dict[str, str]:
    referer = SEARCH_HOME + "?" + urllib.parse.urlencode({"ta": "article", "q": query})
    h = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8,en;q=0.7",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": referer,
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    if cookie:
        h["Cookie"] = cookie
    return h


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_result_cards(html: str) -> list[dict[str, str]]:
    """Parse ``div.doc-result`` cards from a search/page fragment (or full page)."""
    rows: list[dict[str, str]] = []
    parts = re.split(r'<div class="doc-result">', html)
    for block in parts[1:]:
        href_m = re.search(
            r'href="(https://www\.persee\.fr/doc/[^"?#]+)(?:[^"]*)"',
            block,
        )
        title_m = re.search(r'class="title[^"]*"[^>]*>(.*?)</a>', block, re.S)
        authors = re.findall(r'class="name"[^>]*>(.*?)</', block, re.S)
        year_m = re.search(r'class="documentYear"[^>]*>(.*?)</', block, re.S)
        coll_m = re.search(r'class="collection"[^>]*>(.*?)</', block, re.S)
        pages_m = re.search(r'class="documentPageRange"[^>]*>(.*?)</', block, re.S)
        ctx_m = re.search(r'class="searchContext"[^>]*>(.*?)</div>', block, re.S)
        doc_id = ""
        href = href_m.group(1) if href_m else ""
        if href:
            doc_id = href.rstrip("/").rsplit("/", 1)[-1]
        row = {
            "doc_id": doc_id,
            "url": href,
            "title": _strip_tags(title_m.group(1)) if title_m else "",
            "authors": "; ".join(_strip_tags(a) for a in authors if _strip_tags(a)),
            "year": _strip_tags(year_m.group(1)) if year_m else "",
            "collection": _strip_tags(coll_m.group(1)) if coll_m else "",
            "pages": _strip_tags(pages_m.group(1)) if pages_m else "",
            "snippet": _strip_tags(ctx_m.group(1)) if ctx_m else "",
        }
        if row["url"] or row["title"]:
            rows.append(row)
    return rows


def parse_total_hits(html: str) -> int | None:
    """Best-effort total from full search HTML (e.g. ``141 Résultats``)."""
    m = re.search(r"([\d\s\u00a0]+)\s*[Rr]ésultats?", html)
    if not m:
        return None
    digits = re.sub(r"\D", "", m.group(1))
    return int(digits) if digits else None


def fetch_url(
    url: str,
    *,
    query_for_referer: str,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    cookie: str | None = None,
    timeout: float = 45.0,
    retries: int = 3,
    retry_sleep: float = 1.2,
    opener: urllib.request.OpenerDirector | None = None,
) -> str:
    if insecure is None:
        insecure = proxy_implies_insecure(proxy)
    op = opener or make_opener(proxy, insecure=insecure)
    last_err: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            req = urllib.request.Request(
                url,
                headers=_headers(query_for_referer, cookie=cookie),
                method="GET",
            )
            with op.open(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            if attempt >= retries:
                break
            time.sleep(retry_sleep * attempt)
    raise RuntimeError(f"Persée search fetch failed after {retries} tries: {last_err}")


def search_page(
    query: str,
    *,
    page: int = 1,
    ta: str = "article",
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    cookie: str | None = None,
    timeout: float = 45.0,
    retries: int = 3,
) -> list[dict[str, str]]:
    """Fetch one XHR page (1-based ``p``) and parse result cards."""
    p = max(1, int(page))
    params = {"p": str(p), "q": query, "ta": ta}
    url = SEARCH_PAGE + "?" + urllib.parse.urlencode(params)
    html = fetch_url(
        url,
        query_for_referer=query,
        proxy=proxy,
        insecure=insecure,
        cookie=cookie,
        timeout=timeout,
        retries=retries,
    )
    return parse_result_cards(html)


def search_total(
    query: str,
    *,
    ta: str = "article",
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    cookie: str | None = None,
    timeout: float = 45.0,
) -> int | None:
    params = {"q": query, "ta": ta}
    url = SEARCH_HOME + "?" + urllib.parse.urlencode(params)
    html = fetch_url(
        url,
        query_for_referer=query,
        proxy=proxy,
        insecure=insecure,
        cookie=cookie,
        timeout=timeout,
    )
    return parse_total_hits(html)


def search(
    query: str,
    *,
    pages: int = 1,
    start_page: int = 1,
    ta: str = "article",
    include_total: bool = True,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    cookie: str | None = None,
    timeout: float = 45.0,
    sleep_s: float = 0.4,
) -> dict[str, object]:
    """Multi-page search. Returns ``{query, ta, total, pages_fetched, results}``."""
    total: int | None = None
    if include_total:
        try:
            total = search_total(
                query,
                ta=ta,
                proxy=proxy,
                insecure=insecure,
                cookie=cookie,
                timeout=timeout,
            )
        except Exception as e:
            log(f"total lookup failed: {e}")
            total = None

    results: list[dict[str, str]] = []
    seen: set[str] = set()
    fetched = 0
    for p in range(start_page, start_page + max(1, pages)):
        rows = search_page(
            query,
            page=p,
            ta=ta,
            proxy=proxy,
            insecure=insecure,
            cookie=cookie,
            timeout=timeout,
        )
        fetched += 1
        if not rows:
            break
        for row in rows:
            key = row.get("doc_id") or row.get("url") or json.dumps(row, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            row = dict(row)
            row["page"] = str(p)
            results.append(row)
        if sleep_s > 0:
            time.sleep(sleep_s)
    return {
        "query": query,
        "ta": ta,
        "total": total,
        "pages_fetched": fetched,
        "n_results": len(results),
        "results": results,
    }


def smoke(
    *,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
) -> tuple[bool, str]:
    try:
        rows = search_page("Hesselin", page=1, proxy=proxy, insecure=insecure, timeout=40)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    if rows and any("hesselin" in (r.get("snippet") or "").lower() or "hesselin" in (r.get("title") or "").lower() or "hesselin" in (r.get("authors") or "").lower() for r in rows):
        return True, f"ok n={len(rows)}"
    if rows:
        return True, f"ok n={len(rows)} (no snippet match)"
    return False, "empty page"
