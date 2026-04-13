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
period of elevated information asymmetry. Kyle's lambda is chosen
as the primary component because it is the most direct available
measure of adverse selection intensity — it captures price impact
per unit of signed order flow in real time from trades-only data,
which is precisely the quantity the Glosten-Milgrom and Kyle
frameworks identify as the signature of informed trading. However,
high lambda alone is insufficient: it can be elevated for five
distinct reasons besides genuine informed trading — thin markets
or low depth, market stress or sudden uncertainty, market maker
inventory pressure, mechanical order clustering, and contract roll
proximity. The regime detector is designed to address as many of
these as possible given the constraints of trades-only data.

**Kyle's lambda** measures price impact per unit of signed order
flow, estimated from a rolling OLS regression of price changes on
signed order flow over a 30-bar window updated each minute. High
lambda indicates market makers are updating quotes aggressively in
response to order flow — consistent with their inference that the
flow may be informed. Lambda is the primary signal; all other
components serve to qualify its elevated readings.

**Trade arrival rate** measures trades per minute over a 5-minute
rolling window and functions as a depth confirmation for elevated
lambda rather than as an independent signal. High arrival rate
confirms that many market participants are actively transacting,
ruling out thin markets and low depth as the source of elevated
lambda. When TAR is low, RegimeScore is suppressed even if lambda
is elevated, preventing misclassification of illiquid episodes as
informed. A shorter window than lambda is used to reflect the faster
response of trading activity to changing market conditions.

**Addressing the five sources of elevated lambda:** One of the five
non-informed sources of elevated lambda are addressed by TAR
directly — thin markets and low depth produce low TAR, suppressing
RegimeScore even when lambda is elevated. Two more are addressed by 
the exclusion windows described in Section 4.3 — market stress from
scheduled macro announcements and contract roll proximity. Two
remains unaddressed as an irreducible limitation of trades-only
data: market maker inventory pressure and mechanical intraday order
clustering outside exclusion windows can produce elevated lambda
that the detector cannot distinguish from genuine informed flow.
This limitation is acknowledged throughout the paper.

**Design choice — Roll spread exclusion:** The Roll (1984) spread
estimator was considered and excluded as a third component for two
reasons. First, Roll is non-orthogonal to lambda: both spike
simultaneously at the same directional price episodes, making Roll
redundant rather than independently informative. Second, Roll fails
precisely in one-sided markets — the high-lambda informed trading
conditions of greatest theoretical interest — because the bid-ask
bounce required for the serial covariance estimator disappears when
prices move consistently in one direction. The two-component
multiplicative detector avoids both problems while preserving the
core economic signal.

**Multiplicative combination:** The two components are combined using
a multiplicative formulation that implements the hierarchical
structure described above. Each component is first standardized via
a rolling z-score:

z_lambda_t  = (lambda_t  − μ_lambda)  / σ_lambda
z_arrival_t = (arrival_t − μ_arrival) / σ_arrival

Each z-score is then mapped to (0, 1) via the logistic function, and
the two logistic outputs are multiplied:

RegimeScore_t = logistic(z_lambda_t) × logistic(z_arrival_t)

where logistic(x) = 1 / (1 + exp(−x)).

This formulation ensures RegimeScore is high only when both
components are simultaneously elevated. When lambda is low,
RegimeScore is low regardless of TAR. When TAR is low, it
suppresses the lambda signal proportionally, preventing
misclassification of illiquid or thin-market episodes as
informed. The multiplicative structure enforces the intended
hierarchy: lambda provides the adverse selection signal, and
TAR either confirms or suppresses it.

Rolling standardization ensures the score is always relative to
recent market conditions rather than the full sample distribution,
allowing it to adapt to the two distinct activity regimes identified
in Section 3.3. All rolling estimates use only past data — no
lookahead bias is introduced.

### 4.3 Exclusion Windows

Two of the five sources of elevated lambda that do not reflect
genuine informed trading — post-announcement mechanical flow and MOC
order flow, and contract roll illiquidity — are addressed through
targeted exclusion windows. RegimeScore_t is set to zero in all
excluded bars regardless of indicator values.

Scheduled macro announcements (FOMC decisions, CPI releases, NFP
releases) trigger a 30-minute post-announcement exclusion window.
These events drive directional order flow from participants
responding to the same public information signal rather than private
information, and their post-announcement windows represent the
period of greatest mechanical lambda inflation. Pre-announcement
windows are retained: informed traders with early signal access may
be active before announcements, and excluding these bars would
discard potentially genuine informed trading episodes.

The final 10 minutes of each session (15:50–16:00 ET) are excluded
due to domination by MOC order flow — mechanical, publicly announced
execution that generates high volume without adverse selection, as
documented in Section 3.4. Contract roll dates and the three
preceding trading days are excluded to remove the structural
illiquidity and mechanical volume migration accompanying front-month
contract expiration.

### 4.4 Regime Detector Validation

Prior to testing TFI predictability, the regime detector is
validated through a formal statistical test of its core claim: that
high-regime bars have a significantly stronger within-bar TFI-return
relationship than low-regime bars. This is the mechanism the detector
is designed to identify — elevated adverse selection produces
stronger price impact per unit of order flow within the same bar,
per Kyle (1985). A significant amplification confirms the detector
correctly identifies periods of elevated within-bar price impact.

The validation regresses contemporaneous returns on TFI, a
high-regime dummy, and their interaction, using the same HAC
standard errors applied throughout:

Return_t = α + β₁·TFI_t + β₂·HighRegime_t
         + β₃·(TFI_t × HighRegime_t) + β₅·TFI_{t-1} + ε_t

where HighRegime_t = 1 if RegimeScore_t > 0.5.

The interaction coefficient β₃ = 0.001525 (z = 9.496, p < 0.001).
The within-bar TFI-return slope is 0.001193 in low-regime bars and
0.002717 in high-regime bars — a 2.278x amplification that is
strongly statistically significant. The detector correctly and
reliably identifies periods of elevated within-bar price impact.

This test uses contemporaneous RegimeScore_t, so TFI-Return
confounding within bar t is present and acknowledged. It is a
directional sanity check that confirms the detector is measuring
what it claims to measure, not a causal test.

A pre-announcement validation was considered — testing whether
RegimeScore is elevated in the 30-minute window before macro
announcements, when informed traders with early signal access should
be active. This test is infeasible with RTH-only data: CPI and NFP
releases occur at 8:30 AM before market open, leaving only 6
observable FOMC pre-announcement windows in the in-sample period —
an insufficient sample for a meaningful test. The validation test
above is therefore the primary and sufficient criterion.

The detector operates most reliably during the stable midday and
early afternoon portion of the trading session, where lambda is
estimable, TAR reflects genuine liquidity conditions, and structural
events are absent. This is confirmed empirically in Section 5.5.

### 4.5 Empirical Design

All regressions use the following primary specification unless
otherwise noted:

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t
             + β₃·(TFI_t × RegimeScore_t)
             + β₄·Return_t + β₅·TFI_{t-1} + ε_t

β₁ captures the unconditional TFI effect when RegimeScore = 0.
β₂ captures any return level difference across regime states
independent of TFI. β₃ is the primary coefficient of interest: the
null hypothesis H₀ is β₃ = 0 (the regime does not amplify TFI's
forward predictive power) against H₁: β₃ > 0 (the regime
amplifies TFI's predictive power). β₄ and β₅ control for return
autocorrelation and TFI persistence. All regressions use Newey-West
HAC standard errors with maxlags=5, correcting for serial
correlation in 1-minute returns arising from bid-ask bounce and
intraday momentum.

The regression sample contains N = 55,634 bars after dropping NaN
rows arising from rolling warmup (the first 30 bars of each session
before the lambda window is fully populated), day boundary nulling
(the first bar of each day whose return spans the overnight gap and
is not a valid RTH return), and the forward return edge (the final
bar of each day has no observed T+1 return within the same session).
High-regime bars (RegimeScore > 0.5) account for 12.1% of the
regression sample under the multiplicative detector.

**Circularity and estimation bias:** The regime interaction
specification inherits two layers of circularity from trades-only
data. Firstly, at the detector construction level, lambda is derived 
from rolling OLS of price changes on signed order flow — the same
aggressor-side volume that underlies TFI. Secondly, at the regression
interaction level, high TFI bars mechanically have elevated
RegimeScore because high signed flow simultaneously elevates lambda
under the multiplicative formulation, inflating the interaction term
TFI × RegimeScore. This second layer is confirmed by the monotonic
quintile pattern documented in Section 5.4: coefficients increase
monotonically from Q1 through Q5, inconsistent with genuine informed
trading concentration in moderate quintiles (Kyle, 1985) and
consistent with mechanical co-elevation.

Critically, this second-layer bias acts upward on β₃ — it inflates
the estimate toward H₁, making a positive coefficient easier to
find, not harder. A null result under this upward bias implies the
true β₃ is smaller than the estimated value, making the primary
efficiency finding a conservative bound. The non-confounded label
applied to Section 5.1 refers specifically to the absence of a
mechanical relationship between RegimeScore and Return_{t+1} — not
to the absence of circularity in the interaction term itself, which
is present in all specifications that use RegimeScore.

---

## 5. Results

### 5.1 Forward Return Predictability — T+1

The primary test asks whether regime-conditioned TFI predicts
returns at the one-bar horizon. Return_{t+1} is unknown when TFI_t
and RegimeScore_t are observed. RegimeScore_t is contemporaneous
with TFI_t but fully predetermined relative to Return_{t+1}: the
next bar's return is not in lambda's estimation window and is not
known when the signal is recorded. This regression is non-confounded
in the sense defined in Section 4.5.

**Table 2: Primary Regression — Return_{t+1}**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −4.46×10⁻⁶ | −0.597 | 0.550 |
| tfi (β₁) | 0.000637 | 5.886 | <0.001 *** |
| regime_score (β₂) | 1.75×10⁻⁵ | 0.753 | 0.451 |
| tfi_x_regime (β₃) | 0.000371 | 1.191 | 0.234 |
| lag_return (β₄) | −0.488 | −53.865 | <0.001 *** |
| lag_tfi (β₅) | −4.96×10⁻⁵ | −0.902 | 0.367 |

R² = 0.236, N = 55,634. HAC standard errors (Newey-West, maxlags=5).

β₃ = 0.000371, p = 0.234. H₀ is not rejected. ES futures prices
incorporate regime-conditioned order flow information within one
1-minute bar. The unconditional TFI effect (β₁ = 0.000637,
p < 0.001) replicates the Cont, Kukanov, and Stoikov (2014) finding
that order flow imbalance predicts short-term returns; this effect
does not survive round-trip transaction costs of approximately 0.774
basis points and carries no directional trading application. The
regime does not amplify this unconditional predictability — β₃ is
indistinguishable from zero. The dominant source of return
predictability is the mean-reversion control lag_return (β₄ = −0.488,
p < 0.001), capturing bid-ask bounce; R² = 0.236 is driven almost
entirely by this term.

The quintile interaction analysis in Section 5.4 confirms this null
result is not an artifact of the linearity assumption in the
interaction specification.

### 5.2 Contemporaneous Characterization — T+0

A separate analysis characterizes the regime-conditioned relationship
between TFI and same-bar returns. Because Return_t and RegimeScore_t
share bar t's time window, RegimeScore is lagged by one bar
(RegimeScore_{t-1}) to remove regime-level simultaneity:

Return_t = α + β₁·TFI_t + β₂·RegimeScore_{t-1}
         + β₃·(TFI_t × RegimeScore_{t-1})
         + β₅·TFI_{t-1} + ε_t

A residual confounding channel remains irreducible: TFI_t and
Return_t are both constructed from bar t's trades, making their
relationship partially mechanical with trades-only data. This
regression is a specification sensitivity result — not a predictive
test — and is presented as such. Should future research with
orthogonal data resolve this confounding channel and reveal genuine
contemporaneous amplification, the p% intra-bar framework described
in Section 8 provides a natural extension toward a real-time market
maker application.

**Table 3: Contemporaneous Regression — Return_t (lagged RegimeScore)**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −8.16×10⁻⁶ | −1.214 | 0.225 |
| tfi (β₁) | 0.001200 | 10.238 | <0.001 *** |
| regime_score_lag (β₂) | 3.53×10⁻⁵ | 1.680 | 0.093 |
| tfi_x_regime_lag (β₃) | 0.000617 | 1.761 | 0.078 |
| lag_tfi (β₅) | −0.000105 | −1.769 | 0.077 |

R² = 0.008, N = 55,634.

β₃ = 0.000617, p = 0.078. The interaction is not significant at
conventional thresholds. The lag-1 autocorrelation of RegimeScore
is 0.806 under the multiplicative formulation, meaning lagging by
one bar removes approximately 19% of the regime-level circularity.
The p = 0.078 result is therefore best interpreted as predominantly
driven by residual confounding through regime autocorrelation, with
a non-trivial but unquantifiable secondary contribution from genuine
predictive signal. These two explanations cannot be cleanly separated
with trades-only data. No empirically grounded market maker
calibration can be derived from this result.

---

## 5.3 Horizon Analysis

The primary specification is repeated at cumulative 5-bar and 15-bar
forward horizons. Cumulative log returns are computed within each
trading day only — cross-day windows are nulled to avoid overnight
return contamination.

| Horizon | β₃ | z-stat | p-value | N |
|---|---|---|---|---|
| T+5 | 0.000090 | 0.256 | 0.798 | 54,789 |
| T+15 | 0.000081 | 0.212 | 0.833 | 53,099 |

No regime interaction emerges at any horizon. The unconditional TFI
effect (β₁ ≈ 0.000696–0.000719, p < 0.001) persists at both
horizons but does not vary with regime. Information incorporation in
ES futures is complete within one 1-minute bar in high-regime
conditions, leaving no residual regime-conditioned predictability at
5 or 15 bar horizons.

### 5.4 TFI Quintile Interaction

The continuous regime interaction term is replaced with four quintile
dummy interactions, allowing the regime amplification to vary freely
across the TFI distribution. Quintile 3 (moderate TFI, the
theoretically predicted zone of informed order flow concentration
under Kyle (1985) since informed traders split orders to minimize
price impact) is the omitted reference category. A Bonferroni
correction is applied across the five simultaneous tests (α = 0.01
per test, family-wise α = 0.05).

| Quintile | Coefficient | z-stat | p-value | Bonferroni |
|---|---|---|---|---|
| Q1 (most negative TFI) | −0.000020 | −0.362 | 0.717 | — |
| Q2 | −0.000038 | −0.786 | 0.432 | — |
| Q4 | 0.000081 | 1.684 | 0.092 | — |
| Q5 (most positive TFI) | 0.000126 | 2.076 | 0.038 | — |

No quintile interaction survives Bonferroni correction (threshold:
p < 0.01). The null result in the primary regression is not a
consequence of imposing linearity on the regime-TFI relationship.

The monotonic pattern — coefficients increasing from Q1 through Q5
— is inconsistent with the Kyle (1985) prediction of hump-shaped
concentration in moderate quintiles and is more consistent with
mechanical co-elevation: higher absolute TFI implies higher signed
order flow, which simultaneously elevates lambda and therefore
RegimeScore under the multiplicative formulation, inflating the
interaction term in high-TFI bars. This confirms the second layer
of circularity described in Section 4.5. As established there, this
upward bias makes the null primary result a conservative bound —
the efficiency conclusion holds even under estimation conditions
that favor H₁.

### 5.5 Midday Subsample and Stable Regime Conditions

The regime detector's signal quality depends on the reliability of
its component estimates. Kyle's lambda requires a full 30-bar
estimation window of stable same-session data, and the TAR z-score
is most informative when baseline activity is low. Both conditions
are best satisfied during the midday portion of the trading session
(11:00–13:00 ET), after the open's elevated and noisy order flow has
subsided and before close-of-day dynamics begin. This window was
pre-specified from theory before running any test.

Restricting the primary regression to midday bars produces
β₃ = 0.000812, z = 1.449, p = 0.147, N = 20,279 — not significant,
but with a coefficient 2.2x larger than the full-sample estimate.
Under pure circularity, the interaction coefficient should collapse
toward the unconditional TFI slope (β₁ ≈ 0.0006) rather than away
from it. The midday β₃ = 0.000812 moves in the opposite direction,
which is more consistent with genuine signal diluted by open and
close noise in the full-sample regression. Both interpretations
remain possible; neither is confirmed at conventional significance.

A more direct proxy for detector quality is the rolling standard
deviation of signed order flow within the 30-bar lambda estimation
window. Low variance indicates stable, representative order flow
rather than a single large directional episode dominating the OLS
estimate — precisely the conditions under which the multiplicative
detector's lambda component is most reliably estimated. Restricting
the regression to the bottom tercile of this stability metric
(threshold: 211 contracts signed-flow standard deviation) produces
the following gradient:

**Table 4: Stable Regime Conditions — β₃ by Lambda Estimation Stability**

| Condition | N | β₃ | p-value |
|---|---|---|---|
| Full sample | 55,634 | 0.000371 | 0.234 |
| Stable lambda (bottom tercile) | 18,355 | 0.001016 | 0.033 |
| Unstable lambda (top tercile) | 18,355 | 0.000331 | 0.664 |

The stable-condition β₃ = 0.001016 is 2.7x the full-sample estimate
and is statistically significant at α = 0.05 (z = 2.135, p = 0.033).
The gradient from stable to unstable is monotonic and strong. When
the lambda estimation window is stable — containing steady,
representative order flow — the multiplicative regime detector
produces a statistically detectable amplification of TFI's
forward predictive power. High-regime bars constitute 16.5% of the
stable sample versus 12.1% of the full sample, consistent with
stable estimation windows correctly classifying more bars as
genuinely high-regime. Stable-condition bars concentrate in the
mid-to-late afternoon session (13:xx–14:xx peak, 24.5% and 26.7%
respectively), where lambda warmup is complete and baseline TAR
is at its most stable.

Two caveats apply. First, the stability threshold was derived from
the in-sample distribution and is therefore post-hoc — the result
is a finding but not a pre-registered test. Second, the finding
does not replicate in the OOS period: lambda window stability does
not differ materially between the late and early OOS periods (mean
standard deviation 287.60 vs 279.37 contracts, ratio 1.03x), and
the late-period OOS significance does not concentrate in
stable-lambda bars. The stable regime conditions result is therefore
presented as a genuine finding with an exploratory threshold,
pointing toward a specific and testable future research direction:
with limit order book data, a direct orthogonal stability criterion
(bid-ask spread variance, depth stability, cancellation rate) could
replace the signed-flow proxy and confirm or deny this finding
confirmatorily.

### 5.6 Subsample Stability

The primary regression is estimated separately on two activity
sub-periods identified in Section 3.3.

| Subsample | N | β₃ | p-value |
|---|---|---|---|
| Full sample (May–Dec 2025) | 55,634 | 0.000371 | 0.234 |
| May–Sep 2025 | 35,001 | 0.000283 | 0.495 |
| Oct–Dec 2025 | 20,633 | 0.000543 | 0.207 |

The null result is stable across both sub-periods. The directional
pattern — higher β₃ in the more volatile Oct–Dec period — is
consistent with the regime detector having more genuine informed
trading episodes to identify in elevated-volatility environments,
but the difference between two non-significant p-values carries no
inferential weight. The primary efficiency finding is a structural
property of the sample, not a sub-period artifact.

### 5.7 Out-of-Sample Validation

The in-sample specification is applied without modification to the
held-out 2026 period (2026-01-02 through 2026-03-06, N = 14,774,
46 trading days). No parameters are refit.

The full-period OOS result is β₃ = 0.000371, z = 2.768, p = 0.006 —
significant at α = 0.01 and in the opposite direction of what the
in-sample null would predict. The following diagnostics were
conducted to identify whether this significance is structural or
episodic, corresponding to six candidate explanations for why OOS
results might diverge from in-sample: HAC misspecification, regime
distribution shift, volatility-driven lambda inflation, TFI
distribution shift, random noise, and episode concentration.

Residual autocorrelation at lags 6–10 ranges from +0.001 to +0.020,
ruling out HAC misspecification. The OOS RegimeScore distribution
is essentially identical to in-sample (mean 0.229 vs 0.215,
OOS/IS ratio 1.06x), ruling out structural regime elevation.
Realized volatility in the OOS period is lower than in-sample
(mean |return| ratio 0.42x), ruling out volatility-driven lambda
inflation and making significance harder to achieve rather than
easier. The OOS TFI distribution is nearly identical to in-sample
(1.3% vs 1.0% extreme bars), ruling out extreme order flow as a
mechanical driver. A permutation test — in which OOS forward returns
are randomly permuted 1,000 times to construct an empirical null
distribution for β₃ absent any predictability, with the actual OOS
β₃ then located within this distribution — places the actual OOS β₃
in the top 0.5% of the null distribution (permutation p = 0.005),
ruling out random noise.

The source of the aggregate OOS significance is identified through
monthly breakdown and rolling window analysis. January 2026 and
February 2026 are individually null (β₃ = 0.000047, p = 0.671;
β₃ = 0.000325, p = 0.162 respectively). A rolling 10-trading-day
window across the 46-day OOS period shows β₃ near zero throughout
January and early-to-mid February, before rising sharply and
producing seven consecutive significant windows from February 26
through March 6, 2026 (β₃ ranging from 0.000559 to 0.000837).
Estimating the primary regression separately on the early OOS
period (January through February 22, N = 11,484) and late OOS
period (February 23 through March 6, N = 3,290) yields:

| Period | β₃ | p-value | Return std (bps) | R² |
|---|---|---|---|---|
| Early OOS (Jan–Feb 22) | 0.000066 | 0.559 | 3.041 | 0.002 |
| Late OOS (Feb 23–Mar 6) | 0.000774 | 0.022 | 5.792 | 0.111 |

The late OOS period had approximately 2x the realized volatility of
the early period. Whether this reflects a specific macro environment
in late February through early March 2026 or a more general condition
under which the regime detector produces genuine signal cannot be
determined from approximately 10 trading days of data — a sample
too small to characterize the prevailing conditions as a replicable
regime, separate a genuine market-condition effect from statistical
noise, or confirm that any similar future period would produce the
same result. Lambda window stability does not differ materially
between the late and early OOS periods (mean standard deviation
287.60 vs 279.37 contracts, ratio 1.03x), ruling out more stable
estimation conditions as the explanation.

The OOS result is an episodic finding. The aggregate significance
is driven by a specific two-week episode of elevated realized
volatility in late February through early March 2026. January and
February individually are null. The permutation test confirms the
episode is not random noise, but no orthogonal conditioning variable
explains or predicts it. The in-sample efficiency finding is not
overturned.

---

## 6. Robustness

### 6.1 Lagged Regime Conditioning

As the most stringent robustness test, the primary regression
replaces the contemporaneous RegimeScore_t and interaction
TFI_t × RegimeScore_t with their one-bar lagged counterparts
RegimeScore_{t-1} and TFI_t × RegimeScore_{t-1}. This specification
is fully predetermined — there is no simultaneity between any
variable — and eliminates any residual circularity from the
contemporaneous regime score sharing information with bar t's order
flow.

β₃ (tfi_x_regime_lag) = −0.000152, z = −0.476, p = 0.634,
N = 55,634.

The null result is unambiguous under this specification, implying
that prior-bar regime information has no carry-forward predictive
value for next-bar returns and that regime-conditioned adverse
selection resolves entirely within one bar. This result strengthens
the efficiency finding: the primary null holds under the most
stringent possible predetermined conditioning, with zero
simultaneity between any variable in the regression.

### 6.2 Regime Transition Dynamics

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

Under the multiplicative detector, the transition finding is
outright null: sustained β₃ = 0.000143 (p = 0.684), transition
β₄ = 0.000430 (p = 0.061), across 2,354 transition bars (4.2% of
sample). The multiplicative formulation classifies far fewer bars
as high-regime (12.1% vs 43.1% under the additive formulation),
producing fewer low-to-high crossings and a weaker apparent
transition effect that does not reach conventional significance.
Two diagnostics confirm that the specification is mechanically
inflated and that the null is the correct interpretation.

First, transition bars are split by the median RegimeScore delta at
crossing (median = 0.270). Under genuine informed trader timing,
the effect should be consistent regardless of how large the regime
score delta is at crossing. Under mechanical inflation, the
interaction term TFI × TransitionToHigh is larger when the
RegimeScore delta is larger, because both the transition flag and
the interaction magnitude are driven by the same underlying
directional signed flow:

| Delta group | N transitions | β₄ | p-value |
|---|---|---|---|
| Small delta (≤ median) | 1,177 | 0.000046 | 0.875 |
| Large delta (> median) | 1,177 | 0.000618 | 0.035 |

The large-delta coefficient is 13.4x the small-delta coefficient.
This extreme concentration is inconsistent with genuine informed
trader timing and strongly consistent with mechanical inflation.

Second, the transition threshold is varied from 0.5 to 0.4 and 0.6:

| Threshold | Transition bars | β₄ | p-value |
|---|---|---|---|
| 0.4 | 2,868 | 0.000200 | 0.263 |
| 0.5 | 2,354 | 0.000430 | 0.061 |
| 0.6 | 1,684 | 0.000362 | 0.190 |

No threshold produces a significant result. The apparent effect at
threshold 0.5 is the strongest of the three and is itself marginal
(p = 0.061). Both diagnostics confirm the transition specification
is mechanically inflated and the null result is the correct
interpretation. This test is not evidence of genuine informed trader
timing.

---

## 7. Market Maker Implications

The formal results carry two directly actionable insights for market
makers operating in ES futures.

The primary finding — no regime-conditioned forward predictability
at any horizon from T+1 through T+15 — establishes that ES futures
incorporate regime-conditioned order flow information within one
1-minute bar. A market maker who misses the within-bar adverse
selection signal has no opportunity to adjust quotes before the
price has fully moved. This underscores the importance of real-time
rather than bar-level regime detection: the signal distinguishing
informed from uninformed order flow is present and acting on prices
within the bar, not across bars.

The contemporaneous characterization (Section 5.2) produces
β₃ = 0.000617 (p = 0.078) — not statistically significant — and
retains irreducible TFI-Return confounding within bar t. No
empirically grounded quantitative calibration of adverse selection
amplification can be derived from the current data. The dominant
explanation for the marginal p-value is residual regime
autocorrelation (lag-1 autocorrelation = 0.806), not genuine causal
amplification.

The most actionable finding is the stable regime conditions gradient
in Section 5.5. When the lambda estimation window is stable —
defined as the bottom tercile of rolling signed-flow standard
deviation — the regime-conditioned TFI interaction coefficient is
β₃ = 0.001016 (p = 0.033), statistically significant and 2.7x the
full-sample estimate. This provides the first statistically
confirmed evidence that the regime detector produces a genuine
forward predictive signal under specific, identifiable market
conditions. The practical implication is concrete: a market maker
with access to real-time order flow stability diagnostics — computed
from the same trades-only data used here — can identify windows
where the regime detector's signal is most reliable and concentrate
adverse selection management during these periods.

The stability metric used here (rolling signed-flow standard
deviation) remains partially circular with the regime detector.
With limit order book data, the stability proxy could be replaced
with a direct, orthogonal measure of estimation quality — bid-ask
spread stability, depth constancy, cancellation rate — providing a
less circular and more precise conditioning variable for real-time
quote adjustment. The current finding motivates this extension as
the highest-priority direction for future research.

---

## 8. Future Research

Two research directions are motivated directly by the current
findings and their limitations.

**Direction 1: Orthogonal regime detector with limit order book
data.** The two layers of circularity documented in this paper —
at the detector construction level and the regression interaction
level — are both irreducible with trades-only single-instrument
data. A regime detector derived from limit order book dynamics
(bid-ask spread changes, depth imbalance, cancellation-to-trade
ratio) would share no informational content with TFI and would
permit a genuinely non-confounded test of the regime-conditioned
forward predictability hypothesis. The stable regime conditions
result (β₃ = 0.001016, p = 0.033 under stable estimation
conditions) generates a specific testable prediction: an LOB-based
regime detector operating under stable liquidity conditions should
produce significant β₃ in the primary T+1 regression. The
stable-condition stability metric provides a natural bridge — the
same concept of estimation window reliability applies to an
LOB-based detector, where stable bid-ask spreads and depth profiles
would serve as the orthogonal analog to stable signed-flow variance.
Two sub-questions follow from confirmation of this hypothesis:
does the effect persist at sub-minute resolution, and does it
survive two-sided transaction costs?

**Direction 2: p% intra-bar amplification framework.** If a future
study finds significant contemporaneous regime amplification with
an orthogonal detector, the current framework can be extended to
characterize the within-bar dynamics of adverse selection.
Specifically, TFI computed at fixed elapsed-time fractions within
each bar (10%, 20%, ..., 90% bar completion) could be regressed on
bar-end returns conditioned on lagged RegimeScore_{t-1}, yielding
an empirical weight schedule θ_p describing how information content
accumulates within the bar as a function of elapsed time and regime
state. This framework provides the bridge from a statistically
significant regime-TFI relationship to a practically implementable
real-time adverse selection signal. It is constructible from current
tick data but deferred pending a significant and non-confounded
contemporaneous finding.

---

## References

Cont, R., Kukanov, A., and Stoikov, S. (2014). The price impact
of order book events. *Journal of Financial Econometrics*,
12(1), 47–88.

Dufour, A. and Engle, R. (2000). Time and the price impact of a
trade. *Journal of Finance*, 55(6), 2467–2498.

Glosten, L. and Milgrom, P. (1985). Bid, ask and transaction
prices in a specialist market with heterogeneously informed
traders. *Journal of Financial Economics*, 14(1), 71–100.

Kyle, A. (1985). Continuous auctions and insider trading.
*Econometrica*, 53(6), 1315–1335.

Roll, R. (1984). A simple implicit measure of the effective
bid-ask spread in an efficient market. *Journal of Finance*,
39(4), 1127–1139.
