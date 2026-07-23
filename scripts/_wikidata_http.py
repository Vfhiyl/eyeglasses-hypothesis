"""Python HTTPS SPARQL client for query.wikidata.org via optional HTTP CONNECT proxy.

Uses the stdlib ssl stack (same as check_wikidata_cert.py) — not curl.
Wikidata SPARQL prefers Let's Encrypt YE1; CONNECT anti-MITM probe uses OS trust
store verification (any publicly trusted chain) after a successful handshake.
"""
from __future__ import annotations

import hashlib
import socket
import ssl
import urllib.parse
from pathlib import Path

WIKIDATA_HOST = "query.wikidata.org"
WIKIDATA_PORT = 443
EXPECTED_ISSUER_CN = "YE1"
EXPECTED_ISSUER_O = "Let's Encrypt"
# Advisory: current Wikimedia leaf fp (rotates on renew).
KNOWN_GOOD_FP_SHA256 = (
    "061e7990417d681c3d136bceaccf8a3df70bf002b86181ae0aac1b5f2da09d21"
)
USER_AGENT = "eyeglasses-hypothesis/1.4 (python-ssl research pipeline)"


def _rdn_value(peercert: dict, field: str, key: str) -> str:
    for rdn in peercert.get(field, ()):
        for k, v in rdn:
            if k == key:
                return str(v)
    return ""


def _is_mitm_issuer(issuer_cn: str, issuer_o: str) -> bool:
    blob = f"{issuer_cn}|{issuer_o}"
    return "MySQL_Server" in blob or "Auto_Generated_CA" in blob


def peer_is_letsencrypt_ye1(peercert: dict, *, der: bytes | None = None) -> tuple[bool, str]:
    """Strict YE1 check (Wikidata SPARQL path). Rejects MITM and non-YE1 issuers."""
    issuer_cn = _rdn_value(peercert, "issuer", "commonName")
    issuer_o = _rdn_value(peercert, "issuer", "organizationName")
    subject_cn = _rdn_value(peercert, "subject", "commonName")

    if _is_mitm_issuer(issuer_cn, issuer_o):
        return False, f"MITM-like issuer CN={issuer_cn}"

    if issuer_cn != EXPECTED_ISSUER_CN:
        return False, f"issuer CN={issuer_cn!r} (want YE1), subject={subject_cn!r}"

    if issuer_o and EXPECTED_ISSUER_O.lower() not in issuer_o.lower():
        return False, f"issuer O={issuer_o!r} (want Let's Encrypt)"

    fp = hashlib.sha256(der).hexdigest() if der else ""
    note = f"YE1 OK subject={subject_cn} fp={fp[:16]}…" if fp else f"YE1 OK subject={subject_cn}"
    return True, note


def peer_is_trusted_public_ca(peercert: dict, *, der: bytes | None = None) -> tuple[bool, str]:
    """Allowlist gate (hunter / optional): Let's Encrypt YE1 *or* DigiCert."""
    issuer_cn = _rdn_value(peercert, "issuer", "commonName")
    issuer_o = _rdn_value(peercert, "issuer", "organizationName")
    subject_cn = _rdn_value(peercert, "subject", "commonName")
    issuer_blob = f"{issuer_cn} {issuer_o}".strip()

    if _is_mitm_issuer(issuer_cn, issuer_o):
        return False, f"MITM-like issuer CN={issuer_cn}"

    ye1_ok = issuer_cn == EXPECTED_ISSUER_CN and (
        not issuer_o or EXPECTED_ISSUER_O.lower() in issuer_o.lower()
    )
    digicert_ok = "digicert" in issuer_blob.lower()

    if not (ye1_ok or digicert_ok):
        return (
            False,
            f"issuer CN={issuer_cn!r} O={issuer_o!r} (want YE1 or DigiCert), "
            f"subject={subject_cn!r}",
        )

    fp = hashlib.sha256(der).hexdigest() if der else ""
    kind = "YE1" if ye1_ok else "DigiCert"
    note = (
        f"{kind} OK subject={subject_cn} fp={fp[:16]}…"
        if fp
        else f"{kind} OK subject={subject_cn}"
    )
    return True, note


def peer_is_os_trusted_leaf(peercert: dict, *, der: bytes | None = None) -> tuple[bool, str]:
    """Post-handshake leaf check for CONNECT anti-MITM probe.

    Call only after ssl.create_default_context().wrap_socket succeeded (OS trust
    store already verified the chain). Rejects known MITM-like issuer strings.
    """
    issuer_cn = _rdn_value(peercert, "issuer", "commonName")
    issuer_o = _rdn_value(peercert, "issuer", "organizationName")
    subject_cn = _rdn_value(peercert, "subject", "commonName")

    if _is_mitm_issuer(issuer_cn, issuer_o):
        return False, f"MITM-like issuer CN={issuer_cn}"

    fp = hashlib.sha256(der).hexdigest() if der else ""
    note = (
        f"OS-trust OK issuerCN={issuer_cn or '?'} subject={subject_cn} fp={fp[:16]}…"
        if fp
        else f"OS-trust OK issuerCN={issuer_cn or '?'} subject={subject_cn}"
    )
    return True, note


def _read_header(sock: socket.socket, max_bytes: int = 65536) -> bytes:
    buf = b""
    while b"\r\n\r\n" not in buf and len(buf) < max_bytes:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def _parse_proxy(proxy: str | None) -> tuple[str, int, str] | None:
    """Return (host, port, proto). Accepts http://, socks5://, socks4://, or host:port."""
    if not proxy:
        return None
    p = proxy.strip()
    proto = "http"
    lower = p.lower()
    if "://" in lower:
        scheme, rest = p.split("://", 1)
        scheme = scheme.lower()
        if scheme in ("socks5", "socks"):
            proto = "socks5"
        elif scheme == "socks4":
            proto = "socks4"
        else:
            proto = "http"
        p = rest
    else:
        p = p.replace("https://", "").replace("http://", "")
    host, _, port_s = p.rpartition(":")
    return host, int(port_s), proto


def open_wikidata_ssl_socket(
    proxy: str | None,
    *,
    timeout: float = 60.0,
    require_ye1: bool = True,
) -> tuple[ssl.SSLSocket, str]:
    """CONNECT (optional) + TLS to query.wikidata.org. Returns (ssock, cert_note)."""
    from _upstream_tunnel import open_upstream_tunnel

    prox = _parse_proxy(proxy)
    if prox:
        host, port, proto = prox
        sock = open_upstream_tunnel(
            proto, host, port, WIKIDATA_HOST, WIKIDATA_PORT, timeout
        )
        sock.settimeout(timeout)
    else:
        sock = socket.create_connection((WIKIDATA_HOST, WIKIDATA_PORT), timeout=timeout)
        sock.settimeout(timeout)

    ctx = ssl.create_default_context()
    ssock = ctx.wrap_socket(sock, server_hostname=WIKIDATA_HOST)
    der = ssock.getpeercert(binary_form=True) or b""
    peercert = ssock.getpeercert() or {}
    ok, note = peer_is_letsencrypt_ye1(peercert, der=der)
    if require_ye1 and not ok:
        try:
            ssock.close()
        except Exception:
            pass
        raise ssl.SSLError(f"peer cert rejected: {note}")
    return ssock, note


def _http_exchange(ssock: ssl.SSLSocket, request: bytes, timeout: float) -> bytes:
    ssock.settimeout(timeout)
    ssock.sendall(request)
    # Read headers
    header = _read_header(ssock)
    if b"\r\n\r\n" not in header:
        raise OSError("truncated HTTP response headers")
    head, rest = header.split(b"\r\n\r\n", 1)
    status_line = head.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
    if not status_line.startswith("HTTP/1.") or " 200" not in status_line:
        raise OSError(f"HTTP {status_line}")

    headers = {}
    for line in head.split(b"\r\n")[1:]:
        if b":" in line:
            k, v = line.split(b":", 1)
            headers[k.decode().lower()] = v.strip().decode(errors="replace")

    body = rest
    if "content-length" in headers:
        need = int(headers["content-length"])
        while len(body) < need:
            chunk = ssock.recv(min(65536, need - len(body)))
            if not chunk:
                break
            body += chunk
        return body

    # chunked or close-delimited
    if headers.get("transfer-encoding", "").lower() == "chunked":
        return _read_chunked(ssock, body)
    # read until close
    while True:
        chunk = ssock.recv(65536)
        if not chunk:
            break
        body += chunk
    return body


def _read_chunked(ssock: ssl.SSLSocket, initial: bytes) -> bytes:
    buf = initial
    out = b""
    while True:
        while b"\r\n" not in buf:
            chunk = ssock.recv(4096)
            if not chunk:
                return out
            buf += chunk
        line, buf = buf.split(b"\r\n", 1)
        size_s = line.split(b";", 1)[0].strip()
        try:
            size = int(size_s, 16)
        except ValueError as e:
            raise OSError(f"bad chunk size: {line!r}") from e
        if size == 0:
            return out
        while len(buf) < size + 2:
            chunk = ssock.recv(65536)
            if not chunk:
                out += buf[:size]
                return out
            buf += chunk
        out += buf[:size]
        buf = buf[size + 2 :]  # skip trailing CRLF


def post_sparql(
    query: str,
    dest: Path,
    *,
    proxy: str | None = None,
    timeout: float = 90.0,
    require_ye1: bool = True,
) -> tuple[bool, str]:
    """POST SPARQL to Wikidata; write body to dest. Returns (ok, detail)."""
    ssock = None
    try:
        ssock, cert_note = open_wikidata_ssl_socket(
            proxy, timeout=min(timeout, 60.0), require_ye1=require_ye1
        )
        body = urllib.parse.urlencode({"query": query.strip()}).encode()
        req = (
            b"POST /sparql HTTP/1.1\r\n"
            + f"Host: {WIKIDATA_HOST}\r\n".encode()
            + f"User-Agent: {USER_AGENT}\r\n".encode()
            + b"Accept: application/sparql-results+xml, text/csv;q=0.8, */*;q=0.1\r\n"
            + b"Content-Type: application/x-www-form-urlencoded\r\n"
            + f"Content-Length: {len(body)}\r\n".encode()
            + b"Connection: close\r\n"
            + b"\r\n"
            + body
        )
        resp = _http_exchange(ssock, req, timeout)
        if b"REMOTE_ADDR" in resp[:500] or b"REQUEST_URI" in resp[:500]:
            return False, f"proxy echo/MITM body ({cert_note})"
        dest.write_bytes(resp)
        if b"</sparql>" in resp[-1024:] or (b"person" in resp[:200] and b"," in resp[:200]):
            return True, cert_note
        return False, f"unexpected body ({cert_note}) size={len(resp)}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    finally:
        if ssock is not None:
            try:
                ssock.close()
            except Exception:
                pass


def sparql_smoke(proxy: str | None = None, timeout: float = 25.0) -> tuple[bool, str]:
    """Tiny SPARQL check; requires YE1 cert + literal 42 in XML."""
    from tempfile import NamedTemporaryFile

    q = "SELECT ?x WHERE { BIND(42 AS ?x) } LIMIT 1"
    with NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        path = Path(tmp.name)
    try:
        ok, detail = post_sparql(q, path, proxy=proxy, timeout=timeout, require_ye1=True)
        if not ok:
            return False, detail
        data = path.read_bytes()
        if b">42<" not in data:
            return False, f"no BIND(42) literal in body ({detail})"
        return True, detail
    finally:
        path.unlink(missing_ok=True)
