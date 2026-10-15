from collections import Counter
import re,random,statistics
lines=open('/mnt/data/voynich_f1r_sample.txt').read().splitlines()
# Restrict to clean, unambiguous EVA strings; comma and dot both delimit units.
words=[[w for w in re.split(r'[.,]',line) if re.fullmatch('[a-z]+',w)] for line in lines]
tokens=[w for line in words for w in line]
def lev(a,b):
 p=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  q=[i]+[0]*len(b)
  for j,y in enumerate(b,1):q[j]=min(p[j]+1,q[j-1]+1,p[j-1]+(x!=y))
  p=q
 return p[-1]
pairs=[(a,b) for l in words for a,b in zip(l,l[1:]) if a!=b]
obs=sum(lev(a,b)==1 for a,b in pairs)/len(pairs)
# permutation preserves line lengths and all token frequencies while breaking local ordering.
random.seed(408)
null=[]
for _ in range(2000):
 shuffled=tokens[:];random.shuffle(shuffled);pos=0;cur=[]
 for l in words: cur.append(shuffled[pos:pos+len(l)]);pos+=len(l)
 pp=[(a,b) for l in cur for a,b in zip(l,l[1:]) if a!=b]
 null.append(sum(lev(a,b)==1 for a,b in pp)/len(pp))
print('lines',len(lines),'clean tokens',len(tokens),'unique',len(set(tokens)),'adjacent distinct pairs',len(pairs))
print('top',Counter(tokens).most_common(12))
print('edit-1 adjacent rate',round(obs,4),'null mean',round(statistics.mean(null),4),'null 95%',tuple(round(x,4) for x in sorted(null)[49::1900]))
print('permutation p', (1+sum(x>=obs for x in null))/2001)
obs2=sum(a[0]==b[0] for a,b in pairs)/len(pairs)
null2=[]
for _ in range(2000):
 shuffled=tokens[:];random.shuffle(shuffled);pos=0;cur=[]
 for l in words:cur.append(shuffled[pos:pos+len(l)]);pos+=len(l)
 pp=[(a,b) for l in cur for a,b in zip(l,l[1:]) if a!=b]
 null2.append(sum(a[0]==b[0] for a,b in pp)/len(pp))
print('same initial',round(obs2,4),'null mean',round(statistics.mean(null2),4),'permutation p',round((1+sum(x>=obs2 for x in null2))/2001,4))
