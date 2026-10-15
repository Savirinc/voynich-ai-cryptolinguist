"""Audit zodiac labels: does a repeated word preserve ordinal slot across different signs?
Uses transcription order only, no unverified celestial coordinate assumptions.
"""
import pandas as pd, numpy as np, json, re
from itertools import combinations
p='/mnt/data/voynich_zodiac_slot_map.csv'
df=pd.read_csv(p)
df=df[df.voynich_label.astype(str).str.fullmatch('[a-z]+')].copy()
# Slots from original 298 records, NOT recounted after filtering ambiguous words.
all_df=pd.read_csv(p)
all_df['slot']=all_df.groupby('sign',sort=False).cumcount()
df=df.merge(all_df[['folio','record','slot']],on=['folio','record'],validate='one_to_one')
# Only cross-sign exact word recurrences.
grp=df.groupby('voynich_label')
shared={w:g[['sign','slot']].to_dict('records') for w,g in grp if g.sign.nunique()>1}
observed=[]
for w,rows in shared.items():
    for a,b in combinations(rows,2):
        if a['sign']==b['sign']:continue
        diff=abs(a['slot']-b['slot'])
        observed.append((w,a['sign'],b['sign'],a['slot'],b['slot'],diff))
obs=np.mean([t[-1]<=2 for t in observed]); exact=np.mean([t[-1]==0 for t in observed])
# Rotate slots per sign, preserving every within-sign ordering and string identity.
rng=np.random.default_rng(3030)
by_sign={s:g.index.to_numpy() for s,g in df.groupby('sign')}
arr_word=df.voynich_label.to_numpy(); signs=df.sign.to_numpy(); slots=df.slot.to_numpy()
# Use shared cross-sign occurrence pairs indices
pairs=[]
for w in shared:
    ix=np.where(arr_word==w)[0]
    for i,j in combinations(ix,2):
        if signs[i]!=signs[j]:pairs.append((i,j))
ii,jj=np.array(pairs).T
null=[]
for b in range(5000):
    shifted=slots.copy()
    for s,ids in by_sign.items():shifted[ids]=(slots[ids]+rng.integers(30))%30
    null.append(np.mean(np.abs(shifted[ii]-shifted[jj])<=2))
null=np.array(null)
pval=(1+(null>=obs).sum())/(len(null)+1)
result={
'source':p,'usable_labels':int(len(df)),'shared_across_sign_exact_forms':len(shared),'cross_sign_identical_word_pairs':len(observed),
'observed_within_two_provisional_slots':float(obs),'observed_same_provisional_slot':float(exact),
'cyclic_shift_null_mean':float(null.mean()),'cyclic_shift_null_95_interval':[float(x) for x in np.quantile(null,[.025,.975])],
'one_sided_p':float(pval),
'examples_closest':[{'word':w,'sign_a':a,'sign_b':b,'slot_a':int(c),'slot_b':int(d),'distance':int(delta)} for w,a,b,c,d,delta in sorted(observed,key=lambda z:z[-1])[:18]],
'caveat':'Transcription order is not independently established astronomical order. Only an ordinal control; no semantic identifications.'}
with open('/mnt/data/voynich_experiment_030_results.json','w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
