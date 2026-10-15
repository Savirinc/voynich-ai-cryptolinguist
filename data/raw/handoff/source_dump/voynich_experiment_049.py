"""Experiment 049: Probe initial EVA q as negative/polarity morpheme versus boundary-sensitive operator.
User-provided IVTFF EVA ZL v3b transcription. No semantic translations inferred.
"""
from docx import Document
from collections import Counter,defaultdict
from scipy.stats import fisher_exact
import re,json,math
from pathlib import Path
ROOT=Path('/mnt/data')
paras=Document(ROOT/'IVTFF Eva.txt.docx').paragraphs
lines=[];occ=[];labels=[];lang={}
for p in paras:
 s=p.text.strip()
 h=re.match(r'^<(f\d+[rv](?:\d+)?)>\s*<!.*?\$L=([AB])',s)
 if h:lang[h.group(1)]=h.group(2)
 m=re.match(r'^<(f\d+[rv](?:\d+)?)\.(\d+),([^>]+)>\s*(.*)',s)
 if not m: continue
 f,li,loc,payload=m.groups()
 # Remove all editorial annotation, slash tags and uncertainty before extracting.
 payload=re.sub(r'<![^>]*>','',payload) # removes clock and paragraph markers
 # Exclude annotation spans (..), bracket readings, editor escapes; conservative exact words only
 words=[w for w in re.split(r'[.,\s]+',payload) if re.fullmatch(r'[a-z]{2,20}',w)]
 is_label=('L' in loc and 'P' not in loc) or ('@L' in loc) or ('&L' in loc)
 if is_label:
  for w in words: labels.append((f,loc,w))
 if ('P' not in loc) or len(words)<2: continue
 lidx=len(lines);lines.append({'folio':f,'line':int(li),'words':words,'variety':lang.get(f,'?')})
 for i,w in enumerate(words):
  occ.append({'folio':f,'loc':loc,'lineidx':lidx,'idx':i,'word':w,'prev':words[i-1] if i else '' ,'next':words[i+1] if i+1<len(words) else ''})
words=Counter(r['word'] for r in occ)
qstart=sum(w.startswith('q')*n for w,n in words.items());qnext=Counter()
for w,n in words.items():
 if w.startswith('q') and len(w)>1:qnext[w[1]]+=n
pairs=[]
for w,n in words.items():
 if w.startswith('qo') and words[w[1:]]>=5 and n>=5:
  stem=w[1:];pairs.append({'base':stem,'q_form':w,'base_tokens':words[stem],'q_tokens':n,'q_share':round(n/(n+words[stem]),3)})
pairs.sort(key=lambda x:-(x['base_tokens']+x['q_tokens']))
labelq=Counter(w[1] if w.startswith('q') and len(w)>1 else '?' for _,loc,w in labels if w.startswith('q'))
# Word-initial q eligibility by position, only tokens beginning o or qo and len normalized >=3
ct=Counter()
for r in occ:
 w=r['word'];stem=w[1:] if w.startswith('qo') else w
 if not(w.startswith('qo') or (w.startswith('o') and len(w)>2)) or len(stem)<3: continue
 q=int(w.startswith('q'))
 pos='line_start' if r['idx']==0 else 'within_line'
 ct[(pos,q)]+=1
 if r['prev']:
  end=r['prev'][-1]
  if end in 'ynlr':ct[('prev='+end,q)]+=1
# Test q in line initial v in line for eligible tokens
T=[[ct[('line_start',1)],ct[('line_start',0)]],[ct[('within_line',1)],ct[('within_line',0)]]]
OR,p=fisher_exact(T)
# How often do paired forms occur in same folio? joint occurrence across sampled folios
folio_words=defaultdict(set)
for r in occ:folio_words[r['folio']].add(r['word'])
for d in pairs[:20]: d['folios_with_both']=sum(d['q_form'] in s and d['base'] in s for s in folio_words.values())
result={
 'parser':'Only running P loci, clean EVA lower-case tokens, 2-20 chars; partial annotation exclusions; digitized source annotated; label loci separately counted',
 'running_tokens':sum(words.values()),'running_lines':len(lines),'q_word_initial_count':qstart,
 'q_following_character_counts':qnext,'q_following_character_percent':{c:round(100*n/qstart,3) for c,n in qnext.items()},
 'labels_total_clean_tokens':len(labels),'labels_q_initial':sum(w.startswith('q') for f,l,w in labels),'labels_q_following':labelq,
 'q_pair_forms_min5_each':len(pairs),'most_frequent_pairs':pairs[:20],
 'q_eligible_line_start':{'with_q':ct[('line_start',1)],'without_q':ct[('line_start',0)],'rate':round(ct[('line_start',1)]/sum(ct[('line_start',q)] for q in (0,1)),4)},
 'q_eligible_within_line':{'with_q':ct[('within_line',1)],'without_q':ct[('within_line',0)],'rate':round(ct[('within_line',1)]/sum(ct[('within_line',q)] for q in (0,1)),4)},
 'q_line_initial_vs_internal_OR':round(OR,4),'q_line_initial_vs_internal_fisher_p':p,
 'prev_terminal_rates':{c:{'with_q':ct[('prev='+c,1)],'without_q':ct[('prev='+c,0)],'rate':round(ct[('prev='+c,1)]/sum(ct[('prev='+c,q)] for q in (0,1)),4)} for c in 'ynlr'},
 'interpretation':'The observed q/qo distributions and nearby-word dependency establish spelling constraints; neither synonym nor antonym meaning can be inferred without an independent semantic anchor.',
 'caveat':'Line-start rates from transcribed lines, which may differ from actual author-intended grammatical units. Counts depend on IVTFF token selection. Label classification includes all annotated @L/&L rather than strictly zodiac labels.'
}
(ROOT/'voynich_experiment_049_results.json').write_text(json.dumps(result,indent=2,default=dict))
print(json.dumps(result,indent=2,default=dict))
