import pandas as pd, numpy as np, itertools, json
x=pd.read_csv('/mnt/data/voynich_zodiac_slot_map.csv');a=x[x.folio=='f72r1'].copy();a['inner_tub']=a.ring.eq('inner');a['prefix2']=a.voynich_label.str[:2];a['starts_ot']=a.voynich_label.str.startswith('ot');a['starts_o']=a.voynich_label.str.startswith('o');a['length']=a.voynich_label.str.replace(r'[^a-z]','',regex=True).str.len()
res={'folio':'f72r1','feature_grounding':'inner 5 figures stand in tubs; outer 10 do not, as documented by Zandbergen; ring assignment from previously prepared provisional slot map','inner_labels':a[a.inner_tub].voynich_label.tolist(),'outer_labels':a[~a.inner_tub].voynich_label.tolist()}
for feat in ['starts_ot','starts_o','length']:
 vals=a[feat].to_numpy().astype(float); mask=a.inner_tub.to_numpy();obs=float(vals[mask].mean()-vals[~mask].mean());perm=[]
 for indices in itertools.combinations(range(15),5):
  m=np.zeros(15,dtype=bool);m[list(indices)]=True;perm.append(float(vals[m].mean()-vals[~m].mean()))
 perm=np.array(perm)
 res[feat]={'inner_mean':float(vals[mask].mean()),'outer_mean':float(vals[~mask].mean()),'difference':obs,'permutation_two_sided_p':float((np.abs(perm)>=abs(obs)-1e-10).mean())}
with open('/mnt/data/voynich_experiment_040_results.json','w') as f:json.dump(res,f,indent=2)
print(json.dumps(res,indent=2))
