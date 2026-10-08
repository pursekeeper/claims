import sys, time
from itertools import product
from sympy import primerange, isprime
from gmpy2 import is_prime, mpz
from sympy.ntheory.modular import crt

K = int(sys.argv[1])        # exponent power: 2 for A395587, 3 for A396786
NMAX = int(sys.argv[2])

def literal_ok(p, q):
    m = q**5
    r = pow(p, q**K, m)
    return r == 1 or r == m - 1

def residues(q):
    """Set of residues r mod q^5 (as (modulus, list)) satisfying r^(q^K) = +-1 mod q^5.
    Brute force for small q, theory (cyclic group) for larger q, cross-checked."""
    m = q**5
    if q == 2:
        return m, [r for r in range(m) if literal_ok(r, q)]
    # theory: r^(q^K) = 1 iff r = 1 mod q^(5-K); r^(q^K) = -1 iff r = -1 mod q^(5-K)
    mod = q**(5-K)
    theo = sorted({r for r in range(m) if r % mod in (1, mod-1)})
    if q <= 13:
        brute = [r for r in range(m) if literal_ok(r, q)]
        assert brute == theo, q
    return mod, [1, mod-1]

def a(n):
    ps = list(primerange(2, 200))[:n]
    conds = []
    for q in ps:
        mod, rs = residues(q)
        conds.append((mod, rs))
    mods = [c[0] for c in conds]
    M = 1
    for m in mods: M *= m
    best = None
    for combo in product(*[c[1] for c in conds]):
        r, _ = crt(mods, list(combo))
        r = int(r)
        if r == 0: r = M
        x = r
        while True:
            if best is not None and x >= best: break
            if x > 1 and is_prime(mpz(x), 30):
                best = x
                break
            x += M
    # final literal verification
    assert isprime(best) and all(literal_ok(best, q) for q in ps)
    return best

for n in range(1, NMAX+1):
    t = time.time()
    v = a(n)
    print(n, v, "%.1fs" % (time.time()-t), flush=True)
