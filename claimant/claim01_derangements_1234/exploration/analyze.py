from fractions import Fraction
from sympy import Matrix, Rational, symbols, nsimplify
a = [0]+[int(l.split()[1]) for l in open('der1234_21.txt')]  # a[0]=0? define a(0)=1 (empty perm is a derangement) -- report separately
a[0] = 1
A = [1,1,2,6,23,103,513,2761,15767,94359,586590,3763290,24792705,167078577,1148208090,8026793118,56963722223,409687815151,2981863943718,21937062144834,162958355218089,1221225517285209]
print("n, a(n), a(n)/A005802(n), a(n)/a(n-1)")
for n in range(1,22):
    print(n, a[n], "%.6f"%(a[n]/A[n]), "%.5f"%(a[n]/a[n-1]) if a[n-1] else '-')
# guess P-recurrence: sum_{i=0..r} P_i(n) a(n-i) = 0, deg P_i <= d
import itertools
def guess(seq, r, d, start=0):
    # unknowns: coefficients c[i][j] of n^j in P_i, i=0..r, j=0..d
    nunk = (r+1)*(d+1)
    rows = []
    for n in range(start + r, len(seq)):
        row = []
        for i in range(r+1):
            for j in range(d+1):
                row.append(Rational(n)**j * seq[n-i])
        rows.append(row)
    M = Matrix(rows)
    ns = M.nullspace()
    return len(rows), nunk, ns
for r in range(1,5):
    for d in range(0,5):
        neq, nunk, ns = guess(a, r, d, start=1)
        if neq >= nunk + 3 and ns:
            print("recurrence found: order", r, "degree", d, "eqs", neq, "unknowns", nunk, "nullity", len(ns))
            print(ns[0].T)
