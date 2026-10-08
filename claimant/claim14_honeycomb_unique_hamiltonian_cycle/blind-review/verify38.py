import sys
sys.setrecursionlimit(10000)
S = [(0,0),(1,0),(2,1),(3,1),(4,2),(4,3),(5,4),(5,5),(4,5),(4,6),(5,7),(5,8),(4,8),(4,9),(3,9),(2,8),(1,8),(0,7),(0,6),(-1,5),(-1,4),(0,4),(1,5),(1,6),(2,7),(3,7),(3,6),(2,5),(2,4),(3,4),(3,3),(2,2),(1,2),(1,3),(0,3),(-1,2),(-1,1),(0,1)]
assert len(set(S)) == 38
# independent embedding: honeycomb = points of Z^3 with a+b+c in {0,1}, adjacent iff they differ by a unit vector.
def to3(p):
    x,y = p
    s = (x+y) % 3
    assert s != 2
    c = (s - x - y)//3
    return (c+x, c+y, c)
P = [to3(p) for p in S]
for a,b,c in P: assert a+b+c in (0,1)
idx = {p:i for i,p in enumerate(P)}
adj = [[] for _ in P]
for i,(a,b,c) in enumerate(P):
    for d in ((1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)):
        q = (a+d[0], b+d[1], c+d[2])
        if q in idx: adj[i].append(idx[q])
E = sum(len(a) for a in adj)//2
print("vertices", len(P), "edges", E, "degrees", sorted(len(a) for a in adj))
n = len(P)
# count Hamiltonian cycles by plain DFS from vertex 0 (with simple reachability prune for speed)
def dfs(v, visited, cnt):
    if cnt == n:
        return 1 if 0 in adj[v] else 0
    # reachability prune
    rem = [u for u in range(n) if not visited[u]]
    seen = set(); stack = [u for u in adj[v] if not visited[u]]
    seen.update(stack)
    while stack:
        u = stack.pop()
        for w in adj[u]:
            if not visited[w] and w not in seen:
                seen.add(w); stack.append(w)
    if len(seen) != len(rem): return 0
    t = 0
    for u in adj[v]:
        if not visited[u]:
            visited[u] = True
            t += dfs(u, visited, cnt+1)
            visited[u] = False
    return t
vis = [False]*n; vis[0] = True
print("directed Hamiltonian cycles from 0:", c := dfs(0, vis, 1), "=> undirected:", c//2)
