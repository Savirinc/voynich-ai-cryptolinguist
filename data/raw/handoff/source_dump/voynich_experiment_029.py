import pandas as pd,numpy as np,re,json
from pathlib import Path
P=Path('/mnt/data')
x=pd.read_csv(P/'voynich_zodiac_slot_map.csv')
r=pd.read_csv(P/'voynich_historical_zodiac_reference_027.csv')
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Pisces']
x['folio_order']=x.folio.str.extract(r'(\d+)').astype(int)
x['side']=x.folio.str.contains('v').astype(int)
frames=[]
for s in SIGNS:
 t=x[x.sign==s].sort_values(['folio_order','side','transcription_order']).copy()
 t['slot']=np.arange(len(t));frames.append(t)
d=pd.concat(frames).merge(r[['sign','degree_index_0_29','chaldean_decan_ruler']],left_on=['sign','slot'],right_on=['sign','degree_index_0_29'])
d=d[d.voynich_label.map(lambda x:bool(re.fullmatch('[a-z]+',str(x))))].copy()
d['prefix2']=d.voynich_label.str[:2]
# Cross-sign transfer of label feature to planetary ruler, Laplace-smoothed Naive Bayes.
# Evaluate held-out sign log probability of observed prefixes under planet-assigned learned distributions.
# Baseline model ignores planet and learns same features from train signs.
def score(df,ruler_col='chaldean_decan_ruler'):
 scores=[]
 for sign in SIGNS:
  train=df[df.sign!=sign];test=df[df.sign==sign]
  if len(test)<3:continue
  vocabulary=sorted(set(train.prefix2)|set(test.prefix2)); V=len(vocabulary)
  global_counts=train.prefix2.value_counts(); n=len(train)
  by=train.groupby(ruler_col).prefix2.value_counts()
  totals=train[ruler_col].value_counts()
  # fixed shrinkage prior of 5 tokens worth to global empirical distribution
  baseline={f:(global_counts.get(f,0)+1)/(n+V) for f in vocabulary}
  delta=[]
  for row in test.itertuples():
   ruler=getattr(row,ruler_col);f=row.prefix2
   p=(by.get((ruler,f),0)+5*baseline[f])/(totals.get(ruler,0)+5)
   delta.append(np.log(p)-np.log(baseline[f]))
  scores.append({'sign':sign,'n':len(test),'mean_log_gain_nats':float(np.mean(delta)),'positive_share':float(np.mean(np.array(delta)>0))})
 return scores
obs=score(d)
rng=np.random.default_rng(20261011); perms=[]
for i in range(400):
 z=d.copy()
 # shuffle whole ruler-to-prefix association within signs, leaves margins identical
 for sign in SIGNS:
  ids=z.index[z.sign==sign]
  z.loc[ids,'chaldean_decan_ruler']=rng.permutation(z.loc[ids,'chaldean_decan_ruler'].to_numpy())
 ss=score(z)
 perms.append(sum(q['mean_log_gain_nats']*q['n'] for q in ss)/sum(q['n'] for q in ss))
overall=sum(q['mean_log_gain_nats']*q['n'] for q in obs)/sum(q['n'] for q in obs)
arr=np.array(perms)
out={'scope':'Exploratory leave-one-zodiac-sign-out test; fixed transcription order previously selected among four; not a pre-registered blind validation.','labels':len(d),'n_signs':len(obs),'observed_mean_log_likelihood_gain_nats':overall,'control_mean_gain_nats':float(arr.mean()),'control_95pct':[float(v) for v in np.quantile(arr,[.025,.975])],'p_one_sided':float((1+sum(arr>=overall))/(len(arr)+1)),'per_sign':obs,'n_permutations':len(arr)}
(P/'voynich_experiment_029_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
