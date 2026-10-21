import sys, random, pickle, numpy as np
from collections import Counter
import syl_pipe as P, latseg
H = pickle.load(open(latseg.X + "latlib_hold.pkl", "rb"))["calib"]; fs = sorted(H)
words = H[fs[1]][2000:2000 + 28841]; rng = random.Random(1)
codes = P.make_table(Counter(s for w in words for s in P.syllables(w)), rng); cw, truth = P.encrypt(words, codes, rng)
tl = {w: ls for w, (_, ls) in zip(cw, truth)}
for alpha in (1.0, 30.0, 300.0, 3000.0):
    seg = P.seg_gibbs(list(Counter(cw)), alpha=alpha, seed=1)
    acc = np.mean([[len(c) for c in seg[w]] == tl[w] for w in cw])
    cpw = np.mean([len(seg[w]) for w in cw])
    print(f"alpha {alpha}: word-exact {acc:.3f}; chunks/word {cpw:.2f} (true {np.mean([len(t) for t in tl.values()]):.2f}); chunk types {len(set(c for w in cw for c in seg[w]))} (true {len(codes)})", flush=True)
