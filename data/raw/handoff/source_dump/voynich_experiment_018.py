"""Experiment 018: context prediction vs mechanical copy-mutate null.
Preserves number of folios, line lengths, and samples source vocabulary;
mechanical copies modify a word one glyph. Exploratory null, not a historical theory.
"""
import re,collections,random,json,contextlib,io
from pathlib import Path
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,log_loss
with contextlib.redirect_stdout(io.StringIO()):
    source=Path('/mnt/data/voynich_full_experiment_014.py').read_text().split('# JS divergence')[0]
    env={};exec(compile(source,'parser','exec'),env)

def extract(lines):
    pages=collections.defaultdict(list)
    for ln in lines:
        w=ln['tokens']
        if len(w)<3:continue
        for i in range(1,len(w)-1):
            if len(w[i])>=4:pages[ln['page']].append((w[i],w[i-1],w[i+1],i,len(w)))
    return pages

def evaluate(pages,group):
    folios=sorted(pages);random.Random(1701).shuffle(folios)
    trainset=set(folios[:int(len(folios)*.8)])
    train=[e for f in folios if f in trainset for e in pages[f]]
    test=[e for f in folios if f not in trainset for e in pages[f]]
    common=collections.Counter(e[0][-2:] for e in train)
    choices=set(w for w,_ in common.most_common(5))
    def target(e):return e[0][-2:] if e[0][-2:] in choices else 'OTHER'
    def feat(e,mode):
        w,l,r,i,n=e;stem=w[:-2]
        a={'stem='+stem:1,'stem_last='+stem[-1]:1,'stem_first='+stem[0]:1,'stem_length='+str(min(10,len(stem))):1}
        b={'left_word='+l:1,'right_word='+r:1,'left_init='+l[0]:1,'right_init='+r[0]:1,'position_bucket='+str(min(3,i)):1}
        return a if mode=='stem' else (b if mode=='context' else dict(a,**b))
    y=[target(e) for e in train];z=[target(e) for e in test]
    ans={'train':len(train),'test':len(test),'majority':round(sum(t==collections.Counter(y).most_common(1)[0][0] for t in z)/len(z),4)}
    for mode in ['stem','combined','context']:
        v=DictVectorizer();X=v.fit_transform([feat(e,mode) for e in train]);T=v.transform([feat(e,mode) for e in test]);c=LogisticRegression(max_iter=230,C=.3).fit(X,y)
        p=c.predict_proba(T)
        ans[mode]={'accuracy':round(accuracy_score(z,c.classes_[p.argmax(axis=1)]),4),'log_loss':round(log_loss(z,p,labels=c.classes_),4)}
    ans['context_gain_accuracy']=round(ans['combined']['accuracy']-ans['stem']['accuracy'],4)
    ans['context_gain_logloss']=round(ans['stem']['log_loss']-ans['combined']['log_loss'],4)
    return ans

def mechanical(lines,seed):
    rng=random.Random(seed)
    words=[w for ln in lines for w in ln['tokens'] if len(w)>=3]
    letters=collections.Counter(''.join(words));alphabet=list(letters);weights=list(letters.values())
    def mutate(word):
        chars=list(word);action=rng.choice(['replace','insert','delete'])
        if action=='replace':chars[rng.randrange(len(chars))]=rng.choices(alphabet,weights)[0]
        elif action=='insert':chars.insert(rng.randrange(len(chars)+1),rng.choices(alphabet,weights)[0])
        elif len(chars)>3:chars.pop(rng.randrange(len(chars)))
        return ''.join(chars)
    out=[]
    for ln in lines:
        new=[]
        for idx in range(len(ln['tokens'])):
            if new and rng.random()<.65:
                candidate=mutate(new[-1])
            else:candidate=rng.choice(words)
            new.append(candidate)
        out.append({'page':ln['page'],'tokens':new})
    return out
output={'description':'Observed versus word-copy/mutate generated controls; identical evaluation protocol; generated control retains folio and line lengths but is not frequency matched on output or conditioned on section.','groups':{}}
for g in ('A','B'):
    lines=env['groups'][g]
    obs=evaluate(extract(lines),g)
    mechanicals=[evaluate(extract(mechanical(lines,seed)),g) for seed in [101,202,303]]
    output['groups'][g]={'observed':obs,'mechanical_controls':mechanicals}
    print(g,'observed',obs['context_gain_accuracy'],obs['context_gain_logloss'],'mechanical',[(m['context_gain_accuracy'],m['context_gain_logloss']) for m in mechanicals],flush=True)
Path('/mnt/data/voynich_experiment_018_results.json').write_text(json.dumps(output,indent=2))
