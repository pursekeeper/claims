/*
 * Independent recomputation:
 *   - fixed polyominoes via Redelmeier's algorithm
 *   - free polyominoes by keeping only the lexicographically minimal
 *     representative among the 8 symmetry images
 *   - Hamiltonian path test on the cell-adjacency graph (bitmask DFS with
 *     connectivity / leaf / bipartite pruning)
 *
 * usage: ./hampoly N [nproc pid]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

#define MAXN 20

static int N;
static int W, H;          /* grid dims for Redelmeier lattice */
static uint8_t *occ;      /* cell is in the polyomino */
static uint8_t *used;     /* cell has been put in an untried set on the current branch (or is forbidden) */
static int cells[MAXN];
static long long fixedCount[MAXN + 1], freeCount[MAXN + 1], hamCount[MAXN + 1];
static long long dfsNodes[MAXN + 1];
static int nproc = 1, pid = 0;
static long long splitCounter = 0;
static int SPLITDEPTH = 6;

static uint16_t rev16[65536];

static inline uint32_t rev32(uint32_t x) {
    return ((uint32_t)rev16[x & 0xffff] << 16) | rev16[x >> 16];
}
static inline uint32_t revw(uint32_t x, int w) { return rev32(x) >> (32 - w); }

/* ---------------- Hamiltonian path test ---------------- */
static uint32_t nb[MAXN];
static int hn;

static int dfs(int cur, uint32_t rem) {
    if (!rem) return 1;
    dfsNodes[hn]++;
    uint32_t cand = nb[cur] & rem;
    if (!cand) return 0;
    /* connectivity of rem starting from cand */
    uint32_t reach = cand, frontier = cand;
    while (frontier) {
        uint32_t nf = 0, f = frontier;
        while (f) {
            int i = __builtin_ctz(f);
            f &= f - 1;
            nf |= nb[i];
        }
        nf &= rem & ~reach;
        reach |= nf;
        frontier = nf;
    }
    if (reach != rem) return 0;
    /* leaf check: every remaining cell except the final one needs >=2 nbrs in rem u {cur} */
    uint32_t avail = rem | (1u << cur);
    int leaves = 0;
    uint32_t r = rem;
    while (r) {
        int i = __builtin_ctz(r);
        r &= r - 1;
        uint32_t m = nb[i] & avail;
        if ((m & (m - 1)) == 0) { /* degree <= 1 (0 impossible after connectivity) */
            if (++leaves > 1) return 0;
            if (m == (1u << cur) && rem != (1u << i)) return 0;
        }
    }
    /* if a leaf exists that is adjacent only to cur... handled above. Try candidates. */
    while (cand) {
        int c = __builtin_ctz(cand);
        cand &= cand - 1;
        if (dfs(c, rem & ~(1u << c))) return 1;
    }
    return 0;
}

/* rows[]: h row masks of width w; returns 1 if the cell graph has a Hamiltonian path */
static int hamiltonian(const uint32_t *rows, int h, int w, int n) {
    static int8_t id[MAXN][MAXN];
    int k = 0;
    uint32_t colorA = 0;
    for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++) {
            if (rows[y] >> x & 1) {
                id[y][x] = (int8_t)k;
                if (((x + y) & 1) == 0) colorA |= 1u << k;
                k++;
            } else id[y][x] = -1;
        }
    if (k != n) { fprintf(stderr, "bug: k!=n\n"); exit(1); }
    hn = n;
    k = 0;
    for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++) {
            if (id[y][x] < 0) continue;
            uint32_t m = 0;
            if (x > 0 && id[y][x - 1] >= 0) m |= 1u << id[y][x - 1];
            if (x + 1 < w && id[y][x + 1] >= 0) m |= 1u << id[y][x + 1];
            if (y > 0 && id[y - 1][x] >= 0) m |= 1u << id[y - 1][x];
            if (y + 1 < h && id[y + 1][x] >= 0) m |= 1u << id[y + 1][x];
            nb[k++] = m;
        }
    if (n == 1) return 1;
    uint32_t all = (n == 32) ? 0xffffffffu : ((1u << n) - 1);
    int leaves = 0;
    uint32_t leafmask = 0;
    for (int i = 0; i < n; i++) {
        int d = __builtin_popcount(nb[i]);
        if (d == 1) { leaves++; leafmask |= 1u << i; }
    }
    if (leaves > 2) return 0;
    int a = __builtin_popcount(colorA), b = n - a;
    if (a - b > 1 || b - a > 1) return 0;
    uint32_t startmask;
    if (leaves == 0) startmask = all;
    else if (leaves == 1) startmask = leafmask;
    else startmask = leafmask & (0u - leafmask); /* lowest leaf only: both leaves are endpoints */
    if (a > b) startmask &= colorA;
    else if (b > a) startmask &= ~colorA;
    while (startmask) {
        int s = __builtin_ctz(startmask);
        startmask &= startmask - 1;
        if (dfs(s, all & ~(1u << s))) return 1;
    }
    return 0;
}

/* ---------------- canonical (free) check + processing ---------------- */
static void process(int n) {
    fixedCount[n]++;
    int minx = 1 << 30, maxx = -(1 << 30), miny = 1 << 30, maxy = -(1 << 30);
    int xs[MAXN], ys[MAXN];
    for (int i = 0; i < n; i++) {
        int y = cells[i] / W, x = cells[i] % W;
        xs[i] = x; ys[i] = y;
        if (x < minx) minx = x;
        if (x > maxx) maxx = x;
        if (y < miny) miny = y;
        if (y > maxy) maxy = y;
    }
    int w = maxx - minx + 1, h = maxy - miny + 1;
    if (h > w) return; /* the transposed image has a smaller (h,w) key */
    uint32_t rows[MAXN], cols[MAXN];
    memset(rows, 0, sizeof(uint32_t) * h);
    memset(cols, 0, sizeof(uint32_t) * w);
    for (int i = 0; i < n; i++) {
        rows[ys[i] - miny] |= 1u << (xs[i] - minx);
        cols[xs[i] - minx] |= 1u << (ys[i] - miny);
    }
    /* compare original against each transform of same shape; original must be <= all */
    /* T1: vertical flip */
    for (int i = 0; i < h; i++) { uint32_t b = rows[h - 1 - i]; if (rows[i] < b) break; if (rows[i] > b) return; }
    /* T2: horizontal flip */
    for (int i = 0; i < h; i++) { uint32_t b = revw(rows[i], w); if (rows[i] < b) break; if (rows[i] > b) return; }
    /* T3: rotate 180 */
    for (int i = 0; i < h; i++) { uint32_t b = revw(rows[h - 1 - i], w); if (rows[i] < b) break; if (rows[i] > b) return; }
    if (h == w) {
        for (int i = 0; i < h; i++) { uint32_t b = cols[i]; if (rows[i] < b) break; if (rows[i] > b) return; }
        for (int i = 0; i < h; i++) { uint32_t b = cols[w - 1 - i]; if (rows[i] < b) break; if (rows[i] > b) return; }
        for (int i = 0; i < h; i++) { uint32_t b = revw(cols[i], h); if (rows[i] < b) break; if (rows[i] > b) return; }
        for (int i = 0; i < h; i++) { uint32_t b = revw(cols[w - 1 - i], h); if (rows[i] < b) break; if (rows[i] > b) return; }
    }
    freeCount[n]++;
    if (hamiltonian(rows, h, w, n)) hamCount[n]++;
}

/* ---------------- Redelmeier ---------------- */
static void rec(const int *untried, int nu, int size) {
    int myu[4 * MAXN + 8];
    int added[4];
    while (nu > 0) {
        int c = untried[--nu];
        int sz = size + 1;
        if (sz == SPLITDEPTH) {
            if ((splitCounter++ % nproc) != pid) continue;
        }
        occ[c] = 1;
        cells[size] = c;
        if (sz >= SPLITDEPTH || pid == 0) process(sz);
        if (sz < N) {
            memcpy(myu, untried, nu * sizeof(int));
            int nn = nu, na = 0;
            int nbs[4] = { c + 1, c - 1, c + W, c - W };
            for (int j = 0; j < 4; j++) {
                int d = nbs[j];
                if (!used[d]) { used[d] = 1; myu[nn++] = d; added[na++] = d; }
            }
            rec(myu, nn, sz);
            for (int j = 0; j < na; j++) used[added[j]] = 0;
        }
        occ[c] = 0;
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s N [nproc pid]\n", argv[0]); return 1; }
    N = atoi(argv[1]);
    if (argc >= 4) { nproc = atoi(argv[2]); pid = atoi(argv[3]); }
    if (N > MAXN) { fprintf(stderr, "N too big\n"); return 1; }
    if (SPLITDEPTH > N) SPLITDEPTH = N;
    for (int i = 0; i < 65536; i++) {
        uint16_t r = 0;
        for (int b = 0; b < 16; b++) if (i >> b & 1) r |= 1u << (15 - b);
        rev16[i] = r;
    }
    /* lattice: x in [-(N-1), N-1] plus 1 pad each side; y in [0, N-1] plus 1 pad each side */
    W = 2 * N + 1;
    H = N + 2;
    occ = calloc((size_t)W * H, 1);
    used = calloc((size_t)W * H, 1);
    /* forbid: pad columns, pad rows, and row y=0 with x<0 */
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            int rx = x - N; /* real x: index x=N corresponds to rx=0 */
            int ry = y - 1;
            int forbid = (x == 0 || x == W - 1 || y == 0 || y == H - 1 || (ry == 0 && rx < 0));
            if (forbid) used[y * W + x] = 1;
        }
    int origin = 1 * W + N;
    used[origin] = 1;
    int untried[1] = { origin };
    clock_t t0 = clock();
    rec(untried, 1, 0);
    double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
    for (int n = 1; n <= N; n++)
        printf("%d %lld %lld %lld %lld\n", n, fixedCount[n], freeCount[n], hamCount[n], dfsNodes[n]);
    fprintf(stderr, "pid %d/%d done in %.1f s\n", pid, nproc, secs);
    return 0;
}
