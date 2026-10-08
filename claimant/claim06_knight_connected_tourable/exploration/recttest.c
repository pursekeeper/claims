#define main main_unused
#include "knightpoly.c"
#undef main
int main(int argc,char**argv){
  int r=atoi(argv[1]), c=atoi(argv[2]);
  N=r*c; nverts=N; ALL=(N==32)?0xffffffffu:((1u<<N)-1);
  for(int i=0;i<N;i++){ xs[i]=i%c; ys[i]=i/c; adj[i]=0; }
  for(int i=0;i<N;i++) for(int j=i+1;j<N;j++){ int dx=abs(xs[i]-xs[j]),dy=abs(ys[i]-ys[j]); if((dx==1&&dy==2)||(dx==2&&dy==1)){adj[i]|=1u<<j;adj[j]|=1u<<i;} }
  printf("%dx%d conn=%d open=%d closed=%d\n",r,c,connected_mask(ALL),has_open_tour(),has_closed_tour());
  return 0;
}
