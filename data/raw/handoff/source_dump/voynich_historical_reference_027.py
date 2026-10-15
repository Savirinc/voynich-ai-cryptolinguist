import csv, collections, pathlib, json
BASE=pathlib.Path('/mnt/data')
SIGNS=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
# Chaldean decan sequence, traditional planetary order with Aries 0-9 = Mars.
DECANS=['Mars','Sun','Venus','Mercury','Moon','Saturn','Jupiter']
# Classical Egyptian terms/bounds, excerpt for four signs explicitly verified from source
TERMS={
 'Aries':[(6,'Jupiter'),(12,'Venus'),(20,'Mercury'),(25,'Mars'),(30,'Saturn')],
 'Taurus':[(8,'Venus'),(14,'Mercury'),(22,'Jupiter'),(27,'Saturn'),(30,'Mars')],
 'Gemini':[(6,'Mercury'),(12,'Jupiter'),(17,'Venus'),(24,'Mars'),(30,'Saturn')],
 'Cancer':[(7,'Mars'),(13,'Venus'),(19,'Mercury'),(26,'Jupiter'),(30,'Saturn')],
}
reference=[]
for si,sign in enumerate(SIGNS):
 for degree in range(30):
  absolute=si*30+degree
  decan_index=absolute//10
  decan_ruler=DECANS[decan_index%7]
  bound=next((name for end,name in TERMS.get(sign,[]) if degree<end),None)
  reference.append({'sign':sign,'degree_index_0_29':degree,'longitude_tropical_deg':absolute,'decan_1_3':degree//10+1,'chaldean_decan_ruler':decan_ruler,'egyptian_bound_ruler_verified_4_signs_only':bound or '', 'degree_is_hypothesis_for_voynich':True})
with open(BASE/'voynich_historical_zodiac_reference_027.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=reference[0]);w.writeheader();w.writerows(reference)
with open(BASE/'voynich_zodiac_slot_map.csv',newline='') as f: rows=list(csv.DictReader(f))
# Explicitly NO degree mapping. Group statistics only.
counts=collections.Counter(r['sign'] for r in rows)
coverage=[]
for s in SIGNS:
 if counts.get(s):
  coverage.append({'sign':s,'recorded_labels':counts[s], 'expected_degree_slots':30, 'missing_vs_30':30-counts[s], 'reading_order_verified':False, 'matching_rulers_calculated':False})
with open(BASE/'voynich_zodiac_coverage_027.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=coverage[0]);w.writeheader();w.writerows(coverage)
report={'voynich_labeled_records':len(rows),'surviving_signs':len(coverage),'reference_degree_rows':len(reference),'egyptian_bound_reference_rows':len([r for r in reference if r['egyptian_bound_ruler_verified_4_signs_only']]),'missing_label_slots':sum(x['missing_vs_30'] for x in coverage),'matching_to_voynich_performed':False,'reason':'Unverified inter-ring reading order and missing labels prevent sound degree-to-label assignments.','historical_sources':['https://www.loc.gov/item/2021667703/','https://webspace.science.uu.nl/~gent0113/ulughbeg/ulughbeg_star_catalogue.htm','https://www.spucchi.com/wiki/astrology/terms-bounds-essential-dignities/term-tables/']}
(BASE/'voynich_historical_audit_027.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
