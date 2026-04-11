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
held-out out-of-sample period spanning 2026-01-02 through 2026-03-06
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

The informed trading regime score, RegimeScore_t ∈ [0, 1], is a
continuous measure of the probability that bar t occurs during a
period of elevated information asymmetry. It is constructed from two
components, each motivated by the adverse selection framework of
Glosten and Milgrom (1985) and Kyle (1985).

**Kyle's lambda** measures price impact per unit of signed order
flow, estimated from a rolling OLS regression of price changes on
signed order flow over a 30-bar window updated each minute. High
lambda indicates market makers are updating quotes aggressively
in response to order flow — consistent with their inference that
the flow may be informed. However, high lambda alone is
insufficient: elevated price impact can equally reflect thin
markets, market stress, or mechanical order flow rather than
genuine informed trading.

**Trade arrival rate** measures trades per minute over a 5-minute
rolling window, proxying market depth and active liquidity
provision. High arrival rate confirms many market participants are
actively transacting, ruling out thin depth or structural illiquidity
as the source of elevated lambda. A shorter window than lambda is
used to reflect the faster response of trading activity to changing
market conditions.

The two components are combined into a continuous score through
three steps. First, each component is standardized using a rolling
z-score over a 30-bar window:

z_lambda_t  = (lambda_t  − μ_lambda)  / σ_lambda
z_arrival_t = (arrival_t − μ_arrival) / σ_arrival

Second, the components are combined with theoretically motivated
signs:

RawScore_t = z_lambda_t + z_arrival_t

Third, the raw score is mapped to [0, 1] via logistic transformation:

RegimeScore_t = 1 / (1 + exp(−RawScore_t))

Rolling standardization ensures the score is always relative to
recent market conditions rather than the full sample distribution,
allowing it to adapt to the two distinct activity regimes identified
in Section 3.3. All rolling estimates use only past data — no
lookahead bias is introduced.

**Design choice — Roll spread exclusion:** An earlier version of the
detector included the Roll (1984) spread estimator as a third
component. Roll was subsequently removed for two reasons. First,
the Roll estimator is non-orthogonal to lambda: both components
spike simultaneously at the same directional price episodes, making
Roll redundant rather than independently informative. Second, Roll
fails precisely in one-sided markets — the high-lambda informed
trading conditions of greatest theoretical interest — because the
bid-ask bounce required for the serial covariance estimator
disappears when prices move consistently in one direction. The
two-component detector avoids both problems while preserving the
core economic signal.

Two sources of residual misclassification are acknowledged. Market
maker inventory pressure and mechanical order clustering can produce
elevated lambda in liquid markets without informed trading. Kyle's
lambda is also undefined when signed order flow has zero variance
across the estimation window; these bars are excluded from the
regression sample and are self-selecting as uninformative, as the
absence of directional flow is itself evidence against an informed
trading regime.

### 4.3 Exclusion Windows

Scheduled macro announcements are excluded by setting
RegimeScore_t = 0 for the 30 minutes following each FOMC decision,
CPI release, and NFP release. These events drive directional order
flow from participants responding to the same public information
signal rather than private information, and their post-announcement
windows represent the period of greatest mechanical lambda inflation.
Pre-announcement windows are retained: informed traders with early
signal access may be active in the period before announcements,
and excluding these bars would discard potentially genuine informed
trading episodes.

The final 10 minutes of each session (15:50–16:00 ET) are excluded
due to domination by MOC order flow — mechanical, publicly announced
execution that generates high volume without adverse selection, as
documented in Section 3.4. Contract roll dates and the three
preceding trading days are excluded to remove the structural
illiquidity and mechanical volume migration that accompany
front-month contract expiration.

### 4.4 Regime Detector Validation

Prior to testing TFI predictability, the regime detector is
validated against two independent criteria. First, realized
volatility should be higher in high-RegimeScore bars — informed
trading generates volatility through aggressive quote updating even
though volatility is not a regime condition. Second, RegimeScore
should be elevated in the period before scheduled macro
announcements, when informed traders with early signal access are
most active.

A decile analysis confirms the detector is directionally correct —
the highest genuine RegimeScore decile has elevated forward return
volatility (std = 0.001172) relative to middle deciles
(std ≈ 0.000900-0.000978). The amplification is modest because the
most extreme high-lambda episodes are excluded by the announcement
and MOC windows by design. The contemporaneous TFI-return slope is
1.80×10⁻³ in high-regime bars versus 9.66×10⁻⁴ in low-regime bars,
consistent with informed order flow having greater within-bar price
impact in high-regime conditions.

The detector operates most reliably during the stable midday and
early afternoon portion of the trading session, where lambda is
estimable, trade arrival rate reflects genuine liquidity conditions,
and structural events are absent. This intraday pattern is confirmed
empirically by the stable regime conditions analysis in Section 4.6.

### 4.5 Empirical Tests

**Primary specification:**

All regressions use the following primary specification unless
otherwise noted:

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t
             + β₃·(TFI_t × RegimeScore_t)
             + β₄·Return_t + β₅·TFI_{t-1} + ε_t

β₁ captures the unconditional TFI effect when RegimeScore = 0.
β₂ captures any return level difference across regime states
independent of TFI. β₃ is the primary coefficient of interest —
a significant positive β₃ would indicate that the regime detector
identifies periods where TFI's predictive power for next-bar returns
is genuinely amplified. β₄ and β₅ control for return autocorrelation
and TFI persistence. All regressions use Newey-West HAC standard
errors with maxlags=5.

The regression sample contains N = 55,634 bars after dropping
NaN rows arising from rolling warmup, day boundary nulling, and
the forward return edge. High-regime bars (RegimeScore > 0.5)
account for 43.1% of the regression sample.

**Circularity and estimation bias:** The regime interaction
specification inherits two layers of circularity from the use of
trades-only data. At the detector construction level, lambda is
derived from rolling OLS of price changes on signed order flow —
the same aggressor-side volume that underlies TFI. At the regression
interaction level, the quintile interaction analysis (Section 4.6)
reveals that high TFI bars mechanically have elevated RegimeScore
because high signed flow simultaneously elevates lambda, inflating
the interaction term TFI × RegimeScore. This second-layer bias acts
upward on β₃ — it makes finding a positive coefficient easier, not
harder. As a consequence, the null result in the primary regression
holds even under estimation conditions favorable to the alternative
hypothesis, strengthening rather than weakening the efficiency
conclusion.

---

## 4.5 Primary Results

### 4.5.1 Forward Return Predictability — T+1

The primary test asks whether regime-conditioned TFI predicts
returns at the one-bar horizon — a genuinely predictive question
where the outcome (Return_{t+1}) is unknown when the signal
(TFI_t, RegimeScore_t) is observed. RegimeScore_t is contemporaneous
with TFI_t but fully predetermined relative to Return_{t+1}: the
next bar's return is not in lambda's estimation window and is not
known when the signal is recorded. This regression is non-confounded.

**Table 2: Primary Regression — Return_{t+1}**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −4.42×10⁻⁶ | −0.486 | 0.627 |
| tfi (β₁) | 0.000628 | 4.695 | <0.001 *** |
| regime_score (β₂) | 8.42×10⁻⁶ | 0.562 | 0.574 |
| tfi_x_regime (β₃) | 0.000203 | 0.964 | 0.335 |
| lag_return (β₄) | −0.488 | −53.862 | <0.001 *** |
| lag_tfi (β₅) | −4.99×10⁻⁵ | −0.907 | 0.365 |

R² = 0.236, N = 55,634. HAC standard errors (Newey-West, maxlags=5).

β₃ = 0.000203, p = 0.335. The null hypothesis — that the regime
does not amplify TFI's forward predictive power — is not rejected.
ES futures prices incorporate regime-conditioned order flow
information within one 1-minute bar. The unconditional TFI effect
(β₁ = 0.000628, p < 0.001) replicates the Cont, Kukanov, and
Stoikov (2014) finding that order flow imbalance predicts short-term
returns, but this effect does not concentrate in high-regime
conditions. The dominant source of return predictability in the
regression is the mean reversion control lag_return (β₄ = −0.488,
p < 0.001), capturing bid-ask bounce; R² = 0.236 is driven almost
entirely by this term.

The quintile interaction analysis in Section 4.6 confirms this null
result is not an artifact of the linearity assumption in the
interaction specification.

### 4.5.2 Contemporaneous Characterization — T+0

A separate analysis characterizes the regime-conditioned relationship
between TFI and same-bar returns. Because Return_t and RegimeScore_t
share bar t's time window, simultaneous estimation would be
confounded at the regime level; RegimeScore is therefore lagged by
one bar (RegimeScore_{t-1}) to remove regime-level simultaneity:

Return_t = α + β₁·TFI_t + β₂·RegimeScore_{t-1}
         + β₃·(TFI_t × RegimeScore_{t-1})
         + β₅·TFI_{t-1} + ε_t

A residual confounding channel remains: TFI_t and Return_t are both
constructed from bar t's trades, making their relationship partially
mechanical and irreducible with trades-only single-instrument data.
This regression is therefore presented as a specification sensitivity
result rather than a causal finding.

**Table 3: Contemporaneous Regression — Return_t (lagged RegimeScore)**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −8.26×10⁻⁶ | −1.001 | 0.317 |
| tfi (β₁) | 0.001205 | 8.045 | <0.001 *** |
| regime_score_lag (β₂) | 1.77×10⁻⁵ | 1.288 | 0.198 |
| tfi_x_regime_lag (β₃) | 0.000425 | 1.830 | 0.067 |
| lag_tfi (β₅) | −0.000128 | −1.757 | 0.079 |

R² = 0.008, N = 55,634.

β₃ = 0.000425, p = 0.067. The interaction is not significant at
conventional thresholds. The lag-1 autocorrelation of RegimeScore
is 0.8427, meaning lagging by one bar removes only approximately
16% of the regime-level circularity — RegimeScore_{t-1} closely
approximates RegimeScore_t in most consecutive bars, leaving
substantial residual confounding. The p = 0.067 result is therefore
best interpreted as predominantly driven by this residual confounding,
with a non-trivial but unquantifiable secondary contribution from
genuine predictive signal. These two explanations cannot be cleanly
separated with trades-only data.

The initial version of this regression, using a three-component
detector including the Roll spread and a contemporaneous rather than
lagged RegimeScore, produced β₃ = 0.0015, z = 7.214, p < 0.001.
The collapse to β₃ = 0.000425, p = 0.067 under the cleaner
two-component, lagged-regime specification is itself the central
finding of this characterization: the apparent contemporaneous
amplification was substantially circularity-driven. No empirically
grounded market maker calibration application can be derived from
this result.

---

## 4.6 Additional Tests

### 4.6.1 Horizon Analysis

The primary specification is repeated at cumulative 5-bar and
15-bar forward horizons. Cumulative log returns are computed within
each trading day only — cross-day windows are nulled to avoid
overnight return contamination.

| Horizon | β₃ | z-stat | p-value | N |
|---|---|---|---|---|
| T+5 | 0.000012 | 0.050 | 0.960 | 54,789 |
| T+15 | −0.000098 | −0.373 | 0.709 | 53,099 |

No regime interaction emerges at any horizon. The unconditional TFI
effect (β₁ ≈ 0.00071–0.00078, p < 0.001) persists at both horizons
but does not vary with regime. Information incorporation in ES
futures is complete within one 1-minute bar in high-regime
conditions, leaving no residual regime-conditioned predictability
at 5 or 15 bar horizons.

### 4.6.2 Subsample Stability

The primary regression is estimated separately on two activity
sub-periods identified in Section 3.3.

| Subsample | N | β₃ | p-value |
|---|---|---|---|
| Full sample (May–Dec 2025) | 55,634 | 0.000203 | 0.335 |
| May–Sep 2025 | 35,001 | 0.000177 | 0.524 |
| Oct–Dec 2025 | 20,633 | 0.000251 | 0.399 |

The null result is stable across both sub-periods. The directional
pattern — modestly higher β₃ in the more volatile Oct–Dec period —
is consistent with the regime detector having slightly more genuine
informed trading episodes to identify in elevated-volatility
environments, but the difference between two non-significant
p-values carries no inferential weight. The primary finding of no
regime-conditioned forward predictability is a structural property
of the sample, not a sub-period artifact.

### 4.6.3 Out-of-Sample Validation

The in-sample specification is applied without modification to the
held-out 2026 period (2026-01-02 through 2026-03-06, N = 14,774,
46 trading days). No parameters are refit.

The full-period OOS result is β₃ = 0.000239, z = 2.908, p = 0.004.
This is significant at α = 0.01 and is in the opposite direction of
what the in-sample null result would predict. Seven diagnostic tests
were conducted to determine whether this significance is structural
or episodic.

HAC adequacy is confirmed: residual autocorrelation at lags 6–10
ranges from +0.001 to +0.020, ruling out standard error inflation
from insufficient lag truncation. The OOS RegimeScore distribution
is essentially identical to in-sample (mean 0.4618 vs 0.4357,
OOS/IS ratio 1.06x), ruling out structural regime elevation.
Realized volatility in the OOS period is lower than in-sample
(mean |return| 0.000224 vs 0.000533, ratio 0.42x), confirming
the OOS period was not more volatile — this rules out volatility-
driven mechanical lambda inflation and in fact makes significance
harder to achieve, not easier. The OOS TFI distribution is nearly
identical to in-sample (1.3% vs 1.0% extreme bars), ruling out
extreme order flow as a mechanical driver. A permutation test
(N = 1,000 shuffles of OOS forward returns) places the actual OOS
β₃ in the top 0.5% of the null distribution, confirming the result
is not random noise.

The source of the aggregate OOS significance is identified by
monthly breakdown and rolling window analysis. January 2026 and
February 2026 are individually null (β₃ = 0.000060, p = 0.412;
β₃ = 0.000169, p = 0.209 respectively). A rolling 10-trading-day
window across the 46-day OOS period shows β₃ near zero throughout
January and early-to-mid February, before rising sharply and
producing seven consecutive significant windows from February 26
through March 6, 2026 (β₃ ranging from 0.000356 to 0.000531).
Estimating the primary regression separately on the early OOS
period (January through February 22, N = 11,484) and late OOS
period (February 23 through March 6, N = 3,290) yields:

| Period | β₃ | p-value | Return std (bps) | R² |
|---|---|---|---|---|
| Early OOS (Jan–Feb 22) | 0.000046 | 0.515 | 3.041 | 0.002 |
| Late OOS (Feb 23–Mar 6) | 0.000531 | 0.012 | 5.792 | 0.112 |

The late OOS period had approximately 2x the realized volatility of
the early period and a substantially stronger lag_return
mean-reversion coefficient (−0.358 vs −0.053), indicating more
normal return dynamics consistent with a period of elevated genuine
price impact. Whether this reflects a specific macro environment
in late February and early March 2026 or a more general condition
under which the regime detector produces genuine signal cannot be
determined from two weeks of data. Lambda window stability —
measured by the rolling standard deviation of signed order flow
in the 30-bar estimation window — does not differ materially
between the late and early OOS periods (mean std 287.60 vs 279.37
contracts, ratio 1.03x), ruling out the possibility that more
stable estimation conditions explain the late OOS significance.

The OOS result is presented as an episodic finding. The aggregate
significance (p = 0.004) is driven by a specific two-week episode
in late February through early March 2026, during which realized
volatility was elevated relative to the preceding period. January
and February individually are null. The permutation test confirms
the episode is not random noise, but no orthogonal conditioning
variable explains or predicts it. The in-sample efficiency finding
is not overturned.

### 4.6.4 TFI Quintile Interaction

The continuous regime interaction term is replaced with four quintile
dummy interactions, allowing the regime amplification to vary freely
across the TFI distribution. Quintile 3 (moderate TFI) is the
omitted reference category. A Bonferroni correction is applied
across the five simultaneous tests (α = 0.01 per test, family-wise
α = 0.05).

| Quintile | Coefficient | z-stat | p-value | Bonferroni |
|---|---|---|---|---|
| Q1 (most negative TFI) | −0.000013 | −0.382 | 0.702 | — |
| Q2 | −0.000025 | −1.000 | 0.317 | — |
| Q4 | 0.000047 | 1.811 | 0.070 | — |
| Q5 (most positive TFI) | 0.000071 | 1.984 | 0.047 | — |

No quintile interaction survives Bonferroni correction (threshold:
p < 0.01). The null result in the primary regression is not a
consequence of imposing linearity on the regime-TFI relationship.

The monotonic pattern across quintiles — coefficients increasing
from Q1 through Q5 — is informative about the circularity structure
of the regression. Under Kyle (1985), informed traders split orders
to minimize price impact, implying that the regime-TFI interaction
should concentrate in moderate quintiles rather than at the extremes.
The observed monotonic pattern is inconsistent with this prediction
and is more consistent with a mechanical explanation: higher absolute
TFI implies higher signed order flow, which elevates lambda and
therefore RegimeScore, mechanically inflating the interaction term
in high-TFI bars. This confirms a second layer of circularity
operating within the regression itself, beyond the detector
construction level. As noted in Section 4.5, this upward bias in β₃
makes the null result more conservative — the efficiency conclusion
holds even under favorable estimation conditions for the alternative
hypothesis.

### 4.6.5 Midday Subsample and Stable Regime Conditions

The regime detector's signal quality depends on the reliability of
its component estimates. Kyle's lambda requires a full 30-bar
estimation window of stable same-session data, and the trade arrival
rate z-score is most informative when baseline activity is low.
Both conditions are best satisfied during the midday portion of the
trading session (11:00–13:00 ET), after the open's elevated and
noisy order flow has subsided and before close-of-day dynamics begin.
This window was pre-specified from theory before running any test.

Restricting the primary regression to midday bars produces
β₃ = 0.000549, z = 1.398, p = 0.162, N = 20,279 — not significant,
but with a coefficient 2.7x larger than the full-sample estimate.
The circularity explanation for this directional improvement is
constrained by the following observation: under pure mechanical
inflation, the interaction coefficient should collapse toward the
unconditional TFI slope (β₁ ≈ 0.0006) rather than away from it.
The midday β₃ = 0.000549 moves in the opposite direction, which is
more consistent with genuine signal diluted by open and close noise
in the full-sample regression. Both interpretations remain possible;
neither is confirmed at conventional significance thresholds.

A more direct proxy for detector quality is the rolling standard
deviation of signed order flow within the 30-bar lambda estimation
window. Low variance in this window indicates stable, representative
order flow rather than a single large directional episode dominating
the OLS estimate. Restricting the regression to the bottom tercile
of this stability metric (threshold: 211 contracts signed-flow std)
produces the following gradient:

| Condition | N | β₃ | p-value |
|---|---|---|---|
| Full sample | 55,634 | 0.000203 | 0.335 |
| Stable lambda (bottom tercile) | 18,355 | 0.000629 | 0.074 |
| Unstable lambda (top tercile) | 18,355 | 0.000239 | 0.587 |

The stable-condition β₃ = 0.000629 is 3.1x the full-sample estimate,
and the gradient from stable to unstable is monotonic. High-regime
bars constitute a larger fraction of the stable sample (51.6% vs
43.1%), consistent with stable estimation windows correctly
classifying more bars as high-regime. Stable-condition bars
concentrate in the mid-to-late afternoon (13:xx–14:xx peak),
confirming that the time-based midday window and the stability-based
criterion capture related but not identical sets of bars.

This result is exploratory: the stability threshold was derived
from the in-sample distribution and does not replicate in the OOS
period. It is presented as a hypothesis for future research — with
limit order book data, a direct orthogonal stability criterion
(bid-ask spread variance, depth stability, cancellation rate) could
replace the signed-flow proxy and be tested confirmatorily.

---

## 4.7 Robustness

### 4.7.1 Lagged Regime Conditioning

As the most stringent robustness test, the primary regression
replaces the contemporaneous RegimeScore_t and interaction
TFI_t × RegimeScore_t with their one-bar lagged counterparts
RegimeScore_{t-1} and TFI_t × RegimeScore_{t-1}. This specification
is fully predetermined — there is no simultaneity between any
variable — and eliminates any residual circularity from the
contemporaneous regime score sharing information with bar t's
order flow.

β₃ (tfi_x_regime_lag) = −0.000089, z = −0.417, p = 0.677,
N = 55,634.

The null result is unambiguous under this specification. Prior-bar
regime information has no carry-forward predictive value for next-bar
returns. Regime-conditioned adverse selection resolves entirely
within one bar, leaving no exploitable signal at any lag structure.
This result strengthens the efficiency finding: the primary null
holds not only in the contemporaneous regime specification but also
under the most stringent possible predetermined conditioning.

### 4.7.2 Regime Transition Dynamics

An additional specification tests whether TFI is differentially
predictive at the first bar of a regime transition — the moment
when RegimeScore crosses 0.5 from below — relative to sustained
high-regime periods. A transition dummy is constructed as
TransitionToHigh_t = 1 if RegimeScore_t > 0.5, RegimeScore_{t-1}
≤ 0.5, and the prior bar was not in an announcement exclusion window
(to prevent false transitions from exclusion resets):

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t
             + β₃·(TFI_t × RegimeScore_t)
             + β₄·(TFI_t × TransitionToHigh_t)
             + β₅·Return_t + β₆·TFI_{t-1} + ε_t

The initial result — sustained β₃ = 0.000140 (p = 0.512),
transition β₄ = 0.000275 (p = 0.018) across 4,376 transition
bars (7.9% of sample) — appeared to show that TFI is more
predictive at regime transitions than during sustained high-regime
conditions. Two diagnostic tests are conducted to evaluate whether
this reflects genuine informed trader timing or mechanical inflation.

First, transition bars are split by the median RegimeScore delta
at crossing (median = 0.307). Under genuine informed trader timing,
the transition effect should be consistent regardless of the
magnitude of the crossing — a trader does not selectively
concentrate order flow only at large-delta transitions. Under
the circularity explanation, the interaction term TFI × TransitionToHigh
is mechanically larger when the regime score delta is larger, because
both the transition flag and the interaction magnitude are driven
by the same underlying directional signed flow. The results show:

| Delta group | N transitions | β₄ | p-value |
|---|---|---|---|
| Small delta (≤ median, 0.307) | 2,188 | 0.000063 | 0.633 |
| Large delta (> median, 0.307) | 2,188 | 0.000414 | 0.016 |

The large-delta coefficient is 6.6x the small-delta coefficient.
This concentration is inconsistent with genuine informed trader
timing and strongly consistent with mechanical inflation.

Second, the transition threshold is varied from 0.5 to 0.4 and 0.6.
If the finding reflects a genuine market phenomenon, it should be
robust to the specific crossing level. If it is threshold-specific,
it is more likely an artifact.

| Threshold | Transition bars | β₄ | p-value |
|---|---|---|---|
| 0.4 | 4,112 | 0.000400 | 0.001 |
| 0.5 | 4,376 | 0.000275 | 0.018 |
| 0.6 | 4,195 | 0.000174 | 0.154 |

The finding is significant at thresholds 0.4 and 0.5 but disappears
at 0.6. Lower thresholds are associated with larger average
RegimeScore deltas at crossing, producing more mechanical inflation;
higher thresholds require larger underlying changes to cross,
reducing the mechanical component. The threshold dependence mirrors
the delta magnitude finding.

Both diagnostics consistently support the mechanical inflation
explanation. The transition dynamics result is substantially
explained by circularity and is not interpreted as evidence of
genuine informed trader timing.

---

## 5. Market Maker Implications

The formal results provide two directly actionable insights for
market makers operating in ES futures.

The primary finding — no regime-conditioned forward predictability
at any horizon from T+1 through T+15 — establishes that ES futures
incorporate regime-conditioned order flow information within one
1-minute bar. A market maker who misses the within-bar adverse
selection signal has no opportunity to adjust quotes before the
price has fully moved. This underscores the importance of real-time
rather than bar-level regime detection for practical implementation:
the signal that distinguishes informed from uninformed order flow
is present and acting on prices within the bar, not across bars.

The contemporaneous characterization (Section 4.5.2) was initially
intended to provide a quantitative calibration for real-time quote
widening — specifically, the degree to which the regime detector
amplifies the within-bar TFI-return slope. Under the initial
specification (contemporaneous RegimeScore, three-component detector),
β₃ = 0.0015 implied a 2.7x amplification at the mean high-regime
score. This finding does not survive the cleaner specification:
with RegimeScore lagged by one bar and the Roll spread component
removed, β₃ = 0.000425 (p = 0.067) is not statistically significant.
The dominant explanation is residual confounding through regime
autocorrelation (lag-1 autocorrelation = 0.8427), rather than
genuine causal amplification. No empirically grounded quantitative
calibration of adverse selection amplification can be derived from
the current data.

The most actionable directional finding from the additional tests
is the stable regime conditions gradient (Section 4.6.5): when
the lambda estimation window is stable — defined as the bottom
tercile of rolling signed-flow standard deviation — the
regime-conditioned TFI interaction coefficient (β₃ = 0.000629,
p = 0.074) is 3.1x the full-sample estimate and approaches
conventional significance. This suggests that the regime detector
produces its strongest signal precisely when its estimation inputs
are most reliable, and that the ability to identify these stable
estimation windows — using real-time order flow diagnostics —
may be the key conditioning variable for practical adverse selection
management. With limit order book data, the signed-flow stability
proxy could be replaced with a direct, orthogonal measure of
estimation quality (bid-ask spread stability, depth constancy,
low cancellation rate), providing a more precise and less circular
signal for real-time quote adjustment.

---

## 6. Future Research

Two research directions are motivated directly by the current
findings and their limitations.

**Direction 1: Orthogonal regime detector with limit order book data.**
The two layers of circularity documented in this paper — at the
detector construction level and the regression interaction level —
are both irreducible with trades-only single-instrument data. A
regime detector derived from limit order book dynamics (bid-ask
spread changes, depth imbalance, cancellation-to-trade ratio) would
share no informational content with TFI and would permit a genuinely
non-confounded test of the regime-conditioned forward predictability
hypothesis. The stable regime conditions gradient (β₃ = 0.000629,
p = 0.074 under stable estimation conditions) and the midday
directional improvement generate a specific testable prediction:
an LOB-based regime detector operating under stable liquidity
conditions should produce significant β₃ in the primary T+1
regression. Two sub-questions follow from confirmation of this
hypothesis: does the effect persist at sub-minute resolution, and
does it survive two-sided transaction costs?

**Direction 2: p% intra-bar amplification framework.**
If a future study finds significant contemporaneous regime
amplification with an orthogonal detector, the current framework
can be extended to characterize the within-bar dynamics of adverse
selection. Specifically, TFI computed at fixed elapsed-time
fractions within each bar (10%, 20%, ..., 90% bar completion)
could be regressed on bar-end returns conditioned on lagged
RegimeScore_{t-1}, yielding an empirical weight schedule θ_p
describing how information content accumulates within the bar
as a function of elapsed time and regime state. This framework
provides the bridge from a statistically significant regime-TFI
relationship to a practically implementable real-time adverse
selection signal. It is constructible from current tick data but
deferred pending a significant and non-confounded contemporaneous
finding.

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
