import sys, itertools
sys.setrecursionlimit(10000)
LAT=int(sys.argv[1])
def nbrs(a,b):
    if LAT==6: return [(a+1,b),(a-1,b),(a,b+1),(a,b-1),(a+1,b-1),(a-1,b+1)]
    if a%3==1: return [(a+1,b+1),(a-2,b+1),(a+1,b-2)]
    return [(a-1,b-1),(a+2,b-1),(a-1,b+2)]
def hampath(cells):
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[[idx[x] for x in nbrs(*c) if x in idx] for c in cells]
    # brute force: try all starting points, plain DFS
    def dfs(v,vis):
        if len(vis)==n: return True
        for u in adj[v]:
            if u not in vis:
                vis.add(u)
                if dfs(u,vis): return True
                vis.remove(u)
        return False
    return any(dfs(s,{s}) for s in range(n))
def hamcycle(cells):
    n=len(cells); idx={c:i for i,c in enumerate(cells)}
    adj=[[idx[x] for x in nbrs(*c) if x in idx] for c in cells]
    if n<3: return False
    def dfs(v,vis):
        if len(vis)==n: return 0 in adj[v]
        for u in adj[v]:
            if u not in vis:
                vis.add(u)
                if dfs(u,vis): return True
                vis.remove(u)
        return False
    return dfs(0,{0})
tot=0; hc=0; hp=0; bad=0
for line in sys.stdin:
    if line.startswith('LAT'): print(line.strip()); continue
    L,R=line.split('|'); cells=[tuple(map(int,t.split(','))) for t in L.split()]
    c_hc,c_hp=map(int,R.split())
    # check connectivity too
    idx=set(cells); seen={cells[0]}; st=[cells[0]]
    while st:
        v=st.pop()
        for x in nbrs(*v):
            if x in idx and x not in seen: seen.add(x); st.append(x)
    assert len(seen)==len(cells), "disconnected"
    p=hampath(cells); c=hamcycle(cells)
    tot+=1; hp+=p; hc+=c
    if p!=bool(c_hp) or c!=bool(c_hc): bad+=1; print("MISMATCH",line.strip(),p,c)
print("checked",tot,"hampath",hp,"hamcycle",hc,"mismatches",bad)
