import databento as db
import pandas as pd
import numpy as np

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


def load_all_days(directory):
    """
    Load all days of ES futures trades from a directory path.
    Returns a combined DataFrame filtered to RTH (9:30 AM to 4:00 PM ET),
    sorted chronologically.

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
