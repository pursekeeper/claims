// Enumerate free polyominoes with n cells (Redelmeier + canonical form under D4),
// and for each compute on the cell-adjacency graph G (cells = vertices, edge-adjacent cells joined):
//   tau(G) = number of spanning trees (Kirchhoff matrix-tree theorem, exact Bareiss on 128-bit ints)
//   pm(G)  = number of perfect matchings (= domino tilings), 0 for odd n
//   is(G)  = number of independent sets (hard-square configurations, incl. empty set)
// Outputs aggregate statistics and histograms of tau, pm, is over free n-ominoes.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 22
static int N; static long long SPLITK=1, SPLITR=0, splitctr=0;
#define W (2*MAXN+2)
#define H (MAXN+2)
static int cellx[MAXN], celly[MAXN];
static uint8_t used[H][W];
static uint64_t fixedcount, freecount;

// aggregates
static unsigned __int128 sum_tau, sum_pm, sum_is;
static uint64_t max_tau, max_tau_cnt, max_pm, max_pm_cnt, min_is=~0ull, min_is_cnt, max_is, max_is_cnt;
static uint64_t cnt_tau_odd, cnt_unicyclic;

// histograms (simple open hash on value)
#define HS (1<<22)
typedef struct { uint64_t key; uint64_t cnt; } hent;
static hent *h_tau, *h_pm, *h_is;
static void hadd(hent*h, uint64_t key){
  uint64_t i = (key*0x9E3779B97F4A7C15ull)>>42 & (HS-1);
  while(h[i].cnt && h[i].key!=key) i=(i+1)&(HS-1);
  h[i].key=key; h[i].cnt++;
}
static int cmpent(const void*a,const void*b){ const hent*p=a,*q=b; return p->key<q->key?-1:p->key>q->key; }
static void hdump(hent*h, const char*fn){
  FILE*f=fopen(fn,"w"); int m=0;
  for(int i=0;i<HS;i++) if(h[i].cnt) m++;
  hent*arr=malloc(sizeof(hent)*(m?m:1)); int j=0;
  for(int i=0;i<HS;i++) if(h[i].cnt) arr[j++]=h[i];
  qsort(arr,m,sizeof(hent),cmpent);
  for(int i=0;i<m;i++) fprintf(f,"%llu %llu\n",(unsigned long long)arr[i].key,(unsigned long long)arr[i].cnt);
  fclose(f); free(arr);
}

static int cmpcell(const void*a,const void*b){ const int8_t*p=a,*q=b; if(p[0]!=q[0]) return p[0]-q[0]; return p[1]-q[1]; }
static void normalize(int8_t (*c)[2], int n){
  int mx=127,my=127;
  for(int i=0;i<n;i++){ if(c[i][0]<mx)mx=c[i][0]; if(c[i][1]<my)my=c[i][1]; }
  for(int i=0;i<n;i++){ c[i][0]-=mx; c[i][1]-=my; }
  qsort(c,n,2,cmpcell);
}
static int cmpshape(int8_t (*a)[2], int8_t (*b)[2], int n){ return memcmp(a,b,2*n); }

static uint32_t adj[MAXN];
static int nv;

// ---- spanning trees: determinant of reduced Laplacian via Bareiss (fraction-free) ----
static uint64_t spanning_trees(void){
  if(nv==1) return 1;
  int m=nv-1;
  __int128 A[MAXN][MAXN];
  for(int i=0;i<m;i++) for(int j=0;j<m;j++){
    if(i==j) A[i][j]=__builtin_popcount(adj[i]);
    else A[i][j]= (adj[i]>>j &1) ? -1 : 0;
  }
  __int128 prev=1; int sign=1;
  for(int k=0;k<m-1;k++){
    if(A[k][k]==0){
      int s=-1; for(int i=k+1;i<m;i++) if(A[i][k]!=0){s=i;break;}
      if(s<0) return 0;
      for(int j=0;j<m;j++){ __int128 t=A[k][j]; A[k][j]=A[s][j]; A[s][j]=t; }
      sign=-sign;
    }
    for(int i=k+1;i<m;i++){
      for(int j=k+1;j<m;j++){
        A[i][j]=(A[i][j]*A[k][k]-A[i][k]*A[k][j])/prev;
      }
    }
    prev=A[k][k];
  }
  __int128 d=A[m-1][m-1]*sign;
  if(d<0) d=-d;
  return (uint64_t)d;
}

static uint64_t spanning_trees_dbl(void){
  if(nv==1) return 1;
  int m=nv-1; double A[MAXN][MAXN];
  for(int i=0;i<m;i++) for(int j=0;j<m;j++){
    if(i==j) A[i][j]=__builtin_popcount(adj[i]);
    else A[i][j]= (adj[i]>>j &1) ? -1.0 : 0.0;
  }
  double det=1.0;
  for(int k=0;k<m;k++){
    int p=k; double bv=A[k][k]<0?-A[k][k]:A[k][k];
    for(int i=k+1;i<m;i++){ double v=A[i][k]<0?-A[i][k]:A[i][k]; if(v>bv){bv=v;p=i;} }
    if(bv==0) return 0;
    if(p!=k){ for(int j=0;j<m;j++){ double t=A[k][j]; A[k][j]=A[p][j]; A[p][j]=t; } det=-det; }
    det*=A[k][k];
    for(int i=k+1;i<m;i++){ double f=A[i][k]/A[k][k]; if(f!=0) for(int j=k+1;j<m;j++) A[i][j]-=f*A[k][j]; }
  }
  if(det<0) det=-det;
  return (uint64_t)(det+0.5);
}
static int USE_DBL=0, CHECK=0; static uint64_t mismatches=0;
static uint64_t tau_of(void){
  if(CHECK){ uint64_t a=spanning_trees(), b=spanning_trees_dbl(); if(a!=b) mismatches++; return a; }
  return USE_DBL? spanning_trees_dbl() : spanning_trees();
}
// ---- perfect matchings: match lowest uncovered vertex ----
static uint64_t pm_rec(uint32_t rem){
  if(!rem) return 1;
  int v=__builtin_ctz(rem); rem&=~(1u<<v);
  uint32_t cand=adj[v]&rem; uint64_t s=0;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1; s+=pm_rec(rem&~(1u<<u)); }
  return s;
}
static uint64_t perfect_matchings(void){
  if(nv&1) return 0;
  for(int i=0;i<nv;i++) if(!adj[i] && nv>1) return 0;
  return pm_rec((nv>=32)?0xFFFFFFFFu:((1u<<nv)-1));
}

// ---- independent sets: branch on a vertex (max degree within remaining) ----
static uint64_t is_rec(uint32_t rem){
  if(!rem) return 1;
  // pick vertex of max remaining degree; if all degrees <=1 handle quickly? keep simple
  int best=-1, bd=-1; uint32_t r=rem;
  while(r){ int v=__builtin_ctz(r); r&=r-1; int d=__builtin_popcount(adj[v]&rem); if(d>bd){bd=d;best=v;} }
  if(bd==0){ return 1ull<<__builtin_popcount(rem); }
  uint32_t rem2=rem&~(1u<<best);
  return is_rec(rem2) + is_rec(rem2 & ~adj[best]);
}
static uint64_t independent_sets(void){ return is_rec((nv>=32)?0xFFFFFFFFu:((1u<<nv)-1)); }

static void build_adj(int8_t (*c)[2], int n){
  nv=n;
  for(int i=0;i<n;i++) adj[i]=0;
  for(int i=0;i<n;i++) for(int j=i+1;j<n;j++){
    int dx=abs(c[i][0]-c[j][0]), dy=abs(c[i][1]-c[j][1]);
    if(dx+dy==1){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
  }
}

static int DO_HIST=1;
#define KEEP 8
typedef struct { int8_t c[MAXN][2]; } shp;
static shp ex_tau[KEEP], ex_pm[KEEP], ex_ismin[KEEP], ex_ismax[KEEP]; static int nex_tau,nex_pm,nex_ismin,nex_ismax;
static int8_t (*curc)[2];
static void keep(shp*arr,int*n,int reset){ if(reset)*n=0; if(*n<KEEP){ memcpy(arr[*n].c,curc,2*N); (*n)++; } }
static void show(const char*lab, shp*arr,int n){
  for(int s=0;s<n;s++){ int W2=0,H2=0; for(int i=0;i<N;i++){ if(arr[s].c[i][0]>H2)H2=arr[s].c[i][0]; if(arr[s].c[i][1]>W2)W2=arr[s].c[i][1]; }
    char g[MAXN][MAXN+1]; for(int i=0;i<=H2;i++){ for(int j=0;j<=W2;j++) g[i][j]='.'; g[i][W2+1]=0; }
    for(int i=0;i<N;i++) g[arr[s].c[i][0]][arr[s].c[i][1]]='#';
    printf("%s shape %d:\n",lab,s); for(int i=0;i<=H2;i++) printf("  %s\n",g[i]); }
}
static void account(void){
  uint64_t tau=tau_of();
  uint64_t pm=perfect_matchings();
  uint64_t is=independent_sets();
  sum_tau+=tau; sum_pm+=pm; sum_is+=is;
  if(tau>max_tau){max_tau=tau;max_tau_cnt=1;keep(ex_tau,&nex_tau,1);} else if(tau==max_tau){ max_tau_cnt++; keep(ex_tau,&nex_tau,0);}
  if(pm>max_pm){max_pm=pm;max_pm_cnt=1;keep(ex_pm,&nex_pm,1);} else if(pm==max_pm){ max_pm_cnt++; keep(ex_pm,&nex_pm,0);}
  if(is<min_is){min_is=is;min_is_cnt=1;keep(ex_ismin,&nex_ismin,1);} else if(is==min_is){ min_is_cnt++; keep(ex_ismin,&nex_ismin,0);}
  if(is>max_is){max_is=is;max_is_cnt=1;keep(ex_ismax,&nex_ismax,1);} else if(is==max_is){ max_is_cnt++; keep(ex_ismax,&nex_ismax,0);}
  if(tau&1) cnt_tau_odd++;
  // unicyclic: edges == n  (connected) -> tau == cycle length; count separately
  int e=0; for(int i=0;i<nv;i++) e+=__builtin_popcount(adj[i]); e/=2;
  if(e==nv) cnt_unicyclic++;
  if(DO_HIST){ hadd(h_tau,tau); hadd(h_pm,pm); hadd(h_is,is); }
}

static void process(void){
  fixedcount++;
  int8_t c[MAXN][2], best[MAXN][2], t[MAXN][2];
  for(int i=0;i<N;i++){ c[i][0]=cellx[i]; c[i][1]=celly[i]; }
  normalize(c,N);
  memcpy(best,c,2*N);
  for(int s=1;s<8;s++){
    for(int i=0;i<N;i++){
      int x=c[i][0], y=c[i][1], nx, ny;
      switch(s){
        case 1: nx=-x; ny=y; break;
        case 2: nx=x; ny=-y; break;
        case 3: nx=-x; ny=-y; break;
        case 4: nx=y; ny=x; break;
        case 5: nx=-y; ny=x; break;
        case 6: nx=y; ny=-x; break;
        default: nx=-y; ny=-x; break;
      }
      t[i][0]=nx; t[i][1]=ny;
    }
    normalize(t,N);
    if(cmpshape(t,best,N)<0) memcpy(best,t,2*N);
  }
  if(cmpshape(best,c,N)!=0) return;
  freecount++;
  build_adj(c,N); curc=c;
  account();
}

static int untried_x[MAXN*4+10], untried_y[MAXN*4+10];
static void rec(int depth, int ustart, int uend){
  int myend=uend;
  for(int i=ustart;i<uend;i++){
    int x=untried_x[i], y=untried_y[i];
    cellx[depth]=x; celly[depth]=y;
    if(depth+1==N){ process(); continue; }
    if(depth==5 && SPLITK>1){ if((splitctr++)%SPLITK!=SPLITR){ continue; } }
    int saveend=myend;
    const int dx[4]={1,-1,0,0}, dy[4]={0,0,1,-1};
    for(int d=0;d<4;d++){
      int nx=x+dx[d], ny=y+dy[d];
      if(ny<0 || (ny==0 && nx<MAXN)) continue;
      if(used[ny][nx]) continue;
      used[ny][nx]=1; untried_x[myend]=nx; untried_y[myend]=ny; myend++;
    }
    rec(depth+1, i+1, myend);
    for(int k=saveend;k<myend;k++) used[untried_y[k]][untried_x[k]]=0;
    myend=saveend;
  }
}

static void print128(unsigned __int128 v){ char b[64]; int i=63; b[i]=0; if(!v){printf("0");return;} while(v){ b[--i]='0'+(int)(v%10); v/=10; } printf("%s",b+i); }

int main(int argc,char**argv){
  if(argc>1 && strcmp(argv[1],"test")==0){
    // rectangle tests: argv[2]=rows argv[3]=cols
    int r=atoi(argv[2]), cc=atoi(argv[3]); int8_t c[MAXN][2]; int n=0;
    for(int i=0;i<r;i++) for(int j=0;j<cc;j++){ c[n][0]=i; c[n][1]=j; n++; }
    build_adj(c,n);
    printf("%dx%d: tau=%llu pm=%llu is=%llu\n",r,cc,(unsigned long long)spanning_trees(),(unsigned long long)perfect_matchings(),(unsigned long long)independent_sets());
    return 0;
  }
  N=atoi(argv[1]); if(argc>3){SPLITK=atoll(argv[2]);SPLITR=atoll(argv[3]);}
  const char*tag = argc>4 ? argv[4] : "x";
  if(argc>5){ USE_DBL=atoi(argv[5])&1; CHECK=(atoi(argv[5])>>1)&1; }
  int SHOW = argc>6 ? atoi(argv[6]) : 0;
  h_tau=calloc(HS,sizeof(hent)); h_pm=calloc(HS,sizeof(hent)); h_is=calloc(HS,sizeof(hent));
  memset(used,0,sizeof used);
  used[0][MAXN]=1; untried_x[0]=MAXN; untried_y[0]=0;
  rec(0,0,1);
  printf("n=%d fixed=%llu free=%llu\n",N,(unsigned long long)fixedcount,(unsigned long long)freecount);
  printf("sum_tau="); print128(sum_tau); printf(" max_tau=%llu max_tau_cnt=%llu tau_odd=%llu unicyclic=%llu\n",(unsigned long long)max_tau,(unsigned long long)max_tau_cnt,(unsigned long long)cnt_tau_odd,(unsigned long long)cnt_unicyclic);
  printf("sum_pm="); print128(sum_pm); printf(" max_pm=%llu max_pm_cnt=%llu\n",(unsigned long long)max_pm,(unsigned long long)max_pm_cnt);
  printf("sum_is="); print128(sum_is); printf(" min_is=%llu min_is_cnt=%llu max_is=%llu max_is_cnt=%llu\n",(unsigned long long)min_is,(unsigned long long)min_is_cnt,(unsigned long long)max_is,(unsigned long long)max_is_cnt);
  if(CHECK) printf("bareiss/double mismatches=%llu\n",(unsigned long long)mismatches);
  if(SHOW){ show("max_tau",ex_tau,nex_tau); show("max_pm",ex_pm,nex_pm); show("min_is",ex_ismin,nex_ismin); show("max_is",ex_ismax,nex_ismax); }
  char fn[256];
  snprintf(fn,256,"hist_tau_%d_%s.txt",N,tag); hdump(h_tau,fn);
  snprintf(fn,256,"hist_pm_%d_%s.txt",N,tag); hdump(h_pm,fn);
  snprintf(fn,256,"hist_is_%d_%s.txt",N,tag); hdump(h_is,fn);
  return 0;
}
