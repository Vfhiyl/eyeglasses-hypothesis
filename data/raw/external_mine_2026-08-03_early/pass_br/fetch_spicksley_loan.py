#!/usr/bin/env python3
from __future__ import annotations

import http.cookiejar
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PASS = Path(__file__).resolve().parent
OUT = PASS / "ocr_scan"
OUT.mkdir(parents=True, exist_ok=True)
IDENT = "businesshousehol0000unse"
PROXY = "http://127.0.0.1:12309"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
ROOT = Path("/Users/admin/Desktop/proj/other/eyeglasses-hypothesis")


def main() -> None:
    session = ROOT / "config" / "ia_session.local"
    cookie = ""
    if session.is_file():
        for raw in session.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("COOKIE="):
                cookie = line.split("=", 1)[1].strip()
                break
    if not cookie:
        raise SystemExit(f"missing COOKIE= in {session}")
    jar = http.cookiejar.CookieJar()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}),
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(jar),
    )

    def set_cookie(name: str, value: str, domain: str = ".archive.org") -> None:
        jar.set_cookie(
            http.cookiejar.Cookie(
                version=0,
                name=name,
                value=value,
                port=None,
                port_specified=False,
                domain=domain,
                domain_specified=True,
                domain_initial_dot=domain.startswith("."),
                path="/",
                path_specified=True,
                secure=False,
                expires=None,
                discard=False,
                comment=None,
                comment_url=None,
                rest={},
                rfc2109=False,
            )
        )

    for part in cookie.split("; "):
        if "=" in part:
            k, v = part.split("=", 1)
            set_cookie(k, v)

    def req(
        url: str,
        data: bytes | None = None,
        retries: int = 8,
        timeout: float = 90,
        headers: dict[str, str] | None = None,
    ) -> tuple[int | None, bytes | None, dict[str, str]]:
        h = {
            "User-Agent": UA,
            "Accept": "*/*",
            "Referer": f"https://archive.org/details/{IDENT}",
        }
        if headers:
            h.update(headers)
        last: Exception | None = None
        for a in range(1, retries + 1):
            try:
                request = urllib.request.Request(
                    url,
                    data=data,
                    headers=h,
                    method="POST" if data is not None else "GET",
                )
                with opener.open(request, timeout=timeout) as resp:
                    return resp.status, resp.read(), dict(resp.headers)
            except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
                last = e
                print(f"  retry{a} {type(e).__name__}: {e}", flush=True)
                time.sleep(1.2 * a)
        print("FAIL", last)
        return None, None, {}

    print("borrow...")
    st, body, _ = req(
        "https://archive.org/services/loans/loan/",
        data=f"action=borrow_book&identifier={IDENT}".encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    print("borrow", st, (body or b"")[:200])
    st, body, _ = req(
        "https://archive.org/services/loans/loan/",
        data=f"action=create_token&identifier={IDENT}".encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    print("token", st, (body or b"").decode("utf-8", "replace"))
    if body:
        tok = json.loads(body.decode()).get("token")
        if isinstance(tok, str) and tok:
            set_cookie(f"loan-{IDENT}", tok)
            set_cookie(f"br-loan-{IDENT}", "1")
            print("set loan cookies", tok)

    print(
        "cookies:",
        sorted(
            {
                c.name
                for c in jar
                if "loan" in c.name or "search" in c.name or "logged" in c.name
            }
        ),
    )

    for fmt in ["bookreader", "pdf", "epub", "lcp_pdf", "lcp_epub"]:
        data = urllib.parse.urlencode(
            {"action": "media_url", "identifier": IDENT, "format": fmt}
        ).encode()
        st, body, _ = req(
            "https://archive.org/services/loans/loan/",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        print("media", fmt, st, (body or b"")[:300])
        if body and b"http" in body:
            (PASS / f"media_{fmt}.json").write_bytes(body)

    st, body, _ = req(f"https://archive.org/metadata/{IDENT}")
    assert body is not None
    meta = json.loads(body)
    server = meta.get("server") or meta.get("d1")
    direc = meta.get("dir")
    print("server", server, "dir", direc)

    jsia_url = (
        f"https://{server}/BookReader/BookReaderJSIA.php"
        f"?id={IDENT}&itemPath={direc}&server={server}&format=jsonp&subPrefix={IDENT}"
    )
    st, body, _ = req(jsia_url)
    (PASS / "spicksley_jsia.json").write_bytes(body or b"")
    print("jsia", st, len(body or b""), (body or b"")[:180])

    for fname in [
        f"{IDENT}_djvu.txt",
        f"{IDENT}.pdf",
        f"{IDENT}.epub",
        f"{IDENT}_encrypted.pdf",
        f"{IDENT}_lcp.epub",
    ]:
        url = f"https://archive.org/download/{IDENT}/{urllib.parse.quote(fname)}"
        st, body, hdrs = req(url, timeout=120)
        print("dl", fname, st, len(body or b""), "ctype", hdrs.get("Content-Type"))
        if body and len(body) > 50000 and b"<html" not in body[:200].lower():
            out = OUT / fname
            out.write_bytes(body)
            print("WROTE", out, out.stat().st_size)

    for q in ["spectacles", "spectacle", "eyeglasses", "magnifying"]:
        for url in [
            f"https://{server}/fulltext/inside.php?item_id={IDENT}&doc={IDENT}&path={direc}&q={q}",
            f"https://{server}/BookReader/BookReaderGetSearchResults.php?path={direc}&id={IDENT}&q={q}",
            f"https://archive.org/fulltext/inside.php?item_id={IDENT}&q={q}",
        ]:
            st, b2, _ = req(url, retries=4, timeout=40)
            head = (b2 or b"")[:120]
            print("si", q, st, len(b2 or b""), url[:100], head)
            if (
                st == 200
                and b2
                and b2[:1] in (b"{", b"[")
                and b"<html" not in b2[:50].lower()
            ):
                (PASS / f"si_{q}.json").write_bytes(b2)
                print("SAVED search", q)


if __name__ == "__main__":
    main()
