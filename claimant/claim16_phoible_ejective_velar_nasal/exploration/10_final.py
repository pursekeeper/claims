# Final evidence for: ejective consonants vs phonemic velar nasal /ŋ/ (negative association)
exec(open('DATA/sounds/00_load.py').read())
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
from statsmodels.stats.contingency_tables import StratifiedTable
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
def build(Pdf, allinv=None):
    C=Pdf.SegmentClass=='consonant'
    S=lambda m: set(Pdf.InventoryID[m])
    ids=sorted(set(Pdf.InventoryID))
    Z=pd.DataFrame(index=ids)
    Z['ej']=Z.index.isin(S(C&(Pdf.raisedLarynxEjective=='+')))
    Z['ng']=Z.index.isin(S(Pdf.Phoneme.str.match(r'^ŋ$')))
    Z['ng_broad']=Z.index.isin(S(Pdf.Phoneme.str.match(r'^ŋ[^m]*$')&(Pdf.nasal=='+')&(Pdf.labial!='+')))
    meta=Pdf.groupby('InventoryID').agg(LanguageName=('LanguageName','first'),Family_name=('Family_name','first'),Macroarea=('Macroarea','first'),Source=('Source','first'))
    return Z.join(meta)
def summarize(Z,label,y='ng'):
    ct=np.array([[(Z.ej&Z[y]).sum(),(Z.ej&~Z[y]).sum()],[(~Z.ej&Z[y]).sum(),(~Z.ej&~Z[y]).sum()]])
    OR,p=fisher_exact(ct)
    K=Z[Z.Family_name!='UNKNOWN']; tabs=[]
    for g,d in K.groupby('Family_name'):
        t=np.array([[ (d.ej&d[y]).sum(), (d.ej&~d[y]).sum()],[(~d.ej&d[y]).sum(),(~d.ej&~d[y]).sum()]])
        if t[0].sum()>0 and t[1].sum()>0: tabs.append(t)
    mh=StratifiedTable(tabs) if len(tabs)>1 else None
    Ka=Z[Z.Macroarea!='UNKNOWN']; taba=[]
    for g,d in Ka.groupby('Macroarea'):
        t=np.array([[ (d.ej&d[y]).sum(), (d.ej&~d[y]).sum()],[(~d.ej&d[y]).sum(),(~d.ej&~d[y]).sum()]])
        if t[0].sum()>0 and t[1].sum()>0: taba.append(t)
    mha=StratifiedTable(taba) if len(taba)>1 else None
    ej=Z[Z.ej]
    print(f"{label:38s} N={len(Z):4d} ej={len(ej):3d} P(ŋ|ej)={Z[y][Z.ej].mean():.2f} P(ŋ|~ej)={Z[y][~Z.ej].mean():.2f} OR={OR:.2f} p={p:.1e} | MH-fam OR={mh.oddsratio_pooled if mh else float('nan'):.2f} p={mh.test_null_odds().pvalue if mh else float('nan'):.1e} ({len(tabs)} strata) | MH-area OR={mha.oddsratio_pooled if mha else float('nan'):.2f} | ej fams={ej.Family_name[ej.Family_name!='UNKNOWN'].nunique()} areas={ej.Macroarea[ej.Macroarea!='UNKNOWN'].nunique()}")
print("=== MAIN (one inventory per glottocode, marginal segments excluded) ===")
Z0=build(P[P.Marginal!=True]); summarize(Z0,'main')
summarize(Z0,'main, ŋ broad (ŋʷ ŋː ŋ̥ etc.)','ng_broad')
print("\n=== ROBUSTNESS ===")
summarize(build(P),'marginal segments included')
# all inventories (no dedup) 
Pall=ph.merge(P[['InventoryID']].drop_duplicates(),how='left',indicator=True)
Pall=ph.merge(INV[['Glottocode','Family_name','Macroarea']].drop_duplicates('Glottocode'),on='Glottocode',how='left')
Pall['Family_name']=Pall.Family_name.fillna('UNKNOWN'); Pall['Macroarea']=Pall.Macroarea.fillna('UNKNOWN')
summarize(build(Pall[Pall.Marginal!=True]),'all 3020 inventories (no dedup)')
for src in ['ph','upsid','spa','ea','aa','saphon']:
    summarize(build(Pall[(Pall.Marginal!=True)&(Pall.Source==src)]),f'source={src} only (no dedup)')
# one language per family (known families), 300 draws
K=Z0[Z0.Family_name!='UNKNOWN']; rng=np.random.default_rng(1); res=[]
codes,uniq=pd.factorize(K.Family_name); groups=[np.where(codes==i)[0] for i in range(len(uniq))]
ejv=K.ej.values; ngv=K.ng.values
for _ in range(300):
    idx=np.array([g[rng.integers(len(g))] for g in groups]); e=ejv[idx]; n=ngv[idx]
    t=np.array([[(e&n).sum(),(e&~n).sum()],[(~e&n).sum(),(~e&~n).sum()]]); o,p=fisher_exact(t)
    res.append((o,p,n[e].mean(),n[~e].mean(),e.sum()))
R=pd.DataFrame(res,columns=['OR','p','Png_ej','Png_noej','n_ej'])
print(f"one language per family ({len(uniq)} families), 300 draws: median OR={R.OR.median():.2f}, p<0.05 in {(R.p<0.05).mean():.2f}, P(ŋ|ej) median={R.Png_ej.median():.2f}, P(ŋ|~ej)={R.Png_noej.median():.2f}, ej langs per draw ~{R.n_ej.median():.0f}")
print("\n=== per macroarea (main) ===")
for a,d in Z0.groupby('Macroarea'):
    print(f"{a:14s} N={len(d):4d} ej={d.ej.sum():3d}  P(ŋ|ej)={d.ng[d.ej].mean() if d.ej.sum() else float('nan'):.2f}  P(ŋ|~ej)={d.ng[~d.ej].mean():.2f}")
print("\n=== families containing ejective languages: ŋ rate among their ejective vs non-ejective members ===")
rows=[]
for fam,d in Z0[Z0.Family_name!='UNKNOWN'].groupby('Family_name'):
    if d.ej.sum()>0: rows.append((fam,len(d),d.ej.sum(),d.ng[d.ej].sum(),(d.ng[~d.ej].sum() if (~d.ej).sum() else np.nan),(~d.ej).sum()))
F=pd.DataFrame(rows,columns=['family','n','n_ej','n_ej_with_ŋ','n_nonej_with_ŋ','n_nonej']).sort_values('n_ej',ascending=False)
print(F.to_string(index=False))
print("\n=== the 'exceptions': ejective languages that DO have /ŋ/ ===")
E=Z0[Z0.ej&Z0.ng][['LanguageName','Family_name','Macroarea','Source']].sort_values(['Macroarea','Family_name'])
print(E.to_string())
print("\n=== ejective languages lacking ŋ, unknown family: ===")
print(Z0[Z0.ej&(Z0.Family_name=='UNKNOWN')][['LanguageName','Source','ng']].to_string())
