"""Exploratory morphological families and adjacency contextual overlap; not a grammar decoder.
Data: local manually extracted ZL3b samples, sanitized strictly; f1r, f1v, f2r, f3r.
"""
from pathlib import Path
import re, collections, random, json
from itertools import combinations
P=Path(__file__).parent
files=['voynich_f1r_sample.txt','voynich_heldout_f1v_f2r.txt','voynich_f3r_reference.txt']
lines=[]
for fn in files:
 for s in (P/fn).read_text().splitlines():
  if not s or s.startswith('#'):continue
  s=re.sub(r'^<[^>]+>\s*','',s).replace('<->','.')
  toks=[w for w in re.split(r'[.,\s]+',s) if re.fullmatch('[a-z]+',w)]
  if len(toks)>1:lines.append(toks)
words=[w for line in lines for w in line]
freq=collections.Counter(words)
def edit1(a,b):
 if a==b or abs(len(a)-len(b))>1:return False
 if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
 if len(a)>len(b):a,b=b,a
 return any(a==b[:k]+b[k+1:] for k in range(len(b)))
# Only types occurring 2 or more times, for honest context comparisons.
types=[w for w,n in freq.items() if n>=2]
contexts=collections.defaultdict(set)
for ln in lines:
 for i,w in enumerate(ln):
  if i:contexts[w].add(('L',ln[i-1]))
  if i+1<len(ln):contexts[w].add(('R',ln[i+1]))
def jac(a,b):
 x,y=contexts[a],contexts[b]
 return len(x&y)/len(x|y) if x|y else 0
pairs=list(combinations(types,2))
near=[(a,b) for a,b in pairs if edit1(a,b)]
far=[(a,b) for a,b in pairs if not edit1(a,b)]
obs=sum(jac(a,b) for a,b in near)/len(near) if near else 0
rng=random.Random(12012026)
# Frequency-matched-ish baseline: generate random pairs from non-neighbors whose words
# occur in the same frequency bins as the near pairs. Matching frequency avoids the
# most obvious confound but sample size remains small.
def binf(w):return min(freq[w],5)
bins=collections.defaultdict(list)
for a,b in far:bins[tuple(sorted((binf(a),binf(b))))].append((a,b))
patterns=[tuple(sorted((binf(a),binf(b)))) for a,b in near]
controls=[]
for _ in range(2000):
 vals=[]
 for pat in patterns:
  if bins[pat]:
   a,b=rng.choice(bins[pat]);vals.append(jac(a,b))
 controls.append(sum(vals)/len(vals) if vals else 0)
p=(sum(v>=obs for v in controls)+1)/(len(controls)+1)
near_sorted=sorted(((a,b,round(jac(a,b),3)) for a,b in near),key=lambda x:x[2],reverse=True)
result={'lines':len(lines),'tokens':len(words),'unique_forms':len(freq),'repeated_types':len(types),
 'one_edit_pairs_among_repeated_types':len(near),'observed_context_jaccard':round(obs,5),
 'frequency_matched_non_near_null_mean':round(sum(controls)/len(controls),5),
 'one_sided_randomization_p':round(p,5),'top_pair_overlaps':near_sorted[:15],
 'caveats':['Tokens are drawn from simplified transcriptions of four opening folios, not full corpus.',
 'Word contexts are exact immediately neighboring words; sparse data yields low overlap.',
 'One edit apart does not demonstrate morphological relation; orthographic/cipher variants possible.',
 'Frequency-binned control is exploratory and not calibrated for manuscript-wide inference.',
 'Significant positional regularity would not itself imply natural-language grammar.']}
(P/'voynich_experiment_012_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
