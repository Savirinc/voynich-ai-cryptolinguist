import pandas as pd,numpy as np,re,json
from collections import Counter
D=pd.read_csv('/mnt/data/voynich_zodiac_slot_map.csv').sort_values(['folio','transcription_order'])
D=D[D.voynich_label.notna() & ~D.ambiguous_label.fillna(True)].copy()
D['word']=D.voynich_label.str.lower()
D=D[D.word.str.fullmatch('[a-z]+')].copy()
# Test phase-locked recurring initial 1/2-glyph and final 2-glyph patterns at candidate periods 7 and 10.
# Compare mutual info to permutations of word-feature labels within folios to preserve lexical composition.
rng=np.random.default_rng(2601)
results={}
for length,side in [(1,'start'),(2,'start'),(2,'end')]:
    col=f'{side}_{length}'
    D[col]=D.word.str[:length] if side=='start' else D.word.str[-length:]
    counts=D[col].value_counts()
    D[col]=D[col].where(D[col].map(counts)>=4,'OTHER')
    for period in [7,10]:
        groups=[g.copy() for _,g in D.groupby('folio')]
        # phase is purely provisional transcription order within each folio
        phases=np.concatenate([np.arange(len(g))%period for g in groups])
        vals=np.concatenate([g[col].to_numpy() for g in groups]); keys={v:i for i,v in enumerate(sorted(set(vals)))}
        encoded=np.array([keys[v] for v in vals]);K=len(keys)
        def mi(v):
            a=np.zeros((period,K),float)
            np.add.at(a,(phases,v),1)
            p=a/a.sum();px=p.sum(axis=1,keepdims=True);py=p.sum(axis=0,keepdims=True)
            mask=p>0
            return float(np.sum(p[mask]*np.log2((p/(px@py))[mask])))
        obs=mi(encoded)
        null=[]
        for _ in range(1000):
            shuffled=np.concatenate([rng.permutation(encoded[a:b]) for a,b in zip(np.cumsum([0]+[len(g) for g in groups])[:-1],np.cumsum([len(g) for g in groups]))])
            null.append(mi(shuffled))
        results[f'{col}_period{period}']={'observed_MI_bits':obs,'null_mean':float(np.mean(null)),'null_sd':float(np.std(null)),'permutation_p':float((1+sum(x>=obs for x in null))/(len(null)+1)),'n':len(vals)}
print(json.dumps({'n_usable':len(D),'results':results},indent=2))
with open('/mnt/data/voynich_experiment_026_results.json','w') as f:json.dump({'n_usable':len(D),'results':results,'caveat':'Transcription order is not confirmed zodiac degree sequence, so negative results do not rule out planetary cycles. Feature tests exploratory and not corrected for multiple comparisons.'},f,indent=2)
