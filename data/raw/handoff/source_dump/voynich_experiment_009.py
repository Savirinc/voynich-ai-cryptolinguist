"""Experiment 009: sensitivity and controlled null comparisons on existing Voynich extracts.
Only samples, NOT whole manuscript. Bootstrap uses resampled words. Null shuffles
characters globally while preserving observed word lengths and unigram counts.
"""
import random,json,statistics,collections,math
from pathlib import Path
from voynich_experiment_008 import tokens,features,SOURCES,BASE
rng=random.Random(20261011)
words=[]
for s in SOURCES: words+=tokens((BASE/s).read_text(),voy=True)

def segment(word,groups):
    out=[];i=0
    while i<len(word):
        match=next((g for g in groups if word.startswith(g,i)),None)
        out.append(match or word[i]); i+=len(match) if match else 1
    return out

def hent(seq):
    pairs=collections.Counter(); prev=collections.Counter()
    for word in seq:
        for a,b in zip(word,word[1:]):pairs[(a,b)]+=1;prev[a]+=1
    n=sum(pairs.values())
    return -sum(v/n*math.log2(v/prev[a]) for (a,b),v in pairs.items()) if n else None

def calc(ws,groups=()):return hent([segment(w,groups) for w in ws])

def bootstrap(groups=(),b=500):
    vals=[calc([words[rng.randrange(len(words))] for _ in words],groups) for _ in range(b)]
    return [round(statistics.quantiles(vals,n=40)[0],4),round(statistics.quantiles(vals,n=40)[-1],4)]

def shuffle_null(groups=(),b=500):
    # Shuffle individual represented units globally, retaining lengths after segmenting.
    units=[segment(w,groups) for w in words]; lengths=list(map(len,units));pool=[x for u in units for x in u]
    vals=[]
    for _ in range(b):
        perm=pool[:];rng.shuffle(perm);i=0;sample=[]
        for n in lengths:sample.append(perm[i:i+n]);i+=n
        vals.append(hent(sample))
    return [round(statistics.mean(vals),4),round(min(vals),4),round(max(vals),4)]

cases={'eva_characters':(), 'ch_sh_as_single_units':('ch','sh'), 'ch_sh_ck_ct_ph_as_units':('ch','sh','ck','ct','ph')}
r={}
for name,groups in cases.items():
    observed=calc(words,groups); null=shuffle_null(groups)
    r[name]={'observed_H2':round(observed,4),'word_bootstrap_95pct_interval':bootstrap(groups),'shuffled_char_null_mean_min_max':null,'delta_vs_null_mean':round(observed-null[0],4)}
r['n_words']=len(words);r['source_files']=SOURCES;r['limitations']=['Not a medieval language comparison.','Sample is four early folios and contains selection/annotation effects.','Segmentation choices are hypothetical; no proof of correct glyph inventory.','Word bootstrap describes sample variation, not generalization to manuscript.','Shuffled-character null is intentionally simple and does not represent a natural-language alternative.']
(BASE/'voynich_experiment_009_results.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
