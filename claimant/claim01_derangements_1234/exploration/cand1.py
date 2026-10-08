"""Candidate batch 1: permutation-based sequences, brute force for n<=10, generate patterns."""
import itertools, sys
from math import factorial

def contains(p, pat):
    k = len(pat)
    n = len(p)
    for idx in itertools.combinations(range(n), k):
        vals = [p[i] for i in idx]
        # check order isomorphic
        ok = True
        for a in range(k):
            for b in range(a+1, k):
                if (vals[a] < vals[b]) != (pat[a] < pat[b]):
                    ok = False; break
            if not ok: break
        if ok: return True
    return False

def is_derangement(p):
    return all(p[i] != i for i in range(len(p)))

def alternating(p):  # up-down: p1<p2>p3<...
    return all((p[i] < p[i+1]) if i % 2 == 0 else (p[i] > p[i+1]) for i in range(len(p)-1))

N = int(sys.argv[1]) if len(sys.argv) > 1 else 9
pats = [(0,1,2,3),(0,1,3,2),(0,2,1,3),(0,2,3,1),(0,3,2,1),(1,0,3,2),(1,3,0,2),(2,3,0,1),(3,2,1,0),(3,1,2,0),(3,0,1,2),(3,2,0,1)]
res = {pat: [] for pat in pats}
res['alt_der'] = []
res['der_avoid_123'] = []  # validation vs OEIS
res['avoid_1324'] = []  # validation A061552
for n in range(1, N+1):
    cnt = {k: 0 for k in res}
    for p in itertools.permutations(range(n)):
        d = is_derangement(p)
        if not contains(p, (0,2,1,3)):
            cnt['avoid_1324'] += 1
        if d:
            if alternating(p): cnt['alt_der'] += 1
            if not contains(p, (0,1,2)): cnt['der_avoid_123'] += 1
            for pat in pats:
                if not contains(p, pat): cnt[pat] += 1
    for k in res: res[k].append(cnt[k])
    print(n, flush=True)
for k, v in res.items():
    print(k, v)
