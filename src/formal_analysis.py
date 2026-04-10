import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_all_days, remove_outliers, compute_tfi, compute_returns
from signal_construction import (
    compute_lambda,
    compute_arrival_rate,
    compute_exclusion_mask,
    compute_regime_score,
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser(
    '~/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/'
)
OOS_DATA_DIR = os.path.expanduser(
    '~/Desktop/Quant Research Project/raw-data/GLBX-20260101-20260309/'
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

OOS_ANNOUNCEMENT_DATES = [
    # FOMC (2:00 PM ET)
    pd.Timestamp("2026-01-28 14:00", tz=TZ),
    pd.Timestamp("2026-03-18 14:00", tz=TZ),
    # CPI (8:30 AM ET)
    pd.Timestamp("2026-01-13 08:30", tz=TZ),
    pd.Timestamp("2026-02-11 08:30", tz=TZ),
    pd.Timestamp("2026-03-11 08:30", tz=TZ),
    # NFP (8:30 AM ET)
    pd.Timestamp("2026-01-09 08:30", tz=TZ),
    pd.Timestamp("2026-02-11 08:30", tz=TZ),
    pd.Timestamp("2026-03-06 08:30", tz=TZ),
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
arrival_series = compute_arrival_rate(df_clean)

df_indexed = df_clean.set_index('ts_event_et')
bars = df_indexed['price'].resample('1min').count()

ann_dates = ANNOUNCEMENT_DATES
if bars.index.tzinfo is None:
    ann_dates = [dt.tz_localize(None) for dt in ann_dates]

exclusion_mask = compute_exclusion_mask(bars, ann_dates)
regime_score   = compute_regime_score(
    lambda_series, arrival_series, exclusion_mask
)

tfi     = compute_tfi(df_clean)
returns = compute_returns(df_clean)

# ── Extract signed flow for lambda stability metric ───────────────────────────
df_indexed_full = df_clean.set_index('ts_event_et')
signed_flow_series = (
    df_indexed_full.groupby(pd.Grouper(freq='1min'))
    .apply(lambda x: float(x.loc[x['side'] == 'B', 'size'].sum())
                   - float(x.loc[x['side'] == 'A', 'size'].sum()))
    .rename('signed_flow')
)

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
reg['fwd_return']       = reg['log_return'].shift(-1)   # Return_{t+1}
reg['lag_return']       = reg['log_return']              # Return_t (control)
reg['lag_tfi']          = reg['tfi'].shift(1)            # TFI_{t-1} (control)
reg['tfi_x_regime']     = reg['tfi'] * reg['regime_score']
reg['regime_score_lag'] = reg['regime_score'].shift(1)   # RegimeScore_{t-1}
reg['tfi_x_regime_lag'] = reg['tfi'] * reg['regime_score_lag']

n_raw = len(reg)
print(f"    Bars before filters: {n_raw:,}")

# ── Drop NaN rows (rolling warmup + day boundaries + forward return edge) ─────
REGRESSION_COLS = ['fwd_return', 'tfi', 'regime_score',
                   'tfi_x_regime', 'regime_score_lag', 'tfi_x_regime_lag',
                   'lag_return', 'lag_tfi']
reg = reg.dropna(subset=REGRESSION_COLS)
n_final = len(reg)
print(f"    Dropped (NaN/warmup/boundaries): {n_raw - n_final:,}")
print(f"    Final regression N:              {n_final:,}")

# ── RegimeScore autocorrelation diagnostic ────────────────────────────────────
print("\n" + "=" * 60)
print("REGIME SCORE AUTOCORRELATION DIAGNOSTIC")
print("=" * 60)

rs_autocorr_lag1 = reg['regime_score'].autocorr(lag=1)
rs_autocorr_lag5 = reg['regime_score'].autocorr(lag=5)
rs_autocorr_lag30 = reg['regime_score'].autocorr(lag=30)

print(f"\n  RegimeScore autocorrelation:")
print(f"    Lag 1:  {rs_autocorr_lag1:.4f}")
print(f"    Lag 5:  {rs_autocorr_lag5:.4f}")
print(f"    Lag 30: {rs_autocorr_lag30:.4f}")
print(f"\n  Interpretation:")
print(f"    Lag-1 autocorr > 0.85 → lagging by 1 bar removes little")
print(f"    circularity; p=0.067 driven mainly by residual confounding")
print(f"    Lag-1 autocorr < 0.70 → meaningful circularity removed;")
print(f"    p=0.067 may reflect genuine predictive signal")

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
# STABLE REGIME CONDITIONS TEST
# =============================================================================

print("\n" + "=" * 60)
print("STABLE REGIME CONDITIONS TEST")
print("=" * 60)
print("  Rationale: lambda is most accurately estimated when the")
print("  30-bar rolling window contains stable, representative")
print("  signed flow — not dominated by a single price spike.")
print("  Bottom tercile of rolling signed-flow std = most stable")
print("  lambda estimation conditions.")

# Align signed flow to regression index
signed_flow_aligned = signed_flow_series.reindex(reg.index)

# Rolling std of signed flow over 30-bar window (same as lambda window)
# This measures how noisy the lambda estimation window was for each bar
reg['lambda_window_std'] = (
    signed_flow_aligned
    .rolling(30, min_periods=15)
    .std()
    .reindex(reg.index)
)

# Bottom tercile = most stable lambda conditions
stability_threshold = reg['lambda_window_std'].quantile(0.33)
reg_stable = reg[reg['lambda_window_std'] <= stability_threshold].copy()
reg_stable = reg_stable.dropna(subset=REGRESSION_COLS)

print(f"\n  Stability threshold (33rd pctile of lambda window std):")
print(f"    {stability_threshold:.2f} contracts signed flow std")
print(f"  Stable-condition bars: {len(reg_stable):,} "
      f"({len(reg_stable)/len(reg)*100:.1f}% of full sample)")
print(f"  High-regime in stable sample: "
      f"{(reg_stable['regime_score'] > 0.5).sum():,} "
      f"({(reg_stable['regime_score'] > 0.5).mean()*100:.1f}%)")

# Check time-of-day distribution of stable bars
# If stable bars concentrate in midday, this confirms the time-based
# intuition and shows the stability criterion captures the same thing
stable_hour_dist = reg_stable.index.hour.value_counts().sort_index()
print(f"\n  Hour distribution of stable bars (should peak at midday):")
for h, n in stable_hour_dist.items():
    pct = n / len(reg_stable) * 100
    bar = '█' * int(pct / 1.5)
    print(f"    {h:02d}:xx  {n:5,} ({pct:4.1f}%) {bar}")

# Run primary regression on stable-condition bars only
y_stable = reg_stable['fwd_return']
X_stable = sm.add_constant(reg_stable[['tfi', 'regime_score',
                                        'tfi_x_regime',
                                        'lag_return', 'lag_tfi']])
model_stable = sm.OLS(y_stable, X_stable).fit(
    cov_type='HAC', cov_kwds={'maxlags': 5}
)

print(f"\n  Stable-condition primary regression | N={int(model_stable.nobs):,}")
print(f"    β₃ (tfi_x_regime): {model_stable.params['tfi_x_regime']:.6f}")
print(f"    z-stat:            {model_stable.tvalues['tfi_x_regime']:.3f}")
print(f"    p-value:           {model_stable.pvalues['tfi_x_regime']:.4f}")
print(f"    β₁ (tfi):          {model_stable.params['tfi']:.6f}")
print(f"    R²:                {model_stable.rsquared:.6f}")

print(f"\n  Comparison (full sample β₃ = {model.params['tfi_x_regime']:.6f}, "
      f"p = {model.pvalues['tfi_x_regime']:.4f}):")
if model_stable.pvalues['tfi_x_regime'] < model.pvalues['tfi_x_regime']:
    print(f"  → Stable conditions produce lower p-value: CONSISTENT with")
    print(f"    hypothesis that regime detector is more accurate when lambda")
    print(f"    estimation is stable.")
else:
    print(f"  → Stable conditions do NOT produce lower p-value: NOT consistent")
    print(f"    with hypothesis.")

# Also run on top tercile (most unstable) for comparison
stability_threshold_67 = reg['lambda_window_std'].quantile(0.67)
reg_unstable = reg[reg['lambda_window_std'] > stability_threshold_67].copy()
reg_unstable = reg_unstable.dropna(subset=REGRESSION_COLS)

y_unstable = reg_unstable['fwd_return']
X_unstable = sm.add_constant(reg_unstable[['tfi', 'regime_score',
                                            'tfi_x_regime',
                                            'lag_return', 'lag_tfi']])
model_unstable = sm.OLS(y_unstable, X_unstable).fit(
    cov_type='HAC', cov_kwds={'maxlags': 5}
)

print(f"\n  Unstable-condition (top tercile) | N={int(model_unstable.nobs):,}")
print(f"    β₃ (tfi_x_regime): {model_unstable.params['tfi_x_regime']:.6f}")
print(f"    p-value:           {model_unstable.pvalues['tfi_x_regime']:.4f}")
print(f"\n  If stable β₃ > unstable β₃ and stable p < unstable p,")
print(f"  the gradient supports the regime detector quality hypothesis.")

# =============================================================================
# 3. CONTEMPORANEOUS SECONDARY REGRESSION
# =============================================================================

print("\n" + "=" * 60)
print("CONTEMPORANEOUS REGRESSION — Return_t (lagged RegimeScore)")
print("=" * 60)

y_contemp = reg['lag_return']
X_contemp = sm.add_constant(reg[['tfi', 'regime_score_lag', 'tfi_x_regime_lag',
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
# 6. OUT-OF-SAMPLE VALIDATION (2026-01 to 2026-03)
# =============================================================================

print("\n" + "=" * 60)
print("OUT-OF-SAMPLE VALIDATION — 2026 Jan–Mar")
print("=" * 60)

print("\n  [OOS-1] Loading OOS data...")
df_oos       = load_all_days(OOS_DATA_DIR)
df_oos_clean = remove_outliers(df_oos)
print(f"    Loaded {len(df_oos_clean):,} clean RTH trades across "
      f"{df_oos_clean['ts_event_et'].dt.date.nunique()} trading days")

print("  [OOS-2] Computing signals...")
lambda_oos  = compute_lambda(df_oos_clean)
arrival_oos = compute_arrival_rate(df_oos_clean)

df_oos_indexed = df_oos_clean.set_index('ts_event_et')
bars_oos = df_oos_indexed['price'].resample('1min').count()

ann_dates_oos = OOS_ANNOUNCEMENT_DATES
if bars_oos.index.tzinfo is None:
    ann_dates_oos = [dt.tz_localize(None) for dt in ann_dates_oos]

exclusion_mask_oos = compute_exclusion_mask(bars_oos, ann_dates_oos)
regime_score_oos   = compute_regime_score(
    lambda_oos, arrival_oos, exclusion_mask_oos
)

tfi_oos     = compute_tfi(df_oos_clean)
returns_oos = compute_returns(df_oos_clean)

tfi_oos_series = tfi_oos['tfi'] if isinstance(tfi_oos, pd.DataFrame) else tfi_oos
ret_oos_series = (returns_oos['log_return']
                  if isinstance(returns_oos, pd.DataFrame) else returns_oos)

reg_oos = pd.DataFrame({
    'tfi':          tfi_oos_series,
    'log_return':   ret_oos_series,
    'regime_score': regime_score_oos,
})

# Null out first bar of each day — overnight gap is not an RTH return
reg_oos_dates = pd.Series(reg_oos.index.date, index=reg_oos.index)
first_bar_oos = reg_oos_dates != reg_oos_dates.shift(1)
reg_oos.loc[first_bar_oos, 'log_return'] = np.nan

reg_oos['fwd_return']       = reg_oos['log_return'].shift(-1)
reg_oos['lag_return']       = reg_oos['log_return']
reg_oos['lag_tfi']          = reg_oos['tfi'].shift(1)
reg_oos['tfi_x_regime']     = reg_oos['tfi'] * reg_oos['regime_score']
reg_oos['regime_score_lag'] = reg_oos['regime_score'].shift(1)
reg_oos['tfi_x_regime_lag'] = reg_oos['tfi'] * reg_oos['regime_score_lag']

reg_oos = reg_oos.dropna(subset=REGRESSION_COLS)
print(f"    OOS regression N: {len(reg_oos):,}")
print(f"    OOS date range:   {reg_oos.index.min()} → {reg_oos.index.max()}")

# Primary specification, no refitting — apply in-sample spec to OOS data
y_oos = reg_oos['fwd_return']
X_oos = sm.add_constant(reg_oos[['tfi', 'regime_score', 'tfi_x_regime',
                                   'lag_return', 'lag_tfi']])
model_oos = sm.OLS(y_oos, X_oos).fit(cov_type='HAC', cov_kwds={'maxlags': 5})

print(f"\n  OOS Primary (Return_{{t+1}}) | N={int(model_oos.nobs):,}")
print(f"    β₃ (tfi_x_regime): {model_oos.params['tfi_x_regime']:.6f}")
print(f"    p-value:           {model_oos.pvalues['tfi_x_regime']:.4f}")
print(f"    z-stat:            {model_oos.tvalues['tfi_x_regime']:.3f}")

# =============================================================================
# OOS DIAGNOSTIC TESTS
# =============================================================================

print("\n" + "=" * 60)
print("OOS DIAGNOSTIC TESTS — Investigating p=0.004 significance")
print("=" * 60)

# ── Diagnostic 1: Residual autocorrelation beyond maxlags=5 ──────────────────
print("\n--- Diagnostic 1: OOS Residual Autocorrelation ---")
print("  Tests whether HAC maxlags=5 was sufficient for OOS period.")
print("  If residuals autocorrelated beyond lag 5, standard errors")
print("  are underestimated and z-stat is inflated.")

for lag in range(1, 11):
    ac = model_oos.resid.autocorr(lag=lag)
    flag = ' ← beyond maxlags' if lag > 5 else ''
    print(f"    Lag {lag:2d}: {ac:+.4f}{flag}")

# ── Diagnostic 2: RegimeScore distribution comparison OOS vs in-sample ────────
print("\n--- Diagnostic 2: RegimeScore Distribution Comparison ---")
print("  Tests whether OOS period is drawn from the same regime")
print("  distribution as the in-sample period.")

is_stats = reg['regime_score'].describe()
oos_stats = reg_oos['regime_score'].describe()

print(f"\n  {'Metric':<20} {'In-sample':>12} {'OOS':>12} {'Difference':>12}")
print(f"  {'-'*58}")
for metric in ['mean', 'std', '25%', '50%', '75%']:
    diff = oos_stats[metric] - is_stats[metric]
    print(f"  {metric:<20} {is_stats[metric]:>12.4f} "
          f"{oos_stats[metric]:>12.4f} {diff:>+12.4f}")

is_high_pct = (reg['regime_score'] > 0.5).mean()
oos_high_pct = (reg_oos['regime_score'] > 0.5).mean()
print(f"\n  Fraction high-regime (>0.5):")
print(f"    In-sample: {is_high_pct:.4f} ({is_high_pct*100:.1f}%)")
print(f"    OOS:       {oos_high_pct:.4f} ({oos_high_pct*100:.1f}%)")
print(f"    Difference: {(oos_high_pct - is_high_pct):+.4f}")

# ── Diagnostic 3: Realized volatility comparison ──────────────────────────────
print("\n--- Diagnostic 3: Realized Volatility Comparison ---")
print("  Tests whether elevated OOS volatility inflates lambda and")
print("  RegimeScore mechanically, producing spurious interaction.")

is_vol = reg['lag_return'].std()
oos_vol = reg_oos['lag_return'].std()
is_vol_ann = is_vol * np.sqrt(390 * 169)
oos_vol_ann = oos_vol * np.sqrt(390 * 46)

print(f"\n  1-minute return std:")
print(f"    In-sample: {is_vol:.6f} ({is_vol*1e4:.3f} bps per bar)")
print(f"    OOS:       {oos_vol:.6f} ({oos_vol*1e4:.3f} bps per bar)")
print(f"    Ratio (OOS/IS): {oos_vol/is_vol:.3f}x")

# Compare lambda distributions
is_lambda_mean = reg['regime_score'].mean()
oos_lambda_mean = reg_oos['regime_score'].mean()
print(f"\n  Mean RegimeScore (proxy for average lambda level):")
print(f"    In-sample: {is_lambda_mean:.4f}")
print(f"    OOS:       {oos_lambda_mean:.4f}")
print(f"    Ratio:     {oos_lambda_mean/is_lambda_mean:.3f}x")

# ── Diagnostic 4: OOS result by month ─────────────────────────────────────────
print("\n--- Diagnostic 4: OOS Result by Month ---")
print("  Tests whether significance is driven by a specific month.")

oos_months = {
    'January 2026':  (pd.Timestamp('2026-01-01').date(),
                      pd.Timestamp('2026-01-31').date()),
    'February 2026': (pd.Timestamp('2026-02-01').date(),
                      pd.Timestamp('2026-02-28').date()),
}

for month_label, (start, end) in oos_months.items():
    oos_dates = pd.Series(reg_oos.index.date, index=reg_oos.index)
    reg_month = reg_oos[(oos_dates >= start) & (oos_dates <= end)]
    reg_month = reg_month.dropna(subset=REGRESSION_COLS)

    if len(reg_month) < 200:
        print(f"\n  {month_label}: N={len(reg_month)} — too few obs, skipping")
        continue

    y_m = reg_month['fwd_return']
    X_m = sm.add_constant(reg_month[['tfi', 'regime_score',
                                      'tfi_x_regime',
                                      'lag_return', 'lag_tfi']])
    model_m = sm.OLS(y_m, X_m).fit(cov_type='HAC', cov_kwds={'maxlags': 5})

    print(f"\n  {month_label} | N={int(model_m.nobs):,}")
    print(f"    β₃ (tfi_x_regime): {model_m.params['tfi_x_regime']:.6f}")
    print(f"    z-stat:            {model_m.tvalues['tfi_x_regime']:.3f}")
    print(f"    p-value:           {model_m.pvalues['tfi_x_regime']:.4f}")

# Note: March 2026 only has ~3-6 trading days in OOS — skip
print(f"\n  Note: March 2026 has only ~3 trading days in OOS window,")
print(f"  insufficient for separate regression.")

# ── Diagnostic 5: Rolling weekly β₃ across OOS period ─────────────────────────
print("\n--- Diagnostic 5: Rolling Weekly β₃ Across OOS Period ---")
print("  Tests whether significance is concentrated in specific")
print("  episodes or stable across the OOS period.")

oos_dates_series = pd.Series(reg_oos.index.date, index=reg_oos.index)
oos_unique_dates = sorted(oos_dates_series.unique())
window_size = 10  # 2-week rolling window (10 trading days)

print(f"\n  Rolling {window_size}-day window β₃ estimates:")
print(f"  {'Window end':<15} {'N':>6} {'β₃':>12} {'p-value':>10}")
print(f"  {'-'*47}")

rolling_results = []
for i in range(window_size - 1, len(oos_unique_dates)):
    window_start = oos_unique_dates[i - window_size + 1]
    window_end   = oos_unique_dates[i]
    mask = ((oos_dates_series >= window_start) &
            (oos_dates_series <= window_end))
    reg_win = reg_oos[mask].dropna(subset=REGRESSION_COLS)

    if len(reg_win) < 150:
        continue

    y_w = reg_win['fwd_return']
    X_w = sm.add_constant(reg_win[['tfi', 'regime_score',
                                    'tfi_x_regime',
                                    'lag_return', 'lag_tfi']])
    try:
        model_w = sm.OLS(y_w, X_w).fit(
            cov_type='HAC', cov_kwds={'maxlags': 5}
        )
        b3 = model_w.params['tfi_x_regime']
        pv = model_w.pvalues['tfi_x_regime']
        rolling_results.append((window_end, len(reg_win), b3, pv))
        sig = '***' if pv < 0.01 else '**' if pv < 0.05 else ''
        print(f"  {str(window_end):<15} {len(reg_win):>6,} "
              f"{b3:>12.6f} {pv:>10.4f} {sig}")
    except Exception:
        continue

if rolling_results:
    b3_vals = [r[2] for r in rolling_results]
    pv_vals = [r[3] for r in rolling_results]
    n_sig = sum(1 for p in pv_vals if p < 0.05)
    print(f"\n  Summary:")
    print(f"    Windows tested: {len(rolling_results)}")
    print(f"    Windows significant (p<0.05): {n_sig}")
    print(f"    β₃ range: [{min(b3_vals):.6f}, {max(b3_vals):.6f}]")
    print(f"    If significance concentrated in 1-2 windows: episodic")
    print(f"    If significant across most windows: more structural")

# ── Diagnostic 6: OOS TFI distribution comparison ─────────────────────────────
print("\n--- Diagnostic 6: OOS TFI Distribution Comparison ---")
print("  Tests whether OOS period had more extreme TFI values.")
print("  Extreme TFI + circularity → mechanically larger β₃.")

is_tfi_stats = reg['tfi'].describe()
oos_tfi_stats = reg_oos['tfi'].describe()

print(f"\n  {'Metric':<20} {'In-sample':>12} {'OOS':>12} {'Difference':>12}")
print(f"  {'-'*58}")
for metric in ['mean', 'std', '25%', '50%', '75%', 'max']:
    diff = oos_tfi_stats[metric] - is_tfi_stats[metric]
    print(f"  {metric:<20} {is_tfi_stats[metric]:>12.4f} "
          f"{oos_tfi_stats[metric]:>12.4f} {diff:>+12.4f}")

is_extreme = (reg['tfi'].abs() > 0.3).mean()
oos_extreme = (reg_oos['tfi'].abs() > 0.3).mean()
print(f"\n  Fraction of bars with |TFI| > 0.3 (extreme imbalance):")
print(f"    In-sample: {is_extreme:.4f} ({is_extreme*100:.1f}%)")
print(f"    OOS:       {oos_extreme:.4f} ({oos_extreme*100:.1f}%)")
if oos_extreme > is_extreme * 1.1:
    print(f"  → OOS has more extreme TFI: consistent with mechanical")
    print(f"    inflation hypothesis via circularity.")
else:
    print(f"  → OOS TFI distribution similar to in-sample.")

# ── Diagnostic 7: Permutation test ────────────────────────────────────────────
print("\n--- Diagnostic 7: Permutation Test (N=1000) ---")
print("  Tests whether OOS β₃ is in the tail of the null distribution.")
print("  Running 1000 permutations of fwd_return in OOS sample...")

np.random.seed(42)
n_permutations = 1000
perm_b3 = []

y_oos_vals = reg_oos['fwd_return'].values.copy()
X_oos_vals = sm.add_constant(
    reg_oos[['tfi', 'regime_score', 'tfi_x_regime',
              'lag_return', 'lag_tfi']]
).values

for _ in range(n_permutations):
    y_perm = np.random.permutation(y_oos_vals)
    try:
        b = np.linalg.lstsq(X_oos_vals, y_perm, rcond=None)[0]
        perm_b3.append(b[3])  # index 3 = tfi_x_regime after const
    except Exception:
        continue

perm_b3 = np.array(perm_b3)
actual_b3 = model_oos.params['tfi_x_regime']
perm_pvalue = (perm_b3 >= actual_b3).mean()

print(f"\n  Actual OOS β₃: {actual_b3:.6f}")
print(f"  Permutation null β₃: mean={perm_b3.mean():.6f}, "
      f"std={perm_b3.std():.6f}")
print(f"  Permutation p-value (fraction ≥ actual): {perm_pvalue:.4f}")
print(f"  Parametric HAC p-value:                  "
      f"{model_oos.pvalues['tfi_x_regime']:.4f}")
if perm_pvalue < 0.05:
    print(f"  → Actual β₃ is in the top {perm_pvalue*100:.1f}% of the")
    print(f"    permutation distribution. Result is NOT purely spurious.")
else:
    print(f"  → Actual β₃ is NOT in the tail of the permutation")
    print(f"    distribution. Result may be spurious or driven by")
    print(f"    serial dependence not captured by simple permutation.")
print(f"\n  Note: permutation test breaks time series dependence.")
print(f"  A non-significant permutation p-value may reflect serial")
print(f"  correlation rather than a false positive. Compare with")
print(f"  HAC p-value and rolling window results for full picture.")

# =============================================================================
# OOS LAMBDA LEVEL COMPARISON
# =============================================================================

print("\n" + "=" * 60)
print("OOS LAMBDA LEVEL COMPARISON")
print("=" * 60)
print("  Tests whether OOS lambda was structurally elevated,")
print("  mechanically inflating RegimeScore and β₃ via circularity.")

# Recompute lambda stats for OOS reg_oos already built
# regime_score serves as proxy since lambda is the dominant component
is_rs_mean = reg['regime_score'].mean()
oos_rs_mean = reg_oos['regime_score'].mean()
is_rs_p75 = reg['regime_score'].quantile(0.75)
oos_rs_p75 = reg_oos['regime_score'].quantile(0.75)
is_rs_p90 = reg['regime_score'].quantile(0.90)
oos_rs_p90 = reg_oos['regime_score'].quantile(0.90)

print(f"\n  RegimeScore percentile comparison:")
print(f"  {'Percentile':<15} {'In-sample':>12} {'OOS':>12} {'OOS/IS ratio':>14}")
print(f"  {'-'*55}")
for label, is_val, oos_val in [
    ('Mean', is_rs_mean, oos_rs_mean),
    ('75th', is_rs_p75, oos_rs_p75),
    ('90th', is_rs_p90, oos_rs_p90),
]:
    ratio = oos_val / is_val if is_val > 0 else float('nan')
    print(f"  {label:<15} {is_val:>12.4f} {oos_val:>12.4f} {ratio:>14.3f}x")

print(f"\n  If OOS mean RegimeScore is materially higher (>1.1x),")
print(f"  lambda-inflation is a plausible contributor to OOS significance.")

# =============================================================================
# 7. LAGGED REGIME CONDITIONING (RegimeScore_{t-1} on T+1)
# =============================================================================

print("\n" + "=" * 60)
print("LAGGED REGIME CONDITIONING — RegimeScore_{t-1} on Return_{t+1}")
print("=" * 60)

# regime_score_lag and tfi_x_regime_lag are already in REGRESSION_COLS dropna,
# so reg already has non-NaN values for these columns. reg_lag == reg here.
reg_lag = reg

y_lag = reg_lag['fwd_return']
X_lag = sm.add_constant(reg_lag[['tfi', 'regime_score_lag', 'tfi_x_regime_lag',
                                   'lag_return', 'lag_tfi']])
model_lag = sm.OLS(y_lag, X_lag).fit(cov_type='HAC', cov_kwds={'maxlags': 5})

print(f"\n  Lagged-regime Primary | N={int(model_lag.nobs):,}")
print(f"    β₃ (tfi_x_regime_lag): {model_lag.params['tfi_x_regime_lag']:.6f}")
print(f"    p-value:               {model_lag.pvalues['tfi_x_regime_lag']:.4f}")
print(f"    z-stat:                {model_lag.tvalues['tfi_x_regime_lag']:.3f}")

# =============================================================================
# 8. MIDDAY SUBSAMPLE (11:00–13:00 ET)
# =============================================================================

print("\n" + "=" * 60)
print("MIDDAY SUBSAMPLE — 11:00–13:00 ET (hour ∈ {11, 12})")
print("=" * 60)

reg_midday = reg[reg.index.hour.isin([11, 12])]
reg_midday = reg_midday.dropna(subset=REGRESSION_COLS)

y_mid = reg_midday['fwd_return']
X_mid = sm.add_constant(reg_midday[['tfi', 'regime_score', 'tfi_x_regime',
                                      'lag_return', 'lag_tfi']])
model_midday = sm.OLS(y_mid, X_mid).fit(cov_type='HAC', cov_kwds={'maxlags': 5})

print(f"\n  Midday Primary (Return_{{t+1}}) | N={int(model_midday.nobs):,}")
print(f"    β₃ (tfi_x_regime): {model_midday.params['tfi_x_regime']:.6f}")
print(f"    p-value:           {model_midday.pvalues['tfi_x_regime']:.4f}")
print(f"    z-stat:            {model_midday.tvalues['tfi_x_regime']:.3f}")

# =============================================================================
# 9. TFI QUINTILE INTERACTION (Bonferroni-corrected)
# =============================================================================

print("\n" + "=" * 60)
print("TFI QUINTILE INTERACTION — Bonferroni α = 0.01 (5 tests)")
print("=" * 60)

reg['tfi_quintile'] = pd.qcut(reg['tfi'], q=5, labels=[1, 2, 3, 4, 5])
quintile_dummy_cols = []
for q in [1, 2, 4, 5]:
    col = f'tfi_q{q}_x_regime'
    reg[col] = (reg['tfi_quintile'] == q).astype(float) * reg['regime_score']
    quintile_dummy_cols.append(col)

# Replace single tfi_x_regime term with the four quintile dummy interactions.
# Quintile 3 is the omitted reference category.
y_q = reg['fwd_return']
X_q = sm.add_constant(reg[['tfi', 'regime_score'] + quintile_dummy_cols +
                          ['lag_return', 'lag_tfi']])
model_quintile = sm.OLS(y_q, X_q).fit(cov_type='HAC', cov_kwds={'maxlags': 5})

BONFERRONI_ALPHA = 0.05 / 5  # = 0.01, family-wise α = 0.05 across 5 tests
print(f"\n  Quintile Interaction | N={int(model_quintile.nobs):,}")
print(f"  (omitted reference: q3)")
print(f"  {'Term':<22} {'Coeff':>12} {'z-stat':>8} {'p-value':>10} "
      f"{'Bonferroni':>12}")
print(f"  {'-'*68}")
for col in quintile_dummy_cols:
    c = model_quintile.params[col]
    t = model_quintile.tvalues[col]
    p = model_quintile.pvalues[col]
    survives = 'SURVIVES' if p < BONFERRONI_ALPHA else '—'
    print(f"  {col:<22} {c:>12.6f} {t:>8.3f} {p:>10.4f} {survives:>12}")
print(f"\n  Bonferroni threshold (α/5): {BONFERRONI_ALPHA:.4f}")
surviving = [c for c in quintile_dummy_cols
             if model_quintile.pvalues[c] < BONFERRONI_ALPHA]
if surviving:
    print(f"  Quintiles surviving correction: {', '.join(surviving)}")
else:
    print(f"  No quintile interactions survive Bonferroni correction.")

# =============================================================================
# 10. REGIME TRANSITION DYNAMICS
# =============================================================================

print("\n" + "=" * 60)
print("REGIME TRANSITION DYNAMICS — sustained vs transition effects")
print("=" * 60)

# Reindex exclusion_mask to reg.index (reg has NaN-dropped rows).
# fillna(False) treats unmatched bars as not-excluded rather than NaN.
exclusion_mask_reg = exclusion_mask.reindex(reg.index).fillna(False).astype(bool)
prior_excluded = exclusion_mask_reg.shift(1).fillna(False).astype(bool)

high = (reg['regime_score'] > 0.5).astype(int)
# Transition flag: high now, low prior bar, AND prior bar not masked out by
# exclusion window (else exiting an exclusion would spuriously register as a
# transition, since RegimeScore is forced to 0 inside exclusions).
reg['transition_to_high'] = (
    (high == 1) & (high.shift(1) == 0) & (~prior_excluded)
).astype(float)
reg['tfi_x_transition'] = reg['tfi'] * reg['transition_to_high']

y_tr = reg['fwd_return']
X_tr = sm.add_constant(reg[['tfi', 'regime_score', 'tfi_x_regime',
                              'tfi_x_transition', 'lag_return', 'lag_tfi']])
model_transition = sm.OLS(y_tr, X_tr).fit(
    cov_type='HAC', cov_kwds={'maxlags': 5}
)

n_transitions = int(reg['transition_to_high'].sum())
print(f"\n  Transition Dynamics | N={int(model_transition.nobs):,} "
      f"({n_transitions:,} transition bars)")
print(f"    Sustained β₃ (tfi_x_regime):      "
      f"{model_transition.params['tfi_x_regime']:.6f}  "
      f"p={model_transition.pvalues['tfi_x_regime']:.4f}")
print(f"    Transition β (tfi_x_transition):  "
      f"{model_transition.params['tfi_x_transition']:.6f}  "
      f"p={model_transition.pvalues['tfi_x_transition']:.4f}")

# =============================================================================
# TRANSITION DYNAMICS — DELTA MAGNITUDE DIAGNOSTIC
# =============================================================================

print("\n" + "=" * 60)
print("TRANSITION DYNAMICS — DELTA MAGNITUDE DIAGNOSTIC")
print("=" * 60)
print("  Tests whether transition β₄ varies with the size of the")
print("  RegimeScore delta at transition.")
print("  Under CIRCULARITY: larger delta → larger mechanical inflation")
print("    → stronger transition coefficient.")
print("  Under GENUINE SIGNAL: effect should be consistent regardless")
print("    of delta magnitude — informed traders do not front-run")
print("    only large-delta transitions.")

# Compute delta at each transition bar
reg['regime_score_prev'] = reg['regime_score'].shift(1)
reg['transition_delta'] = np.where(
    reg['transition_to_high'] == 1,
    reg['regime_score'] - reg['regime_score_prev'],
    np.nan
)

transition_bars = reg[reg['transition_to_high'] == 1].copy()
transition_bars = transition_bars.dropna(subset=['transition_delta'])

if len(transition_bars) < 50:
    print(f"  Insufficient transition bars ({len(transition_bars)}) for")
    print(f"  delta analysis. Skipping.")
else:
    print(f"\n  Total transition bars: {len(transition_bars):,}")
    print(f"  Delta distribution:")
    print(f"    Mean:   {transition_bars['transition_delta'].mean():.4f}")
    print(f"    Median: {transition_bars['transition_delta'].median():.4f}")
    print(f"    Std:    {transition_bars['transition_delta'].std():.4f}")
    print(f"    Min:    {transition_bars['transition_delta'].min():.4f}")
    print(f"    Max:    {transition_bars['transition_delta'].max():.4f}")

    # Split transitions into small delta (bottom half) and
    # large delta (top half) using median split
    delta_median = transition_bars['transition_delta'].median()

    for delta_label, delta_condition in [
        ('Small delta (below median)', transition_bars['transition_delta'] <= delta_median),
        ('Large delta (above median)', transition_bars['transition_delta'] > delta_median),
    ]:
        small_idx = transition_bars[delta_condition].index
        reg_delta = reg.copy()
        reg_delta['transition_to_high_split'] = 0
        reg_delta.loc[reg_delta.index.isin(small_idx),
                      'transition_to_high_split'] = 1
        reg_delta['tfi_x_transition_split'] = (
            reg_delta['tfi'] * reg_delta['transition_to_high_split']
        )

        n_trans = int(reg_delta['transition_to_high_split'].sum())
        if n_trans < 30:
            print(f"\n  {delta_label}: only {n_trans} bars, skipping.")
            continue

        y_d = reg_delta['fwd_return']
        X_d = sm.add_constant(reg_delta[['tfi', 'regime_score',
                                          'tfi_x_regime',
                                          'tfi_x_transition_split',
                                          'lag_return', 'lag_tfi']])
        X_d = X_d.dropna()
        y_d = y_d.reindex(X_d.index)

        model_d = sm.OLS(y_d, X_d).fit(
            cov_type='HAC', cov_kwds={'maxlags': 5}
        )
        b_trans = model_d.params['tfi_x_transition_split']
        p_trans = model_d.pvalues['tfi_x_transition_split']
        print(f"\n  {delta_label} | N transitions={n_trans}")
        print(f"    Transition β: {b_trans:.6f}  p={p_trans:.4f}")

    print(f"\n  Interpretation:")
    print(f"    If large-delta β >> small-delta β: circularity likely")
    print(f"    If large-delta β ≈ small-delta β: genuine signal more likely")

# =============================================================================
# TRANSITION THRESHOLD ROBUSTNESS — 0.4 and 0.6
# =============================================================================

print("\n" + "=" * 60)
print("TRANSITION THRESHOLD ROBUSTNESS — 0.4 and 0.6")
print("=" * 60)
print("  Tests whether transition dynamics finding (p=0.018 at")
print("  threshold=0.5) is stable across alternative thresholds.")
print("  If result concentrates only at 0.5: likely threshold artifact.")
print("  If result stable across 0.4/0.5/0.6: more robust finding.")

for threshold in [0.4, 0.6]:
    exclusion_mask_reg_thresh = (
        exclusion_mask.reindex(reg.index).fillna(False).astype(bool)
    )
    prior_excluded_thresh = (
        exclusion_mask_reg_thresh.shift(1).fillna(False).astype(bool)
    )

    high_thresh = (reg['regime_score'] > threshold).astype(int)
    reg[f'transition_to_high_{threshold}'] = (
        (high_thresh == 1) &
        (high_thresh.shift(1) == 0) &
        (~prior_excluded_thresh)
    ).astype(float)
    reg[f'tfi_x_transition_{threshold}'] = (
        reg['tfi'] * reg[f'transition_to_high_{threshold}']
    )

    n_trans = int(reg[f'transition_to_high_{threshold}'].sum())

    y_tr = reg['fwd_return']
    X_tr = sm.add_constant(
        reg[['tfi', 'regime_score', 'tfi_x_regime',
              f'tfi_x_transition_{threshold}',
              'lag_return', 'lag_tfi']]
    )
    model_tr = sm.OLS(y_tr, X_tr).fit(
        cov_type='HAC', cov_kwds={'maxlags': 5}
    )

    b_sus  = model_tr.params['tfi_x_regime']
    p_sus  = model_tr.pvalues['tfi_x_regime']
    b_trans = model_tr.params[f'tfi_x_transition_{threshold}']
    p_trans = model_tr.pvalues[f'tfi_x_transition_{threshold}']

    print(f"\n  Threshold = {threshold} | Transition bars: {n_trans:,}")
    print(f"    Sustained β₃ (tfi_x_regime):          "
          f"{b_sus:.6f}  p={p_sus:.4f}")
    print(f"    Transition β (tfi_x_transition):       "
          f"{b_trans:.6f}  p={p_trans:.4f}")

print(f"  Reference: threshold=0.5 | "
      f"Transition bars: {n_transitions:,}")
print(f"    Sustained β₃: "
      f"{model_transition.params['tfi_x_regime']:.6f}  "
      f"p={model_transition.pvalues['tfi_x_regime']:.4f}")
print(f"    Transition β: "
      f"{model_transition.params['tfi_x_transition']:.6f}  "
      f"p={model_transition.pvalues['tfi_x_transition']:.4f}")
print(f"\n  Interpretation:")
print(f"    Consistent transition significance across thresholds")
print(f"    → finding is robust, not a 0.5-threshold artifact.")
print(f"    Significance only at 0.5 → likely threshold-specific.")

# =============================================================================
# 11. TRANSACTION COST ANALYSIS
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

# ── Contemporaneous spec ─────────────────────────────────────────────
a_c  = model_contemp.params['const']
b1_c = model_contemp.params['tfi']
b2_c = model_contemp.params['regime_score_lag']
b3_c = model_contemp.params['tfi_x_regime_lag']
b5_c = model_contemp.params['lag_tfi']
total_c = b1_c + b3_c
p_contemp = model_contemp.pvalues['tfi_x_regime_lag']

print(f"\n  --- Contemporaneous regression ---")
print(f"  (tfi_x_regime_lag: β₃={b3_c:.6f}, p={p_contemp:.4f})")

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

# ── T+1 spec ─────────────────────────────────────────────────────────
a_p  = model.params['const']
b1_p = model.params['tfi']
b2_p = model.params['regime_score']
b3_p = model.params['tfi_x_regime']
b4_p = model.params['lag_return']
b5_p = model.params['lag_tfi']
total_p = b1_p + b3_p
p_primary = model.pvalues['tfi_x_regime']

print(f"\n  --- T+1 regression ---")
print(f"  (tfi_x_regime: β₃={b3_p:.6f}, p={p_primary:.4f})")

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
# 12. SAVE RESULTS
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
_save_summary(model_oos,        os.path.join(RESULTS_DIR, 'oos_primary_regression.txt'))
_save_summary(model_lag,        os.path.join(RESULTS_DIR, 'lagged_regime_regression.txt'))
_save_summary(model_midday,     os.path.join(RESULTS_DIR, 'midday_regression.txt'))
_save_summary(model_quintile,   os.path.join(RESULTS_DIR, 'quintile_interaction_regression.txt'))
_save_summary(model_transition, os.path.join(RESULTS_DIR, 'transition_dynamics_regression.txt'))

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

_add_rows(model_oos,        'oos_primary_t1')
_add_rows(model_lag,        'lagged_regime_t1')
_add_rows(model_midday,     'midday_t1')
_add_rows(model_transition, 'transition_dynamics')

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
