#!/usr/bin/env python3
"""FamilySearch film browse + deepzoom stitch via local CONNECT gateway.

Auth: config/familysearch_session.local  (BEARER= / COOKIE=)
Proxy default: http://127.0.0.1:12309

Page index = film-data images[] (= viewer ?i=N). Deepzoom URL has NO page
number — only ARK + zoom level + tile x_y.

Common usage:
  # Check login still works
  .venv/bin/python scripts/familysearch_film_browse.py ping

  # Stitch ONE image by ARK / viewer URL (no film cache needed)
  .venv/bin/python scripts/familysearch_film_browse.py stitch \\
    --ark 'https://www.familysearch.org/ark:/61903/3:1:S3HY-6L8S-FWN' \\
    --level 11

  # Update session from a Cookie header line (or file)
  .venv/bin/python scripts/familysearch_film_browse.py session \\
    --cookie-file /path/to/cookie.txt

  # Film index (cached under data/raw/familysearch_fulltext/films/)
  .venv/bin/python scripts/familysearch_film_browse.py film --dgs 008470424
  .venv/bin/python scripts/familysearch_film_browse.py film --dgs 008306986   # use cache if present
  .venv/bin/python scripts/familysearch_film_browse.py film --import /tmp/film-data.json
  .venv/bin/python scripts/familysearch_film_browse.py list --ark RZPQ --radius 3
  .venv/bin/python scripts/familysearch_film_browse.py stitch --ark RZPQ --radius 2 --level 11
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CONFIG, DATA_RAW  # noqa: E402

DEFAULT_PROXY = "http://127.0.0.1:12309"
SESSION_FILE = CONFIG / "familysearch_session.local"
FILM_CACHE = DATA_RAW / "familysearch_fulltext" / "films"
ARK_INDEX = FILM_CACHE / "ark_index.json"
IMG_OUT = DATA_RAW / "familysearch_fulltext" / "priority_images"
FILM_DATA_URL = "https://www.familysearch.org/search/filmdatainfo/film-data"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
DEFAULT_DZ_HOST = "https://sg30p0.familysearch.org"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_session(path: Path) -> tuple[str, str]:
    if not path.is_file():
        raise SystemExit(f"Missing {path}")
    bearer = cookie = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip().upper(), v.strip()
        if k == "BEARER":
            bearer = v.removeprefix("Bearer ").strip()
        elif k == "COOKIE":
            cookie = v
    if not bearer or not cookie:
        raise SystemExit(f"BEARER=/COOKIE= required in {path}")
    return bearer, cookie


def make_opener(proxy: str | None) -> urllib.request.OpenerDirector:
    handlers: list[urllib.request.BaseHandler] = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    # gateway MITM
    if proxy and "127.0.0.1" in proxy:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers)


def parse_ark(text: str) -> str:
    """Normalize to '3:1:XXXX-XXXX-XXXX'."""
    t = text.strip()
    m = re.search(r"(3:1:[A-Z0-9-]+)", t, re.I)
    if m:
        return m.group(1)
    # short suffix match later
    if re.fullmatch(r"[A-Z0-9-]{4,}", t, re.I):
        return t
    raise SystemExit(f"Cannot parse ARK from {text!r}")


def ark_from_image_url(url: str) -> str:
    m = re.search(r"(3:1:[A-Z0-9-]+)", url, re.I)
    if not m:
        raise ValueError(f"no ark in {url}")
    return m.group(1)


def http_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    bearer: str,
    cookie: str,
    method: str = "GET",
    body: bytes | None = None,
    referer: str,
    timeout: float = 90.0,
    retries: int = 4,
) -> Any:
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en",
        "authorization": f"Bearer {bearer}",
        "cookie": cookie,
        "user-agent": UA,
        "referer": referer,
        "fs-user-agent-chain": "search-react-prod (film-browse)",
        "x-fs-feature-tag": "das.prod.proxy,dz.prod.proxy",
        "cache-control": "no-cache",
        "pragma": "no-cache",
    }
    if body is not None:
        headers["content-type"] = "application/json"
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with opener.open(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read()[:400]
            if e.code in {429, 502, 503, 504} and attempt < retries:
                log(f"HTTP {e.code}, retry {attempt}")
                time.sleep(1.2 * attempt)
                last = e
                continue
            raise SystemExit(
                f"HTTP {e.code} {url}\n{err_body.decode('utf-8', errors='replace')}"
            ) from e
        except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
            last = e
            if attempt < retries:
                log(f"{type(e).__name__}, retry {attempt}")
                time.sleep(1.2 * attempt)
                continue
            raise SystemExit(f"request failed: {e}") from e
    raise SystemExit(f"request failed: {last}")


def http_bytes(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    bearer: str,
    cookie: str,
    referer: str,
    timeout: float = 60.0,
    retries: int = 4,
) -> bytes:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            url,
            headers={
                "accept": "image/*,*/*;q=0.8",
                "authorization": f"Bearer {bearer}",
                "cookie": cookie,
                "user-agent": UA,
                "referer": referer,
            },
            method="GET",
        )
        try:
            with opener.open(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
        except Exception as e:
            last = e
        if attempt < retries:
            time.sleep(0.7 * attempt)
    raise RuntimeError(str(last))


def cache_path(dgs: str) -> Path:
    return FILM_CACHE / f"{dgs}_film_data.json"


def normalize_dgs(dgs: str | None) -> str | None:
    if not dgs:
        return None
    s = str(dgs).strip()
    if not s.isdigit():
        return s
    # browser sometimes omits leading zeros; cache keys use 9-digit padded
    return s.zfill(9) if len(s) <= 9 else s


def load_cached_film(dgs: str) -> dict[str, Any] | None:
    p = cache_path(normalize_dgs(dgs) or dgs)
    if not p.is_file():
        # also try unpadded / as-given
        alt = FILM_CACHE / f"{dgs}_film_data.json"
        if alt.is_file() and alt != p:
            return json.loads(alt.read_text(encoding="utf-8"))
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def load_ark_index() -> dict[str, Any]:
    if not ARK_INDEX.is_file():
        return {}
    try:
        data = json.loads(ARK_INDEX.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def update_ark_index_for_film(dgs: str, images: list[str]) -> None:
    """Maintain ark → {dgs, i} map so list/stitch can skip re-POSTing film-data."""
    FILM_CACHE.mkdir(parents=True, exist_ok=True)
    idx = load_ark_index()
    # drop stale entries for this dgs
    stale = [k for k, v in idx.items() if isinstance(v, dict) and v.get("dgs") == dgs]
    for k in stale:
        del idx[k]
    for i, u in enumerate(images):
        ark = ark_from_image_url(u)
        if ark.startswith("3:1:"):
            idx[ark] = {"dgs": dgs, "i": i}
    ARK_INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def film_contains_ark(film: dict[str, Any], ark: str) -> bool:
    if not ark:
        return True
    images = film.get("images") or []
    if any(ark in u for u in images):
        return True
    # short suffix match
    if not ark.startswith("3:1:"):
        return any(ark in u for u in images)
    return False


def find_cached_film_for_ark(ark: str) -> dict[str, Any] | None:
    """Resolve film from local cache only (no network)."""
    FILM_CACHE.mkdir(parents=True, exist_ok=True)
    # Fast path: ark_index.json
    meta = load_ark_index().get(ark) if ark.startswith("3:1:") else None
    if isinstance(meta, dict) and meta.get("dgs"):
        cached = load_cached_film(str(meta["dgs"]))
        if cached and film_contains_ark(cached, ark):
            log(f"cache hit ark_index → dgs={meta['dgs']} i={meta.get('i')}")
            return cached
    # Short ark / rebuild: scan *_film_data.json
    for p in sorted(FILM_CACHE.glob("*_film_data.json")):
        cached = json.loads(p.read_text(encoding="utf-8"))
        if film_contains_ark(cached, ark):
            log(f"cache hit via ark in {p.name}")
            # keep index warm
            dgs = str(cached.get("dgsNum") or "")
            if dgs and isinstance(cached.get("images"), list):
                update_ark_index_for_film(dgs, list(cached["images"]))
            return cached
    return None


def save_film_cache(payload: dict[str, Any], *, source: str = "fetch") -> Path:
    FILM_CACHE.mkdir(parents=True, exist_ok=True)
    dgs = normalize_dgs(str(payload["dgsNum"])) or str(payload["dgsNum"])
    images = list(payload.get("images") or [])
    slim = {
        "dgsNum": dgs,
        "type": payload.get("type"),
        "templates": payload.get("templates"),
        "images": images,
        "image_count": len(images),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source": source,
    }
    # optional catalog crumb (browser dumps often include this)
    cats = payload.get("catalogs")
    if isinstance(cats, list) and cats:
        data0 = (cats[0] or {}).get("data") if isinstance(cats[0], dict) else None
        if isinstance(data0, dict):
            slim["catalog_title"] = data0.get("display_title") or data0.get("title")
            notes = data0.get("film_note") or []
            for n in notes:
                if isinstance(n, dict) and str(n.get("digital_film_no", "")).lstrip("0") == dgs.lstrip(
                    "0"
                ):
                    slim["film_note"] = n.get("text")
                    break
    path = cache_path(dgs)
    path.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
    update_ark_index_for_film(dgs, images)
    log(f"cached film {dgs}: {len(images)} images → {path}")
    log(f"ark_index entries for this film updated → {ARK_INDEX}")
    return path


def import_film_payload(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "images" not in raw or "dgsNum" not in raw:
        raise SystemExit(f"import needs JSON with dgsNum + images[]; got keys={list(raw)[:20] if isinstance(raw, dict) else type(raw)}")
    save_film_cache(raw, source=f"import:{path.name}")
    return {
        "dgsNum": normalize_dgs(str(raw["dgsNum"])) or str(raw["dgsNum"]),
        "type": raw.get("type"),
        "templates": raw.get("templates"),
        "images": list(raw["images"]),
        "image_count": len(raw["images"]),
    }


def fetch_film_data(
    opener: urllib.request.OpenerDirector,
    *,
    bearer: str,
    cookie: str,
    dgs: str | None,
    ark: str | None,
    locale: str = "en",
) -> dict[str, Any]:
    dgs = normalize_dgs(dgs)
    if not dgs and not ark:
        raise SystemExit("need --dgs or --ark")
    if ark and not ark.startswith("3:1:"):
        # allow bare; film fetch needs full ark for imageOrFilmUrl
        raise SystemExit("--ark for film fetch must be full 3:1:…")
    image_url = (
        f"https://www.familysearch.org/ark:/61903/{ark}"
        if ark
        else f"https://www.familysearch.org/search/film/{dgs}"
    )
    body_obj = {
        "type": "film-data",
        "loggedIn": True,
        "sessionId": bearer,
        "args": {
            "dgsNum": dgs or "",
            "locale": locale,
            "state": {
                "cat": None,
                "imageOrFilmUrl": image_url,
                "catalogContext": None,
                "viewMode": "i",
                "selectedImageIndex": -1,
            },
        },
    }
    referer = image_url
    log(f"POST film-data dgs={dgs or '?'} ark={ark or '-'}")
    data = http_json(
        opener,
        FILM_DATA_URL,
        bearer=bearer,
        cookie=cookie,
        method="POST",
        body=json.dumps(body_obj).encode("utf-8"),
        referer=referer,
    )
    if not isinstance(data, dict) or "images" not in data:
        raise SystemExit(f"unexpected film-data: {list(data)[:20] if isinstance(data, dict) else type(data)}")
    save_film_cache(data, source="fetch")
    return {
        "dgsNum": normalize_dgs(str(data.get("dgsNum"))) or str(data.get("dgsNum")),
        "type": data.get("type"),
        "templates": data.get("templates"),
        "images": list(data.get("images") or []),
        "image_count": len(data.get("images") or []),
    }


def resolve_film(
    opener: urllib.request.OpenerDirector | None,
    *,
    bearer: str = "",
    cookie: str = "",
    dgs: str | None,
    ark: str | None,
    refresh: bool,
) -> dict[str, Any]:
    dgs = normalize_dgs(dgs)
    # Prefer local cache unless --refresh
    if not refresh:
        if ark:
            # If dgs given, verify ark is on that film; else look up by ark
            if dgs:
                cached = load_cached_film(dgs)
                if cached and film_contains_ark(cached, ark):
                    log(f"cache hit {dgs} ({cached.get('image_count')} images)")
                    return cached
            hit = find_cached_film_for_ark(ark)
            if hit:
                return hit
        elif dgs:
            cached = load_cached_film(dgs)
            if cached:
                log(f"cache hit {dgs} ({cached.get('image_count')} images)")
                return cached
    if refresh or not (dgs and load_cached_film(dgs)):
        pass
    if not dgs and ark:
        raise SystemExit(
            "No local film cache for this ark. "
            "Pass --dgs (from viewer Network film-data), or: "
            "film --import <film-data.json>, or film --dgs … --refresh"
        )
    if not dgs:
        raise SystemExit("need --dgs (or --ark that is already in local film cache)")
    if opener is None:
        raise SystemExit("network fetch required but opener missing")
    return fetch_film_data(
        opener,
        bearer=bearer,
        cookie=cookie,
        dgs=dgs,
        ark=ark if ark and ark.startswith("3:1:") else None,
    )


def find_index(images: list[str], ark_query: str) -> int:
    q = ark_query if ark_query.startswith("3:1:") else ark_query
    for i, u in enumerate(images):
        if q in u:
            return i
    raise SystemExit(f"ARK {ark_query!r} not in film images ({len(images)} pages)")


def dz_base(templates: dict[str, Any] | None, ark: str) -> str:
    tmpl = (templates or {}).get("dzTemplate") or (
        DEFAULT_DZ_HOST + "/service/records/storage/deepzoomcloud/dz/v1/{id}/{image}"
    )
    # tmpl ends with {id}/{image}; we want .../{id}/image_files/{level}/
    base = tmpl.replace("{id}", ark).replace("{image}", "image_files")
    return base.rstrip("/")


def stitch_ark(
    opener: urllib.request.OpenerDirector,
    *,
    bearer: str,
    cookie: str,
    ark: str,
    level: int,
    templates: dict[str, Any] | None,
    out_dir: Path,
    sleep: float,
) -> Path:
    try:
        from PIL import Image
    except ImportError as e:
        raise SystemExit("Pillow required: .venv/bin/pip install pillow") from e

    out_dir.mkdir(parents=True, exist_ok=True)
    base = dz_base(templates, ark)
    referer = f"https://www.familysearch.org/ark:/61903/{ark}"
    tiles: dict[tuple[int, int], Any] = {}
    log(f"stitch {ark} level={level}")
    for y in range(0, 40):
        row_hit = False
        for x in range(0, 40):
            url = f"{base}/{level}/{x}_{y}.jpg"
            try:
                raw = http_bytes(
                    opener, url, bearer=bearer, cookie=cookie, referer=referer
                )
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break
                log(f"HTTP {e.code} at {x}_{y}, skip tile")
                continue
            except Exception as e:
                # transient gateway SSL — skip tile, keep scanning row
                log(f"skip {x}_{y}: {type(e).__name__}")
                continue
            if not raw.startswith(b"\xff\xd8"):
                log(f"non-jpeg {x}_{y}, end row")
                break
            tiles[(x, y)] = Image.open(BytesIO(raw))
            row_hit = True
            if sleep:
                time.sleep(sleep)
        if not row_hit:
            if y == 0:
                raise SystemExit(f"no tiles at level {level} for {ark}")
            break
        log(f"  row {y} cols={sum(1 for xx, yy in tiles if yy == y)}")

    xs = sorted({x for x, _ in tiles})
    ys = sorted({y for _, y in tiles})
    col_w = [max(tiles[(x, y)].width for y in ys if (x, y) in tiles) for x in xs]
    row_h = [max(tiles[(x, y)].height for x in xs if (x, y) in tiles) for y in ys]
    canvas = Image.new("RGB", (sum(col_w), sum(row_h)), (255, 255, 255))
    x_off: dict[int, int] = {}
    acc = 0
    for x, w in zip(xs, col_w):
        x_off[x] = acc
        acc += w
    y_off: dict[int, int] = {}
    acc = 0
    for y, h in zip(ys, row_h):
        y_off[y] = acc
        acc += h
    for (x, y), im in tiles.items():
        canvas.paste(im, (x_off[x], y_off[y]))
    safe = ark.replace(":", "_")
    out = out_dir / f"{safe}_L{level}.jpg"
    canvas.save(out, quality=93)
    log(f"saved {out} {canvas.size} tiles={len(tiles)}")
    return out


def cmd_ping(args: argparse.Namespace) -> None:
    """Verify session via deepzoom tile + optional Full-Text (never prints secrets)."""
    bearer, cookie = load_session(args.session)
    opener = make_opener(args.proxy)
    # Deepzoom is what stitch needs; cookie-auth like the browser image request
    tile = (
        "https://sg30p0.familysearch.org/service/records/storage/deepzoomcloud/"
        "dz/v1/3:1:3Q9M-C394-RZPQ/image_files/10/0_0.jpg"
    )
    try:
        raw = http_bytes(
            opener,
            tile,
            bearer=bearer,
            cookie=cookie,
            referer="https://www.familysearch.org/ark:/61903/3:1:3Q9M-C394-RZPQ",
            retries=3,
        )
    except urllib.error.HTTPError as e:
        if e.code in {401, 403}:
            raise SystemExit(
                f"Session INVALID (deepzoom HTTP {e.code}). Update with: "
                f"… session --cookie-file …"
            ) from e
        raise SystemExit(f"deepzoom HTTP {e.code}") from e
    except SystemExit:
        raise
    except Exception as e:
        raise SystemExit(f"deepzoom failed: {e}") from e
    if not raw.startswith(b"\xff\xd8"):
        raise SystemExit(
            f"Session dubious: deepzoom returned non-JPEG ({len(raw)} bytes). "
            "Refresh Cookie."
        )
    print(f"OK session_valid deepzoom_tile_bytes={len(raw)}")

    # Full-Text probe (needs feature tags)
    url = (
        "https://www.familysearch.org/service/search/fulltext/search"
        "?count=1&m.defaultFacets=on&m.queryRequireDefault=on"
        "&nlQuery=spectacles&offset=0"
    )
    headers_extra = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {bearer}",
        "cookie": cookie,
        "user-agent": UA,
        "referer": "https://www.familysearch.org/en/search/full-text/",
        "fs-user-agent-chain": "search-react-prod (/en/search/full-text)",
        "x-fs-feature-tag": (
            "das.prod.proxy,dz.prod.proxy, search.original.gedcomx,"
            "search_fullTextResultTitle,search_flatRecordType,"
            "search_naturalLanguageSupport,search_fullTextHighlightEnhancement"
        ),
    }
    req = urllib.request.Request(url, headers=headers_extra, method="GET")
    try:
        with opener.open(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"OK fulltext_results={data.get('results')}")
    except urllib.error.HTTPError as e:
        print(f"WARN fulltext HTTP {e.code} (deepzoom still OK; stitch usable)")
    except Exception as e:
        print(f"WARN fulltext {type(e).__name__} (deepzoom still OK; stitch usable)")


def cmd_session(args: argparse.Namespace) -> None:
    """Write BEARER+COOKIE into familysearch_session.local."""
    cookie = (args.cookie or "").strip()
    if args.cookie_file:
        cookie = Path(args.cookie_file).read_text(encoding="utf-8").strip()
        # allow a full fetch(...) paste: extract cookie":"..."
        m = re.search(r'"cookie"\s*:\s*"([^"]+)"', cookie)
        if m:
            cookie = m.group(1)
        # or a line "cookie: value"
        if "\n" in cookie or cookie.lower().startswith("cookie"):
            for line in cookie.splitlines():
                if ":" in line and "cookie" in line.split(":", 1)[0].lower():
                    cookie = line.split(":", 1)[1].strip()
                    break
    if not cookie:
        raise SystemExit("pass --cookie '…' or --cookie-file path")
    sid = ""
    for part in cookie.split(";"):
        part = part.strip()
        if part.lower().startswith("fssessionid="):
            sid = part.split("=", 1)[1].strip()
            break
    if args.bearer:
        sid = args.bearer.removeprefix("Bearer ").strip()
    if not sid:
        raise SystemExit("cookie has no fssessionid=… (or pass --bearer)")
    args.session.parent.mkdir(parents=True, exist_ok=True)
    args.session.write_text(
        "# FamilySearch session — DO NOT COMMIT\n"
        f"# Updated {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"BEARER={sid}\n\n"
        f"COOKIE={cookie}\n",
        encoding="utf-8",
    )
    print(f"wrote {args.session} bearer_len={len(sid)} cookie_len={len(cookie)}")


def cmd_film(args: argparse.Namespace) -> None:
    if args.import_path:
        data = import_film_payload(Path(args.import_path))
        print(f"dgsNum={data.get('dgsNum')} images={len(data.get('images') or [])} (imported)")
        print(f"cache={cache_path(str(data['dgsNum']))}")
        return
    ark = parse_ark(args.ark) if args.ark else None
    if ark and not ark.startswith("3:1:"):
        raise SystemExit("film --ark needs full 3:1:… (or pass --dgs only)")
    if not args.dgs and not ark:
        raise SystemExit("film needs --dgs and/or --ark, or --import FILE")
    # Default: serve from local cache; only POST when missing or --refresh
    if not args.refresh:
        try:
            data = resolve_film(
                None,
                dgs=args.dgs,
                ark=ark,
                refresh=False,
            )
            print(f"dgsNum={data.get('dgsNum')} images={len(data.get('images') or [])} (cache)")
            print(f"dzTemplate={(data.get('templates') or {}).get('dzTemplate')}")
            note = data.get("film_note")
            if note:
                print(f"film_note={note}")
            return
        except SystemExit:
            if not args.dgs:
                raise
            log("cache miss; will POST film-data")
    bearer, cookie = load_session(args.session)
    opener = make_opener(args.proxy)
    data = fetch_film_data(
        opener,
        bearer=bearer,
        cookie=cookie,
        dgs=args.dgs,
        ark=ark,
    )
    print(f"dgsNum={data.get('dgsNum')} images={len(data.get('images') or [])} (fetched)")
    print(f"dzTemplate={(data.get('templates') or {}).get('dzTemplate')}")


def cmd_list(args: argparse.Namespace) -> None:
    bearer, cookie = load_session(args.session)
    opener = make_opener(args.proxy)
    ark_q = parse_ark(args.ark) if args.ark else None
    film = resolve_film(
        opener,
        bearer=bearer,
        cookie=cookie,
        dgs=args.dgs,
        ark=ark_q,
        refresh=args.refresh,
    )
    images: list[str] = list(film["images"])
    if args.index is not None:
        center = args.index
    elif ark_q:
        center = find_index(images, ark_q)
    else:
        center = 0
    lo = max(0, center - args.radius)
    hi = min(len(images), center + args.radius + 1)
    print(f"dgs={film['dgsNum']} total={len(images)} center={center}")
    for i in range(lo, hi):
        ark = ark_from_image_url(images[i])
        mark = " <<" if i == center else ""
        print(f"  [{i:4d}] {ark}  https://www.familysearch.org/ark:/61903/{ark}?i={i}{mark}")


def cmd_stitch(args: argparse.Namespace) -> None:
    bearer, cookie = load_session(args.session)
    opener = make_opener(args.proxy)
    out_dir = Path(args.out_dir)
    ark_q = parse_ark(args.ark) if args.ark else None

    # Fast path: single ARK, no film / no radius → direct deepzoom
    if (
        ark_q
        and ark_q.startswith("3:1:")
        and args.index is None
        and args.radius == 0
        and not args.dgs
    ):
        stitch_ark(
            opener,
            bearer=bearer,
            cookie=cookie,
            ark=ark_q,
            level=args.level,
            templates=None,
            out_dir=out_dir,
            sleep=args.sleep,
        )
        return

    # Expand short ark / index / neighbors via film cache
    if args.radius > 0 and not args.dgs and not (
        ark_q and any(FILM_CACHE.glob("*_film_data.json"))
    ):
        raise SystemExit(
            "--radius needs film index: pass --dgs … or run `film --dgs …` first"
        )

    film = resolve_film(
        opener,
        bearer=bearer,
        cookie=cookie,
        dgs=args.dgs,
        ark=ark_q,
        refresh=args.refresh,
    )
    images: list[str] = list(film["images"])
    templates = film.get("templates") if isinstance(film.get("templates"), dict) else None
    if args.index is not None:
        indices = [args.index]
    elif ark_q:
        indices = [find_index(images, ark_q)]
    else:
        raise SystemExit("stitch needs --ark and/or --index")
    center = indices[0]
    if args.radius > 0:
        indices = list(
            range(max(0, center - args.radius), min(len(images), center + args.radius + 1))
        )
    for i in indices:
        ark = ark_from_image_url(images[i])
        log(f"page i={i} ark={ark}")
        stitch_ark(
            opener,
            bearer=bearer,
            cookie=cookie,
            ark=ark,
            level=args.level,
            templates=templates,
            out_dir=out_dir,
            sleep=args.sleep,
        )


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--session", type=Path, default=SESSION_FILE)
    ap.add_argument("--proxy", default=os.environ.get("https_proxy") or DEFAULT_PROXY)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_ping = sub.add_parser("ping", help="check session (Full-Text)")
    p_ping.set_defaults(func=cmd_ping)

    p_sess = sub.add_parser("session", help="update BEARER/COOKIE local file")
    p_sess.add_argument("--cookie", default=None, help="raw Cookie header value")
    p_sess.add_argument(
        "--cookie-file",
        type=Path,
        default=None,
        help="file with Cookie value or a saved fetch(...) paste",
    )
    p_sess.add_argument("--bearer", default=None, help="override fssessionid")
    p_sess.set_defaults(func=cmd_session)

    p_film = sub.add_parser(
        "film",
        help="cache film-data locally (default: reuse cache; --refresh to re-POST)",
    )
    p_film.add_argument("--dgs", default=None, help="digital film / dgsNum e.g. 008470424")
    p_film.add_argument("--ark", default=None, help="full 3:1:… page ark")
    p_film.add_argument(
        "--import",
        dest="import_path",
        type=Path,
        default=None,
        help="import a browser Network film-data JSON response (no network)",
    )
    p_film.add_argument(
        "--refresh",
        action="store_true",
        help="force POST even if cache exists",
    )
    p_film.set_defaults(func=cmd_film)

    p_list = sub.add_parser("list", help="list page indices / ARKs (uses local film cache)")
    p_list.add_argument("--dgs", default=None, help="dgsNum; optional if --ark is in cache")
    p_list.add_argument("--ark", default=None)
    p_list.add_argument("--index", type=int, default=None)
    p_list.add_argument("--radius", type=int, default=2)
    p_list.add_argument("--refresh", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_st = sub.add_parser(
        "stitch",
        help="deepzoom-stitch page(s); --ark alone needs no film cache",
    )
    p_st.add_argument(
        "--dgs",
        default=None,
        help="film dgsNum (only needed for --index / --radius / short ark)",
    )
    p_st.add_argument("--ark", default=None, help="full 3:1:… or viewer URL")
    p_st.add_argument("--index", type=int, default=None)
    p_st.add_argument("--radius", type=int, default=0, help="also stitch ±N pages")
    p_st.add_argument("--level", type=int, default=11)
    p_st.add_argument("--sleep", type=float, default=0.05, help="delay between tiles")
    p_st.add_argument("--out-dir", type=Path, default=IMG_OUT)
    p_st.add_argument("--refresh", action="store_true")
    p_st.set_defaults(func=cmd_stitch)

    args = ap.parse_args()
    # list: only default Cheshire film when neither dgs nor ark given
    if args.cmd == "list" and args.dgs is None and not getattr(args, "ark", None):
        args.dgs = "008470424"
    args.func(args)


if __name__ == "__main__":
    main()
