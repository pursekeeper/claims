import pandas as pd, numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import StratifiedTable
D='DATA/wals/cldf/'
v=pd.read_csv(D+'values.csv',dtype=str); l=pd.read_csv(D+'languages.csv',dtype=str)
w=v[v.Parameter_ID.isin(['107A','111A'])].pivot(index='Language_ID',columns='Parameter_ID',values='Value')
w=w.join(l.set_index('ID')[['Name','Family','Genus','Macroarea','Glottocode']])
w['pass']=w['107A'].map({'1':1,'2':0}); w['mcaus']=w['111A'].map({'1':0,'2':1,'3':0,'4':1})
rng=np.random.default_rng(1)
def rep(d,x,y,label,grp='Family'):
    d=d.dropna(subset=[x,y]).copy()
    a=((d[x]==1)&(d[y]==1)).sum();b=((d[x]==1)&(d[y]==0)).sum();c=((d[x]==0)&(d[y]==1)).sum();dd=((d[x]==0)&(d[y]==0)).sum()
    OR=a*dd/(b*c); se=np.sqrt(1/a+1/b+1/c+1/dd)
    print(f"{label}: n={len(d)} [{a},{b};{c},{dd}] P(y|x=1)={a/(a+b):.3f} P(y|x=0)={c/(c+dd):.3f} OR={OR:.2f} [{np.exp(np.log(OR)-1.96*se):.2f},{np.exp(np.log(OR)+1.96*se):.2f}] fisher p={stats.fisher_exact([[a,b],[c,dd]])[1]:.1e}")
    d['g']=d[grp].fillna('iso_'+d.index.to_series())
    ORs=[];ps=[]
    for i in range(1000):
        s=d.iloc[rng.permutation(len(d))].drop_duplicates('g')
        a=((s[x]==1)&(s[y]==1)).sum();b=((s[x]==1)&(s[y]==0)).sum();c=((s[x]==0)&(s[y]==1)).sum();dd=((s[x]==0)&(s[y]==0)).sum()
        ORs.append((a+.5)*(dd+.5)/((b+.5)*(c+.5))); ps.append(stats.fisher_exact([[a,b],[c,dd]])[1])
    tabs=[np.array([[((g[x]==1)&(g[y]==1)).sum(),((g[x]==1)&(g[y]==0)).sum()],[((g[x]==0)&(g[y]==1)).sum(),((g[x]==0)&(g[y]==0)).sum()]]) for _,g in d.groupby('g') if g[x].nunique()>1]
    st=StratifiedTable(tabs)
    print(f"   one-per-{grp} (n={d.g.nunique()}): median OR={np.median(ORs):.2f} [{np.percentile(ORs,2.5):.2f},{np.percentile(ORs,97.5):.2f}] share p<.05={np.mean(np.array(ps)<.05):.2f};  MH within-{grp} OR={st.oddsratio_pooled:.2f} CI={tuple(np.round(st.oddsratio_pooled_confint(),2))} p={st.test_null_odds().pvalue:.1e}")
print("=== WALS-only: 107A passive (any type) x 111A morphological causative ===")
rep(w,'pass','mcaus','WALS 107A->111A (family)')
rep(w,'pass','mcaus','WALS 107A->111A (genus)',grp='Genus')
# cross-database via glottocode
G=pd.read_pickle('./wide.pkl')
G=G.reset_index().drop_duplicates('Glottocode').set_index('Glottocode')
wg=w.dropna(subset=['Glottocode']).drop_duplicates('Glottocode').set_index('Glottocode')
X=wg.join(G[['GB147','GB155','GB302','Family_name']],how='inner')
for k in ['GB147','GB155','GB302']: X[k+'b']=X[k].map({'0':0,'1':1})
print("\n=== Cross-database (matched by glottocode), n matched:",len(X))
print("Agreement check: WALS 111A morph-causative vs GB155:"); print(pd.crosstab(X.mcaus,X.GB155b))
print("WALS 107A any-passive vs GB147 bound passive:"); print(pd.crosstab(X['pass'],X.GB147b))
print("WALS 107A any-passive vs (GB147 or GB302):"); X['anyp']=((X.GB147b==1)|(X.GB302b==1)).astype(float); X.loc[X.GB147b.isna()&X.GB302b.isna(),'anyp']=np.nan; print(pd.crosstab(X['pass'],X.anyp))
rep(X,'GB147b','mcaus','GB147 bound passive -> WALS 111A morph causative')
rep(X,'pass','GB155b','WALS 107A any passive -> GB155')
rep(X,'GB302b','mcaus','GB302 free passive -> WALS 111A morph causative')
# WALS: within 107A=present, does GB302 (free) vs GB147 (bound) matter for 111A?
s=X[(X['pass']==1)]
print("\nAmong WALS-passive-present languages: P(WALS morph caus | GB147=1)=%.2f (n=%d), | GB147=0 =%.2f (n=%d)"%(s[s.GB147b==1].mcaus.mean(),s[s.GB147b==1].mcaus.notna().sum(),s[s.GB147b==0].mcaus.mean(),s[s.GB147b==0].mcaus.notna().sum()))
