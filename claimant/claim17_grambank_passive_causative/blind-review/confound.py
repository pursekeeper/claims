import pandas as pd, numpy as np
import statsmodels.formula.api as smf, statsmodels.api as sm
from scipy import stats
import warnings; warnings.filterwarnings('ignore')
W=pd.read_pickle('./wide.pkl')
p=pd.read_pickle('./params.pkl').set_index('ID')
# Index A: general bound verbal morphology (no valency-changing features, no GB147/155/302)
IDX=['GB079','GB080','GB081','GB082','GB083','GB084','GB086','GB089','GB090','GB091','GB092','GB093','GB094',
     'GB107','GB108','GB149','GB151','GB152','GB177','GB286','GB312']
VAL={'GB114':'reflexive','GB115':'reciprocal','GB103':'ben_applic','GB104':'inst_applic','GB148':'antipassive','GB113':'transitivizer'}
def bin(s): return s.map({'0':0,'1':1})
M=W[IDX].apply(bin)
W['ncoded']=M.notna().sum(1)
W['morph']=M.mean(1)
W=W[W.ncoded>=12].copy()
for k in ['GB147','GB155','GB302']+list(VAL): W[k+'b']=bin(W[k])
W['fam']=W.Family_name.fillna('ISOLATE_'+W.index.to_series())
W['tense']=W[['GB082','GB083','GB084']].apply(bin).max(1)
d=W.dropna(subset=['GB147b','GB155b']).copy()
print("n with GB147,GB155 and >=12 index features coded:",len(d))
print("corr(morph, GB147)=%.3f corr(morph,GB155)=%.3f"%(d.morph.corr(d.GB147b),d.morph.corr(d.GB155b)))
print("\n=== Stratify by quartile of bound-verbal-morphology index ===")
d['q']=pd.qcut(d.morph,4,labels=['Q1 low','Q2','Q3','Q4 high'])
rows=[]
for q,g in d.groupby('q',observed=True):
    a=((g.GB147b==1)&(g.GB155b==1)).sum();b=((g.GB147b==1)&(g.GB155b==0)).sum();c=((g.GB147b==0)&(g.GB155b==1)).sum();dd=((g.GB147b==0)&(g.GB155b==0)).sum()
    OR=(a*dd)/max(b*c,0.5)
    rows.append(dict(quartile=q,n=len(g),morph_range=f"{g.morph.min():.2f}-{g.morph.max():.2f}",n_pass=a+b,P_caus_pass=round(a/(a+b),3),P_caus_nopass=round(c/(c+dd),3),RD=round(a/(a+b)-c/(c+dd),3),OR=round(OR,2),fisher_p=stats.fisher_exact([[a,b],[c,dd]])[1]))
print(pd.DataFrame(rows).to_string(index=False))
from statsmodels.stats.contingency_tables import StratifiedTable
tabs=[np.array([[((g.GB147b==1)&(g.GB155b==1)).sum(),((g.GB147b==1)&(g.GB155b==0)).sum()],[((g.GB147b==0)&(g.GB155b==1)).sum(),((g.GB147b==0)&(g.GB155b==0)).sum()]]) for q,g in d.groupby('q',observed=True)]
st=StratifiedTable(tabs); print("MH OR across quartiles: %.2f CI %s"%(st.oddsratio_pooled,tuple(np.round(st.oddsratio_pooled_confint(),2))))
# decile too
d['dec']=pd.qcut(d.morph,10,labels=False,duplicates='drop')
tabs=[np.array([[((g.GB147b==1)&(g.GB155b==1)).sum(),((g.GB147b==1)&(g.GB155b==0)).sum()],[((g.GB147b==0)&(g.GB155b==1)).sum(),((g.GB147b==0)&(g.GB155b==0)).sum()]]) for q,g in d.groupby('dec')]
st=StratifiedTable(tabs); print("MH OR across deciles: %.2f CI %s"%(st.oddsratio_pooled,tuple(np.round(st.oddsratio_pooled_confint(),2))))

print("\n=== Logistic models, family-clustered SEs ===")
import re
def fit(formula,data,label):
    cols=[c for c in re.findall(r'[A-Za-z_][A-Za-z0-9_]*',formula) if c in data.columns]
    data=data.dropna(subset=cols)
    m=smf.logit(formula,data).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pd.factorize(data.fam)[0]})
    ci=np.exp(m.conf_int())
    out=[]
    for k in m.params.index:
        if k.startswith('Intercept') or k.startswith('C(Macroarea') : continue
        out.append(f"{k}: OR={np.exp(m.params[k]):.2f} [{ci.loc[k,0]:.2f},{ci.loc[k,1]:.2f}] p={m.pvalues[k]:.1e}")
    print(f"--- {label} (n={int(m.nobs)})\n   "+"\n   ".join(out))
    return m
fit('GB155b ~ GB147b',d,'M0 passive only')
fit('GB155b ~ GB147b + morph',d,'M1 + morph index')
fit('GB155b ~ GB147b + morph + C(Macroarea)',d,'M2 + morph + macroarea')
fit('GB155b ~ GB147b + morph + I(morph**2) + C(Macroarea)',d,'M3 + morph^2')
fit('GB155b ~ GB147b + C(q) + C(Macroarea)',d,'M4 + morph quartile dummies')
# Add valency-morphology features as covariates (subset with them coded)
dv=d.dropna(subset=['GB114b','GB115b','GB103b','GB148b']).copy()
fit('GB155b ~ GB147b + morph + C(Macroarea) + GB114b + GB115b + GB103b + GB148b',dv,'M5 + reflexive,reciprocal,ben.applic,antipassive')
dv2=dv.dropna(subset=['GB113b'])
fit('GB155b ~ GB147b + morph + C(Macroarea) + GB114b + GB115b + GB103b + GB148b + GB113b',dv2,'M6 + also GB113 transitivizer (overlaps causative)')
# conditional logit / family fixed effects on families with variation: use within-family dummies for families n>=5
print("\n--- M7 family fixed effects (families with n>=5 get own dummy, rest pooled) + morph")
d['famFE']=np.where(d.groupby('fam').fam.transform('size')>=5,d.fam,'other')
m=smf.logit('GB155b ~ GB147b + morph + C(famFE)',d).fit(disp=0,method='bfgs',maxiter=500)
print("   GB147b OR=%.2f CI %s p=%.1e"%(np.exp(m.params['GB147b']),tuple(np.round(np.exp(m.conf_int().loc['GB147b']),2)),m.pvalues['GB147b']))
print("   morph  OR=%.2f p=%.1e"%(np.exp(m.params['morph']),m.pvalues['morph']))

print("\n=== Is passive special? Each bound verbal feature as sole predictor of GB155, and jointly ===")
preds={'GB147b':'bound passive','GB114b':'bound reflexive','GB115b':'bound reciprocal','GB103b':'benefactive applicative','GB104b':'instrumental applicative','GB148b':'bound antipassive','GB113b':'transitivizer affix','tense':'any bound tense (82/83/84)','GB302b':'FREE passive'}
rows=[]
for k,lab in preds.items():
    g=W.dropna(subset=[k,'GB155b'])
    p1=g[g[k]==1].GB155b.mean();p0=g[g[k]==0].GB155b.mean()
    a=((g[k]==1)&(g.GB155b==1)).sum();b=((g[k]==1)&(g.GB155b==0)).sum();c=((g[k]==0)&(g.GB155b==1)).sum();dd=((g[k]==0)&(g.GB155b==0)).sum()
    OR=(a*dd)/(b*c)
    gg=g.dropna(subset=['morph','Macroarea'])
    m=smf.logit(f'GB155b ~ {k} + morph + C(Macroarea)',gg).fit(disp=0,cov_type='cluster',cov_kwds={'groups':pd.factorize(gg.fam)[0]})
    rows.append(dict(feature=lab,n=len(g),P_x1=round((g[k]==1).mean(),2),P_caus_x1=round(p1,3),P_caus_x0=round(p0,3),RD=round(p1-p0,3),rawOR=round(OR,2),adjOR_morph_area=round(np.exp(m.params[k]),2),adj_p=f"{m.pvalues[k]:.0e}"))
print(pd.DataFrame(rows).to_string(index=False))
d.to_pickle('./d.pkl'); W.to_pickle('./W2.pkl')
