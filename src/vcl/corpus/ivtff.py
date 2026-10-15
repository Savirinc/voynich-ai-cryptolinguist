"""IVTFF (Intermediate Voynich Transliteration File Format) parser with full provenance.

Reads the ZL3b EVA transliteration directly from the original DOCX supplied in the
handoff (data/raw/handoff/source_dump/IVTFF Eva.txt.docx). Nothing is normalised
away silently: every token keeps its raw form plus flags describing uncertainty,
alternative readings, ligature braces and rare (@nnn;) glyphs, so that filtering is
an explicit, recorded choice made downstream.

IVTFF conventions used here (ZL3b header comments and Zandbergen's IVTFF 2.0 spec):
  page header  <f1r>  <! $Q=quire $P=page-in-quire $F=fold $B=bifolio $I=illustration
                         $L=Currier language $H=hand $C=column ... >
  line locus   <f1r.3,+P0>  first char: @ new unit, + continuation, * new paragraph,
               = last line, & / ~ label continuations; then type P (paragraph text),
               L (label), C (circular), R (radial), and a subtype.
  inline       '.' certain word space, ',' uncertain word space, <%> paragraph start,
               <$> paragraph end, <-> break for drawing, <!...> comment,
               [a:b] alternative readings, {..} ligature/joined glyphs,
               @nnn; rare glyph code, ? unreadable glyph.
"""
from __future__ import annotations

import hashlib
import html
import re
import zipfile
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCX = ROOT / "data/raw/handoff/source_dump/IVTFF Eva.txt.docx"
DOCX_SHA256 = "6aedc059275bc18c0d4db15a6a6c2e851e9f93a7b532cbed907a34c0db69ddb7"

PAGE_RE = re.compile(r"^<(f\w+?)>\s*<!([^>]*)>")
LINE_RE = re.compile(r"^<(f\w+?)\.(\d+),([^>]+)>\s*(.*)$")
FOLIO_NUM_RE = re.compile(r"^f(\d+)")
TAG_RE = re.compile(r"\$([A-Z])=([^\s$>]+)")


@dataclass
class Page:
    folio: str
    quire: str = "?"
    page_in_quire: str = "?"
    bifolio: str = "?"
    illustration: str = "?"
    currier: str = "?"
    hand: str = "?"
    tags: dict = field(default_factory=dict)

    @property
    def leaf(self) -> str:
        """Physical leaf = folio number (recto and verso share a leaf).

        Pages without a numeric folio (e.g. the Rosettes foldout 'fRos') get their own leaf id.
        """
        m = FOLIO_NUM_RE.match(self.folio)
        return m.group(1) if m else self.folio

    @property
    def bifolio_id(self) -> str:
        """Physical sheet: quire + bifolio number. Stricter grouping than leaf."""
        return f"{self.quire}{self.bifolio}"


@dataclass
class Token:
    folio: str
    leaf: str
    bifolio_id: str
    quire: str
    illustration: str
    currier: str
    hand: str
    line_no: int
    locus: str            # e.g. '+P0'
    locus_type: str       # P / L / C / R / ?
    mode: str             # prose / label / circle / radial
    para_start: bool      # line opens a paragraph (<%> or locus @/*)
    para_end: bool        # line closes a paragraph (<$> or locus =)
    idx: int              # index within line
    n_in_line: int
    raw: str              # token exactly as written (comments removed)
    eva: str              # first alternative reading, braces dropped, rare glyphs kept as @nnn;
    uncertain_glyph: bool  # contains '?'
    alternative: bool      # contains [a:b]
    ligature: bool         # contains {..}
    rare_glyph: bool       # contains @nnn;
    space_before: str      # '.' certain, ',' uncertain, '' line start, '-' drawing break

    @property
    def is_clean(self) -> bool:
        return re.fullmatch(r"[a-z]+", self.eva) is not None and not self.uncertain_glyph


def read_docx_lines(path: Path = DOCX) -> list[str]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != DOCX_SHA256:
        raise ValueError(f"IVTFF DOCX hash mismatch: {digest}")
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf8")
    lines = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        runs = re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, flags=re.S)
        lines.append(html.unescape("".join(runs)))
    return lines


def _first_alternative(s: str) -> str:
    return re.sub(r"\[([^:\]]*)(?::[^\]]*)*\]", r"\1", s)


def _mode(locus_type: str) -> str:
    return {"P": "prose", "L": "label", "C": "circle", "R": "radial"}.get(locus_type, "other")


def parse(lines: list[str] | None = None) -> tuple[dict[str, Page], list[Token]]:
    lines = read_docx_lines() if lines is None else lines
    pages: dict[str, Page] = {}
    tokens: list[Token] = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = PAGE_RE.match(s)
        if m:
            folio, header = m.groups()
            tags = dict(TAG_RE.findall(header))
            pages[folio] = Page(folio, tags.get("Q", "?"), tags.get("P", "?"), tags.get("B", "?"),
                                tags.get("I", "?"), tags.get("L", "?"), tags.get("H", "?"), tags)
            continue
        m = LINE_RE.match(s)
        if not m:
            continue
        folio, num, locus, body = m.groups()
        page = pages.get(folio) or Page(folio)
        lt_m = re.search(r"[PLCR]", locus)
        locus_type = lt_m.group(0) if lt_m else "?"
        para_start = "<%>" in body or locus[:1] in "@*"
        para_end = "<$>" in body or locus[:1] == "="
        body = re.sub(r"<![^>]*>", "", body)             # inline comments
        body = re.sub(r"<[%$~]>", "", body)               # paragraph markers
        body = re.sub(r"<(?!->)[^>]*>", "", body)           # other odd markup e.g. <h>
        body = body.replace("<->", "-")                     # drawing interruption acts as a space
        # split on separators, but not inside [..] or {..}; remember the separator kind
        parts, seps, cur, depth, pending = [], [], "", 0, ""
        for ch in body:
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            if depth == 0 and ch in ".,-":
                if cur:
                    parts.append(cur); seps.append(pending); cur, pending = "", ""
                pending += ch
                continue
            cur += ch
        if cur:
            parts.append(cur); seps.append(pending)
        seps = ["" if i == 0 else ("-" if "-" in sp else "." if "." in sp else ",") for i, sp in enumerate(seps)]
        n = len(parts)
        for i, (raw, sp) in enumerate(zip(parts, seps)):
            eva = _first_alternative(raw).replace("{", "").replace("}", "").replace("'", "")
            tokens.append(Token(
                folio=folio, leaf=page.leaf, bifolio_id=page.bifolio_id, quire=page.quire,
                illustration=page.illustration, currier=page.currier, hand=page.hand,
                line_no=int(num), locus=locus, locus_type=locus_type, mode=_mode(locus_type),
                para_start=para_start, para_end=para_end, idx=i, n_in_line=n, raw=raw, eva=eva,
                uncertain_glyph="?" in raw, alternative="[" in raw, ligature="{" in raw,
                rare_glyph="@" in raw, space_before=sp))
    return pages, tokens


def legacy064_tokens(lines: list[str] | None = None) -> list[dict]:
    """Bit-for-bit re-implementation of the Experiment 064 filter, for reproduction only.

    064 rules: mode is prose if 'P' in locus, label if 'L', circle if 'C';
    splits on [.,\\s]; keeps only words matching [a-z]{2,20} (drops single-glyph words,
    anything with ?, [a:b], {..}, @nnn;) but keeps their position in the line.
    """
    lines = read_docx_lines() if lines is None else lines
    word_re = re.compile(r"[a-z]{2,20}$")
    meta, out = {}, []
    for s in (l.strip() for l in lines):
        h = re.match(r"^<(f\d+[rv]\d*)>\s*<!([^>]+)>", s)
        if h:
            f, header = h.groups(); meta[f] = {}
            for tag, key in [("L", "lang"), ("I", "section"), ("H", "hand")]:
                v = re.search(r"\$" + tag + r"=([^\s$>]+)", header)
                meta[f][key] = v.group(1) if v else "?"
        a = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)", s)
        if not a:
            continue
        f, num, loc, body = a.groups()
        mode = "prose" if "P" in loc else ("label" if "L" in loc else ("circle" if "C" in loc else "other"))
        body = re.sub(r"<![^>]*>", " ", body)
        body = re.sub(r"<(?:%|\$|-)>", "", body)
        words = [w for w in re.split(r"[.,\s]+", body) if w]
        valid = [w if word_re.fullmatch(w) else None for w in words]
        m = meta.get(f, {"lang": "?", "section": "?", "hand": "?"})
        leaf = re.match(r"f(\d+)", f).group(1)
        for i, w in enumerate(valid):
            if w is None:
                continue
            prev = valid[i - 1] if i > 0 else None
            out.append(dict(word=w, folio=f, leaf=leaf, mode=mode, variety=m["lang"], section=m["section"],
                            hand=m["hand"], line=int(num), prev=prev if prev is not None else "^LINE",
                            prev_y=int(bool(prev) and prev.endswith("y")), start=int(i == 0),
                            end=int(i == len(valid) - 1)))
    return out


def token_dicts(tokens: list[Token]) -> list[dict]:
    return [asdict(t) | {"is_clean": t.is_clean} for t in tokens]
