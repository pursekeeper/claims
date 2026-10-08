import pandas as pd, numpy as np
B='DATA/'
ph=pd.read_csv(B+'phoible/data/phoible.csv',low_memory=False,na_values=['NA'],keep_default_na=False)
gb=pd.read_csv(B+'grambank/cldf/languages.csv')
wa=pd.read_csv(B+'wals/cldf/languages.csv')
WALS2GB={'Niger-Congo':'Atlantic-Congo','Oto-Manguean':'Otomanguean','Austro-Asiatic':'Austroasiatic',
 'Trans-New Guinea':'Nuclear Trans New Guinea','Bantu':'Atlantic-Congo','Bantoid':'Atlantic-Congo','Western Nilotic':'Nilotic','Eastern Nilotic':'Nilotic','Southern Nilotic':'Nilotic',
 'South Surmic':'Surmic','North Surmic':'Surmic','South Omotic':'South Omotic','Mongolic':'Mongolic-Khitan','Northwest Caucasian':'Abkhaz-Adyge','Na-Dene':'Athabaskan-Eyak-Tlingit',
 'Athapaskan':'Athabaskan-Eyak-Tlingit','Central Kainji':'Atlantic-Congo','Kainji':'Atlantic-Congo','Defoid':'Atlantic-Congo','Edoid':'Atlantic-Congo','Igboid':'Atlantic-Congo','Gur':'Atlantic-Congo','Kwa':'Atlantic-Congo','Cross River':'Atlantic-Congo','Platoid':'Atlantic-Congo','Grassfields Bantoid':'Atlantic-Congo','Adamawa':'Atlantic-Congo','Ubangi':'Atlantic-Congo','Northern Atlantic':'Atlantic-Congo','Southern Atlantic':'Atlantic-Congo','Nupoid':'Atlantic-Congo','Idomoid':'Atlantic-Congo','Jukunoid':'Atlantic-Congo','Agneby':'Atlantic-Congo','Avikam-Alladian':'Atlantic-Congo','Baatonum':'Atlantic-Congo','Balanta':'Atlantic-Congo','Benue-Congo Plateau':'Atlantic-Congo','Bua':'Atlantic-Congo','Cangin':'Atlantic-Congo','Central Delta':'Atlantic-Congo','Ekoid-Mbe':'Atlantic-Congo','Grusi':'Atlantic-Congo','Jola':'Atlantic-Congo','Kirma-Tyurama':'Atlantic-Congo','Lower Cross':'Atlantic-Congo','Mambiloid':'Atlantic-Congo','Mamfe':'Atlantic-Congo','Mbumic':'Atlantic-Congo','Na-Togo':'Atlantic-Congo','Oti-Volta':'Atlantic-Congo','Peul-Serer':'Atlantic-Congo','Samba-Duru':'Atlantic-Congo','Senufo':'Atlantic-Congo','Tano':'Atlantic-Congo','Tenda':'Atlantic-Congo','Upper Cross':'Atlantic-Congo','Wide Grassfields':'Atlantic-Congo','Nambikuaran':'Nambiquaran','Miwok':'Miwok-Costanoan','Macro-Ge':'Nuclear-Macro-Je','Gbaya-Manza-Ngbaka':'Gbaya-Manza-Ngbaka'}
def meta():
    g=gb[['Glottocode','Family_name','Macroarea','Name','Family_level_ID','Language_level_ID']].dropna(subset=['Glottocode']).drop_duplicates('Glottocode').copy()
    # isolates: no family -> use own name
    g.loc[g.Family_name.isna(),'Family_name']='ISOLATE:'+g.loc[g.Family_name.isna(),'Name']
    g=g[['Glottocode','Family_name','Macroarea']]
    w=wa[['Glottocode','Family','Genus','Macroarea']].dropna(subset=['Glottocode']).drop_duplicates('Glottocode').copy()
    # families not accepted by Glottolog -> use genus
    bad={'Altaic','Hokan','other','Penutian','Australian','Nilo-Saharan','Eastern Sudanic','Niger-Congo'}
    w['Fam']=np.where(w.Family.isin(bad),w.Genus,w.Family)
    w['Fam']=w.Fam.replace(WALS2GB)
    w=w.rename(columns={'Fam':'Family_name'})[['Glottocode','Family_name','Macroarea']]
    m=g.merge(w,on='Glottocode',how='outer',suffixes=('','_w'))
    m['Family_name']=m['Family_name'].fillna(m['Family_name_w'])
    m['Macroarea']=m['Macroarea'].fillna(m['Macroarea_w'])
    return m[['Glottocode','Family_name','Macroarea']]
M=meta()
# ISO fallback
gi=gb[['ISO639P3code','Family_name','Macroarea','Name']].dropna(subset=['ISO639P3code']).drop_duplicates('ISO639P3code').copy()
gi.loc[gi.Family_name.isna(),'Family_name']='ISOLATE:'+gi.loc[gi.Family_name.isna(),'Name']
wi=wa[['ISO_codes','Family','Genus','Macroarea']].dropna(subset=['ISO_codes']).copy()
wi=wi.assign(ISO639P3code=wi.ISO_codes.str.split()).explode('ISO639P3code').drop_duplicates('ISO639P3code')
bad={'Altaic','Hokan','other','Penutian','Australian','Nilo-Saharan','Eastern Sudanic','Niger-Congo'}
wi['Family_name']=np.where(wi.Family.isin(bad),wi.Genus,wi.Family); wi['Family_name']=wi.Family_name.replace(WALS2GB)
MI=pd.concat([gi[['ISO639P3code','Family_name','Macroarea']],wi[['ISO639P3code','Family_name','Macroarea']]]).drop_duplicates('ISO639P3code').rename(columns={'ISO639P3code':'ISO6393'})
pref={'ph':0,'spa':1,'upsid':2,'aa':3,'saphon':4,'ra':5,'ea':6,'er':7}
inv=ph.groupby('InventoryID').agg(Glottocode=('Glottocode','first'),Source=('Source','first'),LanguageName=('LanguageName','first'),n=('Phoneme','size')).reset_index()
inv['pr']=inv.Source.map(pref).fillna(99)
inv=inv.sort_values(['Glottocode','pr','InventoryID'])
sel=inv.dropna(subset=['Glottocode']).drop_duplicates('Glottocode')
P=ph[ph.InventoryID.isin(sel.InventoryID)].merge(M,on='Glottocode',how='left').merge(MI,on='ISO6393',how='left',suffixes=('','_iso'))
P['Family_name']=P['Family_name'].fillna(P['Family_name_iso']).fillna('UNKNOWN')
P['Macroarea']=P['Macroarea'].fillna(P['Macroarea_iso']).fillna('UNKNOWN')
P=P.drop(columns=['Family_name_iso','Macroarea_iso'])
INV=P.groupby('InventoryID').agg(Glottocode=('Glottocode','first'),LanguageName=('LanguageName','first'),Source=('Source','first'),Family_name=('Family_name','first'),Macroarea=('Macroarea','first'),n=('Phoneme','size')).reset_index()
FEATS=list(ph.columns[13:])
# source-based macroarea fill for unknowns: ER is Australian-only, SAPHON South-America-only
fix=(P.Macroarea=='UNKNOWN')&(P.Source=='er'); P.loc[fix,'Macroarea']='Australia'
fix=(P.Macroarea=='UNKNOWN')&(P.Source=='saphon'); P.loc[fix,'Macroarea']='South America'
INV=P.groupby('InventoryID').agg(Glottocode=('Glottocode','first'),LanguageName=('LanguageName','first'),Source=('Source','first'),Family_name=('Family_name','first'),Macroarea=('Macroarea','first'),n=('Phoneme','size')).reset_index()
