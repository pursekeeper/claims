// read polyominoes "n x,y x,y ..." ; for each, knight graph; report per n: K (connected), O (ham path), C (ham cycle)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXN 16
static uint16_t *dp; // dp[mask] bitset of end vertices reachable with path covering mask starting anywhere
int main(){
  static long K[MAXN+1],O[MAXN+1],C[MAXN+1],T[MAXN+1];
  char line[4096];
  dp=malloc(sizeof(uint16_t)<<MAXN);
  while(fgets(line,sizeof line,stdin)){
    int n; int xs[MAXN],ys[MAXN]; char*p=line; n=strtol(p,&p,10);
    for(int i=0;i<n;i++){ xs[i]=strtol(p,&p,10); p++; ys[i]=strtol(p,&p,10);}
    T[n]++;
    uint16_t adj[MAXN]; memset(adj,0,sizeof adj);
    for(int i=0;i<n;i++)for(int j=0;j<n;j++){int dx=abs(xs[i]-xs[j]),dy=abs(ys[i]-ys[j]); if((dx==1&&dy==2)||(dx==2&&dy==1)) adj[i]|=1<<j;}
    // connectivity
    uint16_t seen=1,fr=1; while(fr){uint16_t nf=0; for(int i=0;i<n;i++) if(fr>>i&1) nf|=adj[i]; nf&=~seen; seen|=nf; fr=nf;}
    if(seen!=(uint16_t)((1<<n)-1)) continue;
    K[n]++;
    int full=(1<<n)-1;
    // ham path from vertex 0? need any start: dp[mask] = set of v such that exists path covering mask ending at v.
    memset(dp,0,sizeof(uint16_t)<<n);
    for(int i=0;i<n;i++) dp[1<<i]=1<<i;
    for(int m=1;m<=full;m++){ uint16_t e=dp[m]; if(!e) continue; for(int v=0;v<n;v++) if(e>>v&1){ uint16_t nb=adj[v]&~m; while(nb){int w=__builtin_ctz(nb); nb&=nb-1; dp[m|1<<w]|=1<<w;} } }
    if(dp[full]) O[n]++;
    // ham cycle: path starting at vertex 0 covering all ending at neighbor of 0
    memset(dp,0,sizeof(uint16_t)<<n); dp[1]=1;
    for(int m=1;m<=full;m++){ uint16_t e=dp[m]; if(!e) continue; for(int v=0;v<n;v++) if(e>>v&1){ uint16_t nb=adj[v]&~m; while(nb){int w=__builtin_ctz(nb); nb&=nb-1; dp[m|1<<w]|=1<<w;} } }
    if(n>=3 && (dp[full]&adj[0])) C[n]++;
  }
  for(int n=1;n<=MAXN;n++) if(T[n]) printf("n=%d total=%ld K=%ld O=%ld C=%ld\n",n,T[n],K[n],O[n],C[n]);
}
