#!/usr/bin/env python3
"""List claims-pilot bond returns that are due (README: 0.2 XNO, 7 days after acceptance, unless a
later run overturned the verdict). Address = link_as_account of the review's payment block, from the
local node. Groups by reviewer+address so one send per reviewer covers all their bonds.

  bonds-due.py [YYYY-MM-DD]            list due-and-unreturned as of that date (default today)
  bonds-due.py --mark <address> <block> <date>  set bond_returned={block,date} on every listed review
                                       for that address whose bond_due <= date
"""
import json, sys, datetime, urllib.request
IDX = '/var/lib/gambit/workspace/claims/claims/index.json'
RPC = 'http://127.0.0.1:7076'
def rpc(b):
    r = urllib.request.Request(RPC, json.dumps(b).encode(), {'content-type': 'application/json'})
    return json.load(urllib.request.urlopen(r, timeout=10))
def addr_of(block):
    try: return rpc({'action': 'block_info', 'json_block': 'true', 'hash': block}).get('contents', {}).get('link_as_account')
    except Exception as e: return f'?{e}'
idx = json.load(open(IDX)); items = idx if isinstance(idx, list) else idx['claims']
if sys.argv[1:2] == ['--mark']:
    addr, block, date = sys.argv[2:5]; n = 0
    for c in items:
        for r in c.get('reviews', []):
            if r.get('bond_returned') or not r.get('block') or str(r.get('bond_due', '9999'))[:10] > date: continue
            if addr_of(r['block']) == addr: r['bond_returned'] = {'block': block, 'date': date}; n += 1
    json.dump(idx, open(IDX, 'w'), indent=1, ensure_ascii=False); print('marked', n); sys.exit()
asof = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
groups = {}
for c in items:
    for r in c.get('reviews', []):
        due = str(r.get('bond_due', ''))[:10]
        if not due or due > asof or r.get('bond_returned'): continue
        a = addr_of(r['block']) if r.get('block') else '?no-block'
        g = groups.setdefault((r.get('by'), a), {'claims': [], 'sum': 0.0})
        g['claims'].append(f"#{c['n']}:{r.get('verdict')}/{c.get('status')}/due {due}")
        g['sum'] += float(r.get('bond_withheld_nano', 0))
tot = 0
for (by, a), g in sorted(groups.items()):
    tot += g['sum']; print(f"{by:28s} {a}  Ӿ{g['sum']:.1f}  {len(g['claims'])} bonds"); print('   ', '; '.join(g['claims']))
print(f'total due as of {asof}: Ӿ{tot:.1f} across {len(groups)} sends')
