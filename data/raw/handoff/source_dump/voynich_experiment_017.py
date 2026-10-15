"""Held-out folio prediction of word final-two-character class. No semantic decoding."""
import contextlib,io,runpy,collections,random,json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
with contextlib.redirect_stdout(io.StringIO()):
    source=Path('/mnt/data/voynich_full_experiment_014.py').read_text().split('# JS divergence')[0]
    d={}
    exec(compile(source, 'voynich_parser.py', 'exec'), d)
random.seed(17)
rng=np.random.default_rng(17)
output={"dataset":"uploaded ZL3b docx; conservative parser from experiment 014", "task":"predict final 2 EVA characters of token from immediate word context, using folio holdout", "groups":{}}
for group in ['A','B']:
    lines=d['groups'][group]
    bypage=collections.defaultdict(list)
    for ln in lines:
        ws=ln['tokens']
        if len(ws)<3:continue
        for i in range(1,len(ws)-1):
            word=ws[i]
            if len(word)<4:continue
            bypage[ln['page']].append((word,ws[i-1],ws[i+1],i,len(ws)))
    folios=sorted(bypage)
    random.Random(1701).shuffle(folios)
    trainfolios=set(folios[:int(len(folios)*.8)])
    train=[ex for folio in folios if folio in trainfolios for ex in bypage[folio]]
    test=[ex for folio in folios if folio not in trainfolios for ex in bypage[folio]]
    endings=collections.Counter(w[-2:] for w,*_ in train)
    top=set(w for w,_ in endings.most_common(5))
    def target(ex):
        s=ex[0][-2:]
        return s if s in top else 'OTHER'
    classes=sorted(top|{'OTHER'})
    def context(ex):
        w,left,right,i,n=ex
        return {'left_word='+left:1,'right_word='+right:1,'left_init='+left[0]:1,'right_init='+right[0]:1,'position_bucket='+str(min(3,i)):1}
    def stem(ex):
        w=ex[0][:-2]
        return {'stem='+w:1,'stem_last='+w[-1]:1,'stem_first='+w[0]:1,'stem_length='+str(min(10,len(w))):1}
    def fit_predict(mode,shuffle=False):
        if mode=='context': extract=context
        elif mode=='stem':extract=stem
        else:extract=lambda e:dict(context(e),**stem(e))
        tr=train.copy();te=test.copy()
        if shuffle:
            # shuffle context assignments independently of the target, within training/test partitions
            tc=[context(e) for e in tr];vc=[context(e) for e in te]
            rng.shuffle(tc);rng.shuffle(vc)
            features_tr=tc;features_te=vc
        else:
            features_tr=[extract(e) for e in tr];features_te=[extract(e) for e in te]
        v=DictVectorizer();X=v.fit_transform(features_tr);Y=v.transform(features_te)
        y=[target(e) for e in tr];z=[target(e) for e in te]
        clf=LogisticRegression(max_iter=250, C=.3)
        clf.fit(X,y)
        p=clf.predict_proba(Y)
        return {'accuracy':round(accuracy_score(z,clf.classes_[p.argmax(axis=1)]),4),'log_loss':round(log_loss(z,p,labels=clf.classes_),4)}
    base=collections.Counter(target(e) for e in train)
    majority=base.most_common(1)[0][0]
    output['groups'][group]={'train_folios':len(trainfolios),'test_folios':len(folios)-len(trainfolios),'train_tokens':len(train),'test_tokens':len(test),'classes':classes,'baseline_majority_accuracy':round(sum(target(e)==majority for e in test)/len(test),4),'models':{m:fit_predict(m) for m in ['context','stem','combined']},'shuffled_context':fit_predict('context',True)}
print(json.dumps(output,indent=2))
Path('/mnt/data/voynich_experiment_017_results.json').write_text(json.dumps(output,indent=2))
