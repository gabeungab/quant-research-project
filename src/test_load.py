from data_loader import (load_all_days, remove_outliers,
                         compute_daily_stats, plot_phase1)

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
df_clean = remove_outliers(df)
daily = compute_daily_stats(df_clean)
plot_phase1(df_clean, daily)
