"""Experiment 011: reversible digraph tokenizer control on attested Chaucer pilot and local Voynich sample.
Demonstrates segmentation-dependent entropy, NOT decipherment.
"""
import importlib.util, json, collections
from pathlib import Path
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('v008',ROOT/'voynich_experiment_008.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
V=sum([m.tokens((ROOT/s).read_text(),voy=True) for s in m.SOURCES],[])
E=m.tokens((ROOT/'voynich_middle_english_pilot.txt').read_text())

def segmented(words, pairs):
    pairs=set(pairs); output=[]
    for w in words:
        units=[]; i=0
        while i<len(w):
            if i+1<len(w) and w[i:i+2] in pairs:
                units.append(w[i:i+2]); i+=2
            else:
                units.append(w[i]);i+=1
        assert ''.join(units)==w
        output.append(units)
    return output

def h2(unit_words):
    pair=collections.Counter((a,b) for w in unit_words for a,b in zip(w,w[1:])); prev=collections.Counter(a for w in unit_words for a in w[:-1]); n=sum(pair.values())
    import math
    return round(-sum(v/n*math.log2(v/prev[a]) for (a,b),v in pair.items()),4)

def desc(words,pairs):
    seq=segmented(words,pairs)
    return {'words':len(words),'units':sum(map(len,seq)),'distinct_units':len(set(u for w in seq for u in w)), 'H_next_unit_bits':h2(seq),'units_per_word':round(sum(map(len,seq))/len(seq),3)}

def top_pairs(words):
    counts=collections.Counter(w[i:i+2] for w in words for i in range(len(w)-1))
    return [p for p,c in counts.most_common(5)]

pE=top_pairs(E);pV=top_pairs(V)
out={'method':'Greedy nonoverlapping reversible digraph tokenization, respecting word boundaries. Compare baseline (letters only), ch/sh and five most frequent within-word digraphs chosen independently per corpus.',
     'middle_english_source':'local hand-extracted Chaucer sample, not a representative language corpus',
     'voynich_source':'four early local EVA folio samples, ambiguous tokens excluded',
     'middle_english_pairs':pE,'voynich_pairs':pV,
     'middle_english':{'letters':desc(E,[]),'ch_sh':desc(E,['ch','sh']),'five_common_pairs':desc(E,pE)},
     'voynich':{'letters':desc(V,[]),'ch_sh':desc(V,['ch','sh']),'five_common_pairs':desc(V,pV)},
     'limitations':['A digraph token is a reversible recoding, not a demonstrated medieval cipher.','Entropy per token cannot be compared directly across tokenizations with different units per word.','Different reference genres, text lengths, and EVA glyph conventions confound language inference.','No plaintext, cipher key, or matched historical-language result recovered.']}
(ROOT/'voynich_experiment_011_results.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
