#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import http.cookiejar
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PASS = Path(__file__).resolve().parent
ROOT = Path("/Users/admin/Desktop/proj/other/eyeglasses-hypothesis")
IDENT = "businesshousehol0000unse"
PROXY = "http://127.0.0.1:12309"
UA = "Mozilla/5.0"


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

    def set_cookie(n: str, v: str, d: str = ".archive.org") -> None:
        jar.set_cookie(
            http.cookiejar.Cookie(
                0,
                n,
                v,
                None,
                False,
                d,
                True,
                d.startswith("."),
                "/",
                True,
                False,
                None,
                False,
                None,
                None,
                {},
                False,
            )
        )

    for p in cookie.split("; "):
        if "=" in p:
            k, v = p.split("=", 1)
            set_cookie(k, v)

    def post(action: str, extra: dict[str, str] | None = None) -> dict[str, object]:
        d = {"action": action, "identifier": IDENT}
        if extra:
            d.update(extra)
        data = urllib.parse.urlencode(d).encode()
        req = urllib.request.Request(
            "https://archive.org/services/loans/loan/",
            data=data,
            headers={
                "User-Agent": UA,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "Referer": f"https://archive.org/details/{IDENT}",
            },
        )
        for a in range(6):
            try:
                with opener.open(req, timeout=45) as r:
                    raw = json.loads(r.read().decode())
                    if isinstance(raw, dict):
                        return raw
                    return {}
            except Exception as e:
                print("retry", a, e, flush=True)
                time.sleep(1.3 * (a + 1))
        return {}

    print(post("borrow_book"), flush=True)
    tok = post("create_token")
    print(tok, flush=True)
    token = tok.get("token")
    if not isinstance(token, str):
        raise SystemExit("no token")
    set_cookie(f"loan-{IDENT}", token)
    set_cookie(f"br-loan-{IDENT}", "1")

    info = post("media_url", {"format": "lcp_epub"})
    print(info, flush=True)
    url = info.get("url")
    if not isinstance(url, str):
        raise SystemExit("no license url")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Referer": f"https://archive.org/details/{IDENT}"},
    )
    with opener.open(req, timeout=45) as r:
        lic_raw = r.read()
    lic = json.loads(lic_raw)
    (PASS / "license_lcp_epub.json").write_bytes(lic_raw)
    print("license id", lic["id"], "hint", lic["encryption"]["user_key"]["text_hint"], flush=True)

    candidates = [
        "alanobrienterry918272@gmail.com",
        "alanobrienterry918272%40gmail.com",
        "AlanOBrienTerry918272@gmail.com",
        "alan_obrien_terry_ward_mccoy_liam",
        "@alan_obrien_terry_ward_mccoy_liam",
    ]

    def try_pass(pw: str) -> tuple[bool, bytes]:
        user_key = hashlib.sha256(pw.encode()).digest()
        kc = b64decode(lic["encryption"]["user_key"]["key_check"])
        iv, ct = kc[:16], kc[16:]
        d = Cipher(algorithms.AES(user_key), modes.CBC(iv)).decryptor()
        check = d.update(ct) + d.finalize()
        pad = check[-1]
        if 1 <= pad <= 16 and all(x == pad for x in check[-pad:]):
            check = check[:-pad]
        return check == lic["id"].encode(), check

    for pw in candidates:
        ok, check = try_pass(pw)
        print("pass?", repr(pw), ok, check[:40], flush=True)

    req = urllib.request.Request(
        f"https://archive.org/metadata/{IDENT}", headers={"User-Agent": UA}
    )
    with opener.open(req, timeout=40) as r:
        meta = json.loads(r.read())
    server = meta.get("server") or meta.get("d1")
    direc = meta.get("dir")
    print("server", server, direc, flush=True)

    cookie_hdr = "; ".join(f"{c.name}={c.value}" for c in jar)
    for q in ["spectacles", "spectacle", "magnifying"]:
        urls = [
            f"https://{server}/BookReader/BookReaderGetSearchResults.php?path={direc}&id={IDENT}&q={q}&callback=br",
            f"https://archive.org/fulltext/inside.php?item_id={IDENT}&q={q}",
            f"https://{server}/fulltext/inside.php?item_id={IDENT}&doc={IDENT}&path={direc}&q={q}",
        ]
        for u in urls:
            try:
                req = urllib.request.Request(
                    u,
                    headers={
                        "User-Agent": UA,
                        "Referer": f"https://archive.org/details/{IDENT}",
                        "Cookie": cookie_hdr,
                    },
                )
                with opener.open(req, timeout=35) as r:
                    body = r.read()
                    status = getattr(r, "status", 200)
                print(q, status, len(body), u[:90], body[:120], flush=True)
                if body.startswith(b"br(") or body.lstrip()[:1] in (b"{", b"["):
                    (PASS / f"brsearch_{q}.txt").write_bytes(body)
                    print("SAVED", q, flush=True)
            except Exception as e:
                print("si fail", q, type(e).__name__, e, flush=True)

    (PASS / "spicksley_loan_cookie_fragment.txt").write_text(
        f"loan-{IDENT}={token}; br-loan-{IDENT}=1\n"
    )
    print("wrote loan fragment", flush=True)


if __name__ == "__main__":
    main()
