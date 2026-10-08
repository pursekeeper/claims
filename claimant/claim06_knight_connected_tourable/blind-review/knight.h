// Knight-graph utilities: connectivity, Hamiltonian path / cycle existence, path enumeration.
#pragma once
#include <cstdint>
#include <vector>
#include <algorithm>

typedef uint32_t U32;
#define MAXV 32
static inline uint32_t fullMask(int n) { return n >= 32 ? 0xffffffffu : ((1u << n) - 1); }

struct KGraph {
    int n;
    U32 adj[MAXV];   // adjacency bitmasks
    int color[MAXV]; // (x+y)&1 bipartition
};

static inline int popc(U32 x) { return __builtin_popcount(x); }
static inline int lowbit(U32 x) { return __builtin_ctz(x); }

// Is the set 'mask' connected within the graph (mask nonempty)?
static inline bool connectedMask(const KGraph& g, U32 mask, int start) {
    U32 reach = 1u << start, frontier = reach;
    while (frontier) {
        U32 nf = 0;
        U32 f = frontier;
        while (f) { int v = lowbit(f); f &= f - 1; nf |= g.adj[v]; }
        nf &= mask & ~reach;
        reach |= nf;
        frontier = nf;
    }
    return reach == mask;
}

static inline bool knightConnected(const KGraph& g) {
    return connectedMask(g, fullMask(g.n), 0);
}

// ---------- Hamiltonian path existence (DFS with pruning) ----------
struct HamSearch {
    const KGraph* g;
    U32 all;
    int n;
    int start;      // for cycle: must return to start
    bool wantCycle;

    bool dfs(int cur, U32 visited, int cnt) {
        if (cnt == n) {
            if (wantCycle) return (g->adj[cur] >> start) & 1;
            return true;
        }
        U32 rem = all & ~visited;
        U32 cand = g->adj[cur] & rem;
        if (!cand) return false;
        // connectivity of rem ∪ {cur}
        if (!connectedMask(*g, rem | (1u << cur), cur)) return false;
        // degree pruning within rem ∪ {cur}
        U32 live = rem | (1u << cur);
        int deg1 = 0;
        U32 r = rem;
        if (wantCycle) {
            // every remaining vertex needs 2 neighbours among rem ∪ {cur} ∪ {start};
            // the edge to start is only usable by the last vertex of the path.
            // (when cur == start, the start edge is the ordinary edge to cur: no 'last' constraint)
            U32 livec = live | (1u << start);
            int mustLast = 0;
            bool atStart = (cur == start);
            while (r) {
                int u = lowbit(r); r &= r - 1;
                int d = popc(g->adj[u] & livec);
                if (d < 2) return false;
                if (!atStart && d == 2 && ((g->adj[u] >> start) & 1)) { if (++mustLast > 1) return false; }
            }
        } else {
            while (r) {
                int u = lowbit(r); r &= r - 1;
                int d = popc(g->adj[u] & live);
                if (d == 0) return false;
                if (d == 1) {
                    deg1++;
                    if (deg1 > 1) return false;
                    if (((g->adj[u] >> cur) & 1) && rem != (1u << u)) return false;
                }
            }
        }
        // order candidates by fewest onward moves (Warnsdorff)
        int cs[MAXV], ds[MAXV], k = 0;
        U32 c = cand;
        while (c) { int v = lowbit(c); c &= c - 1; cs[k] = v; ds[k] = popc(g->adj[v] & rem); k++; }
        for (int i = 1; i < k; i++) { int v = cs[i], d = ds[i], j = i - 1; while (j >= 0 && ds[j] > d) { cs[j+1] = cs[j]; ds[j+1] = ds[j]; j--; } cs[j+1] = v; ds[j+1] = d; }
        for (int i = 0; i < k; i++) {
            if (dfs(cs[i], visited | (1u << cs[i]), cnt + 1)) return true;
        }
        return false;
    }
};

static inline bool hasHamCycle(const KGraph& g) {
    int n = g.n;
    if (n < 4) return false;
    if (n & 1) return false;
    int a = 0; for (int i = 0; i < n; i++) a += g.color[i];
    if (2 * a != n) return false;
    for (int i = 0; i < n; i++) if (popc(g.adj[i]) < 2) return false;
    HamSearch hs; hs.g = &g; hs.n = n; hs.all = fullMask(n); hs.wantCycle = true; hs.start = 0;
    return hs.dfs(0, 1u, 1);
}

static inline bool hasHamPath(const KGraph& g) {
    int n = g.n;
    if (n == 1) return true;
    int a = 0; for (int i = 0; i < n; i++) a += g.color[i];
    int b = n - a;
    if (a - b > 1 || b - a > 1) return false;
    int d1 = 0, d1v = -1;
    for (int i = 0; i < n; i++) { int d = popc(g.adj[i]); if (d == 0) return false; if (d == 1) { d1++; d1v = i; } }
    if (d1 > 2) return false;
    HamSearch hs; hs.g = &g; hs.n = n; hs.all = fullMask(n); hs.wantCycle = false; hs.start = 0;
    if (d1 >= 1) return hs.dfs(d1v, 1u << d1v, 1);
    // start set: if colour classes unbalanced, path must start in the larger class
    int mustColor = -1;
    if (a == b + 1) mustColor = 1; else if (b == a + 1) mustColor = 0;
    for (int s = 0; s < n; s++) {
        if (mustColor >= 0 && g.color[s] != mustColor) continue;
        if (hs.dfs(s, 1u << s, 1)) return true;
    }
    return false;
}

// ---------- enumeration of all directed Hamiltonian paths ----------
struct HamEnum {
    const KGraph* g; int n; U32 all;
    std::vector<std::vector<int>> paths;
    int seq[MAXV];
    void dfs(int cur, U32 visited, int cnt) {
        if (cnt == n) { paths.emplace_back(seq, seq + n); return; }
        U32 rem = all & ~visited;
        U32 cand = g->adj[cur] & rem;
        while (cand) { int v = lowbit(cand); cand &= cand - 1; seq[cnt] = v; dfs(v, visited | (1u << v), cnt + 1); }
    }
    void run() { paths.clear(); for (int s = 0; s < n; s++) { seq[0] = s; dfs(s, 1u << s, 1); } }
};
