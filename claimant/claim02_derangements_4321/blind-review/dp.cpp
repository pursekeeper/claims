// Independent exact algorithm: transfer DP building the permutation left to right.
// After p values are placed (positions 1..p), the state is:
//   A  : the set of USED values that are > p  (bitmask over values p+1..n, bit i <-> value p+1+i)
//        |A| = k = number of UNUSED values that are <= p  (these can never become fixed points)
//   tails : patience-sorting tails (LIS or LDS structure), each stored as its RANK =
//        number of unused values smaller than that tail.  Only ranks matter for the future.
// The unused values in sorted order are: k "low" values (<= p), then the unused high values (> p).
// Placing at position p+1 the unused value of rank q:
//   q <  k  -> a low value, cannot be a fixed point.
//   q >= k  -> the (q-k)-th unused high value; it is a fixed point iff it equals p+1,
//              i.e. iff bit0 of A is clear and q == k.
// Patience sorting on ranks (increasing mode): replace first tail with rank > q by q, else append;
// all other tails with rank > q lose 1 (the placed value no longer counts as unused).
// Decreasing mode: replace first tail with rank <= q, else append; same decrement rule.
// Reject if the number of tails would exceed M (M=3 <=> avoid 1234 / 4321).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unordered_map>
#include <vector>
#include <string>
using namespace std;
typedef unsigned long long u64;
typedef unsigned __int128 u128;

struct Key { u64 a; u64 r; bool operator==(const Key&o)const{return a==o.a&&r==o.r;} };
struct KH { size_t operator()(const Key&k)const{ u64 h=k.a*0x9E3779B97F4A7C15ULL ^ (k.r+0x632BE59BD9B4E019ULL)*0xBF58476D1CE4E5B9ULL; h^=h>>31; return h; } };

static void print128(u128 x){ char buf[64]; int i=63; buf[i]=0; if(x==0){printf("0");return;} while(x){buf[--i]='0'+(int)(x%10); x/=10;} printf("%s",buf+i); }

// pack ranks: 6 bits each, L in top 4 bits (max 10 tails)... allow up to 10 tails for sanity mode
static inline u64 packR(const int*r,int L){ u64 x=0; for(int i=0;i<L;i++) x|=(u64)r[i]<<(6*i); x|=(u64)L<<60; return x; }
static inline int unpackR(u64 x,int*r){ int L=(int)(x>>60); for(int i=0;i<L;i++) r[i]=(int)((x>>(6*i))&63); return L; }

int main(int argc,char**argv){
    int nmax = atoi(argv[1]);
    int M    = atoi(argv[2]);      // max allowed increasing/decreasing subsequence length (0 => unlimited, capped at 10)
    int dec  = atoi(argv[3]);      // 0: increasing (avoid 12..(M+1)),  1: decreasing
    int der  = atoi(argv[4]);      // 1: require no fixed points
    for(int n=1;n<=nmax;n++){
        int Meff = M>0? M : (n<10? n : 10);
        unordered_map<Key,u128,KH> cur, nxt;
        cur[Key{0,0}] = 1;
        for(int p=0;p<n;p++){
            nxt.clear();
            int U = n-p; // number of unused values
            for(auto &kv : cur){
                u64 A = kv.first.a; int r[12]; int L = unpackR(kv.first.r,r);
                int k = __builtin_popcountll(A);
                u128 cnt = kv.second;
                // list unused high values (as offsets i: value = p+1+i), i in [0,U)
                int hi[64]; int nh=0;
                for(int i=0;i<U;i++) if(!((A>>i)&1)) hi[nh++]=i;
                // sanity: nh == U-k
                if(nh != U-k){ fprintf(stderr,"inconsistent state\n"); return 1; }
                for(int q=0;q<U;q++){
                    u64 A2;
                    if(q<k){ A2 = A>>1; }
                    else {
                        int off = hi[q-k];           // value = p+1+off
                        if(der && off==0) continue;  // v == p+1 would be a fixed point
                        A2 = (A | (1ULL<<off)) >> 1;
                    }
                    int r2[12]; int L2=L; int j;
                    if(!dec){ for(j=0;j<L;j++) if(r[j]>q) break; }
                    else    { for(j=0;j<L;j++) if(r[j]<=q) break; }
                    if(j==L){ if(L>=Meff) continue; L2=L+1; }
                    for(int i=0;i<L;i++) r2[i] = (r[i]>q)? r[i]-1 : r[i];
                    r2[j]=q;
                    nxt[Key{A2,packR(r2,L2)}] += cnt;
                }
            }
            swap(cur,nxt);
        }
        u128 tot=0; for(auto&kv:cur) tot+=kv.second;
        printf("n=%d ", n); print128(tot); printf("\n"); fflush(stdout);
    }
}
