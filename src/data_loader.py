import databento as db
import pandas as pd
import numpy as np

import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import os


def load_day(filepath):
    """
    Load one day of ES futures trades from a .dbn.zst file.
    Returns a DataFrame filtered to RTH (9:30 AM to 4:00 PM ET).

    Parameters
    ----------
    filepath : str
        Path to a .dbn.zst file from Databento GLBX.MDP3 trades feed.

    Returns
    -------
    pd.DataFrame
        Trades during RTH with ts_event_et column in Eastern time.
    """
    store = db.DBNStore.from_file(filepath)
    df = store.to_df()
    df = df[~df['symbol'].str.contains('-')]

    df['ts_event'] = pd.to_datetime(df['ts_event'], utc=True)
    df['ts_event_et'] = df['ts_event'].dt.tz_convert('America/New_York')

    rth_start = pd.Timestamp('09:30:00').time()
    rth_end = pd.Timestamp('16:00:00').time()

    df_rth = df[
        (df['ts_event_et'].dt.time >= rth_start) &
        (df['ts_event_et'].dt.time <= rth_end)
    ]

    return df_rth


EXCLUDED_DATES = {
    '20250526',  # Memorial Day
    '20250704',  # Independence Day
    '20250901',  # Labor Day
    '20251127',  # Thanksgiving Eve (half-session)
}

def load_all_days(directory):
    """
    Load all days of ES futures trades from a directory path.
    Returns a combined DataFrame filtered to RTH (9:30 AM to 4:00 PM ET),
    sorted chronologically. Excludes known federal holidays and
    half-sessions (see EXCLUDED_DATES constant).

    Parameters
    ----------
    directory : str
        Path to a directory containing .dbn.zst files from Databento
        GLBX.MDP3 trades feed.

    Returns
    -------
    pd.DataFrame
        All RTH trades across all days, sorted by ts_event_et.
    """
    frames = []

    for file in sorted(os.listdir(directory)):
        if file.endswith('.dbn.zst'):
            date_str = file[10:18]
            if date_str in EXCLUDED_DATES:
                print(f"Skipping {file} (excluded date)")
                continue
            filepath = os.path.join(directory, file)
            print(f"Loading {file}...")
            df = load_day(filepath)
            frames.append(df)

    df_all = pd.concat(frames, ignore_index=True)
    df_all = df_all.sort_values('ts_event_et').reset_index(drop=True)

    return df_all


def resample_to_bars(df, bar_size):
    """
    Resample RTH tick data into OHLCV time bars.

    Parameters
    ----------
    df : pd.DataFrame
        RTH trades DataFrame with ts_event_et column.
    bar_size : str
        Pandas offset string for bar size, e.g. '5s', '15min', '4h', '1D'.

    Returns
    -------
    pd.DataFrame
        OHLCV bars with trade count, indexed by ts_event_et.
    """
    df = df.set_index('ts_event_et')

    df_bars = df.resample(bar_size).agg(
        open=('price', 'first'),
        high=('price', 'max'),
        low=('price', 'min'),
        close=('price', 'last'),
        volume=('size', 'sum'),
        trade_count=('price', 'count')
    )

    df_bars = df_bars.dropna(subset=['open'])

    return df_bars


def remove_outliers(df, window=100, threshold=5):
    """
    Remove trades with prices more than a given number of standard
    deviations from the rolling mean price.

    Parameters
    ----------
    df : pd.DataFrame
        RTH trades DataFrame with a price column.
    window : int
        Number of trades to use for rolling mean and std. Default 100.
    threshold : float
        Number of standard deviations beyond which a trade is an outlier.
        Default 5.

    Returns
    -------
    pd.DataFrame
        DataFrame with outlier trades removed.
    """
    rolling_mean = df['price'].rolling(window=window, min_periods=1).mean()
    rolling_std = df['price'].rolling(window=window, min_periods=1).std()

    lower_bound = rolling_mean - threshold * rolling_std
    upper_bound = rolling_mean + threshold * rolling_std

    mask = (df['price'] >= lower_bound) & (df['price'] <= upper_bound)

    n_outliers = (~mask).sum()
    print(f"Removed {n_outliers} outlier trades ({n_outliers / len(df) * 100:.4f}% of data)")

    return df[mask].reset_index(drop=True)


def compute_tfi(df, bar_size='1min'):
    """
    Compute Trade Flow Imbalance (TFI) per time bar.
    TFI = (buy_volume - sell_volume) / (buy_volume + sell_volume)
    Result is between -1 (all selling) and +1 (all buying).

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et, side, and size columns.
    bar_size : str
        Pandas offset string for bar size. Default '1min'.

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by ts_event_et with columns:
        buy_volume, sell_volume, total_volume, tfi.
    """
    df = df.set_index('ts_event_et')

    buy_volume = (
        df[df['side'] == 'B']['size']
        .resample(bar_size)
        .sum()
        .rename('buy_volume')
    )

    sell_volume = (
        df[df['side'] == 'A']['size']
        .resample(bar_size)
        .sum()
        .rename('sell_volume')
    )

    tfi_df = pd.concat([buy_volume, sell_volume], axis=1).fillna(0)
    tfi_df = tfi_df.astype({'buy_volume': 'int64', 'sell_volume': 'int64'})
    tfi_df['total_volume'] = tfi_df['buy_volume'] + tfi_df['sell_volume']

    tfi_df['tfi'] = np.where(
        tfi_df['total_volume'] > 0,
        (tfi_df['buy_volume'] - tfi_df['sell_volume']) / tfi_df['total_volume'],
        float('nan')
    )

    tfi_df = tfi_df.dropna(subset=['tfi'])

    return tfi_df


def compute_returns(df, bar_size='1min'):
    """
    Compute 1-minute log returns from clean RTH tick data.

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et and price columns.
    bar_size : str
        Pandas offset string for bar size. Default '1min'.

    Returns
    -------
    pd.DataFrame
        DataFrame with close price and log_return columns,
        indexed by ts_event_et. First bar of each day will be
        NaN (no previous close to compute return from).
    """
    df = df.set_index('ts_event_et')

    bars = df.resample(bar_size).agg(
        close=('price', 'last')
    ).dropna()

    bars['log_return'] = np.log(bars['close'] / bars['close'].shift(1))

    return bars


def run_ols(tfi_df, returns_df):
    """
    Run OLS regression of forward 1-minute returns on TFI.
    Aligns TFI at time T with return at time T+1 to test
    whether TFI predicts future price movement.

    Parameters
    ----------
    tfi_df : pd.DataFrame
        DataFrame with tfi column, indexed by ts_event_et.
    returns_df : pd.DataFrame
        DataFrame with log_return column, indexed by ts_event_et.

    Returns
    -------
    statsmodels RegressionResults
        Fitted OLS model. Call .summary() to print results.
    """
    merged = pd.DataFrame({
        'tfi': tfi_df['tfi'],
        'forward_return': returns_df['log_return'].shift(-1)
    }).dropna()

    X = sm.add_constant(merged['tfi'])
    Y = merged['forward_return']

    model = sm.OLS(Y, X)
    results = model.fit(cov_type='HAC', cov_kwds={'maxlags': 5})

    return results


def test_autocorrelation(series, lags=10):
    """
    Test for autocorrelation in a time series using the Ljung-Box test.
    Null hypothesis: no autocorrelation up to the specified number of lags.
    A significant p-value (< 0.05) indicates autocorrelation is present.

    Parameters
    ----------
    series : pd.Series
        Time series to test. Can be residuals, returns, TFI, or any
        other series.
    lags : int
        Number of lags to test. Default 10.

    Returns
    -------
    pd.DataFrame
        DataFrame with lb_stat (test statistic) and lb_pvalue for
        each lag from 1 to lags.
    """
    result = acorr_ljungbox(series.dropna(), lags=lags, return_df=True)
    
    print(result)
    return result


def plot_overview(tfi_df, returns_df, day='2025-05-01',
                  save_path='results/overview.png'):
    """
    Produce a 2x2 overview figure and save to disk.
    Top row: TFI and returns for a single trading day (line plots).
    Bottom row: distributions of TFI and returns across full sample
    (histograms).

    Parameters
    ----------
    tfi_df : pd.DataFrame
        DataFrame with tfi column, indexed by ts_event_et.
    returns_df : pd.DataFrame
        DataFrame with log_return column, indexed by ts_event_et.
    save_path : str
        Path to save the figure. Default 'results/overview.png'.
    """
    one_day = day
    tfi_day = tfi_df.loc[one_day]
    returns_day = returns_df.loc[one_day]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].plot(tfi_day.index, tfi_day['tfi'])
    axes[0, 0].set_title('TFI — 2025-05-01')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('TFI')

    axes[0, 1].plot(returns_day.index, returns_day['log_return'])
    axes[0, 1].set_title('Log Returns — 2025-05-01')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Log Return')

    axes[1, 0].hist(tfi_df['tfi'].dropna(), bins=100)
    axes[1, 0].set_title('TFI Distribution — Full Sample')
    axes[1, 0].set_xlabel('TFI')
    axes[1, 0].set_ylabel('Frequency')

    axes[1, 1].hist(returns_df['log_return'].dropna(), bins=100)
    axes[1, 1].set_title('Return Distribution — Full Sample')
    axes[1, 1].set_xlabel('Log Return')
    axes[1, 1].set_ylabel('Frequency')

    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to {save_path}")
    plt.close(fig)


def compute_daily_stats(df):
    """
    Compute daily summary statistics from clean RTH tick data.

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et, price,
        size, and side columns.

    Returns
    -------
    pd.DataFrame
        One row per trading day with columns: trade_count,
        total_volume, buy_sell_ratio, avg_trade_size,
        realized_vol, price_range.
    """
    df = df.set_index('ts_event_et')

    daily = df.resample('1D').agg(
        trade_count=('price', 'count'),
        total_volume=('size', 'sum'),
        avg_trade_size=('size', 'mean'),
        daily_high=('price', 'max'),
        daily_low=('price', 'min')
    )

    buy_vol = (df[df['side'] == 'B']['size']
               .resample('1D').sum()
               .rename('buy_volume'))
    sell_vol = (df[df['side'] == 'A']['size']
                .resample('1D').sum()
                .rename('sell_volume'))

    daily = daily.join(buy_vol).join(sell_vol)
    daily['buy_volume'] = daily['buy_volume'].fillna(0).astype('int64')
    daily['sell_volume'] = daily['sell_volume'].fillna(0).astype('int64')

    daily['price_range'] = daily['daily_high'] - daily['daily_low']
    daily['buy_sell_ratio'] = (
        daily['buy_volume'] /
        daily['sell_volume'].replace(0, float('nan'))
    )

    bars = df.resample('1min').agg(
        close=('price', 'last')
    ).dropna()
    bars['log_return'] = np.log(bars['close'] / bars['close'].shift(1))
    daily['realized_vol'] = bars['log_return'].resample('1D').std()

    daily = daily.drop(columns=['daily_high', 'daily_low',
                                  'buy_volume', 'sell_volume'])
    daily = daily[daily['trade_count'] > 0]

    return daily


def plot_phase1(df_clean, daily, save_dir='results/phase1'):
    """
    Produce Phase 1 exploratory plots and save to results/phase1.

    Parameters
    ----------
    df_clean : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et, price, size columns.
    daily : pd.DataFrame
        Daily summary DataFrame from compute_daily_stats().
    save_dir : str
        Directory to save figures. Default 'results'.
    """
    df = df_clean.set_index('ts_event_et')

    bars = df.resample('1min').agg(
        trade_count=('price', 'count'),
        volume=('size', 'sum'),
        close=('price', 'last')
    ).dropna()

    bars['log_return'] = np.log(bars['close'] / bars['close'].shift(1))

    bars['time_of_day'] = bars.index.time
    intraday_trades = bars.groupby('time_of_day')['trade_count'].mean()
    intraday_volume = bars.groupby('time_of_day')['volume'].mean()
    intraday_vol = bars.groupby('time_of_day')['log_return'].std()

    # Plot 1: Intraday trade arrival rate
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(range(len(intraday_trades)), intraday_trades.values)
    ax.set_title('Intraday Trade Arrival Rate (Average Across 169 Days)')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Average Trades per Minute')
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360, 389])
    ax.set_xticklabels(
        ['9:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:00'],
        rotation=45
    )
    fig.tight_layout()
    fig.savefig(f'{save_dir}/intraday_trade_arrival.png', dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print("Saved intraday_trade_arrival.png")

    # Plot 2: Intraday volume profile
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(range(len(intraday_volume)), intraday_volume.values)
    ax.set_title('Intraday Volume (Average Across 169 Days)')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Average Volume per Minute')
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360, 389])
    ax.set_xticklabels(
        ['9:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:00'],
        rotation=45
    )
    fig.tight_layout()
    fig.savefig(f'{save_dir}/intraday_volume.png', dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print("Saved intraday_volume.png")

    # Plot 3: Intraday volatility profile
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(range(len(intraday_vol)), intraday_vol.values)
    ax.set_title('Intraday Volatility (Average Across 169 Days)')
    ax.set_xlabel('Time of Day')
    ax.set_ylabel('Average Volatility per Minute')
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360, 389])
    ax.set_xticklabels(
        ['9:30', '10:30', '11:30', '12:30', '13:30', '14:30', '15:30', '16:00'],
        rotation=45
    )
    fig.tight_layout()
    fig.savefig(f'{save_dir}/intraday_volatility.png', dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print("Saved intraday_volatility.png")

    # Plot 4: Trade size distribution (log scale)
    fig, ax = plt.subplots(figsize=(12, 4))
    sizes = df['size'][df['size'] > 0]
    ax.hist(sizes, bins=100)
    ax.set_xscale('log')
    ax.set_title('Trade Size Distribution (Log Scale)')
    ax.set_xlabel('Trade Size (log scale)')
    ax.set_ylabel('Frequency')
    fig.tight_layout()
    fig.savefig(f'{save_dir}/trade_size_distribution.png', dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print("Saved trade_size_distribution.png")

    # Plot 5: Daily volume over time
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(daily.index, daily['total_volume'])
    ax.set_title('Daily Volume Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Daily Volume')
    fig.tight_layout()
    fig.autofmt_xdate()
    fig.savefig(f'{save_dir}/daily_volume_over_time.png', dpi=150,
                bbox_inches='tight')
    plt.close(fig)
    print("Saved daily_volume_over_time.png")
