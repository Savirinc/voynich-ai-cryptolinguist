"""Analyze shared Voynichese word-building structure in Currier A/B. Uses parser from Experiment 014, preserving its caveats."""
import runpy, collections, json, math, random
from pathlib import Path
D=runpy.run_path('/mnt/data/voynich_full_experiment_014.py')
groups=D['all_tokens']; rng=random.Random(15015)
def features(words):
 c=collections.Counter(words); n=sum(c.values())
 pref=collections.Counter(w[:2] for w in words if len(w)>=3)
 suff=collections.Counter(w[-2:] for w in words if len(w)>=3)
 starts=collections.Counter(w[0] for w in words)
 ends=collections.Counter(w[-1] for w in words)
 # one-edit morphological neighborhood for frequent words
 common=[w for w,v in c.items() if v>=5]
 return {'n':n,'unique':len(c),'prefix_top':pref.most_common(12),'suffix_top':suff.most_common(12),'initial_top':starts.most_common(10),'final_top':ends.most_common(10),'frequent_word_forms':len(common)}
result={'method':'clean-paragraph-word parsing inherited from Experiment 014; compare prefix/suffix distributions and word-family changes, without inferring meaning','groups':{k:features(v) for k,v in groups.items()}}
A=set(groups['A']);B=set(groups['B']);common=A&B
result['vocab']={'A_unique':len(A),'B_unique':len(B),'shared_types':len(common),'type_jaccard':round(len(common)/len(A|B),4),'shared_token_fraction_A':round(sum(w in common for w in groups['A'])/len(groups['A']),4),'shared_token_fraction_B':round(sum(w in common for w in groups['B'])/len(groups['B']),4)}
# prefixes/suffixes normalized and cosine similarity; find frequent divergences
for kind in ['prefix','suffix']:
 def feat(w):return w[:2] if kind=='prefix' else w[-2:]
 counts={k:collections.Counter(feat(w) for w in words if len(w)>=3) for k,words in groups.items()}
 keys=counts['A'].keys()|counts['B'].keys(); aa=counts['A'];bb=counts['B']; cosine=sum(aa[t]*bb[t] for t in keys)/math.sqrt(sum(x*x for x in aa.values())*sum(x*x for x in bb.values()))
 result[kind]={'cosine':round(cosine,4),'largest_relative_differences':sorted([{'unit':t,'A_pct':round(100*aa[t]/sum(aa.values()),2),'B_pct':round(100*bb[t]/sum(bb.values()),2),'absolute_percentage_point_difference':round(abs(100*aa[t]/sum(aa.values())-100*bb[t]/sum(bb.values())),2)} for t in keys if aa[t]+bb[t]>=150],key=lambda o:-o['absolute_percentage_point_difference'])[:12]}
# edit-1 pairs among frequent tokens, versus their co-presence in groups
freq=collections.Counter(groups['A']+groups['B']); eligible=[w for w,n in freq.items() if n>=15]
def dist1(a,b):
 if abs(len(a)-len(b))>1:return False
 if len(a)==len(b):return sum(x!=y for x,y in zip(a,b))==1
 if len(a)>len(b):a,b=b,a
 i=j=diff=0
 while i<len(a) and j<len(b):
  if a[i]==b[j]:i+=1;j+=1
  else:
   diff+=1;j+=1
   if diff>1:return False
 return True
pairs=[]
for i,a in enumerate(eligible):
 for b in eligible[i+1:]:
  if dist1(a,b):pairs.append((freq[a]+freq[b],a,b,collections.Counter(groups['A'])[a],collections.Counter(groups['B'])[a],collections.Counter(groups['A'])[b],collections.Counter(groups['B'])[b]))
result['word_families']={'frequent_word_threshold':15,'eligible_word_forms':len(eligible),'edit_distance_1_pairs':len(pairs),'examples':[{'words':[a,b],'A_counts':[ca,da],'B_counts':[cb,db]} for _,a,b,ca,cb,da,db in sorted(pairs,reverse=True)[:18]],'caveat':'Orthographic resemblance cannot establish etymological or grammatical relation'}
out=Path('/mnt/data/voynich_experiment_015_results.json');out.write_text(json.dumps(result,indent=2)); print(json.dumps({k:v for k,v in result.items() if k not in ('groups','word_families')},indent=2));print('families',result['word_families']['edit_distance_1_pairs']);print(result['word_families']['examples'][:10])
