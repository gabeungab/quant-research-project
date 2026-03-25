from data_loader import load_all_days, resample_to_bars, remove_outliers

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
df_clean = remove_outliers(df)
df_bars = resample_to_bars(df_clean, "1D")

print(df_bars.shape)
print(df_bars.head())

print(df_clean['price'].describe())
print(df_clean[df_clean['price'] < 1000])
