// independent check: enumerate all permutations (Heap's algorithm), count those with no fixed point and LIS<=3 (mode 1) / LDS<=3 (mode 3)
#include <stdio.h>
#include <stdlib.h>
int n, mode; int p[16]; unsigned long long cnt;
static int lis_le3(void){ int tops[4]; int np=0; for(int i=0;i<n;i++){int v=p[i]; int j=0; while(j<np && (mode==3? tops[j]>v : tops[j]<v)) j++; if(j==np){ if(np==3) return 0; np++;} tops[j]=v;} return 1;}
static void check(void){ for(int i=0;i<n;i++) if(p[i]==i+1) return; if(lis_le3()) cnt++; }
static void heap(int k){ if(k==1){check();return;} for(int i=0;i<k-1;i++){ heap(k-1); int j = (k%2==0)? i : 0; int t=p[j]; p[j]=p[k-1]; p[k-1]=t; } heap(k-1); }
int main(int argc,char**argv){ n=atoi(argv[1]); mode=atoi(argv[2]); for(int i=0;i<n;i++)p[i]=i+1; cnt=0; heap(n); printf("%d %llu\n",n,cnt); return 0;}
