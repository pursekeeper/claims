import numpy as np, itertools
def canon(cells):
    best=None
    for sx in (1,-1):
        for sy in (1,-1):
            for sw in (0,1):
                t=[(sx*x,sy*y) if not sw else (sy*y,sx*x) for x,y in cells]
                mx=min(a for a,b in t); my=min(b for a,b in t)
                t=tuple(sorted((a-mx,b-my) for a,b in t))
                if best is None or t<best: best=t
    return best
def grow(n):
    cur={canon([(0,0)])}
    for k in range(2,n+1):
        nxt=set()
        for p in cur:
            s=set(p)
            for x,y in p:
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    c=(x+dx,y+dy)
                    if c not in s: nxt.add(canon(list(s|{c})))
        cur=nxt
    return cur
def tau(p):
    n=len(p); idx={c:i for i,c in enumerate(p)}
    L=np.zeros((n,n))
    for (x,y),i in idx.items():
        for dx,dy in ((1,0),(0,1)):
            j=idx.get((x+dx,y+dy))
            if j is not None: L[i,i]+=1;L[j,j]+=1;L[i,j]-=1;L[j,i]-=1
    return int(round(np.linalg.det(L[1:,1:]))) if n>1 else 1
def indep(p):
    n=len(p); idx={c:i for i,c in enumerate(p)}
    adj=[0]*n
    for (x,y),i in idx.items():
        for dx,dy in ((1,0),(0,1)):
            j=idx.get((x+dx,y+dy))
            if j is not None: adj[i]|=1<<j; adj[j]|=1<<i
    return sum(1 for m in range(1<<n) if all(not(adj[i]&m) for i in range(n) if m>>i&1))
for n in range(1,10):
    P=grow(n); ts=[tau(p) for p in P]
    line=f"n={n} free={len(P)} sum_tau={sum(ts)} max_tau={max(ts)} cnt={ts.count(max(ts))} odd={sum(t%2 for t in ts)} unicyc={sum(1 for p in P if sum(1 for (x,y) in p for d in ((1,0),(0,1)) if (x+d[0],y+d[1]) in set(p))==n)}"
    if n<=8:
        iss=[indep(p) for p in P]; line+=f" sum_is={sum(iss)} min_is={min(iss)} max_is={max(iss)}"
    print(line)
