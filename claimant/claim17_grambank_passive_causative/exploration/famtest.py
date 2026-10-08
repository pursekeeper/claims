"""Family-controlled tests for a feature pair (A=av -> B=bv).
1. one-language-per-family resampling (Fisher exact + logOR), 1000 draws
2. within-family permutation: shuffle B within each family, 2000 times; statistic = logOR
3. within-family contrast: among families with both A=0 and A=1 languages, compare P(B|A)
4. macroarea breakdown of the four cells.
"""
import pandas as pd, numpy as np, sys
from scipy import stats
D='DATA/'
def load():
    v=pd.read_csv(D+'grambank/cldf/values.csv',low_memory=False)
    L=pd.read_csv(D+'grambank/cldf/languages.csv').set_index('ID')
    v=v[v.Value!='?']
    W=v.pivot(index='Language_ID',columns='Parameter_ID',values='Value')
    multi=['GB024','GB025','GB065','GB130','GB193','GB203']
    B=W[[c for c in W.columns if c not in multi]].apply(pd.to_numeric)
    for m in multi:
        s=pd.to_numeric(W[m])
        B[m+'_a']=np.where(s.isna(),np.nan,((s==1)|(s==3)).astype(float))
        B[m+'_b']=np.where(s.isna(),np.nan,((s==2)|(s==3)).astype(float))
    fam=L.Family_name.reindex(B.index).fillna(pd.Series(B.index,index=B.index))
    mac=L.Macroarea.reindex(B.index); nm=L.Name.reindex(B.index)
    return B,fam,mac,nm,L
def logor(x,y):
    a=((x==1)&(y==1)).sum();b=((x==1)&(y==0)).sum();c=((x==0)&(y==1)).sum();d=((x==0)&(y==0)).sum()
    return np.log((a+.5)*(d+.5)/((b+.5)*(c+.5)))
def famtest(B,fam,mac,nm,A,Bf,av=1,bv=0,ndraw=1000,nperm=2000,verbose=True,seed=0):
    rng=np.random.default_rng(seed)
    m=B[[A,Bf]].dropna(); x=(m[A]==av).astype(int).values; y=(m[Bf]==bv).astype(int).values
    f=fam[m.index].values; mc=mac[m.index].values
    n=len(m); n1=x.sum(); supp=((x==1)&(y==1)).sum(); exc=((x==1)&(y==0)).sum()
    rate=supp/n1; other=((x==0)&(y==1)).sum()/(x==0).sum()
    lo=logor(x,y)
    out=dict(A=A,av=av,B=Bf,bv=bv,n=n,nA=n1,supp=supp,exc=exc,rate=rate,rate_other=other,rd=rate-other,logOR=lo,
             fam_A=len(set(f[x==1])),fam_supp=len(set(f[(x==1)&(y==1)])),fam_exc=len(set(f[(x==1)&(y==0)])),
             mac_supp=len(set(mc[(x==1)&(y==1)])),mac_exc=len(set(mc[(x==1)&(y==0)])))
    # 1. one per family
    groups=pd.Series(range(n)).groupby(f).indices
    los=[];ps=[];rates=[];rds=[]
    for k in range(ndraw):
        idx=np.array([rng.choice(ix) for ix in groups.values()])
        xx=x[idx];yy=y[idx]
        if xx.sum()<5: continue
        los.append(logor(xx,yy))
        t=[[((xx==1)&(yy==1)).sum(),((xx==1)&(yy==0)).sum()],[((xx==0)&(yy==1)).sum(),((xx==0)&(yy==0)).sum()]]
        ps.append(stats.fisher_exact(t,alternative='greater')[1])
        rates.append(t[0][0]/(t[0][0]+t[0][1])); rds.append(t[0][0]/(t[0][0]+t[0][1])-t[1][0]/(t[1][0]+t[1][1]))
    out.update(opf_logOR=np.mean(los),opf_logOR_lo=np.percentile(los,2.5),opf_logOR_hi=np.percentile(los,97.5),
               opf_rate=np.mean(rates),opf_rd=np.mean(rds),opf_fisher_p_median=np.median(ps),opf_fisher_p_frac05=np.mean(np.array(ps)<0.05),opf_nfam=len(groups))
    # 2. within-family permutation of y
    perm=[]
    for k in range(nperm):
        yp=y.copy()
        for ix in groups.values():
            if len(ix)>1: yp[ix]=rng.permutation(yp[ix])
        perm.append(logor(x,yp))
    perm=np.array(perm)
    out.update(perm_mean=perm.mean(),perm_sd=perm.std(),perm_p=(perm>=lo).mean() if lo>0 else (perm<=lo).mean(),perm_z=(lo-perm.mean())/perm.std())
    # 3. within-family contrast
    wf=[]
    for fname,ix in groups.items():
        xx=x[ix];yy=y[ix]
        if xx.sum()>0 and (xx==0).sum()>0:
            wf.append((fname,len(ix),yy[xx==1].mean(),yy[xx==0].mean()))
    wf=pd.DataFrame(wf,columns=['family','n','rate_A1','rate_A0'])
    out.update(wf_nfam=len(wf),wf_pos=(wf.rate_A1>wf.rate_A0).sum(),wf_neg=(wf.rate_A1<wf.rate_A0).sum(),wf_tie=(wf.rate_A1==wf.rate_A0).sum(),
               wf_mean_diff=(wf.rate_A1-wf.rate_A0).mean())
    if len(wf)>0 and (out['wf_pos']+out['wf_neg'])>0:
        out['wf_sign_p']=stats.binomtest(int(out['wf_pos']),int(out['wf_pos']+out['wf_neg'])).pvalue
    if verbose:
        for k,vv in out.items(): print(f'  {k}: {vv:.3f}' if isinstance(vv,float) else f'  {k}: {vv}')
        print('  macroarea table (A=av rows: supp/exc):')
        for a in sorted(set(mc)):
            s=((x==1)&(y==1)&(mc==a)).sum();e=((x==1)&(y==0)&(mc==a)).sum();o1=((x==0)&(y==1)&(mc==a)).sum();o0=((x==0)&(y==0)&(mc==a)).sum()
            print(f'    {a:14s} A=av: {s:4d}/{e:3d}  ({s/(s+e) if s+e else float("nan"):.2f})   A=other: {o1:4d}/{o0:4d} ({o1/(o1+o0) if o1+o0 else float("nan"):.2f})')
        print('  within-family contrasts:'); print(wf.to_string(index=False))
    return out,wf
if __name__=='__main__':
    B,fam,mac,nm,L=load()
    A,Bf,av,bv=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
    famtest(B,fam,mac,nm,A,Bf,av,bv)
