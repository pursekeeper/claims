# Honeycomb-lattice self-avoiding polygons (SAPs) of length L, using the triangle representation:
# honeycomb vertex = triangle (a,b) with a=b=1 mod 3 (up) or 2 mod 3 (down); edges = triangle adjacencies.
# For each L count (i) free SAPs (polygons up to D6+translation) and (ii) distinct free vertex sets.
import sys
def nbrs(a,b):
    if a%3==1: return ((a+1,b+1),(a-2,b+1),(a+1,b-2))
    return ((a-1,b-1),(a+2,b-1),(a-1,b+2))
def rot(p): a,b=p; return (-b,a+b)
def refl(p): a,b=p; return (b,a)
def norm(cells):
    ma=min(a for a,b in cells); mb=min(b for a,b in cells)
    sa=3*(ma//3); sb=3*(mb//3)
    return tuple(sorted((a-sa,b-sb) for a,b in cells))
def canon_set(cells):
    best=None
    for r in range(2):
        cur=[refl(p) for p in cells] if r else list(cells)
        for k in range(6):
            t=norm(cur)
            if best is None or t<best: best=t
            cur=[rot(p) for p in cur]
    return best
def canon_edges(edges):
    best=None
    for r in range(2):
        cur=[(refl(p),refl(q)) for p,q in edges] if r else list(edges)
        for k in range(6):
            pts=[p for e in cur for p in e]
            ma=min(a for a,b in pts); mb=min(b for a,b in pts); sa=3*(ma//3); sb=3*(mb//3)
            t=tuple(sorted(tuple(sorted(((p[0]-sa,p[1]-sb),(q[0]-sa,q[1]-sb)))) for p,q in cur))
            if best is None or t<best: best=t
            cur=[(rot(p),rot(q)) for p,q in cur]
    return best
Lmax=int(sys.argv[1])
sets={L:set() for L in range(1,Lmax+1)}; polys={L:set() for L in range(1,Lmax+1)}
sys.setrecursionlimit(10000)
for origin in ((1,1),(2,2)):
    o=origin
    def ok(p): return p[1]>o[1] or (p[1]==o[1] and p[0]>=o[0])
    path=[o]; onpath={o}
    def dfs(v):
        L=len(path)
        for u in nbrs(*v):
            if u==o and L>=3 and L<=Lmax:
                edges=[(path[i],path[(i+1)%L]) for i in range(L)]
                polys[L].add(canon_edges(edges)); sets[L].add(canon_set(path))
            elif u not in onpath and ok(u) and L<Lmax:
                path.append(u); onpath.add(u); dfs(u); path.pop(); onpath.discard(u)
    dfs(o)
for L in range(2,Lmax+1,2):
    print(L, "free SAPs", len(polys[L]), "distinct vertex sets", len(sets[L]))
