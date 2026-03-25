import databento as db
import pandas as pd

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
