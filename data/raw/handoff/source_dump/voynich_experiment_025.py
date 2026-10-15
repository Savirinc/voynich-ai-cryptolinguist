"""Build source-preserving zodiac label map from uploaded ZL3b DOCX and prior extracted positions.
No astronomical interpretations are inferred from raw clock annotations.
"""
import re, csv, json
from collections import Counter,defaultdict
from docx import Document
SOURCE='/mnt/data/IVTFF Eva.txt.docx'
lines='\n'.join(p.text for p in Document(SOURCE).paragraphs).splitlines()
signs={'f70v2':'Pisces','f70v1':'Aries','f71r':'Aries','f71v':'Taurus','f72r1':'Taurus','f72r2':'Gemini','f72r3':'Cancer','f72v3':'Leo','f72v2':'Virgo','f72v1':'Libra','f73r':'Scorpio','f73v':'Sagittarius'}
# Notes are not uniformly worded across folios; explicit ring labeling is only used where identifiable.
rows=[]; current=None; ring='unspecified'; panel_order=0
for s in lines:
    m=re.match(r'^<(f\d+[rv]\d?)>\s',s)
    if m:
        current=m.group(1);ring='unspecified';panel_order=0
        continue
    if current not in signs:continue
    low=s.lower()
    if s.lstrip().startswith('#'):
        if re.search(r'inner (ring|band)|innermost (ring|band)',low): ring='inner'
        elif re.search(r'middle (ring|band)|middle band',low):ring='middle'
        elif re.search(r'outer (ring|band)|outermost (ring|band)',low):ring='outer'
    m=re.match(r'^<(f\d+[rv]\d?)\.(\d+),([^>]*)>\s*<!([0-9]{2}:[0-9]{2})>(.*)',s)
    if not m or m.group(1)!=current or 'Lz' not in m.group(3):continue
    panel_order+=1
    f,rec,loc,clock,word=m.groups()
    hh,mm=map(int,clock.split(':'))
    angle=round(((hh%12)*60+mm)/2,2)
    rows.append({'folio':f,'sign':signs[f],'record':int(rec),'transcription_order':panel_order,'ring':ring,
                 'clock_position':clock,'angle_deg_clockwise_from_top':angle,'voynich_label':word.strip(),
                 'ambiguous_label':bool(re.search(r'[\[\]{}?@!]',word)),
                 'hypothetical_sign_degree':None,'validation':'ring and circular order need image inspection'})
# Rank within each identified ring in transcription order (NOT astronomical degree assignment).
groups=defaultdict(list)
for r in rows:groups[(r['folio'],r['ring'])].append(r)
for _,items in groups.items():
    for i,r in enumerate(items,1):r['ordinal_within_recorded_ring']=i
path='/mnt/data/voynich_zodiac_slot_map.csv'
with open(path,'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
stats={x:{'count':len([r for r in rows if r['folio']==x]),'rings':dict(Counter(r['ring'] for r in rows if r['folio']==x))} for x in signs}
report={'source':SOURCE,'rows':len(rows),'panels':stats,'warning':'These are transcription-order labels, not celestial degree assignments. Ring markers are inferred only from explicit comments and may be incomplete. Image-level verification required.'}
with open('/mnt/data/voynich_experiment_025_results.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
