# Claimant code for the seventeen seed claims

Published 2026-10-08, after every verdict (the last on 2026-09-19) and the pilot's close (2026-10-07), as the protocol promised:
"the claimant's code after the verdicts". One folder per claim, exactly as supplied on 2026-09-16; the sha256 commitment printed
on each claim page and in [`commitments.txt`](commitments.txt) recomputes from the folder with [`verify-commitments.sh`](verify-commitments.sh)
(all seventeen checked before publishing; claims 4 and 5 share one folder and one hash). Reviewers never saw any of this: every accepted
re-derivation under [`../runs/`](../runs/) was written from the claim statement alone.

The bundle's own description follows, unchanged.

---

# Private bundle for the blind re-derivation pilot

One folder per claim in seed-claims.md (claim numbers match). Each folder has `exploration/` (the code that first produced the numbers),
`blind-review/` (independent re-derivation code, where one was run), `outputs/` (the runs the numbers were read from) and a README mapping
statement lines to files. Provenance: supplied by the pilot's funder. Claims 4, 5, 9, 11, 12 and 15 had no separate blind re-derivation in the original
run (single implementation, or two methods in one session); claim 8 was only partly re-derived. All others were re-derived from the claim alone by an
independent implementation before inclusion here.
All programs are plain C/C++ (gcc/g++ -O2 or -O3) or Python 3 (pandas, numpy, sympy, gmpy2, statsmodels where noted). No file in this bundle
contains machine paths; data directories are referred to as `DATA/` or `./`.
