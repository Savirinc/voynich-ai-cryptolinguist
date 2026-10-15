#!/usr/bin/env python3
"""Voynich ZL3b-n IVTFF reproducible first-word/word-form analysis.
Source: https://www.voynich.nu/data/ZL3b-n.txt (13 May 2025).
Usage: python voynich_full_corpus_analysis.py --download
   or: python voynich_full_corpus_analysis.py --input ZL3b-n.txt
Requires only Python standard library; web access required only for --download.
Conservative handling: exclude ambiguous tokens, labels, marginalia, non-paragraph text.
Exploratory statistical association, NOT decipherment or language identification.
"""
import argparse, collections, json, math, pathlib, random, re, urllib.request
URL='https://www.voynich.nu/data/ZL3b-n.txt'
FOLIO=re.compile(r'^<(f\d+[rv](?:\d+)?)>\s*<!([^>]*)>')
LINE=re.compile(r'^<(f\d+[rv](?:\d+)?)[.](\d+),([^>]*)>\s*(.*)$')
META=re.compile(r'\$L=([AB])')
def parse(raw):
    folio=None; lang=None; rows=[]; nf=collections.Counter()
    for s in raw.splitlines():
        m=FOLIO.match(s)
        if m:
            folio=m.group(1); t=META.search(m.group(2)); lang=t.group(1) if t else None
            continue
        m=LINE.match(s)
        if not m: continue
        page,number,layout,content=m.groups()
        # Only running paragraph lines; omit labels, diagram text, miscellany.
        if not re.search(r'(?:[@+*=]P|=Pt)',layout): continue
        # Strip IVTFF annotation without inventing glyphs. Angle-markup can include special chars.
        content=re.sub(r'<!.*?>','',content)
        content=re.sub(r'<[^>]*>','.',content)
        content=re.sub(r'\[[^\]]*\]|\{[^}]*\}','?',content)
        words=[w for w in re.split(r'[.,\s;:]+',content) if re.fullmatch(r'[a-z]+',w)]
        if len(words)>=3:
            rows.append({'folio':page,'line':int(number),'language':lang,'paragraph_start':'@P' in layout or '*P' in layout,'tokens':words})
            nf[page]+=1
    return rows,nf

def js_distance(first,rest):
    a=collections.Counter(first); b=collections.Counter(rest)
    n=sum(a.values());k=sum(b.values());out=0
    if not n or not k:return None
    for t in a.keys()|b.keys():
        p=a[t]/n;q=b[t]/k;m=(p+q)/2
        if p:out+=p*math.log2(p/m)/2
        if q:out+=q*math.log2(q/m)/2
    return out

def test(rows,n=2000,seed=408):
    rng=random.Random(seed)
    eligible=[r['tokens'][:-1] for r in rows if len(r['tokens'])>=4]
    result={'eligible_lines':len(eligible),'eligible_tokens':sum(len(x) for x in eligible)}
    for feature in ('initial','ending'):
        fn=(lambda w:w[0]) if feature=='initial' else (lambda w:w[-1])
        obs=js_distance([fn(x[0]) for x in eligible],[fn(w) for x in eligible for w in x[1:]])
        more=0
        for _ in range(n):
            left=[];right=[]
            for x in eligible:
                ix=rng.randrange(len(x));left.append(fn(x[ix]));right.extend(fn(w) for j,w in enumerate(x) if j!=ix)
            s=js_distance(left,right)
            if s is not None and obs is not None and s>=obs:more+=1
        result[feature]={'JS_bits':round(obs,5) if obs is not None else None,'permutation_p':round((more+1)/(n+1),6)}
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input');ap.add_argument('--download',action='store_true');ap.add_argument('--out',default='voynich_full_corpus_results.json');ap.add_argument('--permutations',type=int,default=2000)
    args=ap.parse_args()
    if args.download:
        with urllib.request.urlopen(URL,timeout=35) as response: raw=response.read().decode('utf-8-sig')
        pathlib.Path('ZL3b-n.txt').write_text(raw,encoding='utf-8')
    elif args.input:raw=pathlib.Path(args.input).read_text(encoding='utf-8-sig')
    else:ap.error('provide --input FILE or --download')
    rows,nf=parse(raw)
    report={'source':URL,'source_lines':len(raw.splitlines()),'parsed_paragraph_lines':len(rows),'folio_count':len(nf),'tokens':sum(len(r['tokens']) for r in rows),'parsing_notes':'Conservative text-only paragraphs; uncertain words omitted; EVA letters are not necessarily individual glyphs','groups':{}}
    for group,subset in [('all',rows),('Currier A',[r for r in rows if r['language']=='A']),('Currier B',[r for r in rows if r['language']=='B']),('not_paragraph_openings',[r for r in rows if not r['paragraph_start']])]:
        report['groups'][group]=test(subset,args.permutations)
    pathlib.Path(args.out).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
