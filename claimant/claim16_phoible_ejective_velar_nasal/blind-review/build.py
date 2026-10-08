import pandas as pd, numpy as np, unicodedata, re
P = "DATA/"
ph = pd.read_csv(P+"phoible/data/phoible.csv", low_memory=False, na_values=["NA"], keep_default_na=False)
print(ph.shape); print(ph.Source.value_counts()); print(ph.Marginal.value_counts(dropna=False))
print(ph.SegmentClass.value_counts())

# --- Segment-level flags ---
ph["eject"] = ph["raisedLarynxEjective"].eq("+")
# decompose phoneme, find base letter
def base(s):
    s = unicodedata.normalize("NFD", str(s))
    # strip combining marks and modifier letters
    return "".join(c for c in s if unicodedata.category(c) not in ("Mn","Lm","Sk"))
ph["base"] = ph.Phoneme.map(base)
ph["ng_exact"] = ph.Phoneme.eq("ŋ")
ph["ng_any"] = ph.base.str.contains("ŋ") & ph.SegmentClass.eq("consonant")
# ŋ-anywhere: includes prenasalised ᵑɡ? base of "ᵑɡ" -> 'ᵑ' is Lm -> stripped. OK so ᵑɡ excluded. Fine.
# But "ŋɡ" (digraph sequence) would count; and "ŋʷ", "ŋː", "ŋ̥" etc. also count.
print("ng_any variants:", ph.loc[ph.ng_any & ~ph.ng_exact, "Phoneme"].value_counts().head(40))

ph["nasal_c"] = ph.nasal.eq("+") & ph.SegmentClass.eq("consonant") & ph.consonantal.eq("+")
ph["uvular"] = ph.Phoneme.str.contains("[qɢχʁɴʛ]") & ph.SegmentClass.eq("consonant")
ph["glottal"] = ph.Phoneme.str.startswith("ʔ")
ph["implos"] = ph["loweredLarynxImplosive"].eq("+")
ph["click"] = ph["click"].eq("+")
ph["cons"] = ph.SegmentClass.eq("consonant")
ph["nasalized_seg"] = ph.nasal.eq("+")  # includes nasalized vowels

def agg(df, marginal_ok):
    d = df if marginal_ok else df[df.Marginal.ne(True) & df.Marginal.ne("TRUE")]
    g = d.groupby("InventoryID").agg(
        Glottocode=("Glottocode","first"), LanguageName=("LanguageName","first"), Source=("Source","first"),
        n_seg=("Phoneme","size"), n_cons=("cons","sum"),
        eject=("eject","any"), n_eject=("eject","sum"),
        ng_exact=("ng_exact","any"), ng_any=("ng_any","any"),
        n_nasal=("nasal_c","sum"), uvular=("uvular","any"), glottal=("glottal","any"),
        implos=("implos","any"), click=("click","any"))
    return g.reset_index()

print(ph.Marginal.map(type).value_counts())
inv = agg(ph, marginal_ok=False)
inv_m = agg(ph, marginal_ok=True)
inv = inv.merge(inv_m[["InventoryID","eject","ng_exact","ng_any"]].rename(columns={"eject":"eject_m","ng_exact":"ng_exact_m","ng_any":"ng_any_m"}), on="InventoryID")
print("inventories:", len(inv))

# --- one inventory per language ---
# Rule: per Glottocode, prefer source priority (ph > upsid > spa > aa > gm > ea > ra > saphon > er) -- no, avoid source bias:
# I use: the inventory with the LARGEST number of non-marginal segments? That biases toward ŋ presence. Better: random with fixed seed.
# Primary rule: random inventory per glottocode (seed 1). Sensitivity: check with 'first InventoryID' and 'largest'.
rng = np.random.default_rng(1)
inv = inv.dropna(subset=["Glottocode"])
inv["r"] = rng.random(len(inv))
lang = inv.sort_values("r").groupby("Glottocode").head(1).copy()
print("languages:", len(lang))

# --- family / area ---
gb = pd.read_csv(P+"grambank/cldf/languages.csv")
wals = pd.read_csv(P+"wals/cldf/languages.csv")
gb = gb[["Glottocode","Family_name","Macroarea","Latitude","Longitude"]].dropna(subset=["Glottocode"]).drop_duplicates("Glottocode")
wals = wals[["Glottocode","Family","Macroarea","Latitude","Longitude"]].dropna(subset=["Glottocode"]).drop_duplicates("Glottocode").rename(columns={"Family":"Family_name"})
lang = lang.merge(gb, on="Glottocode", how="left")
miss = lang.Family_name.isna() | lang.Macroarea.isna()
print("missing after grambank:", miss.sum())
w = lang.loc[miss, ["Glottocode"]].merge(wals, on="Glottocode", how="left")
for c in ["Family_name","Macroarea","Latitude","Longitude"]:
    lang.loc[miss, c] = w[c].values
print("missing after wals:", lang.Family_name.isna().sum(), lang.Macroarea.isna().sum(), lang.Latitude.isna().sum())
# isolates in grambank have Family_name == "" or NaN? check
print(lang.Family_name.value_counts(dropna=False).head(15))
lang.to_csv("./lang.csv", index=False)
inv.to_csv("./inv.csv", index=False)
