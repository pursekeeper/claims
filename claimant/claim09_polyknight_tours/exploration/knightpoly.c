// Enumerate free n-ominoes (Redelmeier for fixed + canonical form for free),
// and for each free n-omino examine the knight-move graph on its cells:
//   - is it connected?
//   - does it have a Hamiltonian path (open knight's tour)?
//   - does it have a Hamiltonian cycle (closed knight's tour)?
// Optional: -k  enumerate polyknights instead (knight-connected cell sets),
//           -x  enumerate polykings (8-connected sets), and use knight graph on them.
// Usage: knightpoly N [mode] [split k r]   mode: 0=polyomino (default), 1=polyknight
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifndef MAXN
#define MAXN 22
#endif
static int N;
static int MODE = 0;   // 0: polyomino (4-adjacency growth), 1: polyknight (knight adjacency growth)
static long long SPLITK = 1, SPLITR = 0, splitctr = 0;
#define W (2*MAXN+5)
#define H (MAXN+3)
#define X0 (MAXN+2)
static uint8_t reached[H*W];   // in untried set or in polyomino
static uint8_t occ[H*W];
static int poly[MAXN];          // grid ids of cells in current polyomino
static uint64_t cnt_fixed, cnt_free, cnt_conn, cnt_open, cnt_closed;
static uint64_t cnt_conn_fixed;
static int PRINT_EXAMPLES = 0;
static int found_closed_example = 0;

static const int knx[8] = {1,2,2,1,-1,-2,-2,-1};
static const int kny[8] = {2,1,-1,-2,-2,-1,1,2};
static const int orx[4] = {1,0,-1,0};
static const int ory[4] = {0,1,0,-1};

// growth neighbor offsets (as grid deltas)
static int gdelta[8], gnum;

// ---------- free canonical form ----------
static void transform(int t, int x, int y, int *ox, int *oy){
  int a=x,b=y;
  switch(t){
    case 0: *ox=a; *oy=b; break;
    case 1: *ox=-b; *oy=a; break;
    case 2: *ox=-a; *oy=-b; break;
    case 3: *ox=b; *oy=-a; break;
    case 4: *ox=-a; *oy=b; break;
    case 5: *ox=b; *oy=a; break;
    case 6: *ox=a; *oy=-b; break;
    case 7: *ox=-b; *oy=-a; break;
  }
}
static void keyof(int t, int *xs, int *ys, int n, int *key){
  int tx[MAXN], ty[MAXN], mx=1<<20, my=1<<20;
  for(int i=0;i<n;i++){ transform(t,xs[i],ys[i],&tx[i],&ty[i]); if(tx[i]<mx)mx=tx[i]; if(ty[i]<my)my=ty[i]; }
  for(int i=0;i<n;i++) key[i]=(tx[i]-mx)*64+(ty[i]-my);
  // insertion sort
  for(int i=1;i<n;i++){ int v=key[i], j=i-1; while(j>=0 && key[j]>v){ key[j+1]=key[j]; j--; } key[j+1]=v; }
}
// returns 1 if the identity transform gives the lexicographically minimal key (i.e., canonical representative)
static int is_canonical(int *xs, int *ys, int n){
  int k0[MAXN], k[MAXN];
  keyof(0,xs,ys,n,k0);
  for(int t=1;t<8;t++){
    keyof(t,xs,ys,n,k);
    int c=memcmp(k,k0,n*sizeof(int)); // memcmp on ints is fine only if we compare lexicographically; do manual
    c=0; for(int i=0;i<n;i++){ if(k[i]!=k0[i]){ c = (k[i]<k0[i])?-1:1; break; } }
    if(c<0) return 0;
  }
  return 1;
}

// ---------- knight graph tests ----------
static uint32_t adj[MAXN];
static uint32_t ALL;
static int nverts;

static int popc(uint32_t x){ return __builtin_popcount(x); }

static int connected_mask(uint32_t mask){
  if(!mask) return 1;
  uint32_t seen = mask & (-mask), frontier=seen;
  while(frontier){
    uint32_t nf=0;
    uint32_t f=frontier;
    while(f){ int v=__builtin_ctz(f); f&=f-1; nf |= adj[v]; }
    nf &= mask & ~seen;
    seen |= nf; frontier = nf;
  }
  return seen==mask;
}

// Hamiltonian path DFS. visited includes v. Returns 1 if a Ham path completing all vertices exists.
static int ham_path(int v, uint32_t visited){
  uint32_t rem = ALL & ~visited;
  if(!rem) return 1;
  uint32_t vb = 1u<<v;
  if(!(adj[v] & rem)) return 0;
  if(popc(rem)>1){
    if(!connected_mask(rem | vb)) return 0;
    // degree pruning
    int ones=0;
    uint32_t r=rem;
    while(r){ int u=__builtin_ctz(r); r&=r-1;
      int d = popc(adj[u] & (rem|vb));
      if(d==0) return 0;
      if(d==1){ ones++; if(ones>1) return 0; }
    }
  }
  uint32_t cand = adj[v] & rem;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1;
    if(ham_path(u, visited|(1u<<u))) return 1;
  }
  return 0;
}
static int has_open_tour(void){
  // if any vertex has degree 1 it must be an endpoint: start there
  int ones=0, onev=-1;
  for(int i=0;i<nverts;i++){ int d=popc(adj[i]); if(d==0) return nverts==1; if(d==1){ ones++; onev=i; } }
  if(ones>2) return 0;
  if(ones>=1) return ham_path(onev, 1u<<onev);
  for(int s=0;s<nverts;s++) if(ham_path(s, 1u<<s)) return 1;
  return 0;
}
// Hamiltonian cycle: start at vertex 0, path must end adjacent to 0.
static int ham_cyc(int v, uint32_t visited){
  uint32_t rem = ALL & ~visited;
  if(!rem) return (adj[v]&1u)!=0;
  uint32_t vb = 1u<<v;
  if(!(adj[v] & rem)) return 0;
  if(popc(rem)>1){
    if(!connected_mask(rem | vb | 1u)) return 0;
    uint32_t r=rem;
    while(r){ int u=__builtin_ctz(r); r&=r-1;
      int d = popc(adj[u] & (rem|vb|1u));
      if(d<2) return 0;
    }
  }
  uint32_t cand = adj[v] & rem;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1;
    if(ham_cyc(u, visited|(1u<<u))) return 1;
  }
  return 0;
}
static int has_closed_tour(void){
  if(nverts<4) return 0;
  for(int i=0;i<nverts;i++) if(popc(adj[i])<2) return 0;
  return ham_cyc(0, 1u);
}

static int xs[MAXN], ys[MAXN];
static void process(void){
  cnt_fixed++;
  for(int i=0;i<N;i++){ xs[i]=poly[i]%W; ys[i]=poly[i]/W; }
  // knight adjacency
  nverts=N; ALL = (N==32)?0xffffffffu:((1u<<N)-1);
  for(int i=0;i<N;i++) adj[i]=0;
  for(int i=0;i<N;i++) for(int j=i+1;j<N;j++){
    int dx=abs(xs[i]-xs[j]), dy=abs(ys[i]-ys[j]);
    if((dx==1&&dy==2)||(dx==2&&dy==1)){ adj[i]|=1u<<j; adj[j]|=1u<<i; }
  }
  int conn = connected_mask(ALL);
  if(conn) cnt_conn_fixed++;
  if(!is_canonical(xs,ys,N)) return;
  cnt_free++;
  if(!conn) return;
  cnt_conn++;
  // bipartite balance: knight graph is bipartite by cell color
  int black=0; for(int i=0;i<N;i++) if((xs[i]+ys[i])&1) black++;
  int white=N-black;
  if(abs(black-white)>1) return;
  if(has_open_tour()){
    cnt_open++;
    if(black==white && has_closed_tour()){
      cnt_closed++;
      if(PRINT_EXAMPLES && !found_closed_example){
        found_closed_example=1;
        fprintf(stderr,"closed tour example n=%d:", N);
        for(int i=0;i<N;i++) fprintf(stderr," (%d,%d)", xs[i]-X0, ys[i]);
        fprintf(stderr,"\n");
      }
    }
  }
}

// ---------- Redelmeier ----------
static void rec(int *untried, int nu, int size){
  int newlist[MAXN*8+8];
  while(nu>0){
    int c = untried[--nu];
    poly[size]=c; occ[c]=1;
    if(size+1==N){
      // split work
      if(SPLITK>1){ if((splitctr++ % SPLITK)==SPLITR) process(); }
      else process();
    } else {
      int nn=nu;
      memcpy(newlist, untried, nu*sizeof(int));
      int added[8], na=0;
      for(int d=0; d<gnum; d++){
        int nb = c + gdelta[d];
        int x = nb % W, y = nb / W;
        if(y<0 || (y==0 && x<X0)) continue;
        if(x<1 || x>=W-1 || y>=H-1) continue;
        if(reached[nb]) continue;
        reached[nb]=1; newlist[nn++]=nb; added[na++]=nb;
      }
      rec(newlist, nn, size+1);
      for(int i=0;i<na;i++) reached[added[i]]=0;
    }
    occ[c]=0;
  }
}

int main(int argc, char **argv){
  N = atoi(argv[1]);
  if(argc>2) MODE = atoi(argv[2]);
  if(argc>4){ SPLITK=atoll(argv[3]); SPLITR=atoll(argv[4]); }
  if(getenv("EX")) PRINT_EXAMPLES=1;
  if(MODE==0){ gnum=4; for(int d=0;d<4;d++) gdelta[d]=ory[d]*W+orx[d]; }
  else { gnum=8; for(int d=0;d<8;d++) gdelta[d]=kny[d]*W+knx[d]; }
  clock_t t0=clock();
  int start = 0*W + X0;
  reached[start]=1;
  int untried[1]={start};
  rec(untried,1,0);
  double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
  printf("n=%d mode=%d fixed=%llu free=%llu connfixed=%llu conn=%llu open=%llu closed=%llu  (%.1fs)\n",
     N, MODE, (unsigned long long)cnt_fixed,(unsigned long long)cnt_free,(unsigned long long)cnt_conn_fixed,
     (unsigned long long)cnt_conn,(unsigned long long)cnt_open,(unsigned long long)cnt_closed, el);
  return 0;
}
