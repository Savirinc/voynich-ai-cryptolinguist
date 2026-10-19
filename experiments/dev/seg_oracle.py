import random, numpy as np
from collections import Counter, defaultdict
import latseg
from latseg import seg, words_of
from segment import make_codes, GL
plain = words_of("la", "tune")[:24000]; sp = [seg(w) for w in plain]
rng = random.Random(11011); taken = set()
ecode = make_codes(sorted({e for _, e in sp if e}), 1, 3, rng, taken); ecode[""] = ""
scode = make_codes(sorted({s for s, _ in sp}), 2, 5, rng, taken)
cipher = [scode[s] + ecode[e] for s, e in sp]; tb = [len(scode[s]) for s, _ in sp]
inv = set(ecode.values()); types = set(cipher)
def acc(f): return np.mean([f(w) == b for w, b in zip(cipher, tb)])
def longest(w):
    for k in (3, 2, 1):
        if len(w) - k >= 2 and w[-k:] in inv: return len(w) - k
    return len(w)
stem_forms = defaultdict(int)
for w in types:
    for k in range(0, 4):
        if len(w) - k >= 2 and w[len(w)-k:] in inv: stem_forms[w[:len(w)-k]] += 1
def reuse(w):
    opts = [len(w) - k for k in range(0, 4) if len(w) - k >= 2 and w[len(w)-k:] in inv]
    return max(opts, key=lambda b: (stem_forms[w[:b]], len(w) - b))
print("oracle inventory, longest match", acc(longest)); print("oracle inventory, most-reused stem", acc(reuse))
print("share of tokens with null ending", np.mean([e == "" for _, e in sp]))
sc = Counter(s for s, _ in set(sp)); print("tokens whose stem has >=2 forms", np.mean([sc[s] >= 2 for s, _ in sp]))
