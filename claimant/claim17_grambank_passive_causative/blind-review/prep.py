import pandas as pd, numpy as np
D='DATA/grambank/cldf/'
v=pd.read_csv(D+'values.csv',usecols=['Language_ID','Parameter_ID','Value'],dtype=str)
l=pd.read_csv(D+'languages.csv',dtype=str)
W=v.pivot(index='Language_ID',columns='Parameter_ID',values='Value')
W=W.join(l.set_index('ID')[['Glottocode','Name','Family_name','Macroarea','Latitude','Longitude','level']])
print('languages in wide table',len(W))
print('level counts',W.level.value_counts().to_dict())
print('duplicated glottocodes',W.Glottocode.duplicated().sum())
W.to_pickle('./wide.pkl')
p=pd.read_csv(D+'parameters.csv',dtype=str)
p.to_pickle('./params.pkl')
for f in ['GB147','GB155','GB302']:
    print(f, W[f].value_counts(dropna=False).to_dict())
