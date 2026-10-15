"""Experiment 007: representation sensitivity and substitution invariance on local Voynich samples.
No decipherment or historical glyph identification is implied.
Run: python voynich_experiment_007.py
"""
from pathlib import Path
import collections, math, json, re, random
P=Path(__file__).resolve().parent
files=['voynich_f1r_sample.txt','voynich_heldout_f1v_f2r.txt','voynich_f3r_reference.txt']
tokens=[]
for f in files:
    for line in (P/f).read_text().splitlines():
        if line.startswith('#'):continue
        line=re.sub(r'^<[^>]+>\s*','',line)
        tokens += [w for w in re.split(r'[.,\s]+',line) if re.fullmatch('[a-z]+',w)]
# Two mechanically different representations: EVA Roman characters vs paired transliteration chunks.
# Neither is claimed to be a faithful manuscript-glyph segmentation.
def segment(w, paired=False):
    out=[]; i=0
    while i<len(w):
        if paired and w[i:i+2] in ('ch','sh'):
            out.append(w[i:i+2]);i+=2
        else:out.append(w[i]);i+=1
    return out

def metrics(ts):
    seq=[g for w in ts for g in w]
    cnt=collections.Counter(seq)
    pairs=collections.Counter((a,b) for w in ts for a,b in zip(w,w[1:]))
    prev=collections.Counter(a for (a,b),v in pairs.items() for _ in range(v))
    n=len(seq); np=sum(pairs.values())
    ic=sum(v*(v-1) for v in cnt.values())/(n*(n-1))
    h=-sum((v/np)*math.log2(v/prev[a]) for (a,b),v in pairs.items())
    return {'units':n,'unit_types':len(cnt),'within_word_transitions':np,'index_of_coincidence':round(ic,5),'conditional_entropy_bits':round(h,4),'top_units':cnt.most_common(10)}
char=[segment(w) for w in tokens]
paired=[segment(w,True) for w in tokens]
# Simple substitution is a bijection over symbols and therefore preserves these statistics.
rng=random.Random(408)
abc=sorted({g for w in char for g in w}); dest=abc.copy();rng.shuffle(dest); key=dict(zip(abc,dest))
sub=[[key[g] for g in w] for w in char]
report={'scope':{'files':files,'tokens':len(tokens),'folio_scope':'opening folios only, transcription-derived'},'EVA_character_units':metrics(char),'EVA_ch_sh_as_merged_units':metrics(paired),'random_bijective_substitution':{'invariants_equal':metrics(char)==metrics(sub),'metric_values':metrics(sub)},'limitations':['Merging ch/sh is a sensitivity analysis only: not a verified glyph segmentation.','Entropy is measured inside words; experiment 006 joined all words into a single string, so figures are not directly comparable.','Different symbol inventories can have different entropy values, and directly comparing raw bits per symbol can mislead.','No medieval language reference corpus or full Voynich corpus was used.']}
(P/'voynich_experiment_007_results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
