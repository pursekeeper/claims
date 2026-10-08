// Validate knight tests on classical rectangle facts.
#include "knight.h"
#include <cstdio>

static void buildRect(int w, int h, KGraph& g) {
    g.n = w * h;
    for (int i = 0; i < g.n; i++) { g.adj[i] = 0; g.color[i] = ((i % w) + (i / w)) & 1; }
    const int dx[8] = {1,2,2,1,-1,-2,-2,-1}, dy[8] = {2,1,-1,-2,-2,-1,1,2};
    for (int y = 0; y < h; y++) for (int x = 0; x < w; x++)
        for (int k = 0; k < 8; k++) {
            int nx = x + dx[k], ny = y + dy[k];
            if (nx >= 0 && nx < w && ny >= 0 && ny < h) g.adj[y*w+x] |= 1u << (ny*w+nx);
        }
}

int main() {
    struct T { int w, h; bool open, closed; };
    T tests[] = { {3,4,true,false}, {3,5,false,false}, {3,6,false,false}, {4,4,false,false},
                  {5,5,true,false}, {5,6,true,true}, {3,10,true,true}, {3,7,true,false},
                  {4,5,true,false}, {3,8,true,false}, {4,6,true,false}, {1,1,true,false}, {2,2,false,false} };
    int bad = 0;
    for (auto& t : tests) {
        KGraph g; buildRect(t.w, t.h, g);
        if (g.n > MAXV) continue;
        bool o = hasHamPath(g), c = hasHamCycle(g), conn = knightConnected(g);
        printf("%dx%d: connected=%d open=%d (expect %d) closed=%d (expect %d)%s\n", t.w, t.h, conn, o, t.open, c, t.closed,
               (o == t.open && c == t.closed) ? "" : "  <-- MISMATCH");
        if (o != t.open || c != t.closed) bad++;
    }
    // 3x4 counts: known number of open tours on 3x4 board = 8 undirected (16 directed) [classical]
    KGraph g; buildRect(3, 4, g); HamEnum he; he.g = &g; he.n = g.n; he.all = fullMask(g.n); he.run();
    printf("3x4 directed Hamiltonian paths: %zu (undirected %zu)\n", he.paths.size(), he.paths.size() / 2);
    printf("%s\n", bad ? "RECT TESTS FAILED" : "RECT TESTS OK");
    return bad;
}
