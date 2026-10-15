from docx import Document
import re,csv,json,collections,math
source='/mnt/data/IVTFF Eva.txt.docx'
lines=[p.text for p in Document(source).paragraphs]
panels=['f70v2','f71r','f71v','f72r1','f72r2','f72r3','f72v1','f72v2','f72v3','f73r','f73v']
# Include all tagged zodiac folios automatically, not manually supplied sign assignments.
active=None; entries=[]; counts=collections.Counter(); skipped=[]
for line in lines:
 m=re.match(r'^<([^>.]+)>\s*<!',line)
 if m: active=m.group(1)
 m=re.match(r'^<([^>.]+)\.(\d+),([^>]+)>\s*(.*)',line)
 if not m: continue
 folio,idx,loc,tail=m.groups()
 if not (loc.startswith('&Lz') or loc.startswith('@Lz')): continue
 pos=re.search(r'<!\s*(\d\d):(\d\d)',tail)
 if not pos:
  skipped.append({'folio':folio,'record':idx,'reason':'no recorded clock position','raw':tail[:90]}); continue
 hr,mi=map(int,pos.groups())
 if hr>12 or mi>=60:
  skipped.append({'folio':folio,'record':idx,'reason':'invalid clock position','raw':tail[:90]});continue
 # clock at top 00:00, increasing clockwise. Angle not automatically astronomical angle.
 angle=((hr%12)*60+mi)/720*360
 raw=re.sub(r'^<![^>]*>', '', tail).strip()
 valid=bool(re.fullmatch(r'[a-z]+(?:[.,][a-z]+)*',raw))
 entries.append({'folio':folio,'record':int(idx),'loc':loc,'clock_position':f'{hr:02d}:{mi:02d}','angle_clockwise_from_top_deg':round(angle,2),'raw_transcription':raw,'unambiguous_simple':valid})
 counts[folio]+=1
out='/mnt/data/voynich_zodiac_clock_positions.csv'
with open(out,'w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(entries[0]));w.writeheader();w.writerows(entries)
report={'source':'User-provided Zandbergen-Landini IVTFF EVA version 3b; not independent celestial coordinates','clock_position_records':len(entries),'counts_by_panel':dict(counts),'without_parseable_clock_position':len(skipped),'clock_positions_are_transcriber_page_locations_not_star_coordinates':True,'no_verified_starting_degree_or_direction':True,'examples':entries[:8],'omissions':skipped[:12]}
with open('/mnt/data/voynich_zodiac_coordinate_report.json','w') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2)[:4500])
