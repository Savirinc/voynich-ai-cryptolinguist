"""Reproducible small Voynich EVA character language model. Uses no external models."""
from docx import Document
from collections import Counter,defaultdict
import re,random,json,math
src='/mnt/data/IVTFF Eva.txt.docx'
rows=Document(src).paragraphs
pages=defaultdict(list)
for paragraph in rows:
 s=paragraph.text.strip()
 m=re.match(r'^<(f\d+[rv])\.([^>,]+)[^>]*>\s*(.*)$',s,re.I)
 if not m: continue
 folio=m.group(1).lower()
 # Only lines in original running text, not marginal drawings; can expand later.
 if not re.match(r'^\d+$',m.group(2)): continue
 content=m.group(3).split('<!')[0]
 content=re.sub(r'<[^>]*>','',content)
 content=content.replace('.', ' ').replace(',', ' ')
 words=[w for w in content.split() if re.fullmatch(r'[a-z]{2,20}',w)]
 if len(words)>=2: pages[folio].append(words)
folios=sorted(pages)
r=random.Random(20261012);r.shuffle(folios)
cut=max(1,int(.8*len(folios)));trainfolios=set(folios[:cut]);testfolios=set(folios[cut:])
trainlines=[l for f in trainfolios for l in pages[f]]
testlines=[l for f in testfolios for l in pages[f]]
# For next-symbol: word boundaries and newline markers; model character sequence with simple add-alpha smoothing.
tr='\n'.join(' '.join(l) for l in trainlines)
te='\n'.join(' '.join(l) for l in testlines)
alphabet=sorted(set(tr+te));V=len(alphabet)
def fit(order):
 ctx=defaultdict(Counter)
 seq='^'*order+tr
 for i in range(order,len(seq)):ctx[seq[i-order:i]][seq[i]]+=1
 return ctx
def metrics(order,alpha=.15):
 ctx=fit(order); logs=[]; misses=0
 seq='^'*order+te
 for i in range(order,len(seq)):
  key=seq[i-order:i];c=ctx.get(key);total=sum(c.values()) if c else 0
  prob=((c.get(seq[i],0) if c else 0)+alpha)/(total+alpha*V)
  logs.append(-math.log2(prob));misses+= not bool(c)
 return {'bits_per_character':round(sum(logs)/len(logs),4),'perplexity':round(2**(sum(logs)/len(logs)),3),'unseen_context_rate':round(misses/len(logs),4)}
word_train=[w for row in trainlines for w in row];word_test=[w for row in testlines for w in row]
unique=set(word_train)
wordbig=defaultdict(Counter)
for row in trainlines:
 for a,b in zip(['<BOS>']+row,row):wordbig[a][b]+=1
pairs=[(a,b) for row in testlines for a,b in zip(['<BOS>']+row,row)]
from collections import Counter
uni=Counter(word_train)
# Among contexts seen, is the most common successor the correct word? Plus baseline globally common word.
seen=[(a,b) for a,b in pairs if a in wordbig]
acc=sum(wordbig[a].most_common(1)[0][0]==b for a,b in seen)/len(seen)
baseline=sum(uni.most_common(1)[0][0]==b for _,b in pairs)/len(pairs)
# sample conditional predictions from common contexts
samples={}
for seed in ['daiin','chol','qokedy','chedy','ol','ot','<BOS>']:
 if seed in wordbig:samples[seed]=wordbig[seed].most_common(5)
result={'source':'IVTFF Eva.txt.docx, ZL v3b (2025)','folio_split_seed':20261012,'folios_total':len(folios),'folios_train':len(trainfolios),'folios_test':len(testfolios),'train_word_tokens':len(word_train),'test_word_tokens':len(word_test),'test_word_oov_fraction':round(sum(w not in unique for w in word_test)/len(word_test),4),'unique_train_words':len(unique),'alphabet_size_including_space_newline':V,'char_models':{f'order_{i}':metrics(i) for i in (0,1,2,3)},'word_bigram':{'seen_previous_word_fraction':round(len(seen)/len(pairs),4),'top_1_accuracy_when_previous_seen':round(acc,4),'global_most_common_word_baseline_accuracy':round(baseline,4)},'example_next_word_predictions':samples,'caveat':'This predicts EVA surface forms, not meaning; all metrics are held-out folio comparisons; conservative regex rejects many editorial/uncertain forms.'}
with open('/mnt/data/voynich_mini_lm_results.json','w') as o:json.dump(result,o,indent=2)
print(json.dumps(result,indent=2))
