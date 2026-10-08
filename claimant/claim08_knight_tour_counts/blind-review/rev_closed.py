import sys
from collections import defaultdict
N=int(sys.argv[1])
polys=[l.split() for l in open('rev_polys12.txt') if l.startswith(f'{N} ')]
def sym(cells,k):
    t=[]
    for x,y in cells:
        if k&1: x,y=y,x
        if k&2: x=-x
        if k&4: y=-y
        t.append((x,y))
    mx=min(x for x,y in t); my=min(y for x,y in t)
    return [(x-mx,y-my) for x,y in t]
res=defaultdict(lambda:[0,0,0,0,0,0])  # boards,tours,symboards,symtours,holeyboards,holeytours
for p in polys:
    cells=[tuple(map(int,c.split(','))) for c in p[1:]]
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[[j for j in range(n) if (abs(cells[i][0]-cells[j][0]),abs(cells[i][1]-cells[j][1])) in ((1,2),(2,1))] for i in range(n)]
    cyc=set()
    def dfs(v,vis,path):
        if len(path)==n:
            if 0 in adj[v]:
                cyc.add(frozenset(frozenset((path[i],path[(i+1)%n])) for i in range(n)))
            return
        for w in adj[v]:
            if not vis>>w&1: dfs(w,vis|1<<w,path+[w])
    dfs(0,1,[0])
    if not cyc: continue
    base=sorted(sym(cells,0)); stab=[]
    for k in range(8):
        t=sym(cells,k)
        if sorted(t)==base: stab.append({i: idx[t[i]] for i in range(n)})
    orbits={}
    for e in cyc:
        imgs=[frozenset(frozenset(g[a] for a in ed) for ed in e) for g in stab]
        key=min(imgs,key=lambda s:sorted(sorted(x) for x in s))
        orbits[key]=sum(1 for im in imgs if im==e)  # stabilizer size of tour
    w=max(x for x,y in cells)+1; h=max(y for x,y in cells)+1
    frame=f"{min(w,h)}x{max(w,h)}"
    S=set(cells); seen={(-1,-1)}; fr=[(-1,-1)]
    while fr:
        x,y=fr.pop()
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q=(x+dx,y+dy)
            if -1<=q[0]<=w and -1<=q[1]<=h and q not in S and q not in seen: seen.add(q); fr.append(q)
    holey=any((x,y) not in S and (x,y) not in seen for x in range(w) for y in range(h))
    r=res[frame]; r[0]+=1; r[1]+=len(orbits)
    if len(stab)>1: r[2]+=1
    r[3]+=sum(1 for k,v in orbits.items() if v>1)
    if holey: r[4]+=1; r[5]+=len(orbits)
tot=[0]*6
for f in sorted(res):
    print(f,res[f]); tot=[a+b for a,b in zip(tot,res[f])]
print("frame: boards,tours,symboards,symtours,holeyboards,holeytours; totals",tot)
