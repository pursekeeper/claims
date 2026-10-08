from collections import Counter
cnt=Counter()
for l in open('rev_polys12.txt'):
    p=l.split(); n=int(p[0]); cells=[tuple(map(int,c.split(','))) for c in p[1:]]
    idx={c:i for i,c in enumerate(cells)}
    # reduced Laplacian mod 2 as bitmask rows (drop vertex 0)
    rows=[]
    for i in range(1,n):
        x,y=cells[i]; r=0; deg=0
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            j=idx.get((x+dx,y+dy))
            if j is not None:
                deg+=1
                if j>0: r^=1<<(j-1)
        if deg&1: r^=1<<(i-1)
        rows.append(r)
    # rank over GF(2)
    rank=0
    for b in range(n-1):
        piv=None
        for k in range(rank,len(rows)):
            if rows[k]>>b&1: piv=k;break
        if piv is None: continue
        rows[rank],rows[piv]=rows[piv],rows[rank]
        for k in range(len(rows)):
            if k!=rank and rows[k]>>b&1: rows[k]^=rows[rank]
        rank+=1
    if rank==n-1: cnt[n]+=1
print([cnt[n] for n in range(1,13)])
print("A397065:",[1,1,2,4,11,28,86,273,915,3126,10948,38782])
