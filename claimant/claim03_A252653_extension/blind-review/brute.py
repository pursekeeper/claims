import sys
from functools import lru_cache

def canon(cells):
    best = None
    for k in range(8):
        pts = []
        for (x, y) in cells:
            if k & 1: x, y = y, x
            if k & 2: x = -x
            if k & 4: y = -y
            pts.append((x, y))
        mx = min(p[0] for p in pts); my = min(p[1] for p in pts)
        t = tuple(sorted((x - mx, y - my) for x, y in pts))
        if best is None or t < best: best = t
    return best

def has_ham(cells):
    cs = list(cells); n = len(cs); idx = {c: i for i, c in enumerate(cs)}
    adj = [[idx[(x+dx, y+dy)] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if (x+dx, y+dy) in idx] for x, y in cs]
    @lru_cache(maxsize=None)
    def f(mask, cur):
        if mask == (1 << n) - 1: return True
        return any(f(mask | 1 << v, v) for v in adj[cur] if not mask >> v & 1)
    return any(f(1 << s, s) for s in range(n))

N = int(sys.argv[1])
cur = {((0, 0),)}
for n in range(1, N + 1):
    ham = sum(1 for p in cur if has_ham(p))
    print(n, len(cur), ham, flush=True)
    nxt = set()
    for p in cur:
        s = set(p)
        for (x, y) in p:
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q = (x+dx, y+dy)
                if q not in s:
                    nxt.add(canon(s | {q}))
    cur = nxt
