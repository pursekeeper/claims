# check: number of mirror-curve loops == corank over GF(2) of the Laplacian of the cell-adjacency graph (= dim bicycle space + 1), for all polyominoes n<=11 incl. holey ones
def loop_number(cells):
    cs = set(cells); bd = {}
    for (x, y) in cs:
        for node, typ in (((2*x+1, 2*y), 'h'), ((2*x+1, 2*y+2), 'h'), ((2*x, 2*y+1), 'v'), ((2*x+2, 2*y+1), 'v')):
            X, Y = node
            if typ == 'h':
                cy = Y//2; cx = (X-1)//2; above = (cx, cy) in cs; below = (cx, cy-1) in cs
                if above != below: bd[node] = (1, 1) if above else (1, -1)
            else:
                cx = X//2; cy = (Y-1)//2; right = (cx, cy) in cs; left = (cx-1, cy) in cs
                if right != left: bd[node] = (1, 1) if right else (-1, 1)
    seen = set(); loops = 0
    for st, d0 in bd.items():
        if st in seen: continue
        loops += 1; X, Y = st; dx, dy = d0; seen.add(st)
        while True:
            X += dx; Y += dy
            if X % 2 == 0:
                cx = X//2; cy = (Y-1)//2; isb = ((cx-1, cy) in cs) != ((cx, cy) in cs)
                if isb: dx = -dx
            else:
                cy = Y//2; cx = (X-1)//2; isb = ((cx, cy-1) in cs) != ((cx, cy) in cs)
                if isb: dy = -dy
            if isb: seen.add((X, Y))
            if (X, Y, dx, dy) == (st[0], st[1], d0[0], d0[1]): break
    return loops
def corank(cells):
    n=len(cells); idx={c:i for i,c in enumerate(cells)}; rows=[]
    for i in range(n):
        x,y=cells[i]; r=0; deg=0
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            j=idx.get((x+dx,y+dy))
            if j is not None: deg+=1; r^=1<<j
        if deg&1: r^=1<<i
        rows.append(r)
    rank=0
    for b in range(n):
        piv=next((k for k in range(rank,n) if rows[k]>>b&1),None)
        if piv is None: continue
        rows[rank],rows[piv]=rows[piv],rows[rank]
        for k in range(n):
            if k!=rank and rows[k]>>b&1: rows[k]^=rows[rank]
        rank+=1
    return n-rank
bad=0; tot=0; holey=0; maxloops=0
for l in open('rev_polys12.txt'):
    p=l.split(); n=int(p[0])
    if n>11: break
    cells=[tuple(map(int,c.split(','))) for c in p[1:]]
    a=loop_number(cells); b=corank(cells); tot+=1; maxloops=max(maxloops,a)
    if a!=b: bad+=1; print("MISMATCH",cells,a,b)
print("checked",tot,"mismatches",bad,"max loops",maxloops)
