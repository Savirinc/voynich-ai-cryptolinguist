"""Experiment 050: compare boundary effects across alternative Voynich onset operators.
The data are EVA-transcribed symbols, never phonetic or semantic readings.
"""
import re,json,collections,math
from pathlib import Path
from docx import Document
from statsmodels.stats.contingency_tables import StratifiedTable
from scipy.stats import fisher_exact

P=Path('/mnt/data')
raws=Document(P/'IVTFF Eva.txt.docx').paragraphs
lang={}; rows=[]; folio_count=collections.Counter()
for p in raws:
 s=p.text.strip()
 h=re.match(r'^<(f\d+[rv](?:\d+)?)>\s*<!.*?\$L=([AB])',s)
 if h: lang[h[1]]=h[2]
 m=re.match(r'^<(f\d+[rv](?:\d+)?)\.(\d+),([^>]+)>\s*(.*)',s)
 if not m: continue
 fol,lineno,loc,payload=m.groups()
 if 'P' not in loc: continue
 # Avoid corrupting sequences through uncertain editorial spans by dividing at the spans.
 # Keep preceding-word adjacency only across clean adjacent tokens, not across lost words.
 payload=re.sub(r'<![^>]*>',' ',payload)
 tokens=re.split(r'[.,\s]+',payload)
 prior=None
 for idx,w in enumerate(tokens):
  if re.fullmatch(r'[a-z]{2,20}',w):
   rows.append({'folio':fol, 'kind':lang.get(fol,'?'),'word':w,'prev':prior or '', 'lineno':int(lineno)})
   folio_count[fol]+=1
   prior=w
  elif w:
   prior=None

freq=collections.Counter(r['word'] for r in rows)
# Compare prefix-constrained pairs, controlling stem (the shared visible form) and variety.
def compare(name, alt, bare, min_n=1):
 # mapping funcs return shared base or None
 sub=[]
 for r in rows:
  w=r['word']
  a=alt(w); b=bare(w)
  if a is not None:
   sub.append((r,a,1))
  elif b is not None:
   sub.append((r,b,0))
 counts=collections.Counter((stem,treatment) for r,stem,treatment in sub)
 valid={stem for (stem,t),n in counts.items() if counts[(stem,0)]>=min_n and counts[(stem,1)]>=min_n}
 sub=[(r,s,t) for r,s,t in sub if s in valid and r['prev']]
 totals=collections.Counter((int(r['prev'].endswith('y')),t) for r,s,t in sub)
 table=[[totals[(1,1)],totals[(1,0)]],[totals[(0,1)],totals[(0,0)]]]
 strata=collections.defaultdict(lambda:[[0,0],[0,0]])
 for r,s,t in sub: strata[(s,r['kind'])][int(r['prev'].endswith('y'))][t]+=1
 informative=[arr for arr in strata.values() if all(sum(a)>0 for a in arr) and all(sum(arr[i][j] for i in range(2))>0 for j in range(2))]
 output={'contrast':name,'matched_stems':len(valid),'eligible_tokens_with_predecessor':len(sub), 'raw_table_y_vs_other_qform_first':table, 'raw_rates':{'after_y':round(totals[(1,1)]/max(1,totals[(1,1)]+totals[(1,0)]),4), 'after_non_y':round(totals[(0,1)]/max(1,totals[(0,1)]+totals[(0,0)]),4)}, 'informative_strata':len(informative)}
 if informative:
  import numpy as np
  st=StratifiedTable([np.array(x) for x in informative])
  output.update({'adjusted_OR_y':round(float(st.oddsratio_pooled),3),'adjusted_OR_CI':[round(float(x),3) for x in st.oddsratio_pooled_confint()], 'stratified_p':float(st.test_null_odds().pvalue)})
 return output

comparisons=[]
# note alt strips fixed prefix and bare retains remainder starting with o
for name,prefix in [('q + o... versus o...', 'q'),('d + o... versus o...','d'),('y + o... versus o...','y'),('l + o... versus o...','l'),('ch + o... versus o...','ch'),('sh + o... versus o...','sh'),('t + o... versus o...','t'),('k + o... versus o...','k')]:
 comparisons.append(compare(name, lambda w,prefix=prefix: w[len(prefix):] if w.startswith(prefix+'o') and len(w)>len(prefix)+2 else None,
                              lambda w: w if w.startswith('o') and len(w)>2 else None,min_n=2))
# Compare o+visible remainder vs bare visible remainder with same identity
comparisons.append(compare('o + stem versus bare stem',lambda w:w[1:] if w.startswith('o') and len(w)>3 else None,
                           lambda w:w if not w.startswith('o') and len(w)>2 else None,min_n=2))
# Contrast initial ch vs sh on same residual string
comparisons.append(compare('ch + residual versus sh + residual',lambda w:w[2:] if w.startswith('ch') and len(w)>4 else None,
                           lambda w:w[2:] if w.startswith('sh') and len(w)>4 else None,min_n=2))

out={'source':'user-uploaded IVTFF EVA transcription ZL v3b, parsed P-lines; initial adjacent clean words within each line','tokens':len(rows),'folios':len(folio_count), 'comparisons':comparisons, 'notes':['All comparisons are syntactic surface form contrasts; no phonetic or semantic values are assigned.', 'CMH odds ratios control for exact shared remainder and Currier A/B where metadata present.', 'Pairs filtered to at least 2 instances of each form; this is exploratory, multiple contrasts.', 'The split is on visual EVA string sequences; an EVA digraph need not equal two manuscript glyphs.']}
(P/'voynich_experiment_050_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
