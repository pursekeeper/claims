# independent check: grow free polyominoes by adding cells, canonical = min over 8 symmetries of sorted tuple
import sys
def canon(cells):
    best=None
    for sx in (1,-1):
        for sy in (1,-1):
            for sw in (0,1):
                pts=[(sx*x,sy*y) if not sw else (sx*y,sy*x) for x,y in cells]
                mx=min(p[0] for p in pts); my=min(p[1] for p in pts)
                t=tuple(sorted((x-mx,y-my) for x,y in pts))
                if best is None or t<best: best=t
    return best
def ham_cycle(cells):
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[0]*n
    for (x,y),i in idx.items():
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            j=idx.get((x+d[0],y+d[1]))
            if j is not None: adj[i]|=1<<j
    # DP over subsets containing vertex 0: dp[mask] = set of endpoints reachable from 0 visiting exactly mask
    full=(1<<n)-1
    dp={1:1}  # mask -> bitmask of endpoints
    for mask in range(1,1<<n,2):
        ends=dp.get(mask,0)
        if not ends: continue
        e=ends
        while e:
            v=(e&-e).bit_length()-1; e&=e-1
            nb=adj[v]&~mask
            while nb:
                u=(nb&-nb).bit_length()-1; nb&=nb-1
                dp[mask|1<<u]=dp.get(mask|1<<u,0)|(1<<u)
    ends=dp.get(full,0)
    return n>=3 and bool(ends & adj[0])
def ham_path(cells):
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[0]*n
    for (x,y),i in idx.items():
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            j=idx.get((x+d[0],y+d[1]))
            if j is not None: adj[i]|=1<<j
    full=(1<<n)-1
    dp={}
    for s in range(n): dp[1<<s]=1<<s
    for mask in range(1,1<<n):
        ends=dp.get(mask,0)
        if not ends: continue
        e=ends
        while e:
            v=(e&-e).bit_length()-1; e&=e-1
            nb=adj[v]&~mask
            while nb:
                u=(nb&-nb).bit_length()-1; nb&=nb-1
                dp[mask|1<<u]=dp.get(mask|1<<u,0)|(1<<u)
    return bool(dp.get(full,0))
N=int(sys.argv[1])
cur={canon([(0,0)])}
for n in range(1,N):
    nxt=set()
    for p in cur:
        s=set(p)
        for (x,y) in p:
            for d in ((1,0),(-1,0),(0,1),(0,-1)):
                c=(x+d[0],y+d[1])
                if c not in s:
                    nxt.add(canon(list(s|{c})))
    cur=nxt
    hc=sum(1 for p in cur if ham_cycle(list(p))); hp=sum(1 for p in cur if ham_path(list(p)))
    print(n+1,len(cur),hc,hp,flush=True)
