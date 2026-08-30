"""Load gitignored browser sessions from config/*.local or the environment."""

from __future__ import annotations

import os
from pathlib import Path

from _paths import CONFIG


def load_kv_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        out[key.strip().upper()] = val.strip()
    return out


def load_cookie(*, env_name: str, filename: str) -> str:
    env = os.environ.get(env_name, "").strip()
    if env:
        return env
    return (load_kv_file(CONFIG / filename).get("COOKIE") or "").strip()


def load_field(*, env_name: str, filename: str, key: str) -> str:
    env = os.environ.get(env_name, "").strip()
    if env:
        return env
    return (load_kv_file(CONFIG / filename).get(key.upper()) or "").strip()
