"""Experiment 005: conditioned folio-level start-word analysis. No claims of translation.
Usage: python voynich_experiment_005.py [path-to-ZL3b-n.txt]
Source: Zandbergen-Landini ZL3b, May 2025, https://www.voynich.nu/data/ZL3b-n.txt
A strict primary analysis accepts only plain a-z words; a secondary relaxed
analysis splits unambiguous punctuation but drops ambiguous fragments.
"""
import re, random, collections, json, sys
from pathlib import Path

D=Path(__file__).resolve().parent

def from_reference(path):
    data=[]
    for line in path.read_text().splitlines():
        match=re.match(r'^<((?:f\d+[rv])\.\d+)(?:,[^>]*)?>\s*(.*)',line)
        if not match: continue
        locus, body=match.groups()
        body=re.sub(r'<![^>]*>|<%>|<\$>', '', body)
        body=body.replace('<->','.')
        words=[w for w in re.split(r'[.,]',body) if re.fullmatch(r'[a-z]+',w)]
        if len(words)>=2: data.append((locus.split('.')[0],words))
    return data

def from_full(path):
    lines=path.read_text(encoding='utf-8').splitlines()
    out=[]; metadata={}; folio=None
    for ln in lines:
        header=re.match(r'^<(f\d+[rv])>\s+<!([^>]*)>',ln)
        if header:
            folio=header.group(1)
            metadata[folio]=dict(re.findall(r'\$(\w)=([^\s>]+)',header.group(2)))
        match=re.match(r'^<(f\d+[rv])\.\d+,([^>]*)>\s*(.*)',ln)
        if not match:continue
        f,loc,body=match.groups()
        # paragraph text only; labels and circular writing excluded
        if not any(mark in loc for mark in ('P0','Pt')): continue
        body=re.sub(r'<![^>]*>|<%>|<\$>', '',body).replace('<->','.')
        words=[w for w in re.split(r'[.,]',body) if re.fullmatch(r'[a-z]+',w)]
        if len(words)>=2:out.append((f,words))
    return out,metadata

def run(lines,seed=408,n=5000):
    rng=random.Random(seed)
    # Surprise of initial token first/last character given each line's vocabulary
    res={}
    for part in ('initial','final'):
        feat=lambda s:s[0] if part=='initial' else s[-1]
        alphabet={feat(w) for ws in lines for w in ws}
        obs=collections.Counter(feat(ws[0]) for ws in lines)
        expected=collections.Counter()
        for ws in lines:
            for w in ws:expected[feat(w)]+=1/len(ws)
        def stat(ct): return sum((ct[c]-expected[c])**2/(expected[c]+0.001) for c in alphabet)
        measured=stat(obs)
        exceed=0
        for _ in range(n):
            ct=collections.Counter(feat(rng.choice(ws)) for ws in lines)
            exceed+=(stat(ct)>=measured)
        res[part]={'p':round((exceed+1)/(n+1),5),'stat':round(measured,3),
                   'observed_y':obs['y'],'expected_y':round(expected['y'],2),
                   'observed_final_o':obs['o'],'expected_final_o':round(expected['o'],2)}
    return res

if len(sys.argv)>1:
    source=Path(sys.argv[1]); rows,meta=from_full(source)
    groups={'Currier_A':[w for f,w in rows if meta.get(f,{}).get('L')=='A'],
            'Currier_B':[w for f,w in rows if meta.get(f,{}).get('L')=='B']}
    print('Full corpus lines accepted:',len(rows),'Currier groups:',[(k,len(v)) for k,v in groups.items()])
else:
    source=None
    rows=from_reference(D/'voynich_heldout_f1v_f2r.txt')+from_reference(D/'voynich_f3r_reference.txt')
    groups={f:[w for ff,w in rows if ff==f] for f in ('f1v','f2r','f3r')}
    groups['pooled_3_folios']=[w for _,w in rows]
report={'mode':'full_corpus' if source else 'heldout_sample', 'source':str(source) if source else 'f1v,f2r,f3r',
        'tests':{name:{'lines':len(ws),'tokens':sum(map(len,ws)),'results':run(ws)} for name,ws in groups.items() if ws}}
print(json.dumps(report,indent=2))
(D/'voynich_experiment_005_results.json').write_text(json.dumps(report,indent=2))
