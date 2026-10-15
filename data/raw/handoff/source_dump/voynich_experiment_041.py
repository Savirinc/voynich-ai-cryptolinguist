"""Held-out Taurus: do position-conditioned EVA components learned from Pisces/Aries predict Taurus?"""
import pandas as pd, numpy as np, re, json
from collections import Counter
p='/mnt/data/voynich_zodiac_slot_map.csv'
df=pd.read_csv(p)
df['slot']=df.groupby('sign',sort=False).cumcount().add(1)
df=df[df.sign.isin(['Pisces','Aries','Taurus'])].copy()
df['clean']=df.voynich_label.astype(str).str.fullmatch('[a-z]+')
train=df[(df.sign!='Taurus')&df.clean]
test=df[(df.sign=='Taurus')&df.clean].copy()
rng=np.random.default_rng(4119)
results={}
for feat in ['prefix1','prefix2','suffix2','length_bucket']:
 def transform(w):
  if feat=='prefix1':return w[:1]
  if feat=='prefix2':return w[:2]
  if feat=='suffix2':return w[-2:]
  return str(min(len(w)//3,5))
 tr=train.assign(cat=train.voynich_label.map(transform))
 te=test.assign(cat=test.voynich_label.map(transform))
 cats=set(tr.cat)|set(te.cat); vocab=len(cats); globalcount=Counter(tr.cat)
 # likelihood from nearby recorded positions; shrink towards global priors. NOT a learned cipher.
 def likelihood(slot,cat):
  close=tr[abs(tr.slot-slot)<=2]
  numerator=sum(close.cat==cat)+2*(globalcount[cat]+1)/(len(tr)+vocab)
  denominator=len(close)+2
  return numerator/denominator
 slots=te.slot.to_numpy(); vals=te.cat.tolist()
 pred=np.array([[np.log(likelihood(s,v)) for v in vals] for s in slots])
 observed=float(np.mean(np.diag(pred)))
 null=np.array([float(np.mean(pred[np.arange(len(vals)), rng.permutation(len(vals))])) for _ in range(5000)])
 results[feat]={'n_test':len(te),'mean_log_probability':observed,'shuffled_mean':float(null.mean()),'difference':float(observed-null.mean()),'shuffle_95_pct':np.quantile(null,[.025,.975]).tolist(),'p_better_than_shuffle':float((1+np.sum(null>=observed))/(len(null)+1))}
result={'experiment':41,'train_signs':['Pisces','Aries'],'held_out_sign':'Taurus','train_clean':len(train),'test_clean':len(test),'original_sign_label_counts':df.groupby('sign').size().to_dict(),'method':'Position-conditioned category likelihood from Pisces and Aries (slot +/-2), tested on Taurus EVA categories. Permutations randomly reassign Taurus labels to slots. Provisional transcription order, not validated degree order. 5000 shuffles per feature.','metrics':results,'limitations':['No decipherment or translations are inferred','Provisional label order is not verified zodiac-degree order','Small sample and multiple tested features','A negative result does not eliminate unknown language/complex cipher']}
with open('/mnt/data/voynich_experiment_041_results.json','w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
