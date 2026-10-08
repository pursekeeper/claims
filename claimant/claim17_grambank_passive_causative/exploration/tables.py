# Deterministic contingency tables for the Grambank claim. Run: python3 tables.py DATA/grambank/cldf/values.csv
import sys, pandas as pd
v = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False)
w = v[v.Parameter_ID.isin(['GB147','GB155','GB302'])].pivot(index='Language_ID', columns='Parameter_ID', values='Value')
a = w[w.GB147.isin(['0','1']) & w.GB155.isin(['0','1'])]
print("Table A GB147 x GB155 (n=%d):\n" % len(a), pd.crosstab(a.GB147, a.GB155))
b = w[w.GB302.isin(['0','1']) & w.GB155.isin(['0','1'])]
print("Table B GB302 x GB155 (n=%d):\n" % len(b), pd.crosstab(b.GB302, b.GB155))
