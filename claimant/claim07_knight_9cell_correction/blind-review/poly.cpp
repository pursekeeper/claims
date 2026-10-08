// Redelmeier enumeration of fixed polyominoes; free classes by canonical-minimum check.
// Modes:
//   ./poly free N        -> count fixed & free polyominoes of size N (validate A000105)
//   ./poly knight N      -> K, O, C for size N (free polyominoes)
//   ./poly detail N      -> per-board Hamiltonian path counts, Burnside orbit counts (N small)
#include "knight.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <string>
#include <vector>
#include <algorithm>

static int N;
static int MODE; // 0 free, 1 knight, 2 detail
static int NTHREADS = 2;
static int SPLIT_DEPTH = 6;

struct Shape { int w, h; U32 rows[MAXV]; };

// lexicographic compare of shapes (w,h,rows...)
static inline int cmpShape(const Shape& a, const Shape& b) {
    if (a.w != b.w) return a.w < b.w ? -1 : 1;
    if (a.h != b.h) return a.h < b.h ? -1 : 1;
    for (int i = 0; i < a.h; i++) if (a.rows[i] != b.rows[i]) return a.rows[i] < b.rows[i] ? -1 : 1;
    return 0;
}
static inline U32 revbits(U32 x, int w) { U32 r = 0; for (int i = 0; i < w; i++) if ((x >> i) & 1) r |= 1u << (w - 1 - i); return r; }

// the 8 symmetries of a shape. index t: bit0 = transpose first, bit1 = flip horizontally (reverse bits), bit2 = flip vertically (reverse rows)
static void transformShape(const Shape& s, int t, Shape& o) {
    Shape base;
    if (t & 1) { // transpose
        base.w = s.h; base.h = s.w;
        for (int x = 0; x < s.w; x++) { U32 m = 0; for (int y = 0; y < s.h; y++) if ((s.rows[y] >> x) & 1) m |= 1u << y; base.rows[x] = m; }
    } else base = s;
    o.w = base.w; o.h = base.h;
    for (int y = 0; y < base.h; y++) {
        U32 r = base.rows[(t & 4) ? (base.h - 1 - y) : y];
        if (t & 2) r = revbits(r, base.w);
        o.rows[y] = r;
    }
}
// map a cell (x,y) under transform t for a shape of size w,h -> (x',y')
static inline void transformCell(int t, int w, int h, int x, int y, int& ox, int& oy) {
    int bx = x, by = y, bw = w, bh = h;
    if (t & 1) { bx = y; by = x; bw = h; bh = w; }
    if (t & 2) bx = bw - 1 - bx;
    if (t & 4) by = bh - 1 - by;
    ox = bx; oy = by;
}

struct Worker {
    int tid;
    int W;                 // grid width
    std::vector<char> reached, occ;
    std::vector<int> idx;  // grid pos -> cell index
    int cells[MAXV];
    long long nFixed = 0, nFree = 0, K = 0, O = 0, C = 0;
    long long splitCounter = 0;
    // detail mode output
    std::vector<std::string> detailLines;
    long long detailBoards = 0, detailTourTotal = 0, detailCycles = 0;

    void init() {
        W = 2 * N + 3;
        int H = N + 3;
        reached.assign(W * H, 0); occ.assign(W * H, 0); idx.assign(W * H, -1);
        for (int x = 0; x < W; x++) reached[x] = 1;             // row 0 forbidden
        for (int x = 0; x < N + 1; x++) reached[W + x] = 1;      // row 1 left of origin forbidden
    }

    void buildShape(Shape& s, int& minx, int& miny) {
        int maxx = -1, maxy = -1; minx = 1 << 20; miny = 1 << 20;
        for (int i = 0; i < N; i++) { int x = cells[i] % W, y = cells[i] / W; minx = std::min(minx, x); maxx = std::max(maxx, x); miny = std::min(miny, y); maxy = std::max(maxy, y); }
        s.w = maxx - minx + 1; s.h = maxy - miny + 1;
        for (int y = 0; y < s.h; y++) s.rows[y] = 0;
        for (int i = 0; i < N; i++) { int x = cells[i] % W - minx, y = cells[i] / W - miny; s.rows[y] |= 1u << x; }
    }
    // returns true if s is the lexicographic minimum of its 8 transforms; also fills autMask (bit t set if transform t fixes s)
    bool isCanonical(const Shape& s, int& autMask) {
        autMask = 1;
        for (int t = 1; t < 8; t++) {
            Shape o; transformShape(s, t, o);
            int c = cmpShape(o, s);
            if (c < 0) return false;
            if (c == 0) autMask |= 1 << t;
        }
        return true;
    }
    void buildGraph(KGraph& g) {
        g.n = N;
        for (int i = 0; i < N; i++) {
            int p = cells[i];
            int x = p % W, y = p / W;
            g.color[i] = (x + y) & 1;
            U32 m = 0;
            const int offs[8] = { 2*W+1, 2*W-1, -2*W+1, -2*W-1, W+2, W-2, -W+2, -W-2 };
            for (int k = 0; k < 8; k++) { int q = p + offs[k]; if (q >= 0 && q < (int)occ.size() && occ[q]) m |= 1u << idx[q]; }
            g.adj[i] = m;
        }
    }

    void process() {
        nFixed++;
        if (MODE == 0) {
            Shape s; int mx, my; buildShape(s, mx, my); int am;
            if (isCanonical(s, am)) nFree++;
            return;
        }
        KGraph g; buildGraph(g);
        if (!knightConnected(g)) return;
        Shape s; int mx, my; buildShape(s, mx, my); int am;
        if (!isCanonical(s, am)) return;
        K++;
        if (MODE == 1) {
            bool cyc = hasHamCycle(g);
            if (cyc) { C++; O++; }
            else if (hasHamPath(g)) O++;
            return;
        }
        // detail mode
        HamEnum he; he.g = &g; he.n = N; he.all = fullMask(N); he.run();
        bool hp = hasHamPath(g);
        if (hp != !he.paths.empty()) { fprintf(stderr, "INCONSISTENCY between hasHamPath and enumeration!\n"); exit(1); }
        {   // unpruned cross-check of the cycle test: a Hamiltonian cycle exists iff some enumerated path ends adjacent to its start
            bool cycEnum = false;
            for (auto& p : he.paths) if ((g.adj[p[0]] >> p[N - 1]) & 1) { cycEnum = true; break; }
            bool cycFast = hasHamCycle(g);
            if (cycEnum != cycFast) { fprintf(stderr, "INCONSISTENCY between hasHamCycle and enumeration!\n"); exit(1); }
            if (cycEnum) detailCycles++;
        }
        if (he.paths.empty()) return;
        // cell coordinates relative to bounding box
        int cx[MAXV], cy[MAXV];
        for (int i = 0; i < N; i++) { cx[i] = cells[i] % W - mx; cy[i] = cells[i] / W - my; }
        int cellAt[MAXV][MAXV];
        for (int i = 0; i < N; i++) cellAt[cy[i]][cx[i]] = i;
        // Burnside over automorphism group acting on undirected Hamiltonian paths
        long long directed = he.paths.size();
        long long sumFix = 0; int gsize = 0;
        for (int t = 0; t < 8; t++) {
            if (!((am >> t) & 1)) continue;
            gsize++;
            int perm[MAXV];
            for (int i = 0; i < N; i++) { int ox, oy; transformCell(t, s.w, s.h, cx[i], cy[i], ox, oy); perm[i] = cellAt[oy][ox]; }
            long long fixDirected = 0;
            for (auto& p : he.paths) {
                bool same = true, rev = true;
                for (int i = 0; i < N; i++) { int q = perm[p[i]]; if (q != p[i]) same = false; if (q != p[N - 1 - i]) rev = false; }
                if (same || rev) fixDirected++;
            }
            sumFix += fixDirected; // each undirected path fixed contributes 2 directed sequences
        }
        // undirected paths fixed by g = fixDirected/2 ; orbits = (sum over g of fix(g)) / |G|
        if (sumFix % (2 * gsize) != 0) { fprintf(stderr, "Burnside non-integer!\n"); exit(1); }
        long long orbits = sumFix / (2 * gsize);
        detailBoards++; detailTourTotal += orbits;
        std::string line;
        char buf[256];
        snprintf(buf, sizeof buf, "board w=%d h=%d |Aut|=%d directedPaths=%lld undirected=%lld toursUpToSym=%lld\n", s.w, s.h, gsize, directed, directed / 2, orbits);
        line += buf;
        for (int y = 0; y < s.h; y++) { for (int x = 0; x < s.w; x++) line += ((s.rows[y] >> x) & 1) ? '#' : '.'; line += '\n'; }
        detailLines.push_back(line);
    }

    void rec(const int* untried, int cnt, int size) {
        int newlist[4 * MAXV + 8];
        for (int i = 0; i < cnt; i++) {
            int p = untried[i];
            if (size == SPLIT_DEPTH) { // work split among threads
                long long c = splitCounter++;
                if ((int)(c % NTHREADS) != tid) continue;
            }
            cells[size] = p; occ[p] = 1; idx[p] = size;
            if (size + 1 == N) process();
            else {
                int nc = 0;
                for (int j = i + 1; j < cnt; j++) newlist[nc++] = untried[j];
                int added[4], na = 0;
                const int nb[4] = { p + 1, p - 1, p + W, p - W };
                for (int k = 0; k < 4; k++) { int q = nb[k]; if (!reached[q]) { reached[q] = 1; newlist[nc++] = q; added[na++] = q; } }
                rec(newlist, nc, size + 1);
                for (int k = 0; k < na; k++) reached[added[k]] = 0;
            }
            occ[p] = 0; idx[p] = -1;
        }
    }
    void run() {
        init();
        int origin = W + N + 1; // row 1, column N+1
        reached[origin] = 1;
        int lst[1] = { origin };
        rec(lst, 1, 0);
    }
};

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: poly free|knight|detail N [threads] [splitdepth]\n"); return 1; }
    std::string m = argv[1]; N = atoi(argv[2]);
    MODE = (m == "free") ? 0 : (m == "knight") ? 1 : 2;
    if (argc > 3) NTHREADS = atoi(argv[3]);
    if (argc > 4) SPLIT_DEPTH = atoi(argv[4]);
    if (N > MAXV) { fprintf(stderr, "N too large\n"); return 1; }
    if (SPLIT_DEPTH >= N) SPLIT_DEPTH = std::max(0, N - 1);
    if (N == 1) NTHREADS = 1;
    std::vector<Worker> ws(NTHREADS);
    std::vector<std::thread> th;
    for (int t = 0; t < NTHREADS; t++) { ws[t].tid = t; th.emplace_back([&ws, t] { ws[t].run(); }); }
    for (auto& t : th) t.join();
    long long nFixed = 0, nFree = 0, K = 0, O = 0, C = 0, db = 0, dt = 0, dc = 0;
    for (auto& w : ws) { nFixed += w.nFixed; nFree += w.nFree; K += w.K; O += w.O; C += w.C; db += w.detailBoards; dt += w.detailTourTotal; dc += w.detailCycles; }
    if (MODE == 0) printf("n=%d fixed=%lld free=%lld\n", N, nFixed, nFree);
    else if (MODE == 1) printf("n=%d fixed=%lld K=%lld O=%lld C=%lld\n", N, nFixed, K, O, C);
    else {
        for (auto& w : ws) for (auto& l : w.detailLines) printf("%s", l.c_str());
        printf("n=%d fixed=%lld K=%lld tourableBoards(O)=%lld closedTourable(C)=%lld toursUpToBoardSymmetry=%lld\n", N, nFixed, K, db, dc, dt);
    }
    return 0;
}
