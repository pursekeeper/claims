// Count geometrically distinct open and closed knight's tours summed over all free n-ominoes.
// A tour is counted up to the symmetry group of its board (Burnside over Aut(board) <= D4).
#define main main_unused
#include "knightpoly.c"
#undef main

static uint64_t tot_open_tours, tot_closed_tours, tot_open_boards, tot_closed_boards;
static uint64_t tot_open_undirected, tot_closed_undirected; // raw counts (not up to symmetry)
static int autperm[8][MAXN]; static int naut;
static uint32_t padj[MAXN]; // adjacency of current path/cycle
static uint64_t fixcnt[8]; static uint64_t symnum; static uint64_t tot_open_sym, tot_closed_sym;
static int pathseq[MAXN];

static void account_path(int len, int cyclic){
  // build padj
  for(int i=0;i<N;i++) padj[i]=0;
  for(int i=0;i+1<len;i++){ int a=pathseq[i],b=pathseq[i+1]; padj[a]|=1u<<b; padj[b]|=1u<<a; }
  if(cyclic){ int a=pathseq[len-1],b=pathseq[0]; padj[a]|=1u<<b; padj[b]|=1u<<a; }
  int stab=0;
  for(int t=0;t<naut;t++){
    int ok=1;
    for(int i=0;i<N && ok;i++){
      uint32_t m=padj[i], img=0;
      while(m){ int j=__builtin_ctz(m); m&=m-1; img|=1u<<autperm[t][j]; }
      if(img!=padj[autperm[t][i]]) ok=0;
    }
    if(ok) fixcnt[t]++;
    stab+=ok;
  }
  if(stab>1) symnum+=stab;
}
static void dfs_open(int v, uint32_t visited, int len){
  uint32_t rem=ALL&~visited;
  if(!rem){ // undirected: count only when start index < end index
    if(pathseq[0]<pathseq[len-1]) account_path(len,0);
    return;
  }
  uint32_t vb=1u<<v;
  if(!(adj[v]&rem)) return;
  if(popc(rem)>1){
    if(!connected_mask(rem|vb)) return;
    int ones=0; uint32_t r=rem;
    while(r){ int u=__builtin_ctz(r); r&=r-1; int d=popc(adj[u]&(rem|vb)); if(d==0) return; if(d==1){ ones++; if(ones>1) return; } }
  }
  uint32_t cand=adj[v]&rem;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1; pathseq[len]=u; dfs_open(u,visited|(1u<<u),len+1); }
}
static void dfs_cyc(int v, uint32_t visited, int len){
  uint32_t rem=ALL&~visited;
  if(!rem){ if((adj[v]&1u) && pathseq[1]<pathseq[len-1]) account_path(len,1); return; }
  uint32_t vb=1u<<v;
  if(!(adj[v]&rem)) return;
  if(popc(rem)>1){
    if(!connected_mask(rem|vb|1u)) return;
    uint32_t r=rem;
    while(r){ int u=__builtin_ctz(r); r&=r-1; int d=popc(adj[u]&(rem|vb|1u)); if(d<2) return; }
  }
  uint32_t cand=adj[v]&rem;
  while(cand){ int u=__builtin_ctz(cand); cand&=cand-1; pathseq[len]=u; dfs_cyc(u,visited|(1u<<u),len+1); }
}

static void compute_aut(void){
  int k0[MAXN]; keyof(0,xs,ys,N,k0);
  naut=0;
  for(int t=0;t<8;t++){
    int k[MAXN]; keyof(t,xs,ys,N,k);
    int same=1; for(int i=0;i<N;i++) if(k[i]!=k0[i]){ same=0; break; }
    if(!same) continue;
    // build permutation: cell i -> index of transformed cell
    int tx[MAXN],ty[MAXN],mx=1<<20,my=1<<20;
    for(int i=0;i<N;i++){ transform(t,xs[i],ys[i],&tx[i],&ty[i]); if(tx[i]<mx)mx=tx[i]; if(ty[i]<my)my=ty[i]; }
    int mx0=1<<20,my0=1<<20; for(int i=0;i<N;i++){ if(xs[i]<mx0)mx0=xs[i]; if(ys[i]<my0)my0=ys[i]; }
    for(int i=0;i<N;i++){
      int px=tx[i]-mx+mx0, py=ty[i]-my+my0, found=-1;
      for(int j=0;j<N;j++) if(xs[j]==px && ys[j]==py){ found=j; break; }
      autperm[naut][i]=found;
    }
    naut++;
  }
}

static void process2(void){
  for(int i=0;i<N;i++){ xs[i]=poly[i]%W; ys[i]=poly[i]/W; }
  nverts=N; ALL=(1u<<N)-1;
  for(int i=0;i<N;i++) adj[i]=0;
  for(int i=0;i<N;i++) for(int j=i+1;j<N;j++){ int dx=abs(xs[i]-xs[j]),dy=abs(ys[i]-ys[j]); if((dx==1&&dy==2)||(dx==2&&dy==1)){adj[i]|=1u<<j;adj[j]|=1u<<i;} }
  if(!connected_mask(ALL)) return;
  if(!is_canonical(xs,ys,N)) return;
  int black=0; for(int i=0;i<N;i++) if((xs[i]+ys[i])&1) black++;
  if(abs(2*black-N)>1) return;
  compute_aut();
  // open tours
  memset(fixcnt,0,sizeof fixcnt); symnum=0;
  int ones=0; for(int i=0;i<N;i++) if(popc(adj[i])==1) ones++;
  if(ones<=2) for(int s=0;s<N;s++){ pathseq[0]=s; dfs_open(s,1u<<s,1); }
  if(fixcnt[0]){ uint64_t sum=0; for(int t=0;t<naut;t++) sum+=fixcnt[t]; tot_open_tours+=sum/naut; tot_open_boards++; tot_open_undirected+=fixcnt[0]; if(symnum%naut) fprintf(stderr,"sym err\n"); tot_open_sym+=symnum/naut; if(sum%naut) fprintf(stderr,"Burnside error open\n"); }
  if(2*black==N && N>=4){
    memset(fixcnt,0,sizeof fixcnt); symnum=0;
    int mind=8; for(int i=0;i<N;i++) if(popc(adj[i])<mind) mind=popc(adj[i]);
    if(mind>=2){ pathseq[0]=0; dfs_cyc(0,1u,1); }
    if(fixcnt[0]){ uint64_t sum=0; for(int t=0;t<naut;t++) sum+=fixcnt[t]; tot_closed_tours+=sum/naut; tot_closed_boards++; tot_closed_undirected+=fixcnt[0]; if(symnum%naut) fprintf(stderr,"sym err\n"); tot_closed_sym+=symnum/naut; if(sum%naut) fprintf(stderr,"Burnside error closed\n"); }
  }
}

static void rec2(int *untried, int nu, int size){
  int newlist[MAXN*8+8];
  while(nu>0){
    int c=untried[--nu]; poly[size]=c; occ[c]=1;
    if(size+1==N) process2();
    else{
      int nn=nu; memcpy(newlist,untried,nu*sizeof(int)); int added[8],na=0;
      for(int d=0;d<gnum;d++){ int nb=c+gdelta[d]; int x=nb%W,y=nb/W;
        if(y<0||(y==0&&x<X0)) continue; if(x<1||x>=W-1||y>=H-1) continue; if(reached[nb]) continue;
        reached[nb]=1; newlist[nn++]=nb; added[na++]=nb; }
      rec2(newlist,nn,size+1);
      for(int i=0;i<na;i++) reached[added[i]]=0;
    }
    occ[c]=0;
  }
}
int main(int argc,char**argv){
  N=atoi(argv[1]); if(argc>2) MODE=atoi(argv[2]);
  if(MODE==0){ gnum=4; for(int d=0;d<4;d++) gdelta[d]=ory[d]*W+orx[d]; } else { gnum=8; for(int d=0;d<8;d++) gdelta[d]=kny[d]*W+knx[d]; }
  clock_t t0=clock(); int start=X0; reached[start]=1; int untried[1]={start}; rec2(untried,1,0);
  printf("n=%d mode=%d openboards=%llu opentours_geom=%llu opentours_raw=%llu closedboards=%llu closedtours_geom=%llu closedtours_raw=%llu opensym=%llu closedsym=%llu (%.1fs)\n",
    N,MODE,(unsigned long long)tot_open_boards,(unsigned long long)tot_open_tours,(unsigned long long)tot_open_undirected,
    (unsigned long long)tot_closed_boards,(unsigned long long)tot_closed_tours,(unsigned long long)tot_closed_undirected,(unsigned long long)tot_open_sym,(unsigned long long)tot_closed_sym,(double)(clock()-t0)/CLOCKS_PER_SEC);
  return 0;
}
