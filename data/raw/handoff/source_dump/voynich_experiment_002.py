import re,random,collections,statistics,json
p='/mnt/data/voynich_f1r_sample.txt'
lines=[]
for s in open(p):
    w=[x for x in re.split('[.,]',s.strip()) if re.fullmatch('[a-z]+',x)]
    if len(w)>=2:lines.append(w)
print('lines',len(lines),'lengths',collections.Counter(map(len,lines)))
print('token count',sum(map(len,lines)))
print('first ends',collections.Counter(w[0][-1] for w in lines))
print('last ends',collections.Counter(w[-1][-1] for w in lines))
print('internal ends',collections.Counter(w[-1] for line in lines for w in line[1:-1]))
print('first starts',collections.Counter(w[0][0] for w in lines))
print('last starts',collections.Counter(w[-1][0] for w in lines))
print('internal starts',collections.Counter(w[0] for line in lines for w in line[1:-1]))
# line-conditional permutation keeps each line vocab and sample content fixed
rng=random.Random(408)
def chi(observed, expected):return sum((a-b)**2/(b+.001) for a,b in zip(observed,expected))
for typ in ['initial','terminal']:
 for feature in ['first','last']:
  get=lambda w: w[0] if typ=='initial' else w[-1]
  N=len(lines)
  obs=collections.Counter(get(line[0 if feature=='first' else -1]) for line in lines)
  alphabet=sorted(set(get(w) for line in lines for w in line))
  expectation=collections.Counter()
  for line in lines:
   for w in line: expectation[get(w)]+=1/len(line)
  stat=chi([obs[c] for c in alphabet],[expectation[c] for c in alphabet])
  sims=[]
  for _ in range(5000):
   sim=collections.Counter(get(rng.choice(line)) for line in lines)
   sims.append(chi([sim[c] for c in alphabet],[expectation[c] for c in alphabet]))
  p=(1+sum(v>=stat for v in sims))/(1+len(sims))
  print(typ,feature,'observed',obs.most_common(6),'stat',round(stat,3),'null_mean',round(statistics.mean(sims),3),'p',round(p,4))
