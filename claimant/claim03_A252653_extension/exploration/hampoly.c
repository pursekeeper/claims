// Enumerate free polyominoes with n cells (Redelmeier + canonical form),
// count those whose cell-adjacency graph has a Hamiltonian cycle / Hamiltonian path.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXN 20
static int N; static long long SPLITK=1, SPLITR=0, splitctr=0;
// Redelmeier on a half-plane grid: cells (x,y) with y>0 or (y==0 && x>=0). Use lattice width W.
#define W (2*MAXN+2)
#define H (MAXN+2)
static int cellx[MAXN], celly[MAXN];
static uint8_t used[H][W];     // in untried set or in polyomino (reached)
static uint64_t fixedcount, freecount, hamcyc, hampath;
static uint64_t hamcyc_fixed;

typedef struct { int8_t x[MAXN], y[MAXN]; } shape_t;

static int cmpcell(const void*a,const void*b){ const int8_t*p=a,*q=b; if(p[0]!=q[0]) return p[0]-q[0]; return p[1]-q[1]; }

// normalize: translate so min x = 0, min y = 0, sort cells
static void normalize(int8_t (*c)[2], int n){
  int mx=127,my=127;
  for(int i=0;i<n;i++){ if(c[i][0]<mx)mx=c[i][0]; if(c[i][1]<my)my=c[i][1]; }
  for(int i=0;i<n;i++){ c[i][0]-=mx; c[i][1]-=my; }
  qsort(c,n,2,cmpcell);
}
static int cmpshape(int8_t (*a)[2], int8_t (*b)[2], int n){
  return memcmp(a,b,2*n);
}

// Hamiltonian search on small graph: adjacency bitmasks
static uint32_t adj[MAXN];
static int nverts;
static int found;
static void dfs_cycle(int v, uint32_t visited, int depth){
  if(found) return;
  if(depth==nverts){ if(adj[v]&1u) found=1; return; }
  uint32_t cand = adj[v] & ~visited;
  // pruning: any unvisited vertex (other than start-neighbors) with < 2 available connections?
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1;
    dfs_cycle(u, visited|(1u<<u), depth+1);
    if(found) return;
  }
}
static int has_ham_cycle(void){
  if(nverts<4 && nverts!=1) return 0; // grid graphs: cycle needs >=4
  for(int i=0;i<nverts;i++) if(__builtin_popcount(adj[i])<2) return 0;
  found=0; dfs_cycle(0,1u,1); return found;
}
static void dfs_path(int v, uint32_t visited, int depth){
  if(found) return;
  if(depth==nverts){ found=1; return; }
  // pruning: check connectivity of unvisited plus v? keep simple.
  uint32_t cand = adj[v] & ~visited;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1;
    dfs_path(u, visited|(1u<<u), depth+1);
    if(found) return;
  }
}
static int has_ham_path(void){
  int leaves=0;
  for(int i=0;i<nverts;i++) if(__builtin_popcount(adj[i])<2) leaves++;
  if(leaves>2) return 0;
  found=0;
  for(int s=0;s<nverts && !found;s++){
    if(leaves>0 && __builtin_popcount(adj[s])>=2) continue; // must start at a leaf if there is one
    dfs_path(s,1u<<s,1);
  }
  return found;
}

static int PRUNE=0;
static void process(void){
  fixedcount++;
  int8_t c[MAXN][2], best[MAXN][2], t[MAXN][2];
  for(int i=0;i<N;i++){ c[i][0]=cellx[i]; c[i][1]=celly[i]; }
  if(PRUNE){
    // count leaf cells (degree<=1) quickly using the used[][] grid: all N cells are marked used, but so are untried neighbors. So compute degrees from cell list.
    int leaves=0;
    for(int i=0;i<N;i++){ int d=0; for(int j=0;j<N;j++){ if(abs(c[i][0]-c[j][0])+abs(c[i][1]-c[j][1])==1) d++; } if(d<2) leaves++; }
    if(leaves>2) return;
    if(N%2==1 && leaves==0) {} // path still possible
  }
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
  if(cmpshape(best,c,N)!=0) return; // not canonical representative
  freecount++;
  // build adjacency
  nverts=N;
  for(int i=0;i<N;i++) adj[i]=0;
  for(int i=0;i<N;i++) for(int j=i+1;j<N;j++){
    int dx=abs(c[i][0]-c[j][0]), dy=abs(c[i][1]-c[j][1]);
    if(dx+dy==1){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
  }
  if(N%2==0 && has_ham_cycle()) hamcyc++;
  if(has_ham_path()) hampath++;
}

// Redelmeier recursion
static int untried_x[MAXN*4+10], untried_y[MAXN*4+10];
static void rec(int depth, int ustart, int uend){
  // untried set is entries [ustart, uend)
  int myend=uend;
  for(int i=ustart;i<uend;i++){
    int x=untried_x[i], y=untried_y[i];
    cellx[depth]=x; celly[depth]=y;
    if(depth+1==N){ process(); continue; }
    if(depth==5 && SPLITK>1){ if((splitctr++)%SPLITK!=SPLITR){ continue; } }
    // add neighbors
    int saveend=myend;
    const int dx[4]={1,-1,0,0}, dy[4]={0,0,1,-1};
    for(int d=0;d<4;d++){
      int nx=x+dx[d], ny=y+dy[d];
      if(ny<0 || (ny==0 && nx<MAXN)) continue; // origin at (MAXN,0); half-plane rule: y>0 or (y==0 && x>=MAXN)
      if(used[ny][nx]) continue;
      used[ny][nx]=1; untried_x[myend]=nx; untried_y[myend]=ny; myend++;
    }
    rec(depth+1, i+1, myend);
    for(int k=saveend;k<myend;k++) used[untried_y[k]][untried_x[k]]=0;
    myend=saveend;
  }
  // caller restores nothing else; cells chosen are marked used by whoever put them in untried
}

int main(int argc,char**argv){
  N=atoi(argv[1]); if(argc>2) PRUNE=atoi(argv[2]); if(argc>4){SPLITK=atoll(argv[3]);SPLITR=atoll(argv[4]);}
  memset(used,0,sizeof used);
  used[0][MAXN]=1; untried_x[0]=MAXN; untried_y[0]=0;
  rec(0,0,1);
  printf("n=%d fixed=%llu free=%llu hamcycle=%llu hampath=%llu\n",N,
    (unsigned long long)fixedcount,(unsigned long long)freecount,(unsigned long long)hamcyc,(unsigned long long)hampath);
  return 0;
}
