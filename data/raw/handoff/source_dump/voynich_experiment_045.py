import runpy,random,json,numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss,roc_auc_score
p=runpy.run_path('/mnt/data/voynich_experiment_044.py')
train=p['train']; held=p['held'];feature=p['features']
def test(mode,shuffle=False):
 def d(r):
  x=feature(r,False)
  if mode in ('pos','full'):x['line_start='+str(r[5])]=1
  if mode in ('prev','full'):
   pr=r[4];x.update({'prev_first='+pr[:2]:1,'prev_last='+pr[-2:]:1,'prev='+pr:1})
  return x
 v=DictVectorizer();X=v.fit_transform([d(r) for r in train]);T=v.transform([d(r) for r in held]);clf=LogisticRegression(C=.5,solver='liblinear',max_iter=250).fit(X,[r[3] for r in train]);pr=clf.predict_proba(T)[:,1];return (float(log_loss([r[3] for r in held],pr)),float(roc_auc_score([r[3] for r in held],pr)))
out={k:test(k) for k in ['stem','pos','prev','full']}
# Analyze preceding word itself: which beginnings show strongest variation, just descriptive
from collections import Counter,defaultdict
prev=defaultdict(Counter)
for r in train:
 if r[4]!='<BOS>':prev[r[4]][r[3]]+=1
freq=[(w,v[0],v[1],v[1]/sum(v.values())) for w,v in prev.items() if sum(v.values())>=15]
res={'n_train':len(train),'n_test':len(held),'tests':{k:{'logloss':round(v[0],4),'auc':round(v[1],4)} for k,v in out.items()},'preceding_words_high_q':sorted(freq,key=lambda x:x[3],reverse=True)[:8],'preceding_words_low_q':sorted(freq,key=lambda x:x[3])[:8]}
with open('/mnt/data/voynich_experiment_045_results.json','w') as f:json.dump(res,f,indent=2)
print(json.dumps(res,indent=2))
