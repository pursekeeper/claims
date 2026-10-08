import pandas as pd, numpy as np
from scipy import stats
rng=np.random.default_rng(2026)
W=pd.read_pickle('./wide.pkl')
def prep(W,x='GB147',y='GB155'):
    d=W[(W[x].isin(['0','1']))&(W[y].isin(['0','1']))].copy()
    d['x']=(d[x]=='1').astype(int); d['y']=(d[y]=='1').astype(int)
    d['fam']=d.Family_name.fillna('ISOLATE_'+d.index.to_series())
    # isolates: Family_name may be empty -> each is its own family
    return d
def OR_RD(d):
    a=((d.x==1)&(d.y==1)).sum(); b=((d.x==1)&(d.y==0)).sum(); c=((d.x==0)&(d.y==1)).sum(); dd=((d.x==0)&(d.y==0)).sum()
    OR=((a+.5)*(dd+.5))/((b+.5)*(c+.5)); RD=a/(a+b)-c/(c+dd) if (a+b)>0 and (c+dd)>0 else np.nan
    p=stats.fisher_exact([[a,b],[c,dd]])[1]
    return OR,RD,p

def run(x,y,label):
    d=prep(W,x,y)
    print(f"\n######## {label}: {x} -> {y}  n={len(d)}, families={d.fam.nunique()}")
    print("Family_name empty count:",W.Family_name.isna().sum())
    # 3a. one per family resampling
    ORs=[];RDs=[];ps=[]
    for i in range(1000):
        s=d.iloc[rng.permutation(len(d))].drop_duplicates('fam')
        o,r,p=OR_RD(s); ORs.append(o);RDs.append(r);ps.append(p)
    print(f"One-per-family (1000 draws, n per draw={d.fam.nunique()}): median OR={np.median(ORs):.2f} "
          f"[2.5–97.5%: {np.percentile(ORs,2.5):.2f},{np.percentile(ORs,97.5):.2f}]  median RD={np.median(RDs):+.3f} "
          f"[{np.percentile(RDs,2.5):+.3f},{np.percentile(RDs,97.5):+.3f}]  share p<0.05={np.mean(np.array(ps)<0.05):.3f}")
    # 3b. within-family permutation test: shuffle y within family, statistic = Mantel-Haenszel-like sum over families of (a - E[a])
    def mh_stat(d):
        s=0
        for f,g in d.groupby('fam'):
            n=len(g);
            if n<2: continue
            r1=g.x.sum(); c1=g.y.sum()
            if r1 in (0,n) or c1 in (0,n): continue
            a=((g.x==1)&(g.y==1)).sum(); s+= a - r1*c1/n
        return s
    obs=mh_stat(d)
    # fast version: precompute family index arrays
    d=d.reset_index(drop=True)
    fam_codes,fam_uniq=pd.factorize(d.fam)
    xs=d.x.values; ys=d.y.values
    groups=[np.where(fam_codes==k)[0] for k in range(len(fam_uniq))]
    groups=[g for g in groups if len(g)>=2 and 0<xs[g].sum()<len(g)]
    def perm_y():
        yp=ys.copy()
        for g in groups: yp[g]=yp[rng.permutation(g)]
        return yp
    def mh_stat_fast(yp):
        s=0
        for g in groups:
            n=len(g); c1=yp[g].sum()
            if c1 in (0,n): continue
            r1=xs[g].sum(); s+=((xs[g]==1)&(yp[g]==1)).sum()-r1*c1/n
        return s
    null=[]
    for i in range(1000):
        null.append(mh_stat_fast(perm_y()))
    null=np.array(null)
    print(f"Within-family permutation (2000): obs sum(a-E[a])={obs:.1f}, null mean={null.mean():.1f} sd={null.std():.1f}, "
          f"p(two-sided)={(np.abs(null)>=abs(obs)).mean():.4f}")
    # Mantel-Haenszel common OR across families
    from statsmodels.stats.contingency_tables import StratifiedTable
    tabs=[]
    for f,g in d.groupby('fam'):
        if len(g)<2 or g.x.nunique()<2: continue
        t=np.array([[((g.x==1)&(g.y==1)).sum(),((g.x==1)&(g.y==0)).sum()],[((g.x==0)&(g.y==1)).sum(),((g.x==0)&(g.y==0)).sum()]])
        tabs.append(t)
    st=StratifiedTable(tabs)
    print(f"Mantel-Haenszel pooled within-family OR = {st.oddsratio_pooled:.2f} CI {st.oddsratio_pooled_confint()} ; strata={len(tabs)}; p={st.test_null_odds().pvalue:.2e}")
    # 3c. within-family comparisons
    rows=[]
    for f,g in d.groupby('fam'):
        if g.x.nunique()<2: continue
        p1=g[g.x==1].y.mean(); p0=g[g.x==0].y.mean()
        rows.append(dict(family=f,n=len(g),n_x1=(g.x==1).sum(),n_x0=(g.x==0).sum(),P_y_given_x1=round(p1,2),P_y_given_x0=round(p0,2),diff=round(p1-p0,2)))
    R=pd.DataFrame(rows).sort_values('n',ascending=False)
    pos=(R['diff']>0).sum();neg=(R['diff']<0).sum();tie=(R['diff']==0).sum()
    print(f"Families with both values of {x}: {len(R)}: positive={pos}, negative={neg}, tie={tie}; sign test p={stats.binomtest(pos,pos+neg).pvalue:.4f}")
    big=R[R.n>=10]
    print(f"  among families with n>=10 ({len(big)}): positive={(big['diff']>0).sum()}, negative={(big['diff']<0).sum()}, tie={(big['diff']==0).sum()}")
    pd.set_option('display.width',200)
    print(big.to_string(index=False))
    return d

run('GB147','GB155','bound passive -> bound causative')
run('GB302','GB155','free passive -> bound causative')
