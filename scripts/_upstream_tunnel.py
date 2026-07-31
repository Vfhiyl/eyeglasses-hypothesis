"""Open a TCP tunnel to target via HTTP CONNECT / SOCKS5 / SOCKS4 upstream.

Used by the local gateway (presents HTTP CONNECT to clients) and by probes.
No third-party deps. SOCKS5 supports username/password (RFC 1929).
"""
from __future__ import annotations

import base64
import re
import socket
import struct
from dataclasses import dataclass
from urllib.parse import unquote, quote


@dataclass(frozen=True)
class UpstreamSpec:
    """Parsed upstream proxy endpoint (optional user/pass for paid SOCKS/HTTP)."""

    host: str
    port: int
    proto: str = "http"  # http | socks5 | socks4
    username: str | None = None
    password: str | None = None
    premium: bool = False

    @property
    def key(self) -> str:
        return f"{self.proto}://{self.host}:{self.port}"

    def redacted(self) -> str:
        if self.username:
            return f"{self.proto}://{self.username}:***@{self.host}:{self.port}"
        return self.key

    def as_url(self) -> str:
        """URL with credentials (user:pass@host:port). Safe for internal probes."""
        if self.username is not None:
            u = quote(self.username, safe="")
            p = quote(self.password or "", safe="")
            return f"{self.proto}://{u}:{p}@{self.host}:{self.port}"
        return self.key


def parse_upstream_spec(
    raw: str,
    *,
    default_proto: str = "socks5",
    premium: bool = False,
) -> UpstreamSpec | None:
    """Parse paid/free upstream URLs.

    Accepted forms:
      socks5://user:pass@host:port
      socks5://host:port:user:pass          (Evomi / some residential panels)
      socks5://host:port
      host:port:user:pass                   (implies default_proto)
      user:pass@host:port
    """
    line = (raw or "").strip()
    if not line or line.startswith("#"):
        return None
    proto = default_proto
    lower = line.lower()
    if "://" in line:
        scheme, rest = line.split("://", 1)
        scheme = scheme.lower()
        if scheme in ("socks5", "socks5h", "socks"):
            proto = "socks5"
        elif scheme == "socks4":
            proto = "socks4"
        elif scheme in ("http", "https"):
            proto = "http"
        else:
            proto = scheme
        line = rest
    else:
        line = line

    username: str | None = None
    password: str | None = None

    if "@" in line:
        cred, _, hostport = line.rpartition("@")
        if ":" in cred:
            u, _, p = cred.partition(":")
            username, password = unquote(u), unquote(p)
        else:
            username = unquote(cred)
        line = hostport

    # IPv6 in brackets: [2001:db8::1]:1080[:user:pass]
    if line.startswith("["):
        m = re.match(r"^\[([^\]]+)\]:(\d+)(?::([^:]*):(.*))?$", line)
        if not m:
            return None
        host = m.group(1)
        port = int(m.group(2))
        if m.group(3) is not None and username is None:
            username, password = unquote(m.group(3)), unquote(m.group(4) or "")
        return UpstreamSpec(
            host=host, port=port, proto=proto, username=username, password=password, premium=premium
        )

    parts = line.split(":")
    if len(parts) == 2:
        host, port_s = parts
    elif len(parts) >= 4 and username is None:
        # Evomi-style host:port:user:pass (password may contain ':')
        host, port_s, username = parts[0], parts[1], unquote(parts[2])
        password = unquote(":".join(parts[3:]))
    elif len(parts) == 3 and username is None:
        # Ambiguous; treat as host:port:user with empty password
        host, port_s, username = parts[0], parts[1], unquote(parts[2])
        password = ""
    else:
        return None
    try:
        port = int(port_s)
    except ValueError:
        return None
    host = host.strip()
    if not host or not (1 <= port <= 65535):
        return None
    return UpstreamSpec(
        host=host, port=port, proto=proto, username=username, password=password, premium=premium
    )


def open_upstream_tunnel(
    proto: str,
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
    *,
    username: str | None = None,
    password: str | None = None,
) -> socket.socket:
    """Return a connected socket that is already tunneled to target_host:target_port."""
    p = (proto or "http").lower().strip()
    if p in ("http", "https", "connect"):
        return _http_connect(
            proxy_host,
            proxy_port,
            target_host,
            target_port,
            timeout,
            username=username,
            password=password,
        )
    if p in ("socks5", "socks"):
        return _socks5_connect(
            proxy_host,
            proxy_port,
            target_host,
            target_port,
            timeout,
            username=username,
            password=password,
        )
    if p == "socks4":
        return _socks4_connect(proxy_host, proxy_port, target_host, target_port, timeout)
    raise ValueError(f"unsupported upstream proto: {proto!r}")


def _http_connect(
    proxy_host: str,
    proxy_port: int,
    target_host: str,
    target_port: int,
    timeout: float,
    *,
    username: str | None = None,
    password: str | None = None,
) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    sock.settimeout(timeout)
    extra = ""
    if username is not None:
        token = base64.b64encode(f"{username}:{password or ''}".encode()).decode("ascii")
        extra = f"Proxy-Authorization: Basic {token}\r\n"
    sock.sendall(
        (
            f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
            f"Host: {target_host}:{target_port}\r\n"
            f"Proxy-Connection: keep-alive\r\n"
            f"{extra}"
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
    *,
    username: str | None = None,
    password: str | None = None,
) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
    sock.settimeout(timeout)
    if username is not None:
        # Offer user/pass (0x02) only — paid residential endpoints expect this.
        sock.sendall(b"\x05\x01\x02")
        resp = _recv_exact(sock, 2)
        if resp[0] != 5 or resp[1] != 2:
            sock.close()
            raise OSError(f"SOCKS5 auth method rejected: {resp!r}")
        user_b = username.encode("utf-8")
        pass_b = (password or "").encode("utf-8")
        if len(user_b) > 255 or len(pass_b) > 255:
            sock.close()
            raise OSError("SOCKS5 username/password too long")
        sock.sendall(b"\x01" + bytes([len(user_b)]) + user_b + bytes([len(pass_b)]) + pass_b)
        auth_resp = _recv_exact(sock, 2)
        if auth_resp[0] != 1 or auth_resp[1] != 0:
            sock.close()
            raise OSError(f"SOCKS5 username/password failed: {auth_resp!r}")
    else:
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
