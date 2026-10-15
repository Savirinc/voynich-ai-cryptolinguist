"""Experiment 006: calibrated Caesar attack and cipher invariants.
Run: python voynich_experiment_006.py
Sources: local hand-transcribed folio snippets f1r f1v f2r f3r from earlier experiments.
Limitations: EVA letters are transliteration units, NOT necessarily atomic manuscript glyphs.
"""
import collections, json, math, random, re
from pathlib import Path
P=Path(__file__).resolve().parent
ENG_FREQ={'a':8.167,'b':1.492,'c':2.782,'d':4.253,'e':12.702,'f':2.228,'g':2.015,'h':6.094,'i':6.966,'j':.153,'k':.772,'l':4.025,'m':2.406,'n':6.749,'o':7.507,'p':1.929,'q':.095,'r':5.987,'s':6.327,'t':9.056,'u':2.758,'v':.978,'w':2.360,'x':.150,'y':1.974,'z':.074}
BASE="""The purpose of a cipher is to conceal a message while preserving enough structure for the intended reader to recover the original words. A careful analyst counts symbols, measures their order, and compares possible solutions against independent examples. A plausible sentence is not sufficient evidence of success because flexible interpretation can produce countless stories. A valid solution uses the same rules across different pages, anticipates unseen material, and can be tested without knowing the expected answer. The manuscript contains many repeated signs and short groups of signs. Some signs appear together more often than others. Repetition may reveal how a writing system works, but repetition alone cannot establish what the author wished to communicate. We need both a structural model and independent evidence of meaning. A good experiment can reject its own favorite explanation when the evidence does not support it."""
def caesar(s,k): return ''.join(chr((ord(c)-97+k)%26+97) if 'a'<=c<='z' else c for c in s)
def chisq(s):
 letters=[c for c in s if 'a'<=c<='z']; cnt=collections.Counter(letters); n=len(letters)
 return sum((cnt[chr(97+i)]-n*ENG_FREQ[chr(97+i)]/100)**2/(n*ENG_FREQ[chr(97+i)]/100) for i in range(26))
def scan(s):return sorted([(k,round(chisq(caesar(s,-k)),3)) for k in range(26)],key=lambda z:z[1])
def metrics(s):
 s=''.join(c for c in s.lower() if 'a'<=c<='z'); n=len(s); ct=collections.Counter(s); pairs=collections.Counter(zip(s,s[1:])); prev=collections.Counter(s[:-1]);
 ic=sum(v*(v-1) for v in ct.values())/(n*(n-1))
 cond=-sum(v/(n-1)*math.log2(v/prev[a]) for (a,b),v in pairs.items())
 return {'n_characters':n,'distinct_characters':len(ct),'index_coincidence':round(ic,5),'conditional_entropy_bits':round(cond,4),'top_symbols':ct.most_common(8)}
# Strict sample: only plain a-z dot/comma-separated tokens; ambiguous annotation dropped.
lines=[]
for filename in ['voynich_f1r_sample.txt','voynich_heldout_f1v_f2r.txt','voynich_f3r_reference.txt']:
 for line in (P/filename).read_text().splitlines():
  if line.startswith('#'):continue
  line=re.sub(r'^<[^>]+>\s*','',line)
  words=[w for w in re.split(r'[.,\s]+',line) if re.fullmatch('[a-z]+',w)]
  if words: lines.extend(words)
voy=''.join(lines)
english=''.join(c for c in BASE.lower() if c.isascii() and c.isalpha())
key=11; cipher=caesar(english,key); ranked=scan(cipher)
rng=random.Random(408)
def shuffle(s):
 a=list(s);rng.shuffle(a);return ''.join(a)
report={
 'test_A_known_caesar':{'shift_used':key,'best_shift':ranked[0][0],'top_3':ranked[:3],'exactly_recovered':caesar(cipher,-ranked[0][0])==english,'english_original_metrics':metrics(english),'english_cipher_metrics':metrics(cipher)},
 'test_B_voynich':{'sample_files':['voynich_f1r_sample.txt','voynich_heldout_f1v_f2r.txt','voynich_f3r_reference.txt'],'accepted_tokens':len(lines),'voynich_metrics':metrics(voy),'shuffled_voynich_metrics':metrics(shuffle(voy)),'caesar_scan_top3':scan(voy)[:3]},
 'warnings':['Caesar ciphertext recovery is a toy calibration, not a Voynich decipherment.','EVA characters are not guaranteed to correspond one-to-one with genuine Voynich glyphs.','Samples are early Currier A folios; not representative of full manuscript.','Shuffling concatenated letters destroys word boundaries and is only a coarse order baseline.','English baseline is a short authored demonstration, not a medieval language corpus.']}
(P/'voynich_experiment_006_results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
