#!/usr/bin/env python3
"""Independent pure-Python brute force: free polyominoes by growth + canonical set,
knight graph, all Hamiltonian paths by naive DFS, tours canonicalised under board symmetry."""
import sys
from itertools import product

def normalize(cells):
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return tuple(sorted((x - mx, y - my) for x, y in cells))

SYMS = [lambda x, y: (x, y), lambda x, y: (-x, y), lambda x, y: (x, -y), lambda x, y: (-x, -y),
        lambda x, y: (y, x), lambda x, y: (-y, x), lambda x, y: (y, -x), lambda x, y: (-y, -x)]

def canon(cells):
    return min(normalize([f(x, y) for x, y in cells]) for f in SYMS)

def free_polyominoes(n):
    cur = {((0, 0),)}
    for k in range(2, n + 1):
        nxt = set()
        for p in cur:
            s = set(p)
            for x, y in p:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    c = (x + dx, y + dy)
                    if c not in s:
                        nxt.add(canon(list(s | {c})))
        cur = nxt
    return sorted(cur)

KM = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

def knight_adj(cells):
    s = set(cells)
    return {c: [(c[0] + dx, c[1] + dy) for dx, dy in KM if (c[0] + dx, c[1] + dy) in s] for c in cells}

def connected(adj):
    start = next(iter(adj)); seen = {start}; st = [start]
    while st:
        v = st.pop()
        for w in adj[v]:
            if w not in seen: seen.add(w); st.append(w)
    return len(seen) == len(adj)

def ham_paths(adj):
    n = len(adj); out = []
    def dfs(path, seen):
        if len(path) == n: out.append(tuple(path)); return
        for w in adj[path[-1]]:
            if w not in seen:
                seen.add(w); path.append(w); dfs(path, seen); path.pop(); seen.remove(w)
    for s in adj: dfs([s], {s})
    return out

def board_automorphisms(cells):
    base = normalize(cells); auts = []
    for f in SYMS:
        img = [f(x, y) for x, y in cells]
        mx = min(x for x, y in img); my = min(y for x, y in img)
        mapping = {c: (f(*c)[0] - mx, f(*c)[1] - my) for c in cells}
        if normalize(img) == base: auts.append(mapping)
    return auts

def tours_up_to_symmetry(cells, paths, auts):
    seen = set()
    for p in paths:
        key = min(min(tuple(a[c] for c in p), tuple(a[c] for c in reversed(p))) for a in auts)
        seen.add(key)
    return len(seen)

def picture(cells):
    w = max(x for x, y in cells) + 1; h = max(y for x, y in cells) + 1; s = set(cells)
    return "\n".join("".join('#' if (x, y) in s else '.' for x in range(w)) for y in range(h)), w, h

def main():
    n = int(sys.argv[1]); detail = len(sys.argv) > 2
    polys = free_polyominoes(n)
    K = O = C = 0; boards = 0; total = 0; lines = []
    for p in polys:
        adj = knight_adj(p)
        if not connected(adj): continue
        K += 1
        paths = ham_paths(adj)
        if not paths: continue
        O += 1
        if any(p0[-1] in adj[p0[0]] for p0 in paths): C += 1
        if detail:
            auts = board_automorphisms(p)
            t = tours_up_to_symmetry(p, paths, auts)
            boards += 1; total += t
            pic, w, h = picture(p)
            lines.append((w, h, t, len(paths) // 2, len(auts), pic))
    print(f"n={n} free={len(polys)} K={K} O={O} C={C}")
    if detail:
        print(f"tourable boards={boards} tours up to board symmetry={total}")
        for w, h, t, u, a, pic in lines:
            print(f"board {w}x{h} |Aut|={a} undirectedPaths={u} toursUpToSym={t}\n{pic}")
        ones = [(w, h, pic) for w, h, t, u, a, pic in lines if (w, h) == (4, 4) and t == 1]
        print(f"4x4-bounding-box boards with exactly one tour: {len(ones)}")
        for w, h, pic in ones: print(pic); print()

main()
