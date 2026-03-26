from data_loader import (load_all_days, remove_outliers,
                         compute_tfi, compute_returns, plot_overview)

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
df_clean = remove_outliers(df)
tfi = compute_tfi(df_clean)
returns = compute_returns(df_clean)
plot_overview(tfi, returns)
