"""Independent descriptive audit of IVTFF locus classes; no decipherment implied."""
from docx import Document
from collections import Counter
import re, json
source='/mnt/data/IVTFF Eva.txt.docx'
P=[x.text.strip() for x in Document(source).paragraphs]
H=re.compile(r'^<(f\d+[rv]\d?)>\s+<!([^>]*)>')
L=re.compile(r'^<(f\d+[rv]\d?\.\d+),([^>]*)>\s*(.*)')
M={};R=[];current=None
for s in P:
 h=H.match(s)
 if h:
  M[h.group(1)]=dict(re.findall(r'\$(\w)=([^\s>]+)',h.group(2)));current=None;continue
 l=L.match(s)
 if l:
  f=l.group(1).split('.')[0]
  current={'folio':f,'tag':l.group(2),'raw':l.group(3),'metadata':M.get(f,{})};R.append(current)
 elif current and s and not s.startswith('#'):
  current['raw']+=' '+s

def tokens(raw):
 raw=re.sub(r'<!.*?>|<[^>]*>',' ',raw)
 raw=re.sub(r'\{[^}]*\}|\[[^]]*\]|@\d+;','?',raw)
 return [v for v in re.split(r'[.,\s]+',raw) if re.fullmatch('[a-z]{2,}',v)]
for r in R:r['tokens']=tokens(r['raw'])
prose=[r for r in R if 'P' in r['tag'] and r['metadata'].get('L') in ('A','B')]
labels=[r for r in R if 'L' in r['tag'] and r['tag'][0] in '@+&=*~']
zodiac=[r for r in labels if r['metadata'].get('I')=='Z']
counts=lambda rs:Counter(w for r in rs for w in r['tokens'])
cp,cl,cz=counts(prose),counts(labels),counts(zodiac)
def describe(r,c):return {'records':len(r),'folios':len(set(x['folio'] for x in r)),'tokens':sum(c.values()),'types':len(c),'top_words':c.most_common(12)}
out={'source':'User-supplied ZL3b IVTFF 2025 transcription','tokenization':'Strict Latin lower-case strings with length >=2; ambiguous readings excluded; tags by IVTFF locus class; does not equate all labels with semantic names','all_records':len(R),'prose':describe(prose,cp),'all_label_loci':describe(labels,cl),'zodiac_label_loci':describe(zodiac,cz),'zodiac_label_record_folios':Counter(r['folio'] for r in zodiac),'label_token_in_prose_vocabulary_pct':100*sum(n for w,n in cz.items() if w in cp)/max(1,sum(cz.values())),'label_type_in_prose_vocabulary_pct':100*sum(w in cp for w in cz)/max(1,len(cz))}
with open('/mnt/data/voynich_experiment_021_results.json','w') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
