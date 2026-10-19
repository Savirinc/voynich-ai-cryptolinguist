import random, math, numpy as np, sys
from collections import Counter
from latseg import seg, words_of
from segment import make_codes, GL
import seg_gibbs
mode = sys.argv[1]; a_s, a_f = 1.0, float(sys.argv[2])
plain = words_of("la", "tune")[:24000]; sp = [seg(w) for w in plain]
rng = random.Random(11011); taken = set()
EG, SG = (GL[:6], GL[6:]) if mode == "marked" else (GL, GL)
ecode = make_codes(sorted({e for _, e in sp if e}), 1, 3, rng, taken, EG); ecode[""] = ""
scode = make_codes(sorted({s for s, _ in sp}), 2, 5, rng, taken, SG)
cipher = [scode[s] + ecode[e] for s, e in sp]
truth = {}
for (s, e) in sp: truth[scode[s] + ecode[e]] = len(scode[s])
types = list(Counter(cipher))
p_stop, ng = 0.3, len(GL)
def lp0(x): return len(x) * (math.log(1/ng) + math.log(1 - p_stop)) + math.log(p_stop)
def joint(split):
    tot = 0.0
    for parts, a in (([w[:split[w]] for w in types], a_s), ([w[split[w]:] for w in types], a_f)):
        c = Counter(parts); N = len(parts)
        tot += sum(math.log(a) + lp0(x) + math.lgamma(n) for x, n in c.items()) - (math.lgamma(a + N) - math.lgamma(a))
    return tot
found = seg_gibbs.gibbs_segment2(types, a_s=a_s, a_f=a_f, init=sys.argv[3], smooth=float(sys.argv[4]), t0=float(sys.argv[5]))
print("truth joint", round(joint(truth)), "found joint", round(joint(found)))
print("stems/suffixes truth", len({w[:truth[w]] for w in types}), len({w[truth[w]:] for w in types}),
      "found", len({w[:found[w]] for w in types}), len({w[found[w]:] for w in types}))
err = Counter()
for w in cipher:
    t, f = truth[w], found[w]
    if t != f: err[("null-split" if t == len(w) else "missed" if f == len(w) else "wrong-len")] += 1
print("token errors", {k: round(v / len(cipher), 3) for k, v in err.items()})
