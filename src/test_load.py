from data_loader import load_day

df = load_day("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/glbx-mdp3-20250501.trades.dbn.zst")
print(df.shape)
print(df.head())
