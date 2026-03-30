import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_all_days, remove_outliers
from signal_construction import (
    compute_lambda,
    compute_roll_spread,
    compute_arrival_rate,
    compute_exclusion_mask,
    compute_regime_score,
)

# ── Load data ─────────────────────────────────────────────────────────────────

df = load_all_days(
    "/Users/gabeungab/Desktop/Quant Research Project/raw-data/"
    "GLBX-20250501-20251231/"
)
df_clean = remove_outliers(df)

# ── Compute component series ──────────────────────────────────────────────────

lambda_series  = compute_lambda(df_clean)
roll_series    = compute_roll_spread(df_clean)
arrival_series = compute_arrival_rate(df_clean)

# ── Build 1-minute bar index for exclusion mask ───────────────────────────────

df_indexed = df_clean.set_index('ts_event_et')
bars = df_indexed['price'].resample('1min').count()

# ── Define macro announcement datetimes (Eastern) ────────────────────────────
# FOMC, CPI, and NFP releases for in-sample period 2025-05-01 to 2025-12-30.
# Verified against official Fed/BLS release calendars. Oct NFP and CPI not
# published due to 2025 government shutdown — replaced with delayed releases.

TZ = "America/New_York"

announcement_dates = [
    # FOMC statement release (2:00 PM ET)
    pd.Timestamp("2025-05-07 14:00", tz=TZ),
    pd.Timestamp("2025-06-18 14:00", tz=TZ),
    pd.Timestamp("2025-07-30 14:00", tz=TZ),
    pd.Timestamp("2025-09-17 14:00", tz=TZ),
    pd.Timestamp("2025-10-29 14:00", tz=TZ),
    pd.Timestamp("2025-12-10 14:00", tz=TZ),
    # CPI release (8:30 AM ET) — Oct not published; Nov+Oct combined Dec 18
    pd.Timestamp("2025-05-13 08:30", tz=TZ),
    pd.Timestamp("2025-06-11 08:30", tz=TZ),
    pd.Timestamp("2025-07-15 08:30", tz=TZ),
    pd.Timestamp("2025-08-12 08:30", tz=TZ),
    pd.Timestamp("2025-09-10 08:30", tz=TZ),
    pd.Timestamp("2025-12-18 08:30", tz=TZ),
    # NFP release (8:30 AM ET) — Oct not published; Sep delayed Nov 20;
    # Oct+Nov combined Dec 16; Jul 3 (moved from Jul 4 holiday)
    pd.Timestamp("2025-05-02 08:30", tz=TZ),
    pd.Timestamp("2025-06-06 08:30", tz=TZ),
    pd.Timestamp("2025-07-03 08:30", tz=TZ),
    pd.Timestamp("2025-08-01 08:30", tz=TZ),
    pd.Timestamp("2025-09-05 08:30", tz=TZ),
    pd.Timestamp("2025-11-20 08:30", tz=TZ),
    pd.Timestamp("2025-12-16 08:30", tz=TZ),
]

if bars.index.tzinfo is None:
    announcement_dates = [dt.tz_localize(None) for dt in announcement_dates]

# ── Build exclusion mask and regime score ─────────────────────────────────────

exclusion_mask = compute_exclusion_mask(bars, announcement_dates)
regime_score   = compute_regime_score(
    lambda_series, roll_series, arrival_series, exclusion_mask
)

# ── Sanity checks ─────────────────────────────────────────────────────────────

def print_series_stats(name, s):
    print(f"\n{'=' * 50}")
    print(f"{name}")
    print(f"  shape      : {s.shape}")
    print(f"  index range: {s.index.min()}  →  {s.index.max()}")
    print(f"  mean       : {s.mean():.6f}")
    print(f"  std        : {s.std():.6f}")
    print(f"  min        : {s.min():.6f}")
    print(f"  max        : {s.max():.6f}")
    print(f"  NaN count  : {s.isna().sum()}")

print_series_stats("Kyle's lambda",      lambda_series)
rth_mask_check = (
    (lambda_series.index.time >= pd.Timestamp('09:30').time()) &
    (lambda_series.index.time <= pd.Timestamp('16:00').time())
)
print(f"  RTH NaN count  : {lambda_series[rth_mask_check].isna().sum()}")
print(f"  RTH valid count: {lambda_series[rth_mask_check].notna().sum()}")

print_series_stats("Roll spread",        roll_series)
rth_mask_check = (
    (lambda_series.index.time >= pd.Timestamp('09:30').time()) &
    (lambda_series.index.time <= pd.Timestamp('16:00').time())
)
print(f"  RTH NaN count  : {lambda_series[rth_mask_check].isna().sum()}")
print(f"  RTH valid count: {lambda_series[rth_mask_check].notna().sum()}")

print_series_stats("Trade arrival rate", arrival_series)

# ── Exclusion mask breakdown ──────────────────────────────────────────────────

n_bars_total = len(exclusion_mask)
n_excluded   = exclusion_mask.sum()

print(f"\n{'=' * 50}")
print(f"Exclusion mask")
print(f"  total bars     : {n_bars_total}")
print(f"  excluded bars  : {n_excluded}  ({n_excluded / n_bars_total:.4f} of total)")
print(f"  retained bars  : {n_bars_total - n_excluded}")

# ── RegimeScore breakdown ─────────────────────────────────────────────────────

print_series_stats("RegimeScore", regime_score)

n_valid    = regime_score.notna().sum()
n_above_50 = (regime_score > 0.5).sum()
n_above_75 = (regime_score > 0.75).sum()
n_zero     = (regime_score == 0.0).sum()

print(f"\n  RegimeScore breakdowns (non-NaN bars = {n_valid}):")
print(f"    fraction > 0.50 : {n_above_50 / n_valid:.4f}  ({n_above_50} bars)")
print(f"    fraction > 0.75 : {n_above_75 / n_valid:.4f}  ({n_above_75} bars)")
print(f"    fraction = 0.00 : {n_zero / n_valid:.4f}  "
      f"({n_zero} bars, set by exclusion mask)")
