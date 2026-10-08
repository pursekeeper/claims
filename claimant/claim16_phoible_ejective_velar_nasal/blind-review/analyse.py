import pandas as pd, numpy as np, warnings
from scipy import stats
warnings.filterwarnings("ignore")
L = pd.read_csv("./lang.csv")
for c in ["eject","ng_exact","ng_any","eject_m","ng_exact_m","ng_any_m","uvular","glottal","implos","click"]:
    L[c] = L[c].astype(bool)

def tab(d, x="eject", y="ng_exact", label=""):
    a = ((d[x]) & (d[y])).sum(); b = ((d[x]) & (~d[y])).sum()
    c = ((~d[x]) & (d[y])).sum(); dd = ((~d[x]) & (~d[y])).sum()
    OR = (a*dd)/(b*c) if b*c>0 else np.nan
    se = np.sqrt(1/a+1/b+1/c+1/dd) if min(a,b,c,dd)>0 else np.nan
    p = stats.fisher_exact([[a,b],[c,dd]])[1]
    print(f"{label:38s} n={len(d):4d} | ej+: {a}/{a+b} = {a/(a+b):.3f} | ej-: {c}/{c+dd} = {c/(c+dd):.3f} | OR={OR:.3f} [{OR*np.exp(-1.96*se):.3f},{OR*np.exp(1.96*se):.3f}] p={p:.2g}")
    return OR

def mh(d, strat, x="eject", y="ng_exact", label=""):
    num=den=0; k=0; ninf=0
    for s,g in d.groupby(strat):
        n=len(g)
        a=((g[x])&(g[y])).sum(); b=((g[x])&(~g[y])).sum(); c=((~g[x])&(g[y])).sum(); dd=((~g[x])&(~g[y])).sum()
        if (a+b)==0 or (c+dd)==0: continue
        num += a*dd/n; den += b*c/n; k+=1; ninf+=n
    OR = num/den if den>0 else np.nan
    # CMH test
    from statsmodels.stats.contingency_tables import StratifiedTable
    tabs=[]
    for s,g in d.groupby(strat):
        t=np.array([[((g[x])&(g[y])).sum(), ((g[x])&(~g[y])).sum()],[((~g[x])&(g[y])).sum(), ((~g[x])&(~g[y])).sum()]])
        if t[0].sum()>0 and t[1].sum()>0: tabs.append(t)
    st=StratifiedTable(tabs)
    ci=st.oddsratio_pooled_confint()
    p=st.test_null_odds().pvalue
    print(f"{label:38s} MH OR={OR:.3f} [{ci[0]:.3f},{ci[1]:.3f}] CMH p={p:.2g}  informative strata={k}, langs in them={ninf}")
    return OR

print("="*100); print("1. BASIC TABLES (one random inventory per glottocode; all languages incl. those without family metadata)")
tab(L, label="exact ŋ, non-marginal only")
tab(L, y="ng_any", label="any ŋ-based segment, non-marginal")
tab(L, x="eject_m", y="ng_exact_m", label="exact ŋ, marginals counted")
tab(L, x="eject_m", y="ng_any_m", label="any ŋ, marginals counted")
K = L[L.Family_known].copy()
tab(K, label="exact ŋ, only langs w/ family meta")
print("ejective languages:", L.eject.sum(), " with ŋ exact:", (L.eject&L.ng_exact).sum(), " with ŋ any:", (L.eject&L.ng_any).sum())

print("\n"+"="*100); print("2a. MANTEL-HAENSZEL BY FAMILY (isolates/unknowns = own stratum, uninformative)")
mh(K, "Family_name", label="exact ŋ | family")
mh(K, "Family_name", y="ng_any", label="any ŋ | family")
mh(K, "Family_name", x="eject_m", y="ng_exact_m", label="exact ŋ marg | family")

print("\n"+"="*100); print("2b. ONE LANGUAGE PER FAMILY RESAMPLING (1000 draws; isolates count as their own family)")
rng=np.random.default_rng(42)
fams = K.groupby("Family_name").indices
def one_per_family(y="ng_exact", n=1000):
    ors=[]; ps=[]; ns=[]
    for i in range(n):
        idx=[rng.choice(v) for v in fams.values()]
        d=K.iloc[idx]
        a=((d.eject)&(d[y])).sum(); b=((d.eject)&(~d[y])).sum(); c=((~d.eject)&(d[y])).sum(); dd=((~d.eject)&(~d[y])).sum()
        ors.append(((a+.5)*(dd+.5))/((b+.5)*(c+.5))); ps.append(stats.fisher_exact([[a,b],[c,dd]])[1]); ns.append(a+b)
    ors=np.array(ors); ps=np.array(ps)
    print(f"{y}: families={len(fams)}, ejective langs per draw ~{np.mean(ns):.1f}; median OR={np.median(ors):.3f}, 2.5-97.5%=[{np.percentile(ors,2.5):.3f},{np.percentile(ors,97.5):.3f}]; p<0.05 in {np.mean(ps<0.05)*100:.1f}% of draws; p<0.01 in {np.mean(ps<0.01)*100:.1f}%")
one_per_family("ng_exact"); one_per_family("ng_any")

print("\n"+"="*100); print("2c. WITHIN-FAMILY COMPARISONS (families with >=1 ejective and >=1 non-ejective language)")
rows=[]
for f,g in K.groupby("Family_name"):
    e=g[g.eject]; ne=g[~g.eject]
    if len(e)==0 or len(ne)==0: continue
    pe=e.ng_exact.mean(); pn=ne.ng_exact.mean()
    sign = "-" if pe<pn else ("+" if pe>pn else "0")
    rows.append((f,len(e),e.ng_exact.sum(),len(ne),ne.ng_exact.sum(),pe,pn,sign, e.ng_any.mean(), ne.ng_any.mean()))
W=pd.DataFrame(rows,columns=["family","n_ej","ŋ_ej","n_nonej","ŋ_nonej","P(ŋ|ej)","P(ŋ|no ej)","sign","P(ŋany|ej)","P(ŋany|noej)"]).sort_values("n_ej",ascending=False)
pd.set_option("display.width",200); pd.set_option("display.max_rows",200)
print(W.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
print("sign counts (exact ŋ):", W.sign.value_counts().to_dict())
big = W[(W.n_ej>=3)&(W.n_nonej>=3)]
print("families with >=3 on both sides:", len(big), big.sign.value_counts().to_dict())
signs = W[W.sign!="0"]
print("sign test (exact ŋ) all families:", stats.binomtest((signs.sign=="-").sum(), len(signs)).pvalue)
W["signany"]=np.sign(W["P(ŋany|ej)"]-W["P(ŋany|noej)"])
print("any-ŋ sign counts:", W.signany.value_counts().to_dict())

print("\n"+"="*100); print("3. AREA CONTROLS")
mh(K, "Macroarea", label="exact ŋ | macroarea")
mh(K, "Macroarea", y="ng_any", label="any ŋ | macroarea")
K["cell"] = (np.floor(K.Latitude/10)).astype(int).astype(str)+"_"+(np.floor(K.Longitude/10)).astype(int).astype(str)
mh(K, "cell", label="exact ŋ | 10° grid cell")
mh(K, "cell", y="ng_any", label="any ŋ | 10° grid cell")
K["famcell"] = K.Family_name+"|"+K.cell
mh(K, "famcell", label="exact ŋ | family × cell")
K["famarea"] = K.Family_name+"|"+K.Macroarea
mh(K, "famarea", label="exact ŋ | family × macroarea")
print("\nPer-macroarea tables:")
for m,g in K.groupby("Macroarea"):
    tab(g, label=f"  {m}")

print("\nNearest-neighbour matching (different family, within radius):")
from math import radians
def hav(lat1,lon1,lat2,lon2):
    lat1,lon1,lat2,lon2=map(np.radians,[lat1,lon1,lat2,lon2])
    a=np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371*2*np.arcsin(np.sqrt(a))
E=K[K.eject]; N=K[~K.eject]
for radius in [500,1000,2000]:
    for y in ["ng_exact","ng_any"]:
        conc=disc=tie=0; used=set(); pairs=[]
        for _,e in E.iterrows():
            d=hav(e.Latitude,e.Longitude,N.Latitude.values,N.Longitude.values)
            ok=(N.Family_name.values!=e.Family_name)&(d<=radius)
            if not ok.any(): continue
            j=np.argmin(np.where(ok,d,np.inf)); n=N.iloc[j]
            pairs.append((e[y],n[y]))
            if e[y]==n[y]: tie+=1
            elif (not e[y]) and n[y]: conc+=1   # ejective lang lacks ŋ, neighbour has it: supports claim
            else: disc+=1
        p=stats.binomtest(conc,conc+disc).pvalue if conc+disc>0 else np.nan
        print(f"  radius {radius}km, {y}: pairs={len(pairs)} supportive(ej-,nb+)={conc} contrary(ej+,nb-)={disc} ties={tie}  McNemar-exact p={p:.2g}; mean ŋ ej={np.mean([a for a,b in pairs]):.2f} nb={np.mean([b for a,b in pairs]):.2f}")

print("\n"+"="*100); print("4. CONFOUNDERS")
K2 = K.copy()
K2["n_nasal_c"] = K2.n_nasal.astype(float)
for c in ["n_nasal","n_seg","n_cons","uvular","glottal","implos","click"]:
    print(f"  {c}: ej+ mean={K2.loc[K2.eject,c].astype(float).mean():.2f}  ej- mean={K2.loc[~K2.eject,c].astype(float).mean():.2f}; corr with ŋ={np.corrcoef(K2[c].astype(float),K2.ng_exact.astype(float))[0,1]:.2f}")
print("  Source x ejectives x ŋ:")
for s,g in L.groupby("Source"):
    tab(g, label=f"    source={s}")
print("\n  Stratified by n_nasal (exact count):")
mh(K2, "n_nasal", label="exact ŋ | n_nasal")
mh(K2, "n_nasal", y="ng_any", label="any ŋ | n_nasal")
K2["consbin"]=pd.qcut(K2.n_cons,6,duplicates="drop").astype(str)
mh(K2, "consbin", label="exact ŋ | consonant-count sextile")
mh(L.assign(Source=L.Source), "Source", label="exact ŋ | Source (all langs)")
mh(K2, "uvular", label="exact ŋ | uvular")
mh(K2, "glottal", label="exact ŋ | glottal stop")
mh(K2, "implos", label="exact ŋ | implosives")
import statsmodels.formula.api as smf
K2["ej"]=K2.eject.astype(int); K2["ng"]=K2.ng_exact.astype(int); K2["ngany"]=K2.ng_any.astype(int)
K2["logcons"]=np.log(K2.n_cons); K2["uv"]=K2.uvular.astype(int); K2["gl"]=K2.glottal.astype(int); K2["im"]=K2.implos.astype(int)
K2["fam_id"]=pd.factorize(K2.Family_name)[0]
for y in ["ng","ngany"]:
    for form in [f"{y} ~ ej", f"{y} ~ ej + n_nasal + logcons + uv + gl + im", f"{y} ~ ej + n_nasal + logcons + uv + gl + im + C(Source)", f"{y} ~ ej + n_nasal + logcons + uv + gl + im + C(Source) + C(Macroarea)"]:
        m=smf.logit(form, K2).fit(disp=0, cov_type="cluster", cov_kwds={"groups":K2.fam_id})
        print(f"  {form:75s} ej coef={m.params['ej']:.3f} (OR={np.exp(m.params['ej']):.3f}) cl-SE={m.bse['ej']:.3f} p={m.pvalues['ej']:.2g}")
form="ng ~ ej + n_nasal + logcons + uv + gl + im + C(Source) + C(Macroarea)"
m=smf.logit(form, K2).fit(disp=0, cov_type="cluster", cov_kwds={"groups":K2.fam_id})
print(m.summary().tables[1])
# conditional (fixed-effects) logit by family
try:
    from statsmodels.discrete.conditional_models import ConditionalLogit
    d=K2.copy()
    keep=d.groupby("Family_name").ng.transform(lambda s: s.nunique()>1)
    d=d[keep]
    X=d[["ej","n_nasal","logcons","uv","gl","im"]]
    cm=ConditionalLogit(d.ng, X, groups=d.fam_id).fit(disp=0)
    print("  Conditional logit (family fixed effects), n=",len(d)); print(cm.summary().tables[1])
    cm=ConditionalLogit(d.ng, d[["ej"]], groups=d.fam_id).fit(disp=0)
    print("  Conditional logit ej only: coef=",cm.params.iloc[0], "OR=",np.exp(cm.params.iloc[0]), "p=",cm.pvalues.iloc[0])
except Exception as ex: print("cond logit failed", ex)

print("\n"+"="*100); print("5. EXCEPTIONS: ejective languages with exact ŋ")
ex=L[L.eject&L.ng_exact][["Glottocode","LanguageName","Family_name","Macroarea","Source","n_eject","n_nasal","ng_any"]].sort_values(["Family_name","LanguageName"])
print(ex.to_string(index=False)); print("n exceptions:", len(ex))
print("Ejective languages with ŋ-any but not exact:")
print(L[L.eject&L.ng_any&~L.ng_exact][["Glottocode","LanguageName","Family_name","Source"]].to_string(index=False))

print("\n"+"="*100); print("6. BREAK ATTEMPTS")
tab(K[K.Macroarea!="Africa"], label="drop Africa")
tab(K[K.Macroarea=="Africa"], label="Africa only")
tab(K[~K.Family_name.isin(["Afro-Asiatic"])], label="drop Afro-Asiatic")
cauc=["Nakh-Daghestanian","Abkhaz-Adyge","Northwest Caucasian","Kartvelian"]
tab(K[~K.Family_name.isin(cauc)], label="drop Caucasian families")
tab(K[~K.Family_name.isin(cauc+["Afro-Asiatic"])], label="drop Caucasus + Afro-Asiatic")
tab(K[~K.Macroarea.isin(["Africa","Eurasia"])], label="Americas+Papunesia+Australia only")
tab(K[K.Macroarea.isin(["North America","South America"])], label="Americas only")
mh(K[~K.Macroarea.isin(["Africa","Eurasia"])], "Family_name", label="MH family | Americas+Pap+Aus")
mh(K[K.Macroarea!="Africa"], "Family_name", label="MH family | no Africa")
mh(K[~K.Family_name.isin(cauc+["Afro-Asiatic"])], "Family_name", label="MH family | no Cauc/AA")
for s in ["upsid","ph","spa","ea","saphon","aa","gm","ra","er"]:
    g=L[L.Source==s]
    if g.eject.sum()>=3: tab(g, label=f"source={s} only")
# alternative one-inventory rule: use all inventories, cluster by glottocode (sensitivity)
I=pd.read_csv("./inv.csv")
for c in ["eject","ng_exact"]: I[c]=I[c].astype(bool)
tab(I, label="ALL inventories (no dedup)")
I2=I.sort_values("InventoryID").groupby("Glottocode").head(1)
tab(I2, label="lowest InventoryID per glottocode")
# without Australia (no ejectives; ŋ near universal) -- Australia inflates baseline
tab(K[K.Macroarea!="Australia"], label="drop Australia")
tab(K[~K.Macroarea.isin(["Australia","Africa"])], label="drop Australia+Africa")
# Remove languages with <=2 nasals? Check whether the effect is a 'few nasals' effect
tab(K[K.n_nasal>=3], label="langs with >=3 nasal consonants")
tab(K[K.n_nasal<=2], label="langs with <=2 nasal consonants")
# Only languages with a full labial-coronal-velar stop series? approximated: n_cons>=20
tab(K[K.n_cons>=25], label="n_cons>=25")
tab(K[K.n_cons<25], label="n_cons<25")
