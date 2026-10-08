/* Free polyiamond enumeration + Hamiltonian path/cycle counts of the inner dual.
   Triangle cells are honeycomb vertices: integer points (x,y) with (x+y) mod 3 != 2.
   (x+y) mod 3 == 0 : "up" cell, neighbours (x+1,y),(x,y+1),(x-1,y-1)
   (x+y) mod 3 == 1 : "down" cell, neighbours (x-1,y),(x,y-1),(x+1,y+1)
   Lattice translations are (dx,dy) with dx+dy == 0 mod 3.
   Symmetry group (12) = {sigma, sigma o R}, sigma in the 6 linear maps below, R:(x,y)->(2-x,2-y). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "ham.h"

#define MAXN 24
#define OFF (MAXN+2)
#define W (2*OFF+1)
#define MAXU (3*MAXN+8)
#define MAXROWS (2*MAXN+8)

static int N, verbose;
static unsigned char grid[W*W];
static unsigned char ctype[W*W];
static int posid[W*W];
static int cellidx[MAXN];
static int originidx;
static int upoff[3], downoff[3];
static const int L6[6][4] = { {1,0,0,1}, {0,-1,1,-1}, {-1,1,-1,0}, {0,1,1,0}, {1,-1,0,-1}, {-1,0,-1,1} };
static long long cntFixed, cntFree, cntPath, cntCycle, maxCyc;

static int shape_rows(const int *x, const int *y, int t, uint64_t *rows) {
    int tx[MAXN], ty[MAXN];
    int minx = 1<<29, miny = 1<<29, maxy = -(1<<29);
    const int *M = L6[t%6];
    for (int i=0;i<N;i++) {
        int a = x[i], b = y[i];
        if (t>=6) { a = 2-a; b = 2-b; }
        tx[i] = M[0]*a + M[1]*b;
        ty[i] = M[2]*a + M[3]*b;
        if (tx[i]<minx) minx=tx[i];
        if (ty[i]<miny) miny=ty[i];
        if (ty[i]>maxy) maxy=ty[i];
    }
    int r = ((minx+miny)%3+3)%3;       /* shift = (-minx, -miny+r), sum == 0 mod 3 */
    int H = maxy-miny+1+r;
    for (int i=0;i<H;i++) rows[i]=0;
    for (int i=0;i<N;i++) rows[ty[i]-miny+r] |= 1ull << (tx[i]-minx);
    return H;
}
static inline int cmp_rows(const uint64_t *a, int Ha, const uint64_t *b, int Hb) {
    int H = Ha<Hb?Ha:Hb;
    for (int i=0;i<H;i++) if (a[i]!=b[i]) return a[i]<b[i]?-1:1;
    return Ha-Hb;
}

static void print_shape(const int *x, const int *y, const char *tag) {
    printf("  %s:", tag);
    for (int i=0;i<N;i++) printf(" (%d,%d)%c", x[i], y[i], ((x[i]+y[i])%3+3)%3==0?'u':'d');
    printf("\n");
}

static void process(void) {
    int x[MAXN], y[MAXN];
    cntFixed++;
    for (int i=0;i<N;i++){ x[i]=cellidx[i]%W-OFF; y[i]=cellidx[i]/W-OFF; }
    uint64_t rows0[MAXROWS], rows[MAXROWS];
    int H0 = shape_rows(x,y,0,rows0);
    for (int t=1;t<12;t++){ int H=shape_rows(x,y,t,rows); if (cmp_rows(rows,H,rows0,H0)<0) return; }
    cntFree++;
    for (int i=0;i<N;i++) posid[cellidx[i]]=i+1;
    for (int i=0;i<N;i++){ bm a=0; const int *off = ctype[cellidx[i]]==0?upoff:downoff;
        for(int d=0;d<3;d++){int j=cellidx[i]+off[d]; if(posid[j]) a|=1ull<<(posid[j]-1);} HADJ[i]=a; }
    for (int i=0;i<N;i++) posid[cellidx[i]]=0;
    ham_set_n(N);
    int hp = hampath();
    long long hc = hamcycle_count();
    if (hp) cntPath++;
    if (hc) cntCycle++;
    if (hc > maxCyc) { maxCyc = hc; if (hc>1) { char tag[64]; snprintf(tag,sizeof tag,"NEW MAX cycles=%lld", hc); print_shape(x,y,tag);} }
    if (verbose) { char tag[64]; snprintf(tag,sizeof tag,"path=%d cycles=%lld", hp, hc); print_shape(x,y,tag); }
}

static void rec(int *untried, int nu, int size) {
    while (nu > 0) {
        int c = untried[--nu];
        grid[c] = 1; cellidx[size] = c;
        if (size+1 == N) process();
        else {
            int newu[MAXU]; memcpy(newu, untried, nu*sizeof(int)); int nn = nu;
            int added[3], na=0;
            const int *off = ctype[c]==0?upoff:downoff;
            for (int d=0;d<3;d++){ int j=c+off[d]; if (j>originidx && grid[j]==0){ grid[j]=2; newu[nn++]=j; added[na++]=j; } }
            rec(newu, nn, size+1);
            for (int k=0;k<na;k++) grid[added[k]]=0;
        }
        grid[c] = 2;
    }
}

int main(int argc, char **argv) {
    int n1 = atoi(argv[1]), n2 = atoi(argv[2]);
    int which = atoi(argv[3]);           /* 0: origin up only, 1: origin down only, 2: both */
    verbose = argc>4;
    upoff[0]=1; upoff[1]=W; upoff[2]=-1-W;
    downoff[0]=-1; downoff[1]=-W; downoff[2]=1+W;
    for (int yy=0;yy<W;yy++) for (int xx=0;xx<W;xx++) ctype[yy*W+xx] = (unsigned char)((((xx-OFF)+(yy-OFF))%3+3)%3);
    for (N=n1; N<=n2; N++) {
        clock_t t0 = clock();
        cntFixed=cntFree=cntPath=cntCycle=maxCyc=0;
        for (int o=0;o<2;o++) {
            if (which!=2 && which!=o) continue;
            memset(grid,0,sizeof grid);
            originidx = OFF*W + OFF + o;   /* (0,0) up ; (1,0) down */
            int untried[MAXU]; untried[0]=originidx; grid[originidx]=2;
            rec(untried, 1, 0);
        }
        printf("IAM n=%2d which=%d fixed=%lld free=%lld hampath=%lld hamcycle=%lld maxcycles=%lld time=%.1fs\n",
               N, which, cntFixed, cntFree, cntPath, cntCycle, maxCyc, (double)(clock()-t0)/CLOCKS_PER_SEC);
        fflush(stdout);
    }
    return 0;
}
