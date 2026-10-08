# Claims 4 and 5: A395587 a(8..10) and A396786 a(9..11)

(The same three programs serve both claims; the folder for claim 5 is a copy.)

## Exploration (two methods, one session; no separate blind reviewer)
- `exploration/crt.py` — for each of the 2^(n-1) sign choices, combine the residue conditions by CRT and step through the progression to the
  first prime; take the minimum; finally re-check the winner against the literal definition `pow(p, q**K, q**5) in {1, q**5-1}`.
  Requires sympy and gmpy2. Run: `python3 crt.py K NMAX` with K = 2 (A395587) or 3 (A396786). ~5-10 s. Reproduces all listed OEIS terms.
  The residue reduction (p^(q^K) = +-1 mod q^5 <=> p = +-1 mod q^(5-K) for odd q; q = 2 handled separately) is asserted against brute force for q <= 13 inside the script.
- `exploration/verify.c` — independent exhaustive check: CRT only over the first J odd primes, then enumerate every integer <= the claimed value in those
  classes, filter arithmetically, print all survivors. `gcc -O2 -o verify verify.c; ./verify K n J BOUND` (BOUND = claimed a(n)). `outputs/surv.txt` — survivor list for A395587 n = 8.
- `exploration/cert.py` — tests survivors with sympy `isprime`, confirms the claimed value is the unique smallest prime survivor, and prints a Lucas
  primality certificate (factorisation of p-1 with a witness). `python3 cert.py K n J BOUND < surv.txt`.

## Statement lines <-> outputs
- A395587 a(8), a(9), a(10) and A396786 a(9), a(10), a(11): printed by `crt.py`; a(8) of A395587 and a(9) of A396786 additionally by `verify.c` + `cert.py`.
