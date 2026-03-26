from data_loader import load_all_days, remove_outliers, compute_daily_stats

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
df_clean = remove_outliers(df)
daily = compute_daily_stats(df_clean)
print(daily.shape)
print(daily.head())
print(daily.describe())

print(daily[daily['trade_count'] < 50000].sort_values('trade_count'))
print(daily.sort_values('trade_count').head(10))
