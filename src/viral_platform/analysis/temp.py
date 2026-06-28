import pandas as pd

meta = pd.read_csv(r"C:\Users\jtspy\OneDrive\Desktop\Bioinformatics\ViralDatasets\Dengue\elife-32942-supp7\extracted\cell_metadata_dengue.tsv", sep="\t")
counts = pd.read_csv(r"C:\Users\jtspy\OneDrive\Desktop\Bioinformatics\ViralDatasets\Dengue\elife-32942-supp7\extracted\counts_dengue.tsv", sep="\t")

# print(f"Meta Head:\n{meta.head()}")
# print(f"Meta Columns:\n{meta.columns}")

# print(f"Counts Head:\n{counts.head()}")
# print(f"Counts Columns:\n{counts.columns}")

# print(f"Counts shape: {counts.shape}")
# print(f"Counts Tail:\n{counts.tail()}")
# print(f"Count Ensembl: {counts['EnsemblID'].tail(20)}")

mask = ~counts["EnsemblID"].str.startswith(("ENSG", "ERCC", "__", "NIST"), na=False)
print(counts.loc[mask, "EnsemblID"])