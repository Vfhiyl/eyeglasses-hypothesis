#!/usr/bin/env python3
"""MIA (mia.medici.org) search helper for Spinelli / MdP digs.

Usage:
  python3 scripts/32_mia_search.py people Spinelli
  python3 scripts/32_mia_search.py docs-person 12345
  python3 scripts/32_mia_search.py docs-place Marradi --year-from 1534 --year-to 1540
  python3 scripts/32_mia_search.py word "Spinelli Marradi" --year-from 1535 --year-to 1540
  python3 scripts/32_mia_search.py spinelli-hunt
  python3 scripts/32_mia_search.py volume-desc 118
  python3 scripts/32_mia_search.py document 25944
  python3 scripts/32_mia_search.py docs-mdp 181
  python3 scripts/32_mia_search.py docs-mdp 181 --all

Session: config/mia_session.local (COOKIE= / ACCOUNT=) or env MIA_COOKIE / MIA_ACCOUNT.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _session_local import load_cookie, load_field  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "mia_spinelli"

MIA_COOKIE = load_cookie(env_name="MIA_COOKIE", filename="mia_session.local")
MIA_ACCOUNT = load_field(
    env_name="MIA_ACCOUNT", filename="mia_session.local", key="ACCOUNT"
)

BASE = "https://mia.medici.org/Mia/json"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)


def get_me_account() -> str:
    """Logged-in account string required by wordSearch (UI: params.owner = me.account)."""
    global MIA_ACCOUNT
    if MIA_ACCOUNT.strip():
        return MIA_ACCOUNT.strip()
    resp = get_json("user/me")
    if resp.get("status") != "ok":
        raise SystemExit(f"user/me failed: {resp}")
    data = resp.get("data") or []
    if not data or not isinstance(data[0], dict) or not data[0].get("account"):
        raise SystemExit(f"user/me missing account: {resp}")
    MIA_ACCOUNT = str(data[0]["account"])
    return MIA_ACCOUNT


def _headers(content_json: bool = False) -> dict[str, str]:
    h = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": MIA_COOKIE,
        "origin": "https://mia.medici.org",
        "referer": "https://mia.medici.org/Mia/index.html",
        "user-agent": UA,
    }
    if content_json:
        h["content-type"] = "application/json;charset=UTF-8"
    return h


def _request(
    method: str,
    url: str,
    body: object | None = None,
    timeout: float = 60.0,
) -> Any:
    data = None
    headers = _headers(content_json=body is not None)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")[:500]
        raise SystemExit(f"HTTP {e.code} for {url}\n{err_body}") from e
    except urllib.error.URLError as e:
        raise SystemExit(f"URL error for {url}: {e}") from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise SystemExit(f"Non-JSON response from {url}:\n{raw[:400]}") from None


def get_json(path: str) -> Any:
    return _request("GET", f"{BASE}/{path.lstrip('/')}")


def post_json(path: str, body: object) -> Any:
    return _request("POST", f"{BASE}/{path.lstrip('/')}", body=body)


def save(name: str, payload: object) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def find_people(query: str) -> list[dict[str, Any]]:
    q = urllib.parse.quote(query, safe="")
    resp = get_json(f"document/findPeople/{q}")
    if resp.get("status") != "ok":
        return []
    people = (resp.get("data") or {}).get("people") or []
    return list(people)


def find_places(query: str) -> list[dict[str, Any]]:
    q = urllib.parse.quote(query, safe="")
    resp = get_json(f"document/findPlaces/{q}")
    if resp.get("status") != "ok":
        return []
    return list((resp.get("data") or {}).get("places") or [])


def find_people_by_id(people_id: int) -> Any:
    return get_json(f"document/findPeopleById/{people_id}")


def find_document(doc_id: int) -> Any:
    return get_json(f"document/findDocument/{doc_id}")


def find_volume_description(volume_id: int) -> Any:
    return get_json(f"volumeInsertDescription/findVolume/{volume_id}/")


def biographical_people(person_id: int) -> Any:
    return get_json(f"biographical/findBiographicalPeople/{person_id}")


def _inactive_filters() -> list[dict[str, Any]]:
    """Full advanced-search array scaffold used by MIA UI (inactive slots).

    Matches the body posted by SEARCH DOCUMENTS / volume page
    'Documents related to this Volume' (archivalLocationAdvancedSearch).
    """
    return [
        {
            "searchSection": "archivalLocationSearch",
            "type": "archivalLocationAdvancedSearch",
            "isActiveFilter": False,
            "collection": None,
            "series": None,
            "volume": None,
            "insert": None,
        },
        {
            "searchSection": "categoryAndTypologySearch",
            "type": "categoryAndTypologyAdvancedSearch",
            "isActiveFilter": False,
        },
        {
            "searchSection": "transcriptionSearch",
            "type": "transcriptionAdvancedSearch",
            "isActiveFilter": False,
        },
        {
            "searchSection": "synopsisSearch",
            "type": "synopsisAdvancedSearch",
            "isActiveFilter": False,
        },
        {
            "searchSection": "placesSearch",
            "type": "placesAdvancedSearch",
            "isActiveFilter": False,
            "places": [],
        },
        {
            "searchSection": "peopleSearch",
            "type": "peopleAdvancedSearch",
            "isActiveFilter": False,
            "people": [],
        },
        {
            "searchSection": "topicsSearch",
            "type": "topicsAdvancedSearch",
            "isActiveFilter": False,
            "topics": [],
        },
        {
            "searchSection": "dateSearch",
            "type": "dateAdvancedSearch",
            "isActiveFilter": False,
            "dateFilterType": "",
            "dateYear": "",
            "dateMonth": "",
            "dateDay": "",
            "dateBYear": "",
            "dateBMonth": "",
            "dateBDay": "",
        },
        {
            "searchSection": "documentOwnerSearch",
            "type": "documentOwnerAdvancedSearch",
            "isActiveFilter": False,
        },
        {
            "searchSection": "languagesSearch",
            "type": "languagesAdvancedSearch",
            "isActiveFilter": False,
        },
    ]


def _apply_date(
    filters: list[dict[str, Any]],
    year_from: int | None,
    year_to: int | None,
    year_in: int | None,
) -> None:
    for f in filters:
        if f.get("searchSection") != "dateSearch":
            continue
        if year_in is not None:
            f["isActiveFilter"] = True
            f["dateFilterType"] = "in"
            f["dateYear"] = str(year_in)
            return
        if year_from is not None or year_to is not None:
            a = year_from if year_from is not None else year_to
            b = year_to if year_to is not None else year_from
            assert a is not None and b is not None
            f["isActiveFilter"] = True
            f["dateFilterType"] = "between"
            f["dateYear"] = str(a)
            f["dateBYear"] = str(b)
            return


def advanced_search(
    *,
    people_ids: list[int] | None = None,
    place_ids: list[int] | None = None,
    collection: str | None = None,
    series: str | None = None,
    volume: str | None = None,
    insert: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    year_in: int | None = None,
    start: int = 0,
    limit: int = 50,
    order_by: str = "docYear",
    order: str = "asc",
    news_feed: bool = False,
) -> Any:
    """POST de/advancedsearch/advancedSearchResults/{start}/{limit}/{orderBy}/{order}.

    Volume-page 'Documents related to this Volume' uses archival location with
    collection name + volume *name* (e.g. MdP volume=\"181\"), not volumeId.
    """
    filters = _inactive_filters()
    archival_active = any(x is not None for x in (collection, series, volume, insert))
    if archival_active:
        for f in filters:
            if f.get("searchSection") == "archivalLocationSearch":
                f["isActiveFilter"] = True
                f["collection"] = collection
                f["series"] = series
                f["volume"] = volume
                f["insert"] = insert
    if people_ids:
        for f in filters:
            if f.get("searchSection") == "peopleSearch":
                f["isActiveFilter"] = True
                # MIA person-doc helper posts bare IDs; UI posts objects. IDs work.
                f["people"] = list(people_ids)
    if place_ids:
        for f in filters:
            if f.get("searchSection") == "placesSearch":
                f["isActiveFilter"] = True
                f["places"] = list(place_ids)
    _apply_date(filters, year_from, year_to, year_in)
    # Minimal person-only body (same as findDocPeople) is also accepted; use full
    # array when combining place/date/archival so inactive slots stay present.
    person_only = (
        people_ids
        and not place_ids
        and not archival_active
        and year_from is None
        and year_to is None
        and year_in is None
    )
    if person_only:
        body: object = [
            {
                "people": list(people_ids),
                "isActiveFilter": True,
                "type": "peopleAdvancedSearch",
                "searchSection": "peopleSearch",
            }
        ]
    else:
        body = filters
    path = (
        f"de/advancedsearch/advancedSearchResults/"
        f"{start}/{limit}/{order_by}/{order}"
        f"/?isNewsFeedSearch={'true' if news_feed else 'false'}"
    )
    return post_json(path, body)


def advanced_search_all(
    *,
    page_size: int = 20,
    max_docs: int | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Page through advancedSearchResults until exhausted (or max_docs)."""
    start = 0
    order_by = kwargs.pop("order_by", "docYear")
    order = kwargs.pop("order", "asc")
    all_docs: list[Any] = []
    last: Any = None
    while True:
        limit = page_size
        if max_docs is not None:
            remaining = max_docs - len(all_docs)
            if remaining <= 0:
                break
            limit = min(page_size, remaining)
        resp = advanced_search(
            start=start,
            limit=limit,
            order_by=order_by,
            order=order,
            **kwargs,
        )
        last = resp
        batch = _extract_docs(resp)
        if not batch:
            break
        all_docs.extend(batch)
        if len(batch) < limit:
            break
        start += limit
    return {
        "status": (last or {}).get("status") if isinstance(last, dict) else None,
        "message": (last or {}).get("message") if isinstance(last, dict) else None,
        "n_docs": len(all_docs),
        "data": all_docs,
        "last_page": last,
    }


def _extract_docs(payload: Any) -> list[Any]:
    if not isinstance(payload, dict):
        return []
    data = payload.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        docs = (
            data.get("docs")
            or data.get("documents")
            or data.get("results")
            or data.get("data")
        )
        if isinstance(docs, list):
            return docs
    return []


def word_search(
    query: str,
    *,
    start: int = 0,
    limit: int = 50,
    order_by: str = "docYear",
    order: str = "asc",
    owner: object | None = None,
    search_type: str = "DE_SYNOPSIS",
) -> Any:
    """POST search/de/wordSearch — UI searchType is DE_SYNOPSIS or DE_TRANSCRIPTION.

    ``ALL`` is rejected by the API. ``owner`` must be the logged-in account string.
    """
    # UI: quoted tokens -> matchSearchWords; bare -> partialSearchWords
    tokens = []
    buf = ""
    in_q = False
    for ch in query.strip():
        if ch == '"':
            in_q = not in_q
            buf += ch
            continue
        if ch.isspace() and not in_q:
            if buf:
                tokens.append(buf)
                buf = ""
            continue
        buf += ch
    if buf:
        tokens.append(buf)
    match_parts: list[str] = []
    partial_parts: list[str] = []
    for tok in tokens:
        if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"':
            match_parts.append(tok[1:-1])
        else:
            partial_parts.append(tok)
    # UI: params.owner = $rootScope.me.account (string account id).
    own: Any
    if owner is None:
        own = get_me_account()
    elif isinstance(owner, dict):
        own = owner.get("account") or get_me_account()
    else:
        own = owner
    params: dict[str, Any] = {
        "owner": own,
        "partialSearchWords": (" ".join(partial_parts) + " ") if partial_parts else "",
        "matchSearchWords": (" ".join(match_parts) + " ") if match_parts else "",
        "searchType": search_type,
        "onlyMyEntities": False,
        "everyoneElsesEntities": False,
        "allEntities": True,
    }
    path = f"search/de/wordSearch/{start}/{limit}/{order_by}/{order}"
    return post_json(path, params)


def find_mdp_volume(volume_name: str) -> list[dict[str, Any]]:
    """Search Mediceo del Principato (collectionId=1) volumes by name."""
    q = urllib.parse.quote(volume_name, safe="")
    resp = get_json(f"upload/findVolume/1?q={q}&limit=30")
    return list(resp.get("volume") or [])


def docs_in_volume(
    volume_id: int,
    *,
    query: str = "",
    page: int = 0,
    per_page: int = 100,
) -> Any:
    url = (
        f"document/findDocumentsInVolume/{volume_id}"
        f"?page={page}&perPage={per_page}&notChildren=true"
    )
    if query:
        url += "&q=" + urllib.parse.quote(query, safe="")
    return get_json(url)


def people_related_to_document(doc_id: int) -> Any:
    return get_json(f"document/findPeopleRelatedtoDocument/{doc_id}")


def _doc_date(doc: dict[str, Any]) -> str:
    # Response shapes vary; try common fields.
    for key in ("docYear", "docModernYear", "year"):
        if doc.get(key):
            y = doc.get(key)
            m = doc.get("docMonth") or doc.get("month") or 0
            d = doc.get("docDay") or doc.get("day") or 0
            return f"{y}-{m:02d}-{d:02d}" if isinstance(y, int) else str(y)
    date = doc.get("date") or {}
    if isinstance(date, dict):
        y = date.get("docModernYear") or date.get("docYear") or "?"
        m = date.get("docMonth") or 0
        d = date.get("docDay") or 0
        try:
            return f"{int(y)}-{int(m):02d}-{int(d):02d}"
        except (TypeError, ValueError):
            return str(y)
    return "?"


def _summarize_docs(payload: Any, limit: int = 30) -> None:
    if not isinstance(payload, dict):
        print(payload)
        return
    print("status:", payload.get("status"), "|", payload.get("message"))
    docs = _extract_docs(payload)
    if payload.get("n_docs") is not None and not docs:
        # advanced_search_all shape
        raw = payload.get("data")
        if isinstance(raw, list):
            docs = raw
    print(f"n_docs={len(docs)}")
    for doc in docs[:limit]:
        if not isinstance(doc, dict):
            print(" ", doc)
            continue
        did = doc.get("documentId") or doc.get("id")
        producers = doc.get("producers") or []
        pname = ""
        if producers and isinstance(producers[0], dict):
            pname = producers[0].get("mapNameLf") or ""
        places = doc.get("placeOfOrigin") or doc.get("places") or []
        pl = ""
        if places and isinstance(places[0], dict):
            pl = places[0].get("placeName") or ""
        recip = ""
        recipients = doc.get("recipients") or doc.get("addressees") or []
        if recipients and isinstance(recipients[0], dict):
            recip = (
                recipients[0].get("mapNameLf")
                or recipients[0].get("name")
                or ""
            )
        syn = (doc.get("synopsis") or doc.get("shortSynopsis") or "")[:60]
        print(
            f"  doc={did} date={_doc_date(doc)} "
            f"from={pname[:36]!r} to={recip[:36]!r} place={pl[:28]!r}"
        )
        if syn:
            print(f"    syn={syn!r}")


def cmd_people(args: argparse.Namespace) -> None:
    people = find_people(args.query)
    path = save(f"people_{args.query.replace(' ', '_')}.json", people)
    print(f"n={len(people)} -> {path}")
    for p in people:
        print(
            f"  id={p.get('id')} {p.get('mapNameLf')} "
            f"b={p.get('bornYear')} d={p.get('deathYear')}"
        )


def cmd_places(args: argparse.Namespace) -> None:
    places = find_places(args.query)
    path = save(f"places_{args.query.replace(' ', '_')}.json", places)
    print(f"n={len(places)} -> {path}")
    for p in places:
        print(f"  id={p.get('id')} {p.get('placeName')}")


def cmd_docs_person(args: argparse.Namespace) -> None:
    resp = advanced_search(
        people_ids=[args.person_id],
        year_from=args.year_from,
        year_to=args.year_to,
        year_in=args.year_in,
        start=args.start,
        limit=args.limit,
    )
    path = save(f"docs_person_{args.person_id}.json", resp)
    print(f"wrote {path}")
    _summarize_docs(resp, limit=args.limit)


def cmd_docs_place(args: argparse.Namespace) -> None:
    places = find_places(args.query)
    if not places:
        raise SystemExit(f"No places for {args.query!r}")
    pid = int(places[0]["id"])
    print(f"using place id={pid} {places[0].get('placeName')}")
    resp = advanced_search(
        place_ids=[pid],
        year_from=args.year_from,
        year_to=args.year_to,
        year_in=args.year_in,
        start=args.start,
        limit=args.limit,
    )
    path = save(f"docs_place_{pid}.json", resp)
    print(f"wrote {path}")
    _summarize_docs(resp, limit=args.limit)


def cmd_word(args: argparse.Namespace) -> None:
    resp = word_search(
        args.query,
        start=args.start,
        limit=args.limit,
        search_type=args.search_type,
    )
    safe = args.query.replace('"', "").replace(" ", "_")[:40]
    path = save(f"word_{args.search_type}_{safe}.json", resp)
    print(f"wrote {path}")
    _summarize_docs(resp, limit=args.limit)


def cmd_document(args: argparse.Namespace) -> None:
    resp = find_document(args.doc_id)
    path = save(f"document_{args.doc_id}.json", resp)
    print(f"wrote {path}")
    print(json.dumps(resp, ensure_ascii=False, indent=2)[:2000])


def cmd_volume(args: argparse.Namespace) -> None:
    resp = find_volume_description(args.volume_id)
    path = save(f"volume_{args.volume_id}.json", resp)
    print(f"wrote {path}")
    print(json.dumps(resp, ensure_ascii=False, indent=2)[:2000])


def cmd_spinelli_hunt(args: argparse.Namespace) -> None:
    """Targeted hunt for Benedetto Spinelli / Marradi 1534–1540."""
    report: dict[str, Any] = {"people": [], "hits": []}

    people = find_people("Spinelli")
    report["people"] = people
    save("hunt_people_Spinelli.json", people)

    # Prefer birth/death near 1483–1547; also keep name matches with Benedetto.
    scored: list[tuple[int, dict[str, Any]]] = []
    for p in people:
        name = (p.get("mapNameLf") or "").lower()
        score = 0
        if "benedetto" in name:
            score += 100
        by = p.get("bornYear")
        dy = p.get("deathYear")
        try:
            by_i = int(by) if by is not None else None
            dy_i = int(dy) if dy is not None else None
        except (TypeError, ValueError):
            by_i = dy_i = None
        if by_i is not None and 1475 <= by_i <= 1495:
            score += 40
        if dy_i is not None and 1540 <= dy_i <= 1555:
            score += 40
        if "marradi" in name:
            score += 20
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    print("=== candidate Spinelli people ===")
    for score, p in scored[:15]:
        print(
            f"  score={score} id={p.get('id')} {p.get('mapNameLf')} "
            f"b={p.get('bornYear')} d={p.get('deathYear')}"
        )

    targets = [p for _, p in scored[:8]] or people[:10]
    for p in targets:
        pid = int(p["id"])
        print(f"\n=== docs for person {pid} {p.get('mapNameLf')} ===")
        resp = advanced_search(
            people_ids=[pid],
            year_from=1534,
            year_to=1547,
            start=0,
            limit=args.limit,
        )
        save(f"hunt_docs_person_{pid}_1534_1547.json", resp)
        _summarize_docs(resp, limit=20)
        report["hits"].append({"person": p, "docs": resp})

        # Also unfiltered (first page) in case date filter is sparse.
        resp2 = advanced_search(people_ids=[pid], start=0, limit=min(30, args.limit))
        save(f"hunt_docs_person_{pid}_all.json", resp2)
        _summarize_docs(resp2, limit=15)

    places = find_places("Marradi")
    save("hunt_places_Marradi.json", places)
    if places:
        pl_id = int(places[0]["id"])
        print(f"\n=== docs place Marradi id={pl_id} 1534–1540 ===")
        resp = advanced_search(
            place_ids=[pl_id],
            year_from=1534,
            year_to=1540,
            start=0,
            limit=args.limit,
        )
        save(f"hunt_docs_place_{pl_id}_1534_1540.json", resp)
        _summarize_docs(resp, limit=30)
        report["hits"].append({"place": places[0], "docs": resp})

    for q in (
        "Spinelli Marradi",
        '"Spinelli"',
        "Capitano Marradi",
        "occhi di vetro",
        "occhiali",
    ):
        print(f"\n=== word search {q!r} ===")
        resp = word_search(q, start=0, limit=min(40, args.limit))
        safe = q.replace('"', "").replace(" ", "_")[:40]
        save(f"hunt_word_{safe}.json", resp)
        _summarize_docs(resp, limit=15)
        report["hits"].append({"word": q, "docs": resp})

    path = save("hunt_spinelli_report.json", report)
    print(f"\nfull report -> {path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MIA search CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("people", help="SEARCH PEOPLE")
    sp.add_argument("query")
    sp.set_defaults(func=cmd_people)

    sp = sub.add_parser("places", help="SEARCH PLACES")
    sp.add_argument("query")
    sp.set_defaults(func=cmd_places)

    sp = sub.add_parser("docs-person", help="Advanced search by person id")
    sp.add_argument("person_id", type=int)
    sp.add_argument("--year-from", type=int, default=None)
    sp.add_argument("--year-to", type=int, default=None)
    sp.add_argument("--year-in", type=int, default=None)
    sp.add_argument("--start", type=int, default=0)
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_docs_person)

    sp = sub.add_parser("docs-place", help="Advanced search by place name")
    sp.add_argument("query")
    sp.add_argument("--year-from", type=int, default=None)
    sp.add_argument("--year-to", type=int, default=None)
    sp.add_argument("--year-in", type=int, default=None)
    sp.add_argument("--start", type=int, default=0)
    sp.add_argument("--limit", type=int, default=50)
    sp.set_defaults(func=cmd_docs_place)

    sp = sub.add_parser("word", help="Word / transcription search")
    sp.add_argument("query")
    sp.add_argument("--start", type=int, default=0)
    sp.add_argument("--limit", type=int, default=50)
    sp.add_argument(
        "--type",
        dest="search_type",
        default="DE_SYNOPSIS",
        choices=("DE_SYNOPSIS", "DE_TRANSCRIPTION"),
        help="MIA wordSearch searchType (ALL is rejected)",
    )
    sp.set_defaults(func=cmd_word)

    sp = sub.add_parser("document", help="Fetch one document by id")
    sp.add_argument("doc_id", type=int)
    sp.set_defaults(func=cmd_document)

    sp = sub.add_parser("volume-desc", help="Fetch volume description by id")
    sp.add_argument("volume_id", type=int)
    sp.set_defaults(func=cmd_volume)

    sp = sub.add_parser("volume-find", help="Find MdP volume by name (e.g. 181)")
    sp.add_argument("volume_name")
    sp.set_defaults(func=cmd_volume_find)

    sp = sub.add_parser(
        "docs-volume",
        help="Legacy findDocumentsInVolume by volumeId (often empty; prefer docs-mdp)",
    )
    sp.add_argument("volume_id", type=int)
    sp.add_argument("--q", default="", help="optional query filter")
    sp.add_argument("--page", type=int, default=0)
    sp.add_argument("--limit", type=int, default=100)
    sp.set_defaults(func=cmd_docs_volume)

    sp = sub.add_parser(
        "docs-mdp",
        help=(
            "Advanced search by MdP filza name — same as volume page "
            "'Documents related to this Volume' (e.g. docs-mdp 181)"
        ),
    )
    sp.add_argument("volume", help="Volume/filza name as in UI, e.g. 181")
    sp.add_argument(
        "--collection",
        default="Mediceo del Principato",
        help="Collection display name (default: Mediceo del Principato)",
    )
    sp.add_argument("--series", default=None)
    sp.add_argument("--insert", default=None)
    sp.add_argument("--year-from", type=int, default=None)
    sp.add_argument("--year-to", type=int, default=None)
    sp.add_argument("--year-in", type=int, default=None)
    sp.add_argument("--start", type=int, default=0)
    sp.add_argument(
        "--limit",
        type=int,
        default=20,
        help="page size (UI default 20)",
    )
    sp.add_argument(
        "--all",
        action="store_true",
        help="page through all results (e.g. all 61 for vol 181)",
    )
    sp.add_argument("--max", type=int, default=None, help="cap when using --all")
    sp.add_argument("--order-by", default="docYear")
    sp.add_argument("--order", default="asc", choices=("asc", "desc"))
    sp.set_defaults(func=cmd_docs_mdp)

    sp = sub.add_parser("spinelli-hunt", help="Run Spinelli/Marradi 1534–1540 hunt")
    sp.add_argument("--limit", type=int, default=80)
    sp.set_defaults(func=cmd_spinelli_hunt)

    return p


def cmd_volume_find(args: argparse.Namespace) -> None:
    vols = find_mdp_volume(args.volume_name)
    path = save(f"volume_find_{args.volume_name}.json", vols)
    print(f"n={len(vols)} -> {path}")
    for v in vols:
        print(
            f"  volumeId={v.get('volumeId')} name={v.get('volumeName')} "
            f"aeCount={v.get('aeCount')}"
        )
        try:
            vd = find_volume_description(int(v["volumeId"]))
            data = ((vd.get("data") or {}).get("data") or vd.get("data") or {})
            if isinstance(data, dict):
                print(
                    f"    years={data.get('startYear')}-{data.get('endYear')} "
                    f"sezione={data.get('sezione')}"
                )
        except Exception as e:
            print("    desc err", e)


def cmd_docs_mdp(args: argparse.Namespace) -> None:
    """Same call as volume page 'Documents related to this Volume' (61 for 181)."""
    collection = args.collection
    volume = str(args.volume)
    kwargs: dict[str, Any] = {
        "collection": collection,
        "series": args.series,
        "volume": volume,
        "insert": args.insert,
        "year_from": args.year_from,
        "year_to": args.year_to,
        "year_in": args.year_in,
        "order_by": args.order_by,
        "order": args.order,
    }
    if args.all:
        resp = advanced_search_all(page_size=args.limit, max_docs=args.max, **kwargs)
        path = save(f"docs_mdp_{volume}_all.json", resp)
    else:
        resp = advanced_search(start=args.start, limit=args.limit, **kwargs)
        path = save(f"docs_mdp_{volume}_{args.start}_{args.limit}.json", resp)
    print(f"wrote {path}")
    _summarize_docs(resp, limit=min(args.limit if not args.all else 80, 80))
    # Quick Spinelli / Marradi scan on returned rows
    docs = _extract_docs(resp) if not args.all else list(resp.get("data") or [])
    needles = ("spinelli", "marradi", "capitano", "occhi", "occhiali", "vetro")
    hits = 0
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        blob = json.dumps(doc, ensure_ascii=False).lower()
        if any(n in blob for n in needles):
            hits += 1
            did = doc.get("documentId") or doc.get("id")
            print(f"  HIT needle doc={did} date={_doc_date(doc)}")
    print(f"needle_hits={hits} / {len(docs)}")


def cmd_docs_volume(args: argparse.Namespace) -> None:
    resp = docs_in_volume(
        args.volume_id, query=args.q, page=args.page, per_page=args.limit
    )
    path = save(f"docs_volume_{args.volume_id}.json", resp)
    print(f"wrote {path}")
    print("status:", resp.get("status"), resp.get("message"), "total", resp.get("totalCount"))
    data = resp.get("data") or []
    if isinstance(data, list):
        for d in data[:30]:
            if isinstance(d, dict):
                print(
                    f"  doc={d.get('documentId')} "
                    f"{d.get('docYear')}-{d.get('docMonth')}-{d.get('docDay')}"
                )
            else:
                print(" ", d)


def main() -> None:
    if not MIA_COOKIE.strip():
        print(
            "Missing MIA session: set MIA_COOKIE or write config/mia_session.local",
            file=sys.stderr,
        )
        sys.exit(2)
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
