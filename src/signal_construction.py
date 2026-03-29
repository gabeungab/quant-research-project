import pandas as pd
import numpy as np


def compute_lambda(df, window=30):
    """
    Estimate Kyle's lambda via rolling OLS of 1-minute bar price changes
    on aggregate signed order flow. Lambda measures price impact per unit
    of order flow and serves as the primary proxy for information asymmetry.

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et, price, size,
        and side columns.
    window : int
        Rolling window in 1-minute bars. Default 30.

    Returns
    -------
    pd.Series
        Kyle's lambda estimate at each 1-minute bar.
        OLS coefficient: cov(delta_p, signed_flow) / var(signed_flow).
    """
    df = df.set_index('ts_event_et')

    signed_flow = (
        df['size'] * df['side'].map({'B': 1, 'A': -1, 'N': 0}).fillna(0)
    )

    closes = df['price'].resample('1min').last()
    bar_dp = closes.diff()
    bar_flow = signed_flow.resample('1min').sum()

    roll_cov = bar_dp.rolling(window=window, min_periods=window).cov(bar_flow)
    roll_var = bar_flow.rolling(window=window, min_periods=window).var()

    lambda_series = roll_cov / roll_var.replace(0, float('nan'))

    return lambda_series


def compute_roll_spread(df, window=30):
    """
    Estimate the Roll (1984) spread via the rolling serial covariance
    of consecutive 1-minute bar price changes.

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et and price columns.
    window : int
        Rolling window in 1-minute bars. Default 30.

    Returns
    -------
    pd.Series
        Roll spread estimate at each 1-minute bar, defined as
        2 * sqrt(max(0, -cov(delta_p_t, delta_p_{t-1}))).
    """
    df = df.set_index('ts_event_et')

    closes = df['price'].resample('1min').last()
    delta_p = closes.diff()

    cov_serial = delta_p.rolling(window=window, min_periods=window).cov(
        delta_p.shift(1)
    )

    roll_series = 2 * np.sqrt((-cov_serial).clip(lower=0))

    return roll_series


def compute_arrival_rate(df, window=5):
    """
    Estimate the trade arrival rate as a rolling mean of 1-minute trade counts.
    Elevated arrival rates indicate heightened market activity and are associated
    with periods of increased informed trading. 

    Parameters
    ----------
    df : pd.DataFrame
        Clean RTH trades DataFrame with ts_event_et and price columns.
    window : int
        Rolling window in 1-minute bars. Default 5.

    Returns
    -------
    pd.Series
        Rolling mean trades-per-minute at each 1-minute bar.
    """
    df = df.set_index('ts_event_et')

    trade_count = df['price'].resample('1min').count()
    arrival_series = trade_count.rolling(window=window, min_periods=window).mean()

    return arrival_series


def compute_regime_score(lambda_series, roll_series, arrival_series,
                          exclusion_mask, lambda_window=30, arrival_window=5):
    """
    Combine Kyle's lambda, Roll spread, and trade arrival rate into a
    continuous RegimeScore in [0, 1] via rolling z-score standardization
    and a logistic transformation.

    Parameters
    ----------
    lambda_series : pd.Series
        Kyle's lambda estimates at each 1-minute bar.
    roll_series : pd.Series
        Roll spread estimates at each 1-minute bar.
    arrival_series : pd.Series
        Trade arrival rate estimates at each 1-minute bar.
    exclusion_mask : pd.Series
        Boolean Series indexed by ts_event_et; True where bar is excluded.
    lambda_window : int
        Rolling window for lambda and roll z-scores. Default 30.
    arrival_window : int
        Rolling window for arrival rate z-score. Default 5.

    Returns
    -------
    pd.Series
        RegimeScore in [0, 1] at each 1-minute bar.
    """
    def rolling_zscore(series, window):
        mean = series.rolling(window=window, min_periods=window).mean()
        std = series.rolling(window=window, min_periods=window).std()
        return (series - mean) / std.replace(0, float('nan'))

    z_lambda = rolling_zscore(lambda_series, window=lambda_window)
    z_roll = rolling_zscore(roll_series, window=lambda_window)
    z_arrival = rolling_zscore(arrival_series, window=arrival_window)

    composite = z_lambda - z_roll + z_arrival
    regime_score = 1 / (1 + np.exp(-composite))

    # Align exclusion mask to regime_score index before applying
    exclusion_aligned = exclusion_mask.reindex(regime_score.index, fill_value=False)
    regime_score = regime_score.where(~exclusion_aligned, other=0.0)

    return regime_score


ROLL_DATES = [
    pd.Timestamp('2025-06-19'),  # ESM5 -> ESU5
    pd.Timestamp('2025-09-18'),  # ESU5 -> ESZ5
    pd.Timestamp('2025-12-18'),  # ESZ5 -> ESH6
    pd.Timestamp('2026-03-19'),  # ESH6 -> ESM6
]

def compute_exclusion_mask(bars, announcement_dates):
    """
    Build a boolean exclusion mask over the 1-minute bar index, marking
    three categories of contaminated observations: the final 10 minutes
    of each RTH session (15:50-16:00 ET), a +- 30-minute window around
    each macro announcement, and contract roll dates plus three preceding
    trading days.

    Parameters
    ----------
    bars : pd.DataFrame or pd.Series
        1-minute bar DataFrame/Series indexed by ts_event_et.
    announcement_dates : list of pd.Timestamp
        Timezone-aware announcement datetimes (Eastern). Each triggers
        a ±30-minute exclusion window.

    Returns
    -------
    pd.Series
        Boolean Series indexed by ts_event_et; True where bar is excluded.
    """
    index = bars.index
    mask = pd.Series(False, index=index)

    # 1. Final 10 minutes of each RTH session (15:50-16:00 ET)
    cutoff_time = pd.Timestamp('15:50').time()
    mask |= pd.Series(index.time >= cutoff_time, index=index)

    # 2. ±30 minutes around each macro announcement
    for ann_dt in announcement_dates:
        window_start = ann_dt - pd.Timedelta(minutes=30)
        window_end = ann_dt + pd.Timedelta(minutes=30)
        mask |= (index >= window_start) & (index <= window_end)

    # 3. Contract roll dates and 3 preceding trading days
    index_dates = pd.Series(index.date, index=index)
    for roll_date in ROLL_DATES:
        roll_start = (roll_date - pd.offsets.BDay(3)).date()
        mask |= (
            (index_dates >= roll_start) &
            (index_dates <= roll_date.date())
        )

    return mask
