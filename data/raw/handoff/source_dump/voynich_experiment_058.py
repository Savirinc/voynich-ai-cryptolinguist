#!/usr/bin/env python3
"""Experiment 058. Honest surface-token prediction after reversible word-form merging.

Source: user-provided IVTFF EVA ZL3b transcription (DOCX). Uses running text only.
Split: all sides/panels of the same numbered leaf held together.
Compare raw hierarchical unigram/bigram + char-trigram LM with a reversible latent-family
model: predict canonical family THEN predict exact surface form given line-end and previous-y.
Negative control: equal-size frequency-stratified random family mergers.
No phonetic or semantic interpretations of EVA are made.
"""
from docx import Document
from collections import Counter, defaultdict
from pathlib import Path
import hashlib, re, math, json, random, statistics, os
import numpy as np
P=Path('/mnt/data')
SEED=os.environ.get('VOYNICH_058_SEED','base')
NULL=int(os.environ.get('VOYNICH_058_NULL_TRIALS','20'))
source=P/'IVTFF Eva.txt.docx'
raw_lines=[];meta={}
for paragraph in Document(source).paragraphs:
 s=paragraph.text.strip()
 header=re.match(r'^<(f\d+[rv](?:\d+)?)>\s*<!([^>]+)>',s)
 if header:
  f,h=header.groups();l=re.search(r'\$L=([AB])',h)
  meta[f]=l[1] if l else '?'
 m=re.match(r'^<(f\d+[rv](?:\d+)?)\.(\d+),([^>]+)>\s*(.*)',s)
 if not m: continue
 f,no,loc,raw=m.groups()
 if 'P' not in loc: continue
 raw_clean=re.sub(r'<![^>]*>',' ',raw)
 raw_clean=re.sub(r'<(?:%|\$|-)>','',raw_clean)
 pieces=[z for z in re.split(r'[.,\s]+',raw_clean) if z]
 tok=[w if re.fullmatch('[a-z]{2,20}',w) else None for w in pieces]
 if not tok:continue
 raw_lines.append({'folio':f,'no':int(no),'loc':loc,'raw':raw,'tokens':tok,'variety':meta.get(f,'?')})
raw_lines.sort(key=lambda r:(int(re.match(r'f(\d+)',r['folio']).group(1)),r['folio'],r['no']))
# Distinctive folio-number identifier prevents f70r and f70v split leakage.
def split_for(f):
 leaf=re.match(r'f(\d+)',f).group(1)
 u=int(hashlib.sha256(('voynich-experiment-058-leaf:'+leaf if SEED=='base' else 'voynich-058-cv:'+SEED+':'+leaf).encode()).hexdigest()[:10],16)%10
 return 'test' if u==0 else ('val' if u==1 else 'train')
sequences=[]
for line in raw_lines:
 w=line['tokens']; split=split_for(line['folio'])
 for i,cur in enumerate(w):
  if cur is None:continue
  prev=w[i-1] if i else None
  if prev is None: prev='^LINE'
  sequences.append({'folio':line['folio'],'split':split,'word':cur,
   'prev':prev,'prev_y':int(prev.endswith('y')),
   'line_end':int(i==len(w)-1),'variety':line['variety'],
   'line':line['no']})
train=[r for r in sequences if r['split']=='train']
val=[r for r in sequences if r['split']=='val']
test=[r for r in sequences if r['split']=='test']
trainc=Counter(r['word'] for r in train)
# paired forms: independent prefix and line-ending transformations; rely only on training evidence.
q_pairs=[('q'+w,w) for w,n in trainc.items() if w.startswith('o') and n>=2 and trainc['q'+w]>=2]
m_pairs=[(w[:-1]+'iin',w) for w,n in trainc.items() if w.endswith('m') and n>=2 and trainc[w[:-1]+'iin']>=2]
q_pairs=sorted(set(q_pairs));m_pairs=sorted(set(m_pairs))

class DSU:
 def __init__(self):self.parent={}
 def get(self,a):
  if a not in self.parent:self.parent[a]=a
  if a!=self.parent[a]:self.parent[a]=self.get(self.parent[a])
  return self.parent[a]
 def merge(self,a,b):self.parent[self.get(a)]=self.get(b)

def family_map(qpairs,mpairs):
 d=DSU()
 for a,b in qpairs+mpairs:d.merge(a,b)
 groups=defaultdict(list)
 for w in d.parent:groups[d.get(w)].append(w)
 # choose canonical representative by q-stripped then iin-preferred, lexical tie break.
 reps={}
 for g in groups.values():
  g=sorted(g,key=lambda w:(w.startswith('q'),w.endswith('m'),-trainc[w],w))
  for w in g:reps[w]=g[0]
 return reps

# Token-char model. Gives positive probability to unseen words, unlike word-only models.
class CharLM:
 def __init__(self,words,order=2,alpha=.3):
  self.counts=defaultdict(Counter); self.context=Counter(); self.alpha=alpha
  self.chars=set('abcdefghijklmnopqrstuvwxyz')|{'$'}
  for w,n in words.items():
   for a,b in self.grams(w):
    self.counts[a][b]+=n;self.context[a]+=n
 def grams(self,w):
  x='^^'+w+'$'
  return [(x[i-2:i],x[i]) for i in range(2,len(x))]
 def p(self,w):
  v=1.0; denom=len(self.chars)
  for ctx,z in self.grams(w):
   v*= (self.counts[ctx][z]+self.alpha)/(self.context[ctx]+self.alpha*denom)
  return v

class Model:
 def __init__(self,train,map_,lam=.2,char_mix=.2,var_smooth=12):
  self.map=map_;self.lam=lam;self.char_mix=char_mix;self.var_smooth=var_smooth
  self.uni=Counter();self.bi=defaultdict(Counter);self.prevcount=Counter()
  self.variant=defaultdict(Counter);self.ctxvar=defaultdict(Counter)
  self.group=defaultdict(set)
  for r in train:
   base=self.map.get(r['word'],r['word'])
   prev=self.map.get(r['prev'],r['prev'])
   self.uni[base]+=1;self.bi[prev][base]+=1;self.prevcount[prev]+=1
   self.variant[base][r['word']]+=1
   self.ctxvar[(base,r['prev_y'],r['line_end'])][r['word']]+=1
   self.group[base].add(r['word'])
  self.N=sum(self.uni.values()); self.char=CharLM(self.uni)
  self.chcache={}
 def pb(self,base,prev):
  if base not in self.chcache:self.chcache[base]=self.char.p(base)
  u=(1-self.char_mix)*self.uni[base]/self.N+self.char_mix*self.chcache[base]
  if prev not in self.prevcount:return u
  return self.lam*self.bi[prev][base]/self.prevcount[prev]+(1-self.lam)*u
 def pv(self,base,form,cy,le):
  g=self.group.get(base)
  if not g:return 1.0
  if len(g)==1:
   return 1.0 if form in g else 1e-12
  var=self.variant[base];cv=self.ctxvar[(base,cy,le)]
  # shrink conditional variant distribution towards family marginal.
  gsize=len(g);nbase=sum(var.values());nctx=sum(cv.values())
  prior=(var[form]+.5)/(nbase+0.5*gsize)
  return (cv[form]+self.var_smooth*prior)/(nctx+self.var_smooth)
 def eval(self,docs):
  logsum=0;details=[]; unseen=0
  for r in docs:
   w=r['word'];base=self.map.get(w,w)
   prev=self.map.get(r['prev'],r['prev'])
   p=max(1e-300,self.pb(base,prev)*self.pv(base,w,r['prev_y'],r['line_end']))
   logs=-math.log2(p);logsum+=logs
   if w not in trainc:unseen+=1
   details.append((r['folio'],logs,w,base))
  return logsum/len(docs),details,unseen

# Choose config using validation for each model (fair tuning of baselines).
configs=[(.15,.2,3)]

def tune(map_):
 best=None
 for lam,cm,smooth in configs:
  m=Model(train,map_,lam,cm,smooth)
  err,_,_=m.eval(val)
  if best is None or err<best[0]:best=(err,(lam,cm,smooth))
 return best

rawmap={}
qmap=family_map(q_pairs,[])
mmap=family_map([],m_pairs)
fullmap=family_map(q_pairs,m_pairs)
output={'experiment':'058','source':'User-supplied IVTFF EVA ZL3b DOCX',
 'dataset':{'clean_running_tokens':len(sequences),'train':len(train),'validation':len(val),'test':len(test),
   'training_word_types':len(trainc),'training_leaves':len({re.search(r'f(\d+)',r['folio']).group(1) for r in train}),
   'test_leaves':len({re.search(r'f(\d+)',r['folio']).group(1) for r in test}),
   'q_pairs_training_min2':len(q_pairs),'m_pairs_training_min2':len(m_pairs)},
 'models':{},'controls':[],'method':'Held-out original word probability: P(canonical word | preceding canonical word) * P(original surface | canonical, preceding word ends y, line ends). Character ngram fallback for unseen word forms. Parameters selected on the original validation split, then fixed across five follow-up splits.'}
for title,mp in [('raw',rawmap),('q_only',qmap),('m_only',mmap),('q_and_m',fullmap)]:
 dev,params=tune(mp); model=Model(train,mp,*params)
 err,details,unseen=model.eval(test)
 merges=len({v for v in trainc})-len({mp.get(w,w) for w in trainc})
 output['models'][title]={'validation_bits_per_word':round(dev,5),'test_bits_per_word':round(err,5),'params':params,'merged_types':merges,'test_unseen_word_tokens':unseen}
 # retain per folio bits for uncertainty (all models use same test instances)
 (P/f'voynich_058_{SEED}_{title}_folio_losses.json').write_text(json.dumps({f:{'loss_total':sum(x[1] for x in details if x[0]==f),'n':sum(x[0]==f for x in details)} for f in sorted({x[0] for x in details})},indent=2))
 print(title,output['models'][title],flush=True)

# Adversarial controls: mismatched pairs with similar frequency, preserving counts/types and source-form classes.
def shuffled_pairs(pairs,rng):
 # Pair first ends to second ends with similar frequency (log frequency bucket sorted then local block shuffles).
 if not pairs:return []
 a=[x for x,_ in pairs];bs=[x for _,x in pairs]
 bs.sort(key=lambda w:math.log1p(trainc[w]))
 # rank first elems by frequency then permute targets locally within 10-word windows.
 a.sort(key=lambda w:math.log1p(trainc[w]))
 new=[]
 for k in range(0,len(a),10):
  local=bs[k:k+10];rng.shuffle(local)
  new.extend(zip(a[k:k+10],local))
 return new

rng=random.Random(58017)
# fixed config selected by validation for correct combined merging; null has identical model complexity and total merged edges.
params=output['models']['q_and_m']['params']
for i in range(NULL):
 fake=family_map(shuffled_pairs(q_pairs,rng),shuffled_pairs(m_pairs,rng))
 mm=Model(train,fake,*params)
 error,_,_=mm.eval(test)
 merges=len(trainc)-len({fake.get(w,w) for w in trainc})
 output['controls'].append({'iteration':i,'test_bits_per_word':round(error,5),'merged_types':merges})
 if i%5==0:print('null',i,error,flush=True)
control=[z['test_bits_per_word'] for z in output['controls']]
output['control_summary']={'mean_test_bits_per_word':float(np.mean(control)) if control else None,
 'sd':float(np.std(control)) if control else None,'min':min(control) if control else None,'max':max(control) if control else None,
 'empirical_fraction_controls_not_worse_than_true':(sum(x<=output['models']['q_and_m']['test_bits_per_word'] for x in control)+1)/(len(control)+1) if control else None,
 'warning':'Random controls preserve approximate sizes and train-frequency ranks, not exact distribution of contextual word features.'}
# Additional placebo: same number of -m/-iin family merges, but partners randomized by train frequency.
m_rng=random.Random(58311); m_controls=[]
m_params=output['models']['m_only']['params']
for i in range(int(os.environ.get('VOYNICH_058_M_NULL_TRIALS','50'))):
    fake=family_map([],shuffled_pairs(m_pairs,m_rng))
    model=Model(train,fake,*m_params)
    err,_,_=model.eval(test)
    m_controls.append({'iteration':i,'test_bits_per_word':round(err,5),
      'merged_types':len(trainc)-len({fake.get(w,w) for w in trainc})})
output['m_only_placebos']={'runs':m_controls,'mean_test_bits_per_word':float(np.mean([r['test_bits_per_word'] for r in m_controls])) if m_controls else None,
 'minimum_test_bits_per_word':min(r['test_bits_per_word'] for r in m_controls) if m_controls else None,
 'empirical_p_lower_is_better':(1+sum(r['test_bits_per_word']<=output['models']['m_only']['test_bits_per_word'] for r in m_controls))/(len(m_controls)+1) if m_controls else None}
output['limitations']=[
 'No claim of underlying semantic identity; reversible normalization is evaluated on reconstruction of exact original EVA words, not just shorter vocabulary.',
 'Only transcription-clear running-text words; labels and visually ambiguous glyphs excluded.',
 'Line boundary metadata comes from IVTFF and could contain transcription artifacts.',
 'No exhaustive search of medieval French or other language was conducted.',
 'Unigram/bigram models and randomized controls are model-class-dependent; any apparent gains require replication with other heldout splits and stronger neural baselines.'
]
(P/('voynich_experiment_058_results.json' if SEED=='base' else f'voynich_058_cv_{SEED}.json')).write_text(json.dumps(output,indent=2))
print('FINAL',json.dumps({k:v for k,v in output.items() if k not in ('controls',)},indent=2))
