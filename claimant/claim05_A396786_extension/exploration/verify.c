// Independent check: enumerate all x <= B satisfying the +-1 conditions for the
// first J odd primes (via a hand-rolled CRT over residue combos), then filter by
// the remaining primes' conditions and by the mod-2 condition; print survivors.
// Usage: verify K n J B    (K=2 -> A395587 uses mod q^(5-K)=q^3; K=3 -> q^2)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
typedef unsigned long long u64;
static u64 primes[]={2,3,5,7,11,13,17,19,23,29,31,37,41,43,47};
static u128 ipow(u64 b,int e){u128 r=1;while(e--)r*=b;return r;}
static u128 modinv(u128 a,u128 m){ // extended gcd
  __int128 t=0,nt=1,r=m,nr=a%m; while(nr){__int128 q=r/nr,tmp; tmp=t-q*nt;t=nt;nt=tmp; tmp=r-q*nr;r=nr;nr=tmp;} if(t<0)t+=m; return (u128)t;}
static u128 parse(const char*s){u128 v=0;for(;*s;s++)v=v*10+(*s-'0');return v;}
static void print128(u128 v){char b[64];int i=63;b[i]=0;if(!v){puts("0");return;}while(v){b[--i]='0'+(int)(v%10);v/=10;}puts(b+i);}
// deterministic Miller-Rabin for < 2^64; for larger just print candidate
static u64 mulmod(u64 a,u64 b,u64 m){return (u128)a*b%m;}
static u64 powmod(u64 a,u64 e,u64 m){u64 r=1;a%=m;while(e){if(e&1)r=mulmod(r,a,m);a=mulmod(a,a,m);e>>=1;}return r;}
static int isprime64(u64 n){if(n<2)return 0;static const u64 bs[]={2,3,5,7,11,13,17,19,23,29,31,37};
  for(int i=0;i<12;i++){if(n%bs[i]==0)return n==bs[i];}
  u64 d=n-1;int s=0;while(!(d&1)){d>>=1;s++;}
  for(int i=0;i<12;i++){u64 x=powmod(bs[i],d,n);if(x==1||x==n-1)continue;int ok=0;for(int r=1;r<s;r++){x=mulmod(x,x,n);if(x==n-1){ok=1;break;}}if(!ok)return 0;}return 1;}
int main(int argc,char**argv){
  int K=atoi(argv[1]),n=atoi(argv[2]),J=atoi(argv[3]); u128 B=parse(argv[4]);
  int e=5-K;
  // mod-2 condition: residues r mod 32 with r^(2^K) = +-1 mod 32
  int ok2[32]={0}; for(int r=0;r<32;r++){u64 v=1;int ex=1<<K;for(int i=0;i<ex;i++)v=v*r%32; if(v==1||v==31)ok2[r]=1;}
  u128 M=1; u128 mods[16]; for(int i=1;i<=J;i++){mods[i]=ipow(primes[i],e);M*=mods[i];}
  long count=0,surv=0;
  for(int combo=0;combo<(1<<J);combo++){
    // CRT: x = sum r_i * (M/m_i) * inv(M/m_i mod m_i)
    u128 x=0;
    for(int i=1;i<=J;i++){u128 mi=mods[i];u128 Mi=M/mi;u128 ri=((combo>>(i-1))&1)?mi-1:1; u128 c=(ri*modinv(Mi%mi,mi))%mi; x=(x+c*Mi)%M;}
    // sanity check of CRT
    for(int i=1;i<=J;i++){u128 mi=mods[i];u128 ri=((combo>>(i-1))&1)?mi-1:1; if(x%mi!=ri){fprintf(stderr,"CRT bug\n");return 1;}}
    for(u128 y=x; y<=B; y+=M){
      count++;
      if(y<2) continue;
      if(!ok2[(int)(y%32)]) continue;
      int good=1;
      for(int i=J+1;i<n;i++){u128 mi=mods[i]=ipow(primes[i],e);u128 r=y%mi; if(r!=1&&r!=mi-1){good=0;break;}}
      if(!good) continue;
      // survivor of all residue conditions
      if(y < ((u128)1<<64)){ if(!isprime64((u64)y)) continue; }
      surv++; print128(y);
    }
  }
  fprintf(stderr,"candidates stepped: %ld, printed: %ld (%s)\n",count,surv, (B<((u128)1<<64))?"64-bit: primes only":">64-bit: residue survivors, need external primality");
  return 0;
}
