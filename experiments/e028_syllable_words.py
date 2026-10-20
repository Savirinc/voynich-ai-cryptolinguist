"""E028 (Occam rung 1, word level): do the units of simple-syllable languages behave like Voynich words in topic
clustering (E019) and persistence of common words (E021)?

Pre-registered in reports/E028_PREREG.md. Texts: the E027 Bibles (data/external/bibles). Tokens per language as in
E027: haw1868, ton, mri2012, vie1934 words (NFC; for these NATIVE and MARKS give the same token identities) and
Mandarin pinyin syllables WITH tone digits (cmn-cu89s/MARKS; toneless reported). Anchors: latVUC, eng-kjv words.
Sampling (E019 design: one segment per source): each Bible, in canonical book order, is cut into 4 equal quarters;
a sample takes one random contiguous window of N/4+1 tokens from each quarter. 10 samples per text, at Voynich DEV
size (28,841) and Currier B size (19,490).
Features: E019 burst() -> I_word, top_word; E021 persistence() -> PERS_30, COV_30 (functions imported unchanged).
Family SIMPLE = the 5 simple-syllable texts pooled (50 samples); family BIBLE_EU = the 2 anchors pooled (20).
CONSISTENT iff |z| <= 3 on all four features (sd floor 0.01, as E019/E021).
Gate: BIBLE_EU's mean I_word and mean PERS_30 lie inside the E019 / E021 'word' family ranges (0.271-0.712; 0.229-0.562).

Run: caffeinate -ims .venv/bin/python experiments/e028_syllable_words.py [--calib]
"""
from __future__ import annotations

import argparse, hashlib, json, random, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import e011_twin_search as E  # noqa: E402
import e019_unit_burstiness as A19  # noqa: E402
import e021_persistence as A21  # noqa: E402
import e027_simple_syllables as S  # noqa: E402

SEED = 28028
PREREG = ROOT / "reports/E028_PREREG.md"
OUT = ROOT / "experiments/results/e028.json"
FEATS = ["I_word", "top_word", "PERS_30", "COV_30"]
TEXTS = {"haw1868": "NATIVE", "ton": "NATIVE", "mri2012": "NATIVE", "vie1934": "NATIVE", "cmn-cu89s": "MARKS"}
ANCH = {"latVUC": "NATIVE", "eng-kjv": "NATIVE"}
EXTRA = {"cmn-cu89s#toneless": ("cmn-cu89s", "NATIVE")}   # reported only
WORD_RANGE = {"I_word": (0.271, 0.712), "PERS_30": (0.229, 0.562)}
Z_OK, NS = 3.0, 10


def all_tokens(bid, rendering):
    S.N, S.SKIP = 10 ** 9, 0          # whole text, nothing skipped
    return ["".join(w) for w in S.words(bid, rendering)]


def sample(toks, N, rng):
    q = len(toks) // 4; per = N // 4 + 1; out = []
    for i in range(4):
        s = rng.randrange(i * q, (i + 1) * q - per)
        out += toks[s:s + per]
    return out[:N]


def feats(toks):
    Iw, Tw, _ = A19.burst(toks)
    return {"I_word": Iw, "top_word": Tw, **A21.persistence(toks)}


def summarize(rows):
    mu = {k: float(np.mean([r[k] for r in rows])) for k in FEATS}
    sd = {k: max(float(np.std([r[k] for r in rows], ddof=1)), 0.01) for k in FEATS}
    return mu, sd, {k: [min(r[k] for r in rows), max(r[k] for r in rows)] for k in FEATS}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--calib", action="store_true"); a = ap.parse_args()
    prereg_sha = hashlib.sha256(PREREG.read_bytes()).hexdigest() if PREREG.exists() else None
    if not a.calib and prereg_sha is None:
        sys.exit("pre-registration missing")
    lines, cur, _, _ = E.voynich_lines()
    sizes = {"DEV": sum(1 for l in lines for w in l if w), "B": sum(1 for l, c in zip(lines, cur) if c == "B" for w in l if w)}
    rng = random.Random(SEED)
    rows = []
    for name, (bid, r) in {**{k: (k, v) for k, v in {**TEXTS, **ANCH}.items()}, **EXTRA}.items():
        toks = all_tokens(bid, r)
        for part, N in sizes.items():
            for i in range(NS):
                rows.append({"text": name, "part": part, **feats(sample(toks, N, rng))})
        d = [x for x in rows if x["text"] == name and x["part"] == "DEV"]
        print(f"{name:20s} tokens {len(toks):7d} DEV " + " ".join(f"{k} {np.mean([x[k] for x in d]):.3f}" for k in FEATS), flush=True)
    res = {"experiment": "e028", "prereg_sha256": prereg_sha, "seed": SEED, "sizes": sizes, "rows": rows, "parts": {}}
    fam = {"SIMPLE": list(TEXTS), "BIBLE_EU": list(ANCH)}
    for part in sizes:
        res["parts"][part] = {"families": {}}
        for f, members in fam.items():
            mu, sd, rg = summarize([x for x in rows if x["part"] == part and x["text"] in members])
            res["parts"][part]["families"][f] = {"mean": mu, "sd": sd, "range": rg}
            print(part, f, " ".join(f"{k} {mu[k]:.3f}±{sd[k]:.3f}" for k in FEATS), flush=True)
    mu = res["parts"]["DEV"]["families"]["BIBLE_EU"]["mean"]
    gate = all(lo <= mu[k] <= hi for k, (lo, hi) in WORD_RANGE.items())
    res["gate"] = gate
    print("gate (Bible anchors behave like E019/E021 word twins):", gate, flush=True)
    if a.calib:       # never compute the Voynich statistics in calibration
        (ROOT / "experiments/results/smoke").mkdir(parents=True, exist_ok=True)
        (ROOT / "experiments/results/smoke/e028_calib.json").write_text(json.dumps(res, indent=1)); return
    for part, toks in (("DEV", [w for l in lines for w in l if w]),
                       ("B", [w for l, c in zip(lines, cur) if c == "B" for w in l if w])):
        v = feats(toks); P = res["parts"][part]; P["voynich"] = v
        for f, o in P["families"].items():
            o["z"] = {k: (v[k] - o["mean"][k]) / o["sd"][k] for k in FEATS}
            o["consistent"] = bool(all(abs(o["z"][k]) <= Z_OK for k in FEATS))
        for t in list(TEXTS) + list(ANCH) + list(EXTRA):
            mu_t, sd_t, _ = summarize([x for x in rows if x["part"] == part and x["text"] == t])
            P.setdefault("per_text", {})[t] = {k: (v[k] - mu_t[k]) / sd_t[k] for k in FEATS}
        print(part, "Voynich", {k: round(v[k], 3) for k in FEATS}, flush=True)
        for f, o in P["families"].items():
            print(f"  {f:9s} z " + " ".join(f"{k} {o['z'][k]:+.1f}" for k in FEATS) + ("  CONSISTENT" if o["consistent"] else "  inconsistent"), flush=True)
        for t, z in P["per_text"].items():
            print(f"    {t:20s} z " + " ".join(f"{k} {z[k]:+.1f}" for k in FEATS), flush=True)
    res["verdict"] = ("VOID (gate failed)" if not gate else
                      "RUNG 1 CONSISTENT AT WORD LEVEL" if res["parts"]["DEV"]["families"]["SIMPLE"]["consistent"]
                      else "RUNG 1 INCONSISTENT AT WORD LEVEL")
    print("VERDICT:", res["verdict"], flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    from vcl.eval.ledger import append
    append([dict(experiment="E028", model=f"family/{f}", checkpoint_sha256=f"prereg={prereg_sha[:12]}",
                 split=f"voynich_{part}", metric=f"z_{k}", value=round(o["z"][k], 2), command=" ".join(sys.argv),
                 notes="CONSISTENT" if o["consistent"] else "inconsistent")
            for part in sizes for f, o in res["parts"][part]["families"].items() for k in FEATS]
           + [dict(experiment="E028", model="verdict", checkpoint_sha256=f"prereg={prereg_sha[:12]}", split="voynich_DEV",
                   metric="verdict", value=0, command=" ".join(sys.argv), notes=res["verdict"])])


if __name__ == "__main__":
    main()
