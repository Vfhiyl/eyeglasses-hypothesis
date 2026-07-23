#!/usr/bin/env python3
"""Hunt free HTTP CONNECT proxies that complete TLS with a valid (non-MITM) cert.

Stops when --need successes are found. Concurrent. Writes survivors to a file.

Usage:
  .venv/bin/python scripts/check_https_proxy_cert.py --need 10 --limit 800 --workers 40
"""
from __future__ import annotations

import argparse
import hashlib
import random
import socket
import ssl
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_LISTS = [
    # Proxifly / ProxyScrape (jsDelivr CDN mirrors)
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/https/data.txt",
    "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/protocols/socks5/data.txt",
    "https://cdn.jsdelivr.net/gh/proxyscrape/free-proxy-list@main/proxies/all/data.txt",
    # VPSLab (updated ~15m)
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_ssl.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/http_all.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks5_all.txt",
    "https://raw.githubusercontent.com/VPSLabCloud/VPSLab-Free-Proxy-List/main/socks4_all.txt",
    # IPLocate (multi-protocol; all-proxies uses scheme prefixes)
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/http.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/https.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks4.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt",
    "https://raw.githubusercontent.com/iplocate/free-proxy-list/main/all-proxies.txt",
    # Large community scrapers
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
    # Newer / additional sources (2025–2026)
    "https://raw.githubusercontent.com/mohammedcha/ProxRipper/main/full_proxies/http.txt",
    "https://raw.githubusercontent.com/mohammedcha/ProxRipper/main/full_proxies/https.txt",
    "https://raw.githubusercontent.com/mohammedcha/ProxRipper/main/full_proxies/socks5.txt",
    "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/https.txt",
    "https://cdn.jsdelivr.net/gh/hproxy-com/free-proxy-list@main/http.txt",
    "https://cdn.jsdelivr.net/gh/hproxy-com/free-proxy-list@main/https.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://vakhov.github.io/fresh-proxy-list/http.txt",
    "https://vakhov.github.io/fresh-proxy-list/https.txt",
    "https://sunny9577.github.io/proxy-scraper/generated/http_proxies.txt",
    "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/http.txt",
    "https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/https.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
]


@dataclass
class ProbeResult:
    proxy: str
    ok: bool
    detail: str
    fingerprint_sha256: str = ""
    subject: str = ""


def parse_proxy_line(
    line: str, *, default_proto: str = "http"
) -> tuple[str, int, str] | None:
    """Return (host, port, proto) with proto in {http, socks5, socks4}."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    # clarketm format: IP:PORT <other>
    line = line.split()[0]
    proto = default_proto
    lower = line.lower()
    if lower.startswith("socks5://"):
        proto = "socks5"
        line = line.split("://", 1)[1]
    elif lower.startswith("socks4://"):
        proto = "socks4"
        line = line.split("://", 1)[1]
    elif lower.startswith("socks://"):
        proto = "socks5"
        line = line.split("://", 1)[1]
    elif lower.startswith("https://"):
        proto = "http"
        line = line.split("://", 1)[1]
    elif lower.startswith("http://"):
        proto = "http"
        line = line.split("://", 1)[1]
    if "@" in line:
        line = line.split("@", 1)[1]
    if ":" not in line:
        return None
    host, _, port_s = line.rpartition(":")
    host = host.strip("[]")
    try:
        port = int(port_s)
    except ValueError:
        return None
    if not host or not (1 <= port <= 65535):
        return None
    return host, port, proto


def fetch_proxy_list(url: str, timeout: float) -> list[tuple[str, int, str]]:
    from _upstream_tunnel import infer_default_proto

    default_proto = infer_default_proto(url)
    req = urllib.request.Request(url, headers={"User-Agent": "proxy-cert-check/1.2"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    out: list[tuple[str, int, str]] = []
    for line in text.splitlines():
        p = parse_proxy_line(line, default_proto=default_proto)
        if p:
            out.append(p)
    return out


def read_connect_response(sock: socket.socket, max_bytes: int = 65536) -> bytes:
    buf = b""
    while b"\r\n\r\n" not in buf and len(buf) < max_bytes:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def peer_cert_summary(der: bytes, peercert: dict) -> tuple[str, str]:
    fp = hashlib.sha256(der).hexdigest()
    subject = ""
    for rdn in peercert.get("subject", ()):
        for k, v in rdn:
            if k == "commonName":
                subject = v
    sans = [val for typ, val in peercert.get("subjectAltName", ()) if typ == "DNS"]
    if sans:
        subject = subject + " | SAN=" + ",".join(sans[:8])
    return fp, subject


def sparql_smoke_via_proxy(
    proxy_host: str,
    proxy_port: int,
    timeout: float = 25.0,
    *,
    proto: str = "http",
) -> bool:
    """Confirm proxy can POST SPARQL to Wikidata over Python TLS (YE1 required)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _wikidata_http import sparql_smoke

    scheme = "socks5" if proto.startswith("socks5") else ("socks4" if proto == "socks4" else "http")
    ok, _detail = sparql_smoke(f"{scheme}://{proxy_host}:{proxy_port}", timeout=timeout)
    return ok


def probe_via_proxy(
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
    *,
    sparql_check: bool = False,
    proto: str = "http",
) -> ProbeResult:
    from _upstream_tunnel import open_upstream_tunnel

    label = f"{proto}://{proxy_host}:{proxy_port}"
    sock: socket.socket | None = None
    ssock: ssl.SSLSocket | None = None
    try:
        sock = open_upstream_tunnel(
            proto, proxy_host, proxy_port, target_host, target_port, timeout
        )
        sock.settimeout(timeout)

        ctx = ssl.create_default_context()
        ssock = ctx.wrap_socket(sock, server_hostname=target_host)
        sock = None
        der = ssock.getpeercert(binary_form=True) or b""
        peercert = ssock.getpeercert() or {}
        fp, subject = peer_cert_summary(der, peercert)
        # Defense in depth: reject leaves that look like common open-proxy MITM CAs.
        issuer_str = ""
        issuer_cn = ""
        for rdn in peercert.get("issuer", ()):
            for k, v in rdn:
                issuer_str += f"{k}={v};"
                if k == "commonName":
                    issuer_cn = str(v)
        if "MySQL_Server" in issuer_str or "Auto_Generated_CA" in issuer_str:
            return ProbeResult(label, False, f"MITM-like issuer: {issuer_str[:80]}")
        # For Wikidata, require Let's Encrypt YE1 (same gate as fetch script).
        if target_host == "query.wikidata.org" and issuer_cn != "YE1":
            return ProbeResult(label, False, f"not YE1 (issuer CN={issuer_cn or '?'})")
        ssock.sendall(
            f"HEAD / HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n".encode()
        )
        try:
            ssock.recv(2048)
        except Exception:
            pass
        if sparql_check and target_host == "query.wikidata.org":
            try:
                ssock.close()
            except Exception:
                pass
            ssock = None
            if not sparql_smoke_via_proxy(
                proxy_host, proxy_port, timeout=max(15.0, timeout * 3), proto=proto
            ):
                return ProbeResult(label, False, "TLS YE1 OK but SPARQL smoke failed")
            return ProbeResult(label, True, "TLS+SPARQL OK (YE1)", fp, subject)
        return ProbeResult(label, True, "TLS OK", fp, subject)
    except ssl.SSLCertVerificationError as e:
        return ProbeResult(label, False, f"MITM/untrusted cert: {e}")
    except Exception as e:
        return ProbeResult(label, False, f"{type(e).__name__}")
    finally:
        for s in (ssock, sock):
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass


def probe_direct(target_host: str, target_port: int, timeout: float) -> ProbeResult:
    sock = ssock = None
    try:
        sock = socket.create_connection((target_host, target_port), timeout=timeout)
        ctx = ssl.create_default_context()
        ssock = ctx.wrap_socket(sock, server_hostname=target_host)
        sock = None
        der = ssock.getpeercert(binary_form=True) or b""
        peercert = ssock.getpeercert() or {}
        fp, subject = peer_cert_summary(der, peercert)
        return ProbeResult("DIRECT", True, "baseline", fp, subject)
    except Exception as e:
        return ProbeResult("DIRECT", False, f"{type(e).__name__}: {e}")
    finally:
        for s in (ssock, sock):
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass


def unique_proxies(items: Iterable[tuple[str, int, str]]) -> list[tuple[str, int, str]]:
    seen: set[tuple[str, int, str]] = set()
    out: list[tuple[str, int, str]] = []
    for p in items:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def collect_proxy_pool(
    list_urls: list[str],
    *,
    timeout: float = 20.0,
    merge_out: Path | None = None,
) -> list[tuple[str, int, str]]:
    """Fetch all list URLs, parse, and dedupe (proto, host, port) across sources."""
    proxies: list[tuple[str, int, str]] = []
    ok_lists = 0
    for url in list_urls:
        try:
            got = fetch_proxy_list(url, timeout=timeout)
            print(f"[list] {len(got):5d}  {url}", file=sys.stderr)
            proxies.extend(got)
            ok_lists += 1
        except Exception as e:
            print(f"[list] FAIL {e} | {url}", file=sys.stderr)
    before = len(proxies)
    proxies = unique_proxies(proxies)
    print(
        f"[dedupe] sources_ok={ok_lists}/{len(list_urls)} raw={before} unique={len(proxies)}",
        file=sys.stderr,
    )
    if merge_out is not None:
        merge_out.parent.mkdir(parents=True, exist_ok=True)
        merge_out.write_text(
            "\n".join(f"{proto}://{h}:{p}" for h, p, proto in proxies) + ("\n" if proxies else ""),
            encoding="utf-8",
        )
        print(f"[dedupe] wrote merged pool -> {merge_out}", file=sys.stderr)
    return proxies


def probe_pool(
    proxies: list[tuple[str, int, str]],
    *,
    host: str,
    port: int,
    timeout: float,
    need: int,
    workers: int,
    sparql_check: bool = False,
) -> tuple[list[ProbeResult], int]:
    baseline = probe_direct(host, port, timeout)
    if baseline.ok:
        print(f"[baseline] {host} OK fp={baseline.fingerprint_sha256[:16]}… {baseline.subject}", file=sys.stderr)
    else:
        print(f"[baseline] FAIL {baseline.detail}", file=sys.stderr)

    ok_rows: list[ProbeResult] = []
    tried = 0
    t0 = time.time()

    def _job(item: tuple[str, int, str]) -> ProbeResult:
        return probe_via_proxy(
            item[0], item[1], host, port, timeout, sparql_check=sparql_check, proto=item[2]
        )

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_job, p): p for p in proxies}
        for fut in as_completed(futures):
            tried += 1
            r = fut.result()
            if r.ok:
                note = r.detail
                if baseline.ok and r.fingerprint_sha256 != baseline.fingerprint_sha256:
                    note = "TLS OK (leaf fp differs from baseline — CDN OK if still trusted)"
                print(f"[PASS] {r.proxy} | {note} | {r.subject}", flush=True)
                ok_rows.append(r)
                if len(ok_rows) >= need:
                    for f in futures:
                        f.cancel()
                    break
            elif tried % 50 == 0:
                print(
                    f"[progress] tried={tried} pass={len(ok_rows)} elapsed={time.time()-t0:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )
    print(f"[round] tried={tried} pass={len(ok_rows)} in {time.time()-t0:.1f}s", file=sys.stderr)
    return ok_rows, tried


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="www.google.com", help="TLS target (default google; use scribd if needed)")
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--timeout", type=float, default=5.0)
    ap.add_argument("--limit", type=int, default=1000, help="max proxies to try per round")
    ap.add_argument("--need", type=int, default=10, help="stop after this many PASS")
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--proxy", action="append", default=[])
    ap.add_argument("--list-url", action="append", default=[])
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument(
        "--out",
        default=str(
            Path(__file__).resolve().parents[1] / "outputs" / "tables" / "working_https_proxies.txt"
        ),
    )
    ap.add_argument(
        "--merge-out",
        default=str(
            Path(__file__).resolve().parents[1] / "outputs" / "tables" / "proxy_pool_merged.txt"
        ),
        help="write deduped candidate pool (all sources) here",
    )
    ap.add_argument(
        "--rounds",
        type=int,
        default=1,
        help="reshuffle+probe up to N rounds until --need PASS (keeps hunting)",
    )
    ap.add_argument("--also-check", default="", help="optional second host to re-check PASses (e.g. www.scribd.com)")
    ap.add_argument(
        "--sparql-check",
        action="store_true",
        help="After TLS OK to query.wikidata.org, also require a tiny SPARQL POST to succeed",
    )
    args = ap.parse_args()

    # Auto-enable SPARQL smoke when hunting specifically for Wikidata query host.
    sparql_check = args.sparql_check or (args.host == "query.wikidata.org")

    proxies: list[tuple[str, int, str]] = []
    for p in args.proxy:
        parsed = parse_proxy_line(p)
        if parsed:
            proxies.append(parsed)

    if not args.no_fetch:
        urls = args.list_url or DEFAULT_LISTS
        # Dedupe list URLs themselves (CDN + raw duplicates)
        seen_u: set[str] = set()
        urls = [u for u in urls if not (u in seen_u or seen_u.add(u))]
        merge_path = Path(args.merge_out) if args.merge_out else None
        proxies.extend(collect_proxy_pool(urls, timeout=25.0, merge_out=merge_path))

    proxies = unique_proxies(proxies)
    if not proxies:
        print("[pool] empty — no proxies to probe", file=sys.stderr)
        return 1

    rng = random.Random(args.seed if args.seed is not None else time.time_ns())
    ok_rows: list[ProbeResult] = []
    tried_total = 0
    already_tried: set[tuple[str, int, str]] = set()

    for round_i in range(1, max(1, args.rounds) + 1):
        remaining = [p for p in proxies if p not in already_tried]
        if not remaining:
            print("[pool] exhausted unique candidates", file=sys.stderr)
            break
        rng.shuffle(remaining)
        batch = remaining[: args.limit]
        already_tried.update(batch)
        print(
            f"[pool] round={round_i}/{args.rounds} probing {len(batch)} "
            f"(unique_left={len(remaining)} need={args.need - len(ok_rows)})",
            file=sys.stderr,
        )
        found, tried = probe_pool(
            batch,
            host=args.host,
            port=args.port,
            timeout=args.timeout,
            need=max(1, args.need - len(ok_rows)),
            workers=args.workers,
            sparql_check=sparql_check,
        )
        tried_total += tried
        # Dedupe PASS by proxy string
        seen_ok = {r.proxy for r in ok_rows}
        for r in found:
            if r.proxy not in seen_ok:
                ok_rows.append(r)
                seen_ok.add(r.proxy)
        if len(ok_rows) >= args.need:
            break
        print(f"[pool] still short: have={len(ok_rows)} need={args.need}", file=sys.stderr)

    # Optional second-host check
    if args.also_check and ok_rows:
        print(f"\n[recheck] {args.also_check} …", file=sys.stderr)
        also_ok = []
        for r in ok_rows:
            parsed = parse_proxy_line(r.proxy)
            if not parsed:
                continue
            host, port_i, proto = parsed
            rr = probe_via_proxy(
                host, port_i, args.also_check, 443, args.timeout, proto=proto
            )
            tag = "PASS" if rr.ok else "FAIL"
            print(f"  [{tag}] {r.proxy} -> {args.also_check}: {rr.detail}")
            if rr.ok:
                also_ok.append(r.proxy)
        print(f"[recheck] {len(also_ok)}/{len(ok_rows)} also reach {args.also_check}", file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# working proxies (cert verify OK) for {args.host}",
        f"# generated {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
        f"# probed={tried_total} passed={len(ok_rows)} need={args.need} sources={len(DEFAULT_LISTS)}",
    ]
    for r in ok_rows:
        lines.append(f"{r.proxy}\t{r.fingerprint_sha256}\t{r.subject}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(file=sys.stderr)
    print(f"Done: {len(ok_rows)}/{tried_total} PASS -> {out}", file=sys.stderr)
    for r in ok_rows:
        # Local HTTP CONNECT clients still use http:// scheme; socks labels are for hunter/gateway.
        hp = r.proxy.split("://", 1)[-1]
        print(f"  export https_proxy=http://{hp} http_proxy=http://{hp}", file=sys.stderr)

    return 0 if len(ok_rows) >= min(args.need, 1) and len(ok_rows) >= 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
