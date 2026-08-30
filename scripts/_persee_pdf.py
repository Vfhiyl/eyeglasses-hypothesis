"""Persée PDF download via ALTCHA proof-of-work (docAsPDF POST).

Flow (browser-equivalent):
  1. GET doc page (warm JSESSIONID cookies)
  2. GET /captcha-challenge  → {algorithm, challenge, salt, signature, maxnumber}
  3. Solve SHA-256(salt||number) == challenge
  4. POST /docAsPDF/{id}.pdf  body=altcha=<base64 JSON payload>

Default proxy: local CONNECT gateway (http://127.0.0.1:12309).
"""
from __future__ import annotations

import base64
import hashlib
import http.cookiejar
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from _persee_sparql import DEFAULT_PROXY, log, proxy_implies_insecure

# Re-export for CLI convenience
__all__ = [
    "DEFAULT_PROXY",
    "PerseeSession",
    "build_altcha_payload",
    "doc_id_from_url",
    "doc_page_url",
    "download_pdf",
    "fetch_challenge",
    "pdf_url_for",
    "smoke",
    "solve_challenge",
]

CHALLENGE_URL = "https://www.persee.fr/captcha-challenge"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)
SEC_CH_UA = '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'


def doc_id_from_url(doc_url: str) -> str:
    path = urllib.parse.urlparse(doc_url).path.rstrip("/")
    # /doc/{id} or /docAsPDF/{id}.pdf
    leaf = path.rsplit("/", 1)[-1]
    if leaf.endswith(".pdf"):
        leaf = leaf[: -len(".pdf")]
    if not leaf:
        raise ValueError(f"Cannot parse document id from: {doc_url}")
    return leaf


def doc_page_url(doc_id_or_url: str) -> str:
    if doc_id_or_url.startswith("http"):
        if "/docAsPDF/" in doc_id_or_url:
            return f"https://www.persee.fr/doc/{doc_id_from_url(doc_id_or_url)}"
        return doc_id_or_url.split("?")[0].rstrip("/")
    return f"https://www.persee.fr/doc/{doc_id_or_url}"


def pdf_url_for(doc_id_or_url: str) -> str:
    doc_id = doc_id_from_url(doc_id_or_url) if "://" in doc_id_or_url or "/" in doc_id_or_url else doc_id_or_url
    if doc_id_or_url.startswith("http") and "/docAsPDF/" in doc_id_or_url:
        return doc_id_or_url.split("?")[0]
    return f"https://www.persee.fr/docAsPDF/{doc_id_from_url(doc_page_url(doc_id_or_url))}.pdf"


def solve_challenge(
    challenge: str,
    salt: str,
    algorithm: str,
    max_number: int,
) -> tuple[int, int]:
    """Return (number, took_ms). PoW: SHA-256(utf8(salt + str(number))).hex == challenge."""
    algo = algorithm.upper().replace("_", "-")
    if algo != "SHA-256":
        raise NotImplementedError(f"Unsupported algorithm: {algorithm}")
    started = time.perf_counter()
    target = challenge.lower()
    for number in range(max_number + 1):
        digest = hashlib.sha256(f"{salt}{number}".encode("utf-8")).hexdigest()
        if digest == target:
            return number, int((time.perf_counter() - started) * 1000)
    raise RuntimeError(f"No solution found within maxnumber={max_number}")


def build_altcha_payload(challenge_data: dict[str, object], number: int, took_ms: int) -> str:
    payload = {
        "algorithm": challenge_data["algorithm"],
        "challenge": challenge_data["challenge"],
        "number": number,
        "salt": challenge_data["salt"],
        "signature": challenge_data["signature"],
        "took": took_ms,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


class PerseeSession:
    """Cookie-aware HTTP session (optional CONNECT gateway)."""

    def __init__(
        self,
        *,
        proxy: str | None = DEFAULT_PROXY,
        insecure: bool | None = None,
        extra_cookie: str | None = None,
    ) -> None:
        if insecure is None:
            insecure = proxy_implies_insecure(proxy)
        self.proxy = proxy
        self.jar = http.cookiejar.CookieJar()
        # Proxy/SSL handlers + cookie jar (same pattern as search client)
        handlers: list[urllib.request.BaseHandler] = []
        if proxy:
            handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        if insecure:
            import ssl

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            handlers.append(urllib.request.HTTPSHandler(context=ctx))
        handlers.append(urllib.request.HTTPCookieProcessor(self.jar))
        self.opener = urllib.request.build_opener(*handlers)
        self._extra_cookie = extra_cookie

    def _merge_cookie_header(self, headers: dict[str, str]) -> dict[str, str]:
        if not self._extra_cookie:
            return headers
        # CookieJar will also send; prepend user cookie for Liferay bits if needed
        existing = headers.get("Cookie", "")
        merged = self._extra_cookie if not existing else f"{self._extra_cookie}; {existing}"
        headers = dict(headers)
        headers["Cookie"] = merged
        return headers

    def request(
        self,
        url: str,
        *,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        method: str | None = None,
        timeout: float = 120.0,
        referer: str | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        hdrs = {
            "User-Agent": USER_AGENT,
            "Accept-Language": "zh-CN,zh;q=0.9,fr;q=0.8,en;q=0.7",
            "sec-ch-ua": SEC_CH_UA,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Origin": "https://www.persee.fr",
        }
        if referer:
            hdrs["Referer"] = referer
        if headers:
            hdrs.update(headers)
        hdrs = self._merge_cookie_header(hdrs)
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with self.opener.open(req, timeout=timeout) as resp:
                return resp.status, {k: v for k, v in resp.headers.items()}, resp.read()
        except urllib.error.HTTPError as exc:
            return exc.code, {k: v for k, v in exc.headers.items()}, exc.read()


def fetch_challenge(
    session: PerseeSession,
    *,
    referer: str,
    timeout: float = 45.0,
) -> dict[str, object]:
    status, _, body = session.request(
        CHALLENGE_URL,
        headers={
            "Accept": "*/*",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        },
        referer=referer,
        timeout=timeout,
    )
    if status != 200:
        raise RuntimeError(f"captcha-challenge HTTP {status}: {body[:200]!r}")
    data = json.loads(body.decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"unexpected challenge JSON type {type(data).__name__}")
    return data


def download_pdf(
    doc_url_or_id: str,
    dest: Path | None = None,
    *,
    proxy: str | None = DEFAULT_PROXY,
    insecure: bool | None = None,
    cookie: str | None = None,
    timeout: float = 120.0,
    session: PerseeSession | None = None,
) -> Path:
    """Warm doc page → solve ALTCHA → POST docAsPDF → write PDF file."""
    page = doc_page_url(doc_url_or_id)
    doc_id = doc_id_from_url(page)
    pdf_url = pdf_url_for(page)
    target = dest or Path(f"{doc_id}.pdf")

    sess = session or PerseeSession(proxy=proxy, insecure=insecure, extra_cookie=cookie)

    log(f"warm {page}")
    status, _, _ = sess.request(
        page,
        headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
        referer="https://www.persee.fr/",
        timeout=timeout,
    )
    if status != 200:
        raise RuntimeError(f"doc page HTTP {status}")

    log("captcha-challenge…")
    challenge = fetch_challenge(sess, referer=page, timeout=min(60.0, timeout))
    max_number = int(challenge.get("maxnumber") or challenge.get("maxNumber") or 1_000_000)
    log(f"solve PoW maxnumber={max_number}")
    number, took_ms = solve_challenge(
        str(challenge["challenge"]),
        str(challenge["salt"]),
        str(challenge["algorithm"]),
        max_number,
    )
    log(f"solved number={number} took={took_ms}ms")
    payload = build_altcha_payload(challenge, number, took_ms)

    log(f"POST {pdf_url}")
    status, headers, raw = sess.request(
        pdf_url,
        data=urllib.parse.urlencode({"altcha": payload}).encode("utf-8"),
        headers={
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            ),
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        },
        method="POST",
        referer=page,
        timeout=timeout,
    )
    ctype = headers.get("Content-Type", "")
    log(f"response HTTP {status} ctype={ctype!r} bytes={len(raw)}")

    if status == 200 and raw.startswith(b"%PDF"):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        log(f"saved {target} ({len(raw)} bytes)")
        return target

    if status == 403:
        raise RuntimeError("ALTCHA rejected (HTTP 403) — payload invalid/expired?")
    if status == 500 and len(raw) == 0:
        raise RuntimeError(
            "ALTCHA ok but Persée returned empty HTTP 500 (media outage). Retry later."
        )
    preview = raw[:300].decode("utf-8", errors="replace")
    raise RuntimeError(f"Unexpected PDF response HTTP {status}: {preview}")


def smoke(*, proxy: str | None = DEFAULT_PROXY, insecure: bool | None = None) -> tuple[bool, str]:
    """Tiny challenge fetch + PoW only (no PDF write)."""
    try:
        page = "https://www.persee.fr/doc/pharm_0035-2349_1972_num_60_215_7165"
        sess = PerseeSession(proxy=proxy, insecure=insecure)
        st, _, _ = sess.request(page, headers={"Accept": "text/html"}, referer="https://www.persee.fr/")
        if st != 200:
            return False, f"doc HTTP {st}"
        ch = fetch_challenge(sess, referer=page)
        n, took = solve_challenge(
            str(ch["challenge"]),
            str(ch["salt"]),
            str(ch["algorithm"]),
            int(ch.get("maxnumber") or 100000),
        )
        return True, f"ok number={n} took={took}ms"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
