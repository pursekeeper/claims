# Deterministic contingency tables for the PHOIBLE claim. Run: python3 tables.py DATA/phoible/data/phoible.csv
import sys, pandas as pd
p = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False, low_memory=False)
q = p[p.Marginal != "TRUE"]
g = q.groupby('InventoryID')
ej = g.apply(lambda d: (d.raisedLarynxEjective == '+').any())
ng = g.apply(lambda d: (d.Phoneme == 'ŋ').any())
print("Table A (all inventories):\n", pd.crosstab(ej, ng, rownames=['ejectives'], colnames=['ng']))
inv = p.groupby('InventoryID').Glottocode.first().reset_index()
inv = inv[inv.Glottocode != 'NA']; inv['iid'] = inv.InventoryID.astype(int)
keep = set(inv.sort_values('iid').groupby('Glottocode').InventoryID.first())
print("Table B (lowest InventoryID per Glottocode, n=%d):\n" % len(keep), pd.crosstab(ej[ej.index.isin(keep)], ng[ng.index.isin(keep)], rownames=['ejectives'], colnames=['ng']))
