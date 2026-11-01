import sys, math, random
from collections import Counter, defaultdict
sys.path[:0] = ["src", "experiments"]
import numpy as np
import e117_surprise_map as X
import e093_explanation_model as E93
from vcl.corpus.ivtff import parse
from vcl.corpus.splits import locked_test_leaves
_, toks = parse(); locked = set(locked_test_leaves(toks))
# lines with paragraph-start flag, DEV prose
L, ps = defaultdict(list), {}
for t in toks:
    if t.mode == "prose" and t.leaf not in locked:
        k = (t.folio, t.line_no)
        if t.is_clean: L[k].append(t.eva)
        ps[k] = ps.get(k, False) or bool(t.para_start)
pages, meta, _ = E93.voynich()
S = X.surprisal(pages)
# map surprisal back by folio order
key = lambda f: (int("".join(c for c in f if c.isdigit()) or 0), f)
folios = sorted({k[0] for k in L}, key=key)
rows = defaultdict(list)
for f, e in zip(folios, S):
    ks = sorted([k for k in L if k[0] == f and L[k]], key=lambda k: k)
    ks = sorted(ks, key=lambda k: list(L).index(k)) if False else ks
    for i, (k, l) in enumerate(zip([k for k in L if k[0] == f and L[k]], e)):
        tag = "page-first" if i == 0 else ("para-first (mid-page)" if ps[k] else "other")
        rows[tag] += l[1:] if tag != "other" else l
for k, v in rows.items(): print(f"{k:24s} mean surprisal {np.mean(v):.2f} bits  n {len(v)}")
# page-unique share
def uniq(entries):
    df = Counter(w for e in entries for w in {w for l in e for w in l})
    h = r = nh = nr = 0
    for e in entries:
        f = [w for l in e for w in l]
        if len(f) < 30: continue
        hh = f[1:11]; rr = f[11:]
        h += sum(df[w] == 1 for w in hh); nh += len(hh); r += sum(df[w] == 1 for w in rr); nr += len(rr)
    return h / nh, r / nr
print("Voynich page-unique share head/rest %.3f / %.3f" % uniq(pages))
rng = random.Random(1)
N = sum(len(w) for p in pages for w in p)
c = X.take(X.culpeper_entries(), N, rng); print("Culpeper head/rest %.3f / %.3f" % uniq(c))
g = X.take(X.gen_entries(X.E100W / "err5_random_s15/generate/generated_text.txt"), N, rng); print("generator err5_random_s15 head/rest %.3f / %.3f" % uniq(g))
g = X.take(X.gen_entries(X.E100W / "default_s11/generate/generated_text.txt"), N, rng); print("generator default_s11 head/rest %.3f / %.3f" % uniq(g))
