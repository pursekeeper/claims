import sys, itertools
from collections import defaultdict
polys=[l.split() for l in open('rev_polys12.txt') if l.startswith('9 ')]
def sym(cells,k):
    t=[]
    for x,y in cells:
        if k&1: x,y=y,x
        if k&2: x=-x
        if k&4: y=-y
        t.append((x,y))
    mx=min(x for x,y in t); my=min(y for x,y in t)
    return [(x-mx,y-my) for x,y in t]
res=defaultdict(lambda:[0,0,0,0])  # frame -> boards, tours, symboards, symtours
detail=[]
for p in polys:
    cells=[tuple(map(int,c.split(','))) for c in p[1:]]
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[[j for j in range(n) if (abs(cells[i][0]-cells[j][0]),abs(cells[i][1]-cells[j][1])) in ((1,2),(2,1))] for i in range(n)]
    paths=set()
    def dfs(v,vis,path):
        if len(path)==n:
            e=frozenset(frozenset((path[i],path[i+1])) for i in range(n-1)); paths.add(e); return
        for w in adj[v]:
            if not vis>>w&1: dfs(w,vis|1<<w,path+[w])
    for s in range(n): dfs(s,1<<s,[s])
    if not paths: continue
    # stabilizer: symmetries mapping cell set to itself (as normalized)
    base=sorted(sym(cells,0))
    stab=[]
    for k in range(8):
        t=sym(cells,k)
        if sorted(t)==base:
            stab.append({i: idx[t[i]] for i in range(n)})  # cell i -> image cell index
    orbits=set()
    for e in paths:
        imgs=[frozenset(frozenset(g[a] for a in ed) for ed in e) for g in stab]
        orbits.add(min(imgs,key=lambda s:sorted(sorted(x) for x in s)))
    # geometrically distinct tours = orbits of paths under stabilizer
    w=max(x for x,y in cells)+1; h=max(y for x,y in cells)+1
    frame=f"{min(w,h)}x{max(w,h)}"
    holey = False
    # hole: bounding box cell not in poly and not connected to outside
    S=set(cells); outside=set(); fr=[(-1,-1)]
    seen={(-1,-1)}
    while fr:
        x,y=fr.pop()
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q=(x+dx,y+dy)
            if -1<=q[0]<=w and -1<=q[1]<=h and q not in S and q not in seen: seen.add(q); fr.append(q)
    for x in range(w):
        for y in range(h):
            if (x,y) not in S and (x,y) not in seen: holey=True
    r=res[frame]; r[0]+=1; r[1]+=len(orbits);
    if len(stab)>1: r[2]+=1
    detail.append((frame,len(stab),holey,len(orbits),len(paths),cells))
tot=[0,0]
for f in sorted(res): print(f,res[f]); tot[0]+=res[f][0]; tot[1]+=res[f][1]
print("total boards,tours",tot)
print("4x4 boards: (stab size, holey, distinct tours, raw undirected paths)")
for d in sorted(detail):
    if d[0]=='4x4': print(d[1:5], d[5])
print("boards with a unique tour by frame:", {f:sum(1 for d in detail if d[0]==f and d[3]==1) for f in sorted(res)})
