"""Audit whether transcriber clock positions independently support 30 equal zodiac degrees.
Uses previously extracted CSV; positions are coarse annotations, not pixel coordinates.
"""
import csv,json,math,statistics,collections
from pathlib import Path
base=Path(__file__).parent
rows=list(csv.DictReader(open(base/'voynich_zodiac_clock_positions.csv',encoding='utf8')))
result={"purpose":"test how well annotated clock positions constrain geometric degree hypotheses","caveat":"clock annotations are transcriber approximations, not measured nymph/star centroids; no zodiac longitude assigned","panels":{}}
for folio in dict.fromkeys(x['folio'] for x in rows):
    subset=[x for x in rows if x['folio']==folio]
    angles=[float(x['angle_clockwise_from_top_deg']) for x in subset]
    n=len(angles)
    sortedang=sorted(angles)
    gaps=[(sortedang[(i+1)%n]-sortedang[i])%360 for i in range(n)]
    unique=len(set(angles))
    # Ideal projection for n equally spaced marks can be rotated; compare sorted positions to ideal phase
    # duplicates and coarse positions prevent reliable match even for true equal-spacing source
    result['panels'][folio]={"labels":n,"unique_clock_angles":unique,"duplicate_positions":n-unique,"median_sorted_angular_gap_deg":statistics.median(gaps),"zero_gaps":sum(abs(x)<1e-9 for x in gaps),"ideal_even_spacing_deg":360/n,"distinct_angles_allow_one_to_one_degree_assignment":unique==n}
result['totals']={"records":len(rows),"unique_position_count_sum":sum(x['unique_clock_angles'] for x in result['panels'].values()),"duplicate_annotations":sum(x['duplicate_positions'] for x in result['panels'].values()),"panels_with_duplicate_angles":sum(x['duplicate_positions']>0 for x in result['panels'].values()),"panels_with_30_records":sum(x['labels']==30 for x in result['panels'].values())}
(base/'voynich_experiment_023_results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result['totals'],indent=2))
for k,v in result['panels'].items(): print(k,v['labels'],v['unique_clock_angles'],v['median_sorted_angular_gap_deg'])
