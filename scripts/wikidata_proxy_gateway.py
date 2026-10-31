#!/usr/bin/env python3
"""Local smart CONNECT gateway for Wikidata (ccswitch-style).

Listens on 127.0.0.1:12309 as an HTTP CONNECT proxy. Clients set:
  export https_proxy=http://127.0.0.1:12309 http_proxy=http://127.0.0.1:12309

Internally maintains an in-memory scored pool of upstream free proxies (HTTP
CONNECT and SOCKS4/5), hunts when quality is low, and fails over within a
per-request time budget. Clients always speak HTTP CONNECT to this gateway;
SOCKS upstreams are wrapped transparently.

Paid Evomi sessions are read from the gitignored config/wikidata_premium.local.env
(one PREMIUM_PROXY=<url> per line; env WIKIDATA_PREMIUM_PROXIES overrides) and
preferred by default. Extra URLs can still be passed with --premium.

Stability v4 (anti-MITM gate + CONNECT tunnel):
  - Hunter: active probe on query.wikidata.org (YE1 + SPARQL) → pool admission
  - CONNECT default: anti-MITM TLS probe through upstream BEFORE 200 (OS trust store
    verify). MITM/untrusted cert → route-quarantine that (proxy, host); never hand to
    browser. Then blind tunnel; client still does its own TLS (RFC/MDN).
  - --no-anti-mitm-probe: skip probe (v3 tunnel-only; browser may see cert errors)
  - Live score: per-destination-host route quarantine on probe/tunnel failure
  - sticky: per-target-host sticky upstream
  - Hunt triggers (v4.1): global usable < min; OR primary host route-eligible < min;
    OR recent fail-rate high; OR CONNECT exhausted / empty pick → immediate wake.
    Do NOT treat "global usable≥3" as healthy while www/query.wikidata.org are route-thin.
  - Premium: always tried first when not route-quarantined; free pool is fallback.

Foreground only — Ctrl+C exits. Logs on state changes (not every byte) to
console and outputs/logs/wikidata_proxy_gateway.log (truncated on each start).

Examples:
  .venv/bin/python scripts/wikidata_proxy_gateway.py
  .venv/bin/python scripts/wikidata_proxy_gateway.py --listen 12309 --budget 30 --min-usable 3
  .venv/bin/python scripts/wikidata_proxy_gateway.py --no-anti-mitm-probe  # v3 tunnel-only
  .venv/bin/python scripts/wikidata_proxy_gateway.py
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import select
import socket
import ssl
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CONFIG, OUTPUT_LOGS  # noqa: E402
from _upstream_tunnel import open_upstream_tunnel, parse_upstream_spec  # noqa: E402
from _wikidata_http import (  # noqa: E402
    peer_is_os_trusted_leaf,
    peer_is_trusted_public_ca,
    sparql_smoke,
)
from check_https_proxy_cert import (  # noqa: E402
    DEFAULT_LISTS,
    fetch_proxy_list,
    parse_proxy_line,
    unique_proxies,
)

DEFAULT_LOG_FILE = OUTPUT_LOGS / "wikidata_proxy_gateway.log"

# Paid upstreams (e.g. Evomi sticky sessions: host:port shared; password suffix =
# sticky exit) live in the gitignored config/wikidata_premium.local.env, one
# `PREMIUM_PROXY=<url>` per line. Env WIKIDATA_PREMIUM_PROXIES (whitespace- or
# comma-separated) overrides the file. Never hardcode credentials here.
PREMIUM_ENV_VAR = "WIKIDATA_PREMIUM_PROXIES"
PREMIUM_LOCAL_FILE = CONFIG / "wikidata_premium.local.env"


def load_local_premium_proxies(path: Path = PREMIUM_LOCAL_FILE) -> tuple[str, ...]:
    env = os.environ.get(PREMIUM_ENV_VAR, "").strip()
    if env:
        return tuple(u for u in env.replace(",", " ").split() if u)
    if not path.is_file():
        return ()
    urls: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        if key.strip().upper() == "PREMIUM_PROXY" and val.strip():
            urls.append(val.strip())
    return tuple(urls)


def _upstream_key(
    proto: str,
    host: str,
    port: int,
    *,
    username: str | None = None,
    password: str | None = None,
) -> str:
    """Unique pool key. Auth/session must disambiguate shared host:port exits."""
    base = f"{proto}://{host}:{port}"
    if username is None and password is None:
        return base
    if password and "_session-" in password:
        sess = password.rsplit("_session-", 1)[-1]
        return f"{base}|{username or ''}|s-{sess}"
    dig = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()[:10]
    return f"{base}|{username or ''}|{dig}"


def _session_tag(password: str | None) -> str:
    if password and "_session-" in password:
        return password.rsplit("_session-", 1)[-1]
    return ""

# ---------------------------------------------------------------------------
# Console + file (state-change only)
# ---------------------------------------------------------------------------

_print_lock = threading.Lock()
_last_lines: dict[str, str] = {}
_log_path: Path | None = None


def init_log_file(path: Path) -> None:
    """Truncate previous run's log, then append for this process."""
    global _log_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")  # delete/replace previous contents
    _log_path = path


def log(kind: str, msg: str, *, force: bool = False) -> None:
    """Print + append to log file when message for this kind changes (or force=True)."""
    with _print_lock:
        if not force and _last_lines.get(kind) == msg:
            return
        _last_lines[kind] = msg
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line, flush=True)
        if _log_path is not None:
            with _log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


# ---------------------------------------------------------------------------
# Scored pool (sticky + quarantine + recent-window success)
# ---------------------------------------------------------------------------

RECENT_WINDOW_S = 300.0  # 5 minutes
HUNT_BOOST_HALFLIFE_S = 90.0  # hunt YE1 boost fades fast without live traffic
ROUTE_QUARANTINE_BASE_S = 25.0
ROUTE_QUARANTINE_CAP_S = 300.0
# Hosts that must stay route-eligible; global "usable" alone is not enough.
PRIMARY_HUNT_HOSTS = ("query.wikidata.org", "www.wikidata.org")
RECENT_FAIL_WINDOW_S = 60.0
RECENT_FAIL_MIN_N = 3
RECENT_FAIL_RATE_HUNT = 0.40  # hunt if fail/(ok+fail) ≥ this in the window


@dataclass
class RouteStat:
    """Per (upstream, destination-host) live outcome — soft demote, not global kill."""

    ok: int = 0
    fail: int = 0
    consec_fails: int = 0
    quarantine_until: float = 0.0
    last_detail: str = ""


@dataclass
class ProxyStat:
    host: str
    port: int
    proto: str = "http"  # http | socks5 | socks4
    username: str | None = None
    password: str | None = None
    premium: bool = False
    attempts: int = 0
    connect_ok: int = 0
    ye1_ok: int = 0
    sparql_ok: int = 0
    timeouts: int = 0
    failures: int = 0
    consec_fails: int = 0
    total_latency_ms: float = 0.0
    last_ok_at: float = 0.0
    last_fail_at: float = 0.0
    last_detail: str = ""
    score: float = 20.0
    hunt_boost: float = 0.0
    hunt_boost_at: float = 0.0
    quarantine_until: float = 0.0
    recent: list | None = None

    def __post_init__(self) -> None:
        if self.recent is None:
            self.recent = []

    @property
    def key(self) -> str:
        return _upstream_key(
            self.proto,
            self.host,
            self.port,
            username=self.username,
            password=self.password,
        )

    def label(self) -> str:
        if self.premium:
            u = self.username or "?"
            sess = _session_tag(self.password)
            tail = f"/s-{sess}" if sess else ""
            return f"premium:{self.proto}://{u}:***@{self.host}:{self.port}{tail}"
        return self.key

    def effective_score(self, now: float | None = None) -> float:
        now = now or time.time()
        boost = 0.0
        if self.hunt_boost > 0 and self.hunt_boost_at > 0:
            age = max(0.0, now - self.hunt_boost_at)
            boost = self.hunt_boost * (0.5 ** (age / HUNT_BOOST_HALFLIFE_S))
        return min(100.0, self.score + boost)

    def prune_recent(self, now: float) -> None:
        cutoff = now - RECENT_WINDOW_S
        self.recent = [(t, ok) for t, ok in (self.recent or []) if t >= cutoff]

    def recent_success_rate(self, now: float | None = None) -> float | None:
        now = now or time.time()
        self.prune_recent(now)
        if not self.recent:
            return None
        return sum(1 for _, ok in self.recent if ok) / len(self.recent)

    def push_outcome(self, ok: bool, now: float | None = None) -> None:
        now = now or time.time()
        assert self.recent is not None
        self.recent.append((now, ok))
        self.prune_recent(now)
        rate = self.recent_success_rate(now)
        if rate is None:
            return
        n = len(self.recent)
        confidence = min(1.0, n / 8.0)
        target = 5.0 + rate * 90.0
        self.score = self.score * (1.0 - 0.45 * confidence) + target * (0.45 * confidence)


class ProxyPool:
    """Thread-safe pool with sticky routing, quarantine, and recent-window scoring."""

    def __init__(
        self,
        *,
        min_usable: int = 3,
        score_floor: float = 25.0,
        dead_below: float = 8.0,
        sticky_ttl: float = 60.0,
        quarantine_base: float = 45.0,
        quarantine_cap: float = 600.0,
        prefer_premium: bool = True,
    ) -> None:
        self._lock = threading.RLock()
        self._proxies: dict[str, ProxyStat] = {}
        self.min_usable = min_usable
        self.score_floor = score_floor
        self.dead_below = dead_below
        self.sticky_ttl = sticky_ttl
        self.quarantine_base = quarantine_base
        self.quarantine_cap = quarantine_cap
        self.prefer_premium = prefer_premium
        self.req_ok = 0
        self.req_fail = 0
        # Global sticky kept for hunter-era compatibility; CONNECT uses per-host sticky.
        self._sticky_key: str | None = None
        self._sticky_until: float = 0.0
        self._sticky_by_host: dict[str, tuple[str, float]] = {}
        self._routes: dict[tuple[str, str], RouteStat] = {}
        # Recent CONNECT outcomes (ts, ok) — drives fail-rate hunting.
        self._recent_req: list[tuple[float, bool]] = []
        # Hunter wake-up: set on exhausted CONNECT / high fail pressure.
        self.hunt_wake = threading.Event()

    def size(self) -> int:
        with self._lock:
            return len(self._proxies)

    def _is_quarantined(self, st: ProxyStat, now: float) -> bool:
        return st.quarantine_until > now

    def _route_key(self, proxy_key: str, target_host: str) -> tuple[str, str]:
        return (proxy_key, target_host.lower())

    def _route_blocked(self, proxy_key: str, target_host: str | None, now: float) -> bool:
        if not target_host:
            return False
        rt = self._routes.get(self._route_key(proxy_key, target_host))
        return bool(rt and rt.quarantine_until > now)

    def usable(self) -> list[ProxyStat]:
        now = time.time()
        with self._lock:
            return [
                p
                for p in self._proxies.values()
                if not self._is_quarantined(p, now) and p.effective_score(now) >= self.score_floor
            ]

    def _push_recent(self, ok: bool) -> None:
        now = time.time()
        self._recent_req.append((now, ok))
        # Cap list; prune old outside fail window + buffer.
        cutoff = now - max(RECENT_FAIL_WINDOW_S, 120.0)
        self._recent_req = [(t, o) for t, o in self._recent_req if t >= cutoff][-200:]

    def nudge_hunt(self, reason: str) -> None:
        """Wake hunter immediately (e.g. CONNECT exhausted all route-eligible upstreams)."""
        log("hunt", f"nudge wake — {reason}", force=True)
        self.hunt_wake.set()

    def recent_fail_stats(self) -> tuple[int, int, float]:
        """Return (ok, fail, fail_rate) over RECENT_FAIL_WINDOW_S."""
        now = time.time()
        with self._lock:
            cutoff = now - RECENT_FAIL_WINDOW_S
            rows = [(t, o) for t, o in self._recent_req if t >= cutoff]
        ok = sum(1 for _, o in rows if o)
        fail = sum(1 for _, o in rows if not o)
        n = ok + fail
        rate = (fail / n) if n else 0.0
        return ok, fail, rate

    def usable_for_host(self, target_host: str) -> list[ProxyStat]:
        """Proxies that pick() could still try for this destination (not globally/route-Q)."""
        now = time.time()
        th = target_host.lower()
        with self._lock:
            return [
                p
                for p in self._proxies.values()
                if not self._is_quarantined(p, now)
                and not self._route_blocked(p.key, th, now)
                and p.effective_score(now) >= self.score_floor
            ]

    def needs_hunt(self) -> bool:
        with self._lock:
            now = time.time()
            usable = [
                p
                for p in self._proxies.values()
                if not self._is_quarantined(p, now) and p.effective_score(now) >= self.score_floor
            ]
            if len(usable) < self.min_usable:
                return True
            top = sorted(usable, key=lambda p: p.effective_score(now), reverse=True)[: self.min_usable]
            if not top:
                return True
            mean = sum(p.effective_score(now) for p in top) / len(top)
            if mean < self.score_floor + 10:
                return True
            # Per-primary-host: route quarantine can zero out a host while global usable looks fine.
            for host in PRIMARY_HUNT_HOSTS:
                n_host = sum(
                    1
                    for p in self._proxies.values()
                    if not self._is_quarantined(p, now)
                    and not self._route_blocked(p.key, host, now)
                    and p.effective_score(now) >= self.score_floor
                )
                if n_host < self.min_usable:
                    return True
        ok, fail, rate = self.recent_fail_stats()
        if fail >= RECENT_FAIL_MIN_N and rate >= RECENT_FAIL_RATE_HUNT:
            return True
        return False

    def hunt_reason(self) -> str:
        """Short reason string for logs when hunting."""
        with self._lock:
            now = time.time()
            usable = [
                p
                for p in self._proxies.values()
                if not self._is_quarantined(p, now) and p.effective_score(now) >= self.score_floor
            ]
            if len(usable) < self.min_usable:
                return f"global_usable={len(usable)}<{self.min_usable}"
            parts = []
            for host in PRIMARY_HUNT_HOSTS:
                n_host = sum(
                    1
                    for p in self._proxies.values()
                    if not self._is_quarantined(p, now)
                    and not self._route_blocked(p.key, host, now)
                    and p.effective_score(now) >= self.score_floor
                )
                if n_host < self.min_usable:
                    parts.append(f"{host}_eligible={n_host}")
            if parts:
                return "route_thin:" + ",".join(parts)
        ok, fail, rate = self.recent_fail_stats()
        if fail >= RECENT_FAIL_MIN_N and rate >= RECENT_FAIL_RATE_HUNT:
            return f"fail_rate={rate:.0%} ({fail}f/{ok}ok in {RECENT_FAIL_WINDOW_S:.0f}s)"
        return "score_low"

    def snapshot_line(self) -> str:
        with self._lock:
            now = time.time()
            usable = [
                p
                for p in self._proxies.values()
                if not self._is_quarantined(p, now) and p.effective_score(now) >= self.score_floor
            ]
            qn = sum(1 for p in self._proxies.values() if self._is_quarantined(p, now))
            top = sorted(self._proxies.values(), key=lambda p: p.effective_score(now), reverse=True)[:5]
            parts = []
            for p in top:
                mark = "Q" if self._is_quarantined(p, now) else ""
                prem = "*" if p.premium else ""
                parts.append(f"{p.key}{prem}={p.effective_score(now):.0f}{mark}")
            sticky = ""
            if self._sticky_key and self._sticky_until > now:
                sticky = f" sticky={self._sticky_key}({self._sticky_until - now:.0f}s)"
            n_prem = sum(1 for p in self._proxies.values() if p.premium)
            return (
                f"pool total={len(self._proxies)} usable={len(usable)} quarantined={qn} "
                f"premium={n_prem} req_ok={self.req_ok} req_fail={self.req_fail}{sticky} "
                f"top=[{', '.join(parts) or '-'}]"
            )

    def seed(
        self,
        host: str,
        port: int,
        score: float = 40.0,
        proto: str = "http",
        *,
        username: str | None = None,
        password: str | None = None,
        premium: bool = False,
    ) -> None:
        key = _upstream_key(proto, host, port, username=username, password=password)
        with self._lock:
            if key not in self._proxies:
                self._proxies[key] = ProxyStat(
                    host=host,
                    port=port,
                    proto=proto,
                    username=username,
                    password=password,
                    premium=premium,
                    score=score,
                )
            else:
                st = self._proxies[key]
                st.score = max(st.score, score)
                if username is not None:
                    st.username = username
                    st.password = password
                if premium:
                    st.premium = True
        tag = "premium seed" if premium else "seed"
        log("add", f"{tag} {key} score={score:.0f}", force=True)
        log("pool", self.snapshot_line())

    def seed_premium(self, raw: str, *, score: float = 95.0) -> bool:
        """Parse Evomi/standard URL and insert as preferred upstream. Returns True if ok."""
        spec = parse_upstream_spec(raw, default_proto="socks5", premium=True)
        if not spec:
            log("cfg", f"premium parse failed: {raw[:40]}…", force=True)
            return False
        self.seed(
            spec.host,
            spec.port,
            score=score,
            proto=spec.proto,
            username=spec.username,
            password=spec.password,
            premium=True,
        )
        sess = _session_tag(spec.password)
        extra = f" session={sess}" if sess else ""
        log("cfg", f"premium preferred → {spec.redacted()}{extra}", force=True)
        return True

    def add_or_boost(
        self,
        host: str,
        port: int,
        *,
        ye1: bool,
        sparql: bool,
        latency_ms: float,
        detail: str,
        proto: str = "http",
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Hunter found YE1-good proxy — provisional hunt_boost, decays without live traffic."""
        key = _upstream_key(proto, host, port, username=username, password=password)
        now = time.time()
        with self._lock:
            st = self._proxies.get(key) or ProxyStat(
                host=host,
                port=port,
                proto=proto,
                username=username,
                password=password,
                score=25.0,
            )
            st.attempts += 1
            st.connect_ok += 1
            if ye1:
                st.ye1_ok += 1
            if sparql:
                st.sparql_ok += 1
            st.total_latency_ms += latency_ms
            st.last_ok_at = now
            st.last_detail = detail
            st.consec_fails = 0
            st.quarantine_until = 0.0
            boost = 35.0
            if sparql:
                boost += 10.0
            if latency_ms < 1500:
                boost += 5.0
            st.hunt_boost = max(st.hunt_boost * 0.3, boost)
            st.hunt_boost_at = now
            st.push_outcome(True, now)
            self._proxies[key] = st
        log("pool", self.snapshot_line())

    def record_connect_success(
        self,
        host: str,
        port: int,
        latency_ms: float,
        *,
        proto: str = "http",
        target_host: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        key = _upstream_key(proto, host, port, username=username, password=password)
        now = time.time()
        with self._lock:
            st = self._proxies.get(key)
            if not st:
                return
            st.attempts += 1
            st.connect_ok += 1
            st.consec_fails = 0
            st.total_latency_ms += latency_ms
            st.last_ok_at = now
            st.quarantine_until = 0.0
            st.push_outcome(True, now)
            if st.hunt_boost > 0:
                st.score = min(100.0, st.score + min(15.0, st.hunt_boost * 0.25))
                st.hunt_boost *= 0.5
            self.req_ok += 1
            self._push_recent(True)
            self._sticky_key = key
            self._sticky_until = now + self.sticky_ttl
            if target_host:
                th = target_host.lower()
                self._sticky_by_host[th] = (key, now + self.sticky_ttl)
                rk = self._route_key(key, th)
                rt = self._routes.get(rk) or RouteStat()
                rt.ok += 1
                rt.consec_fails = 0
                rt.quarantine_until = 0.0
                rt.last_detail = "tunnel ok"
                self._routes[rk] = rt
        host_note = f", host={target_host}" if target_host else ""
        log("sticky", f"sticky → {key} for {self.sticky_ttl:.0f}s (ok{host_note})", force=True)
        log("pool", self.snapshot_line())

    def record_route_failure(
        self,
        host: str,
        port: int,
        target_host: str,
        reason: str,
        *,
        timeout: bool = False,
        proto: str = "http",
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Soft demote: quarantine this upstream only for target_host (not global drop)."""
        key = _upstream_key(proto, host, port, username=username, password=password)
        now = time.time()
        th = target_host.lower()
        with self._lock:
            st = self._proxies.get(key)
            if not st:
                st = ProxyStat(
                    host=host,
                    port=port,
                    proto=proto,
                    username=username,
                    password=password,
                    score=20.0,
                )
                self._proxies[key] = st
            st.attempts += 1
            st.failures += 1
            if timeout:
                st.timeouts += 1
            st.last_fail_at = now
            st.last_detail = f"{th}: {reason}"
            st.push_outcome(False, now)
            rk = self._route_key(key, th)
            rt = self._routes.get(rk) or RouteStat()
            rt.fail += 1
            rt.consec_fails += 1
            rt.last_detail = reason
            q = min(
                ROUTE_QUARANTINE_CAP_S,
                ROUTE_QUARANTINE_BASE_S * (2 ** max(0, rt.consec_fails - 1)),
            )
            rt.quarantine_until = now + q
            self._routes[rk] = rt
            sticky = self._sticky_by_host.get(th)
            if sticky and sticky[0] == key:
                del self._sticky_by_host[th]
            self.req_fail += 1
            self._push_recent(False)
            consec = rt.consec_fails
            # If this host now has too few route-eligible upstreams, wake hunter.
            n_host = sum(
                1
                for p in self._proxies.values()
                if not self._is_quarantined(p, now)
                and not self._route_blocked(p.key, th, now)
                and p.effective_score(now) >= self.score_floor
            )
            thin = n_host < self.min_usable
        log(
            "route",
            f"route-Q {key} → {th} {q:.0f}s (consec={consec}) {reason[:70]}",
            force=True,
        )
        log("pool", self.snapshot_line())
        if thin:
            self.nudge_hunt(f"route-thin {th} eligible={n_host}<{self.min_usable}")

    def record_failure(
        self,
        host: str,
        port: int,
        reason: str,
        *,
        timeout: bool = False,
        proto: str = "http",
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Global quarantine — hunter / optional CONNECT preflight / proxy-hard fails."""
        key = _upstream_key(proto, host, port, username=username, password=password)
        now = time.time()
        with self._lock:
            st = self._proxies.get(key)
            if not st:
                st = ProxyStat(
                    host=host,
                    port=port,
                    proto=proto,
                    username=username,
                    password=password,
                    score=20.0,
                )
                self._proxies[key] = st
            st.attempts += 1
            st.failures += 1
            st.consec_fails += 1
            if timeout:
                st.timeouts += 1
            st.last_fail_at = now
            st.last_detail = reason
            st.push_outcome(False, now)
            q = min(
                self.quarantine_cap,
                self.quarantine_base * (2 ** max(0, st.consec_fails - 1)),
            )
            st.quarantine_until = now + q
            if self._sticky_key == key:
                self._sticky_key = None
                self._sticky_until = 0.0
            for h in [h for h, (k, _) in self._sticky_by_host.items() if k == key]:
                del self._sticky_by_host[h]
            rate = st.recent_success_rate(now)
            if st.consec_fails >= 4 and (rate is None or rate < 0.15) and not st.premium:
                del self._proxies[key]
                log("drop", f"drop {key} consec_fails={st.consec_fails} ({reason})", force=True)
            else:
                log(
                    "quarantine",
                    f"quarantine {key} {q:.0f}s (consec={st.consec_fails}) {reason[:60]}",
                    force=True,
                )
            self.req_fail += 1
        log("pool", self.snapshot_line())

    def pick(
        self, exclude: set[str] | None = None, *, target_host: str | None = None
    ) -> ProxyStat | None:
        """Prefer premium, then per-host sticky; else power-of-two among eligible."""
        exclude = exclude or set()
        now = time.time()
        with self._lock:
            th = target_host.lower() if target_host else None

            def _eligible(st: ProxyStat) -> bool:
                return (
                    st.key not in exclude
                    and not self._is_quarantined(st, now)
                    and not self._route_blocked(st.key, th, now)
                    and st.effective_score(now) >= self.dead_below
                )

            if self.prefer_premium:
                premium = [p for p in self._proxies.values() if p.premium and _eligible(p)]
                if premium:
                    # Prefer sticky premium for this host if still eligible.
                    if th:
                        sticky = self._sticky_by_host.get(th)
                        if sticky and sticky[1] > now:
                            st = self._proxies.get(sticky[0])
                            if st and st.premium and _eligible(st):
                                return st
                    if len(premium) == 1:
                        return premium[0]
                    a, b = random.sample(premium, 2)
                    return a if a.effective_score(now) >= b.effective_score(now) else b

            if th:
                sticky = self._sticky_by_host.get(th)
                if sticky and sticky[1] > now and sticky[0] not in exclude:
                    st = self._proxies.get(sticky[0])
                    if (
                        st
                        and not self._is_quarantined(st, now)
                        and not self._route_blocked(st.key, th, now)
                    ):
                        return st
            elif (
                self._sticky_key
                and self._sticky_until > now
                and self._sticky_key not in exclude
            ):
                st = self._proxies.get(self._sticky_key)
                if st and not self._is_quarantined(st, now):
                    return st

            cands = [p for p in self._proxies.values() if _eligible(p)]
            if not cands:
                return None
            usable = [p for p in cands if p.effective_score(now) >= self.score_floor]
            pool = usable or cands
            if len(pool) == 1:
                return pool[0]
            a, b = random.sample(pool, 2)
            return a if a.effective_score(now) >= b.effective_score(now) else b

    def decay(self) -> None:
        now = time.time()
        dropped = 0
        with self._lock:
            for key in list(self._proxies):
                st = self._proxies[key]
                if st.premium:
                    continue  # never idle-drop paid upstream
                last = max(st.last_ok_at, st.last_fail_at)
                idle = (now - last) if last > 0 else 9999.0
                eff = st.effective_score(now)
                if idle > 300 and eff < self.score_floor:
                    del self._proxies[key]
                    dropped += 1
                elif idle > 600:
                    del self._proxies[key]
                    dropped += 1
        if dropped:
            log("drop", f"decay-dropped {dropped} stale prox(ies)", force=True)
            log("pool", self.snapshot_line())


# ---------------------------------------------------------------------------
# Upstream tunnel (HTTP CONNECT / SOCKS5 / SOCKS4)
# ---------------------------------------------------------------------------

def upstream_connect(
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
    """Open tunnel via upstream (http/socks5/socks4). Returns connected socket."""
    return open_upstream_tunnel(
        proto,
        proxy_host,
        proxy_port,
        target_host,
        target_port,
        timeout,
        username=username,
        password=password,
    )


def probe_upstream(
    host: str,
    port: int,
    *,
    proto: str = "http",
    target_host: str,
    target_port: int,
    timeout: float,
    sparql: bool,
    cert_mode: str = "allowlist",
    username: str | None = None,
    password: str | None = None,
) -> tuple[bool, str, float, bool, bool]:
    """Return (ok, detail, latency_ms, cert_ok, sparql_ok).

    cert_mode:
      - allowlist: YE1 or DigiCert (hunter / Wikidata admission)
      - os_trust: system CA verify succeeded + reject MITM-like issuer (CONNECT anti-MITM)
    """
    t0 = time.monotonic()
    sock = None
    ssock = None
    try:
        sock = upstream_connect(
            proto,
            host,
            port,
            target_host,
            target_port,
            timeout,
            username=username,
            password=password,
        )
        ctx = ssl.create_default_context()
        ssock = ctx.wrap_socket(sock, server_hostname=target_host)
        sock = None
        der = ssock.getpeercert(binary_form=True) or b""
        peercert = ssock.getpeercert() or {}
        if cert_mode == "os_trust":
            cert_ok, note = peer_is_os_trusted_leaf(peercert, der=der)
        else:
            cert_ok, note = peer_is_trusted_public_ca(peercert, der=der)
        if not cert_ok:
            return False, note, (time.monotonic() - t0) * 1000, False, False
        sparql_ok = False
        if sparql and target_host == "query.wikidata.org":
            try:
                ssock.close()
            except Exception:
                pass
            ssock = None
            scheme = "socks5" if proto.startswith("socks5") else ("socks4" if proto == "socks4" else "http")
            if username is not None:
                from urllib.parse import quote

                proxy_url = (
                    f"{scheme}://{quote(username, safe='')}:{quote(password or '', safe='')}"
                    f"@{host}:{port}"
                )
            else:
                proxy_url = f"{scheme}://{host}:{port}"
            ok_s, detail_s = sparql_smoke(proxy_url, timeout=min(20.0, timeout + 5))
            sparql_ok = ok_s
            if not ok_s:
                return False, f"cert OK but SPARQL fail: {detail_s}", (time.monotonic() - t0) * 1000, True, False
            return True, f"cert+SPARQL OK ({note})", (time.monotonic() - t0) * 1000, True, True
        return True, note, (time.monotonic() - t0) * 1000, True, sparql_ok
    except ssl.SSLCertVerificationError as e:
        # Typical free-proxy MITM: untrusted / replaced leaf — do not hand to browser.
        return False, f"SSL verify (likely MITM): {e}", (time.monotonic() - t0) * 1000, False, False
    except TimeoutError:
        return False, "timeout", (time.monotonic() - t0) * 1000, False, False
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", (time.monotonic() - t0) * 1000, False, False
    finally:
        for s in (ssock, sock):
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass


# ---------------------------------------------------------------------------
# Hunter
# ---------------------------------------------------------------------------

class Hunter:
    def __init__(
        self,
        pool: ProxyPool,
        *,
        target_host: str,
        target_port: int,
        sparql: bool,
        workers: int = 40,
        batch: int = 400,
        probe_timeout: float = 8.0,
        interval: float = 15.0,
    ) -> None:
        self.pool = pool
        self.target_host = target_host
        self.target_port = target_port
        self.sparql = sparql
        self.workers = workers
        self.batch = batch
        self.probe_timeout = probe_timeout
        self.interval = interval
        self._stop = threading.Event()
        self._hunting = threading.Event()
        self._thread: threading.Thread | None = None
        self._candidates: list[tuple[str, int, str]] = []
        self._cand_lock = threading.Lock()
        self._cursor = 0

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="hunter", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _refresh_candidates(self) -> None:
        log("hunt", "refreshing candidate lists…", force=True)
        rows: list[tuple[str, int, str]] = []
        ok = 0
        for url in DEFAULT_LISTS:
            if self._stop.is_set():
                break
            try:
                got = fetch_proxy_list(url, timeout=20.0)
                rows.extend(got)
                ok += 1
            except Exception:
                continue
        rows = unique_proxies(rows)
        random.shuffle(rows)
        with self._cand_lock:
            self._candidates = rows
            self._cursor = 0
        n_socks = sum(1 for *_, proto in rows if proto.startswith("socks"))
        log(
            "hunt",
            f"candidates loaded: {len(rows)} ({n_socks} socks*) from {ok}/{len(DEFAULT_LISTS)} sources",
            force=True,
        )

    def _next_batch(self) -> list[tuple[str, int, str]]:
        with self._cand_lock:
            if not self._candidates or self._cursor >= len(self._candidates):
                return []
            batch = self._candidates[self._cursor : self._cursor + self.batch]
            self._cursor += len(batch)
            return batch

    def _hunt_once(self, *, force: bool = False) -> int:
        if self._hunting.is_set():
            return 0
        self._hunting.set()
        added = 0
        try:
            batch = self._next_batch()
            if not batch:
                self._refresh_candidates()
                batch = self._next_batch()
            if not batch:
                return 0
            why = self.pool.hunt_reason() if self.pool.needs_hunt() else ("forced" if force else "manual")
            log(
                "hunt",
                f"hunting batch={len(batch)} reason={why} force={force} need_usable≈{self.pool.min_usable}",
                force=True,
            )
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futs = {
                    ex.submit(
                        probe_upstream,
                        h,
                        p,
                        proto=proto,
                        target_host=self.target_host,
                        target_port=self.target_port,
                        timeout=self.probe_timeout,
                        sparql=self.sparql,
                    ): (h, p, proto)
                    for h, p, proto in batch
                }
                for fut in as_completed(futs):
                    if self._stop.is_set():
                        break
                    # Forced hunts finish enough of the batch to actually refill route-thin hosts.
                    if not force and not self.pool.needs_hunt():
                        break
                    if force and added >= max(2, self.pool.min_usable) and not self.pool.needs_hunt():
                        break
                    h, p, proto = futs[fut]
                    try:
                        ok, detail, lat, ye1, sparql_ok = fut.result()
                    except Exception as e:
                        ok, detail, lat, ye1, sparql_ok = False, str(e), 0.0, False, False
                    if ok and ye1:
                        self.pool.add_or_boost(
                            h, p, ye1=ye1, sparql=sparql_ok, latency_ms=lat, detail=detail, proto=proto
                        )
                        added += 1
                        log("add", f"+ {proto}://{h}:{p} score↑ ({detail})", force=True)
            log("hunt", f"hunt round done added={added} | {self.pool.snapshot_line()}", force=True)
            return added
        finally:
            self._hunting.clear()

    def _loop(self) -> None:
        # Initial fill; then wake on interval OR pool.hunt_wake (CONNECT failure / route-thin).
        while not self._stop.is_set():
            force = self.pool.hunt_wake.is_set()
            if force:
                self.pool.hunt_wake.clear()
            need = self.pool.needs_hunt()
            if need or force:
                self._hunt_once(force=force or need)
            else:
                ok, fail, rate = self.pool.recent_fail_stats()
                log(
                    "hunt",
                    f"pool healthy — idle | recent {fail}f/{ok}ok ({rate:.0%}) | {self.pool.snapshot_line()}",
                )
            self.pool.decay()
            # Fail pressure → poll sooner; otherwise normal interval. Wake early on nudge.
            wait = 3.0 if (force or self.pool.needs_hunt()) else self.interval
            self.pool.hunt_wake.wait(timeout=wait)


# ---------------------------------------------------------------------------
# CONNECT gateway server
# ---------------------------------------------------------------------------

def _pipe(a: socket.socket, b: socket.socket) -> None:
    try:
        while True:
            r, _, _ = select.select([a, b], [], [], 60.0)
            if not r:
                break
            for src in r:
                dst = b if src is a else a
                data = src.recv(65536)
                if not data:
                    return
                dst.sendall(data)
    except Exception:
        return
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                s.close()
            except Exception:
                pass


def _read_http_headers(sock: socket.socket, max_bytes: int = 65536) -> bytes:
    buf = b""
    while b"\r\n\r\n" not in buf and len(buf) < max_bytes:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


class Gateway:
    def __init__(
        self,
        pool: ProxyPool,
        *,
        listen_host: str,
        listen_port: int,
        budget: float,
        slice_timeout: float,
        anti_mitm_probe: bool = True,
    ) -> None:
        self.pool = pool
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.budget = budget
        self.slice_timeout = slice_timeout
        self.anti_mitm_probe = anti_mitm_probe
        self._stop = threading.Event()
        self._sock: socket.socket | None = None

    def serve_forever(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.listen_host, self.listen_port))
        self._sock.listen(128)
        self._sock.settimeout(1.0)
        mode = (
            "anti-MITM probe ON (OS-trust before 200)"
            if self.anti_mitm_probe
            else "tunnel-only (cert→client only)"
        )
        log(
            "listen",
            f"listening CONNECT on {self.listen_host}:{self.listen_port} "
            f"(budget={self.budget:.0f}s slice={self.slice_timeout:.0f}s, {mode})",
            force=True,
        )
        log(
            "hint",
            f"export https_proxy=http://127.0.0.1:{self.listen_port} "
            f"http_proxy=http://127.0.0.1:{self.listen_port}",
            force=True,
        )
        while not self._stop.is_set():
            try:
                client, addr = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(
                target=self._handle,
                args=(client, addr),
                name=f"conn-{addr[1]}",
                daemon=True,
            ).start()

    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

    def _handle(self, client: socket.socket, addr: tuple) -> None:
        upstream: socket.socket | None = None
        try:
            client.settimeout(30.0)
            header = _read_http_headers(client)
            if not header:
                return
            first = header.split(b"\r\n", 1)[0].decode("latin-1", errors="replace")
            parts = first.split()
            if len(parts) < 2 or parts[0].upper() != "CONNECT":
                client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n\r\n")
                log("req", f"reject non-CONNECT from {addr[0]}: {first[:60]}", force=True)
                return
            target = parts[1]
            if ":" in target:
                th, _, tp = target.rpartition(":")
                target_host, target_port = th, int(tp)
            else:
                target_host, target_port = target, 443

            deadline = time.monotonic() + self.budget
            tried: set[str] = set()
            last_err = "no upstream"
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                if remaining < 0.5:
                    break
                st = self.pool.pick(exclude=tried, target_host=target_host)
                if st is None:
                    # Wait for hunter / quarantine expiry — do NOT re-hammer failed upstreams.
                    last_err = "empty/quarantined pool" if self.pool.size() else "empty pool"
                    self.pool.nudge_hunt(f"no route-eligible upstream for {target_host}")
                    time.sleep(min(2.5, max(0.8, remaining / 5)))
                    continue
                tried.add(st.key)
                slice_t = min(self.slice_timeout, remaining)
                lat_pf = 0.0
                if self.anti_mitm_probe:
                    # Quality gate: verify real public cert through upstream BEFORE 200.
                    # Failures (MITM/untrusted) → route-Q; browser never sees the bad cert.
                    pre_t = min(slice_t, max(4.0, slice_t * 0.75))
                    ok_pf, detail_pf, lat_pf, cert_pf, _ = probe_upstream(
                        st.host,
                        st.port,
                        proto=st.proto,
                        target_host=target_host,
                        target_port=target_port,
                        timeout=pre_t,
                        sparql=False,
                        cert_mode="os_trust",
                        username=st.username,
                        password=st.password,
                    )
                    if not (ok_pf and cert_pf):
                        last_err = f"{st.key} anti-MITM: {detail_pf}"
                        is_to = "timeout" in detail_pf.lower()
                        self.pool.record_route_failure(
                            st.host,
                            st.port,
                            target_host,
                            f"anti-MITM {detail_pf}",
                            timeout=is_to,
                            proto=st.proto,
                            username=st.username,
                            password=st.password,
                        )
                        continue
                    remaining = deadline - time.monotonic()
                    if remaining < 0.5:
                        break
                    slice_t = min(self.slice_timeout, remaining)

                t0 = time.monotonic()
                try:
                    upstream = upstream_connect(
                        st.proto,
                        st.host,
                        st.port,
                        target_host,
                        target_port,
                        slice_t,
                        username=st.username,
                        password=st.password,
                    )
                    lat = (time.monotonic() - t0) * 1000
                    self.pool.record_connect_success(
                        st.host,
                        st.port,
                        lat,
                        proto=st.proto,
                        target_host=target_host,
                        username=st.username,
                        password=st.password,
                    )
                    client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                    via = st.label()
                    if self.anti_mitm_probe:
                        detail = (
                            f"CONNECT {target_host}:{target_port} via {via} "
                            f"(anti-MITM {lat_pf:.0f}ms + tunnel {lat:.0f}ms, tried={len(tried)})"
                        )
                    else:
                        detail = (
                            f"CONNECT {target_host}:{target_port} via {via} "
                            f"(tunnel {lat:.0f}ms, tried={len(tried)})"
                        )
                    log("req", detail)
                    client.settimeout(None)
                    upstream.settimeout(None)
                    pipe_t0 = time.monotonic()
                    _pipe(client, upstream)
                    upstream = None
                    if time.monotonic() - pipe_t0 < 0.8:
                        self.pool.record_route_failure(
                            st.host,
                            st.port,
                            target_host,
                            "short tunnel after handoff",
                            timeout=False,
                            proto=st.proto,
                            username=st.username,
                            password=st.password,
                        )
                    return
                except Exception as e:
                    last_err = f"{st.key}: {e}"
                    is_to = isinstance(e, TimeoutError) or "timed out" in str(e).lower()
                    self.pool.record_route_failure(
                        st.host,
                        st.port,
                        target_host,
                        str(e),
                        timeout=is_to,
                        proto=st.proto,
                        username=st.username,
                        password=st.password,
                    )
                    if upstream:
                        try:
                            upstream.close()
                        except Exception:
                            pass
                        upstream = None
                    continue

            client.sendall(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n")
            log(
                "req",
                f"FAIL CONNECT {target_host}:{target_port} after {len(tried)} upstream(s): {last_err}",
                force=True,
            )
            self.pool.nudge_hunt(
                f"CONNECT exhausted {target_host} tried={len(tried)} last={last_err[:80]}"
            )
        except Exception as e:
            log("req", f"handler error {addr}: {e}", force=True)
        finally:
            if upstream:
                try:
                    upstream.close()
                except Exception:
                    pass
            try:
                client.close()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listen", type=int, default=12309, help="local CONNECT listen port")
    ap.add_argument("--bind", default="127.0.0.1", help="bind address (default loopback)")
    ap.add_argument("--budget", type=float, default=30.0, help="per-request upstream failover budget (s)")
    ap.add_argument("--slice", type=float, default=5.0, help="max time per upstream attempt (s)")
    ap.add_argument("--min-usable", type=int, default=3, help="hunt when usable proxies below this")
    ap.add_argument("--score-floor", type=float, default=25.0, help="score >= this counts as usable")
    ap.add_argument("--sticky-ttl", type=float, default=60.0, help="seconds to pin a successful upstream")
    ap.add_argument(
        "--quarantine-base",
        type=float,
        default=45.0,
        help="base quarantine seconds after a failure (doubles each consecutive fail)",
    )
    ap.add_argument(
        "--host",
        default="query.wikidata.org",
        help="hunter health-check host (Wikidata YE1+SPARQL)",
    )
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--sparql-check", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument(
        "--anti-mitm-probe",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="OS-trust TLS probe through upstream before CONNECT 200 (default on; "
        "--no-anti-mitm-probe = v3 tunnel-only)",
    )
    ap.add_argument("--workers", type=int, default=40, help="hunter concurrency")
    ap.add_argument("--batch", type=int, default=400, help="proxies probed per hunt round")
    ap.add_argument("--hunt-interval", type=float, default=12.0, help="seconds between hunt checks")
    ap.add_argument(
        "--seed",
        action="append",
        default=[],
        help="seed upstream host:port (repeatable)",
    )
    ap.add_argument(
        "--premium",
        action="append",
        default=[],
        help=(
            "extra paid upstream URL (repeatable), in addition to config/wikidata_premium.local.env. "
            "Formats: socks5://user:pass@host:port OR socks5://host:port:user:pass"
        ),
    )
    ap.add_argument(
        "--no-hardcoded-premium",
        action="store_true",
        help="skip config/wikidata_premium.local.env (only --premium extras, if any)",
    )
    ap.add_argument(
        "--prefer-premium",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="try paid upstream(s) before free pool (default on)",
    )
    ap.add_argument(
        "--premium-smoke",
        type=int,
        default=3,
        help="smoke-test up to N hardcoded premium sessions at start (0=skip)",
    )
    ap.add_argument(
        "--log-file",
        default=str(DEFAULT_LOG_FILE),
        help=f"log file (truncated on each start; default {DEFAULT_LOG_FILE})",
    )
    args = ap.parse_args()

    init_log_file(Path(args.log_file))
    log("log", f"logging to {args.log_file} (fresh file this run)", force=True)
    log(
        "cfg",
        f"v4 sticky_ttl={args.sticky_ttl:.0f}s quarantine_base={args.quarantine_base:.0f}s "
        f"budget={args.budget:.0f}s anti_mitm_probe={args.anti_mitm_probe} "
        f"prefer_premium={args.prefer_premium}",
        force=True,
    )

    pool = ProxyPool(
        min_usable=args.min_usable,
        score_floor=args.score_floor,
        sticky_ttl=args.sticky_ttl,
        quarantine_base=args.quarantine_base,
        prefer_premium=args.prefer_premium,
    )
    for s in args.seed:
        parsed = parse_proxy_line(s)
        if parsed:
            h, p, proto = parsed
            pool.seed(h, p, proto=proto)

    premium_urls: list[str] = []
    if not args.no_hardcoded_premium:
        local_premium = load_local_premium_proxies()
        if not local_premium:
            log(
                "cfg",
                f"no premium upstreams: {PREMIUM_LOCAL_FILE} missing/empty and "
                f"{PREMIUM_ENV_VAR} unset (free pool only)",
                force=True,
            )
        premium_urls.extend(local_premium)
    premium_urls.extend(args.premium)
    seen_prem: set[str] = set()
    n_seeded = 0
    for raw in premium_urls:
        if raw in seen_prem:
            continue
        seen_prem.add(raw)
        if pool.seed_premium(raw):
            n_seeded += 1
    log("cfg", f"premium seeded={n_seeded} (hardcoded={not args.no_hardcoded_premium})", force=True)

    # Smoke a few sessions in parallel (not all 10 — keeps startup snappy).
    premium_stats = [p for p in pool.usable() if p.premium]
    random.shuffle(premium_stats)
    smoke_n = max(0, min(args.premium_smoke, len(premium_stats)))
    smoke_targets = premium_stats[:smoke_n]

    def _smoke_one(st: ProxyStat) -> tuple[ProxyStat, bool, str, float]:
        ok, detail, lat, cert_ok, _ = probe_upstream(
            st.host,
            st.port,
            proto=st.proto,
            target_host=args.host,
            target_port=args.port,
            timeout=12.0,
            sparql=False,
            cert_mode="os_trust",
            username=st.username,
            password=st.password,
        )
        return st, bool(ok and cert_ok), detail, lat

    if smoke_targets:
        with ThreadPoolExecutor(max_workers=min(5, len(smoke_targets))) as ex:
            for st, ok, detail, lat in ex.map(_smoke_one, smoke_targets):
                if ok:
                    pool.record_connect_success(
                        st.host,
                        st.port,
                        lat,
                        proto=st.proto,
                        target_host=args.host,
                        username=st.username,
                        password=st.password,
                    )
                    log("cfg", f"premium smoke OK {st.label()} {lat:.0f}ms ({detail})", force=True)
                else:
                    pool.record_route_failure(
                        st.host,
                        st.port,
                        args.host,
                        f"premium smoke: {detail}",
                        proto=st.proto,
                        username=st.username,
                        password=st.password,
                    )
                    log("cfg", f"premium smoke FAIL {st.label()}: {detail}", force=True)

    hunter = Hunter(
        pool,
        target_host=args.host,
        target_port=args.port,
        sparql=args.sparql_check,
        workers=args.workers,
        batch=args.batch,
        interval=args.hunt_interval,
    )
    gw = Gateway(
        pool,
        listen_host=args.bind,
        listen_port=args.listen,
        budget=args.budget,
        slice_timeout=args.slice,
        anti_mitm_probe=args.anti_mitm_probe,
    )

    hunter.start()
    try:
        gw.serve_forever()
    except KeyboardInterrupt:
        log("exit", "Ctrl+C — shutting down", force=True)
    finally:
        gw.stop()
        hunter.stop()
        log("exit", f"bye | {pool.snapshot_line()}", force=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
