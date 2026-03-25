from data_loader import load_all_days, remove_outliers, compute_tfi

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
df_clean = remove_outliers(df)
tfi = compute_tfi(df_clean)

print(tfi.shape)
print(tfi.head(10))
print(tfi['tfi'].describe())
