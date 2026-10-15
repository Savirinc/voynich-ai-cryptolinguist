from docx import Document
from collections import Counter,defaultdict
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,roc_auc_score,accuracy_score
import re,random,json,numpy as np
P=Document('/mnt/data/IVTFF Eva.txt.docx').paragraphs
rows=[]
for p in P:
 m=re.match(r'^<(f\d+[rv])\.(\d+)[^>]*>\s*(.*)',p.text.strip(),re.I)
 if not m:continue
 ws=[w for w in re.split(r'[., ]+',m.group(3).split('<!')[0]) if re.fullmatch(r'[a-z]{2,20}',w)]
 if not ws:continue
 f=m.group(1)
 for i,w in enumerate(ws):
  if w.startswith('qo') or (w.startswith('o') and len(w)>2):
   stem=w[1:] if w.startswith('qo') else w
   if len(stem)<3:continue
   prev=ws[i-1] if i else '<BOS>'
   rows.append((f,w,stem,int(w.startswith('q')),prev,i==0))
folios=sorted(set(r[0] for r in rows));rng=random.Random(20261012);rng.shuffle(folios);test=set(folios[::5]);train=[r for r in rows if r[0] not in test];held=[r for r in rows if r[0] in test]
# heldout stem overlaps
seen=set(r[2] for r in train)
def features(r,context=False):
 f,w,stem,y,prev,bos=r
 d={'stem='+stem:1,'stem_initial='+stem[:2]:1,'stem_final='+stem[-2:]:1}
 if context:
  d.update({'prev_first='+prev[:2]:1,'prev_last='+prev[-2:]:1,'prev='+prev:1,'line_start='+str(bos):1})
 return d
def evaluate(context):
 v=DictVectorizer();X=v.fit_transform([features(r,context) for r in train]);T=v.transform([features(r,context) for r in held]);clf=LogisticRegression(C=.5,max_iter=250,solver='liblinear');clf.fit(X,[r[3] for r in train]);prob=clf.predict_proba(T)[:,1];y=np.array([r[3] for r in held]);return {'logloss':round(log_loss(y,prob),5),'auc':round(roc_auc_score(y,prob),5),'accuracy':round(accuracy_score(y,prob>=.5),5)},v,clf
b,v,c=evaluate(False);ext,_,_=evaluate(True)
y=np.array([r[3] for r in held]);baseline=float(np.mean([r[3] for r in train]));naive={'logloss':round(log_loss(y,np.full(len(y),baseline)),5),'auc':.5}
# context significance compare q probability stratified on previous words when stem repeated
ct=defaultdict(Counter)
for _,w,s,y,prev,bos in rows:ct[s][y]+=1
shared={s:x for s,x in ct.items() if x[0]>=5 and x[1]>=5}
# q overrepresented at word start?
bypos=defaultdict(Counter)
for f,w,s,y,prev,bos in rows:bypos['line_start' if bos else 'inside_line'][y]+=1
result={'train':len(train),'heldout':len(held),'heldout_folios':len(test),'q_fraction_train':baseline,'heldout_stem_seen_fraction':sum(r[2] in seen for r in held)/len(held),'models':{'constant':naive,'stem_only':b,'stem_plus_previous_word_and_line_position':ext},'shared_stems_with_at_least_five_each':len(shared),'most_common_shared_stems':[(s,ct[s][0],ct[s][1]) for s in sorted(shared,key=lambda s:sum(ct[s].values()),reverse=True)[:12]],'line_position':{k:dict(v) for k,v in bypos.items()},'caveat':'Predicts surface q prefix choice among o/qo words; not an interpretation or proof of a grammatical operator. Prefix choices can be script mechanics.'}
with open('/mnt/data/voynich_experiment_044_results.json','w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
