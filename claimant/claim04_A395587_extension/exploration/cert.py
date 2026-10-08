import sys, subprocess
from sympy import isprime, factorint
K,n,J,B = sys.argv[1:5]
out = subprocess.run(['./verify',K,n,J,B],capture_output=True,text=True)
xs = sorted(int(l) for l in out.stdout.split())
print(out.stderr.strip())
pr = [x for x in xs if isprime(x)]
print('prime survivors <= B:', pr)
p = pr[0]; assert p == int(B)
f = factorint(p-1); assert all(isprime(q) for q in f)
for a in range(2,500):
    if pow(a,p-1,p)==1 and all(pow(a,(p-1)//q,p)!=1 for q in f):
        print('n=%s: %d minimal; Lucas witness a=%d, p-1=%s => PROVEN prime'%(n,p,a,f)); break
