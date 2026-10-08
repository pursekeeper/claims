import re,sys,collections
n=int(sys.argv[1])
parts=[open(f'big_{n}_{i}.txt').read() for i in (0,1)]
def kv(s):
    d={}
    for m in re.finditer(r'(\w+)=(\d+)',s.split('max_tau shape')[0]): d[m.group(1)]=int(m.group(2))
    return d
A,B=[kv(p) for p in parts]
out={}
for k in ['fixed','free','sum_tau','sum_pm','sum_is','tau_odd','unicyclic']: out[k]=A[k]+B[k]
def mx(k,ck,lo=False):
    a,b=A[k],B[k]
    if a==b: return a, A[ck]+B[ck]
    if (a<b)!=lo: return b,B[ck]
    return a,A[ck]
out['max_tau'],out['max_tau_cnt']=mx('max_tau','max_tau_cnt')
out['max_pm'],out['max_pm_cnt']=mx('max_pm','max_pm_cnt')
out['min_is'],out['min_is_cnt']=mx('min_is','min_is_cnt',lo=True)
out['max_is'],out['max_is_cnt']=mx('max_is','max_is_cnt')
print(n,out)
for q in ['tau','pm','is']:
    h=collections.Counter()
    for i in (0,1):
        for line in open(f'hist_{q}_{n}_s{i}.txt'):
            k,c=map(int,line.split()); h[k]+=c
    with open(f'hist_{q}_{n}_x.txt','w') as f:
        for k in sorted(h): f.write(f'{k} {h[k]}\n')
    print(q,'distinct values',len(h))
