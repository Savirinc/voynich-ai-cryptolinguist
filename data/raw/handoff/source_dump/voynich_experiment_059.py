#!/usr/bin/env python3
"""Voynich Exp 059: physical-line dependence and possible terminal ligatures.
Input: user-provided ZL3b IVTFF EVA transcription, 2025-05-13.
Approach: avoid assuming same spelling implies same meaning. Compare terminal
m/i i n and matched final m/iin, m/in spellings, line-end and paragraph-end
behavior, line fill proxy within folios, stratified by stem and Currier A/B.
The final visual allograph test requires actual image coordinates and is NOT
claimed completed by this transcription analysis.
"""
from docx import Document
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean,median
from math import isfinite
from scipy.stats import mannwhitneyu, fisher_exact
from statsmodels.stats.contingency_tables import StratifiedTable,Table2x2
import json,re
D=Document('/mnt/data/IVTFF Eva.txt.docx')
meta={}; lines=[]
for p in D.paragraphs:
 s=p.text.strip()
 hdr=re.match(r'^<(f\d+[rv](?:\d+)?)>\s*<!([^>]+)>',s)
 if hdr:
  f,h=hdr.groups();m=re.search(r'\$L=([AB])',h);meta[f]=m.group(1) if m else '?'
 m=re.match(r'^<(f\d+[rv](?:\d+)?)\.(\d+),([^>]+)>\s*(.*)',s)
 if not m:continue
 f,number,loc,body=m.groups()
 if 'P' not in loc: continue
 ends_para='<$>' in body
 clean=re.sub(r'<![^>]*>',' ',body)
 clean=re.sub(r'<(?:%|\$|-)>','',clean)
 parts=[z for z in re.split(r'[.,\s]+',clean) if z]
 tokens=[z if re.fullmatch('[a-z]{2,20}',z) else None for z in parts]
 if not tokens:continue
 lines.append({'folio':f,'number':int(number),'currier':meta.get(f,'?'),'tokens':tokens,
               'paraend':ends_para,'total_chars':sum(len(z) for z in tokens if z),
               'last_clean':tokens[-1] is not None,
               'has_uncertain':None in tokens})
obs=[]
for r in lines:
 for j,w in enumerate(r['tokens']):
  if w is None:continue
  # If an unreadable final token exists, don't count a preceding token as last.
  end=(j==len(r['tokens'])-1)
  obs.append({'folio':r['folio'],'currier':r['currier'],'word':w,
              'line_end':end,'para_end':end and r['paraend'],
              'normal_end':end and not r['paraend'],
              'line_words':len(r['tokens']), 'line_chars':r['total_chars'],
              'before_chars':sum(len(z)+1 for z in r['tokens'][:j] if z),
              'line_id':r['folio']+'.'+str(r['number'])})
ct=Counter(r['word'] for r in obs)
ends=Counter()
for r in obs:
 w=r['word'];pos='line_end' if r['line_end'] else 'internal_line'
 for char in ['m','n','i','y','r','l']:
  if char in w:
   ends[(char,'word_end' if w.endswith(char) else 'word_internal')]+=w.count(char) - (int(w.endswith(char)) if not w.endswith(char) else 0) if not w.endswith(char) else 1
 # explicitly count glyph occurrences
for char in ['m','n','i','q']:
 end=sum(w['word'].endswith(char) for w in obs)
 inner=sum(w['word'][:-1].count(char) for w in obs)
 ends[(char,'word_final_tokens')]=end;ends[(char,'word_internal_occurrences')]=inner

def pair_table(longa,shortb,minfreq=3):
 """a and b are suffixes; same literal preceding stem, e.g. daiin vs dam."""
 A=longa; B=shortb
 stem_counts=defaultdict(Counter)
 rows=[]
 for r in obs:
  w=r['word'];suffix=A if w.endswith(A) else (B if w.endswith(B) else None)
  if suffix is None:continue
  stem=w[:-len(suffix)]
  if not stem: continue
  stem_counts[stem][suffix]+=1
  rows.append((stem,suffix,r))
 eligible={s for s,c in stem_counts.items() if c[A]>=minfreq and c[B]>=minfreq}
 matched=[(s,form,r) for s,form,r in rows if s in eligible]
 a_line=sum(form==A and r['line_end'] for s,form,r in matched)
 a_non=sum(form==A and not r['line_end'] for s,form,r in matched)
 b_line=sum(form==B and r['line_end'] for s,form,r in matched)
 b_non=sum(form==B and not r['line_end'] for s,form,r in matched)
 # OR of short form B at line_end vs elsewhere.
 table=[[b_line,a_line],[b_non,a_non]]
 OR,p=fisher_exact(table)
 try:lo,hi=Table2x2(table).oddsratio_confint()
 except:lo,hi=None,None
 # Stratified by word family and Currier A/B.
 grouped=defaultdict(lambda:[[0,0],[0,0]])
 for s,form,r in matched:
  tab=grouped[(s,r['currier'])]
  tab[0 if r['line_end'] else 1][0 if form==B else 1]+=1
 stabs=[t for t in grouped.values() if min([sum(t[0]),sum(t[1]),t[0][0]+t[1][0],t[0][1]+t[1][1]])>0]
 cmh=None
 if stabs:
  st=StratifiedTable(stabs)
  cmh={'strata':len(stabs),'odds_ratio':float(st.oddsratio_pooled),'confint':list(map(float,st.oddsratio_pooled_confint())),
       'test_p':float(st.test_null_odds().pvalue)}
 # Compare proxy line lengths for line-ending terminal A vs B on matching families.
 endrows=[(form,r) for s,form,r in matched if r['line_end'] and not r['para_end'] and r['currier'] in ('A','B')]
 counts_by_folio=defaultdict(list)
 for r in lines:
  if r['last_clean'] and r['folio']:
   counts_by_folio[r['folio']].append(r['total_chars'])
 med={k:median(v) for k,v in counts_by_folio.items() if len(v)>=3}
 # line fill proxy = prior visible letters as a fraction of typical full line's transcript length.
 proxy={}
 for form in [A,B]:
  vals=[r['before_chars']/med[r['folio']] for ff,r in endrows if ff==form and r['folio'] in med and med[r['folio']]>0]
  proxy[form]={'n':len(vals),'median':median(vals) if vals else None,'mean':mean(vals) if vals else None}
 x=[r['before_chars']/med[r['folio']] for ff,r in endrows if ff==B and r['folio'] in med and med[r['folio']]>0]
 y=[r['before_chars']/med[r['folio']] for ff,r in endrows if ff==A and r['folio'] in med and med[r['folio']]>0]
 line_p=float(mannwhitneyu(x,y).pvalue) if x and y else None
 # Paragraph effect among line-end only
 p_b=sum(f==B and r['para_end'] for s,f,r in matched)
 n_b=sum(f==B and r['normal_end'] for s,f,r in matched)
 p_a=sum(f==A and r['para_end'] for s,f,r in matched)
 n_a=sum(f==A and r['normal_end'] for s,f,r in matched)
 par_or,par_p=fisher_exact([[p_b,p_a],[n_b,n_a]])
 return {'pair':A+' -> '+B, 'matched_families':len(eligible),'matched_total':len(matched),
         'four_cell':{'short_at_line_end':b_line,'long_at_line_end':a_line,'short_internal':b_non,'long_internal':a_non},
         'unadjusted_OR':OR,'unadjusted_CI95':[lo,hi],'fisher_p':p,'matched_stem_currier':cmh,
         'line_fill_proxy':proxy,'line_fill_MW_p':line_p,
         'paragraph_end_vs_ordinary_end':{'paragraph_short':p_b,'paragraph_long':p_a,'ordinary_short':n_b,'ordinary_long':n_a,'OR':par_or,'p':par_p},
         'examples':sorted([{'stem':s,'long':s+A,'short':s+B,'long_n':c[A],'short_n':c[B]} for s,c in stem_counts.items() if s in eligible],key=lambda v:-v['short_n'])[:12]}
results={'method':'IVTFF EVA ZL3b running text; conservative clear word forms, preserve physical line and paragraph boundaries',
 'counts':{'running_lines':len(lines),'running_tokens':len(obs),'word_types':len(ct),'allographs_word_final':{c:{'final':ends[(c,'word_final_tokens')], 'internal':ends[(c,'word_internal_occurrences')]} for c in ['m','n','i','q']}},
 'pairs':{k:pair_table(*v) for k,v in {'iin_vs_m':('iin','m'),'in_vs_m':('in','m'),'iin_vs_n':('iin','n'),'l_vs_r':('l','r'),'ey_vs_dy':('ey','dy')}.items()}}
P=Path('/mnt/data');(P/'Voynich_Experiment_059_results.json').write_text(json.dumps(results,indent=2))
for k,v in results['pairs'].items():
 print(k,'N',v['matched_total'],'families',v['matched_families'],'four',v['four_cell'],
       'OR',round(v['unadjusted_OR'],2),'stratified',v['matched_stem_currier'], 'linefill',v['line_fill_proxy'], 'Plinefill',v['line_fill_MW_p'],flush=True)
print(results['counts'],flush=True)
# Hardest geometric proxy control: compare line length before final word INSIDE identical folio+stem groups.
from numpy.random import default_rng
rng=default_rng(5905)
within=defaultdict(lambda:defaultdict(list))
for row in obs:
 if not row['line_end'] or row['para_end']:continue
 w=row['word']
 tag='m' if w.endswith('m') else ('iin' if w.endswith('iin') else None)
 if tag is None:continue
 stem=w[:-len(tag)]
 if not stem:continue
 within[(row['folio'],stem)][tag].append(row['before_chars'])
groups={k:v for k,v in within.items() if 'm' in v and 'iin' in v}
diffs=[mean(v['m'])-mean(v['iin']) for v in groups.values()]
observed=mean(diffs) if diffs else None
perms=[]
if diffs:
 for it in range(20000):
  each=[]
  for v in groups.values():
   n=len(v['m']); vals=v['m']+v['iin']
   order=rng.permutation(len(vals))
   each.append(mean([vals[int(i)] for i in order[:n]])-mean([vals[int(i)] for i in order[n:]]))
  perms.append(mean(each))
 p=(1+sum(abs(x)>=abs(observed) for x in perms))/(len(perms)+1)
else:p=None
results['within_folio_stem_line_length']={'comparable_groups':len(groups),'matched_line_ending_occurrences':sum(sum(len(a) for a in v.values()) for v in groups.values()),
  'observed_mean_difference_characters_before_final_word_m_minus_iin':observed,
  'pairwise_group_permutation_two_sided_p':p,'num_permutations':len(perms),
  'group_positive_differences':sum(x>0 for x in diffs),'group_negative_differences':sum(x<0 for x in diffs),
  'interpretation_caveat':'EVA length is not physical pixel width; tiny within-folio+stem sample; no image geometry validated.'}
(P/'Voynich_Experiment_059_results.json').write_text(json.dumps(results,indent=2))
print('Within folio and stem',results['within_folio_stem_line_length'],flush=True)
