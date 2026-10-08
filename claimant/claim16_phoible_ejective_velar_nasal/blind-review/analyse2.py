import pandas as pd, numpy as np, warnings, unicodedata
from scipy import stats
warnings.filterwarnings("ignore")
exec(open("./analyse.py").read().split('print("="*100); print("1.')[0])  # reuse tab/mh helpers only
P = "DATA/"
ph = pd.read_csv(P+"phoible/data/phoible.csv", low_memory=False, na_values=["NA"], keep_default_na=False)
ph = ph[ph.Marginal.ne(True)]
def base(s):
    s = unicodedata.normalize("NFD", str(s)); return "".join(c for c in s if unicodedata.category(c) not in ("Mn","Lm","Sk"))
ph["base"]=ph.Phoneme.map(base)
nas = ph[ph.nasal.eq("+") & ph.SegmentClass.eq("consonant") & ph.consonantal.eq("+")]
# distinct nasal places other than ŋ: m, n, ɲ, ɳ, ɴ; count nasal segments not containing ŋ
other = nas[~nas.base.str.contains("ŋ")].groupby("InventoryID").size().rename("n_other_nasal")
has_m = nas[nas.base.str.contains("m")].groupby("InventoryID").size().rename("has_m")
has_n = nas[nas.base.str.contains("n") & ~nas.base.str.contains("ɲ|ɳ|ŋ|ɴ")].groupby("InventoryID").size().rename("has_n")
has_palnas = nas[nas.base.str.contains("ɲ")].groupby("InventoryID").size().rename("has_pal")
# velar stops: does the language have a plain velar stop k? (ŋ needs a velar place)
velk = ph[ph.SegmentClass.eq("consonant") & ph.base.str.contains("k|ɡ|g")].groupby("InventoryID").size().rename("has_velar_stop")
L = L.merge(other, left_on="InventoryID", right_index=True, how="left").merge(has_m, left_on="InventoryID", right_index=True, how="left").merge(has_n, left_on="InventoryID", right_index=True, how="left").merge(has_palnas, left_on="InventoryID", right_index=True, how="left")
for c in ["n_other_nasal","has_m","has_n","has_pal"]: L[c]=L[c].fillna(0)
L["has_pal"]=L.has_pal>0
# grambank subfamily (2nd node of lineage)
gb = pd.read_csv(P+"grambank/cldf/languages.csv")
gb["sub"] = gb.lineage.fillna("").map(lambda s: "/".join(s.split("/")[:2]) if s else "")
gb["sub3"] = gb.lineage.fillna("").map(lambda s: "/".join(s.split("/")[:3]) if s else "")
L = L.merge(gb[["Glottocode","sub","sub3"]], on="Glottocode", how="left")
L["sub"] = np.where(L["sub"].fillna("")=="", L.Family_name+"|nosub", L["sub"])
L["sub3"] = np.where(L["sub3"].fillna("")=="", L["sub"], L["sub3"])
K = L[L.Family_known].copy()

print("="*100); print("4b. NASAL-SYSTEM CONFOUND: other-nasal count (excluding ŋ-based)")
print(pd.crosstab([K.eject], K.n_other_nasal.clip(upper=4)))
for k in [1,2,3,4]:
    g=K[K.n_other_nasal.clip(upper=4)==k]
    if g.eject.sum()>0: tab(g, label=f"  n_other_nasal={k}{'+' if k==4 else ''}")
mh(K, "n_other_nasal", label="exact ŋ | n_other_nasal")
mh(K, "n_other_nasal", y="ng_any", label="any ŋ | n_other_nasal")
K["fam_on"]=K.Family_name+"|"+K.n_other_nasal.astype(str)
mh(K, "fam_on", label="exact ŋ | family × n_other_nasal")
K["area_on"]=K.Macroarea+"|"+K.n_other_nasal.astype(str)
mh(K, "area_on", label="exact ŋ | macroarea × n_other_nasal")
# The "m n only" world
g=K[(K.n_other_nasal==2)]
tab(g, label="  exactly 2 non-ŋ nasals (m,n)")
mh(g, "Macroarea", label="  m,n only | macroarea")
mh(g, "Family_name", label="  m,n only | family")
g=K[(K.n_other_nasal>=3)]
tab(g, label="  >=3 non-ŋ nasals (m,n,ɲ..)")
mh(g, "Macroarea", label="  >=3 non-ŋ | macroarea")
print("\n  palatal nasal ɲ vs ejectives (is it 'ejective langs lack ALL non-anterior nasals'?):")
tab(K, y="has_pal", label="  P(ɲ|ej) vs P(ɲ|no ej)")
mh(K, "Macroarea", y="has_pal", label="  ɲ | macroarea")

print("\n"+"="*100); print("2d. MH BY GLOTTOLOG SUBFAMILY (grambank lineage 2nd/3rd node; WALS-only langs = family|nosub)")
mh(K, "sub", label="exact ŋ | subfamily(2)")
mh(K, "sub3", label="exact ŋ | subfamily(3)")
print("  informative subfamilies:")
for s,g in K.groupby("sub3"):
    e=g[g.eject]; ne=g[~g.eject]
    if len(e) and len(ne): print(f"   {s:45s} ej: {e.ng_exact.sum()}/{len(e)}  non-ej: {ne.ng_exact.sum()}/{len(ne)}")

print("\n"+"="*100); print("4c. LOGIT WITHOUT AUSTRALIA/PAPUNESIA (no ejective langs there; Australia causes separation), family-clustered SE")
import statsmodels.formula.api as smf
D=K[~K.Macroarea.isin(["Australia","Papunesia"])].copy()
D["ej"]=D.eject.astype(int); D["ng"]=D.ng_exact.astype(int); D["logcons"]=np.log(D.n_cons); D["uv"]=D.uvular.astype(int); D["gl"]=D.glottal.astype(int); D["im"]=D.implos.astype(int)
D["fam_id"]=pd.factorize(D.Family_name)[0]; D["on"]=D.n_other_nasal
for form in ["ng ~ ej", "ng ~ ej + C(Macroarea)", "ng ~ ej + on", "ng ~ ej + on + logcons + uv + gl + im", "ng ~ ej + on + logcons + uv + gl + im + C(Source) + C(Macroarea)"]:
    m=smf.logit(form, D).fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups":D.fam_id})
    print(f"  {form:70s} n={int(m.nobs)} ej OR={np.exp(m.params['ej']):.3f} [{np.exp(m.params['ej']-1.96*m.bse['ej']):.3f},{np.exp(m.params['ej']+1.96*m.bse['ej']):.3f}] p={m.pvalues['ej']:.2g}")
from statsmodels.discrete.conditional_models import ConditionalLogit
d=D[D.groupby("Family_name").ng.transform(lambda s: s.nunique()>1)]
for cols in [["ej"],["ej","on"],["ej","on","logcons","uv","gl","im"]]:
    cm=ConditionalLogit(d.ng, d[cols], groups=d.fam_id).fit(disp=0, maxiter=500)
    print(f"  Family fixed-effects logit {cols}: ej OR={np.exp(cm.params['ej']):.3f} [{np.exp(cm.params['ej']-1.96*cm.bse['ej']):.3f},{np.exp(cm.params['ej']+1.96*cm.bse['ej']):.3f}] p={cm.pvalues['ej']:.2g} (n={len(d)})")
# mixed model with family random intercept
try:
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    for form in ["ng ~ ej", "ng ~ ej + on + C(Macroarea)"]:
        mm=BinomialBayesMixedGLM.from_formula(form, {"fam":"0 + C(Family_name)"}, D).fit_vb()
        i=list(mm.model.exog_names).index("ej")
        print(f"  Random-intercept(family) logit {form}: ej OR={np.exp(mm.fe_mean[i]):.3f}, sd={mm.fe_sd[i]:.3f}, approx z={mm.fe_mean[i]/mm.fe_sd[i]:.2f}")
except Exception as ex: print("mixed failed", ex)

print("\n"+"="*100); print("6b. MORE BREAK ATTEMPTS")
tab(K[K.Macroarea=="North America"], label="North America")
mh(K[K.Macroarea=="North America"], "Family_name", label="  N America | family")
tab(K[K.Macroarea=="South America"], label="South America")
tab(K[K.Macroarea=="Eurasia"], label="Eurasia")
tab(K[(K.Macroarea=="Eurasia")&~K.Family_name.isin(["Nakh-Daghestanian","Abkhaz-Adyge","Northwest Caucasian","Kartvelian"])], label="Eurasia minus Caucasian fams")
print("  Eurasian ejective languages:"); print(K[(K.Macroarea=="Eurasia")&K.eject][["LanguageName","Family_name","ng_exact"]].to_string(index=False))
# Africa without Ethiopia/Horn (lat 3-18, lon 33-48) and without Khoisan-area (S Africa)
eth=(K.Latitude.between(2,18))&(K.Longitude.between(32,49))
tab(K[(K.Macroarea=="Africa")&eth], label="Africa: Ethiopia/Horn box")
tab(K[(K.Macroarea=="Africa")&~eth], label="Africa: outside Horn box")
mh(K[(K.Macroarea=="Africa")], "sub3", label="  Africa | subfamily3")
# Ethiopia box: ejective vs non-ejective (areal control within Ethiopia)
mh(K[(K.Macroarea=="Africa")&eth], "Family_name", label="  Horn box | family")
