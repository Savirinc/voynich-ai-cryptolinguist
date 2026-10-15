"""Sourced plaintext corpora for the known-answer curriculum.

Source: Project Gutenberg (public domain in the USA), selected deterministically from the
official catalog (data/raw/corpora/pg_catalog.csv). Raw downloads are not committed; their
URL, Gutenberg id, title, author and SHA-256 are recorded in data/raw/corpora/SOURCE_MANIFEST.json
so the corpus can be rebuilt and verified (`python -m vcl.synthetic.corpora fetch`).

Text normalisation: strip the PG header/footer, lowercase, keep letters of the language's
script (Unicode category L*) and single spaces. Non-Latin scripts are kept native, so solvers
meet genuinely different alphabets.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORPORA = ROOT / "data/raw/corpora"
MANIFEST = CORPORA / "SOURCE_MANIFEST.json"

# language code -> (family, script)
LANGUAGES = {
    "en": ("germanic", "latin"), "de": ("germanic", "latin"), "nl": ("germanic", "latin"),
    "sv": ("germanic", "latin"), "da": ("germanic", "latin"), "no": ("germanic", "latin"),
    "af": ("germanic", "latin"), "is": ("germanic", "latin"), "fy": ("germanic", "latin"),
    "enm": ("germanic", "latin"),
    "fr": ("romance", "latin"), "it": ("romance", "latin"), "es": ("romance", "latin"),
    "pt": ("romance", "latin"), "la": ("romance", "latin"), "ca": ("romance", "latin"),
    "ro": ("romance", "latin"), "gl": ("romance", "latin"), "fur": ("romance", "latin"),
    "pl": ("slavic", "latin"), "cs": ("slavic", "latin"), "sl": ("slavic", "latin"),
    "bg": ("slavic", "cyrillic"), "ru": ("slavic", "cyrillic"), "sr": ("slavic", "mixed"),
    "fi": ("uralic", "latin"), "hu": ("uralic", "latin"),
    "tl": ("austronesian", "latin"), "ilo": ("austronesian", "latin"), "ceb": ("austronesian", "latin"),
    "cy": ("celtic", "latin"), "ga": ("celtic", "latin"),
    "el": ("hellenic", "greek"),
    "he": ("semitic", "hebrew"),
    "te": ("dravidian", "telugu"),
    "eo": ("constructed", "latin"),
}
MAX_BOOKS = 6
MAX_CHARS = 400_000


def strip_gutenberg(text: str) -> str:
    s = re.search(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", text, flags=re.I | re.S)
    e = re.search(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", text, flags=re.I)
    return text[s.end() if s else 0: e.start() if e else len(text)]


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    text = "".join(ch if unicodedata.category(ch).startswith(("L", "M")) else " " for ch in text)
    return re.sub(r"\s+", " ", text).strip()


def select_books(catalog=CORPORA / "pg_catalog.csv") -> dict[str, list[dict]]:
    by_lang: dict[str, list[dict]] = {k: [] for k in LANGUAGES}
    for r in csv.DictReader(open(catalog, encoding="utf8")):
        if r["Type"] == "Text" and r["Language"] in by_lang:
            by_lang[r["Language"]].append(r)
    picked = {}
    for lang, rows in by_lang.items():
        # deterministic, author-diverse choice: one book per author, ordered by hashed id
        rows.sort(key=lambda r: hashlib.sha256(f"vcl:{r['Text#']}".encode()).hexdigest())
        seen, out = set(), []
        for r in rows:
            a = r["Authors"].split(";")[0].strip() or "anon"
            if a in seen:
                continue
            seen.add(a); out.append(r)
            if len(out) >= MAX_BOOKS:
                break
        picked[lang] = out
    return picked


def _from_manifest(manifest) -> dict[str, list[dict]]:
    """Rebuild from the committed manifest (the live catalog changes over time)."""
    out: dict[str, list[dict]] = {}
    for bid, m in manifest["books"].items():
        out.setdefault(m["lang"], []).append({"Text#": bid, "Title": m["title"], "Authors": m["author"]})
    return out


def fetch(sleep=1.0, from_catalog=False):
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"source": "Project Gutenberg", "books": {}}
    (CORPORA / "pg").mkdir(parents=True, exist_ok=True)
    selection = select_books() if (from_catalog or not manifest["books"]) else _from_manifest(manifest)
    for lang, rows in selection.items():
        for r in rows:
            bid = r["Text#"]
            dest = CORPORA / "pg" / f"{lang}_{bid}.txt"
            if bid in manifest["books"] and dest.exists():
                continue
            expected = manifest["books"].get(bid, {}).get("normalised_sha256")
            url = f"https://www.gutenberg.org/cache/epub/{bid}/pg{bid}.txt"
            try:
                raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "vcl-research/0.1"}),
                                             timeout=60).read()
            except Exception as ex:  # noqa: BLE001 - record and continue
                print("FAIL", lang, bid, ex); continue
            text = normalise(strip_gutenberg(raw.decode("utf8", errors="replace")))[:MAX_CHARS]
            if len(text) < 5000:
                print("SKIP short", lang, bid, len(text)); continue
            if expected and hashlib.sha256(text.encode()).hexdigest() != expected:
                print("HASH MISMATCH (upstream text changed)", lang, bid); continue
            dest.write_text(text, encoding="utf8")
            manifest["books"][bid] = {"lang": lang, "family": LANGUAGES[lang][0], "script": LANGUAGES[lang][1],
                                      "title": r["Title"][:200], "author": r["Authors"][:200], "url": url,
                                      "raw_sha256": hashlib.sha256(raw).hexdigest(),
                                      "normalised_sha256": hashlib.sha256(text.encode()).hexdigest(),
                                      "chars": len(text), "licence": "Public domain in the USA (Project Gutenberg)"}
            print("ok", lang, bid, len(text), r["Title"][:50])
            MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
            time.sleep(sleep)


def load_books() -> list[dict]:
    """All fetched books as dicts with provenance + 'text'. Verifies normalised hashes."""
    manifest = json.loads(MANIFEST.read_text())
    out = []
    for bid, m in sorted(manifest["books"].items(), key=lambda kv: (kv[1]["lang"], kv[0])):
        text = (CORPORA / "pg" / f"{m['lang']}_{bid}.txt").read_text(encoding="utf8")
        if hashlib.sha256(text.encode()).hexdigest() != m["normalised_sha256"]:
            raise ValueError(f"corpus hash mismatch for {bid}")
        out.append(m | {"id": bid, "text": text})
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["fetch"]:
        fetch()
