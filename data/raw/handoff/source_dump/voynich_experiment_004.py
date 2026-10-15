import re,collections,random
src=open('/mnt/data/voynich_heldout_f1v_f2r.txt').readlines()
rows=[]
for s in src:
 if not s.startswith('<f'):continue
 folio=s.split('>')[0][1:]
 raw=s.split('>',1)[1].strip().replace('<->','.')
 tokens=[x for x in re.split('[.,]',raw) if re.fullmatch('[a-z]+',x)]
 if len(tokens)>=2:rows.append((folio,tokens))

def ptest(lines,feature,seed=9041,N=10000):
 rng=random.Random(seed)
 g=lambda s: s[0] if feature=='first_glyph' else s[-1]
 alphabet=set(g(w) for line in lines for w in line)
 obs=collections.Counter(g(line[0]) for line in lines)
 exp=collections.Counter()
 for line in lines:
  for w in line:exp[g(w)]+=1/len(line)
 def chi(c):return sum((c[k]-exp[k])**2/(exp[k]+1e-3) for k in alphabet)
 measured=chi(obs)
 count=sum(chi(collections.Counter(g(rng.choice(line)) for line in lines))>=measured for _ in range(N))
 return (count+1)/(N+1),dict(obs),dict(exp)
for folio in ['f1v','f2r','combined']:
 selected=[line for tag,line in rows if folio=='combined' or tag.startswith(folio+'.')]
 print(folio,len(selected),sum(map(len,selected)))
 for feature in ['first_glyph','last_glyph']:
  p,obs,exp=ptest(selected,feature)
  print(feature,round(p,5), 'y first',obs.get('y',0), 'expected',round(exp.get('y',0),2),'o final',obs.get('o',0), 'expected',round(exp.get('o',0),2))
