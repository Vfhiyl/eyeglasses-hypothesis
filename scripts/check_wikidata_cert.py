#!/usr/bin/env python3
"""Check TLS leaf certificate for a host, optionally via HTTP CONNECT proxy.

Reports whether the peer leaf looks like the real Wikimedia / Let's Encrypt YE1
cert (vs MITM such as MySQL auto-generated CAs).

Examples:
  # Direct (baseline)
  .venv/bin/python scripts/check_wikidata_cert.py

  # Via proxy
  .venv/bin/python scripts/check_wikidata_cert.py --proxy 18.228.228.159:8360

  # Several proxies
  .venv/bin/python scripts/check_wikidata_cert.py \\
      --proxy 18.228.228.159:8360 \\
      --proxy 43.205.242.234:8960

  # Custom host
  .venv/bin/python scripts/check_wikidata_cert.py --host query.wikidata.org --proxy IP:PORT
"""
from __future__ import annotations

import argparse
import hashlib
import socket
import ssl
import sys
from dataclasses import dataclass


EXPECTED_ISSUER_CN = "YE1"
EXPECTED_ISSUER_O = "Let's Encrypt"
# Known-good leaf fingerprint from direct connect (may rotate on cert renew).
# Script treats matching issuer+subject as primary; fingerprint is advisory.
KNOWN_GOOD_FP_SHA256 = (
    "061e7990417d681c3d136bceaccf8a3df70bf002b86181ae0aac1b5f2da09d21"
)


@dataclass
class CertReport:
    label: str
    ok_connect: bool
    verify_ok: bool
    subject_cn: str
    issuer_cn: str
    issuer_o: str
    fingerprint_sha256: str
    detail: str
    looks_like_ye1: bool
    matches_known_fp: bool


def _rdn_dict(peercert: dict, field: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for rdn in peercert.get(field, ()):
        for k, v in rdn:
            out[str(k)] = str(v)
    return out


def _subject_issuer_from_der(der: bytes) -> tuple[str, str, str]:
    """Return (subject_cn, issuer_o, issuer_cn) by shelling openssl (no extra deps)."""
    import subprocess
    import tempfile
    from pathlib import Path

    if not der:
        return "", "", ""
    with tempfile.NamedTemporaryFile(suffix=".der", delete=False) as tmp:
        path = Path(tmp.name)
        path.write_bytes(der)
    try:
        r = subprocess.run(
            ["openssl", "x509", "-inform", "DER", "-in", str(path), "-noout", "-subject", "-issuer"],
            capture_output=True,
            text=True,
            check=False,
        )
        subject_cn = issuer_cn = issuer_o = ""
        for line in r.stdout.splitlines():
            if line.startswith("subject="):
                # subject=CN=...
                for part in line[len("subject=") :].split(","):
                    part = part.strip()
                    if part.startswith("CN="):
                        subject_cn = part[3:]
            if line.startswith("issuer="):
                for part in line[len("issuer=") :].split(","):
                    part = part.strip()
                    if part.startswith("CN="):
                        issuer_cn = part[3:]
                    if part.startswith("O="):
                        issuer_o = part[2:]
        return subject_cn, issuer_o, issuer_cn
    finally:
        path.unlink(missing_ok=True)


def _read_connect_response(sock: socket.socket, max_bytes: int = 65536) -> bytes:
    buf = b""
    while b"\r\n\r\n" not in buf and len(buf) < max_bytes:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def probe_cert(
    target_host: str,
    target_port: int,
    *,
    proxy: str | None,
    timeout: float,
    verify: bool,
) -> CertReport:
    label = proxy or "DIRECT"
    sock: socket.socket | None = None
    ssock: ssl.SSLSocket | None = None
    try:
        if proxy:
            ph, _, ps = proxy.rpartition(":")
            sock = socket.create_connection((ph, int(ps)), timeout=timeout)
            sock.settimeout(timeout)
            sock.sendall(
                (
                    f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
                    f"Host: {target_host}:{target_port}\r\n"
                    f"\r\n"
                ).encode()
            )
            header = _read_connect_response(sock)
            status = header.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
            if " 200" not in status:
                return CertReport(
                    label, False, False, "", "", "", "", f"CONNECT failed: {status}", False, False
                )
        else:
            sock = socket.create_connection((target_host, target_port), timeout=timeout)
            sock.settimeout(timeout)

        ctx = ssl.create_default_context() if verify else ssl._create_unverified_context()
        ssock = ctx.wrap_socket(sock, server_hostname=target_host)
        sock = None
        der = ssock.getpeercert(binary_form=True) or b""
        peercert = ssock.getpeercert() or {}
        fp = hashlib.sha256(der).hexdigest()
        sub = _rdn_dict(peercert, "subject")
        iss = _rdn_dict(peercert, "issuer")
        subject_cn = sub.get("commonName", "")
        issuer_cn = iss.get("commonName", "")
        issuer_o = iss.get("organizationName", "")
        if not subject_cn or not issuer_cn:
            subject_cn, issuer_o2, issuer_cn = _subject_issuer_from_der(der)
            issuer_o = issuer_o or issuer_o2

        looks = issuer_cn == EXPECTED_ISSUER_CN and (
            EXPECTED_ISSUER_O.lower() in (issuer_o or "").lower()
            or not issuer_o  # openssl parse sometimes omits O depending on format
        )
        if issuer_cn == EXPECTED_ISSUER_CN and EXPECTED_ISSUER_O.lower() in (issuer_o or EXPECTED_ISSUER_O).lower():
            looks = True
        if issuer_cn == EXPECTED_ISSUER_CN:
            looks = True  # YE1 alone is the key signal we care about

        if "MySQL_Server" in issuer_cn or "Auto_Generated_CA" in issuer_cn:
            looks = False

        return CertReport(
            label=label,
            ok_connect=True,
            verify_ok=verify,
            subject_cn=subject_cn or "(unknown)",
            issuer_cn=issuer_cn or "(unknown)",
            issuer_o=issuer_o or "(unknown)",
            fingerprint_sha256=fp,
            detail="TLS OK" if verify else "TLS OK (verify disabled — inspect fields manually)",
            looks_like_ye1=looks,
            matches_known_fp=(fp == KNOWN_GOOD_FP_SHA256),
        )
    except ssl.SSLCertVerificationError as e:
        # Retry once unverified to show what MITM cert looks like
        return _probe_unverified_after_fail(target_host, target_port, proxy, timeout, str(e))
    except Exception as e:
        return CertReport(
            label, False, False, "", "", "", "", f"{type(e).__name__}: {e}", False, False
        )
    finally:
        for s in (ssock, sock):
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass


def _probe_unverified_after_fail(
    target_host: str,
    target_port: int,
    proxy: str | None,
    timeout: float,
    err: str,
) -> CertReport:
    """Verification failed — dump leaf anyway so we can see MySQL MITM vs real cert."""
    report = probe_cert(
        target_host, target_port, proxy=proxy, timeout=timeout, verify=False
    )
    report.verify_ok = False
    report.detail = f"VERIFY FAIL: {err}"
    if "MySQL_Server" in report.issuer_cn or "Auto_Generated_CA" in report.issuer_cn:
        report.looks_like_ye1 = False
        report.detail += " | MITM-like issuer (MySQL auto CA)"
    return report


def _print_report(r: CertReport) -> None:
    ye = "YES" if r.looks_like_ye1 else "NO"
    fp_m = "YES" if r.matches_known_fp else "no"
    ver = "OK" if r.verify_ok else "FAIL/off"
    print(f"=== {r.label}")
    print(f"  connect/TLS : {r.detail}")
    print(f"  verify      : {ver}")
    print(f"  subject CN  : {r.subject_cn}")
    print(f"  issuer O    : {r.issuer_o}")
    print(f"  issuer CN   : {r.issuer_cn}")
    print(f"  sha256      : {r.fingerprint_sha256}")
    print(f"  Let's Encrypt YE1? : {ye}")
    print(f"  matches known good fp? : {fp_m}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="query.wikidata.org")
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--proxy", action="append", default=[], help="host:port (repeatable)")
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument(
        "--no-direct",
        action="store_true",
        help="Skip direct (no-proxy) baseline probe",
    )
    args = ap.parse_args()

    reports: list[CertReport] = []
    if not args.no_direct:
        print(f"Target {args.host}:{args.port}\n")
        reports.append(
            probe_cert(args.host, args.port, proxy=None, timeout=args.timeout, verify=True)
        )

    for p in args.proxy:
        p = p.replace("http://", "").replace("https://", "").strip()
        reports.append(
            probe_cert(args.host, args.port, proxy=p, timeout=args.timeout, verify=True)
        )

    if not reports:
        print("Nothing to probe; pass --proxy or omit --no-direct", file=sys.stderr)
        return 2

    for r in reports:
        _print_report(r)

    # Exit 0 only if every probed path that connected looks like YE1 and verified
    # (direct baseline failure still counts as error)
    bad = [r for r in reports if not (r.verify_ok and r.looks_like_ye1)]
    if bad:
        print(
            f"Result: {len(reports) - len(bad)}/{len(reports)} look like Let's Encrypt YE1 (verified)."
        )
        return 1
    print(f"Result: all {len(reports)} path(s) look like Let's Encrypt YE1 (verified).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
