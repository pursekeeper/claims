/* Free polyhex enumeration (Redelmeier fixed enumeration + canonical form under 12 symmetries),
   plus Hamiltonian path / cycle counts of the inner dual.  Axial coordinates (q,r). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "ham.h"

#define MAXN 20
#define OFF (MAXN+2)
#define W (2*OFF+1)
#define MAXU (6*MAXN+8)
#define MAXROWS (2*MAXN+4)

static int N, verbose;
static unsigned char grid[W*W];
static int posid[W*W];
static int cellidx[MAXN];
static int originidx;
static const int nbq[6] = {1,0,-1,-1,0,1};
static const int nbr[6] = {0,1,1,0,-1,-1};
static int nboff[6];
static int T[12][4];
static long long cntFixed, cntFree, cntPath, cntCycle, maxCyc;

static void init_transforms(void) {
    int R[4] = {0,-1,1,1};   /* q' = -r ; r' = q + r  (rotation by 60 deg) */
    int F[4] = {0,1,1,0};    /* q' = r ; r' = q       (reflection) */
    int cur[4] = {1,0,0,1};
    for (int k=0;k<6;k++) {
        memcpy(T[k], cur, sizeof cur);
        T[6+k][0] = F[0]*cur[0]+F[1]*cur[2]; T[6+k][1] = F[0]*cur[1]+F[1]*cur[3];
        T[6+k][2] = F[2]*cur[0]+F[3]*cur[2]; T[6+k][3] = F[2]*cur[1]+F[3]*cur[3];
        int n0 = R[0]*cur[0]+R[1]*cur[2], n1 = R[0]*cur[1]+R[1]*cur[3];
        int n2 = R[2]*cur[0]+R[3]*cur[2], n3 = R[2]*cur[1]+R[3]*cur[3];
        cur[0]=n0;cur[1]=n1;cur[2]=n2;cur[3]=n3;
    }
}

static int shape_rows(const int *q, const int *r, const int *M, uint64_t *rows) {
    int tq[MAXN], tr[MAXN];
    int minq = 1<<29, minr = 1<<29, maxr = -(1<<29);
    for (int i=0;i<N;i++) {
        tq[i] = M[0]*q[i] + M[1]*r[i];
        tr[i] = M[2]*q[i] + M[3]*r[i];
        if (tq[i]<minq) minq=tq[i];
        if (tr[i]<minr) minr=tr[i];
        if (tr[i]>maxr) maxr=tr[i];
    }
    int H = maxr-minr+1;
    for (int i=0;i<H;i++) rows[i]=0;
    for (int i=0;i<N;i++) rows[tr[i]-minr] |= 1ull << (tq[i]-minq);
    return H;
}
static inline int cmp_rows(const uint64_t *a, int Ha, const uint64_t *b, int Hb) {
    int H = Ha<Hb?Ha:Hb;
    for (int i=0;i<H;i++) if (a[i]!=b[i]) return a[i]<b[i]?-1:1;
    return Ha-Hb;
}

static void print_shape(const int *q, const int *r, const char *tag) {
    printf("  %s:", tag);
    for (int i=0;i<N;i++) printf(" (%d,%d)", q[i], r[i]);
    printf("\n");
}

static void process(void) {
    int q[MAXN], r[MAXN];
    cntFixed++;
    for (int i=0;i<N;i++){ q[i]=cellidx[i]%W-OFF; r[i]=cellidx[i]/W-OFF; }
    uint64_t rows0[MAXROWS], rows[MAXROWS];
    int H0 = shape_rows(q,r,T[0],rows0);
    for (int t=1;t<12;t++){ int H=shape_rows(q,r,T[t],rows); if (cmp_rows(rows,H,rows0,H0)<0) return; }
    cntFree++;
    for (int i=0;i<N;i++) posid[cellidx[i]]=i+1;
    for (int i=0;i<N;i++){ bm a=0; for(int d=0;d<6;d++){int j=cellidx[i]+nboff[d]; if(posid[j]) a|=1ull<<(posid[j]-1);} HADJ[i]=a; }
    for (int i=0;i<N;i++) posid[cellidx[i]]=0;
    ham_set_n(N);
    int hp = hampath();
    long long hc = hamcycle_count();
    if (hp) cntPath++;
    if (hc) cntCycle++;
    if (hc > maxCyc) maxCyc = hc;
    if (verbose) { char tag[64]; snprintf(tag,sizeof tag,"path=%d cycles=%lld", hp, hc); print_shape(q,r,tag); }
}

static void rec(int *untried, int nu, int size) {
    while (nu > 0) {
        int c = untried[--nu];
        grid[c] = 1; cellidx[size] = c;
        if (size+1 == N) process();
        else {
            int newu[MAXU]; memcpy(newu, untried, nu*sizeof(int)); int nn = nu;
            int added[6], na=0;
            for (int d=0;d<6;d++){ int j=c+nboff[d]; if (j>originidx && grid[j]==0){ grid[j]=2; newu[nn++]=j; added[na++]=j; } }
            rec(newu, nn, size+1);
            for (int k=0;k<na;k++) grid[added[k]]=0;
        }
        grid[c] = 2;
    }
}

int main(int argc, char **argv) {
    int n1 = atoi(argv[1]), n2 = argc>2 ? atoi(argv[2]) : n1;
    verbose = argc>3;
    init_transforms();
    for (int d=0;d<6;d++) nboff[d] = nbq[d] + nbr[d]*W;
    originidx = OFF*W + OFF;
    for (N=n1; N<=n2; N++) {
        clock_t t0 = clock();
        cntFixed=cntFree=cntPath=cntCycle=maxCyc=0;
        memset(grid,0,sizeof grid);
        int untried[MAXU]; untried[0]=originidx; grid[originidx]=2;
        rec(untried, 1, 0);
        printf("HEX n=%2d fixed=%lld free=%lld hampath=%lld hamcycle=%lld maxcycles=%lld time=%.1fs\n",
               N, cntFixed, cntFree, cntPath, cntCycle, maxCyc, (double)(clock()-t0)/CLOCKS_PER_SEC);
        fflush(stdout);
    }
    return 0;
}
