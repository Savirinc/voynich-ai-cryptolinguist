"""Voynich twins: known-answer generators that turn real plaintext (or nothing) into Voynich-like EVA text.

Five mechanism families (E011). Families 1-3 encode plaintext and are exactly decodable from the key; families 4-5
are meaningless generators (decoy class, ``is_language=False``). All five emit EVA-character words assembled from
the same **glyph-chunk pools** (prefix / middle / suffix pieces of Voynich DEV words, see :func:`chunk_pools`), so
every family shares one glyph-shape prior and differs only in the *mechanism* that strings the chunks together.
That is deliberate: E011 asks which mechanisms can reproduce Voynich's statistics, not whether a generator can
invent EVA from scratch.

Literature sources (verification status as of 2026-10-17, WebSearch; see reports/VOYNICH_TWINS.md):

1. ``naibbe``: M. A. Greshko, "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich
   Manuscript-like ciphertext", Cryptologia (online 2025-11-26), doi:10.1080/01611194.2025.2566408.
   VERIFIED (title, author, DOI, high-level design). Design details verified only via secondary sources (press,
   the author's and critics' posts on voynich.ninja): plaintext is randomly *respaced* into unigrams and bigrams
   (~47:53); every token becomes one ciphertext word; a bigram word = prefix string (1st letter) + suffix string
   (2nd letter); 6 substitution tables chosen per letter with ratios 5:2:2:2:1:1 (playing cards / dice); no nulls;
   no line-level mechanism. The actual table contents were NOT available (paper paywalled) -> this is a clearly
   labelled APPROXIMATION ("Naibbe-style"): tables are drawn from the shared chunk pools, not Greshko's tables.
2. ``abbreviation``: medieval Latin abbreviation practice (suspension, contraction, prefix/suffix signs,
   brevigraphs for frequent words) as catalogued by A. Cappelli, *Lexicon abbreviaturarum* (1899; standard
   reference, not re-verified here). The *idea* of an abbreviation/shorthand reading of Voynichese is old
   (e.g. Newbold 1921, Feely 1943 -- UNVERIFIED citations, background only). Sign inventories here are
   data-driven (most frequent word endings/beginnings of the source text), an approximation of a real system.
3. ``syllabary``: plaintext syllabified (onset + vowel nucleus + coda split), frequent syllables -> glyph clusters,
   rare syllables spelled letter by letter. No single literature source; generic syllabary/abugida hypothesis.
4. ``rugg_grille``: G. Rugg, "An elegant hoax? A possible solution to the Voynich manuscript", Cryptologia 28(1),
   2004. VERIFIED via secondary sources (Wikipedia, press): a table of Voynich-like syllables (reported ~40 rows x
   ~39 columns, three-part prefix/mid/suffix words) read through a moving three-hole Cardan grille. Our table size,
   grille shapes and emptiness rates are search parameters (approximation).
5. ``self_citation``: T. Timm & A. Schinner, "A possible generating algorithm of the Voynich manuscript",
   Cryptologia (online 2019-05-25; print vol. 44, 2020). Title/authors/date VERIFIED via secondary sources
   (voynich.ninja, Schmeh); DOI 10.1080/01611194.2019.1596999 UNVERIFIED. Mechanism as described there: start from
   a few seed words and repeatedly copy earlier words (preferably from the previous line, near the same
   position) with small modifications (similar-glyph substitution, adding/removing prefixes, combining words).
   Our mutation rule set is an approximation of that description.

Line layout: families 1-4 produce a word stream that is wrapped into lines of a target glyph width (fixed per spec;
E011 uses Voynich DEV's mean line length). ``self_citation`` builds lines itself (its copying rule is line-aware).
No family has an explicit line-position mechanism (Naibbe's own paper reports lacking one), so line-position
effects (line-final m, y->q) are a held-out check in E011, never fitted.
"""
from __future__ import annotations

import math
import random
import re
from collections import Counter
from itertools import accumulate
from dataclasses import dataclass, field
from vcl.synthetic import naibbe_exact as _NX  # noqa: E402  faithful Naibbe port (published tables)

VOWELS = set("aeiouyàáâãäåæèéêëìíîïòóôõöøùúûüýÿœαεηιουωаеёиоуыэюяאוי")

# ---------------------------------------------------------------------------------------------------------------
# Glyph-chunk pools
# ---------------------------------------------------------------------------------------------------------------
_SPLIT = re.compile(r"^(q?[oy]?|[dslr]?)(.*?)((?:[ao]?i+[nrlm]|[ao]?[nrlm]|e*[dlrs]?y|[dlrs])?)$")


def split_word(w: str) -> tuple[str, str, str]:
    """Three-part (prefix, middle, suffix) split of an EVA word. Purely descriptive, deterministic."""
    m = _SPLIT.match(w)
    return m.group(1), m.group(2), m.group(3)


def chunk_pools(words, top_m: int = 400) -> dict[str, dict[str, int]]:
    """Frequency pools of prefix / middle / suffix chunks from a list of EVA word tokens (DEV leaves only)."""
    P, M, S = Counter(), Counter(), Counter()
    for w in words:
        p, m, s = split_word(w)
        P[p] += 1; M[m] += 1; S[s] += 1
    return {"P": dict(P.most_common()), "M": dict(M.most_common(top_m)), "S": dict(S.most_common())}


class ChunkSampler:
    """Samples Voynich-like glyph strings of a positional kind from chunk pools.

    tau: temperature on pool counts (weight = count**tau; small tau flattens, large tau favours frequent chunks).
    p_single: chance a middle chunk is replaced by one glyph drawn from the middle-glyph distribution.
    p_mid_final: chance a final/suffix unit carries a middle chunk before its suffix.
    """

    def __init__(self, pools, tau: float = 1.0, p_single: float = 0.2, p_mid_final: float = 0.3):
        self.p_single, self.p_mid_final = p_single, p_mid_final
        self.tab = {}
        for k in "PMS":
            items = [(c, n) for c, n in pools[k].items()]
            self.tab[k] = ([c for c, _ in items], list(accumulate(n ** tau for _, n in items)))
            nz = [(c, n) for c, n in items if c]
            self.tab[k + "+"] = ([c for c, _ in nz], list(accumulate(n ** tau for _, n in nz)))
        g = Counter()
        for c, n in pools["M"].items():
            for ch in c:
                g[ch] += n
        self.tab["g"] = (list(g), list(accumulate(n ** tau for n in g.values())))

    def _d(self, k, rng):
        c, w = self.tab[k]
        return rng.choices(c, cum_weights=w)[0]

    def mid(self, rng):
        return self._d("g", rng) if rng.random() < self.p_single else self._d("M+", rng)

    def sample(self, kind: str, rng: random.Random) -> str:
        if kind == "I":      # word-initial unit: optional prefix + middle
            return self._d("P", rng) + self.mid(rng)
        if kind == "M":
            return self.mid(rng)
        if kind == "F":      # word-final unit: (middle) + suffix
            return (self.mid(rng) if rng.random() < self.p_mid_final else "") + self._d("S+", rng)
        if kind == "W":      # whole word
            s = self._d("P", rng) + (self.mid(rng) if rng.random() < 0.85 else "") + self._d("S", rng)
            return s or self._d("S+", rng)
        if kind in "PS":
            return self._d(kind + "+", rng)
        raise ValueError(kind)


class PrefixFree:
    """Incrementally built prefix-free code set (no code is a proper prefix of another, no duplicates)."""

    def __init__(self):
        self.codes: set[str] = set()
        self.prefixes: set[str] = set()

    def ok(self, c: str) -> bool:
        if not c or c in self.codes or c in self.prefixes:
            return False
        return not any(c[:i] in self.codes for i in range(1, len(c)))

    def add(self, c: str):
        self.codes.add(c)
        for i in range(1, len(c)):
            self.prefixes.add(c[:i])


_FALLBACK = "okeydachitslrqpfnm"


def _draw(kind, sampler, rng, accept, economy: int, tries: int = 400) -> str:
    """Draw `economy` acceptable candidates and keep the shortest (economy>1 favours short codes)."""
    got = []
    for _ in range(tries):
        c = sampler.sample(kind, rng)
        if accept(c):
            got.append(c)
            if len(got) >= economy:
                break
    L = 1
    while not got:       # constraint exhausted the pool: extend samples with extra middle chunks
        for _ in range(200):
            c = sampler.sample(kind, rng)
            extra = "".join(sampler.mid(rng) for _ in range(L))
            c = extra + c if kind in "FS" else c + extra
            if accept(c):
                got.append(c); break
        L += 1
        if L > 6:        # last resort: random EVA strings
            for _ in range(10000):
                c = "".join(rng.choice(_FALLBACK) for _ in range(L))
                if accept(c):
                    got.append(c); break
    return min(got, key=len)


def _code_table(symbols, kind, sampler, rng, pf: PrefixFree | None, n_hom: int, economy: int,
                taken: dict | None = None):
    """symbol -> list of n_hom distinct codes. With pf, codes are prefix-free jointly with pf; with `taken`
    (code -> symbol), codes stay unique across symbols (a code may never decode to two symbols)."""
    out = {}
    for s in symbols:
        codes = []
        for _ in range(n_hom):
            def accept(c):
                if c in codes:
                    return False
                if pf is not None and not pf.ok(c):
                    return False
                return taken is None or c not in taken
            c = _draw(kind, sampler, rng, accept, economy)
            codes.append(c)
            if pf is not None:
                pf.add(c)
            if taken is not None:
                taken[c] = s
        out[s] = codes
    return out


def _hom_weights(n, skew):
    return [1.0 / (h + 1) ** skew for h in range(n)]


def wrap_lines(words: list[str], rng: random.Random, width_mean: float = 49.7, width_sd: float = 9.0):
    """Wrap a word stream into lines of target glyph width (incl. spaces), one jittered width per line."""
    lines, cur, w, target = [], [], 0, max(8, rng.gauss(width_mean, width_sd))
    for x in words:
        add = len(x) + (1 if cur else 0)
        if cur and w + add > target:
            lines.append(cur); cur, w, target = [], 0, max(8, rng.gauss(width_mean, width_sd))
            add = len(x)
        cur.append(x); w += add
    if cur:
        lines.append(cur)
    return lines


def _alphabet(plain: str) -> list[str]:
    cnt = Counter(c for c in plain if c != " ")
    return [c for c, _ in sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))]


# ---------------------------------------------------------------------------------------------------------------
# Family 1: Naibbe-style verbose homophonic table cipher (APPROXIMATION of Greshko 2025)
# ---------------------------------------------------------------------------------------------------------------
NAIBBE_RATIOS = [5, 2, 2, 2, 1, 1]


def naibbe_key(params: dict, seed: int, plain: str, pools) -> dict:
    p = {**NAIBBE_DEFAULTS, **params}
    rng = random.Random(seed)
    smp = ChunkSampler(pools, p["tau"], p["p_single"], p["p_mid_final"])
    alpha = _alphabet(plain)
    T = int(p["n_tables"])
    pf = PrefixFree()
    Ptab, Stab, Utab = [], [], []
    s_taken: dict[str, str] = {}
    u_taken: dict[str, str] = {}
    shared = set()
    for t in range(T):
        if t and rng.random() < p["share"]:            # table repeats table 0 for this whole table (less homophony)
            Ptab.append(dict(Ptab[0])); Stab.append(dict(Stab[0])); shared.add(t); continue
        Ptab.append({c: v[0] for c, v in _code_table(alpha, "I", smp, rng, pf, 1, int(p["economy"])).items()})
        Stab.append({c: v[0] for c, v in _code_table(alpha, "F", smp, rng, None, 1, int(p["economy"]),
                                                     taken=s_taken).items()})
    pcodes = {c: s for tab in Ptab for s, c in tab.items()}

    def parses_as_bigram(w):
        for i in range(1, len(w)):
            if w[:i] in pcodes and w[i:] in s_taken:
                return True
        return False
    for t in range(T):
        if t in shared:
            Utab.append(dict(Utab[0])); continue
        Utab.append({})
        for c in alpha:
            Utab[t][c] = _draw("W", smp, rng, lambda w: w not in u_taken and not parses_as_bigram(w)
                               and w not in pcodes, int(p["economy"]))
            u_taken[Utab[t][c]] = c
    w = [r ** p["table_skew"] for r in NAIBBE_RATIOS[:T]]
    return {"family": "naibbe", "params": p, "seed": seed, "alphabet": alpha, "P": Ptab, "S": Stab, "U": Utab,
            "table_weights": w}


def naibbe_encode(plain: str, key: dict, seed: int) -> list[str]:
    rng = random.Random(seed)
    letters = [c for c in plain if c != " " and c in key["U"][0]]
    T = len(key["table_weights"])
    pick = lambda: rng.choices(range(T), weights=key["table_weights"])[0]
    out, i, pb = [], 0, key["params"]["p_bigram"]
    while i < len(letters):
        if i + 1 < len(letters) and rng.random() < pb:
            out.append(key["P"][pick()][letters[i]] + key["S"][pick()][letters[i + 1]]); i += 2
        else:
            out.append(key["U"][pick()][letters[i]]); i += 1
    return out


def naibbe_decode(words: list[str], key: dict) -> str:
    U = {c: s for tab in key["U"] for s, c in tab.items()}
    P = {c: s for tab in key["P"] for s, c in tab.items()}
    S = {c: s for tab in key["S"] for s, c in tab.items()}
    out = []
    for w in words:
        if w in U:
            out.append(U[w]); continue
        for i in range(1, len(w)):
            if w[:i] in P:
                out.append(P[w[:i]] + S[w[i:]]); break
        else:
            raise ValueError(f"undecodable word {w!r}")
    return "".join(out)


NAIBBE_DEFAULTS = dict(p_bigram=0.528, n_tables=6, table_skew=1.0, share=0.0, tau=1.0, p_single=0.2,
                       p_mid_final=0.3, economy=1)
NAIBBE_BOUNDS = dict(p_bigram=(0.2, 0.8), n_tables=(1, 6), table_skew=(0.0, 2.0), share=(0.0, 0.8),
                     tau=(0.2, 1.5), p_single=(0.0, 0.8), p_mid_final=(0.0, 0.9), economy=(1, 6))


# ---------------------------------------------------------------------------------------------------------------
# Shared positional prefix-free unit code (families 2 and 3)
# ---------------------------------------------------------------------------------------------------------------
def _unit_code(units, smp, rng, n_hom, economy, positional: bool):
    """Initial table I (prefix-free) and non-initial tables M, F (jointly prefix-free). A word of units
    u1..uk is I[u1] M[u2] ... M[u_{k-1}] F[uk]; a one-unit word is I[u1]. Always uniquely parseable.
    positional=False: M and F tables are the same draw (kind 'M' for both) -> weaker positional allography."""
    pfI, pfMF = PrefixFree(), PrefixFree()
    I = _code_table(units, "I", smp, rng, pfI, n_hom, economy)
    M = _code_table(units, "M", smp, rng, pfMF, n_hom, economy)
    F = _code_table(units, "F", smp, rng, pfMF, n_hom, economy) if positional else None
    return {"I": I, "M": M, "F": F}


def _emit_units(us, code, rng, hw):
    if not us:
        return ""
    F = code["F"] or code["M"]
    s = rng.choices(code["I"][us[0]], weights=hw)[0]
    for j, u in enumerate(us[1:], 1):
        tab = F if j == len(us) - 1 else code["M"]
        s += rng.choices(tab[u], weights=hw)[0]
    return s


def _parse_units(w, code):
    I = {c: u for u, cs in code["I"].items() for c in cs}
    Mi = {c: ("M", u) for u, cs in code["M"].items() for c in cs}
    if code["F"]:
        Mi.update({c: ("F", u) for u, cs in code["F"].items() for c in cs})
    for i in range(1, len(w) + 1):
        if w[:i] in I:
            us, rest = [I[w[:i]]], w[i:]
            break
    else:
        raise ValueError(f"no initial code in {w!r}")
    while rest:
        for i in range(1, len(rest) + 1):
            if rest[:i] in Mi:
                kind, u = Mi[rest[:i]]; us.append(u); rest = rest[i:]
                if code["F"] and kind == "F" and rest:
                    raise ValueError(f"final code before end in {w!r}")
                break
        else:
            raise ValueError(f"unparseable remainder {rest!r} in {w!r}")
    return us


# ---------------------------------------------------------------------------------------------------------------
# Family 2: abbreviation / shorthand system, then positional glyph mapping
# ---------------------------------------------------------------------------------------------------------------
SUSP, CONTR = "<~>", "<^>"


def _affix_signs(words: Counter, n: int, end: bool):
    sc = Counter()
    for w, c in words.items():
        for L in (2, 3, 4):
            if len(w) > L + 1:
                sc[w[-L:] if end else w[:L]] += c * (L - 1)
    out = []
    for a, _ in sc.most_common():
        if len(out) >= n:
            break
        if not any(a.endswith(b) or b.endswith(a) for b in out) if end else \
           not any(a.startswith(b) or b.startswith(a) for b in out):
            out.append(a)
    return out


def abbreviation_key(params: dict, seed: int, plain: str, pools) -> dict:
    p = {**ABBREV_DEFAULTS, **params}
    rng = random.Random(seed)
    words = Counter(w for w in plain.split(" ") if w)
    suf = _affix_signs(words, int(p["n_suffix_signs"]), True)
    pre = _affix_signs(words, int(p["n_prefix_signs"]), False)
    wsig = [w for w, _ in words.most_common() if len(w) >= 2][: int(p["n_word_signs"])]
    units = _alphabet(plain) + [f"<-{s}>" for s in suf] + [f"<{s}->" for s in pre] + [f"<{w}>" for w in wsig] \
        + [SUSP, CONTR]
    smp = ChunkSampler(pools, p["tau"], p["p_single"], p["p_mid_final"])
    code = _unit_code(units, smp, rng, int(p["n_hom"]), int(p["economy"]), bool(round(p["positional"])))
    key = {"family": "abbreviation", "params": p, "seed": seed, "suffix_signs": suf, "prefix_signs": pre,
           "word_signs": wsig, "units": units, "code": code}
    # expansion lexicon: most frequent full word per abbreviated form (built on the key's own text sample)
    exp = {}
    r2 = random.Random(seed + 1)
    for w, c in words.items():
        a = "".join(_abbrev_word(w, key, r2))
        exp.setdefault(a, Counter())[w] += c
    key["expand"] = {a: c.most_common(1)[0][0] for a, c in exp.items()}
    return key


def _abbrev_word(w: str, key: dict, rng) -> list[str]:
    p = key["params"]
    if w in key["word_signs"]:
        return [f"<{w}>"]
    head, body, tail = [], w, []
    for s in key["prefix_signs"]:
        if body.startswith(s) and len(body) > len(s) + 1:
            head, body = [f"<{s}->"], body[len(s):]; break
    for s in key["suffix_signs"]:
        if body.endswith(s) and len(body) > len(s):
            tail, body = [f"<-{s}>"], body[:-len(s)]; break
    us = head + list(body) + tail
    n_letters = len(w)
    r = rng.random()
    if n_letters >= p["susp_min_len"] and r < p["p_suspend"]:
        return us[: int(p["susp_keep"])] + [SUSP]
    if len(us) >= 4 and r < p["p_suspend"] + p["p_contract"]:
        mid = [u for u in us[1:-1] if not (len(u) == 1 and u in VOWELS)]
        return [us[0]] + mid + [us[-1], CONTR]
    return us


def abbreviate(plain: str, key: dict, seed: int) -> list[list[str]]:
    """The abbreviated unit sequence per word (what the glyph layer actually encodes)."""
    rng = random.Random(seed)
    return [_abbrev_word(w, key, rng) for w in plain.split(" ") if w]


def abbreviation_encode(plain: str, key: dict, seed: int) -> list[str]:
    units = abbreviate(plain, key, seed)
    rng = random.Random(seed ^ 0x5EED)
    hw = _hom_weights(int(key["params"]["n_hom"]), key["params"]["hom_skew"])
    return [_emit_units(us, key["code"], rng, hw) for us in units]


def abbreviation_decode(words: list[str], key: dict, expand: bool = False) -> str:
    """Exact inverse of the glyph layer -> abbreviated text ('<~>' suspension, '<^>' contraction, '<-us>' signs).
    With expand=True each abbreviated form is replaced by its most frequent expansion (lossy by nature)."""
    out = []
    for w in words:
        a = "".join(_parse_units(w, key["code"]))
        out.append(key["expand"].get(a, _naive_expand(a)) if expand else a)
    return " ".join(out)


def _naive_expand(a: str) -> str:
    return re.sub(r"<(-?)([^<>~^]*?)(-?)>", lambda m: m.group(2), a).replace(SUSP, "").replace(CONTR, "")


ABBREV_DEFAULTS = dict(n_suffix_signs=8, n_prefix_signs=3, n_word_signs=10, p_suspend=0.1, susp_min_len=6,
                       susp_keep=3, p_contract=0.1, tau=1.0, p_single=0.3, p_mid_final=0.2, economy=2, n_hom=1,
                       hom_skew=1.0, positional=1)
ABBREV_BOUNDS = dict(n_suffix_signs=(0, 16), n_prefix_signs=(0, 8), n_word_signs=(0, 30), p_suspend=(0.0, 0.5),
                     susp_min_len=(4, 9), susp_keep=(1, 4), p_contract=(0.0, 0.5), tau=(0.2, 1.5),
                     p_single=(0.0, 0.9), p_mid_final=(0.0, 0.9), economy=(1, 6), n_hom=(1, 3),
                     hom_skew=(0.0, 2.0), positional=(0, 1))


# ---------------------------------------------------------------------------------------------------------------
# Family 3: syllabary / abugida
# ---------------------------------------------------------------------------------------------------------------
def syllabify(w: str, max_onset: int = 2) -> list[str]:
    """Onset-maximal syllabification on orthographic vowels: consonant clusters between nuclei give their last
    `max_onset` consonants to the next syllable's onset, the rest to the previous coda."""
    if not w:
        return []
    isv = [c in VOWELS for c in w]
    nuclei, i = [], 0
    while i < len(w):
        if isv[i]:
            j = i
            while j + 1 < len(w) and isv[j + 1] and j + 1 - i < 2:
                j += 1
            nuclei.append((i, j)); i = j + 1
        else:
            i += 1
    if not nuclei:
        return [w]
    cuts = []
    for (a, b), (c, d) in zip(nuclei, nuclei[1:]):
        gap = c - b - 1
        cuts.append(b + 1 + max(0, gap - max_onset) if gap > 0 else c)
    out, s = [], 0
    for c in cuts:
        out.append(w[s:c]); s = c
    out.append(w[s:])
    return [x for x in out if x]


def syllabary_key(params: dict, seed: int, plain: str, pools) -> dict:
    p = {**SYLL_DEFAULTS, **params}
    rng = random.Random(seed)
    sy = Counter()
    for w in plain.split(" "):
        sy.update(syllabify(w, int(p["max_onset"])))
    inv = [s for s, _ in sy.most_common() if len(s) > 1][: int(p["n_syll"])]
    units = inv + [c for c in _alphabet(plain) if c not in inv]
    smp = ChunkSampler(pools, p["tau"], p["p_single"], p["p_mid_final"])
    code = _unit_code(units, smp, rng, int(p["n_hom"]), int(p["economy"]), bool(round(p["positional"])))
    return {"family": "syllabary", "params": p, "seed": seed, "units": units, "inventory": inv, "code": code}


def syllable_units(w: str, key: dict) -> list[str]:
    inv = set(key["inventory"])
    out = []
    for s in syllabify(w, int(key["params"]["max_onset"])):
        out += [s] if s in inv else list(s)
    return out


def _syll_groups(plain: str, key: dict):
    k = int(key["params"]["units_per_word"])
    for w in plain.split(" "):
        if not w:
            continue
        us = syllable_units(w, key)
        if k <= 0:
            yield us
        else:                               # plaintext word split into ciphertext words of <= k units
            for i in range(0, len(us), k):
                yield us[i:i + k]


def syllabary_encode(plain: str, key: dict, seed: int) -> list[str]:
    rng = random.Random(seed)
    hw = _hom_weights(int(key["params"]["n_hom"]), key["params"]["hom_skew"])
    return [_emit_units(us, key["code"], rng, hw) for us in _syll_groups(plain, key)]


def syllabary_decode(words: list[str], key: dict) -> str:
    """Exact inverse. With units_per_word > 0 the plaintext word spaces are not encoded (letters only)."""
    sep = " " if int(key["params"]["units_per_word"]) <= 0 else ""
    return sep.join("".join(_parse_units(w, key["code"])) for w in words)


SYLL_DEFAULTS = dict(n_syll=120, max_onset=2, units_per_word=0, tau=1.0, p_single=0.3, p_mid_final=0.2, economy=2, n_hom=1,
                     hom_skew=1.0, positional=1)
SYLL_BOUNDS = dict(n_syll=(10, 300), max_onset=(1, 3), units_per_word=(0, 4), tau=(0.2, 1.5), p_single=(0.0, 0.9),
                   p_mid_final=(0.0, 0.9), economy=(1, 6), n_hom=(1, 3), hom_skew=(0.0, 2.0), positional=(0, 1))


# ---------------------------------------------------------------------------------------------------------------
# Family 4: Rugg (2004) table and grille -- meaningless
# ---------------------------------------------------------------------------------------------------------------
def rugg_generate(n_words: int, params: dict, seed: int, pools) -> tuple[list[str], dict]:
    p = {**RUGG_DEFAULTS, **params}
    rng = random.Random(seed)
    smp = ChunkSampler(pools, p["tau"], p["p_single"], 0.0)
    R, C = int(p["rows"]), int(p["triples"])
    pe = [p["p_empty_P"], p["p_empty_M"], p["p_empty_S"]]
    kinds = ["P", "M", "S"]

    def cell(k):
        if rng.random() < pe[k]:
            return ""
        return smp.mid(rng) if k == 1 else smp.sample(kinds[k], rng)
    table = [[cell(j % 3) for j in range(3 * C)] for _ in range(R)]
    mo = int(p["max_row_offset"])
    grilles = [(0, rng.randint(0, mo), rng.randint(0, mo)) for _ in range(int(p["n_grilles"]))]
    out, gi, r, c, run = [], 0, rng.randrange(R), rng.randrange(C), 0
    while len(out) < n_words:
        g = grilles[gi]
        w = "".join(table[(r + g[k]) % R][3 * c + k] for k in range(3))
        if w:
            out.append(w)
        c += 1
        if c == C:
            c, r = 0, (r + 1) % R
        run += 1
        if run >= p["grille_run"]:
            run, gi = 0, (gi + 1) % len(grilles)
    return out, {"table": table, "grilles": grilles}


RUGG_DEFAULTS = dict(rows=40, triples=13, p_empty_P=0.6, p_empty_M=0.12, p_empty_S=0.05, tau=1.0, p_single=0.2,
                     n_grilles=3, max_row_offset=3, grille_run=40)
RUGG_BOUNDS = dict(rows=(8, 80), triples=(3, 25), p_empty_P=(0.0, 0.95), p_empty_M=(0.0, 0.7),
                   p_empty_S=(0.0, 0.7), tau=(0.2, 1.5), p_single=(0.0, 0.8), n_grilles=(1, 6),
                   max_row_offset=(0, 8), grille_run=(5, 400))


# ---------------------------------------------------------------------------------------------------------------
# Family 5: Timm & Schinner (2019/2020) self-citation -- meaningless
# ---------------------------------------------------------------------------------------------------------------
_SIMILAR = [["o", "a", "y"], ["k", "t"], ["p", "f"], ["ch", "sh"], ["d", "l", "r", "s"], ["n", "r", "l", "m"],
            ["e", "ee"], ["i", "ii"]]
_PREFIXES = ["q", "o", "qo", "y", "ch", "d", "s"]


def _mutate(w: str, rng: random.Random, smp: ChunkSampler, pool_words) -> str:
    op = rng.random()
    if op < 0.55:                              # similar-glyph substitution
        grp = rng.choice(_SIMILAR)
        pos = [(m.start(), g) for g in grp for m in re.finditer(re.escape(g), w)]
        if pos:
            i, g = rng.choice(pos)
            alt = rng.choice([x for x in grp if x != g])
            return w[:i] + alt + w[i + len(g):]
        return w
    if op < 0.75:                              # add or remove a prefix
        for pre in sorted(_PREFIXES, key=len, reverse=True):
            if w.startswith(pre) and len(w) > len(pre) + 1 and rng.random() < 0.5:
                return w[len(pre):]
        return rng.choice(_PREFIXES) + w
    if op < 0.9:                               # combine: head of this word + tail of another earlier word
        other = rng.choice(pool_words)
        a, b = split_word(w), split_word(other)
        return (a[0] + a[1] + b[2]) or w
    p_, m_, s_ = split_word(w)                 # replace the suffix
    return p_ + m_ + smp.sample("S", rng)


def self_citation_generate(n_words: int, params: dict, seed: int, pools, width_mean: float = 49.7,
                           width_sd: float = 9.0) -> tuple[list[list[str]], dict]:
    p = {**SELF_DEFAULTS, **params}
    rng = random.Random(seed)
    smp = ChunkSampler(pools, p["tau"], p["p_single"], p["p_mid_final"])
    seeds = [smp.sample("W", rng) for _ in range(int(p["n_seed_words"]))]
    lines, cur, prev, recent, n, width = [], [], [], list(seeds), 0, max(8, rng.gauss(width_mean, width_sd))
    W = int(p["window"])
    while n < n_words:
        r = rng.random()
        if r < p["p_fresh"]:
            src = smp.sample("W", rng)
        elif prev and r < p["p_fresh"] + p["p_prev_line"]:
            j = min(len(prev) - 1, max(0, len(cur) + rng.choice([-1, 0, 0, 1])))
            src = prev[j]
        else:
            src = rng.choice(recent[-W:])
        w = src
        if rng.random() < p["p_mutate"]:
            k = 1 + (int(rng.expovariate(1 / p["extra_mutations"])) if p["extra_mutations"] > 0 else 0)
            for _ in range(min(k, 6)):
                w = _mutate(w, rng, smp, recent[-W:])
        w = w or src
        add = len(w) + (1 if cur else 0)
        if cur and sum(len(x) for x in cur) + len(cur) - 1 + add > width:
            lines.append(cur); prev, cur = cur, []
            width = max(8, rng.gauss(width_mean, width_sd))
        cur.append(w); recent.append(w); n += 1
        if len(recent) > 4 * W:
            recent = recent[-2 * W:]
    if cur:
        lines.append(cur)
    return lines, {"seed_words": seeds}


SELF_DEFAULTS = dict(n_seed_words=12, p_prev_line=0.5, window=30, p_mutate=0.7, extra_mutations=0.5, p_fresh=0.02,
                     tau=1.0, p_single=0.2, p_mid_final=0.3)
SELF_BOUNDS = dict(n_seed_words=(3, 60), p_prev_line=(0.0, 0.95), window=(3, 120), p_mutate=(0.2, 1.0),
                   extra_mutations=(0.0, 3.0), p_fresh=(0.0, 0.2), tau=(0.2, 1.5), p_single=(0.0, 0.8),
                   p_mid_final=(0.0, 0.9))


# ---------------------------------------------------------------------------------------------------------------
# Registry and a single generation entry point
# ---------------------------------------------------------------------------------------------------------------
@dataclass
class Family:
    name: str
    is_language: bool
    citation: str
    citation_status: str
    defaults: dict
    bounds: dict
    key_fn: object = None
    encode_fn: object = None
    decode_fn: object = None
    letters_per_glyph: float = 0.5     # rough plaintext chars needed per output glyph (for sizing samples)
    notes: str = ""


FAMILIES = {
    "naibbe": Family("naibbe", True, "Greshko, Cryptologia 2025, doi:10.1080/01611194.2025.2566408",
                     "VERIFIED (paper exists; design via secondary sources); tables APPROXIMATED",
                     NAIBBE_DEFAULTS, NAIBBE_BOUNDS, naibbe_key, naibbe_encode, naibbe_decode, 0.45,
                     "spaces of the plaintext are dropped (respacing); decode returns letters only"),
    "naibbe_exact": Family("naibbe_exact", True, "Greshko, Cryptologia 2025, doi:10.1080/01611194.2025.2566408",
                           "VERIFIED: author's published tables + reference code (github greshko/naibbe-cipher "
                           "@ f2675ec), faithful port; see vcl.synthetic.naibbe_exact",
                           _NX.DEFAULTS, _NX.BOUNDS, _NX.key, _NX.encode, _NX.decode, 0.45,
                           "no free parameters; Latin/Italian alphabet (w->uu, j->i, k->c, diacritics stripped)"),
    "abbreviation": Family("abbreviation", True, "Cappelli, Lexicon abbreviaturarum 1899 (practice); data-driven signs",
                           "background reference, not re-verified; sign inventory is an approximation",
                           ABBREV_DEFAULTS, ABBREV_BOUNDS, abbreviation_key, abbreviation_encode,
                           abbreviation_decode, 1.1, "decode is exact to the abbreviated text; expansion is lossy"),
    "syllabary": Family("syllabary", True, "generic syllabary/abugida hypothesis (no single source)", "n/a",
                        SYLL_DEFAULTS, SYLL_BOUNDS, syllabary_key, syllabary_encode, syllabary_decode, 1.0),
    "rugg_grille": Family("rugg_grille", False, "Rugg, Cryptologia 28(1) 2004, 'An elegant hoax?'",
                          "VERIFIED via secondary sources; table/grille sizes are parameters",
                          RUGG_DEFAULTS, RUGG_BOUNDS),
    "self_citation": Family("self_citation", False, "Timm & Schinner, Cryptologia 2019/2020",
                            "title/authors/date VERIFIED via secondary sources; DOI unverified; rules approximated",
                            SELF_DEFAULTS, SELF_BOUNDS),
}


def generate(family: str, params: dict, seed: int, pools, n_words: int, plain: str | None = None,
             width_mean: float = 49.7, width_sd: float = 9.0) -> dict:
    """Generate one Voynich twin sample. Returns {'lines', 'is_language', 'key', 'plaintext'}.

    Language families need `plain` (normalised corpus text, long enough); the key is built from `plain` itself
    (alphabet, sign/syllable inventories), so the sample is fully reproducible from (family, params, seed, plain)."""
    fam = FAMILIES[family]
    rng = random.Random(seed ^ 0xA11CE)
    if fam.is_language:
        if plain is None:
            raise ValueError("language family needs plaintext")
        key = fam.key_fn(params, seed, plain, pools)
        words = fam.encode_fn(plain, key, seed + 1)[:n_words]
        return {"lines": wrap_lines(words, rng, width_mean, width_sd), "is_language": True, "key": key,
                "plaintext": plain}
    if family == "rugg_grille":
        words, key = rugg_generate(n_words, params, seed, pools)
        return {"lines": wrap_lines(words, rng, width_mean, width_sd), "is_language": False, "key": key,
                "plaintext": None}
    lines, key = self_citation_generate(n_words, params, seed, pools, width_mean, width_sd)
    return {"lines": lines, "is_language": False, "key": key, "plaintext": None}


def clip_params(family: str, params: dict) -> dict:
    """Clip to bounds; integer-valued bounds give integer parameters."""
    b = FAMILIES[family].bounds
    out = {}
    for k, (lo, hi) in b.items():
        v = params.get(k, FAMILIES[family].defaults[k])
        v = min(hi, max(lo, v))
        out[k] = int(round(v)) if isinstance(lo, int) and isinstance(hi, int) else float(v)
    return out


def random_params(family: str, rng: random.Random) -> dict:
    b = FAMILIES[family].bounds
    return clip_params(family, {k: (rng.randint(lo, hi) if isinstance(lo, int) and isinstance(hi, int)
                                    else rng.uniform(lo, hi)) for k, (lo, hi) in b.items()})


def perturb_params(family: str, params: dict, rng: random.Random, scale: float = 0.15, n_changes: int = 2) -> dict:
    b = FAMILIES[family].bounds
    q = dict(params)
    for k in rng.sample(list(b), min(n_changes, len(b))):
        lo, hi = b[k]
        if isinstance(lo, int) and isinstance(hi, int):
            step = max(1, int(round((hi - lo) * scale)))
            q[k] = q[k] + rng.randint(-step, step)
        else:
            q[k] = q[k] + rng.gauss(0, (hi - lo) * scale)
    return clip_params(family, q)
