/* Direct uniqueness test: enumerate all honeycomb self-avoiding polygons (SAPs) with up to L vertices
   (same cell/vertex coordinates as iam.c), reduce to free polygons under the 12 symmetries, and for each
   polygon whose vertex set has chords (induced subgraph != plain cycle) count the Hamiltonian cycles of the
   induced subgraph.  Reports per length: fixed polygons, free polygons, free polygons with chords,
   maximum number of Hamiltonian cycles, and prints any vertex set with >1 Hamiltonian cycle. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "ham.h"

#define LMAX 44
#define OFF (LMAX+2)
#define W (2*OFF+1)
#define MAXROWS (2*LMAX+8)

static int L;
static unsigned char visited[W*W];
static unsigned char ctype[W*W];
static int dist[W*W];
static int posid[W*W];
static int path[LMAX+2];
static int originidx;
static int upoff[3], downoff[3];
static const int L6[6][4] = { {1,0,0,1}, {0,-1,1,-1}, {-1,1,-1,0}, {0,1,1,0}, {1,-1,0,-1}, {-1,0,-1,1} };
static long long cFixed[LMAX+2], cFree[LMAX+2], cChord[LMAX+2], cMulti[LMAX+2], maxCyc[LMAX+2], nodes;

static int shape_rows(const int *x, const int *y, int n, int t, uint64_t *rows) {
    int tx[LMAX+2], ty[LMAX+2];
    int minx = 1<<29, miny = 1<<29, maxy = -(1<<29);
    const int *M = L6[t%6];
    for (int i=0;i<n;i++) {
        int a = x[i], b = y[i];
        if (t>=6) { a = 2-a; b = 2-b; }
        tx[i] = M[0]*a + M[1]*b;
        ty[i] = M[2]*a + M[3]*b;
        if (tx[i]<minx) minx=tx[i];
        if (ty[i]<miny) miny=ty[i];
        if (ty[i]>maxy) maxy=ty[i];
    }
    int r = ((minx+miny)%3+3)%3;
    int H = maxy-miny+1+r;
    for (int i=0;i<H;i++) rows[i]=0;
    for (int i=0;i<n;i++) rows[ty[i]-miny+r] |= 1ull << (tx[i]-minx);
    return H;
}
static inline int cmp_rows(const uint64_t *a, int Ha, const uint64_t *b, int Hb) {
    int H = Ha<Hb?Ha:Hb;
    for (int i=0;i<H;i++) if (a[i]!=b[i]) return a[i]<b[i]?-1:1;
    return Ha-Hb;
}

static void record(int n) {           /* path[0..n-1] is a closed polygon of n vertices */
    if (path[1] > path[n-1]) return;  /* one orientation only */
    cFixed[n]++;
    int x[LMAX+2], y[LMAX+2];
    for (int i=0;i<n;i++){ x[i]=path[i]%W-OFF; y[i]=path[i]/W-OFF; }
    uint64_t rows0[MAXROWS], rows[MAXROWS];
    int H0 = shape_rows(x,y,n,0,rows0);
    for (int t=1;t<12;t++){ int H=shape_rows(x,y,n,t,rows); if (cmp_rows(rows,H,rows0,H0)<0) return; }
    cFree[n]++;
    /* induced subgraph on the vertex set */
    for (int i=0;i<n;i++) posid[path[i]]=i+1;
    int edges=0;
    for (int i=0;i<n;i++){ bm a=0; const int *off = ctype[path[i]]==0?upoff:downoff;
        for(int d=0;d<3;d++){int j=path[i]+off[d]; if(posid[j]) { a|=1ull<<(posid[j]-1); edges++; } } HADJ[i]=a; }
    for (int i=0;i<n;i++) posid[path[i]]=0;
    edges/=2;
    if (edges == n) { if (maxCyc[n]<1) maxCyc[n]=1; return; }   /* no chords: exactly the one cycle */
    cChord[n]++;
    ham_set_n(n);
    long long hc = hamcycle_count();
    if (hc > maxCyc[n]) maxCyc[n]=hc;
    if (hc != 1) {
        cMulti[n]++;
        printf("  n=%d hamcycles=%lld chords=%d :", n, hc, edges-n);
        for (int i=0;i<n;i++) printf(" (%d,%d)", x[i], y[i]);
        printf("\n"); fflush(stdout);
    }
}

static void dfs(int cur, int len) {   /* path[0..len] set, len edges used */
    nodes++;
    const int *off = ctype[cur]==0?upoff:downoff;
    for (int d=0;d<3;d++) {
        int nb = cur+off[d];
        if (nb == originidx) { if (len+1 >= 6) record(len+1); continue; }
        if (nb < originidx || visited[nb]) continue;
        if (len+1+dist[nb] > L) continue;
        visited[nb]=1; path[len+1]=nb;
        dfs(nb, len+1);
        visited[nb]=0;
    }
}

static void bfs_dist(void) {
    static int q[W*W];
    for (int i=0;i<W*W;i++) dist[i]=1<<20;
    int h=0,t=0; q[t++]=originidx; dist[originidx]=0;
    while (h<t) { int c=q[h++]; if (dist[c] >= L) continue;
        int cx=c%W, cy=c/W; if (cx<1||cx>=W-1||cy<1||cy>=W-1) continue;
        const int *off = ctype[c]==0?upoff:downoff;
        for (int d=0;d<3;d++){ int j=c+off[d]; if (dist[j]>dist[c]+1){ dist[j]=dist[c]+1; q[t++]=j; } } }
}

int main(int argc, char **argv) {
    L = atoi(argv[1]);
    upoff[0]=1; upoff[1]=W; upoff[2]=-1-W;
    downoff[0]=-1; downoff[1]=-W; downoff[2]=1+W;
    for (int yy=0;yy<W;yy++) for (int xx=0;xx<W;xx++) ctype[yy*W+xx] = (unsigned char)((((xx-OFF)+(yy-OFF))%3+3)%3);
    clock_t t0=clock();
    for (int o=0;o<2;o++) {
        originidx = OFF*W + OFF + o;
        bfs_dist();
        memset(visited,0,sizeof visited);
        visited[originidx]=1; path[0]=originidx;
        dfs(originidx, 0);
    }
    printf("honeycomb SAPs up to %d vertices, DFS nodes=%lld, time=%.1fs\n", L, nodes, (double)(clock()-t0)/CLOCKS_PER_SEC);
    for (int n=6;n<=L;n+=2)
        printf("len=%2d fixedSAP=%lld freeSAP=%lld withChords=%lld maxHamCycles=%lld setsWithCount!=1=%lld\n",
               n, cFixed[n], cFree[n], cChord[n], maxCyc[n], cMulti[n]);
    return 0;
}
