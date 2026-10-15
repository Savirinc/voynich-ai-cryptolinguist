"""Exp 016: context similarity of one-edit forms vs matched unrelated word pairs.
Exploratory observational analysis; does not establish grammatical relationships.
"""
import contextlib, io, runpy, collections, math, random, json, statistics
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
    d=runpy.run_path('/mnt/data/voynich_full_experiment_014.py')
rng=random.Random(16016)
def edit1(a,b):
    if abs(len(a)-len(b))>1:return False
    if len(a)==len(b):return sum(c!=e for c,e in zip(a,b))==1
    if len(a)>len(b):a,b=b,a
    i=j=0; miss=0
    while i<len(a) and j<len(b):
        if a[i]==b[j]:i+=1;j+=1
        else:j+=1;miss+=1
        if miss>1:return False
    return True

def cos(a,b):
    dot=sum(v*b.get(k,0) for k,v in a.items());
    norm=math.sqrt(sum(v*v for v in a.values())*sum(v*v for v in b.values()))
    return dot/norm if norm else 0

def contexts(g):
    counts=collections.Counter(); profile=collections.defaultdict(collections.Counter)
    for line in d['groups'][g]:
        ws=line['tokens']
        for i,w in enumerate(ws):
            counts[w]+=1
            # Neighbor first glyphs, a deliberately low-dimensional context representation.
            left='^' if i==0 else ws[i-1][0]
            right='$' if i==len(ws)-1 else ws[i+1][0]
            profile[w]['L:'+left]+=1
            profile[w]['R:'+right]+=1
    return counts,profile
out={'source':'Uploaded ZL3b manuscript transcription','method':'For each Currier group separately: contexts = first EVA glyph of preceding/following word, with line boundaries. Compare cosine similarity of edit-distance-1 word pairs to random pairs matched on length and frequency. Bootstrap random pair sets, 1500 replicates.', 'caveats':['EVA characters are not necessarily manuscript glyphs','word contexts may depend on spelling and topic, not grammar','baseline matching approximates frequency and length, but does not control all confounding','parser excludes uncertain tokens but may retain editorial fragments','hypothesis explored after inspecting manuscript; p-values are exploratory'], 'groups':{}}
for g in ('A','B'):
    c,prof=contexts(g)
    words=[w for w,n in c.items() if n>=15]
    editpairs=[]
    for i,a in enumerate(words):
        for b in words[i+1:]:
            if edit1(a,b) and max(c[a],c[b])/min(c[a],c[b])<=3:
                editpairs.append((a,b))
    scores=[cos(prof[a],prof[b]) for a,b in editpairs]
    # pool matched for length abs <=1, ratio <=3, non-edit
    pools={}
    for a,b in editpairs:
        target=(len(a)+len(b))/2
        fa,fb=sorted((c[a],c[b])); targf=math.sqrt(fa*fb)
        options=[]
        for x in words:
            if abs(len(x)-len(a))>1 or not (1/2<=c[x]/c[a]<=2):continue
            for y in words:
                if y==x or abs(len(y)-len(b))>1 or not (1/2<=c[y]/c[b]<=2):continue
                if edit1(x,y):continue
                options.append((x,y))
        pools[(a,b)]=options
    editpairs=[pair for pair in editpairs if pools[pair]]
    scores=[cos(prof[a],prof[b]) for a,b in editpairs]
    null=[]
    for _ in range(1500):
        null.append(statistics.mean(cos(prof[x],prof[y]) for pair in editpairs for x,y in [rng.choice(pools[pair])]))
    mean=statistics.mean(scores) if scores else None
    p=(1+sum(x>=mean for x in null))/(len(null)+1) if scores else None
    out['groups'][g]={'eligible_words':len(words),'edit1_pairs_compared':len(editpairs),'mean_cosine_edit1':round(mean,4) if mean is not None else None,'mean_matched_control':round(statistics.mean(null),4) if null else None,'p_one_sided':round(p,5) if p is not None else None, 'illustrative_pairs': [{'pair':[a,b], 'count':[c[a],c[b]],'cosine':round(cos(prof[a],prof[b]),3)} for a,b in sorted(editpairs,key=lambda pair:-sum(c[w] for w in pair))[:8]]}
print(json.dumps(out,indent=2))
Path('/mnt/data/voynich_experiment_016_results.json').write_text(json.dumps(out,indent=2))
