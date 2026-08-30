"""Persée Linked Data SPARQL client (data.persee.fr), default via local CONNECT gateway.

Real endpoint (Virtuoso):
  https://data.persee.fr/sparql

Note: ``/charte/css/sparqlendpoint.css`` is Virtuoso UI chrome, not the API.

Proxy (default):
  http://127.0.0.1:12309
  Local gateway often MITMs TLS → insecure verify is on by default when proxy
  points at 127.0.0.1 / localhost.
"""
from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Mapping


DEFAULT_PROXY = "http://127.0.0.1:12309"
SPARQL_URL = "https://data.persee.fr/sparql"
DEFAULT_GRAPH = "http://data.persee.fr"
USER_AGENT = "eyeglasses-hypothesis/persee-sparql (research pipeline)"
REFERER = "https://data.persee.fr/sparql"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def proxy_implies_insecure(proxy: str | None) -> bool:
    if not proxy:
        return False
    host = proxy.split("://", 1)[-1].split("@")[-1].split(":")[0].lower()
    return host in {"127.0.0.1", "localhost", "::1"}


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


def bindings_to_rows(payload: Mapping[str, object]) -> list[dict[str, str]]:
    """Flatten SPARQL JSON bindings to {var: value-string} rows."""
    results = payload.get("results")
    if not isinstance(results, Mapping):
        return []
    raw = results.get("bindings")
    if not isinstance(raw, list):
        return []
    rows: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        row: dict[str, str] = {}
        for var, cell in item.items():
            if isinstance(cell, Mapping) and "value" in cell:
                row[str(var)] = str(cell["value"])
            else:
                row[str(var)] = str(cell)
        rows.append(row)
    return rows


def query(
    sparql: str,
    *,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    method: str = "GET",
    graph: str = DEFAULT_GRAPH,
    timeout: float = 60.0,
    retries: int = 3,
    retry_sleep: float = 1.2,
    opener: urllib.request.OpenerDirector | None = None,
) -> dict[str, object]:
    """Run a SPARQL SELECT/ASK; return parsed ``application/sparql-results+json``."""
    if insecure is None:
        insecure = proxy_implies_insecure(proxy)
    op = opener or make_opener(proxy, insecure=insecure)
    params = {
        "default-graph-uri": graph,
        "query": sparql.strip(),
        "format": "application/sparql-results+json",
        "timeout": "0",
    }
    body = urllib.parse.urlencode(params).encode()
    method_u = method.upper()
    last_err: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            if method_u == "GET":
                url = SPARQL_URL + "?" + urllib.parse.urlencode(params)
                req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/sparql-results+json",
                        "Referer": REFERER,
                    },
                    method="GET",
                )
            elif method_u == "POST":
                req = urllib.request.Request(
                    SPARQL_URL,
                    data=body,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/sparql-results+json",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Referer": REFERER,
                    },
                    method="POST",
                )
            else:
                raise ValueError(f"unsupported method {method!r}")
            with op.open(req, timeout=timeout) as resp:
                raw = resp.read()
            payload = json.loads(raw.decode("utf-8", errors="replace"))
            if not isinstance(payload, dict):
                raise ValueError(f"unexpected JSON root type {type(payload).__name__}")
            return payload
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
            ValueError,
        ) as e:
            last_err = e
            if attempt >= retries:
                break
            time.sleep(retry_sleep * attempt)
    raise RuntimeError(f"Persée SPARQL failed after {retries} tries: {last_err}")


def query_rows(
    sparql: str,
    *,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    method: str = "GET",
    graph: str = DEFAULT_GRAPH,
    timeout: float = 60.0,
    retries: int = 3,
    retry_sleep: float = 1.2,
    opener: urllib.request.OpenerDirector | None = None,
) -> list[dict[str, str]]:
    payload = query(
        sparql,
        proxy=proxy,
        insecure=insecure,
        method=method,
        graph=graph,
        timeout=timeout,
        retries=retries,
        retry_sleep=retry_sleep,
        opener=opener,
    )
    return bindings_to_rows(payload)


def smoke(
    *,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    method: str = "GET",
    timeout: float = 30.0,
) -> tuple[bool, str]:
    """Tiny SELECT; returns (ok, detail)."""
    try:
        rows = query_rows(
            "SELECT (1 AS ?x) WHERE {}",
            proxy=proxy,
            insecure=insecure,
            method=method,
            timeout=timeout,
            retries=2,
        )
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    if rows and rows[0].get("x") == "1":
        return True, "ok"
    return False, f"unexpected rows={rows!r}"


def search_persons(
    name_substr: str,
    *,
    limit: int = 50,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    method: str = "GET",
    timeout: float = 60.0,
) -> list[dict[str, str]]:
    """Match foaf:Person by case-insensitive substring on foaf:name."""
    needle = name_substr.strip().lower().replace("\\", "\\\\").replace('"', '\\"')
    lim = max(1, int(limit))
    sparql = f"""
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX schema: <http://schema.org/>
SELECT ?person ?name ?birth ?death WHERE {{
  ?person a foaf:Person ; foaf:name ?name .
  FILTER(CONTAINS(LCASE(STR(?name)), "{needle}"))
  OPTIONAL {{ ?person schema:birthDate ?birth }}
  OPTIONAL {{ ?person schema:deathDate ?death }}
}} LIMIT {lim}
"""
    return query_rows(
        sparql,
        proxy=proxy,
        insecure=insecure,
        method=method,
        timeout=timeout,
    )


def documents_for_person_uri(
    person_uri: str,
    *,
    limit: int = 50,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    method: str = "GET",
    timeout: float = 90.0,
) -> list[dict[str, str]]:
    """Docs that link to a Persée authority Person URI (any predicate)."""
    uri = person_uri.strip()
    if not uri.startswith("http"):
        raise ValueError(f"person_uri must be http(s) URI, got {uri!r}")
    lim = max(1, int(limit))
    sparql = f"""
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
SELECT ?doc ?rel ?title ?date WHERE {{
  ?doc ?rel <{uri}> .
  FILTER(?rel != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
  OPTIONAL {{ ?doc dcterms:title ?title }}
  OPTIONAL {{ ?doc dc:title ?title }}
  OPTIONAL {{ ?doc dcterms:date ?date }}
  OPTIONAL {{ ?doc dc:date ?date }}
}} LIMIT {lim}
"""
    return query_rows(
        sparql,
        proxy=proxy,
        insecure=insecure,
        method=method,
        timeout=timeout,
    )


def prefix_block() -> str:
    """Common prefixes for interactive / CLI queries."""
    return """PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX schema: <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
"""
