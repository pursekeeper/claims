import pandas as pd, numpy as np
from scipy import stats
W=pd.read_pickle('./wide.pkl')

def table(df,x='GB147',y='GB155',label=''):
    d=df[(df[x].isin(['0','1']))&(df[y].isin(['0','1']))]
    a=((d[x]=='1')&(d[y]=='1')).sum(); b=((d[x]=='1')&(d[y]=='0')).sum()
    c=((d[x]=='0')&(d[y]=='1')).sum(); dd=((d[x]=='0')&(d[y]=='0')).sum()
    OR=(a*dd)/(b*c) if b*c>0 else np.inf
    se=np.sqrt(1/a+1/b+1/c+1/dd)
    p1=a/(a+b); p0=c/(c+dd); q1=a/(a+c)
    chi=stats.chi2_contingency([[a,b],[c,dd]])[1]
    print(f"{label:35s} n={len(d):4d} [{x}=1: y1={a},y0={b}] [{x}=0: y1={c},y0={dd}] "
          f"P(y|x=1)={p1:.3f} P(y|x=0)={p0:.3f} RD={p1-p0:+.3f} P(x|y=1)={q1:.3f} "
          f"OR={OR:.2f} [{np.exp(np.log(OR)-1.96*se):.2f},{np.exp(np.log(OR)+1.96*se):.2f}] p={chi:.2e}")
    return dict(n=len(d),a=a,b=b,c=c,d=dd,p1=p1,p0=p0,OR=OR)

print("=== 2. Raw 2x2 (drop ? and NA on both) ===")
table(W,label='all rows')
table(W[W.level=='language'],label='level==language only')
print("\nAlso: P(GB155=1) marginal among languages with both coded:")
d=W[(W.GB147.isin(['0','1']))&(W.GB155.isin(['0','1']))]
print(' P(GB155=1)=%.3f  P(GB147=1)=%.3f'%((d.GB155=='1').mean(),(d.GB147=='1').mean()))
print("\n--- missingness pattern: are ? values co-occurring? ---")
print(pd.crosstab(W.GB147.fillna('NA'),W.GB155.fillna('NA')))
print("\n=== 5. GB302 free passive -> GB155 ===")
table(W,x='GB302',label='GB302 vs GB155 (raw)')
table(W[W.GB147=='0'],x='GB302',label='GB302 vs GB155 | GB147=0')
table(W[W.GB147=='1'],x='GB302',label='GB302 vs GB155 | GB147=1')
print("crosstab GB147 x GB302")
print(pd.crosstab(W.GB147.fillna('NA'),W.GB302.fillna('NA')))
# "any passive" vs none
d=W[(W.GB147.isin(['0','1']))&(W.GB302.isin(['0','1']))].copy()
d['ptype']=np.select([(d.GB147=='1')&(d.GB302=='1'),(d.GB147=='1'),(d.GB302=='1')],['both','bound_only','free_only'],'none')
dd=d[d.GB155.isin(['0','1'])]
print(dd.groupby('ptype').GB155.apply(lambda s: f"n={len(s)} P(caus)={(s=='1').mean():.3f}"))
