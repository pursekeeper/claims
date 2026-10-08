/* Hamiltonian path / cycle tests on small graphs (<= 64 vertices), bitmask DFS with pruning. */
#ifndef HAM_H
#define HAM_H
#include <stdint.h>
typedef uint64_t bm;
static int HN;          /* number of vertices */
static bm  HADJ[64];    /* adjacency bitmasks */
static bm  HALL;        /* mask of all vertices */

static inline int ctz64(bm x){ return __builtin_ctzll(x); }
static inline int pc64(bm x){ return __builtin_popcountll(x); }
static inline void ham_set_n(int n){ HN=n; HALL = (n>=64)? ~0ull : ((1ull<<n)-1); }

/* are all vertices in rem reachable from v using only vertices in rem (plus the first step from v)? */
static inline int reachable_all(int v, bm rem) {
    bm reach = HADJ[v] & rem;
    bm frontier = reach;
    while (reach != rem && frontier) {
        bm nxt = 0, f = frontier;
        while (f) { int u = ctz64(f); f &= f-1; nxt |= HADJ[u]; }
        nxt &= rem & ~reach;
        reach |= nxt; frontier = nxt;
    }
    return reach == rem;
}

/* ---- Hamiltonian path ---- */
static int hp_dfs(int v, bm visited) {
    bm rem = HALL & ~visited;
    if (!rem) return 1;
    if (!reachable_all(v, rem)) return 0;
    int ends = 0;
    bm r = rem;
    while (r) {
        int u = ctz64(r); r &= r-1;
        int deg = pc64(HADJ[u] & rem);
        int adjv = (HADJ[v] >> u) & 1;
        if (deg == 0) { if (!adjv || rem != (1ull<<u)) return 0; }
        else if (deg == 1 && !adjv) { if (++ends > 1) return 0; }
    }
    bm cand = HADJ[v] & rem;
    while (cand) { int u = ctz64(cand); cand &= cand-1; if (hp_dfs(u, visited | (1ull<<u))) return 1; }
    return 0;
}
static int hampath(void) {
    if (HN == 1) return 1;
    int leaves = 0; bm leafmask = 0;
    for (int i=0;i<HN;i++) { int d = pc64(HADJ[i]); if (d==0) return 0; if (d==1) { leaves++; leafmask |= 1ull<<i; } }
    if (leaves > 2) return 0;
    bm starts = leaves ? leafmask : HALL;
    while (starts) { int s = ctz64(starts); starts &= starts-1; if (hp_dfs(s, 1ull<<s)) return 1; }
    return 0;
}

/* ---- Hamiltonian cycle: existence and count (undirected cycles) ---- */
static long long hc_dfs(int v, bm visited, int countall) {
    bm rem = HALL & ~visited;
    if (!rem) return (HADJ[v] & 1ull) ? 1 : 0;
    if (!(HADJ[0] & rem)) return 0;
    if (!reachable_all(v, rem)) return 0;
    bm extra = (1ull<<v) | 1ull;
    bm r = rem;
    while (r) { int u = ctz64(r); r &= r-1; if (pc64(HADJ[u] & (rem | extra)) < 2) return 0; }
    long long c = 0; bm cand = HADJ[v] & rem;
    while (cand) {
        int u = ctz64(cand); cand &= cand-1;
        c += hc_dfs(u, visited | (1ull<<u), countall);
        if (c && !countall) return 1;
    }
    return c;
}
static int hamcycle(void) {
    if (HN < 3) return 0;
    for (int i=0;i<HN;i++) if (pc64(HADJ[i]) < 2) return 0;
    return hc_dfs(0, 1ull, 0) ? 1 : 0;
}
static long long hamcycle_count(void) {
    if (HN < 3) return 0;
    for (int i=0;i<HN;i++) if (pc64(HADJ[i]) < 2) return 0;
    return hc_dfs(0, 1ull, 1) / 2;
}
#endif
