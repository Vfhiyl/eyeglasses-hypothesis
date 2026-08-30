#!/usr/bin/env python3
"""FamilySearch Full-Text search via local CONNECT gateway.

Auth from browser DevTools → config/familysearch_session.local
  BEARER=…   (Authorization: Bearer … / fssessionid)
  COOKIE=…   (full Cookie header)

Proxy (default):
  http://127.0.0.1:12309

Examples:
  .venv/bin/python scripts/familysearch_fulltext_search.py \\
    --query spectacles --year-from 1400 --year-to 1650 --pages 3

  .venv/bin/python scripts/familysearch_fulltext_search.py \\
    --query '"pair of spectacles"' --record-type will --pages 5 --dump-facets
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
from _paths import CONFIG, DATA_RAW, OUTPUT_TABLES  # noqa: E402

DEFAULT_PROXY = "http://127.0.0.1:12309"
SESSION_FILE = CONFIG / "familysearch_session.local"
API = "https://www.familysearch.org/service/search/fulltext/search"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
SEC_CH_UA = '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'
FEATURE_TAG = (
    "das.prod.proxy,dz.prod.proxy, search.original.gedcomx,"
    "search.default.facet.include.race,search_fullTextResultTitle,"
    "search_flatRecordType,search_naturalLanguageSupport,"
    "search_fullTextHighlightEnhancement"
)
OUT_DIR = DATA_RAW / "familysearch_fulltext"
DEFAULT_JSONL = OUTPUT_TABLES / "familysearch_spectacles_hits.jsonl"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_session(path: Path) -> tuple[str, str]:
    if not path.is_file():
        raise SystemExit(f"Missing session file: {path}")
    bearer = ""
    cookie = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip().upper()
        val = val.strip()
        if key == "BEARER":
            bearer = val.removeprefix("Bearer ").strip()
        elif key == "COOKIE":
            cookie = val
    if not bearer:
        raise SystemExit(f"BEARER= missing in {path}")
    if not cookie:
        raise SystemExit(f"COOKIE= missing in {path}")
    return bearer, cookie


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


def build_url(
    *,
    query: str,
    offset: int,
    count: int,
    record_years: list[int],
    place_code: str | None,
    record_type_id: str | None,
    collection: str | None,
    extra: list[str],
) -> str:
    """Build FS Full-Text URL.

    Facet param shapes (from live facets payload):
      Year century:  c.recordYear1=on&f.recordYear0=1600
      Place region:  c.recordPlace1=on&f.recordPlace0=9   (9=UK&Ireland)
      Collection:    c.collectionId=on&f.collectionId=…
      Record type:   c.recordTypeId=on&f.recordTypeId=…
    """
    params: list[tuple[str, str]] = [
        ("count", str(count)),
        ("m.defaultFacets", "on"),
        ("m.queryRequireDefault", "on"),
        ("nlQuery", query),
        ("offset", str(offset)),
    ]
    if record_years:
        params.append(("c.recordYear1", "on"))
        for y in record_years:
            params.append(("f.recordYear0", str(y)))
    if place_code:
        params.append(("c.recordPlace1", "on"))
        params.append(("f.recordPlace0", place_code))
    if record_type_id:
        params.append(("c.recordTypeId", "on"))
        params.append(("f.recordTypeId", record_type_id))
    if collection:
        params.append(("c.collectionId", "on"))
        params.append(("f.collectionId", collection))
    for item in extra:
        if "=" not in item:
            raise SystemExit(f"--extra needs key=value, got {item!r}")
        k, v = item.split("=", 1)
        params.append((k, v))
    return f"{API}?{urllib.parse.urlencode(params)}"


def http_get_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    bearer: str,
    cookie: str,
    referer: str,
    timeout: float,
    retries: int = 4,
) -> dict[str, Any]:
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en",
        "authorization": f"Bearer {bearer}",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "cookie": cookie,
        "fs-user-agent-chain": "search-react-prod (/en/search/full-text/results)",
        "referer": referer,
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": UA,
        "x-fs-feature-tag": FEATURE_TAG,
    }
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with opener.open(req, timeout=timeout) as resp:
                raw = resp.read()
                ctype = resp.headers.get("content-type", "")
            if "json" not in ctype and not raw[:1] == b"{":
                preview = raw[:400].decode("utf-8", errors="replace")
                raise SystemExit(f"Non-JSON response ({ctype}): {preview}")
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise SystemExit(f"Unexpected JSON root type: {type(data)}")
            return data
        except urllib.error.HTTPError as e:
            body = e.read()[:800]
            if e.code in {429, 502, 503, 504} and attempt < retries:
                wait = 1.5 * attempt
                log(f"HTTP {e.code}, retry {attempt}/{retries} in {wait:.1f}s")
                time.sleep(wait)
                last_err = e
                continue
            raise SystemExit(
                f"HTTP {e.code} for {url}\n{body.decode('utf-8', errors='replace')}"
            ) from e
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last_err = e
            if attempt < retries:
                wait = 1.5 * attempt
                log(f"{type(e).__name__}: {e}; retry {attempt}/{retries} in {wait:.1f}s")
                time.sleep(wait)
                continue
            raise SystemExit(f"URL/SSL error via proxy after {retries} tries: {e}") from e
    raise SystemExit(f"URL/SSL error via proxy: {last_err}")


def flatten_hit(entry: dict[str, Any], *, query: str) -> dict[str, Any]:
    """Flatten FS entry + nested content block."""
    content = entry.get("content") if isinstance(entry.get("content"), dict) else {}
    title = content.get("title") or entry.get("collectionTitle") or ""
    highlights = content.get("highlightTexts") or []
    if isinstance(highlights, list):
        hl_text = " | ".join(str(h) for h in highlights[:8])
    else:
        hl_text = str(highlights)[:800]
    text_doc = content.get("textDocument") or ""
    context = ""
    if isinstance(text_doc, str) and text_doc:
        low = text_doc.lower()
        for needle in (
            "pair of spectacles",
            "paire of spectacles",
            "peyre spectac",
            "spectacles",
            "spectacle",
            "eyeglasses",
            "pair of glasses",
        ):
            i = low.find(needle)
            if i >= 0:
                context = " ".join(text_doc[max(0, i - 100) : i + 160].split())
                break
    if not hl_text and context:
        hl_text = context
    year = content.get("recordDate") or ""
    place = content.get("recordPlace") or ""
    return {
        "query": query,
        "title": title,
        "years": year,
        "place": place,
        "highlights": hl_text[:800],
        "context": context[:500],
        "record_type": content.get("recordType") or "",
        "collection": entry.get("collectionTitle") or "",
        "collection_id": entry.get("collectionId") or "",
        "source_url": entry.get("sourceUrl") or "",
        "ark": entry.get("id") or "",
        "raw": entry,
    }


def extract_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("entries", "results", "hits", "items", "searchResults"):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
    # gedcomx-ish nesting
    data = payload.get("data")
    if isinstance(data, dict):
        return extract_entries(data)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    return []


def extract_total(payload: dict[str, Any]) -> int | None:
    # Live API uses `results` as total hit count (int)
    val = payload.get("results")
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    for key in ("totalHits", "total", "count", "resultCount"):
        v = payload.get(key)
        if isinstance(v, int):
            return v
    return None


def _parse_year(years: object) -> int | None:
    if isinstance(years, int):
        return years
    if isinstance(years, str):
        digits = "".join(ch if ch.isdigit() else " " for ch in years).split()
        for d in digits:
            if len(d) == 4:
                return int(d)
    return None


def score_hit(hit: dict[str, Any]) -> int:
    blob = " ".join(
        str(hit.get(k, ""))
        for k in ("title", "highlights", "collection", "record_type", "place")
    ).lower()
    score = 0
    for tok, pts in (
        ("will", 10),
        ("probate", 10),
        ("inventory", 8),
        ("testament", 8),
        ("bequeath", 8),
        ("peyre spectac", 12),
        ("pair of spectac", 12),
        ("spectacles", 5),
        ("spectacle", 4),
        ("eyeglasses", 5),
        ("england", 4),
        ("united kingdom", 4),
        ("london", 2),
        ("york", 2),
        ("canterbury", 4),
        ("periodical", -12),
        ("newspaper", -12),
        ("biography", -8),
        ("advertis", -8),
        ("tennessee", -6),
        ("kentucky", -6),
        ("united states", -3),
    ):
        if tok in blob:
            score += pts
    y = _parse_year(hit.get("years"))
    if y is not None:
        if 1400 <= y <= 1650:
            score += 14
        elif 1651 <= y <= 1750:
            score += 4
        elif y >= 1800:
            score -= 8
    return score


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--query", "-q", required=True, help="nlQuery / keywords")
    ap.add_argument("--pages", type=int, default=3, help="pages to fetch (default 3)")
    ap.add_argument("--count", type=int, default=20, help="hits per page (default 20)")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument(
        "--record-year",
        type=int,
        action="append",
        default=[],
        help="century bucket for f.recordYear0 (repeatable), e.g. 1600 1700",
    )
    ap.add_argument(
        "--place-code",
        default=None,
        help="f.recordPlace0 code: 9=UK&Ireland, 5=Continental Europe, 10=USA",
    )
    ap.add_argument(
        "--record-type-id",
        default=None,
        help="f.recordTypeId from facets (e.g. wills if listed)",
    )
    ap.add_argument("--collection", default=None, help="f.collectionId")
    ap.add_argument(
        "--extra",
        action="append",
        default=[],
        help="raw query param key=value (repeatable); use after inspecting browser",
    )
    ap.add_argument(
        "--list-facets",
        action="store_true",
        help="print Year/Place/RecordType/Collection facet top rows then exit",
    )
    ap.add_argument("--proxy", default=os.environ.get("https_proxy") or DEFAULT_PROXY)
    ap.add_argument("--session", type=Path, default=SESSION_FILE)
    ap.add_argument("--insecure", action="store_true", help="skip TLS verify (gateway MITM)")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--sleep", type=float, default=0.7)
    ap.add_argument("--out", type=Path, default=DEFAULT_JSONL)
    ap.add_argument("--raw-dir", type=Path, default=OUT_DIR)
    ap.add_argument("--dump-facets", action="store_true", help="print facet keys from page 0")
    ap.add_argument("--top", type=int, default=25, help="print top-N scored hits")
    args = ap.parse_args()

    bearer, cookie = load_session(args.session)
    # Gateway often MITMs TLS; default insecure=True when using local proxy
    insecure = args.insecure or (
        args.proxy is not None and "127.0.0.1" in args.proxy
    )
    opener = make_opener(args.proxy, insecure=insecure)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    referer_q = urllib.parse.urlencode({"nlQuery": args.query})
    referer = f"https://www.familysearch.org/en/search/full-text/results?{referer_q}"

    all_hits: list[dict[str, Any]] = []
    total: int | None = None
    pages_to_fetch = 1 if args.list_facets else args.pages

    for page in range(pages_to_fetch):
        offset = args.offset + page * args.count
        url = build_url(
            query=args.query,
            offset=offset,
            count=args.count,
            record_years=args.record_year,
            place_code=args.place_code,
            record_type_id=args.record_type_id,
            collection=args.collection,
            extra=args.extra,
        )
        log(f"GET offset={offset} via {args.proxy}")
        payload = http_get_json(
            opener,
            url,
            bearer=bearer,
            cookie=cookie,
            referer=referer,
            timeout=args.timeout,
        )
        raw_path = args.raw_dir / f"page_{offset:05d}.json"
        raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if page == 0:
            total = extract_total(payload)
            log(f"total≈{total} keys={list(payload.keys())[:20]}")
            if args.dump_facets or args.list_facets:
                for fac in payload.get("facets") or []:
                    if not isinstance(fac, dict):
                        continue
                    print(f"\n==== {fac.get('displayName')} ({fac.get('count')})")
                    for kid in (fac.get("facets") or [])[:40]:
                        print(
                            f"  {str(kid.get('displayCount')):>8}  "
                            f"{kid.get('displayName')}  |  {kid.get('params')}"
                        )
                if args.list_facets:
                    return
        entries = extract_entries(payload)
        log(f"page entries={len(entries)} → {raw_path.name}")
        if not entries and page == 0:
            log("No entries parsed — inspect raw JSON keys / nesting")
        for ent in entries:
            hit = flatten_hit(ent, query=args.query)
            hit["score"] = score_hit(hit)
            all_hits.append(hit)
        if page + 1 < pages_to_fetch:
            time.sleep(args.sleep)

    # write jsonl (without huge raw if too big — keep raw for now, user wants leads)
    with args.out.open("w", encoding="utf-8") as f:
        for hit in sorted(all_hits, key=lambda h: h["score"], reverse=True):
            slim = {k: v for k, v in hit.items() if k != "raw"}
            slim["raw_keys"] = sorted(hit["raw"].keys()) if isinstance(hit.get("raw"), dict) else []
            f.write(json.dumps(slim, ensure_ascii=False) + "\n")

    log(f"wrote {len(all_hits)} hits → {args.out}")
    print("\n=== TOP HITS ===")
    for i, hit in enumerate(sorted(all_hits, key=lambda h: h["score"], reverse=True)[: args.top], 1):
        title = (hit.get("title") or "")[:120]
        hl = (hit.get("highlights") or "")[:220].replace("\n", " ")
        print(f"{i:2d}. score={hit['score']:+d}  {title}")
        if hl:
            print(f"    {hl}")


if __name__ == "__main__":
    main()
