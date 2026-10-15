import pandas as pd, json
from collections import Counter
p='/mnt/data/voynich_tournament_064/indexed_clean_corpus.csv'
df=pd.read_csv(p).fillna('')
df['EVA']=df.EVA.astype(str)
lex={'chedy':'DEUS','shedy':'HEUS','lchedy':'MEUS','qol':'NON','qokol':'NOCET','chol':'DAT','daiin':'OLEUM','oly':'FLOS','okaiin':'FOCUM'}
cnt=Counter(df.EVA)
rows=[]
for eva,proposal in lex.items():
    sub=df[df.EVA.eq(eva)]
    sections=sub.section.value_counts().to_dict()
    rows.append(dict(EVA=eva,claimed_plaintext=proposal,total=len(sub),distinct_folios=sub.folio.nunique(),sections=sections,first_examples=sub[['folio','line_id']].head(6).to_dict('records')))
linegroups=df.groupby(['folio','line_id']).EVA.agg(list)
colocs={}
for a,b in [('chedy','qol'),('chedy','chol'),('qol','qokol'),('chedy','shedy')]:
    both=sum(a in v and b in v for v in linegroups)
    colocs[f'{a} & {b}']=both
res={'total_tokens':len(df),'most_common':cnt.most_common(20),'claims':rows,'claim_line_colocations':colocs}
with open('/mnt/data/voynich_solution_audit_068.json','w') as f:json.dump(res,f,indent=2)
for r in rows:print(r['EVA'],r['claimed_plaintext'],r['total'],r['distinct_folios'],r['sections'])
print('colocations',colocs)
