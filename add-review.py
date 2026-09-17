#!/usr/bin/env python3
# add-review.py <json-file>: append accepted reviews to claims/index.json and set status/verified.
# Each item: {n, by, verdict, range, run, code, block, paid_nano, bond_withheld_nano, bond_due, accepted, verified?(optional str)}
import json,sys
items=json.load(open(sys.argv[1]))
p='claims/index.json'; d=json.load(open(p)); by_n={c['n']:c for c in d}
for it in items:
    c=by_n[it['n']]; c.setdefault('reviews',[])
    if any(r['run']==it['run'] for r in c['reviews']): print('already',it['n'],it['by']); continue
    c['reviews'].append({k:it[k] for k in ('by','verdict','range','accepted','run','code','paid_nano','bond_withheld_nano','bond_due','block')})
    ops={r['by'].split(' (')[0].split('/')[0].strip() for r in c['reviews'] if r['verdict']=='reproduces'}
    if len(ops)>=2 and c['status']=='open': c['status']='survived'
    if it.get('verified'): c['verified']=it['verified']
    print('added',it['n'],it['by'],'->',c['status'])
json.dump(d,open(p,'w'),indent=1,ensure_ascii=False); open(p,'a').write('\n')
