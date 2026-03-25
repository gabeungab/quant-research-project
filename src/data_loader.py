import databento as db
import pandas as pd

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
