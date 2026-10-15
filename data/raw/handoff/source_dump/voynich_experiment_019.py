"""Experiment 019: compare manuscript and two null generators across multiple diagnostics.
NOTE: nulls preserve line layout, do not simulate historical manuscript production.
Source: locally uploaded ZL3b IVTFF EVA DOCX. Only unambiguous parsed paragraph text.
"""
import re,collections,random,json,contextlib,io,math
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
    source=Path('/mnt/data/voynich_full_experiment_014.py').read_text().split('# JS divergence')[0]
    env={};exec(compile(source,'existing_parser','exec'),env)

def ed1(a,b):
    if abs(len(a)-len(b))>1:return False
    if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
    if len(a)>len(b):a,b=b,a
    i=j=diff=0
    while i<len(a) and j<len(b):
        if a[i]==b[j]: i+=1;j+=1
        else:diff+=1;j+=1
        if diff>1:return False
    return True

def tv(x,y):
    a=sum(x.values());b=sum(y.values())
    return .5*sum(abs(x[k]/a-y[k]/b) for k in x.keys()|y.keys()) if a and b else None

def calc(lines):
    lines=[r['tokens'] for r in lines if len(r['tokens'])>=3]
    words=[w for line in lines for w in line]
    n=len(words);freq=collections.Counter(words)
    adjacent=[(a,b) for line in lines for a,b in zip(line,line[1:])]
    first=collections.Counter(w[:1] for line in lines for w in line[:1]);interior=collections.Counter(w[:1] for line in lines for w in line[1:])
    repeats=sum(a==b for a,b in adjacent)/len(adjacent)
    oneedit=sum(ed1(a,b) for a,b in adjacent)/len(adjacent)
    suffix=collections.Counter(w[-2:] for w in words if len(w)>=3)
    # share of tokens from vocabulary observed at least twice
    return dict(tokens=n, lines=len(lines),types=len(freq),type_token=round(len(freq)/n,4),
        repeated_neighbor=round(repeats,4),one_edit_neighbor=round(oneedit,4),
        line_start_initial_TV=round(tv(first,interior),4),
        suffix_top5_mass=round(sum(v for _,v in suffix.most_common(5))/sum(suffix.values()),4),
        repeated_type_token_mass=round(sum(v for v in freq.values() if v>=2)/n,4))

def generate(lines,mode,seed):
    rng=random.Random(seed); words=[w for r in lines for w in r['tokens']]
    letter_counts=collections.Counter(''.join(words));chars=list(letter_counts);weights=list(letter_counts.values())
    def mutate(w):
        w=list(w);op=rng.choice(['sub','insert','delete'])
        if op=='sub':w[rng.randrange(len(w))]=rng.choices(chars,weights)[0]
        elif op=='insert':w.insert(rng.randrange(len(w)+1),rng.choices(chars,weights)[0])
        elif len(w)>1:w.pop(rng.randrange(len(w)))
        return ''.join(w)
    ret=[]
    for r in lines:
        line=[]
        for i in range(len(r['tokens'])):
            if mode=='copy_mutate' and i and rng.random()<.65:
                w=mutate(line[-1])
            else:w=rng.choice(words)
            line.append(w)
        ret.append({'tokens':line})
    return ret

out={'description':'Five diagnostics across genuine Voynich and two synthetic nulls; sample parsed without ambiguous glyphs; artificial parameters chosen beforehand; no claim to identify meaning.','groups':{}}
for g in 'AB':
    lines=env['groups'][g]
    d={'real':calc(lines)}
    for mode in ['iid','copy_mutate']:
        d[mode]=[calc(generate(lines,mode,seed)) for seed in [7,13,29]]
    out['groups'][g]=d
    print(g,json.dumps(d),flush=True)
Path('/mnt/data/voynich_experiment_019_results.json').write_text(json.dumps(out,indent=2))
