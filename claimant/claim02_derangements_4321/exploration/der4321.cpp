// Count permutations of [n] that avoid 1234 (LIS <= 3) and optionally have no fixed points.
// Build the permutation left to right. State = (set of used values, pile tops of patience sorting).
// A permutation avoids 1234 iff patience sorting (greedy LIS piles) never needs a 4th pile.
// Level-by-level DP: level k holds all states with k values placed, with multiplicity.
// usage: ./der1234 N MODE   MODE=1: derangements avoiding 1234; MODE=0: all 1234-avoiders (validation, A005802);
//        MODE=2: derangements (no pattern restriction, validation A000166)
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <unordered_map>
#include <vector>
using namespace std;
typedef unsigned long long u64;
typedef unsigned __int128 u128;

int main(int argc, char** argv) {
    int N = atoi(argv[1]);
    int mode = atoi(argv[2]);
    int maxpiles = (mode == 2) ? 1000 : 3; // mode 3: avoid 4321 (decreasing piles)
    for (int n = 1; n <= N; n++) {
        // key: used (n bits) | t1<<32 | t2<<40 | t3<<48  (tops 1..n, 0 = empty pile)
        unordered_map<u64, u64> cur, nxt;
        cur[0] = 1;
        for (int k = 0; k < n; k++) {
            nxt.clear();
            nxt.reserve(cur.size() * 4 + 16);
            int pos = k + 1; // 1-indexed position being filled
            for (auto& kv : cur) {
                u64 key = kv.first; u64 cnt = kv.second;
                u64 used = key & 0xFFFFFFFFULL;
                int t[3] = { (int)((key >> 32) & 0xFF), (int)((key >> 40) & 0xFF), (int)((key >> 48) & 0xFF) };
                int np = 0; while (np < 3 && t[np]) np++;
                for (int v = 1; v <= n; v++) {
                    if (used & (1ULL << (v - 1))) continue;
                    if (mode != 0 && v == pos) continue; // fixed point forbidden
                    int nt[3] = { t[0], t[1], t[2] };
                    int npiles = np;
                    if (mode == 2) {
                        // no pattern restriction: don't track piles
                        nt[0] = nt[1] = nt[2] = 0;
                    } else {
                        // place v on leftmost pile whose top > v (tops are increasing left to right)
                        int j = 0;
                        while (j < np && ((mode==3) ? (t[j] > v) : (t[j] < v))) j++;
                        if (j == np) { if (np == maxpiles) continue; npiles = np + 1; }
                        nt[j] = v;
                    }
                    u64 nkey = (used | (1ULL << (v - 1))) | ((u64)nt[0] << 32) | ((u64)nt[1] << 40) | ((u64)nt[2] << 48);
                    nxt[nkey] += cnt;
                }
            }
            cur.swap(nxt);
        }
        u128 total = 0;
        for (auto& kv : cur) total += kv.second;
        // print u128
        char buf[64]; int p = 63; buf[p] = 0;
        if (total == 0) buf[--p] = '0';
        while (total > 0) { buf[--p] = '0' + (int)(total % 10); total /= 10; }
        printf("%d %s\n", n, buf + p);
        fflush(stdout);
    }
}
