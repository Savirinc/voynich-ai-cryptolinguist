"""E077: where is a label word odd - in its bridge (as foreign names are) or everywhere? See reports/E077_PREREG.md.

Slots: front (longest match among the text's 10 commonest fronts of 0-3 characters), ending (longest match among its
20 commonest endings of 0-4 characters), bridge = what is left. Lists and the "known bridge" set come from ordinary words
(Voynich: prose; Latin: words that are not names). A bridge is known if it is the bridge of >= 3 different ordinary
word types. Normal rates per slot: front in list (non-empty), ending in list (non-empty), bridge known.
Target vs control (rare ordinary words, frequency 1-2, drawn to the target's length distribution); excess oddness per
slot = control normal rate - target normal rate; bootstrap (2,000) for z of the bridge excess and of
(bridge excess - ending excess).
Run: .venv/bin/python experiments/e077_label_oddness.py
"""
from __future__ import annotations

import json, random, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
OUT = ROOT / "experiments/results/e077.json"
SEED, BOOT, Z_BAR = 77077, 2000, 3.0


def log(*a):
    print(*a, flush=True)


def lists(types):
    fr, en = Counter(), Counter()
    for w in types:
        for k in (1, 2, 3):
            if len(w) > k:
                fr[w[:k]] += 1
        for k in (1, 2, 3, 4):
            if len(w) > k:
                en[w[-k:]] += 1
    return [p for p, _ in fr.most_common(10)], [p for p, _ in en.most_common(20)]


def cut(w, F, E):
    f = max((p for p in F if w.startswith(p) and len(p) < len(w)), key=len, default="")
    rest = w[len(f):]
    e = max((p for p in E if rest.endswith(p) and len(p) < len(rest)), key=len, default="")
    return f, rest[:len(rest) - len(e)], e


def known_bridges(types, F, E):
    c = Counter(cut(w, F, E)[1] for w in types)
    return {b for b, n in c.items() if n >= 3 and b}


def rates(words, F, E, KB):
    cs = [cut(w, F, E) for w in words]
    return np.array([[f != "", e != "", m in KB] for f, m, e in cs], float)


def matched_control(target, pool, rng):
    byL = defaultdict(list)
    for w in pool:
        byL[len(w)].append(w)
    out = []
    for w in target:
        L = len(w); d = 0
        while not (byL.get(L + d) or byL.get(L - d)) and d < 20:
            d += 1
        cand = byL.get(L + d, []) + (byL.get(L - d, []) if d else [])
        out.append(rng.choice(cand))
    return out


def compare(target, pool_types, ordinary_types, rng):
    F, E = lists(ordinary_types)
    KB = known_bridges(ordinary_types, F, E)
    ctrl = matched_control(target, pool_types, rng)
    T, C = rates(target, F, E, KB), rates(ctrl, F, E, KB)
    exc = C.mean(0) - T.mean(0)            # front, ending, bridge
    nr = np.random.default_rng(SEED)
    bs = []
    for _ in range(BOOT):
        ti = nr.integers(0, len(T), len(T)); ci = nr.integers(0, len(C), len(C))
        bs.append(C[ci].mean(0) - T[ti].mean(0))
    bs = np.array(bs)
    sd = np.maximum(bs.std(0, ddof=1), 1e-9); dsd = max((bs[:, 2] - bs[:, 1]).std(ddof=1), 1e-9)
    return {"n": len(target), "target_normal": dict(zip(["front", "ending", "bridge"], T.mean(0).round(4).tolist())),
            "control_normal": dict(zip(["front", "ending", "bridge"], C.mean(0).round(4).tolist())),
            "excess": dict(zip(["front", "ending", "bridge"], exc.round(4).tolist())),
            "z_bridge": float(exc[2] / sd[2]), "z_ending": float(exc[1] / sd[1]),
            "z_bridge_minus_ending": float((exc[2] - exc[1]) / dsd),
            "lists": {"front": F, "ending": E}, "examples": [(w, cut(w, F, E)) for w in target[:15]]}


def reading(r):
    if r["z_bridge"] > Z_BAR and r["z_bridge_minus_ending"] > Z_BAR:
        return "NAME-LIKE (odd in the bridge)"
    if r["z_ending"] > Z_BAR or r["z_bridge"] > Z_BAR:
        return "ODD EVERYWHERE"
    return "NOT ODD"


def latin():
    from e027_simple_syllables import bible_text
    t = unicodedata.normalize("NFC", bible_text("latVUC"))
    toks = re.findall(r"[^\W\d_]+|[.:;!?]", t)
    cap, low, mid = Counter(), Counter(), Counter()
    prev = "."
    for x in toks:
        if x in ".:;!?":
            prev = "."; continue
        if x[0].isupper():
            cap[x.lower()] += 1
            if prev != "." and not x.isupper():
                mid[x.lower()] += 1
        else:
            low[x] += 1
        prev = x
    names = sorted(w for w in mid if w not in low and mid[w] >= 1 and len(w) >= 3)
    nameset = set(names)
    seq = [x.lower() for x in toks if x not in ".:;!?" and not x.isupper()]
    tokfreq = Counter(seq)
    name_tokens = [w for w in seq if w in nameset]
    ordinary = sorted(w for w in tokfreq if w not in nameset)
    rare = [w for w in ordinary if tokfreq[w] <= 2]
    return name_tokens, rare, ordinary, len(names)


def voynich():
    from vcl.corpus.ivtff import parse
    from vcl.corpus.splits import locked_test_leaves
    _, toks = parse()
    locked = set(locked_test_leaves(toks))
    dev = [t for t in toks if t.leaf not in locked and t.is_clean]
    pf = Counter(t.eva for t in dev if t.mode == "prose")
    labels = [t.eva for t in dev if t.mode == "label"]
    ordinary = sorted(pf)
    rare = [w for w in ordinary if pf[w] <= 2]
    return labels, rare, ordinary, sorted(locked, key=lambda x: (len(x), x)), Counter(t.illustration for t in dev if t.mode == "label")


def main():
    rng = random.Random(SEED)
    res = {"experiment": "E077"}
    nt, rare, ordinary, nn = latin()
    r = compare(nt, rare, ordinary, rng); r["name_types"] = nn; res["latin_names"] = r
    log(f"[known answer] Latin names: {nn} types, {r['n']} tokens | normal rates names {r['target_normal']} rare words {r['control_normal']}")
    log(f"  excess oddness {r['excess']} | z bridge {r['z_bridge']:+.2f} ending {r['z_ending']:+.2f} bridge-minus-ending {r['z_bridge_minus_ending']:+.2f} -> {reading(r)}")
    log(f"  examples {r['examples'][:10]}")
    valid = reading(r).startswith("NAME-LIKE")
    labels, vrare, vord, locked, sec = voynich()
    v = compare(labels, vrare, vord, rng); res["voynich_labels"] = v; res["locked_test_excluded"] = locked; res["label_sections"] = dict(sec)
    log(f"[VOYNICH] labels {v['n']} tokens | normal rates labels {v['target_normal']} rare prose words {v['control_normal']}")
    log(f"  excess oddness {v['excess']} | z bridge {v['z_bridge']:+.2f} ending {v['z_ending']:+.2f} bridge-minus-ending {v['z_bridge_minus_ending']:+.2f} -> {reading(v)}")
    log(f"  examples {v['examples'][:12]}")
    res.update(validated=valid, verdict=reading(v) if valid else "VOID")
    log(f"VERDICT {res['verdict']} (known answer {'passed' if valid else 'failed'})")
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
