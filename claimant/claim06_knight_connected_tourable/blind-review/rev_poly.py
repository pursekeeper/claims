import sys
# generate free polyominoes up to N by growth, canonical form under D4, write cells
N = int(sys.argv[1])
def norm(cells):
    mx = min(x for x,y in cells); my = min(y for x,y in cells)
    return tuple(sorted((x-mx,y-my) for x,y in cells))
def canon(cells):
    best=None
    for k in range(8):
        t=[]
        for x,y in cells:
            if k&1: x,y=y,x
            if k&2: x=-x
            if k&4: y=-y
            t.append((x,y))
        c=norm(t)
        if best is None or c<best: best=c
    return best
cur={((0,0),)}
out=open(sys.argv[2],'w')
for n in range(1,N+1):
    for p in sorted(cur):
        out.write(str(n)+' '+' '.join(f"{x},{y}" for x,y in p)+'\n')
    if n==N: break
    nxt=set()
    for p in cur:
        s=set(p)
        for x,y in p:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q=(x+dx,y+dy)
                if q not in s:
                    nxt.add(canon(list(p)+[q]))
    cur=nxt
    print(n+1,len(cur),file=sys.stderr)
