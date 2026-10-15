"""Voynich experiment 003: test line-initial signals after removing paragraph openings.
Primary source: Zandbergen-Landini v3b (2025), f1r, hand-transcribed sample from previous experiment.
This is NOT a whole-manuscript test. All tests condition on the words in each line.
"""
import re, random, collections, json
from pathlib import Path
raw=Path('/mnt/data/voynich_f1r_sample.txt').read_text().splitlines()
paragraph_start_lines={1,7,11,22} # numbering as in ZL3b; 1-based physical lines
paragraph_terminal_lines={6,10,21,28}
records=[]
for i,s in enumerate(raw,1):
    # Keep only complete alphabetic tokens; ambiguous forms discarded, not repaired.
    words=[w for w in re.split(r'[.,]',s.strip()) if re.fullmatch('[a-z]+',w)]
    if len(words)>=2:
        records.append(dict(number=i,words=words, paragraph_start=i in paragraph_start_lines,
                            paragraph_end=i in paragraph_terminal_lines))
def test(recs,part='start', position='first',n=10000,seed=408):
    rng=random.Random(seed)
    get=(lambda w:w[0]) if part=='start' else (lambda w:w[-1])
    alphabet=sorted({get(w) for row in recs for w in row['words']})
    expected=collections.Counter()
    for row in recs:
        words=row['words']
        for w in words: expected[get(w)]+=1/len(words)
    observed=collections.Counter(get(row['words'][0 if position=='first' else -1]) for row in recs)
    def stat(counts):return sum((counts[x]-expected[x])**2/(expected[x]+1e-3) for x in alphabet)
    v=stat(observed)
    more=0
    for _ in range(n):
        candidate=collections.Counter(get(rng.choice(row['words'])) for row in recs)
        more += stat(candidate)>=v
    return {'n_lines':len(recs),'statistic':round(v,3),'p':round((more+1)/(n+1),5),
            'observed':dict(observed.most_common()),'expected':{k:round(v,2) for k,v in expected.items()}}
subsets={'all_lines':records,'not_paragraph_start':[r for r in records if not r['paragraph_start']],
         'nonparagraph_long_lines':[r for r in records if not r['paragraph_start'] and len(r['words'])>=6],
         'paragraph_start_only':[r for r in records if r['paragraph_start']]}
results={subset:{f'{part}_{pos}':test(rows,part,pos) for part in ['start','end'] for pos in ['first','last']} for subset,rows in subsets.items()}
out='/mnt/data/voynich_experiment_003_results.json'
Path(out).write_text(json.dumps(results,indent=2))
for name, tests in results.items():
    print(name, 'n=',len(subsets[name]),'p=',{k:round(v['p'],4) for k,v in tests.items()})
print('Saved:',out)
