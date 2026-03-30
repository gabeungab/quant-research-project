import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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

INDIVIDUAL_DAYS = {
    'high_vol':     pd.Timestamp('2025-06-13', tz='America/New_York'),
    'low_vol':      pd.Timestamp('2025-07-25', tz='America/New_York'),
    'announcement': pd.Timestamp('2025-07-30', tz='America/New_York'),
    'normal':       pd.Timestamp('2025-08-13', tz='America/New_York'),
}

_DAY_LABELS = {
    'high_vol':     'High Volatility (2025-06-13)',
    'low_vol':      'Low Volatility (2025-07-25)',
    'announcement': 'FOMC Announcement (2025-07-30)',
    'normal':       'Normal Day (2025-08-13)',
}

_RTH_OPEN  = pd.Timestamp('09:30').time()
_RTH_CLOSE = pd.Timestamp('16:00').time()


def _plot_component(series, name, filename_prefix, save_dir,
                    daily_agg='mean', dist_filter='none',
                    ts_filter='none'):
    """
    Four-panel plot for a 1-minute bar Series: daily time series,
    intraday average, distribution, and individual days.
    Saves each panel as a separate PNG.

    Parameters
    ----------
    daily_agg : str
        Aggregation for the daily time series panel — 'mean' or 'max'.
    dist_filter : str
        Filter applied to distribution values after RTH and NaN removal.
        'none'     — no additional filter (use for lambda).
        'positive' — keep only values > 0 (use for Roll, arrival,
                     RegimeScore where zeros are artifacts).
    """
    os.makedirs(save_dir, exist_ok=True)

    # ── 1. Full sample time series (resampled to daily, trading days only) ────
    daily_series = getattr(series.dropna().resample('1D'), daily_agg)()
    daily_series = daily_series[daily_series.notna()]
    if ts_filter == 'positive':
        daily_series = daily_series[daily_series > 0]

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(daily_series.index, daily_series.values, linewidth=1.2)
    ax.set_title(f'{name} — Daily {daily_agg.capitalize()} Across Sample')
    ax.set_xlabel('Date')
    ax.set_ylabel(name)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.tight_layout()
    fig.savefig(f'{save_dir}/{filename_prefix}_timeseries.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {filename_prefix}_timeseries.png")

    # ── 2. Intraday average ───────────────────────────────────────────────────
    rth_mask = (
        (series.index.time >= _RTH_OPEN) &
        (series.index.time <= _RTH_CLOSE)
    )
    rth = series[rth_mask].dropna()
    intraday_avg = rth.groupby(rth.index.time).mean()

    n = len(intraday_avg)
    tick_positions = [0, 60, 120, 180, 240, 300, min(350, n-41), min(390, n-1)]
    tick_labels    = ['9:30', '10:30', '11:30', '12:30',
                      '13:30', '14:30', '15:30', '16:00']

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(range(n), intraday_avg.values)
    ax.set_title(f'{name} — Intraday Average (169-Day Mean at Each Minute)')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel(f'Mean {name}')
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45)
    fig.tight_layout()
    fig.savefig(f'{save_dir}/{filename_prefix}_intraday.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {filename_prefix}_intraday.png")

    # ── 3. Distribution (RTH bars only, component-specific filtering) ─────────
    rth_mask_dist = (
        (series.index.time >= _RTH_OPEN) &
        (series.index.time <= _RTH_CLOSE)
    )
    rth_values = series[rth_mask_dist].dropna().values
    if dist_filter == 'positive':
        rth_values = rth_values[rth_values > 0]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(rth_values, bins=100, edgecolor='none')
    ax.set_title(f'{name} — Distribution (RTH Bars Only)')
    ax.set_xlabel(name)
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    fig.savefig(f'{save_dir}/{filename_prefix}_distribution.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {filename_prefix}_distribution.png")

    # ── 4. Individual days (2×2) ──────────────────────────────────────────────
    series_et = series.copy()
    series_et.index = series.index.tz_convert('America/New_York').tz_localize(None)
    local_index = series_et.index

    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    for ax, (key, ts) in zip(axes.flatten(), INDIVIDUAL_DAYS.items()):
        day_date = ts.date()
        day_series = series_et[local_index.date == day_date].dropna()
        if len(day_series) == 0:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                    transform=ax.transAxes)
        else:
            ax.plot(day_series.index, day_series.values)
            day = day_series.index[0].date()
            ticks = [pd.Timestamp(f'{day} {t}') for t in
                     ['09:30', '10:30', '11:30', '12:30',
                      '13:30', '14:30', '15:30', '16:00']]
            ax.set_xticks(ticks)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.set_xlim(
                pd.Timestamp(f'{day} 09:30').tz_localize(None),
                pd.Timestamp(f'{day} 16:00').tz_localize(None)
            )
        ax.set_title(f'{name} — {_DAY_LABELS[key]}')
        ax.set_xlabel('Time')
        ax.set_ylabel(name)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(f'{save_dir}/{filename_prefix}_individual_days.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved {filename_prefix}_individual_days.png")


def plot_arrival(arrival_series, save_dir='results/phase3'):
    _plot_component(arrival_series, 'Trade Arrival Rate', 'arrival',
                    save_dir, daily_agg='mean',
                    dist_filter='positive', ts_filter='positive')

def plot_lambda(lambda_series, save_dir='results/phase3'):
    _plot_component(lambda_series, "Kyle's Lambda", 'lambda',
                    save_dir, daily_agg='max',
                    dist_filter='none', ts_filter='none')

def plot_regime_score(regime_score, save_dir='results/phase3'):
    _plot_component(regime_score, 'RegimeScore', 'regime_score',
                    save_dir, daily_agg='mean',
                    dist_filter='positive', ts_filter='positive')

def plot_roll(roll_series, save_dir='results/phase3'):
    _plot_component(roll_series, 'Roll Spread', 'roll',
                    save_dir, daily_agg='max',
                    dist_filter='positive', ts_filter='positive')


def plot_tfi_by_regime(tfi_df, returns_df, regime_score,
                       save_dir='results/phase3'):
    """
    Three plots showing TFI conditional on RegimeScore.

    Plot 1 — Scatter: TFI vs 1-min forward log return, side-by-side
             for high (>0.5) and low (≤0.5) RegimeScore bars.
    Plot 2 — Overlapping density histograms of TFI for each regime.
    Plot 3 — ACF of TFI at lags 1–20 for each regime.
    """
    from statsmodels.tsa.stattools import acf

    os.makedirs(save_dir, exist_ok=True)

    # Handle both Series and DataFrame inputs
    tfi = tfi_df['tfi'] if isinstance(tfi_df, pd.DataFrame) else tfi_df
    fwd_return = (
        returns_df['log_return'] if isinstance(returns_df, pd.DataFrame)
        else returns_df
    ).shift(-1)

    df = pd.DataFrame({
        'tfi':          tfi,
        'fwd_return':   fwd_return,
        'regime_score': regime_score,
    }).dropna()

    print(f"  Combined aligned bars: {len(df):,}")

    high = df[df['regime_score'] > 0.5]
    low  = df[df['regime_score'] <= 0.5]

    print(f"  High-regime bars: {len(high):,}   Low-regime bars: {len(low):,}")

    # ── Plot 1: TFI vs forward return, by regime ──────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, subset, label, color in [
        (axes[0], high, 'High RegimeScore (>0.5)',   'steelblue'),
        (axes[1], low,  'Low RegimeScore (\u22640.5)', 'tomato'),
    ]:
        # Sample for visual clarity — regression uses full data
        plot_subset = subset.sample(min(5000, len(subset)), random_state=42)
        ax.scatter(plot_subset['tfi'], plot_subset['fwd_return'],
                   alpha=0.15, s=4, color=color, rasterized=True)
        if len(subset) > 1:
            m, b = np.polyfit(subset['tfi'], subset['fwd_return'], 1)
            x_rng = np.linspace(subset['tfi'].min(), subset['tfi'].max(), 200)
            ax.plot(x_rng, m * x_rng + b, color='black', linewidth=1.5,
                    label=f'slope = {m:.2e}')
            ax.legend(fontsize=9)
        ax.axhline(0, color='gray', linewidth=0.6, linestyle='--')
        ax.axvline(0, color='gray', linewidth=0.6, linestyle='--')
        ax.set_title(label)
        ax.set_xlabel('TFI')
        ax.set_ylabel('1-min Forward Log Return')
    fig.suptitle('TFI vs Forward Return by RegimeScore', fontsize=13)
    fig.tight_layout()
    fig.savefig(f'{save_dir}/tfi_scatter_by_regime.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved tfi_scatter_by_regime.png")

    # ── Plot 2: TFI distribution by regime ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(high['tfi'].values, bins=80, alpha=0.5, density=True,
            color='steelblue', label='High RegimeScore (>0.5)')
    ax.hist(low['tfi'].values,  bins=80, alpha=0.5, density=True,
            color='tomato',    label='Low RegimeScore (\u22640.5)')
    ax.set_title('TFI Distribution by RegimeScore')
    ax.set_xlabel('TFI')
    ax.set_ylabel('Density')
    ax.legend()
    fig.tight_layout()
    fig.savefig(f'{save_dir}/tfi_distribution_by_regime.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved tfi_distribution_by_regime.png")

    # ── Plot 3: TFI ACF by regime ─────────────────────────────────────────────
    nlags = 20
    lags  = np.arange(1, nlags + 1)

    high_acf = acf(high['tfi'].values, nlags=nlags, fft=True)[1:]
    low_acf  = acf(low['tfi'].values,  nlags=nlags, fft=True)[1:]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, acf_vals, n, label, color in [
        (axes[0], high_acf, len(high), 'High RegimeScore (>0.5)',   'steelblue'),
        (axes[1], low_acf,  len(low),  'Low RegimeScore (\u22640.5)', 'tomato'),
    ]:
        ci = 1.96 / np.sqrt(n)
        ax.bar(lags, acf_vals, color=color, alpha=0.75, width=0.6)
        ax.axhline( ci, color='gray', linestyle='--', linewidth=1)
        ax.axhline(-ci, color='gray', linestyle='--', linewidth=1)
        ax.axhline(0,   color='black', linewidth=0.5)
        ax.set_title(f'TFI ACF — {label}')
        ax.set_xlabel('Lag (minutes)')
        ax.set_ylabel('Autocorrelation')
        ax.set_xticks(lags)
    fig.suptitle('TFI Autocorrelation Function by RegimeScore', fontsize=13)
    fig.tight_layout()
    fig.savefig(f'{save_dir}/tfi_acf_by_regime.png',
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved tfi_acf_by_regime.png")


if __name__ == '__main__':
    DATA_DIR = (
        "/Users/gabeungab/Desktop/Quant Research Project/raw-data/"
        "GLBX-20250501-20251231/"
    )

    print("Loading data...")
    df       = load_all_days(DATA_DIR)
    df_clean = remove_outliers(df)

    print("Computing signals...")
    lambda_series  = compute_lambda(df_clean)
    roll_series    = compute_roll_spread(df_clean)
    arrival_series = compute_arrival_rate(df_clean)

    df_indexed = df_clean.set_index('ts_event_et')
    bars       = df_indexed['price'].resample('1min').count()

    TZ = "America/New_York"
    announcement_dates = [
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

    if bars.index.tzinfo is None:
        announcement_dates = [dt.tz_localize(None) for dt in announcement_dates]

    exclusion_mask = compute_exclusion_mask(bars, announcement_dates)
    regime_score   = compute_regime_score(
        lambda_series, roll_series, arrival_series, exclusion_mask
    )

    print("Computing TFI and returns...")
    tfi     = compute_tfi(df_clean)
    returns = compute_returns(df_clean)

    print("Generating plots...")
    plot_lambda(lambda_series)
    plot_roll(roll_series)
    plot_arrival(arrival_series)
    plot_regime_score(regime_score)
    plot_tfi_by_regime(tfi, returns, regime_score)

    print("Done. All plots saved to results/phase3/")
