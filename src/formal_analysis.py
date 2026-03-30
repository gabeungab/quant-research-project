import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_all_days, remove_outliers, compute_tfi, compute_returns
from signal_construction import (
    compute_lambda,
    compute_roll_spread,
    compute_arrival_rate,
    compute_exclusion_mask,
    compute_regime_score,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    '~/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/'
)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'phase4')
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── Announcement dates (Eastern) ──────────────────────────────────────────────
TZ = 'America/New_York'
ANNOUNCEMENT_DATES = [
    # FOMC (2:00 PM ET)
    pd.Timestamp("2025-05-07 14:00", tz=TZ),
    pd.Timestamp("2025-06-18 14:00", tz=TZ),
    pd.Timestamp("2025-07-30 14:00", tz=TZ),
    pd.Timestamp("2025-09-17 14:00", tz=TZ),
    pd.Timestamp("2025-10-29 14:00", tz=TZ),
    pd.Timestamp("2025-12-10 14:00", tz=TZ),
    # CPI (8:30 AM ET)
    pd.Timestamp("2025-05-13 08:30", tz=TZ),
    pd.Timestamp("2025-06-11 08:30", tz=TZ),
    pd.Timestamp("2025-07-15 08:30", tz=TZ),
    pd.Timestamp("2025-08-12 08:30", tz=TZ),
    pd.Timestamp("2025-09-10 08:30", tz=TZ),
    pd.Timestamp("2025-12-18 08:30", tz=TZ),
    # NFP (8:30 AM ET)
    pd.Timestamp("2025-05-02 08:30", tz=TZ),
    pd.Timestamp("2025-06-06 08:30", tz=TZ),
    pd.Timestamp("2025-07-03 08:30", tz=TZ),
    pd.Timestamp("2025-08-01 08:30", tz=TZ),
    pd.Timestamp("2025-09-05 08:30", tz=TZ),
    pd.Timestamp("2025-11-20 08:30", tz=TZ),
    pd.Timestamp("2025-12-16 08:30", tz=TZ),
]

# =============================================================================
# 1. DATA PREPARATION
# =============================================================================

print("=" * 60)
print("PHASE 4 — FORMAL STATISTICAL ANALYSIS")
print("=" * 60)

# ── Load and clean ────────────────────────────────────────────────────────────
print("\n[1] Loading data...")
df = load_all_days(DATA_DIR)
df_clean = remove_outliers(df)
print(f"    Loaded {len(df_clean):,} clean RTH trades across "
      f"{df_clean['ts_event_et'].dt.date.nunique()} trading days")

# ── Compute signals ───────────────────────────────────────────────────────────
print("\n[2] Computing signals...")
lambda_series  = compute_lambda(df_clean)
roll_series    = compute_roll_spread(df_clean)
arrival_series = compute_arrival_rate(df_clean)

df_indexed = df_clean.set_index('ts_event_et')
bars = df_indexed['price'].resample('1min').count()

ann_dates = ANNOUNCEMENT_DATES
if bars.index.tzinfo is None:
    ann_dates = [dt.tz_localize(None) for dt in ann_dates]

exclusion_mask = compute_exclusion_mask(bars, ann_dates)
regime_score   = compute_regime_score(
    lambda_series, roll_series, arrival_series, exclusion_mask
)

tfi     = compute_tfi(df_clean)
returns = compute_returns(df_clean)

# ── Build regression DataFrame ────────────────────────────────────────────────
print("\n[3] Building regression DataFrame...")

# Handle Series or DataFrame inputs
tfi_series = tfi['tfi'] if isinstance(tfi, pd.DataFrame) else tfi
ret_series = returns['log_return'] if isinstance(returns, pd.DataFrame) else returns

reg = pd.DataFrame({
    'tfi':          tfi_series,
    'log_return':   ret_series,
    'regime_score': regime_score,
})

# Null out first bar of each day — overnight gap is not an RTH return
reg_dates = pd.Series(reg.index.date, index=reg.index)
first_bar = reg_dates != reg_dates.shift(1)
reg.loc[first_bar, 'log_return'] = np.nan

# Construct regression variables per research design
reg['fwd_return']   = reg['log_return'].shift(-1)   # Return_{t+1}
reg['lag_return']   = reg['log_return']              # Return_t (control)
reg['lag_tfi']      = reg['tfi'].shift(1)            # TFI_{t-1} (control)
reg['tfi_x_regime'] = reg['tfi'] * reg['regime_score']

n_raw = len(reg)
print(f"    Bars before filters: {n_raw:,}")

# ── Drop NaN rows (rolling warmup + day boundaries + forward return edge) ─────
REGRESSION_COLS = ['fwd_return', 'tfi', 'regime_score',
                   'tfi_x_regime', 'lag_return', 'lag_tfi']
reg = reg.dropna(subset=REGRESSION_COLS)
n_final = len(reg)
print(f"    Dropped (NaN/warmup/boundaries): {n_raw - n_final:,}")
print(f"    Final regression N:              {n_final:,}")

# ── Summary statistics ────────────────────────────────────────────────────────
print("\n[4] Summary statistics — regression variables:")
print("-" * 60)
print(reg[REGRESSION_COLS].describe().round(6).to_string())

print("\n    Regime distribution:")
high_n = (reg['regime_score'] > 0.5).sum()
low_n  = (reg['regime_score'] <= 0.5).sum()
print(f"      High-regime bars (RegimeScore > 0.5): {high_n:,} "
      f"({high_n / n_final * 100:.1f}%)")
print(f"      Low-regime bars  (RegimeScore ≤ 0.5): {low_n:,} "
      f"({low_n / n_final * 100:.1f}%)")

print("\n    Date range:")
print(f"      First bar:    {reg.index.min()}")
print(f"      Last bar:     {reg.index.max()}")
print(f"      Trading days: {reg.index.normalize().nunique()}")

# =============================================================================
# 2. PRIMARY REGRESSION (T+1)
# =============================================================================

print("\n" + "=" * 60)
print("PRIMARY REGRESSION — Return_{t+1}")
print("=" * 60)

y = reg['fwd_return']
X = sm.add_constant(reg[['tfi', 'regime_score', 'tfi_x_regime',
                           'lag_return', 'lag_tfi']])

model  = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
print(model.summary())

# =============================================================================
# 3. CONTEMPORANEOUS SECONDARY REGRESSION
# =============================================================================

print("\n" + "=" * 60)
print("CONTEMPORANEOUS REGRESSION — Return_t")
print("=" * 60)

y_contemp = reg['lag_return']
X_contemp = sm.add_constant(reg[['tfi', 'regime_score', 'tfi_x_regime',
                                   'lag_tfi']])

model_contemp = sm.OLS(y_contemp, X_contemp).fit(
    cov_type='HAC', cov_kwds={'maxlags': 5}
)
print(model_contemp.summary())

# =============================================================================
# 4. HORIZON ANALYSIS
# =============================================================================

print("\n" + "=" * 60)
print("HORIZON ANALYSIS — T+5 and T+15 Cumulative Returns")
print("=" * 60)

horizon_models = {}
reg_dates_series = pd.Series(reg.index.date, index=reg.index)

for h in [5, 15]:
    col_h = f'fwd_return_{h}'

    # Vectorized cumulative forward return — sum of next h log_return bars
    reg[col_h] = reg['log_return'].rolling(h).sum().shift(-h)

    # Null out bars where the h-bar window crosses a day boundary
    for i in range(1, h + 1):
        crosses = reg_dates_series != reg_dates_series.shift(-i)
        reg.loc[crosses, col_h] = np.nan

    horizon_cols = [col_h, 'tfi', 'regime_score', 'tfi_x_regime',
                    'lag_return', 'lag_tfi']
    reg_h = reg.dropna(subset=horizon_cols)

    y_h = reg_h[col_h]
    X_h = sm.add_constant(reg_h[['tfi', 'regime_score', 'tfi_x_regime',
                                   'lag_return', 'lag_tfi']])
    model_h = sm.OLS(y_h, X_h).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    horizon_models[h] = model_h

    print(f"\n  Horizon T+{h} | N={len(reg_h):,}")
    print(f"  {'Variable':<20} {'Coeff':>12} {'z-stat':>8} {'p-value':>10}")
    print(f"  {'-'*54}")
    for var in ['const', 'tfi', 'regime_score', 'tfi_x_regime',
                'lag_return', 'lag_tfi']:
        c   = model_h.params[var]
        t   = model_h.tvalues[var]
        p   = model_h.pvalues[var]
        sig = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else ''
        print(f"  {var:<20} {c:>12.6f} {t:>8.3f} {p:>10.4f} {sig}")
    print(f"  R²: {model_h.rsquared:.6f}")

# =============================================================================
# 5. SUBSAMPLE STABILITY
# =============================================================================

print("\n" + "=" * 60)
print("SUBSAMPLE STABILITY")
print("=" * 60)

subsample_models = {}
subsamples = {
    'full':    (None, None),
    'may_sep': (pd.Timestamp('2025-05-01').date(),
                pd.Timestamp('2025-09-30').date()),
    'oct_dec': (pd.Timestamp('2025-10-01').date(),
                pd.Timestamp('2025-12-31').date()),
}
period_labels = {
    'full':    'Full sample (May–Dec 2025)',
    'may_sep': 'May–Sep 2025',
    'oct_dec': 'Oct–Dec 2025',
}

for label, (start, end) in subsamples.items():
    if start is None:
        reg_sub = reg.copy()
    else:
        idx_dates = pd.Series(reg.index.date, index=reg.index)
        reg_sub = reg[(idx_dates >= start) & (idx_dates <= end)]

    reg_sub = reg_sub.dropna(subset=REGRESSION_COLS)

    if len(reg_sub) < 100:
        print(f"\n  {label}: insufficient observations ({len(reg_sub)}), skipping")
        continue

    y_sub = reg_sub['fwd_return']
    X_sub = sm.add_constant(reg_sub[['tfi', 'regime_score', 'tfi_x_regime',
                                      'lag_return', 'lag_tfi']])
    model_sub = sm.OLS(y_sub, X_sub).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
    subsample_models[label] = model_sub

    print(f"\n  {period_labels[label]} | N={len(reg_sub):,}")
    print(f"  {'Variable':<20} {'Coeff':>12} {'z-stat':>8} {'p-value':>10}")
    print(f"  {'-'*54}")
    for var in ['const', 'tfi', 'regime_score', 'tfi_x_regime',
                'lag_return', 'lag_tfi']:
        c   = model_sub.params[var]
        t   = model_sub.tvalues[var]
        p   = model_sub.pvalues[var]
        sig = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.10 else ''
        print(f"  {var:<20} {c:>12.6f} {t:>8.3f} {p:>10.4f} {sig}")
    print(f"  R²: {model_sub.rsquared:.6f}")

# =============================================================================
# 6. TRANSACTION COST ANALYSIS
# =============================================================================

print("\n" + "=" * 60)
print("TRANSACTION COST ANALYSIS")
print("=" * 60)

ES_TICK = 0.25
mean_price = df_indexed['price'].resample('1min').last().dropna().mean()
one_tick_log   = float(np.log1p(ES_TICK / mean_price))
round_trip_log = 2.0 * one_tick_log

print(f"\n  Mean ES close price:         {mean_price:,.2f}")
print(f"  One-way cost (1 tick):       {one_tick_log   * 1e4:.3f} bps")
print(f"  Round-trip cost (2 ticks):   {round_trip_log * 1e4:.3f} bps")

mean_lag_ret  = float(reg['lag_return'].mean())
mean_lag_tfi_ = float(reg['lag_tfi'].mean())
high_mask     = reg['regime_score'] > 0.5
mean_regime_h = float(reg.loc[high_mask, 'regime_score'].mean())
tfi_p25 = float(reg.loc[high_mask, 'tfi'].quantile(0.25))
tfi_p50 = float(reg.loc[high_mask, 'tfi'].median())
tfi_p75 = float(reg.loc[high_mask, 'tfi'].quantile(0.75))

print(f"\n  High-regime TFI percentiles (RegimeScore > 0.5):")
print(f"    25th: {tfi_p25:.4f}   Median: {tfi_p50:.4f}   75th: {tfi_p75:.4f}")

# ── Contemporaneous spec (β₃ significant, p<0.001) ───────────────────────────
print(f"\n  --- Contemporaneous regression (β₃ significant, p<0.001) ---")
a_c  = model_contemp.params['const']
b1_c = model_contemp.params['tfi']
b2_c = model_contemp.params['regime_score']
b3_c = model_contemp.params['tfi_x_regime']
b5_c = model_contemp.params['lag_tfi']
total_c = b1_c + b3_c

def pred_contemp(tfi_val, regime_val):
    return (a_c + b1_c * tfi_val + b2_c * regime_val
            + b3_c * tfi_val * regime_val + b5_c * mean_lag_tfi_)

print(f"  {'TFI':<12} {'Gross (bps)':>12} {'Net 1-way (bps)':>16} "
      f"{'Net RT (bps)':>14}")
print(f"  {'-'*56}")
for tfi_val, tag in [(tfi_p25, 'p25 (short)'),
                      (tfi_p50, 'p50  (mid) '),
                      (tfi_p75, 'p75  (long)')]:
    gross = pred_contemp(tfi_val, mean_regime_h)
    net1  = gross - one_tick_log  * np.sign(tfi_val)
    net2  = gross - round_trip_log * np.sign(tfi_val)
    print(f"  {tag:<12} {gross*1e4:>12.3f} {net1*1e4:>16.3f} {net2*1e4:>14.3f}")

if abs(total_c) > 1e-12:
    tfi_be_1way = ((one_tick_log - a_c - b2_c * mean_regime_h
                    - b5_c * mean_lag_tfi_) / total_c)
    tfi_be_rt   = ((round_trip_log - a_c - b2_c * mean_regime_h
                    - b5_c * mean_lag_tfi_) / total_c)
    print(f"\n  Break-even TFI (contemporaneous, RegimeScore={mean_regime_h:.3f}):")
    print(f"    One-way  (1 tick):    {tfi_be_1way:.4f}")
    print(f"    Round-trip (2 ticks): {tfi_be_rt:.4f}")

# ── T+1 spec (β₃ not significant, p=0.570 — for completeness) ────────────────
print(f"\n  --- T+1 regression (β₃ not significant, p=0.570) ---")
a_p  = model.params['const']
b1_p = model.params['tfi']
b2_p = model.params['regime_score']
b3_p = model.params['tfi_x_regime']
b4_p = model.params['lag_return']
b5_p = model.params['lag_tfi']
total_p = b1_p + b3_p

def pred_primary(tfi_val, regime_val):
    return (a_p + b1_p * tfi_val + b2_p * regime_val
            + b3_p * tfi_val * regime_val
            + b4_p * mean_lag_ret + b5_p * mean_lag_tfi_)

print(f"  {'TFI':<12} {'Gross (bps)':>12} {'Net 1-way (bps)':>16} "
      f"{'Net RT (bps)':>14}")
print(f"  {'-'*56}")
for tfi_val, tag in [(tfi_p25, 'p25 (short)'),
                      (tfi_p50, 'p50  (mid) '),
                      (tfi_p75, 'p75  (long)')]:
    gross = pred_primary(tfi_val, mean_regime_h)
    net1  = gross - one_tick_log  * np.sign(tfi_val)
    net2  = gross - round_trip_log * np.sign(tfi_val)
    print(f"  {tag:<12} {gross*1e4:>12.3f} {net1*1e4:>16.3f} {net2*1e4:>14.3f}")

# =============================================================================
# 7. SAVE RESULTS
# =============================================================================

print("\n" + "=" * 60)
print("SAVING RESULTS TO results/phase4/")
print("=" * 60)

def _save_summary(fitted_model, filepath):
    with open(filepath, 'w') as f:
        f.write(str(fitted_model.summary()))
    print(f"  Saved: {os.path.basename(filepath)}")

_save_summary(model,         os.path.join(RESULTS_DIR, 'primary_regression.txt'))
_save_summary(model_contemp, os.path.join(RESULTS_DIR, 'contemporaneous_regression.txt'))

for h, m in horizon_models.items():
    _save_summary(m, os.path.join(RESULTS_DIR, f'horizon_t{h}_regression.txt'))

for label, m in subsample_models.items():
    _save_summary(m, os.path.join(RESULTS_DIR, f'subsample_{label}_regression.txt'))

rows = []
def _add_rows(fitted_model, model_label):
    for var in ['const', 'tfi', 'regime_score', 'tfi_x_regime',
                'lag_return', 'lag_tfi']:
        if var not in fitted_model.params:
            continue
        rows.append({
            'model':     model_label,
            'variable':  var,
            'coeff':     fitted_model.params[var],
            't_stat':    fitted_model.tvalues[var],
            'p_value':   fitted_model.pvalues[var],
            'r_squared': fitted_model.rsquared,
            'n_obs':     int(fitted_model.nobs),
        })

_add_rows(model,         'primary_t1')
_add_rows(model_contemp, 'contemporaneous')
for h, m in horizon_models.items():
    _add_rows(m, f'horizon_t{h}')
for label, m in subsample_models.items():
    _add_rows(m, f'subsample_{label}')

coeff_df = pd.DataFrame(rows)
coeff_df.to_csv(os.path.join(RESULTS_DIR, 'key_coefficients.csv'),
                index=False, float_format='%.8f')
print(f"  Saved: key_coefficients.csv")

tc_path = os.path.join(RESULTS_DIR, 'transaction_cost_analysis.txt')
with open(tc_path, 'w') as f:
    f.write("TRANSACTION COST ANALYSIS\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Mean ES close price:          {mean_price:,.2f}\n")
    f.write(f"One-way cost (1 tick):        {one_tick_log*1e4:.4f} bps\n")
    f.write(f"Round-trip cost (2 ticks):    {round_trip_log*1e4:.4f} bps\n\n")
    f.write("CONTEMPORANEOUS (significant):\n")
    f.write(f"  beta_TFI:                   {b1_c:.8f}\n")
    f.write(f"  beta_interaction:           {b3_c:.8f}\n")
    f.write(f"  beta_TFI + beta_int:        {total_c:.8f}\n")
    if abs(total_c) > 1e-12:
        f.write(f"  Break-even TFI (1-way):    {tfi_be_1way:.6f}\n")
        f.write(f"  Break-even TFI (RT):       {tfi_be_rt:.6f}\n")
    f.write("\nT+1 (not significant, for completeness):\n")
    f.write(f"  beta_TFI:                   {b1_p:.8f}\n")
    f.write(f"  beta_interaction:           {b3_p:.8f}\n")
    f.write(f"  beta_TFI + beta_int:        {total_p:.8f}\n")
print(f"  Saved: transaction_cost_analysis.txt")

print("\n" + "=" * 60)
print("PHASE 4 ANALYSIS COMPLETE")
print("=" * 60)
