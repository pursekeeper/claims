"""Hard test of the claim:  GB147=1 (morphological passive on the lexical verb) -> GB155=1 (causative by affix/clitic).
Outputs evidence table, exceptions, family/macroarea breakdown, family-controlled tests, GEE with family clusters,
WALS replication (107A passive x 111A causative), specificity vs other valency features."""
import pandas as pd, numpy as np
from scipy import stats
import statsmodels.api as sm, statsmodels.formula.api as smf
from famtest import load, famtest, logor
D='DATA/'
B,fam,mac,nm,L=load()
A,CC='GB147','GB155'
m=B[[A,CC]].dropna().copy(); m['fam']=fam[m.index]; m['mac']=mac[m.index]; m['name']=nm[m.index]
print('N languages coded on both:',len(m))
ct=pd.crosstab(m[A],m[CC]); print(ct)
a1=m[m[A]==1]; a0=m[m[A]==0]
print(f'P(caus|pass)={a1[CC].mean():.3f} (n={len(a1)})   P(caus|no pass)={a0[CC].mean():.3f} (n={len(a0)})   risk diff={a1[CC].mean()-a0[CC].mean():.3f}')
print(f'P(pass|caus)={m[m[CC]==1][A].mean():.3f}   P(pass|no caus)={m[m[CC]==0][A].mean():.3f}')
print(f'logOR={logor(m[A].values,m[CC].values):.3f}; exception cell obs={((m[A]==1)&(m[CC]==0)).sum()} expected under independence={len(a1)*(1-m[CC].mean()):.1f}')
print('\n--- macroarea breakdown: P(caus|pass) vs P(caus|no pass) ---')
for ar,g in m.groupby('mac'):
    g1=g[g[A]==1]; g0=g[g[A]==0]
    print(f'{ar:14s} pass: {int(g1[CC].sum()):4d}/{len(g1):4d} ({g1[CC].mean():.2f})   no-pass: {int(g0[CC].sum()):4d}/{len(g0):4d} ({g0[CC].mean():.2f})')
print('\n--- families ---')
fa=a1.groupby('fam')[CC].agg(['sum','count']); fa['exc']=fa['count']-fa['sum']
print('families with >=1 passive language:',len(fa),'; families where ALL passive languages have causative affix:',(fa.exc==0).sum(),
      '; families with >=1 exception:',(fa.exc>0).sum(),'; families where exceptions are the majority:',(fa.exc>fa['sum']).sum())
print('supporting families across macroareas:',a1[a1[CC]==1].groupby('mac').fam.nunique().to_dict())
print('exceptions by family (exc/pass-langs):'); print(fa[fa.exc>0].sort_values('exc',ascending=False).to_string())
print('\n--- exceptions by name ---')
exc=a1[a1[CC]==0].sort_values(['mac','fam','name'])
for ar,g in exc.groupby('mac'): print(ar+': '+'; '.join(f'{r["name"]} ({r.fam})' for _,r in g.iterrows()))
print('\n--- family-controlled tests ---')
o,wf=famtest(B,fam,mac,nm,A,CC,1,1,ndraw=1000,nperm=2000,verbose=False,seed=7)
for k in ['opf_nfam','opf_logOR','opf_logOR_lo','opf_logOR_hi','opf_rate','opf_rd','opf_fisher_p_median','opf_fisher_p_frac05','perm_mean','perm_sd','perm_z','perm_p','wf_nfam','wf_pos','wf_neg','wf_tie','wf_mean_diff','wf_sign_p']:
    v=o[k]; print(f'  {k}: {v:.3f}' if isinstance(v,float) else f'  {k}: {v}')
print('  within-family contrasts (families with both passive and non-passive languages):'); print(wf.sort_values('n',ascending=False).round(2).to_string(index=False))
print('\n--- GEE logistic, clusters=family, exchangeable correlation; covariates: macroarea, verbal-morphology richness ---')
morph=['GB082','GB083','GB084','GB086','GB107','GB108','GB114','GB115','GB312','GB103','GB104','GB158','GB151','GB149','GB148','GB080','GB079']
d=m.copy(); d['rich']=B.loc[d.index,morph].mean(axis=1); d['famc']=pd.factorize(d.fam)[0]
d=d.rename(columns={A:'passive',CC:'causative'}).dropna(subset=['rich'])
for form in ['causative ~ passive','causative ~ passive + rich','causative ~ passive + rich + C(mac)']:
    g=smf.gee(form,groups='famc',data=d,family=sm.families.Binomial(),cov_struct=sm.cov_struct.Exchangeable()).fit()
    print(f'  {form}: passive coef={g.params["passive"]:.3f} (OR={np.exp(g.params["passive"]):.2f}), 95%CI=[{np.exp(g.conf_int().loc["passive",0]):.2f},{np.exp(g.conf_int().loc["passive",1]):.2f}], p={g.pvalues["passive"]:.2e}, n={int(g.nobs)}')
print('\n--- specificity: other bound valency/verbal features -> causative affix (one-per-family logOR) ---')
for f in ['GB147','GB148','GB114','GB115','GB103','GB104','GB108','GB312','GB083','GB302']:
    o2,_=famtest(B,fam,mac,nm,f,CC,1,1,ndraw=300,nperm=10,verbose=False,seed=3)
    print(f'  {f}: P(caus|{f}=1)={o2["rate"]:.2f} vs {o2["rate_other"]:.2f}; opf logOR={o2["opf_logOR"]:.2f} [{o2["opf_logOR_lo"]:.2f},{o2["opf_logOR_hi"]:.2f}]')
print('\n--- WALS replication: 107A Passive constructions x 111A Nonperiphrastic causative constructions ---')
wv=pd.read_csv(D+'wals/cldf/values.csv',low_memory=False); wl=pd.read_csv(D+'wals/cldf/languages.csv').set_index('ID')
w=wv[wv.Parameter_ID.isin(['107A','111A'])].pivot(index='Language_ID',columns='Parameter_ID',values='Code_ID').dropna()
w['fam']=wl.Family.reindex(w.index); w['mac']=wl.Macroarea.reindex(w.index); w['glot']=wl.Glottocode.reindex(w.index)
wc=pd.read_csv(D+'wals/cldf/codes.csv'); cn=dict(zip(wc.ID,wc.Name))
w['pass']=(w['107A']=='107A-1').astype(int); w['morphcaus']=w['111A'].isin(['111A-2','111A-4']).astype(int)
print('111A codes:',{c:cn[c] for c in sorted(w['111A'].unique())}); print('107A codes:',{c:cn[c] for c in sorted(w['107A'].unique())})
print(pd.crosstab(w['pass'],w['111A'].map(cn)))
print(f'  WALS n={len(w)}: P(morph caus|passive)={w[w["pass"]==1].morphcaus.mean():.3f} (n={int((w["pass"]==1).sum())})  P(morph caus|no passive)={w[w["pass"]==0].morphcaus.mean():.3f} (n={int((w["pass"]==0).sum())}); logOR={logor(w["pass"].values,w.morphcaus.values):.2f}')
rng=np.random.default_rng(0); los=[]
grp=pd.Series(range(len(w))).groupby(w.fam.values).indices
for k in range(1000):
    idx=np.array([rng.choice(ix) for ix in grp.values()]); los.append(logor(w['pass'].values[idx],w.morphcaus.values[idx]))
print(f'  WALS one-per-family (n fam={len(grp)}): logOR mean={np.mean(los):.2f} [{np.percentile(los,2.5):.2f},{np.percentile(los,97.5):.2f}]')
wf2=[]
for fn,ix in grp.items():
    xx=w['pass'].values[ix]; yy=w.morphcaus.values[ix]
    if xx.sum()>0 and (xx==0).sum()>0: wf2.append((fn,yy[xx==1].mean(),yy[xx==0].mean()))
wf2=pd.DataFrame(wf2,columns=['fam','r1','r0']); print('  WALS within-family: pos',(wf2.r1>wf2.r0).sum(),'neg',(wf2.r1<wf2.r0).sum(),'tie',(wf2.r1==wf2.r0).sum())
# overlap of WALS and Grambank samples
ov=w[w.glot.isin(m.index)]; print('  WALS languages also in Grambank sample:',len(ov),'; WALS-only:',len(w)-len(ov))
wo=w[~w.glot.isin(m.index)]
if len(wo)>30: print(f'  WALS-only languages: P(morph caus|passive)={wo[wo["pass"]==1].morphcaus.mean():.2f} (n={int((wo["pass"]==1).sum())}) vs {wo[wo["pass"]==0].morphcaus.mean():.2f} (n={int((wo["pass"]==0).sum())})')
# agreement between codings for overlapping languages
ov=ov.set_index('glot'); both=ov.join(m[[A,CC]],how='inner')
print('  coding agreement on overlap: passive',(both['pass']==both[A]).mean().round(2),' causative',(both.morphcaus==both[CC]).mean().round(2))
