#include <stdio.h>
#include "ham.h"
static void clear(int n){ ham_set_n(n); for(int i=0;i<n;i++) HADJ[i]=0; }
static void e(int a,int b){ HADJ[a]|=1ull<<b; HADJ[b]|=1ull<<a; }
int main(void){
    /* K4: 3 Hamiltonian cycles, path yes */
    clear(4); for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)e(i,j);
    printf("K4: path=%d cycles=%lld (expect 1, 3)\n", hampath(), hamcycle_count());
    /* cube Q3: 6 Hamiltonian cycles */
    clear(8); for(int i=0;i<8;i++)for(int b=0;b<3;b++){int j=i^(1<<b); if(i<j)e(i,j);}
    printf("Q3: path=%d cycles=%lld (expect 1, 6)\n", hampath(), hamcycle_count());
    /* Petersen: no Hamiltonian cycle, has Hamiltonian path */
    clear(10); for(int i=0;i<5;i++){e(i,(i+1)%5); e(i,i+5); e(i+5,(i+2)%5+5);}
    printf("Petersen: path=%d cycles=%lld (expect 1, 0)\n", hampath(), hamcycle_count());
    /* wheel W6: 6 Hamiltonian cycles */
    clear(7); for(int i=0;i<6;i++){e(i,(i+1)%6); e(i,6);}
    printf("W6: path=%d cycles=%lld (expect 1, 6)\n", hampath(), hamcycle_count());
    /* star K_{1,3}: no path */
    clear(4); e(0,1);e(0,2);e(0,3);
    printf("K13: path=%d cycles=%lld (expect 0, 0)\n", hampath(), hamcycle_count());
    /* path P5 : path yes, no cycle */
    clear(5); e(0,1);e(1,2);e(2,3);e(3,4);
    printf("P5: path=%d cycles=%lld (expect 1, 0)\n", hampath(), hamcycle_count());
    /* two triangles sharing a vertex (bowtie): no ham path? bowtie: 0-1-2-0, 2-3-4-2: path 0-1-2-3-4 exists; cycles 0 */
    clear(5); e(0,1);e(1,2);e(2,0);e(2,3);e(3,4);e(4,2);
    printf("bowtie: path=%d cycles=%lld (expect 1, 0)\n", hampath(), hamcycle_count());
    /* C6 with one chord (theta graph): C6 plus edge 0-3 : ham cycles = 1 */
    clear(6); for(int i=0;i<6;i++)e(i,(i+1)%6); e(0,3);
    printf("C6+chord: path=%d cycles=%lld (expect 1, 1)\n", hampath(), hamcycle_count());
    /* K3,3: 3-regular bipartite, 6 Hamiltonian cycles */
    clear(6); for(int i=0;i<3;i++)for(int j=3;j<6;j++)e(i,j);
    printf("K33: path=%d cycles=%lld (expect 1, 6)\n", hampath(), hamcycle_count());
    return 0;
}
