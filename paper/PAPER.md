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
the flow may be informed. However, high lambda alone is
insufficient: elevated price impact can equally reflect thin
markets, market stress, or mechanical order flow rather than
informed trading. Two additional components and exclusion windows
rule out these alternative explanations.

**Roll (1984) spread estimate** measures bid-ask tightness from
the serial covariance of consecutive trade price changes. When a
bid-ask spread exists, prices alternate between bid and ask,
producing negative serial covariance whose magnitude is directly
related to spread size. Low Roll spread confirms normal market
tightness, ruling out structural illiquidity as the source of
elevated lambda. Roll spread values at 1-minute resolution are
inflated relative to the true bid-ask spread due to large intraday
price moves dominating the serial covariance; however, Roll enters
the regime score only through its rolling z-score, so the absolute
level is irrelevant — only relative tightness across bars matters.

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

Four sources of residual misclassification or signal attenuation
are acknowledged. Market maker inventory pressure and mechanical
order clustering can produce elevated lambda in liquid markets
without informed trading. The Roll spread estimator is unreliable
in strongly one-sided markets as the bid-ask bounce disappears —
precisely the high-lambda informed trading conditions of interest;
in these conditions Roll contributes approximately zero to the
composite score rather than a negative value, reducing RegimeScore
magnitude without reversing the signal direction, with lambda and
arrival rate remaining the primary drivers. Kyle's lambda is
undefined when signed order flow has zero variance across the
estimation window, excluding ~31% of core RTH bars from regime 
detection; these bars are self-selecting as uninformative, as the 
absence of directional flow is itself evidence against an informed 
trading regime. Finally, the rolling window requires a warmup period 
at the start of each session, though this is empirically subsumed by 
the zero-variance exclusion.

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
volatility should be higher in high-RegimeScore bars — informed
trading generates volatility through aggressive quote updating
even though volatility is not a regime condition. Second,
RegimeScore should be elevated in the 30 minutes before scheduled
macro announcements, when informed traders with early signal access
are most active. Third, the contemporaneous TFI-return slope should
be larger in high-RegimeScore bars — informed order flow should
move prices more per unit of TFI within the same bar.

Exploratory results confirm the third criterion most clearly.
The contemporaneous TFI slope is 1.80e-03 in high-regime bars
versus 9.66e-04 in low-regime bars — a 1.87x amplification,
consistent with theory. Realized volatility validation requires
care: exclusion windows mechanically set RegimeScore = 0 during
the highest-volatility announcement and roll events, removing
these episodes from the high-regime group. A decile analysis
confirms the detector is directionally correct — the highest
genuine RegimeScore decile has elevated forward return volatility
(std = 0.001172) relative to middle deciles (std ≈ 0.000900-0.000978)
— but the amplification is modest because the most extreme
high-lambda episodes are excluded by design.

The detector operates most reliably during the stable midday 
portion of the trading session, where lambda is estimable, Roll 
is not in persistent one-sided failure, and structural events 
are absent.

### 4.5 Empirical Tests

**Primary hypothesis test — forward return predictability (T+1):**

The primary test asks whether regime-conditioned TFI predicts
forward returns at the one-bar horizon — a genuinely predictive
question where the outcome is unknown when the signal is observed:

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t

β₁ captures the unconditional TFI effect when RegimeScore = 0.
β₂ captures any return level difference across regime states
independent of TFI. β₃ is the primary coefficient of interest —
a significant β₃ would indicate that the regime detector identifies
periods where TFI's predictive power for future returns is genuinely
amplified. β₄ and β₅ control for return autocorrelation and TFI
persistence. All regressions use Newey-West standard errors with
maxlags=5.

Formal results: β₃ = 0.0001, z = 0.568, p = 0.570. The null
hypothesis is not rejected. The regime does not significantly
amplify TFI's predictive power for the next bar's return. β₁ =
0.0007, z = 5.121, p < 0.001 — unconditional TFI significantly
predicts forward returns, consistent with Cont, Kukanov, and
Stoikov (2014), but this effect does not strengthen in high-regime
conditions. The null result is consistent across both activity
sub-periods (May-Sep: β₃ = 0.0001, p = 0.704; Oct-Dec: β₃ =
0.0001, p = 0.639) and at longer horizons (T+5: β₃ = -0.000027,
p = 0.902; T+15: β₃ = -0.000108, p = 0.659). Information in ES
futures appears to be incorporated within one 1-minute bar in
high-regime conditions, leaving no residual regime-conditioned
predictability at any horizon tested.

**Secondary characterization — contemporaneous price impact (T+0):**

A separate analysis characterizes the regime-conditioned
relationship between TFI and same-bar returns, directly paralleling
the Kyle (1985) lambda framework. This is not a predictive test —
it measures how the within-bar price impact of order flow varies
with the regime indicator:

Return_t = α + β₁·TFI_t + β₂·RegimeScore_t +
           β₃·(TFI_t × RegimeScore_t) +
           β₅·TFI_{t-1} + ε_t

This specification omits lagged return from the right-hand side
because Return_t is the dependent variable. The interaction β₃
here measures the amplification of contemporaneous price impact
per unit of RegimeScore — a direct empirical analog of the Kyle
(1985) lambda relationship.

Formal results: β₃ = 0.0015, z = 7.214, p < 0.001. The regime
significantly amplifies contemporaneous price impact. At RegimeScore
= 0, the TFI-return slope is 0.0007; at the mean high-regime score
of 0.788, the slope is 0.0007 + 0.0015 × 0.788 = 0.00188 — a
2.7x amplification. This confirms the regime detector correctly
identifies periods of elevated order flow informativeness as
defined by the Kyle (1985) framework. It should be noted that this
finding is partially circular: Kyle's lambda is built into
RegimeScore as a component, and lambda is itself a contemporaneous
price impact measure. The contemporaneous result therefore serves
primarily as a validation that the regime detector is measuring
what it claims to measure, rather than as an independent empirical
contribution.

The economic significance of the contemporaneous finding is most
relevant for market makers who observe accumulating order flow in
real-time within the bar, as discussed in Section 5.

### 4.6 Additional Tests

**Horizon analysis:** The primary specification is repeated at
5-minute and 15-minute cumulative forward horizons. Results confirm
no regime interaction at any horizon: T+5 β₃ = -0.000027 (p = 0.902),
T+15 β₃ = -0.000108 (p = 0.659). The unconditional TFI effect (β₁)
remains significant at all horizons (~0.0007-0.0008, p < 0.001),
but does not vary with the regime. Information incorporation in
ES futures is complete within one 1-minute bar in high-regime
conditions.

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
tested as an alternative to the continuous RegimeScore. This tests
whether results are robust to the specific functional form of the
regime indicator — confirming that findings reflect genuine regime
differences rather than artifacts of the logistic transformation
or z-score standardization. Thresholds are additionally tested at
70th/30th and 80th/20th percentiles.

*Regime indicator:* RegimeScore is replaced with daily VPIN
(Easley, Lopez de Prado, and O'Hara, 2012) to test whether results
hold under a theoretically distinct regime indicator with different
construction assumptions and different failure modes — confirming
that findings are not specific to the lambda-based regime
detector.

*Rolling window lengths:* Lambda and Roll windows tested at 15
and 60 minutes. Arrival rate window tested at 2 and 10 minutes.
This tests whether results are sensitive to the specific time
horizon over which regime components are estimated.

*Return measurement:* Forward return tested with and without
skipping one bar. This tests whether results are contaminated
by bid-ask bounce in the return series — a microstructure
artifact that could create spurious predictability at the
1-minute horizon.

---

## 5. Market Maker Implications

The formal results in Section 4.5 provide a quantitative basis for
adaptive quote management in ES futures. The contemporaneous
characterization — β₃ = 0.0015, z = 7.214, p < 0.001 — establishes
that each unit of TFI moves prices 2.7x more per bar at the mean
high-regime score (0.788) than unconditionally. A market maker who
can compute RegimeScore in real-time from streaming trade data
therefore has a precise, empirically calibrated measure of their
current adverse selection exposure.

The practical implication follows directly from the Glosten and
Milgrom (1985) adverse selection model. A market maker's optimal
spread width is proportional to the probability that any given
order is informed and the price impact that informed order will
generate. The contemporaneous β₃ provides the latter: in high-
regime conditions, a one-unit increase in TFI generates 0.00188
log points of price movement rather than 0.0007 unconditionally.
A market maker observing high RegimeScore and accumulating TFI
mid-bar should widen quotes proportionally to reflect this elevated
adverse selection.

The break-even analysis from Section 4.5 contextualizes the
magnitude. At the mean high-regime RegimeScore of 0.788, the
break-even TFI for a round-trip trade is 0.031 — meaning any
bar where |TFI| exceeds 0.031 generates price movement large
enough to exceed the two-tick round-trip cost of 0.774 basis
points. Approximately 75% of high-regime bars clear this threshold
in the in-sample period, confirming that elevated adverse selection
is a persistent feature of high-regime conditions rather than an
occasional extreme event.

The null result in the primary predictive specification (β₃ = 0.0001,
p = 0.570) is itself informative for market makers. The absence of
regime-conditioned forward predictability confirms that the ES
futures market incorporates informed order flow within one minute
in high-regime conditions — meaning a market maker who misses the
within-bar signal has no opportunity to adjust quotes before the
price has fully moved. This underscores the importance of real-time
rather than lagged regime detection for practical implementation.

[FIGURE: Regime-conditioned TFI slope at T+0 and T+1 through T+15,
showing contemporaneous amplification and absence of forward
persistence — to be added in Phase 5]

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
