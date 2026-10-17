"""Unit inventories for Voynich EVA text (and for any word stream): which strings count as one symbol?

Background: Rozanova & Temerev, "A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space: What the
Units of Voynichese Are Not", arXiv:2608.17096 (Aug 2026). They test whether EVA glyphs behave like plaintext
letters (conditional entropy, learned BPE scale, calibrated attack), whether ZL tokens behave like words (adjacent
token MI) and whether separators are uniform (certain '.' vs uncertain ','). This module provides the inventories
E012 compares; it makes no claim about which, if any, is "correct".

Inventories (each maps one EVA word -> list of unit strings; ``"".join(units) == word`` always holds):
  * ``raw``       -- one EVA character per unit ("decomposed" EVA in the paper's terms).
  * ``collapsed`` -- the paper's composite-collapsed representation: cth, ckh, cph, cfh, ch, sh, iin, in, ee are
                     single units (greedy longest match, so 'eee' -> 'ee'+'e', 'iiin' -> 'i'+'iin').
  * ``slot``      -- the Slot alphabet of M. Zattera, "A New Transliteration Alphabet Brings New Evidence of Word
                     Structure and Multiple 'Languages' in the Voynich Manuscript", Proc. Int. Conf. on the Voynich
                     Manuscript 2022, CEUR-WS Vol-3313 paper 10, Figure 3 (VERIFIED 2026-10-17 by reading the CEUR
                     PDF): 26 characters q s d o y l r t k p f ch sh cth ckh cph cfh e ee eee a i ii iii m n.
                     Glyphs outside it (g x v u j b z, stray c/h) are kept as single-glyph units. Greedy longest
                     match ('eeee' -> 'eee'+'e').
  * ``BPE``       -- byte-pair encoding (Sennrich et al. 2016) learned on a word list (merges never cross a
                     token boundary) or, with :func:`learn_bpe_lines`, on space-erased line strings (the paper's
                     separator-erasure test). Ties are broken deterministically (count, then pair lexicographically),
                     so learning is reproducible bit for bit. Vocabulary size V = base alphabet + merges.
  * ``letters`` / ``syllables`` for plaintext controls (syllables via the onset-maximal rule in
    :func:`vcl.synthetic.twins.syllabify`).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable

COMPOSITES = ["cth", "ckh", "cph", "cfh", "iin", "ch", "sh", "in", "ee"]
SLOT_ALPHABET = ["q", "s", "d", "o", "y", "l", "r", "t", "k", "p", "f", "ch", "sh", "cth", "ckh", "cph", "cfh",
                 "e", "ee", "eee", "a", "i", "ii", "iii", "m", "n"]
SLOT_SOURCE = ("Zattera 2022, CEUR-WS Vol-3313 paper 10, Fig. 3 'The Slot alphabet' (verified from the PDF, "
               "2026-10-17)")


def greedy_segment(word: str, inventory: Iterable[str]) -> list[str]:
    """Left-to-right longest-match segmentation; characters not starting any inventory unit become 1-char units."""
    inv = sorted(set(inventory), key=lambda u: (-len(u), u))
    out, i = [], 0
    while i < len(word):
        u = next((u for u in inv if word.startswith(u, i)), word[i])
        out.append(u); i += len(u)
    return out


def raw_units(word: str) -> list[str]:
    return list(word)


def collapsed_units(word: str) -> list[str]:
    return greedy_segment(word, COMPOSITES)


def slot_units(word: str) -> list[str]:
    return greedy_segment(word, SLOT_ALPHABET)


def syllable_units(word: str, max_onset: int = 2) -> list[str]:
    from vcl.synthetic.twins import syllabify
    return syllabify(word, max_onset)


FIXED = {"raw": raw_units, "collapsed": collapsed_units, "slot": slot_units}


# ------------------------------------------------------------------------------------------------------- BPE
@dataclass
class BPE:
    """Ordered merge list learned by :func:`learn_bpe`. ``apply`` reproduces the training segmentation for
    training words and segments unseen words with the same ordered rules (standard BPE encoding)."""
    base: str                                   # name of the base segmentation ('raw', 'collapsed', 'letters')
    merges: list[tuple[str, str]] = field(default_factory=list)
    alphabet: list[str] = field(default_factory=list)   # base units seen in training

    def truncated(self, n_merges: int) -> "BPE":
        return BPE(self.base, self.merges[:max(0, n_merges)], self.alphabet)

    def for_vocab(self, vocab: int) -> "BPE":
        """Merges so that len(alphabet) + merges == vocab (0 merges if the base alphabet is already larger)."""
        return self.truncated(vocab - len(self.alphabet))

    @property
    def vocab(self) -> list[str]:
        return self.alphabet + [a + b for a, b in self.merges]

    def apply_units(self, units: list[str]) -> list[str]:
        rank = {p: i for i, p in enumerate(self.merges)}
        s = list(units)
        while len(s) > 1:
            best, bi = None, -1
            for i in range(len(s) - 1):
                r = rank.get((s[i], s[i + 1]))
                if r is not None and (best is None or r < best):
                    best, bi = r, i
            if best is None:
                break
            a, b = self.merges[best]
            out, i = [], 0
            while i < len(s):
                if i < len(s) - 1 and s[i] == a and s[i + 1] == b:
                    out.append(a + b); i += 2
                else:
                    out.append(s[i]); i += 1
            s = out
        return s

    def apply(self, word: str, base_fn: Callable[[str], list[str]] | None = None) -> list[str]:
        base_fn = base_fn or BASES[self.base]
        return self.apply_units(base_fn(word))


def _letters(w: str) -> list[str]:
    return list(w)


BASES = {"raw": raw_units, "collapsed": collapsed_units, "slot": slot_units, "letters": _letters}


def _learn(seqs: list[list[str]], weights: list[int], n_merges: int, min_count: int = 2,
           checkpoints: Iterable[int] = (), on_checkpoint: Callable[[int, list[list[str]]], None] | None = None
           ) -> list[tuple[str, str]]:
    """Incremental BPE on weighted sequences. Mutates ``seqs`` into the final segmentation."""
    pc: Counter = Counter()
    where: dict[tuple[str, str], set[int]] = defaultdict(set)
    for i, s in enumerate(seqs):
        for p in zip(s, s[1:]):
            pc[p] += weights[i]; where[p].add(i)
    cps = set(checkpoints)
    merges: list[tuple[str, str]] = []
    if 0 in cps and on_checkpoint:
        on_checkpoint(0, seqs)
    for k in range(1, n_merges + 1):
        if not pc:
            break
        best = max(pc.items(), key=lambda kv: (kv[1], kv[0]))
        if best[1] < min_count:
            break
        (a, b) = pair = best[0]
        merges.append(pair)
        new = a + b
        for i in list(where.get(pair, ())):
            s, w = seqs[i], weights[i]
            for p in zip(s, s[1:]):
                pc[p] -= w
                if pc[p] <= 0:
                    del pc[p]
                where[p].discard(i)
            out, j = [], 0
            while j < len(s):
                if j < len(s) - 1 and s[j] == a and s[j + 1] == b:
                    out.append(new); j += 2
                else:
                    out.append(s[j]); j += 1
            seqs[i] = out
            for p in zip(out, out[1:]):
                pc[p] += w; where[p].add(i)
        where.pop(pair, None)
        if k in cps and on_checkpoint:
            on_checkpoint(k, seqs)
    return merges


def learn_bpe(words: Iterable[str], n_merges: int, base: str = "raw", min_count: int = 2,
              checkpoints: Iterable[int] = (), on_checkpoint=None) -> BPE:
    """Within-token BPE learned on a word list (token frequencies are weights; merges never cross tokens).
    ``on_checkpoint(k, {word: units})`` is called after k merges for k in ``checkpoints``."""
    wc = Counter(w for w in words if w)
    types = sorted(wc)
    seqs = [BASES[base](w) for w in types]
    alphabet = sorted({u for s in seqs for u in s})
    cb = None
    if on_checkpoint:
        def cb(k, ss):
            on_checkpoint(k, dict(zip(types, [list(s) for s in ss])))
    merges = _learn(seqs, [wc[t] for t in types], n_merges, min_count, checkpoints, cb)
    return BPE(base, merges, alphabet)


def learn_bpe_lines(lines: list[list[str]], n_merges: int, base: str = "raw", min_count: int = 2,
                    checkpoints: Iterable[int] = (), on_checkpoint=None) -> BPE:
    """Space-erased BPE: every line's words are concatenated (spaces deleted) and BPE is learned on the
    continuous line strings, so merges may cross the erased separators. ``on_checkpoint(k, segs)`` receives the
    unit segmentation of each line (list per line)."""
    seqs = [[u for w in l for u in BASES[base](w)] for l in lines]
    alphabet = sorted({u for s in seqs for u in s})
    cb = None
    if on_checkpoint:
        def cb(k, ss):
            on_checkpoint(k, [list(s) for s in ss])
    merges = _learn(seqs, [1] * len(seqs), n_merges, min_count, checkpoints, cb)
    return BPE(base, merges, alphabet)


def segment_lines_erased(bpe: BPE, lines: list[list[str]]) -> list[list[str]]:
    """Apply a space-erased BPE to lines (concatenated, no spaces) -> unit list per line."""
    return [bpe.apply_units([u for w in l for u in BASES[bpe.base](w)]) for l in lines]


def crossing_rates(line_units: list[list[str]], lines: list[list[str]], seps: list[list[str]] | None = None
                   ) -> dict[str, float]:
    """Share of hidden separator positions that fall INSIDE a learned unit (paper Table 8).
    ``seps[i][j]`` = separator class before word j of line i ('.', ',', ...); j=0 is ignored."""
    tot, crossed = Counter(), Counter()
    for li, (units, words) in enumerate(zip(line_units, lines)):
        bounds, pos = set(), 0
        for u in units:
            pos += len(u); bounds.add(pos)
        pos, glyph_total = 0, sum(len(w) for w in words)
        for j, w in enumerate(words):
            if j:
                cls = seps[li][j] if seps else "sep"
                tot[cls] += 1; tot["all_separators"] += 1
                if pos not in bounds:
                    crossed[cls] += 1; crossed["all_separators"] += 1
            pos += len(w)
        for p in range(1, glyph_total):
            tot["all_positions"] += 1
            crossed["all_positions"] += p not in bounds
    return {k: crossed[k] / tot[k] for k in tot if tot[k]} | {f"n_{k}": tot[k] for k in tot}
