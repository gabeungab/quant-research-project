# ES Futures Microstructure Research — Working Paper

---

## 3. Data

### 3.1 Source and Instrument

This study uses trade-level data from CME Globex obtained via
Databento (GLBX.MDP3, Trades schema). The data provides a complete
record of every executed trade in ES futures at nanosecond timestamp
precision, including execution price, contract size, and aggressor
side (B = buyer, A = seller, N = unknown).

Analysis is restricted to Regular Trading Hours: 9:30 AM to 4:00 PM
Eastern time. The overnight Globex session is excluded due to its
structurally different liquidity profile. Calendar spread instruments
(e.g. ESM5-ESU5), which appeared in the raw feed with spread prices
rather than outright futures prices, were removed by filtering any
symbol containing a hyphen.

### 3.2 Sample Period and Cleaning

The in-sample period covers 2025-05-01 through 2025-12-30. A
held-out out-of-sample period spanning 2026-01-01 through 2026-03-09
is reserved exclusively for final validation and is not used in any
model estimation or specification search.

Four trading days were excluded due to anomalously low activity
relative to the sample mean of 348,369 trades per day: Memorial Day
(2025-05-26, 14,711 trades), Independence Day (2025-07-04, 13,367
trades), Labor Day (2025-09-01, 11,431 trades), and the half-session
preceding Thanksgiving (2025-11-27, 9,258 trades). A natural gap
separates these four days from all other sessions, including
recognized reduced-activity days such as Juneteenth (51,784 trades)
which are retained as legitimate trading sessions.

Price outliers were removed using a rolling five-standard-deviation
filter with a window of 100 trades, eliminating 114,413 records
(~0.19% of the raw sample). An additional 2,856,579 records share
nanosecond timestamps with at least one other trade; inspection
confirmed these as legitimate multi-level fills and all are retained.

The final clean in-sample dataset contains ~58.8 million RTH trades
across 169 trading days.

### 3.3 Descriptive Statistics

Table 1 presents daily summary statistics across the 169-day
in-sample period.

| Statistic               | Mean      | Std       | Min     | Max       |
|-------------------------|-----------|-----------|---------|-----------|
| Trade count             | 348,369   | 142,128   | 51,784  | 1,015,024 |
| Total volume (contracts)| 1,070,364 | 335,016   | 121,454 | 2,509,428 |
| Avg trade size          | 3.17      | 0.33      | 2.35    | 3.92      |
| Price range (pts)       | 121.4     | 38.8      | 30.5    | 298.5     |
| Buy/sell volume ratio   | 1.003     | 0.022     | 0.942   | 1.096     |
| Realized vol (per min)  | 0.000894  | 0.001429  | 0.000125| 0.006346  |

Buyer- and seller-initiated trades account for 49.91% and 50.09% of
volume respectively, with unknown aggressor side comprising a
negligible 0.000003% of records. Individual trade sizes are highly
right-skewed: the median is 1 contract and the 75th percentile is
3 contracts, while the maximum reaches 1,968 contracts. Daily volume
was relatively stable at ~1 million contracts per day from May
through September 2025, becoming more elevated and volatile from
October through December, suggesting two distinct activity regimes
within the sample period.

[FIGURE 1: Daily total volume over time across 169 trading days,
showing two distinct activity regimes — daily_volume_over_time.png]

### 3.4 Intraday Patterns

Intraday volume exhibits a modified inverse-J shape across the
trading day, peaking at the open, declining steadily through the
morning, remaining low through midday, and surging sharply at the
close — reaching ~52,000 contracts per minute in the final minute
of trading, driven by MOC order flow (Figure 2). Trade arrival rate
follows the same pattern, with ~4,000 trades per minute at the open
and ~7,500 at the close, indicating that the close-of-day spike
reflects both more trades and larger average trade sizes.

[FIGURE 2: Average intraday volume by minute across 169 trading
days — intraday_volume.png]

Intraday realized volatility exhibits a distinctly different pattern.
Volatility spikes sharply at the open (~0.0053 per minute, ~3x the
midday average) as overnight information is incorporated into prices,
then declines rapidly and remains flat through midday and into the
close, with no corresponding spike despite the sharp increase in
volume. This divergence is consistent with MOC-driven close activity
— uninformed, publicly announced order flow that generates no adverse
selection and therefore minimal price impact — in contrast to the
open, where informed order flow drives both high volume and high
volatility through adverse selection.

[FIGURE 3: Average intraday realized volatility by minute across
169 trading days — intraday_volatility.png]
