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

---

## 4. Signal Construction and Empirical Design

### 4.1 Trade Flow Imbalance

The primary signal is Trade Flow Imbalance (TFI), defined as the
normalized difference between buyer- and seller-initiated volume
within each 1-minute bar:

TFI_t = (BuyVol_t − SellVol_t) / (BuyVol_t + SellVol_t)

where BuyVol_t and SellVol_t are the total contract size of
buyer-initiated (aggressor side B) and seller-initiated (aggressor
side A) trades respectively within bar t. TFI_t ∈ [−1, 1], with
positive values indicating net buying pressure and negative values
indicating net selling pressure.

Unconditionally, TFI mixes informed and uninformed order flow.
Index fund rebalancing, inventory management by market makers, and
retail liquidity trades all contribute to TFI without carrying
information about future price direction. The analysis therefore
conditions TFI on a regime indicator designed to isolate periods
where order flow is more likely to reflect private information.

### 4.2 Informed Trading Regime Score

The informed trading regime score, RegimeScore_t ∈ [0, 1], is
a continuous measure of the probability that bar t occurs during
a period of elevated information asymmetry. It is constructed from
three components, each motivated by the adverse selection framework
of Glosten and Milgrom (1985) and Kyle (1985).

**Kyle's lambda** measures price impact per unit of signed order
flow, estimated from a rolling OLS regression of price changes on
signed order flow over a 30-minute window updated each minute.
High lambda indicates market makers are updating quotes aggressively
in response to order flow — consistent with their inference that
the flow may be informed.

**Roll (1984) spread estimate** measures bid-ask tightness from
the serial covariance of consecutive trade price changes. When a
bid-ask spread exists, prices alternate between bid and ask,
producing negative serial covariance whose magnitude is directly
related to spread size. Low Roll spread confirms normal market
tightness, ruling out structural illiquidity as the source of
elevated lambda.

**Trade arrival rate** measures trades per minute over a 5-minute
rolling window, proxying market depth and active liquidity
provision. High arrival rate confirms many market makers are
actively quoting, ruling out thin depth as the source of elevated
lambda. A shorter window than lambda and Roll is used to reflect
the faster response of trading activity to changing market
conditions.

The three components are combined into a continuous score:

1. Standardize each component using rolling z-scores over a
   30-minute window:
   z_lambda_t = (lambda_t − μ_lambda) / σ_lambda
   z_roll_t   = (Roll_t − μ_roll) / σ_roll
   z_arrival_t = (arrival_t − μ_arrival) / σ_arrival

2. Combine with theoretically motivated signs:
   RawScore_t = z_lambda_t − z_roll_t + z_arrival_t

3. Map to [0, 1] via logistic transformation:
   RegimeScore_t = 1 / (1 + exp(−RawScore_t))

Rolling standardization ensures the score is always relative to
recent market conditions rather than the full sample distribution,
allowing the score to adapt to the two distinct activity regimes
identified in Section 3.3. All rolling estimates use only past
data — no lookahead bias is introduced.

### 4.3 Exclusion Windows

Three categories of known uninformed directional flow are excluded
by setting RegimeScore_t = 0 regardless of indicator values:

The final 10 minutes of each session (15:50–16:00 ET) are dominated
by MOC order flow — mechanical, publicly announced execution that
generates high volume without price impact, as documented in Section
3.4. The 30 minutes surrounding scheduled macro announcements
(FOMC, CPI, NFP) are excluded because these public information
events drive directional order flow from participants responding to
the same public signal rather than private information. Contract
roll dates and the three preceding trading days are excluded to
remove the structural illiquidity and mechanical volume migration
that accompany front-month contract expiration.

### 4.4 Regime Detector Validation

Prior to testing TFI predictability, the regime detector is
validated against three independent criteria. First, realized
volatility should be significantly higher in high-RegimeScore bars
— informed trading generates volatility through aggressive quote
updating even though volatility is not a regime condition. Second,
RegimeScore should be elevated in the 30 minutes before scheduled
macro announcements, when informed traders with early signal access
are most active. Third, price impact should be more persistent in
high-RegimeScore bars — informed trading produces permanent price
impact as information is incorporated, while uninformed trading
produces temporary impact that reverts as market makers recognize
the flow was not informative.

### 4.5 Primary Specification

The primary test regresses forward returns on TFI using
RegimeScore as a continuous moderator:

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t

β₁ captures TFI predictability when RegimeScore = 0. β₂ captures
any return level difference across regime states independent of
TFI. β₃ is the primary coefficient of interest — it measures the
additional TFI slope per unit increase in informed trading
probability. A positive and significant β₃ indicates TFI predicts
returns more strongly as the probability of informed trading
increases. β₄ and β₅ control for return autocorrelation and TFI
persistence respectively, ensuring β₃ reflects genuine
regime-conditioned predictability rather than autocorrelation
structure. All regressions use Newey-West standard errors with
maxlags=5 to correct for autocorrelation and heteroskedasticity
in the residuals.

### 4.6 Additional Tests

**Horizon analysis:** The primary specification is repeated at
1-minute, 5-minute, and 15-minute forward horizons to characterize
the decay of TFI predictability across regimes. The decay structure
provides evidence on the speed of information incorporation in ES
futures and determines the practical time window during which the
regime signal is actionable.

**Effect size decomposition:** The distribution of RegimeScore
across the full sample and each sub-period is reported, including
the fraction of bars with RegimeScore > 0.5 and RegimeScore > 0.75.
This contextualizes the economic significance of the finding —
a highly predictive signal active in 3% of bars has different
practical implications than one active in 30% of bars.

**Subsample stability:** The primary test is repeated on the full
in-sample period (2025-05-01 to 2025-12-30) and the two activity
sub-periods identified in Section 3.3 (2025-05-01 to 2025-09-30
and 2025-10-01 to 2025-12-30) independently. Consistency across
sub-periods indicates a structural property of ES futures rather
than a sample-specific artifact.

**Transaction cost analysis:** The predicted return per bar at
high RegimeScore levels is compared against the ES futures
round-trip transaction cost of one tick (0.25 index points,
~4 basis points of notional). The annualized Sharpe ratio of a
strategy trading in the direction of TFI when RegimeScore > 0.5,
net of transaction costs, is reported.

**Out-of-sample validation:** The in-sample estimated model
(coefficients fixed) is applied to the held-out period
2026-01-01 through 2026-03-09. Graceful degradation — weaker
but same sign and direction — is the expected outcome.

### 4.7 Robustness

The following robustness checks are pre-specified:

*Regime operationalization:* A binary regime dummy (1 if lambda
exceeds its 75th percentile, Roll falls below its 25th percentile,
and arrival rate exceeds its 75th percentile, simultaneously) is
tested as an alternative to the continuous RegimeScore. Thresholds
are additionally tested at 70th/30th and 80th/20th percentiles.

*Regime indicator:* RegimeScore is replaced with daily VPIN
(Easley, Lopez de Prado, and O'Hara, 2012) to test whether results
are consistent across theoretically distinct regime indicators with
different failure modes.

*Rolling window lengths:* Lambda and Roll windows tested at 15
and 60 minutes. Arrival rate window tested at 2 and 10 minutes.

*Return measurement:* Forward return tested with and without
skipping one bar to account for bid-ask bounce contamination in
the return series.

---

## 5. Market Maker Implications

[TO BE WRITTEN — Phase 5]

The magnitude of β₃ in the informed regime provides a quantitative
input to market maker quote adjustment. A market maker observing
high RegimeScore — elevated price impact, tight spreads, and active
market participation — faces increased adverse selection risk. The
Kyle (1985) framework maps the estimated lambda directly to the
optimal adverse selection component of the bid-ask spread. The
decay structure from Section 4.6 (horizon analysis) determines
the duration over which the market maker should maintain this
adjusted quoting behavior before returning to the unconditional
regime.

---

## References

Cont, R., Kukanov, A., and Stoikov, S. (2014). The price impact
of order book events. *Journal of Financial Econometrics*,
12(1), 47–88.

Easley, D., Lopez de Prado, M., and O'Hara, M. (2012). Flow
toxicity and liquidity in a high-frequency world. *Review of
Financial Studies*, 25(5), 1457–1493.

Glosten, L. and Milgrom, P. (1985). Bid, ask and transaction
prices in a specialist market with heterogeneously informed
traders. *Journal of Financial Economics*, 14(1), 71–100.

Kyle, A. (1985). Continuous auctions and insider trading.
*Econometrica*, 53(6), 1315–1335.

Roll, R. (1984). A simple implicit measure of the effective
bid-ask spread in an efficient market. *Journal of Finance*,
39(4), 1127–1139.
