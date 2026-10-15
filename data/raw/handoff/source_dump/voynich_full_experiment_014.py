"""Full manuscript exploratory analysis of ZL3b IVTFF EVA file embedded in DOCX.
Keeps ONLY unambiguous lowercase EVA tokens and paragraph-text loci; skips labels.
Results are conservative exploratory measurements, not a decipherment.
"""
import re,json,collections,random,math
from pathlib import Path
from docx import Document
from scipy.spatial.distance import jensenshannon
SRC=Path('/mnt/data/IVTFF Eva.txt.docx')
OUT=Path('/mnt/data/voynich_full_experiment_014_results.json')
rows=[p.text.strip() for p in Document(SRC).paragraphs]
page_re=re.compile(r'^<([fF]\d+[rv](?:\d)?)>\s+<!([^>]*)>')
locus_re=re.compile(r'^<([fF]\d+[rv](?:\d)?\.\d+),([^>]*)>\s*(.*)')
state={}; page=None; loci=[]; last=None
for row in rows:
    p=page_re.match(row)
    if p:
        page=p.group(1); metadata=p.group(2)
        state[page]={k:v for k,v in re.findall(r'\$(\w)=([^\s>]+)',metadata)}
        last=None;continue
    if not row or row.startswith('#'):continue
    m=locus_re.match(row)
    if m:
        if m.group(1).split('.')[0] not in state:continue
        last={'page':m.group(1).split('.')[0],'loc':m.group(2),'raw':m.group(3)}
        loci.append(last)
    elif last is not None:
        last['raw']+=' '+row
# comments and annotations are replaced with spaces to avoid joining fragments
# (? inside word, editorial brackets, hyphenated page interruptions) invalidate token
for x in loci:
    raw=x['raw']
    raw=re.sub(r'<!.*?>',' ',raw)
    raw=re.sub(r'<[^>]*>',' ',raw)
    raw=re.sub(r'\{[^}]*\}|\[[^]]*\]|@\d+;','?',raw)
    pieces=re.split(r'[.,\s]+',raw)
    x['tokens']=[w for w in pieces if re.fullmatch('[a-z]+',w)]
    x['language']=state[x['page']].get('L','?')
    x['hand']=state[x['page']].get('H','?')
    x['category']=state[x['page']].get('I','?')
    x['text_locus']=bool(re.search(r'P',x['loc'].split(',')[-1]))
text=[x for x in loci if x['text_locus'] and len(x['tokens'])>=2 and x['language'] in ('A','B')]
groups={letter:[x for x in text if x['language']==letter] for letter in ('A','B')}
all_tokens={g:[w for x in group for w in x['tokens']] for g,group in groups.items()}
res={'source':SRC.name,'docx_paragraphs':len(rows),'folio_headers':len(state),'loci_total':len(loci),'text_lines_clean_2plus':len(text),'rules':'paragraph-text loci with at least 2 lowercase unambiguous EVA tokens; editorial segments excluded, incomplete fragments may survive if not marked; results depend on transcription convention', 'groups':{}}
for g,xs in groups.items():
    tokens=all_tokens[g];cnt=collections.Counter(tokens)
    res['groups'][g]={'folio_count':len(set(x['page'] for x in xs)),'line_count':len(xs),'token_count':len(tokens),'unique_words':len(cnt),'top_words':cnt.most_common(12),'mean_token_length':round(sum(map(len,tokens))/len(tokens),3),'top_prefix_2':collections.Counter(w[:2] for w in tokens if len(w)>=2).most_common(8),'top_suffix_2':collections.Counter(w[-2:] for w in tokens if len(w)>=2).most_common(8)}
# JS divergence for common vocab on word counts
vocab=set(all_tokens['A'])|set(all_tokens['B']); cnts={g:collections.Counter(v) for g,v in all_tokens.items()}
def js(ca,cb):
    keys=set(ca)|set(cb);na=sum(ca.values());nb=sum(cb.values());
    pa=[ca[k]/na for k in keys];pb=[cb[k]/nb for k in keys]
    return float(jensenshannon(pa,pb,base=2)**2)
res['word_js_divergence_bits']=round(js(cnts['A'],cnts['B']),5)
# folio-weighted shuffle, preserve overall line and folio structure; word-frequency distributions differing on folio labels.
byfolio=collections.defaultdict(list)
for x in text:byfolio[x['page']].extend(x['tokens'])
folios={f:state[f].get('L','?') for f in byfolio}
Afolios=[f for f in byfolio if folios[f]=='A'];Bfolios=[f for f in byfolio if folios[f]=='B']
selected=Afolios+Bfolios
rng=random.Random(20261011)
obs=res['word_js_divergence_bits']; sims=[]
for _ in range(300):
    tmp=selected.copy();rng.shuffle(tmp)
    a=collections.Counter(w for f in tmp[:len(Afolios)] for w in byfolio[f]);b=collections.Counter(w for f in tmp[len(Afolios):] for w in byfolio[f])
    sims.append(js(a,b))
res['folio_label_permutation']={'trials':len(sims),'p_ge_obs':round((1+sum(v>=obs for v in sims))/(len(sims)+1),5),'mean_js':round(sum(sims)/len(sims),5),'note':'Randomizes folio A/B assignment while preserving folio text. Does not control for topical section or scribe.'}
OUT.write_text(json.dumps(res,indent=2),encoding='utf8')
print(json.dumps(res,indent=2))
