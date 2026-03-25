from data_loader import load_day
from data_loader import load_all_days

df = load_all_days("/Users/gabeungab/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/")
print(df.shape)
print(df.head())
