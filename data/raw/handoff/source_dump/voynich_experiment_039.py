import pandas as pd,numpy as np,json,re
from itertools import combinations
x=pd.read_csv('/mnt/data/voynich_zodiac_slot_map.csv')
rings={}
for (folio,ring),g in x.groupby(['folio','ring']):
 g=g.sort_values(['angle_deg_clockwise_from_top','record'])
 rings[f'{folio}:{ring}']=(g.voynich_label.astype(str).tolist(),g.sign.iloc[0])
pairs=[]
for (a,(u,sa)),(b,(v,sb)) in combinations(rings.items(),2):
 if len(u)!=len(v) or len(u)<5 or sa==sb:continue
 pairs.append((a,b,u,v))
def score(u,v):
 valid=[(a,b) for a,b in zip(u,v) if re.fullmatch('[a-z]+',a) and re.fullmatch('[a-z]+',b)]
 return (sum(a[:2]==b[:2] for a,b in valid)/len(valid)) if len(valid)>=3 else np.nan
def best(u,v):
 scores=[score(u,list(np.roll(v[::-1] if flip else v,s))) for flip in (False,True) for s in range(len(v))]
 return max((q for q in scores if not np.isnan(q)),default=0)
obs=np.array([best(u,v) for _,_,u,v in pairs]); rng=np.random.default_rng(3939);null=[]
for n in range(1500):
 q=[best(list(rng.permutation(u)),list(rng.permutation(v))) for _,_,u,v in pairs]
 null.append(np.mean(q))
null=np.array(null)
result={'experiment':39,'change_from_038':'Preserve original ring lengths and spatial slots. Ambiguous tokens marked missing rather than deleted. Same-size ring pairs only, different signs. Optimize rotations/direction in both real and permuted controls.','pairs':len(pairs),'mean_optimized_prefix2_agreement':float(np.mean(obs)),'null_mean':float(null.mean()),'null_95pct':np.quantile(null,[.025,.975]).tolist(),'p_one_sided':float((1+sum(null>=np.mean(obs)))/(len(null)+1)),'pairs_data':[{'a':a,'b':b,'n':len(u),'observed_best':float(best(u,v))} for a,b,u,v in pairs],'caveats':['Still exploratory and rings may not map directly to degrees','Same ring size does not imply corresponding degree locations','No word meanings established']}
with open('/mnt/data/voynich_experiment_039_results.json','w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
