"""Semantic-anchor helpers (E010 / E010B).

Reads Voynich label text from the local ZL3b IVTFF via vcl.corpus.ivtff, exposes the zodiac
page structure (label rings, circular text rings) recorded in the transcription's comments,
and loads the curated anchor dataset data/derived/anchors_v1/anchors.jsonl.

Nothing here proposes a reading of any Voynich word.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from .corpus.ivtff import LINE_RE, PAGE_RE, parse, read_docx_lines

ROOT = Path(__file__).resolve().parents[2]
ANCHORS = ROOT / "data/derived/anchors_v1/anchors.jsonl"
SPLITS = ROOT / "data/derived/splits.json"

# Zodiac pages in manuscript order. Month spellings: R. Zandbergen, voynich.nu/writing.html
# (accessed 2026-10-17); '(m)' etc. are his expansion marks, kept verbatim. 'zl_comment' is the
# spelling given in the ZL3b transcription's own page comments (only three pages mention it).
ZODIAC = [
    # folio,  sign,              month_voynich_nu, zl_comment, modern month
    ("f70v2", "Pisces",          "mars",           "Mars",  "March"),
    ("f70v1", "Aries (dark)",    "aberil",         "Abril", "April"),
    ("f71r",  "Aries (light)",   "aberil",         None,    "April"),
    ("f71v",  "Taurus (light)",  "may",            "May",   "May"),
    ("f72r1", "Taurus (dark)",   "may",            None,    "May"),
    ("f72r2", "Gemini",          "jong",           None,    "June"),
    ("f72r3", "Cancer",          "iollet",         None,    "July"),
    ("f72v3", "Leo",             "augst",          None,    "August"),
    ("f72v2", "Virgo",           "septe(m)b(r)",   None,    "September"),
    ("f72v1", "Libra",           "octe(m)bre",     None,    "October"),
    ("f73r",  "Scorpius",        "nove(m)bre",     None,    "November"),
    ("f73v",  "Sagittarius",     "decebre",        None,    "December"),
]
ZODIAC_FOLIOS = [z[0] for z in ZODIAC]


def locked_leaves() -> set[str]:
    return set(json.loads(SPLITS.read_text())["locked_test_leaves"])


@lru_cache(maxsize=1)
def _lines() -> tuple[str, ...]:
    return tuple(read_docx_lines())


@lru_cache(maxsize=1)
def _parsed():
    return parse(list(_lines()))


def tokens_of(folio: str):
    return [t for t in _parsed()[1] if t.folio == folio]


def first_word(folio: str) -> str | None:
    """First token of the first paragraph-text (P) locus of a page."""
    for t in tokens_of(folio):
        if t.locus_type == "P":
            return t.eva
    return None


def page_labels(folio: str) -> list[dict]:
    """Label loci (type L) of a page: [{'locus': 'f2r.14', 'eva': 'ytoail', 'tokens': [...]}]."""
    out: dict[str, dict] = {}
    for t in tokens_of(folio):
        if t.locus_type == "L":
            key = f"{folio}.{t.line_no}"
            out.setdefault(key, {"locus": key, "type": t.locus, "tokens": []})["tokens"].append(t.eva)
    for v in out.values():
        v["eva"] = ".".join(v["tokens"])
    return list(out.values())


def zodiac_structure(folio: str) -> dict:
    """Ring structure of one zodiac page, from the transcription's own comments (structure only).

    Returns {'label_groups': [{'heading', 'labels': [{'locus','clock','tokens','eva'}]}],
             'text_rings': [{'locus','tokens'}]}  in transcription order (outer -> inner for rings).
    A label group starts at every '@L' locus; its heading is the last '#' comment seen before it.
    """
    lines = _lines()
    toks = {(t.line_no): [] for t in tokens_of(folio)}
    for t in tokens_of(folio):
        toks[t.line_no].append(t.eva)
    cur, heading, groups, rings = None, "", [], []
    for raw in lines:
        s = raw.strip()
        m = PAGE_RE.match(s)
        if m:
            cur = m.group(1)
            continue
        if cur != folio:
            continue
        if s.startswith("#"):
            c = s.lstrip("# ").strip()
            if c:
                heading = c
            continue
        m = LINE_RE.match(s)
        if not m or m.group(1) != folio:
            continue
        num, locus, body = int(m.group(2)), m.group(3), m.group(4)
        clock = re.match(r"<!(\d\d:\d\d)>", body)
        if "L" in locus:
            if locus.startswith("@") or not groups:
                groups.append({"heading": heading, "labels": []})
            groups[-1]["labels"].append({"locus": f"{folio}.{num}", "clock": clock.group(1) if clock else None,
                                         "tokens": toks.get(num, []), "eva": ".".join(toks.get(num, []))})
        elif "C" in locus:
            if locus.startswith("@") or not rings:
                rings.append({"locus": f"{folio}.{num}", "tokens": []})
            rings[-1]["tokens"].extend(toks.get(num, []))
    return {"label_groups": groups, "text_rings": rings}


def zodiac_pages() -> list[dict]:
    locked = locked_leaves()
    pages = _parsed()[0]
    out = []
    for folio, sign, month, zl, modern in ZODIAC:
        st = zodiac_structure(folio)
        leaf = pages[folio].leaf
        out.append({"folio": folio, "leaf": leaf, "locked": leaf in locked, "sign": sign,
                    "month_latin_script": month, "month_zl_comment": zl, "month_modern": modern,
                    "n_labels": sum(len(g["labels"]) for g in st["label_groups"]), **st})
    return out


def load_anchors(path: Path = ANCHORS) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
