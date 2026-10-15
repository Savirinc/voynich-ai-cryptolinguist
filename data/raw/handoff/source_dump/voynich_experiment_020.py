"""Experiment 020: paragraph-start versus ordinary line-start versus line-end.
Data: user supplied ZL3b 2025 IVTFF DOCX. Conservative regex parsed EVA words.
Within-line shuffle control retains every line's word inventory, paragraph marker, language.
"""
from docx import Document
from collections import Counter,defaultdict
import re,random,json
source='/mnt/data/IVTFF Eva.txt.docx'
rows=[p.text.strip() for p in Document(source).paragraphs]
header=re.compile(r'^<(f\d+[rv]\d?)>\s+<!([^>]*)>')
locus=re.compile(r'^<(f\d+[rv]\d?\.\d+),([^>]*)>\s*(.*)')
meta={}; current=None; records=[]
for s in rows:
 h=header.match(s)
 if h:
  fol=h.group(1);meta[fol]=dict(re.findall(r'\$(\w)=([^\s>]+)',h.group(2)));current=None;continue
 m=locus.match(s)
 if m:
  fol=m.group(1).split('.')[0]
  if fol in meta:
   current={'folio':fol,'loc':m.group(2),'raw':m.group(3)};records.append(current)
 elif current is not None and s and not s.startswith('#'):
  current['raw']+=' '+s
lines=[]
for r in records:
 if 'P' not in r['loc'] or meta[r['folio']].get('L') not in ['A','B']:continue
 raw=r['raw']; par='<%>' in raw or r['loc'].startswith(('@P','*P'))
 raw=re.sub(r'<!.*?>',' ',raw)
 raw=re.sub(r'<[^>]*>',' ',raw)
 raw=re.sub(r'\{[^}]*\}|\[[^]]*\]|@\d+;','?',raw)
 words=[w for w in re.split(r'[.,\s]+',raw) if re.fullmatch(r'[a-z]+',w)]
 if len(words)>=3:lines.append({'lang':meta[r['folio']]['L'],'folio':r['folio'],'par':par,'words':words})
def tv(a,b):
 a=Counter(a);b=Counter(b);na=sum(a.values());nb=sum(b.values())
 return .5*sum(abs(a[k]/na-b[k]/nb) for k in a.keys()|b.keys())
def metrics(ls):
 par=[r['words'][0][0] for r in ls if r['par']]
 reg=[r['words'][0][0] for r in ls if not r['par']]
 mid=[w[0] for r in ls for w in r['words'][1:-1]]
 end=[r['words'][-1][0] for r in ls]
 suf_par=[r['words'][0][-2:] for r in ls if r['par']]
 suf_reg=[r['words'][0][-2:] for r in ls if not r['par']]
 return {'paragraph_start_vs_ordinary_start':tv(par,reg),'ordinary_start_vs_interior':tv(reg,mid),'line_end_vs_interior':tv(end,mid),'paragraph_start_suffix_vs_ordinary_start':tv(suf_par,suf_reg)}
rng=random.Random(20261011)
out={'method':'EVA character initial comparisons and suffix comparisons; paragraph flags from <%> or @P/*P; line-level shuffle null preserves line token inventory; multiple exploratory tests; non-independent text units; avoid grammar claims','groups':{}}
for lang in 'AB':
 ls=[r for r in lines if r['lang']==lang]
 obs=metrics(ls)
 sims={k:[] for k in obs}
 for i in range(500):
  perm=[{**r,'words':rng.sample(r['words'],len(r['words']))} for r in ls]
  m=metrics(perm)
  for k,v in m.items():sims[k].append(v)
 out['groups'][lang]={'line_count':len(ls),'paragraph_start_count':sum(r['par'] for r in ls),'folios':len(set(r['folio'] for r in ls)),'comparisons':{k:{'observed_tv':round(v,4),'null_mean_tv':round(sum(sims[k])/len(sims[k]),4),'p_ge_obs':round((1+sum(z>=v for z in sims[k]))/(len(sims[k])+1),4)} for k,v in obs.items()}}
print(json.dumps(out,indent=2))
with open('/mnt/data/voynich_experiment_020_results.json','w') as f:json.dump(out,f,indent=2)
