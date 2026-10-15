"""Experiment 013: morphology and line position across 4 manually extracted folios.
Exploratory, not a full corpus / decipherment. Standard tokens only.
"""
from pathlib import Path
from collections import Counter
import re,json,random,math
P=Path(__file__).parent
sources={'f1r':'voynich_f1r_sample.txt','f1v_f2r':'voynich_heldout_f1v_f2r.txt','f3r':'voynich_f3r_reference.txt'}
lines={}
for name,fn in sources.items():
 out=[]
 for s in (P/fn).read_text().splitlines():
  if not s.strip() or s.startswith('#'): continue
  s=re.sub(r'^<[^>]+>\s*','',s).replace('<->','.')
  t=[w for w in re.split(r'[.,\s]+',s) if re.fullmatch(r'[a-z]+',w)]
  if len(t)>=3:out.append(t)
 lines[name]=out
# Use two observations of each line: first word versus internal words, to avoid line-final special positions.
def extract(lns):
 pos=[];neg=[]
 for l in lns:
  pos.append(l[0]); neg.extend(l[1:-1])
 return pos,neg

def feat(w,k=2,where='prefix'):
 return w[:k] if where=='prefix' else w[-k:]

def JS(p,q):
 keys=set(p)|set(q); a=sum(p.values());b=sum(q.values())
 if not a or not b:return float('nan')
 s=0
 for v in keys:
  x=p[v]/a;y=q[v]/b;m=(x+y)/2
  if x:s+=.5*x*math.log2(x/m)
  if y:s+=.5*y*math.log2(y/m)
 return s

def div(rows,k,where):
 pos,neg=extract(rows)
 return JS(Counter(feat(w,k,where) for w in pos),Counter(feat(w,k,where) for w in neg))

def perm(rows,k,where,repeats=2000,seed=13):
 obs=div(rows,k,where);r=random.Random(seed);null=[]
 for _ in range(repeats):
  new=[]
  for l in rows:
   j=r.randrange(len(l)-1) # exclude final position in permutation to match internal test
   new.append([l[j]]+l[:j]+l[j+1:])
  null.append(div(new,k,where))
 return {'js_bits':round(obs,5),'permutation_p':round((1+sum(v>=obs for v in null))/(repeats+1),5),'null_mean':round(sum(null)/repeats,5)}
result={'sample':{x:{'lines':len(ls),'tokens':sum(map(len,ls))} for x,ls in lines.items()},'tests':{}}
for name,lns in lines.items():
 result['tests'][name]={f'{where}_{k}':perm(lns,k,where) for where in ['prefix','suffix'] for k in [1,2]}
result['caveats']=['Only four opening folios, f1v and f2r bundled in one file.','Transcription uncertain tokens dropped, biasing word selection.','Four comparisons per group; interpret p-values with multiple-testing caution.','Within-line shuffling can affect contexts but is a valid positional null, not a natural-language control.','No verified full-corpus data; no language or decipherment inferred.']
(P/'voynich_experiment_013_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
