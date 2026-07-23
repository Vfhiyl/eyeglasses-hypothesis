"""Open a TCP tunnel to target via HTTP CONNECT / SOCKS5 / SOCKS4 upstream.

Used by the local gateway (presents HTTP CONNECT to clients) and by probes.
No third-party deps.
"""
from __future__ import annotations

import socket
import struct


def open_upstream_tunnel(
    proto: str,
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
) -> socket.socket:
    """Return a connected socket that is already tunneled to target_host:target_port."""
    p = (proto or "http").lower().strip()
    if p in ("http", "https", "connect"):
        return _http_connect(proxy_host, proxy_port, target_host, target_port, timeout)
    if p in ("socks5", "socks"):
        return _socks5_connect(proxy_host, proxy_port, target_host, target_port, timeout)
    if p == "socks4":
        return _socks4_connect(proxy_host, proxy_port, target_host, target_port, timeout)
    raise ValueError(f"unsupported upstream proto: {proto!r}")


def _http_connect(
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    sock.settimeout(timeout)
    sock.sendall(
        (
            f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
            f"Host: {target_host}:{target_port}\r\n"
            f"Proxy-Connection: keep-alive\r\n"
            f"\r\n"
        ).encode()
    )
    buf = b""
    while b"\r\n\r\n" not in buf and len(buf) < 65536:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    status = buf.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
    if " 200" not in status:
        sock.close()
        raise OSError(f"HTTP CONNECT {status or 'empty'}")
    return sock


def _socks5_connect(
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    sock.settimeout(timeout)
    # greeting: ver=5, nmethods=1, method=0 (no auth)
    sock.sendall(b"\x05\x01\x00")
    resp = _recv_exact(sock, 2)
    if resp[0] != 5 or resp[1] != 0:
        sock.close()
        raise OSError(f"SOCKS5 auth rejected: {resp!r}")

    host_b = target_host.encode("idna")
    if len(host_b) > 255:
        sock.close()
        raise OSError("SOCKS5 hostname too long")
    req = b"\x05\x01\x00\x03" + bytes([len(host_b)]) + host_b + struct.pack("!H", target_port)
    sock.sendall(req)
    # reply: ver, rep, rsv, atyp, ...
    hdr = _recv_exact(sock, 4)
    if hdr[0] != 5:
        sock.close()
        raise OSError(f"SOCKS5 bad ver in reply: {hdr!r}")
    if hdr[1] != 0:
        sock.close()
        raise OSError(f"SOCKS5 connect failed rep={hdr[1]}")
    atyp = hdr[3]
    if atyp == 1:  # IPv4
        _recv_exact(sock, 4 + 2)
    elif atyp == 3:  # domain
        ln = _recv_exact(sock, 1)[0]
        _recv_exact(sock, ln + 2)
    elif atyp == 4:  # IPv6
        _recv_exact(sock, 16 + 2)
    else:
        sock.close()
        raise OSError(f"SOCKS5 unknown atyp={atyp}")
    return sock


def _socks4_connect(
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
) -> socket.socket:
    """SOCKS4a (hostname) — works for most public SOCKS4 lists."""
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    sock.settimeout(timeout)
    host_b = target_host.encode("idna") + b"\x00"
    # ver=4, cmd=1 CONNECT, port, ip=0.0.0.1 (SOCKS4a marker), userid="", hostname
    req = b"\x04\x01" + struct.pack("!H", target_port) + b"\x00\x00\x00\x01" + b"\x00" + host_b
    sock.sendall(req)
    resp = _recv_exact(sock, 8)
    if resp[0] not in (0, 4) or resp[1] != 0x5A:
        sock.close()
        raise OSError(f"SOCKS4 connect failed: {resp!r}")
    return sock


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise OSError("socket closed during SOCKS handshake")
        buf += chunk
    return buf


def infer_default_proto(url: str) -> str:
    u = url.lower()
    if "socks5" in u:
        return "socks5"
    if "socks4" in u:
        return "socks4"
    return "http"
