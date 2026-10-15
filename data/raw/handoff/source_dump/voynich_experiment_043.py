from docx import Document
import re, collections, json, math
from scipy.stats import fisher_exact
source='/mnt/data/IVTFF Eva.txt.docx'
lines=[]
for p in Document(source).paragraphs:
 m=re.match(r'^<(f\d+[rv])\.(\d+)[^>]*>\s*(.*)',p.text.strip(),re.I)
 if not m: continue
 words=[w for w in re.split(r'[., ]+',m.group(3).split('<!')[0]) if re.fullmatch(r'[a-z]{2,20}',w)]
 if words: lines.append((m.group(1),words))
c=collections.Counter(w for _,words in lines for w in words)
N=sum(c.values());qwords=[(w,n) for w,n in c.items() if w.startswith('q')]
all_q=sum(w.count('q')*n for w,n in c.items())
q_init=sum(n for w,n in c.items() if w.startswith('q'))
qo=sum(n for w,n in c.items() if w.startswith('qo'))
qcounter=sum(n for w,n in qwords if c[w[1:]]>0)
# Is prefix q detachable more than other initial glyphs, matching vocabulary sizes roughly?
removal={}
for letter in 'qodsch':
 subset=[(w,n) for w,n in c.items() if w.startswith(letter)]
 tot=sum(n for _,n in subset)
 counterpart=sum(n for w,n in subset if c[w[1:]]>0)
 removal[letter]={'tokens':tot,'with_attested_stripped_form':counterpart,'fraction':round(counterpart/tot,4) if tot else None}
# Evaluate q 'word beginning' bias versus all characters
allch=sum(sum(w.count(ch)*n for ch in set(w)) for w,n in c.items())
# Bigram association of first q with next glyph o compared to initial non-q being followed o
q_o=qo;q_other=q_init-qo
nonq_o=sum(n for w,n in c.items() if not w.startswith('q') and len(w)>1 and w[1]=='o')
nonq_other=sum(n for w,n in c.items() if not w.startswith('q') and len(w)>1 and w[1]!='o')
odds,p=fisher_exact([[q_o,q_other],[nonq_o,nonq_other]])
# held-out folio split stable q prefix structure
folios=sorted({folio for folio,_ in lines});train=set(f for i,f in enumerate(folios) if i%5);test=set(folios)-train
splits={}
for name, fs in [('train',train),('held_out',test)]:
 wc=collections.Counter(w for f,words in lines if f in fs for w in words)
 total=sum(wc.values()); qt=sum(n for w,n in wc.items() if w.startswith('q'));qot=sum(n for w,n in wc.items() if w.startswith('qo'))
 splits[name]={'folios':len(fs),'tokens':total,'q_initial_fraction':round(qt/total,4),'qo_given_q_initial':round(qot/qt,4)}
result={'source':source,'method':'running-text folio.number lines; exact lower-case EVA words only; split on spaces dot comma; editor-uncertain tokens excluded','lines':len(lines),'tokens':N,'types':len(c),'all_q_glyph_instances':all_q,'q_at_start':q_init,'q_inside_word':all_q-q_init,'qo_initial':qo,'q_prefix_detachment':{'count':qcounter,'fraction':round(qcounter/q_init,4)},'prefix_detachment_comparators':removal,'first_following_o_association':{'q_then_o':q_o,'q_then_not_o':q_other,'nonq_then_o':nonq_o,'nonq_then_not_o':nonq_other,'odds_ratio':odds,'fisher_p':p},'folio_heldout':splits,'illustrative_pairs':{w:{'with_q':c[w],'without_q':c[w[1:]]} for w in ['qokedy','qokeedy','qokain','qokaiin','qokal','qotedy']},'limitation':'Evidence for productive graphic prefix, not evidence for meaning/sound. Stripped counterparts may occur by chance due to frequent short word forms.'}
with open('/mnt/data/voynich_experiment_043_results.json','w') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
