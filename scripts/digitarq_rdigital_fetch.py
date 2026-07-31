#!/usr/bin/env python3
"""Fetch Digitarq RPD file lists + dissemination images via local CONNECT proxy.

Correct endpoints (browser fileViewer):
  GET /api/rdigital/<docUuid>?fromIndex=&max=   → page of file descriptors
  GET /rdigital/dissemination?fileId=<id>       → JPEG/PNG

Auth: JWT from Digitarq login cookie `token=…`
  (file: config/digitarq_token.local, or --token, or env DIGITARQ_TOKEN)

Proxy (required by default):
  export https_proxy=http://127.0.0.1:12309 http_proxy=http://127.0.0.1:12309
  (or pass --proxy)

Examples:
  .venv/bin/python scripts/digitarq_rdigital_fetch.py \\
    --uuid 0411458db88448f5b433cb70bae3d12d --catalog-only

  .venv/bin/python scripts/digitarq_rdigital_fetch.py \\
    --uuid 0411458db88448f5b433cb70bae3d12d --download --ocr-scan \\
    --keep-keywords azevedo,bispo,1480,1476,1495,prazo,livro
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _paths import CONFIG, DATA_RAW, OUTPUT_LOGS  # noqa: E402

DEFAULT_UUID = "0411458db88448f5b433cb70bae3d12d"
DEFAULT_PROXY = "http://127.0.0.1:12309"
DEFAULT_OUT = DATA_RAW / "azevedo_porto" / "digitarq" / "cvseprt_002_0043"
TOKEN_FILE = CONFIG / "digitarq_token.local"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)

# B1 / Azevedo / early prazo signals (case-insensitive substring match on OCR)
DEFAULT_KEYWORDS = (
    "azevedo",
    "azeevedo",
    "bispo",
    "oporto",
    "porto",
    "donato",
    "xabregas",
    "1480",
    "1476",
    "1475",
    "1495",
    "1492",
    "1510",
    "1517",
    "1535",
    "prazo",
    "livro 51",
    "liv. 51",
    "copia",
    "cópia",
    "sentenca",
    "sentença",
)


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def load_token(explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    env = (os.environ.get("DIGITARQ_TOKEN") or "").strip()
    if env:
        return env
    if TOKEN_FILE.is_file():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
        # allow "token=…" lines
        if t.lower().startswith("token="):
            t = t.split("=", 1)[1].strip()
        if t:
            return t
    raise SystemExit(
        f"No Digitarq JWT. Put it in {TOKEN_FILE} or pass --token / DIGITARQ_TOKEN"
    )


def make_opener(proxy: str | None, *, insecure: bool) -> urllib.request.OpenerDirector:
    handlers: list[urllib.request.BaseHandler] = []
    if proxy:
        handlers.append(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers)


def http_json(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    token: str,
    referer: str,
    timeout: float,
) -> object:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json, text/plain, */*",
            "User-Agent": UA,
            "Referer": referer,
            "Cookie": f"token={token}",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    with opener.open(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8"))


def http_bytes(
    opener: urllib.request.OpenerDirector,
    url: str,
    *,
    token: str,
    referer: str,
    timeout: float,
    accept: str = "*/*",
) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": UA,
            "Referer": referer,
            "Cookie": f"token={token}",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
        method="GET",
    )
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()


def fetch_catalog(
    opener: urllib.request.OpenerDirector,
    *,
    uuid: str,
    token: str,
    page_size: int,
    timeout: float,
) -> list[dict[str, object]]:
    base = f"https://digitarq.arquivos.pt/api/rdigital/{uuid}"
    referer = (
        f"https://digitarq.arquivos.pt/fileViewer/{uuid}"
        f"?isRepresentation=false"
    )
    first = http_json(
        opener,
        f"{base}?fromIndex=0&max={page_size}",
        token=token,
        referer=referer,
        timeout=timeout,
    )
    if not isinstance(first, dict):
        raise RuntimeError(f"unexpected catalog payload: {type(first)}")
    total = int(first.get("total") or 0)
    results = list(first.get("results") or [])
    log(f"catalog total={total} first_page={len(results)}")
    from_index = len(results)
    while from_index < total:
        page = http_json(
            opener,
            f"{base}?fromIndex={from_index}&max={page_size}",
            token=token,
            referer=referer,
            timeout=timeout,
        )
        if not isinstance(page, dict):
            raise RuntimeError("bad page payload")
        batch = list(page.get("results") or [])
        if not batch:
            log(f"empty page at fromIndex={from_index}; stop")
            break
        results.extend(batch)
        from_index += len(batch)
        if from_index % 50 == 0 or from_index >= total:
            log(f"catalog progress {from_index}/{total}")
        time.sleep(0.05)
    return results


def page_index_from_name(name: str) -> int | None:
    # Digitarq names vary: "..._m0123.jpg" or bare "m0123.jpg"
    m = re.search(r"(?:^|_)m(\d+)\.(?:jpg|jpeg|png|tif|tiff)$", name, re.I)
    return int(m.group(1)) if m else None


def download_one(
    opener: urllib.request.OpenerDirector,
    *,
    uuid: str,
    token: str,
    file_id: str,
    dest: Path,
    timeout: float,
) -> tuple[str, bool, str]:
    if dest.exists() and dest.stat().st_size > 1000:
        return file_id, True, "exists"
    referer = (
        f"https://digitarq.arquivos.pt/fileViewer/{uuid}"
        f"?isRepresentation=false&selectedFile={file_id}&fileType=IMAGE"
    )
    url = f"https://digitarq.arquivos.pt/rdigital/dissemination?fileId={file_id}"
    try:
        data = http_bytes(
            opener,
            url,
            token=token,
            referer=referer,
            timeout=timeout,
            accept="image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        )
        if len(data) < 500 or data[:1] == b"{":
            return file_id, False, f"bad body len={len(data)}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
        return file_id, True, f"{len(data)}b"
    except urllib.error.HTTPError as e:
        return file_id, False, f"HTTP {e.code}"
    except Exception as e:
        return file_id, False, f"{type(e).__name__}: {e}"


def ocr_image(path: Path, *, langs: tuple[str, ...] = ("por+eng", "eng+lat", "eng")) -> str:
    """Best-effort OCR; Portuguese pack may be missing — fall back through langs."""
    import subprocess

    for lang in langs:
        try:
            r = subprocess.run(
                ["tesseract", str(path), "stdout", "-l", lang, "--psm", "6"],
                capture_output=True,
                timeout=90,
                check=False,
            )
            text = (r.stdout or b"").decode("utf-8", errors="replace").strip()
            if text:
                return text
        except FileNotFoundError:
            break
        except Exception:
            continue
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(path)
        for lang in langs:
            try:
                text = (pytesseract.image_to_string(img, lang=lang) or "").strip()
                if text:
                    return text
            except Exception:
                continue
    except ImportError:
        pass
    return ""


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    low = text.lower()
    return [k for k in keywords if k.lower() in low]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uuid", default=DEFAULT_UUID, help="Digitarq document UUID")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output directory")
    ap.add_argument("--token", default=None, help="JWT (else config/digitarq_token.local)")
    ap.add_argument("--proxy", default=os.environ.get("https_proxy") or DEFAULT_PROXY)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--insecure", action="store_true", default=True, help="skip TLS verify (MITM gateway)")
    ap.add_argument("--page-size", type=int, default=50)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--catalog-only", action="store_true")
    ap.add_argument("--download", action="store_true", help="download images")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument(
        "--indices",
        default="",
        help="comma page indices (mNNNN) to download, 1-based from filename",
    )
    ap.add_argument(
        "--every",
        type=int,
        default=0,
        help="also download every Nth page (0=off)",
    )
    ap.add_argument(
        "--range",
        default="",
        help="download inclusive page range like 1-40 or 900-1078",
    )
    ap.add_argument("--all", action="store_true", help="download all pages (large)")
    ap.add_argument("--ocr-scan", action="store_true", help="OCR downloaded images; copy hits to keep/")
    ap.add_argument(
        "--keep-keywords",
        default=",".join(DEFAULT_KEYWORDS),
        help="comma keywords for OCR keep filter",
    )
    ap.add_argument("--sleep", type=float, default=0.05)
    args = ap.parse_args()

    token = load_token(args.token)
    proxy = None if args.no_proxy else args.proxy
    out: Path = args.out
    img_dir = out / "images"
    keep_dir = out / "keep"
    ocr_dir = out / "ocr"
    out.mkdir(parents=True, exist_ok=True)
    log_path = OUTPUT_LOGS / "digitarq_rdigital_fetch.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    opener = make_opener(proxy, insecure=args.insecure)
    log(f"uuid={args.uuid} proxy={proxy or '(none)'} out={out}")

    catalog_path = out / "catalog.json"
    if catalog_path.exists() and not args.catalog_only:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        log(f"loaded catalog {len(catalog)} from {catalog_path}")
    else:
        catalog = fetch_catalog(
            opener,
            uuid=args.uuid,
            token=token,
            page_size=args.page_size,
            timeout=args.timeout,
        )
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        log(f"wrote {catalog_path} n={len(catalog)}")

    if args.catalog_only:
        return 0

    # Build selection of pages to download
    by_idx: dict[int, dict[str, object]] = {}
    for row in catalog:
        name = str(row.get("name") or "")
        idx = page_index_from_name(name)
        if idx is not None:
            by_idx[idx] = row

    want: set[int] = set()
    if args.all:
        want.update(by_idx)
    if args.indices.strip():
        for part in args.indices.split(","):
            part = part.strip()
            if part.isdigit():
                want.add(int(part))
    if args.range.strip():
        a, _, b = args.range.partition("-")
        want.update(range(int(a), int(b) + 1))
    if args.every and args.every > 0:
        want.update(i for i in by_idx if i % args.every == 1 or i % args.every == 0)

    # Sensible default sample if nothing specified but --download
    if args.download and not want:
        # cover + indice + early body + mid + late (livro copies often deeper)
        want.update(range(1, 41))
        want.update(range(100, 121))
        want.update(range(200, 211))
        want.update(range(400, 411))
        want.update(range(600, 611))
        want.update(range(800, 811))
        want.update(range(1000, 1079))
        log(f"default sample selection n={len(want)}")

    if not args.download:
        log("nothing to download (pass --download). catalog ready.")
        return 0

    jobs: list[tuple[int, str, Path]] = []
    for idx in sorted(want):
        row = by_idx.get(idx)
        if not row:
            continue
        fid = str(row["id"])
        name = str(row.get("name") or f"{fid}.jpg")
        jobs.append((idx, fid, img_dir / name))

    log(f"download jobs={len(jobs)} workers={args.workers}")
    ok_n = fail_n = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = {
            ex.submit(
                download_one,
                opener,
                uuid=args.uuid,
                token=token,
                file_id=fid,
                dest=dest,
                timeout=args.timeout,
            ): (idx, fid, dest)
            for idx, fid, dest in jobs
        }
        for fut in as_completed(futs):
            idx, fid, dest = futs[fut]
            _fid, ok, detail = fut.result()
            if ok:
                ok_n += 1
            else:
                fail_n += 1
                log(f"FAIL m{idx:04d} fileId={fid} {detail}")
            if (ok_n + fail_n) % 20 == 0:
                log(f"download progress ok={ok_n} fail={fail_n}")
            time.sleep(args.sleep)

    log(f"download done ok={ok_n} fail={fail_n}")

    if not args.ocr_scan:
        return 0 if fail_n == 0 else 1

    keywords = [k.strip() for k in args.keep_keywords.split(",") if k.strip()]
    keep_dir.mkdir(parents=True, exist_ok=True)
    ocr_dir.mkdir(parents=True, exist_ok=True)
    hits_meta: list[dict[str, object]] = []
    scanned = 0
    for idx, fid, dest in jobs:
        if not dest.exists():
            continue
        text = ocr_image(dest)
        scanned += 1
        ocr_path = ocr_dir / (dest.stem + ".txt")
        ocr_path.write_text(text, encoding="utf-8")
        hits = keyword_hits(text, keywords)
        if hits:
            keep_path = keep_dir / dest.name
            if not keep_path.exists():
                keep_path.write_bytes(dest.read_bytes())
            hits_meta.append(
                {
                    "page": idx,
                    "fileId": fid,
                    "name": dest.name,
                    "keywords": hits,
                    "ocr_excerpt": text[:800].replace("\n", " "),
                }
            )
            log(f"KEEP m{idx:04d} hits={hits}")
        if scanned % 10 == 0:
            log(f"ocr progress {scanned}/{len(jobs)} keeps={len(hits_meta)}")

    meta_path = out / "keep_hits.json"
    meta_path.write_text(json.dumps(hits_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"ocr done scanned={scanned} keeps={len(hits_meta)} → {keep_dir}")
    log_path.write_text(
        f"uuid={args.uuid}\nok={ok_n}\nfail={fail_n}\nkeeps={len(hits_meta)}\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
