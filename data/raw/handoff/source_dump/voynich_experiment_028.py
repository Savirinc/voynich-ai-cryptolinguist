import pandas as pd, numpy as np, re, json
from itertools import combinations
from pathlib import Path
D=Path('/mnt/data')
x=pd.read_csv(D/'voynich_zodiac_slot_map.csv').fillna({'ring':'unspecified'})
r=pd.read_csv(D/'voynich_historical_zodiac_reference_027.csv')
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Pisces']
# only unambiguous single-token labels for straightforward morphology tests.
x['valid']=x.voynich_label.apply(lambda s:bool(re.fullmatch('[a-z]+',str(s))))
x['folio_order']=x.folio.apply(lambda s: int(re.search(r'\d+',s).group()))
x['side']=x.folio.apply(lambda s: 0 if 'r' in s else 1)
# Ring-order variants are hypotheses, not confirmed reading orders.
ring_priorities={'outer_first':{'outer':0,'middle':1,'inner':2,'unspecified':0},'inner_first':{'inner':0,'middle':1,'outer':2,'unspecified':0}}
def ordered(sign,mode,reverse=False):
    y=x[x.sign==sign].copy()
    if mode=='record': y=y.sort_values(['folio_order','side','transcription_order'])
    else:
        y['ring_idx']=y.ring.map(ring_priorities[mode]);y=y.sort_values(['folio_order','side','ring_idx','angle_deg_clockwise_from_top','record'])
    if reverse:y=y.iloc[::-1]
    y=y.copy();y['slot']=np.arange(len(y))
    return y
# One-to-one provisional slot->degree mapping; absent labels (29 vs 30) are not repaired.
def compute(mode,reverse=False,seed=1,B=2000):
    frames=[ordered(s,mode,reverse) for s in SIGNS]
    d=pd.concat(frames,ignore_index=True)
    # mapping from sign/degree to historical rulers
    d=d.merge(r[['sign','degree_index_0_29','chaldean_decan_ruler','egyptian_bound_ruler_verified_4_signs_only']],left_on=['sign','slot'],right_on=['sign','degree_index_0_29'],how='left')
    d=d[d.valid].reset_index(drop=True)
    n=len(d); idx_i,idx_j=np.triu_indices(n,1)
    across=(d.sign.to_numpy()[idx_i]!=d.sign.to_numpy()[idx_j])
    ii=idx_i[across]; jj=idx_j[across]
    tokens=d.voynich_label.to_numpy(); a=d.chaldean_decan_ruler.to_numpy()
    # only across signs, and comparative pair probability; null rotates within each sign
    feats={'first_glyph':np.array([t[:1] for t in tokens]),'first_two_EVA':np.array([t[:2] for t in tokens]),'last_two_EVA':np.array([t[-2:] for t in tokens])}
    matches={k:(v[ii]==v[jj]) for k,v in feats.items()}
    rng=np.random.default_rng(seed)
    group_indices=[np.where(d.sign.to_numpy()==s)[0] for s in SIGNS]
    def stat(a,v):
        same=(a[ii]==a[jj]); other=~same
        return float(v[same].mean()-v[other].mean()),int(same.sum())
    out={}
    for k,v in matches.items():
        obs,npairs=stat(a,v)
        vals=[]
        for _ in range(B):
            aa=a.copy()
            # rotate ruler assignments within sign; preserves ruler distribution and label sequence
            for inds in group_indices:
                aa[inds]=np.roll(a[inds],rng.integers(len(inds)))
            vals.append(stat(aa,v)[0])
        vals=np.array(vals)
        out[k]={'effect_pp':round(100*obs,3),'same_ruler_pairs':npairs,'null_avg_effect_pp':round(100*vals.mean(),3),'null_95pct_effect_pp':[round(float(q)*100,3) for q in np.quantile(vals,[0.025,0.975])],'p_two_sided':round(float((1+np.sum(np.abs(vals)>=abs(obs)))/(B+1)),4),'p_positive':round(float((1+np.sum(vals>=obs))/(B+1)),4)}
    return {'labels_usable':len(d),'folio_panels':int(d.folio.nunique()),'mode':mode,'reverse':reverse,'tests':out}
if __name__=='__main__':
    variants=[('record',False),('record',True),('outer_first',False),('inner_first',False)]
    res={'method':'Cross-sign label-morphology agreement conditional on traditional Chaldean decan rulers; provisional slot order, permutations cyclically rotate decan rulers within sign. No chart epoch involved.', 'variants':[compute(m,rev,seed=2026+i,B=1000) for i,(m,rev) in enumerate(variants)]}
    (D/'voynich_experiment_028_results.json').write_text(json.dumps(res,indent=2))
    for v in res['variants']:
        print(v['mode'],v['reverse'],v['labels_usable'],[(k,t['effect_pp'],t['p_positive']) for k,t in v['tests'].items()])
