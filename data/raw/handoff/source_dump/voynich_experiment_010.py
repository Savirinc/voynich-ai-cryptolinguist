"""Pilot only. Local Voynich EVA vs public domain Chaucer source, matched token count.
For full historical-language scoring, replace manual Chaucer excerpt with licensed corpora,
add genre controls and multiple unrelated texts, and normalize across glyphs.
"""
from pathlib import Path
import importlib.util, json, random, statistics
root=Path(__file__).parent
spec=importlib.util.spec_from_file_location('exp008',root/'voynich_experiment_008.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
vs=[]
for s in m.SOURCES: vs += m.tokens((root/s).read_text(),voy=True)
ch=m.tokens((root/'voynich_middle_english_pilot.txt').read_text())
n=min(len(vs),len(ch)); rng=random.Random(20261011)
# Matched word count; multiple random subsets from larger Voynich text.
V=[]
for i in range(200):
 x=rng.sample(vs,n)
 V.append(m.features(x)['within_word_conditional_entropy'])
C=m.features(ch[:n]); Vfull=m.features(vs)
# permutation null for Chaucer tokens, preserve word lengths and inventory
shuffles=[]
for _ in range(200):
 w=ch[:n]; flat=list(''.join(w));rng.shuffle(flat); ix=0; made=[]
 for word in w:
  made.append(''.join(flat[ix:ix+len(word)]));ix+=len(word)
 shuffles.append(m.features(made)['within_word_conditional_entropy'])
out={'status':'pilot_real_middle_english_not_language_identification','voynich_source':'local early-folio samples, normalized EVA','chaucer_source':'Canterbury Tales General Prologue, Gutenberg 22120 lines 1344-1385, hand-extracted and orthographically simplified','chaucer_word_count':len(ch),'matched_word_count':n,'chaucer':C,'voynich_complete_local_sample':Vfull,'voynich_equal_size_entropy_mean':statistics.mean(V),'voynich_equal_size_entropy_range':[min(V),max(V)],'chaucer_shuffled_character_entropy_mean':statistics.mean(shuffles),'limitations':['Chaucer excerpt short and poetic; manual punctuation removal and conversion of diacritics','Different alphabets and EVA encoding bias comparisons','No cipher simulation and no language-family identification','Sampling without replacement from small early folio sample; not independent across repeats']}
(root/'voynich_experiment_010_results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['chaucer','voynich_complete_local_sample']},indent=2))
print('Chaucer actual entropy',C['within_word_conditional_entropy'],'Voynich all',Vfull['within_word_conditional_entropy'])
