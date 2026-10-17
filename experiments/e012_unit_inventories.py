"""E012: unit inventories -- does any principled choice of Voynich units make the text look like an ordinary
alphabetic or syllabic encoding of a language, and does solver v2 crack it at that scale? (STRUCTURAL + calibrated
solver test; NO decipherment, no interpretation of Voynich words.)

Prior work replicated / extended: Rozanova & Temerev, arXiv:2608.17096 (Aug 2026), "A Glyph Is Not a Letter, a Token
Is Not a Word, a Space Is Not a Space". Their claims re-measured here on OUR DEV data (eval/PROTOCOL_v1.md: DEV
leaves only; LOCKED_TEST leaves never read): composite-collapsed h_cond ~2.7, adjacent-token MI share <1%, edge-glyph
MI ~0.2 bits, hapax-type share ~70%, separator internality (uncertain ',' vs certain '.'), BPE dependence trough and
its quire stability, space-erased BPE crossing rates.

Stages
  stats  : replication; inventories (raw, collapsed, Zattera slot, BPE V=40/80/150/300, space-erased BPE V=80)
           on Voynich DEV, on 32 corpus languages (letters, syllables, same BPE procedure) and on twin families
           (naibbe_exact + E011 twins) re-tokenised with the same procedure; language-cloud placement; edge coupling.
  solver : solver v2 (v1 + self-null abstention, margin from E005) on windows of 250 tokens per inventory for
           Voynich DEV and calibration conditions (known-answer substitution ciphers of real languages matched in
           symbol count and unit-type count; syllable-substitution ciphers; naibbe_exact; Rugg / self-citation twins;
           order-3 Markov surrogates of the Voynich unit stream). Voynich decodes are NEVER stored or printed.

Run: caffeinate -ims .venv/bin/python experiments/e012_unit_inventories.py --stage all [--workers 3] [--smoke]
"""
from __future__ import annotations

import argparse, json, math, random, sys, time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vcl.corpus import units as U  # noqa: E402
from vcl.corpus.ivtff import parse  # noqa: E402
from vcl.corpus.splits import locked_test_leaves  # noqa: E402
from vcl.synthetic.corpora import load_books  # noqa: E402
from vcl.synthetic import twins as T  # noqa: E402
from vcl.synthetic import naibbe_exact as NX  # noqa: E402

SEED = 12012
OUT = ROOT / "experiments/results/e012.json"
STATS_OUT = ROOT / "experiments/results/e012_stats.json"
SOLVER_ROWS = ROOT / "experiments/results/e012_solver_rows.jsonl"
VOCABS = [40, 80, 150, 300]
ERASED_V = 80
DK = [0, 4, 8, 16, 32, 64, 128, 256, 512]
SELFNULL_MARGIN = None   # read from experiments/results/e005.json
WIN_TOKENS = 250
LONG_WIN_TOKENS = 750      # extra, longer windows for the large inventories (more text per unit type)
LONG_INVS = ["bpe80", "bpe150", "bpe300"]
PAPER = {"h1_collapsed": 3.98, "hcond_collapsed": 2.69, "h1_raw": 3.89, "hcond_raw": 2.32,
         "hcond_within_token_collapsed": 2.43, "hcond_controls": [3.45, 3.52],
         "token_mi_bits": 0.0661, "token_mi_share": 0.0079, "token_mi_share_merged": 0.0054,
         "token_mi_share_controls": [0.0202, 0.0972],
         "edge_mi_bits": 0.197, "edge_mi_share": 0.057, "edge_mi_bits_controls": [0.018, 0.120],
         "hapax_share": 0.697, "hapax_share_merged": 0.730, "hapax_controls": [0.468, 0.677], "edit1_ratio": 1.12,
         "internality_uncertain": 0.494, "internality_certain": 0.029, "internality_linebreak": -0.036,
         "D0": 1.595, "D64": 1.045, "bpe_min_k": 64, "crossfit_min_k": 32, "half_overlap_k64": 0.839,
         "erased_crossing_certain": 0.025, "erased_crossing_uncertain": 0.203, "erased_crossing_all": 0.600,
         "erased_crossing_latin": 0.155,
         "naibbe_edge_bits": [0.006, 0.009], "naibbe_hapax": 0.41, "naibbe_hcond": 2.71}


# ================================================================================================ data
def voynich_dev_lines():
    """DEV prose lines in manuscript order: dicts with tokens (EVA or None if not clean), separators, metadata."""
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    L = defaultdict(list)
    for t in toks:
        if t.mode == "prose" and t.leaf not in locked:
            L[(t.folio, t.line_no)].append(t)
    order = sorted(L, key=lambda k: (int("".join(c for c in k[0] if c.isdigit()) or 0), k))
    lines = []
    for k in order:
        ts = L[k]
        lines.append({"folio": k[0], "line": k[1], "quire": ts[0].quire, "currier": ts[0].currier,
                      "leaf": ts[0].leaf, "para_start": ts[0].para_start,
                      "tokens": [t.eva if t.is_clean else None for t in ts], "seps": [t.space_before for t in ts]})
    assert not ({l["leaf"] for l in lines} & locked)
    return lines, sorted(locked, key=lambda x: (len(x), x))


def merge_uncertain(lines):
    """Paper's 'weak spaces merged': join tokens across every ',' separator (only when both sides are clean)."""
    out = []
    for l in lines:
        toks, seps = [], []
        for w, s in zip(l["tokens"], l["seps"]):
            if s == "," and toks and toks[-1] is not None and w is not None:
                toks[-1] = toks[-1] + w
            else:
                toks.append(w); seps.append(s)
        out.append({**l, "tokens": toks, "seps": seps})
    return out


def language_samples(n_tokens, template):
    """One contiguous sample of n_tokens words per language from tune+ref books (never role=test), wrapped into
    lines with the Voynich DEV tokens-per-line template. Languages with too little non-test text are skipped."""
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    by = defaultdict(list)
    for b in load_books():
        r = roles.get(b["id"], {}).get("role")
        if r in ("tune", "ref"):
            by[b["lang"]].append((0 if r == "tune" else 1, b["id"], b["text"]))
    out, skipped = {}, {}
    for lang in sorted(by):
        words = []
        for _, _, txt in sorted(by[lang]):
            words += txt[2000:].split(" ")[1:-1]
        words = [w for w in words if w]
        if len(words) < n_tokens:
            skipped[lang] = len(words); continue
        words = words[:n_tokens]
        lines, i, j = [], 0, 0
        while i < len(words):
            k = template[j % len(template)]; lines.append(words[i:i + k]); i += k; j += 1
        out[lang] = lines
    return out, skipped


# ================================================================================================ statistics
def H(c) -> float:
    a = np.array([v for v in c.values() if v > 0], float)
    if a.size == 0:
        return 0.0
    p = a / a.sum()
    return float(-(p * np.log2(p)).sum())


def mi_pairs(pairs) -> float:
    if not pairs:
        return 0.0
    return H(Counter(a for a, _ in pairs)) + H(Counter(b for _, b in pairs)) - H(Counter(pairs))


def stream_stats(word_units: list[list[str]]) -> dict:
    """Unit-level statistics of a word stream (each word = list of units). Entropies on the concatenated unit
    stream with spaces and line breaks removed (paper sec. 2.7)."""
    seq = [u for w in word_units for u in w]
    c1 = Counter(seq)
    h1 = H(c1)
    hc = H(Counter(zip(seq, seq[1:]))) - H(Counter(seq[:-1]))
    within = [p for w in word_units for p in zip(w, w[1:])]
    hcw = H(Counter(within)) - H(Counter(a for a, _ in within)) if within else 0.0
    wl = np.array([len(w) for w in word_units], float)
    fr = np.array(sorted(c1.values(), reverse=True)[:100], float)
    r = np.arange(1, len(fr) + 1)
    zipf = float(np.polyfit(np.log(r), np.log(fr), 1)[0]) if len(fr) > 2 else 0.0
    return {"n_units": len(seq), "types": len(c1), "types_ge_100": sum(v >= 100 for v in c1.values()),
            "h1": h1, "h_cond": hc, "D": h1 - hc, "hc_ratio": hc / h1 if h1 else 0.0, "h_cond_within": hcw,
            "wl_mean": float(wl.mean()), "wl_cv": float(wl.std() / wl.mean()), "unit_zipf": zipf,
            "single_unit_words": float(np.mean(wl == 1))}


def _line_pairs(lines_keys):
    """Adjacent pairs within lines; None breaks adjacency."""
    out = []
    for l in lines_keys:
        for a, b in zip(l, l[1:]):
            if a is not None and b is not None:
                out.append((a, b))
    return out


def _shuffle_lines(lines_keys, rng):
    out = []
    for l in lines_keys:
        pos = [i for i, x in enumerate(l) if x is not None]
        vals = [l[i] for i in pos]
        rng.shuffle(vals)
        m = list(l)
        for i, v in zip(pos, vals):
            m[i] = v
        out.append(m)
    return out


def shuffle_corrected(lines_keys, f_pair, n_shuf, rng, denom_fn):
    """Excess MI = I(observed adjacent pairs) - mean over within-line shuffles; share = excess / denom."""
    obs_pairs = [(f_pair[0](a), f_pair[1](b)) for a, b in _line_pairs(lines_keys)]
    obs = mi_pairs(obs_pairs)
    sh = []
    for _ in range(n_shuf):
        sp = [(f_pair[0](a), f_pair[1](b)) for a, b in _line_pairs(_shuffle_lines(lines_keys, rng))]
        sh.append(mi_pairs(sp))
    exc = obs - float(np.mean(sh))
    d = denom_fn(obs_pairs)
    return {"observed_bits": obs, "shuffled_bits": float(np.mean(sh)), "excess_bits": exc,
            "share": exc / d if d else 0.0, "destroyed": 1 - (float(np.mean(sh)) / obs) if obs else 0.0,
            "n_pairs": len(obs_pairs)}


def token_order(lines_tokens, rng, n_shuf=100, cap=2000):
    """Paper eq. (1): adjacent-token MI after within-line shuffle, 2,000-type cap, share of capped H(T)."""
    cnt = Counter(w for l in lines_tokens for w in l if w is not None)
    keep = {w for w, _ in cnt.most_common(cap)}
    f = lambda w: w if w in keep else "<other>"
    capped = Counter(f(w) for l in lines_tokens for w in l if w is not None)
    r = shuffle_corrected(lines_tokens, (f, f), n_shuf, rng, lambda _: H(capped))
    r["H_T_capped"] = H(capped)
    return r


def edge_order(lines_units, rng, n_shuf=100):
    """Last unit of token t -> first unit of token t+1, shuffle-corrected; share of H(first unit) over pairs.
    lines_units: lines of tuples of units (None = break)."""
    return shuffle_corrected(lines_units, (lambda w: w[-1], lambda w: w[0]), n_shuf, rng,
                             lambda pairs: H(Counter(b for _, b in pairs)))


def _ed1(a, b):
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        return sum(x != y for x, y in zip(a, b)) == 1
    if la > lb:
        a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))


def edit1_ratio(lines_tokens, rng, n_shuf=20):
    obs = np.mean([_ed1(a, b) for a, b in _line_pairs(lines_tokens)])
    sh = [np.mean([_ed1(a, b) for a, b in _line_pairs(_shuffle_lines(lines_tokens, rng))]) for _ in range(n_shuf)]
    return float(obs / np.mean(sh))


def hapax_share(tokens):
    c = Counter(tokens)
    return sum(v == 1 for v in c.values()) / len(c), len(c), sum(v for _, v in c.most_common(50)) / len(tokens)


def internality(lines):
    """Paper eq. (2)-(3), composite-collapsed glyphs, add-0.5 smoothing on the within-token bigram table,
    position-independent within-token unigram marginals. Classes: certain '.', uncertain ',', continuation line
    break (last glyph of a line -> first glyph of the next line of the same page, next line not paragraph-initial).
    """
    toks = [U.collapsed_units(w) for l in lines for w in l["tokens"] if w]
    bi = Counter(p for u in toks for p in zip(u, u[1:]))
    uni = Counter(g for u in toks for g in u)
    V = sorted(uni)
    n_bi = sum(bi.values()) + 0.5 * len(V) ** 2
    pu = {g: uni[g] / sum(uni.values()) for g in V}

    def s(a, c):
        return math.log2(((bi.get((a, c), 0) + 0.5) / n_bi) / (pu[a] * pu[c]))
    s_int = float(np.mean([s(a, c) for u in toks for a, c in zip(u, u[1:])]))
    s_rand = float(sum(pu[a] * pu[c] * s(a, c) for a in V for c in V))
    cls = defaultdict(list)
    for i, l in enumerate(lines):
        for j in range(1, len(l["tokens"])):
            a, b = l["tokens"][j - 1], l["tokens"][j]
            if a and b and l["seps"][j] in ".,":
                v = s(U.collapsed_units(a)[-1], U.collapsed_units(b)[0])
                cls[{".": "certain", ",": "uncertain"}[l["seps"][j]]].append(v)
                cls["first_separator_of_line" if j == 1 else "mid_line_separator"].append(v)
        if i + 1 < len(lines):
            n = lines[i + 1]
            if n["folio"] == l["folio"] and not n["para_start"] and l["tokens"] and n["tokens"] \
                    and l["tokens"][-1] and n["tokens"][0]:
                cls["continuation_line_break"].append(s(U.collapsed_units(l["tokens"][-1])[-1],
                                                        U.collapsed_units(n["tokens"][0])[0]))
    return {k: {"I": (float(np.mean(v)) - s_rand) / (s_int - s_rand), "n": len(v)} for k, v in sorted(cls.items())} | \
        {"anchors_bits": {"s_internal": s_int, "s_random": s_rand}}


def word_units_lines(lines_tokens, seg):
    """Apply a segmentation fn to lines of tokens (None kept) -> (word_units list, lines of unit tuples)."""
    cache = {}

    def g(w):
        if w not in cache:
            cache[w] = tuple(seg(w))
        return cache[w]
    L = [[g(w) if w is not None else None for w in l] for l in lines_tokens]
    return [w for l in L for w in l if w is not None], L


def D_curve(seg_by_k: dict[int, dict[str, list[str]]], words) -> dict:
    out = {}
    for k, m in sorted(seg_by_k.items()):
        seq = [u for w in words for u in m[w]]
        h1 = H(Counter(seq)); hc = H(Counter(zip(seq, seq[1:]))) - H(Counter(seq[:-1]))
        out[k] = {"D": h1 - hc, "types": len(set(seq)), "h1": h1, "span": len(seq) and
                  sum(len(u) for u in seq) / len(seq)}
    return out


def bpe_curve(words, ks=DK, base="raw"):
    segs = {}
    U.learn_bpe(words, max(ks), base=base, checkpoints=ks, on_checkpoint=lambda k, m: segs.__setitem__(k, m))
    return D_curve(segs, words)


def crossfit_curve(lines, ks=DK):
    """Paper's cross-fit: learn BPE on all DEV quires but one, apply to the omitted quire, glyph-weighted D_k."""
    quires = sorted({l["quire"] for l in lines})
    acc = defaultdict(lambda: [0.0, 0])
    for q in quires:
        tr = [w for l in lines if l["quire"] != q for w in l["tokens"] if w]
        te = [w for l in lines if l["quire"] == q for w in l["tokens"] if w]
        if len(te) < 300:
            continue
        full = U.learn_bpe(tr, max(ks))
        n = sum(len(w) for w in te)
        for k in ks:
            b = full.truncated(k)
            seq = [u for w in te for u in b.apply(w)]
            D = H(Counter(seq)) - (H(Counter(zip(seq, seq[1:]))) - H(Counter(seq[:-1])))
            acc[k][0] += D * n; acc[k][1] += n
    return {k: v[0] / v[1] for k, v in sorted(acc.items())}


def half_splits(lines, n=20, seed=SEED, ks=(32, 64)):
    """Random disjoint halves of the DEV quires: overlap of learned compound-unit sets, and argmin of D_k."""
    rng = random.Random(seed)
    quires = sorted({l["quire"] for l in lines})
    res = []
    for _ in range(n):
        qs = quires[:]; rng.shuffle(qs); A = set(qs[: len(qs) // 2])
        ws = [[w for l in lines if (l["quire"] in A) == side for w in l["tokens"] if w] for side in (True, False)]
        row = {}
        for k in list(ks) + [v - 25 for v in VOCABS]:
            sets = [set(m for m in (a + b for a, b in U.learn_bpe(w, k).merges)) for w in ws]
            row[f"overlap_k{k}"] = len(sets[0] & sets[1]) / max(1, min(len(s) for s in sets))
        for side, w in enumerate(ws):
            c = bpe_curve(w, ks=[0, 16, 32, 64, 128, 256])
            row[f"argmin_half{side}"] = min(c, key=lambda k: c[k]["D"])
        res.append(row)
    keys = res[0].keys()
    return {k: (float(np.median([r[k] for r in res])) if "overlap" in k else dict(Counter(r[k] for r in res)))
            for k in keys}


# ================================================================================================ inventories
def inventories_for(lines_tokens, base_words=None, erased_lines=None, kind="eva"):
    """All E012 inventories for one corpus. kind='eva' (Voynich & twins) or 'lang' (letters/syllables base).
    BPE is learned on THIS corpus (same procedure everywhere). Returns {name: (word_units, lines_units)} and,
    for the erased inventory, the unit stream per line (no word boundaries)."""
    words = [w for l in lines_tokens for w in l if w is not None]
    out = {}
    base = "raw" if kind == "eva" else "letters"
    if kind == "eva":
        for name, fn in U.FIXED.items():
            out[name] = word_units_lines(lines_tokens, fn)
    else:
        out["letters"] = word_units_lines(lines_tokens, list)
        out["syllables"] = word_units_lines(lines_tokens, U.syllable_units)
    full = U.learn_bpe(words, max(VOCABS), base=base)
    bpes = {}
    for V in VOCABS:
        b = full.for_vocab(V); bpes[V] = b
        out[f"bpe{V}"] = word_units_lines(lines_tokens, b.apply)
    el = erased_lines if erased_lines is not None else [[w for w in l if w is not None] for l in lines_tokens]
    el = [l for l in el if l]
    eb = U.learn_bpe_lines(el, max(0, ERASED_V - len(full.alphabet)), base=base)
    erased = U.segment_lines_erased(eb, el)
    return out, bpes, (eb, erased, el)


def erased_stats(erased_units):
    seq = [u for l in erased_units for u in l]
    c1 = Counter(seq); h1 = H(c1)
    hc = H(Counter(zip(seq, seq[1:]))) - H(Counter(seq[:-1]))
    fr = np.array(sorted(c1.values(), reverse=True)[:100], float); r = np.arange(1, len(fr) + 1)
    return {"n_units": len(seq), "types": len(c1), "h1": h1, "h_cond": hc, "D": h1 - hc,
            "hc_ratio": hc / h1, "unit_zipf": float(np.polyfit(np.log(r), np.log(fr), 1)[0]),
            "span": sum(len(u) for u in seq) / len(seq)}


CLOUD_FEATS = ["log_types", "h1", "h_cond", "hc_ratio", "wl_mean", "wl_cv", "unit_zipf", "edge_share"]
ERASED_FEATS = ["log_types", "h1", "h_cond", "hc_ratio", "unit_zipf", "span"]


def corpus_profile(lines_tokens, kind, rng, n_shuf, erased_lines=None):
    invs, bpes, (eb, erased, el) = inventories_for(lines_tokens, kind=kind, erased_lines=erased_lines)
    prof = {}
    for name, (wu, lu) in invs.items():
        st = stream_stats(wu)
        eo = edge_order(lu, rng, n_shuf)
        st.update({"edge_bits": eo["excess_bits"], "edge_share": eo["share"], "edge_destroyed": eo["destroyed"],
                   "log_types": math.log(st["types"])})
        prof[name] = st
    es = erased_stats(erased); es["log_types"] = math.log(es["types"])
    prof[f"erased_bpe{ERASED_V}"] = es
    toks = [w for l in lines_tokens for w in l if w is not None]
    hs, nt, top50 = hapax_share(toks)
    to = token_order(lines_tokens, rng, n_shuf)
    word = {"n_tokens": len(toks), "word_types": nt, "hapax_share": hs, "top50_coverage": top50,
            "token_mi_bits": to["excess_bits"], "token_mi_share": to["share"],
            "edit1_ratio": edit1_ratio(lines_tokens, rng, max(5, n_shuf // 5))}
    return prof, word, {"bpe": bpes, "erased_bpe": eb, "erased_units": erased, "erased_lines": el, "invs": invs}


def place_in_cloud(v: dict, cloud: dict[str, dict], feats) -> dict:
    """RMS z of Voynich (or a twin) against the language cloud; inside = <= p95 of the languages' own LOO RMS z."""
    langs = sorted(cloud)
    M = np.array([[cloud[l][f] for f in feats] for l in langs])
    mu, sd = M.mean(0), M.std(0, ddof=1) + 1e-9
    z = (np.array([v[f] for f in feats]) - mu) / sd
    loo = []
    for i in range(len(langs)):
        Mi = np.delete(M, i, 0)
        zi = (M[i] - Mi.mean(0)) / (Mi.std(0, ddof=1) + 1e-9)
        loo.append(float(np.sqrt(np.mean(zi ** 2))))
    d = float(np.sqrt(np.mean(z ** 2)))
    p95 = float(np.percentile(loo, 95))
    return {"rms_z": round(d, 3), "cloud_loo_p95": round(p95, 3), "inside": bool(d <= p95),
            "z": {f: round(float(x), 2) for f, x in zip(feats, z)},
            "features_outside_2sd": [f for f, x in zip(feats, z) if abs(x) >= 2]}


# ================================================================================================ stats stage
def twin_corpora(n_tokens, smoke=False):
    """naibbe_exact (la, it, fr) + E011 best twin of every other family, all re-generated at the Voynich token
    count from role=tune plaintext."""
    specs = json.loads((ROOT / "data/derived/twins_v1/specs.json").read_text())
    pools, (wm, ws) = specs["pools"], specs["layout_line_width_mean_sd"]
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    tune = defaultdict(str)
    for b in load_books():
        if roles.get(b["id"], {}).get("role") == "tune" and len(tune[b["lang"]]) < 600_000:
            tune[b["lang"]] += " " + b["text"][2000:]
    best = {}
    for s in specs["specs"]:
        best.setdefault(s["family"], s)
    jobs = [("naibbe_exact", lg, {}) for lg in (["la"] if smoke else ["la", "it", "fr"])]
    jobs += [(f, best[f]["lang"], best[f]["params"]) for f in ["naibbe", "syllabary", "abbreviation",
                                                                 "rugg_grille", "self_citation"]]
    out = {}
    for i, (fam, lg, params) in enumerate(jobs):
        g = T.generate(fam, params, SEED + i, pools, n_tokens, plain=tune[lg] if lg else None, width_mean=wm,
                       width_sd=ws)
        lines = g["lines"]
        n, cut = 0, []
        for l in lines:
            cut.append(l); n += len(l)
            if n >= n_tokens:
                break
        out[f"{fam}/{lg}" if lg else fam] = {"lines": cut, "is_language": g["is_language"]}
    return out


def stats_stage(a):
    t0 = time.time()
    rng = random.Random(SEED)
    lines, locked = voynich_dev_lines()
    toks_lines = [l["tokens"] for l in lines]
    words = [w for l in toks_lines for w in l if w]
    n_shuf = 10 if a.smoke else 100
    res = {"experiment": "E012", "seed": SEED, "protocol": "DEV leaves only; LOCKED_TEST excluded: " + ",".join(locked),
           "paper": "Rozanova & Temerev, arXiv:2608.17096 (2026)", "paper_values": PAPER}
    # ---------------------------------------------------------------- 1. replication
    rep = {"data": {"lines": len(lines), "clean_tokens": len(words), "glyphs": sum(map(len, words)),
                    "quires": len({l["quire"] for l in lines}),
                    "separators": dict(Counter(s for l in lines for s in l["seps"][1:]))}}
    for name, fn in (("collapsed", U.collapsed_units), ("raw", U.raw_units)):
        st = stream_stats([fn(w) for w in words])
        rep[f"entropy_{name}"] = {k: st[k] for k in ("n_units", "types", "types_ge_100", "h1", "h_cond",
                                                      "h_cond_within")} | {"perplexity": 2 ** st["h_cond"]}
    to = token_order(toks_lines, rng, n_shuf)
    tom = token_order([l["tokens"] for l in merge_uncertain(lines)], rng, n_shuf)
    rep["token_order"] = to; rep["token_order_uncertain_merged"] = tom
    _, lu = word_units_lines(toks_lines, U.collapsed_units)
    rep["edge_order_collapsed"] = edge_order(lu, rng, n_shuf)
    _, lur = word_units_lines(toks_lines, U.raw_units)
    rep["edge_order_raw"] = edge_order(lur, rng, n_shuf)
    # y->q contribution (paper: ~half of the edge information)
    pairs = [(a[-1], b[0]) for a, b in _line_pairs(lu)]
    pc, pa, pb, N = Counter(pairs), Counter(a for a, _ in pairs), Counter(b for _, b in pairs), len(pairs)
    rep["edge_pmi_top"] = sorted(([f"{x}->{y}", round(c / N * math.log2(c * N / (pa[x] * pb[y])), 4)]
                                  for (x, y), c in pc.items()), key=lambda r: -r[1])[:6]
    hs, nt, top50 = hapax_share(words)
    mw = [w for l in merge_uncertain(lines) for w in l["tokens"] if w]
    rep["vocabulary"] = {"tokens": len(words), "types": nt, "hapax_share": hs, "top50_coverage": top50,
                         "merged_hapax_share": hapax_share(mw)[0], "merged_tokens": len(mw),
                         "edit1_ratio": edit1_ratio(toks_lines, rng, 20)}
    rep["internality"] = internality(lines)
    rep["bpe_curve_raw"] = bpe_curve(words)
    rep["bpe_curve_collapsed_base"] = bpe_curve(words, ks=[0, 16, 32, 64, 128, 256], base="collapsed")
    rep["bpe_crossfit_loqo"] = crossfit_curve(lines) if not a.smoke else {}
    rep["bpe_half_splits"] = half_splits(lines, n=4 if a.smoke else 20)
    by_cur = {c: [w for l in lines if l["currier"] == c for w in l["tokens"] if w] for c in "AB"}
    rep["bpe_curve_currier"] = {c: {k: v["D"] for k, v in bpe_curve(w, ks=[0, 16, 32, 64, 128, 256]).items()}
                                for c, w in by_cur.items()}
    # space-erased BPE on lines whose tokens are all clean, crossing rates at 64 merges (paper Table 8)
    full_lines = [l for l in lines if l["tokens"] and all(l["tokens"])]
    el = [l["tokens"] for l in full_lines]
    segs = {}
    U.learn_bpe_lines(el, 256, checkpoints=[0, 16, 32, 64, 128, 256], on_checkpoint=lambda k, s: segs.__setitem__(k, s))
    er = {}
    for k, s in segs.items():
        seq = [u for x in s for u in x]
        er[k] = {"D": H(Counter(seq)) - (H(Counter(zip(seq, seq[1:]))) - H(Counter(seq[:-1]))),
                 "types": len(set(seq))}
    rep["erased_bpe_curve"] = er
    rep["erased_crossing_k64"] = U.crossing_rates(segs[64], el, [l["seps"] for l in full_lines])
    rep["erased_lines_used"] = len(el)
    res["replication"] = rep
    print("replication done", round(time.time() - t0), "s", flush=True)

    # ---------------------------------------------------------------- 2-3. inventories, cloud, twins
    template = [sum(1 for w in l if w) for l in toks_lines if any(l)]
    vprof, vword, vextra = corpus_profile(toks_lines, "eva", rng, n_shuf, erased_lines=el)
    res["voynich_profile"] = vprof; res["voynich_word"] = vword
    res["voynich_bpe_vocab"] = {V: vextra["bpe"][V].vocab[-12:] for V in VOCABS}
    langs, skipped = language_samples(len(words), template)
    if a.smoke:
        langs = {k: langs[k] for k in list(langs)[:5]}
    lprof, lword = {}, {}
    for lg, ll in langs.items():
        p, w, ex = corpus_profile(ll, "lang", rng, max(10, n_shuf // 5))
        lprof[lg], lword[lg] = p, w
        if lg == "la":
            # Latin crossing rate after space erasure at 64 merges (paper: 15.5%)
            s64 = U.segment_lines_erased(U.learn_bpe_lines(ex["erased_lines"], 64, base="letters"),
                                         ex["erased_lines"])
            res["latin_erased_crossing_k64"] = U.crossing_rates(s64, ex["erased_lines"])
        print("  lang", lg, round(time.time() - t0), "s", flush=True)
    res["languages"] = {"n": len(langs), "skipped_too_small": skipped, "profiles": lprof, "word": lword}
    twins = twin_corpora(len(words), a.smoke)
    tprof, tword = {}, {}
    for name, d in twins.items():
        p, w, _ = corpus_profile(d["lines"], "eva", rng, max(10, n_shuf // 5))
        tprof[name], tword[name] = p, w
        print("  twin", name, round(time.time() - t0), "s", flush=True)
    res["twins"] = {"profiles": tprof, "word": tword,
                    "is_language": {k: v["is_language"] for k, v in twins.items()}}

    # placement: each Voynich/twin inventory vs language clouds built with the matched procedure
    match = {"raw": ["letters", "syllables"], "collapsed": ["letters", "syllables"], "slot": ["letters", "syllables"]}
    for V in VOCABS:
        match[f"bpe{V}"] = [f"bpe{V}", "letters", "syllables"]
    match[f"erased_bpe{ERASED_V}"] = [f"erased_bpe{ERASED_V}"]
    place = {}
    for inv, refs in match.items():
        place[inv] = {}
        for ref in refs:
            feats = ERASED_FEATS if inv.startswith("erased") else CLOUD_FEATS
            cloud = {lg: p[ref] for lg, p in lprof.items()}
            row = {"voynich": place_in_cloud(vprof[inv], cloud, feats)}
            for tn, tp in tprof.items():
                row[tn] = place_in_cloud(tp[inv], cloud, feats)["rms_z"]
            place[inv][ref] = row
    res["placement"] = place
    wf = ["hapax_share", "token_mi_share", "top50_coverage", "edit1_ratio"]
    res["placement_word_level"] = {"voynich": place_in_cloud(vword, lword, wf)} | \
        {tn: place_in_cloud(tw, lword, wf)["rms_z"] for tn, tw in tword.items()}
    # edge coupling table
    edge = {}
    for inv in ["raw", "collapsed", "slot"] + [f"bpe{V}" for V in VOCABS]:
        lang_ref = "letters" if inv in ("raw", "collapsed", "slot") else inv
        lv = [lprof[lg][lang_ref]["edge_bits"] for lg in lprof]
        ls = [lprof[lg][lang_ref]["edge_share"] for lg in lprof]
        edge[inv] = {"voynich_bits": vprof[inv]["edge_bits"], "voynich_share": vprof[inv]["edge_share"],
                     "languages_bits_median_max": [float(np.median(lv)), float(np.max(lv))],
                     "languages_share_median_max": [float(np.median(ls)), float(np.max(ls))],
                     "languages_syllables_bits_median_max": [
                         float(np.median([lprof[l]["syllables"]["edge_bits"] for l in lprof])),
                         float(np.max([lprof[l]["syllables"]["edge_bits"] for l in lprof]))],
                     "twins_bits": {tn: tp[inv]["edge_bits"] for tn, tp in tprof.items()},
                     "twins_share": {tn: tp[inv]["edge_share"] for tn, tp in tprof.items()}}
    res["edge_coupling"] = edge
    res["wall_s_stats"] = round(time.time() - t0)
    STATS_OUT.write_text(json.dumps(res, indent=1, default=float))
    return res


# ================================================================================================ solver stage
_S = {}


def _init_solver():
    from vcl.solvers.api import solve
    from vcl.solvers.lm import Library
    _S["solve"], _S["lib"] = solve, Library.full()


def _run_task(t):
    from vcl.synthetic.schema import PublicTask
    from vcl.solvers.selfnull import solve_v2
    from vcl.eval.score import char_acc
    t0 = time.time()
    task = PublicTask(t["id"], t["symbols"], "e012")
    p = solve_v2(task, _S["solve"], t["margin"], library=_S["lib"], seed=t["seed"])
    chosen = next((x["chosen"] for x in p.log if isinstance(x, dict) and "chosen" in x), {})
    self_null = next((x for x in p.log if isinstance(x, dict) and "self_null_conf" in x), None)
    row = {k: t[k] for k in ("id", "inventory", "window_tokens", "condition", "is_language", "lang", "n_symbols", "n_types",
                             "has_boundaries")}
    row.update({"answered": not p.abstain, "confidence": round(float(p.confidence), 4),
                "family": chosen.get("family"), "language_guess": p.language,
                "gap": chosen.get("gap"), "self_null": self_null, "seconds": round(time.time() - t0, 1)})
    if t.get("gold") is not None and not p.abstain and p.plaintext is not None:
        row["char_acc"] = round(char_acc(p.plaintext.replace(" ", ""), t["gold"].replace(" ", "")), 4)
    if t["condition"] == "voynich":
        row["language_guess"] = None   # not reported: a guessed language is not evidence (see report)
        row["decode_withheld"] = True  # Voynich decodes are never stored
    return row


def _symbols(word_units, boundaries=True):
    out = []
    for w in word_units:
        if out and boundaries:
            out.append(" ")
        out.extend(w)
    return out


def _markov(symbols, n, rng, order=3):
    tr = defaultdict(Counter)
    for i in range(order, len(symbols)):
        tr[tuple(symbols[i - order:i])][symbols[i]] += 1
    out = list(symbols[:order])
    while len(out) < n:
        c = tr.get(tuple(out[-order:]))
        if not c:
            out.extend(symbols[:order]); continue
        out.append(rng.choices(list(c), weights=list(c.values()))[0])
    out = out[:n]
    while out and out[0] == " ":
        out.pop(0)
    while out and out[-1] == " ":
        out.pop()
    return out


def _sub_cipher(plain: str, K: int, rng, boundaries=True):
    """Known-answer substitution of letters: mono if K <= #letters, else homophonic with K symbols allocated by
    frequency (each letter >= 1 homophone, uniform choice)."""
    if not boundaries:
        plain = plain.replace(" ", "")
    c = Counter(ch for ch in plain if ch != " ")
    alloc = {l: 1 for l in c}
    for _ in range(max(0, K - len(c))):
        l = max(c, key=lambda x: (c[x] / alloc[x], x)); alloc[l] += 1
    names = [f"u{i}" for i in range(sum(alloc.values()))]
    rng.shuffle(names)
    ids, n = {}, 0
    for l in sorted(alloc):
        ids[l] = names[n:n + alloc[l]]; n += alloc[l]
    return [" " if ch == " " else rng.choice(ids[ch]) for ch in plain], ("mono" if K <= len(c) else "homophonic")


def _syll_cipher(words, n_sym, boundaries=True):
    names, out = {}, []
    for w in words:
        if out and boundaries:
            out.append(" ")
        for s in U.syllable_units(w):
            out.append(names.setdefault(s, f"s{len(names)}"))
        if len(out) >= n_sym:
            break
    return out[:n_sym]


def build_solver_tasks(a, margin):
    rng = random.Random(SEED + 1)
    lines, _ = voynich_dev_lines()
    toks_lines = [l["tokens"] for l in lines]
    words = [w for l in toks_lines for w in l if w]
    full_lines = [l["tokens"] for l in lines if l["tokens"] and all(l["tokens"])]
    vb = U.learn_bpe(words, max(VOCABS))
    vbe = U.learn_bpe_lines(full_lines, ERASED_V - len(vb.alphabet))
    n_win = 2 if a.smoke else 6
    roles = json.loads((ROOT / "data/derived/benchmark_v1/book_roles.json").read_text())
    tune = defaultdict(str)
    for b in load_books():
        if roles.get(b["id"], {}).get("role") == "tune" and len(tune[b["lang"]]) < 400_000:
            tune[b["lang"]] += " " + b["text"][2000:]
    ka_langs = ["la", "it", "de", "fr", "es", "cs"][: (2 if a.smoke else 6)]
    syl_langs = ["la", "it", "de"][: (1 if a.smoke else 3)]
    nx_langs = ["la", "it", "fr"][: (1 if a.smoke else 3)]
    # twin streams for meaningless decoys (E011 best specs), re-tokenised per inventory with BPE learned on them
    specs = json.loads((ROOT / "data/derived/twins_v1/specs.json").read_text())
    pools, (wm, ws) = specs["pools"], specs["layout_line_width_mean_sd"]
    best = {}
    for s in specs["specs"]:
        best.setdefault(s["family"], s)
    dec = {}
    for i, fam in enumerate(["rugg_grille", "self_citation"]):
        g = T.generate(fam, best[fam]["params"], SEED + 50 + i, pools, 6000, width_mean=wm, width_sd=ws)
        dw = [w for l in g["lines"] for w in l if w]
        dec[fam] = (dw, U.learn_bpe(dw, max(VOCABS)), U.learn_bpe_lines([l for l in g["lines"] if l],
                                                                       ERASED_V - 25))
    # naibbe_exact: encode without space removal so the plaintext n-grams align with cipher tokens (gold)
    nx = {}
    for lg in nx_langs:
        k = NX.key({}, 0, "")
        cw, grams = NX.encode_tokens(tune[lg][:60000], k, SEED + 7)
        nx[lg] = (cw, grams, U.learn_bpe(cw, max(VOCABS)))
    invs = ["raw", "collapsed", "slot"] + [f"bpe{V}" for V in VOCABS] + [f"erased_bpe{ERASED_V}"]
    if a.smoke:
        invs = ["collapsed", "bpe150", f"erased_bpe{ERASED_V}"]
    tasks = []

    def seg_fn(inv, bpe):
        if inv in U.FIXED:
            return U.FIXED[inv]
        return bpe.for_vocab(int(inv[3:])).apply

    def add(inv, cond, sym, is_lang, lang=None, gold=None, extra="", wt=WIN_TOKENS):
        tasks.append({"id": f"{inv}|w{wt}|{cond}|{lang}|{extra}", "inventory": inv if wt == WIN_TOKENS
                      else f"{inv}@w{wt}", "window_tokens": wt, "condition": cond, "symbols": sym,
                      "is_language": is_lang, "lang": lang, "gold": gold, "n_symbols": len(sym),
                      "n_types": len(set(sym) - {" "}), "has_boundaries": " " in sym, "margin": margin,
                      "seed": rng.randrange(2 ** 31)})

    plan = [(inv, WIN_TOKENS, False) for inv in invs]
    plan += [(inv, LONG_WIN_TOKENS, True) for inv in invs if inv in LONG_INVS]
    for inv, wt, long in plan:
        erased = inv.startswith("erased")
        nw = n_win if not long else max(2, n_win // 2)
        offs = [int(i * (len(words) - wt) / (nw - 1)) for i in range(nw)]
        n_ka = len(ka_langs) if not long else max(2, len(ka_langs) * 2 // 3)
        n_rep = 1 if (a.smoke or long) else 2
        vwin = []
        for o in offs:
            if erased:
                # lines (all-clean) covering the same manuscript region, units across erased spaces
                start = int(o / len(words) * len(full_lines))
                ls, n = [], 0
                for l in full_lines[start:]:
                    ls.append(l); n += len(l)
                    if n >= wt:
                        break
                sym = [u for x in U.segment_lines_erased(vbe, ls) for u in x]
            else:
                sym = _symbols([seg_fn(inv, vb)(w) for w in words[o:o + wt]])
            vwin.append(sym)
            add(inv, "voynich", sym, None, extra=str(o), wt=wt)
        L, K = int(np.median([len(s) for s in vwin])), int(np.median([len(set(s) - {" "}) for s in vwin]))
        # known-answer letter substitution matched in symbol count and unit-type count
        for j, lg in enumerate(ka_langs[:n_ka]):
            txt = tune[lg]
            s0 = rng.randrange(5000, len(txt) - 20 * L)
            s0 = txt.find(" ", s0) + 1
            plain = txt[s0:s0 + (L if not erased else int(L * 1.2))].rsplit(" ", 1)[0]
            sym, kind = _sub_cipher(plain, K, rng, boundaries=not erased)
            add(inv, f"ka_letters_{kind}", sym, True, lg, gold=plain, extra=str(j), wt=wt)
        for j, lg in enumerate(syl_langs[: 1 if long else None]):
            txt = tune[lg]; s0 = rng.randrange(5000, len(txt) - 40 * L)
            sym = _syll_cipher(txt[s0:].split(" ")[1:], L, boundaries=not erased)
            add(inv, "ka_syllables", sym, True, lg, gold=None, extra=str(j), wt=wt)
        for lg, (cw, grams, nb) in list(nx.items())[: 1 if long else None]:
            o = rng.randrange(0, len(cw) - 2 * wt)
            if erased:
                eb = U.learn_bpe_lines([cw[i:i + 9] for i in range(0, len(cw), 9)], ERASED_V - 25)
                sym = eb.apply_units([g for w in cw[o:o + wt] for g in w])
            else:
                sym = _symbols([seg_fn(inv, nb)(w) for w in cw[o:o + wt]])
            add(inv, "naibbe_exact", sym, True, lg, gold="".join(grams[o:o + wt]), wt=wt)
        for fam, (dw, db, dbe) in dec.items():
            for j in range(n_rep):
                o = rng.randrange(0, len(dw) - wt)
                if erased:
                    sym = dbe.apply_units([g for w in dw[o:o + wt] for g in w])
                else:
                    sym = _symbols([seg_fn(inv, db)(w) for w in dw[o:o + wt]])
                add(inv, f"decoy_{fam}", sym, False, extra=str(j), wt=wt)
        if erased:
            src = [u for x in U.segment_lines_erased(vbe, full_lines) for u in x]
        else:
            src = _symbols([seg_fn(inv, vb)(w) for w in words])
        for j in range(n_rep):
            add(inv, "decoy_markov3_voynich_units", _markov(src[rng.randrange(len(src) // 2):], L, rng), False,
                extra=str(j), wt=wt)
    return tasks


def solver_stage(a):
    t0 = time.time()
    margin = json.loads((ROOT / "experiments/results/e005.json").read_text())["margin"]
    tasks = build_solver_tasks(a, margin)
    print(f"solver tasks: {len(tasks)}", Counter(t["condition"] for t in tasks), flush=True)
    rows = []
    done = set()
    if SOLVER_ROWS.exists() and a.resume:
        rows = [json.loads(l) for l in SOLVER_ROWS.read_text().splitlines() if l.strip()]
        done = {r["id"] for r in rows}
    todo = [t for t in tasks if t["id"] not in done]
    # interleave so a partial run covers every inventory
    todo.sort(key=lambda t: (t["condition"] == "voynich", t["inventory"], t["id"]))
    with Pool(a.workers, initializer=_init_solver) as pool, open(SOLVER_ROWS, "a") as f:
        for r in pool.imap_unordered(_run_task, todo):
            rows.append(r); f.write(json.dumps(r, default=float) + "\n"); f.flush()
            print(f"  [{len(rows)}/{len(tasks)}] {r['inventory']:14s} {r['condition']:30s} "
                  f"ans={int(r['answered'])} conf={r['confidence']:.3f} acc={r.get('char_acc', '-')} "
                  f"{r['seconds']}s", flush=True)
    ids = {t["id"] for t in tasks}
    rows = [r for r in rows if r["id"] in ids]
    return summarise_solver(rows, margin, round(time.time() - t0))


def summarise_solver(rows, margin, wall):
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[r["inventory"]][r["condition"]].append(r)
    meaningless = [r for r in rows if r["is_language"] is False]
    # streams a letter-substitution solver cannot read correctly: decoys + verbose (naibbe_exact) + syllable ciphers;
    # any answer on them is a false discovery (naibbe answers were also scored: all had char acc < 0.9)
    nonletter = [r for r in rows if r["condition"].startswith(("decoy", "naibbe", "ka_syllables"))]
    table = {}
    for inv, conds in by.items():
        t = {}
        for c, rs in conds.items():
            ans = [r for r in rs if r["answered"]]
            acc = [r.get("char_acc", 0.0) for r in ans]
            t[c] = {"n": len(rs), "answered": len(ans), "answer_rate": len(ans) / len(rs),
                    "solved_ge_0.9": sum(x >= 0.9 for x in acc) if c.startswith(("ka_letters", "naibbe")) else None,
                    "mean_char_acc_answered": float(np.mean(acc)) if acc and c.startswith(("ka_letters", "naibbe"))
                    else None,
                    "mean_types": float(np.mean([r["n_types"] for r in rs])),
                    "mean_symbols": float(np.mean([r["n_symbols"] for r in rs])),
                    "confidences": [r["confidence"] for r in rs]}
        ka = [r for c, rs in conds.items() if c.startswith("ka_letters") for r in rs]
        ka_acc = [r.get("char_acc", 0.0) if r["answered"] else 0.0 for r in ka]
        gate1 = bool(ka) and float(np.mean([x >= 0.9 for x in ka_acc])) >= 0.9
        dec = [r for c, rs in conds.items() if c.startswith("decoy") for r in rs]
        nl = [r for c, rs in conds.items() if c.startswith(("decoy", "naibbe", "ka_syllables")) for r in rs]
        t["_nonletter_false_answer_rate"] = float(np.mean([r["answered"] for r in nl])) if nl else None
        t["_gate1_known_answer_solved_rate"] = float(np.mean([x >= 0.9 for x in ka_acc])) if ka else None
        t["_gate1_pass"] = gate1
        t["_decoy_false_positive_rate"] = float(np.mean([r["answered"] for r in dec])) if dec else None
        vy = conds.get("voynich", [])
        t["_voynich_answered"] = []
        for r in vy:
            if r["answered"]:
                fpr_inv = float(np.mean([d["answered"] and d["confidence"] >= r["confidence"] for d in dec])) if dec else None
                fpr_all = float(np.mean([d["answered"] and d["confidence"] >= r["confidence"] for d in meaningless]))
                fa_inv = float(np.mean([d["answered"] and d["confidence"] >= r["confidence"] for d in nl]))
                fa_all = float(np.mean([d["answered"] and d["confidence"] >= r["confidence"] for d in nonletter]))
                t["_voynich_answered"].append({"id": r["id"], "confidence": r["confidence"],
                                               "nonletter_false_answer_rate_at_conf_this_inventory": fa_inv,
                                               "nonletter_false_answer_rate_at_conf_pooled": fa_all,
                                               "decoy_fpr_at_conf_this_inventory": fpr_inv,
                                               "decoy_fpr_at_conf_pooled": fpr_all,
                                               "status": "VOID (Gate 1 failed)" if not gate1 else
                                               "answered -- NOT a reading; see report"})
        t["_voynich_status"] = ("VOID: Gate 1 (known-answer >= 0.9 at this unit scale) failed" if not gate1 else
                                "valid run")
        table[inv] = t
    return {"margin": margin, "n_tasks": len(rows), "table": table, "wall_s": wall,
            "pooled_decoy_fpr": float(np.mean([r["answered"] for r in meaningless])) if meaningless else None,
            "pooled_nonletter_false_answer_rate": float(np.mean([r["answered"] for r in nonletter])) if nonletter
            else None}


# ================================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["stats", "solver", "all", "resummarise"], default="all")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--resume", action="store_true", help="reuse finished solver rows in e012_solver_rows.jsonl")
    a = ap.parse_args()
    global STATS_OUT, SOLVER_ROWS, OUT
    if a.smoke:
        d = ROOT / "experiments/results/smoke"; d.mkdir(exist_ok=True, parents=True)
        STATS_OUT, SOLVER_ROWS, OUT = d / "e012_stats.json", d / "e012_solver_rows.jsonl", d / "e012.json"
    if not a.resume and a.stage in ("solver", "all") and SOLVER_ROWS.exists():
        SOLVER_ROWS.unlink()
    if a.stage == "resummarise":   # recompute the solver summary from the saved rows (no solver calls)
        res = json.loads(OUT.read_text())
        rows = [json.loads(l) for l in SOLVER_ROWS.read_text().splitlines() if l.strip()]
        res["solver"] = summarise_solver(rows, res["solver"]["margin"], res["solver"]["wall_s"])
        res["solver"]["resummarised"] = "added non-letter false-answer rates (decoys + naibbe_exact + syllables)"
        OUT.write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({k: {kk: v for kk, v in t.items() if kk.startswith("_")} for k, t in
                          res["solver"]["table"].items()}, indent=1))
        return
    res = stats_stage(a) if a.stage in ("stats", "all") else json.loads(STATS_OUT.read_text())
    if a.stage in ("solver", "all"):
        res["solver"] = solver_stage(a)
    res["command"] = " ".join(["caffeinate -ims .venv/bin/python"] + sys.argv)
    OUT.write_text(json.dumps(res, indent=1, default=float))
    if not a.smoke and "solver" in res:
        write_ledger(res)
    print("written", OUT)


def write_ledger(res):
    from vcl.eval.ledger import append
    rep, cmd = res["replication"], res["command"]
    rows = [
        ("hcond_collapsed", rep["entropy_collapsed"]["h_cond"], "paper 2.69 (full ZL corpus)"),
        ("hcond_raw", rep["entropy_raw"]["h_cond"], "paper 2.32"),
        ("token_mi_share", rep["token_order"]["share"], "paper 0.79%"),
        ("edge_mi_bits_collapsed", rep["edge_order_collapsed"]["excess_bits"], "paper 0.197"),
        ("hapax_share", rep["vocabulary"]["hapax_share"], "paper 69.7% at 32,747 tokens"),
        ("internality_uncertain", rep["internality"]["uncertain"]["I"], "paper 0.494"),
        ("internality_certain", rep["internality"]["certain"]["I"], "paper 0.029"),
    ]
    out = [dict(experiment="E012", model="replication:rozanova_temerev_2026", split="voynich_DEV", metric=m,
                value=round(v, 4), command=cmd, notes=n) for m, v, n in rows]
    for inv, p in res["placement"].items():
        for ref, row in p.items():
            out.append(dict(experiment="E012", model=f"inventory:{inv}", split="voynich_DEV",
                            metric=f"rms_z_vs_{ref}_cloud", value=row["voynich"]["rms_z"], command=cmd,
                            notes=f"inside={row['voynich']['inside']}; cloud LOO p95 {row['voynich']['cloud_loo_p95']}"))
    for inv, t in res["solver"]["table"].items():
        for metric, v in (("gate1_known_answer_solved_rate", t["_gate1_known_answer_solved_rate"]),
                          ("decoy_false_positive_rate", t["_decoy_false_positive_rate"]),
                          ("voynich_answer_rate", t.get("voynich", {}).get("answer_rate"))):
            if v is not None:
                out.append(dict(experiment="E012", model=f"solver_v2@{inv}", checkpoint_sha256=
                                f"margin={res['solver']['margin']:.4f}", split="voynich_DEV_windows+calibration",
                                metric=metric, value=round(v, 4), command=cmd, notes=t["_voynich_status"]))
    append(out)


if __name__ == "__main__":
    main()
