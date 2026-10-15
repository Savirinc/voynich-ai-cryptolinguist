import pandas as pd,numpy as np,re,json
from collections import Counter
from difflib import SequenceMatcher
p='/mnt/data/voynich_zodiac_slot_map.csv';df=pd.read_csv(p)
df['slot']=df.groupby('sign',sort=False).cumcount()
df=df[df.voynich_label.astype(str).str.fullmatch('[a-z]+')].copy().reset_index(drop=True)
# compare exact ngram + prefix / suffix overlap, controls shuffle labels within sign preserving all word statistics
arr=df.voynich_label.tolist(); slots=df.slot.to_numpy(); signs=df.signs if False else df.sign.to_numpy()
pairs=[(i,j) for i in range(len(df)) for j in range(i+1,len(df)) if signs[i]!=signs[j] and slots[i]==slots[j]]
print('N labels',len(df),'N slot pairs',len(pairs),'signs',df.sign.nunique())
def metrics(words):
  a=np.array([words[i] for i,j in pairs],dtype=object);b=np.array([words[j] for i,j in pairs],dtype=object)
  return [np.mean(a==b),np.mean([x[:2]==y[:2] for x,y in zip(a,b)]),np.mean([x[-2:]==y[-2:] for x,y in zip(a,b)]),np.mean([SequenceMatcher(None,x,y).ratio() for x,y in zip(a,b)])]
obs=metrics(arr); rng=np.random.default_rng(37037); by={s:np.where(signs==s)[0] for s in set(signs)};null=[]
for k in range(1200):
  new=arr.copy()
  for s,idx in by.items():
    perm=rng.permutation(idx)
    for i,j in zip(idx,perm):new[i]=arr[j]
  null.append(metrics(new))
null=np.array(null)
res={'experiment':'037','method':'same provisional ordinal labels across different signs, compared with labels shuffled within each sign; 1200 iterations','usable_labels':len(df),'same_position_pairs':len(pairs),'metrics':['exact_word','same_2_prefix','same_2_suffix','sequence_similarity'], 'observed':obs,'null_mean':null.mean(axis=0).tolist(),'null_95percent':np.quantile(null,[.025,.975],axis=0).T.tolist(),'one_sided_p':((null>=np.array(obs)).sum(axis=0)+1).astype(float).tolist() if False else ((null>=np.array(obs)).sum(axis=0)+1).astype(float).astype(float).tolist(),'caveat':'Sequence order and ring start ambiguous; metrics dependent and exploratory.'}
res['one_sided_p']=[float((1+(null[:,k]>=obs[k]).sum())/(len(null)+1)) for k in range(4)]
print(json.dumps(res,indent=2));open('/mnt/data/voynich_experiment_037_results.json','w').write(json.dumps(res,indent=2))
