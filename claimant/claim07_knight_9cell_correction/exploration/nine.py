import sys, itertools
sys.setrecursionlimit(10000)
n = int(sys.argv[1]) if len(sys.argv)>1 else 9

def norm(cells):
    mx=min(x for x,y in cells); my=min(y for x,y in cells)
    return tuple(sorted((x-mx,y-my) for x,y in cells))
def syms(cells):
    out=[]
    for t in range(8):
        c=[]
        for x,y in cells:
            if t&4: x,y=y,x
            if t&1: x=-x
            if t&2: y=-y
            c.append((x,y))
        out.append(norm(c))
    return out
def canon(cells): return min(syms(cells))

# grow free polyominoes
cur={((0,0),)}
for k in range(2,n+1):
    nxt=set()
    for p in cur:
        s=set(p)
        for x,y in p:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q=(x+dx,y+dy)
                if q not in s:
                    nxt.add(canon(s|{q}))
    cur=nxt
print("free polyominoes", n, len(cur))

KN=[(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)]
def knight_adj(p):
    s=set(p); idx={c:i for i,c in enumerate(p)}
    adj=[[] for _ in p]
    for c in p:
        for dx,dy in KN:
            q=(c[0]+dx,c[1]+dy)
            if q in s: adj[idx[c]].append(idx[q])
    return adj
def ham_paths(adj):
    m=len(adj); paths=[]
    def rec(path,vis):
        if len(path)==m: paths.append(tuple(path)); return
        for u in adj[path[-1]]:
            if not vis&(1<<u): rec(path+[u],vis|(1<<u))
    for s in range(m): rec([s],1<<s)
    return paths
def has_hole(p):
    s=set(p); mx=max(x for x,y in p); my=max(y for x,y in p)
    # flood outside within bounding box padded by 1
    seen=set(); st=[(-1,-1)]
    while st:
        x,y=st.pop()
        if (x,y) in seen or (x,y) in s or x<-1 or y<-1 or x>mx+1 or y>my+1: continue
        seen.add((x,y)); st+= [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    for x in range(mx+1):
        for y in range(my+1):
            if (x,y) not in s and (x,y) not in seen: return True
    return False

tourable=[]; total_geom_tours=0
for p in sorted(cur):
    adj=knight_adj(p)
    paths=ham_paths(adj)
    if not paths: continue
    # undirected paths as tuples of cell sequences, up to board symmetry
    cellpaths=set()
    for pa in paths:
        seq=[p[i] for i in pa]
        if seq[0]>seq[-1]: seq=seq[::-1]
        cellpaths.add(tuple(seq))
    # geometric distinctness: identify under symmetries mapping board to itself
    geo=set()
    for cp in cellpaths:
        variants=[]
        for t in range(8):
            c=[]
            for x,y in cp:
                if t&4: x,y=y,x
                if t&1: x=-x
                if t&2: y=-y
                c.append((x,y))
            mx=min(x for x,y in c); my=min(y for x,y in c)
            c=[(x-mx,y-my) for x,y in c]
            if tuple(sorted(c))!=p: continue
            if c[0]>c[-1]: c=c[::-1]
            variants.append(tuple(c))
        geo.add(min(variants))
    tourable.append((p,len(geo),has_hole(p)))
    total_geom_tours+=len(geo)
print("tourable boards", len(tourable), "geometrically distinct tours", total_geom_tours)
print("holey tourable boards", sum(1 for p,g,h in tourable if h))
for p,g,h in tourable:
    mx=max(x for x,y in p); my=max(y for x,y in p)
    rows=[]
    for y in range(my,-1,-1):
        rows.append(''.join('#' if (x,y) in p else '.' for x in range(mx+1)))
    print(f"tours={g} hole={h}"); print('\n'.join(rows)); print()

from collections import Counter
def frame(p):
    mx=max(x for x,y in p)+1; my=max(y for x,y in p)+1
    return tuple(sorted((mx,my)))
def is_sym(p): return len(set(syms(p)))<8
c=Counter()
for p,g,h in tourable:
    c[(frame(p),g,is_sym(p),h)]+=1
for k in sorted(c): print("frame=%s tours=%d symmetric=%s holey=%s : %d boards"%(k[0],k[1],k[2],k[3],c[k]))
