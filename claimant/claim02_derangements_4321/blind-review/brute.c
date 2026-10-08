// Brute force: enumerate all permutations of {1..n} (Heap's algorithm),
// compute LIS, LDS, and number of fixed points directly.
// Prints for each n: der&LIS<=3, der&LDS<=3, LIS<=3 (no der cond), derangements.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n;
static int p[20];

static int lis(void){ // O(n^2) DP
    int best=0, d[20];
    for(int i=0;i<n;i++){ d[i]=1; for(int j=0;j<i;j++) if(p[j]<p[i] && d[j]+1>d[i]) d[i]=d[j]+1; if(d[i]>best)best=d[i]; }
    return best;
}
static int lds(void){
    int best=0, d[20];
    for(int i=0;i<n;i++){ d[i]=1; for(int j=0;j<i;j++) if(p[j]>p[i] && d[j]+1>d[i]) d[i]=d[j]+1; if(d[i]>best)best=d[i]; }
    return best;
}

int main(int argc,char**argv){
    int nmax = argc>1 ? atoi(argv[1]) : 10;
    for(n=1;n<=nmax;n++){
        unsigned long long c_der_1234=0, c_der_4321=0, c_1234=0, c_der=0;
        for(int i=0;i<n;i++) p[i]=i+1;
        int c[20]; memset(c,0,sizeof c);
        // evaluate
        #define EVAL do{ int fp=0; for(int i=0;i<n;i++) if(p[i]==i+1) fp++; \
            int L=lis(); int D=lds(); \
            if(L<=3) c_1234++; if(fp==0) c_der++; \
            if(fp==0 && L<=3) c_der_1234++; if(fp==0 && D<=3) c_der_4321++; }while(0)
        EVAL;
        int i=0;
        while(i<n){
            if(c[i]<i){
                if(i%2==0){int t=p[0];p[0]=p[i];p[i]=t;} else {int t=p[c[i]];p[c[i]]=p[i];p[i]=t;}
                EVAL;
                c[i]++; i=0;
            } else { c[i]=0; i++; }
        }
        printf("n=%2d der&avoid1234=%llu der&avoid4321=%llu avoid1234=%llu derangements=%llu\n",
               n,c_der_1234,c_der_4321,c_1234,c_der);
        fflush(stdout);
    }
    return 0;
}
