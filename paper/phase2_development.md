# Phase 2 — Research Question Development

## Overview

This document traces the development of the research question for
this project: the intellectual path from raw data and initial
intuitions to a precise, theoretically grounded empirical question.
It is written to be transparent about the reasoning process, the
dead ends, and the decisions made at each stage.

---

## 1. Starting Point — What the Data Can Answer

The dataset — ES futures trades with aggressor side, price, size,
and timestamp — naturally supports questions about order flow and
price discovery. The fundamental question in this space is whether
the direction and intensity of executed order flow predicts
subsequent price movement, and under what conditions this
relationship is strongest.

The unconditional relationship between order flow imbalance
and short-term returns is already well-established in equity 
markets (Cont, Kukanov, and Stoikov, 2014). The contribution of
this study is to examine whether this relationship holds in
ES futures specifically, and whether it varies systematically
with the informed trading composition of order flow.

---

## 2. The Core Intuition — Why TFI in Futures Is Interesting

Financial markets move to incorporate information about the
underlying asset's fundamental value. This happens through the
trading activity of informed participants — those with private
information about where the price should be. Unlike in equity
markets, ES futures trade on a pure order-driven market; 
participants include institutional hedgers, systematic 
quantitative traders, arbitrageurs, and market makers.

Trade Flow Imbalance (TFI) — the normalized difference between
buyer-initiated and seller-initiated volume within a time window
— captures the aggregate directional pressure of all participants. 
The signal is theoretically motivated; if informed traders are 
buying because they believe the price is too low, TFI will be 
positive and subsequent returns should be positive as the market 
incorporates the information. 

The problem is that TFI mixes informed and uninformed flow. An
index fund rebalancing, a retail trader closing a position, or a
market maker managing inventory all contribute to TFI without
carrying information about future price direction. Unconditionally,
this dilution reduces TFI's predictive power. The research question
therefore becomes; can we identify market states where TFI reflects
a higher proportion of informed flow, and does TFI predict returns
more strongly in those states?

---

## 3. Characterizing Informed Trading Regimes

### 3.1 The Informed/Uninformed Decomposition Problem

The distinction between informed and uninformed trading is central
to market microstructure theory and directly motivates the regime
conditioning approach taken here.

Glosten and Milgrom (1985) model the bid-ask spread as compensation 
for adverse selection; market makers who trade with informed 
counterparties lose money on average because the informed trader 
knows something they do not (Glosten and Milgrom, 1985). To break 
even, market makers widen spreads in proportion to the probability 
that any given trade is informed. A key implication is that spread 
width reflects the market's expectation of informed trading activity 
— wider spreads signal higher information asymmetry.

Kyle (1985) models how informed traders behave given this
environment (Kyle, 1985). Rather than trading aggressively and 
immediately revealing their information, informed traders disguise 
their positions by spreading orders over time. Price moves gradually
as market makers infer the direction of informed flow. The rate
at which prices respond to order flow — price impact — reflects
the degree of information asymmetry: higher impact means the
market is incorporating more private information per unit of
order flow.

Together these models make a shared empirical prediction: when
informed trading is more prevalent, price impact is higher and
order flow is more predictive of subsequent returns. This
prediction is the theoretical foundation for the regime
conditioning approach — if we can identify periods when informed
trading is more active, TFI should be more predictive of returns
in those periods than unconditionally.

### 3.2 VPIN — Considered and Partially Rejected

The Volume-synchronized Probability of Informed Trading (VPIN),
developed by Easley, Lopez de Prado, and O'Hara (2012), directly 
estimates the proportion of informed trading from order flow 
(Easley, Lopez de Prado, and O'Hara, 2012). VPIN divides trading 
into fixed-volume buckets and measures the average absolute 
imbalance across buckets as a proxy for the probability that any 
given trade is informed.

VPIN was seriously considered as the primary regime indicator.
Its theoretical appeal is significant — it directly targets the
informed/uninformed decomposition rather than using a proxy. After
careful analysis, several limiting assumptions were identified:

**Assumption 1:** Informed traders all trade in one direction.
In practice, different informed traders may have conflicting
signals or trade both sides to disguise positions.

**Assumption 2:** Uninformed traders arrive symmetrically. 
In reality, systematic uninformed flows (MOC orders, index
rebalancing, stop-loss cascades) create predictable one-sided
uninformed pressure that VPIN misclassifies as informed.

**Assumption 3:** Trade arrival follows stationary independent
Poisson processes. Two sub-violations apply. Stationarity
fails intraday — trade arrival at the open is roughly five
times higher than at midday, biasing intraday VPIN estimates.
Independence fails due to trade clustering — activity brings 
more activity in ways that volume buckets only partially correct.

**Assumption 4:** Information events affect one side only. 
Macroannouncements often cause two-sided informed responses 
as participants interpret the same news differently.

The verdict: VPIN is retained as a robustness check computed at
the daily level (where the intraday stationarity problem averages
out, partially addressing assumption 3) but is not used as the 
primary regime indicator due to these limitations that are not
patchable without introducing even more limitations. Daily VPIN 
provides a secondary test of whether results are robust to the 
choice of regime indicator.

### 3.3 Kyle's Lambda as Primary Regime Indicator

Kyle's lambda — the price impact coefficient from regressing
price changes on signed order flow — is a more direct measure of
information asymmetry than VPIN. While VPIN infers informed
trading from imbalance patterns, lambda measures the actual
price response to order flow, which is the ultimate consequence
of informed trading activity.

High lambda means market makers are updating quotes aggressively
in response to order flow — consistent with their inference that
the flow may be informed. This is theoretically grounded in the
Kyle (1985) model, where lambda is the equilibrium price impact
coefficient that reflects the degree of information asymmetry.

The disambiguation problem: high lambda can indicate informed
trading but also thin markets, market stress, market maker
inventory pressure, mechanical order clustering, or contract
roll proximity — all of which create elevated price impact
without informed trading being present.

### 3.4 Defining the Lambda Disambiguation Problem

High lambda is necessary but not sufficient for detecting
informed trading. Five alternative explanations must be
considered and addressed:

**Thin markets / low depth:** When few market makers are
quoting or available depth is shallow, even small order
flow moves price significantly. Spreads typically widen
as market makers demand greater compensation for providing
liquidity with few competitors. Addressable: wide spreads
and low trade activity are observable proxies for thin
market conditions.

**Market stress or sudden uncertainty:** Flash crashes,
unexpected news, or circuit breaker proximity cause market
makers to pull quotes or post very wide spreads. Any order
flow moves price dramatically through suddenly thin
markets. Addressable for sustained stress: spreads widen
and trade arrival drops before impact fully materializes.
Residual: the first moments of sudden onset stress may
briefly contaminate observations before spreads and
arrival respond.

**Market maker inventory pressure:** Market makers who
have accumulated large one-sided inventory skew quotes
directionally to discourage further flow, creating price
impact unrelated to information. Not directly addressable:
inventory states are unobservable from trades-only data.
A cumulative TFI filter was considered and rejected —
sustained one-sided TFI is equally consistent with
genuine informed trading.

**Mechanical order clustering:** Algorithmic traders
submitting correlated orders around technical price levels
or round numbers create apparent directional flow without
information content. Not addressable: order-level
submission data required to distinguish clustered
uninformed flow from genuine directional pressure.

**Contract roll proximity:** As the front-month contract
approaches expiration, liquidity migrates to the next
contract. Lambda on the expiring contract rises from
structural illiquidity rather than information.
Addressable: roll dates are known in advance and
liquidity migration begins predictably in the days
before the formal roll.

### 3.5 Addressing the Lambda Disambiguation Problem

Three conditions implement the available solutions:

**Condition 1: Low Roll (1984) spread estimate**

When a bid-ask spread exists, trade prices bounce between
bid and ask as buyers and sellers alternate hitting the
market — a price increase (buyer hitting the ask) tends
to be followed by a price decrease (seller hitting the
bid). Consecutive price changes therefore have opposite
signs and their serial covariance is negative. Roll (1984)
showed that the spread equals 2√(max(0, −Cov(ΔP_t,
ΔP_{t−1}))): recoverable from this covariance alone
without observing quotes directly (Roll, 1984).

*Addresses:* Thin markets and sustained market stress —
both produce wide spreads detectable by Roll.
*Residual:* Roll fails in strongly one-sided markets
because the bid-ask bounce disappears. Condition 2
compensates.

**Condition 2: High trade arrival rate**

Trades per minute over a rolling window proxies market
depth and active liquidity provision. High arrival rate
confirms many market makers are actively quoting and
reasonable depth is present.

*Addresses:* Thin markets — jointly with Roll, providing
a complementary signal that remains informative in
one-sided markets where Roll fails.
*Residual:* Inventory pressure and mechanical clustering
can coexist with normal arrival rates.

**Condition 3: Exclusion windows**

*Final 10 minutes (15:50–16:00 ET):* MOC order flow —
mechanical, publicly announced, non-information-driven.
Phase 1 confirmed no volatility spike at close despite
massive volume, consistent with uninformed execution
generating high lambda without informed trading.

*30-minute windows around FOMC, CPI, NFP:* Public
information events driving directional TFI from 
participants responding to the same public signal rather 
than private information.

*Contract roll dates and three preceding trading days:*
Mechanical liquidity migration from front-month to next
contract. The three-day pre-roll window captures the
gradual thinning that begins before the formal roll date.

*Addresses:* Contract roll proximity — fully. MOC and
announcement effects — well addressed. Residual: sudden
unexpected shocks in the first moments before spreads
and arrival respond.

**Remaining limitations**

Three sources of residual misclassification are not fully
addressable from these three conditions and trades-only data.

Market maker inventory pressure and mechanical order clustering
can produce elevated lambda in liquid markets without informed
trading. Both introduce noise and increase misclassification
of uninformed periods as informed, diluting the regime signal
and biasing against finding a significant result.

The Roll spread estimator becomes unreliable when order flow
is strongly one-sided — the bid-ask bounce disappears as
consecutive price changes move in the same direction. This
failure occurs precisely in high-lambda informed trading
conditions. Trade arrival rate partially compensates by
remaining informative regardless of flow directionality,
but during sustained directional episodes the Roll component
contributes little, effectively reducing the detector to a
two-component measure (still not counterproductive).

Additionally, the 30-minute rolling window requires a warmup 
period at the start of each trading session, excluding the 
first 30 minutes of each day from regime detection.

### 3.6 The Complete Informed Trading Regime
```
Informed Trading Regime =

    [1] High Kyle's lambda
        Price impact per unit of signed order flow is
        elevated. Market makers are updating quotes
        aggressively, consistent with informed flow.

    [2] Low Roll spread estimate
        Bid-ask tightness is normal. Rules out structural
        illiquidity and sustained market stress.

    [3] High trade arrival rate
        Market depth and liquidity provision are normal.
        Rules out thin markets. Compensates for Roll
        failure in one-sided markets.

    [4] Outside exclusion windows
        Not in final 10 minutes — MOC regime.
        Not within 30 minutes of FOMC, CPI, or NFP —
        public information events.
        Not on or within 3 trading days before contract
        roll dates — mechanical volume events.
```

---

## 4. Connecting the Regime to TFI and Returns

In the informed trading regime defined above, the composition
of executed order flow shifts. Uninformed participants face
higher adverse selection costs and reduce activity. Informed
participants continue trading because their information
advantage justifies the higher cost. TFI measured in this
regime therefore reflects a higher proportion of directional
information about future price movement.

The testable prediction: TFI's regression coefficient on
forward returns should be larger in magnitude, more
statistically significant, and more economically meaningful
in the informed regime than outside it.

A secondary prediction concerns signal decay: if TFI in the
informed regime reflects genuine private information, its
predictive power should persist across multiple horizons as
the information is gradually incorporated, decaying more
slowly than in non-informed regimes where any predictive
power reflects noise that reverts quickly.

---

## 5. Research Questions

### Primary Question

Does trade flow imbalance (TFI) predict short-term returns in 
ES futures at the one-minute horizon — and more importantly, 
is this predictive relationship significantly stronger during
periods of elevated information asymmetry, characterized by
high price impact, normal market liquidity, and absence of
known uninformed-flow events?

### Secondary Question

How does the predictive power of TFI decay across return
horizons (1-minute, 5-minute, 15-minute) in informed versus
non-informed regimes, and what does the decay structure imply
about the speed of information incorporation in ES futures?

### Market Maker Implications

If TFI is more predictive in informed trading regimes, a
market maker observing high lambda, tight spreads, and high
trade arrival rate should widen quotes and increase the
weight placed on recent TFI when setting prices — adjusting
the adverse selection component of the spread in proportion
to the estimated regime probability. The magnitude of the
TFI coefficient in the informed regime provides a quantitative
input to this adjustment.

---

## 6. Methodology Preview

**Signal construction:**

TFI_t = (BuyVol_t − SellVol_t) / (BuyVol_t + SellVol_t)

Computed at 1-minute resolution. BuyVol and SellVol are total
contract size of buyer- and seller-initiated trades within
each bar.

**Regime score construction:**

RegimeScore_t is a continuous measure of informed trading
probability at bar t, constructed from three components:

1. Standardize each component using rolling z-scores:
   - Kyle's lambda: rolling OLS of price changes on signed
     order flow, 30-minute window updated each minute
   - Roll spread: serial covariance of consecutive trade
     price changes, 30-minute window
   - Trade arrival rate: trades per minute, 5-minute window
     (shorter window reflects faster response of activity
     to market conditions)

   z_lambda_t = (lambda_t − μ_lambda) / σ_lambda
   z_roll_t   = (Roll_t − μ_roll) / σ_roll
   z_arrival_t = (arrival_t − μ_arrival) / σ_arrival

2. Combine with theoretically motivated signs:
   RawScore_t = z_lambda_t − z_roll_t + z_arrival_t

   Lambda positive: higher impact signals informed flow.
   Roll negative: tighter spread confirms liquid conditions
   where high lambda reflects information, not illiquidity.
   Arrival rate positive: active market confirms depth is
   normal rather than structurally thin.

3. Map to [0, 1] via logistic transformation:
   RegimeScore_t = 1 / (1 + exp(−RawScore_t))

   RegimeScore_t → 1 indicates strongly informed conditions.
   RegimeScore_t → 0 indicates strongly uninformed conditions.
   RegimeScore_t = 0.5 when indicators are ambiguous.

4. Set RegimeScore_t = 0 for all bars in exclusion windows
   regardless of indicator values:
   - Final 10 minutes of session (MOC regime)
   - 30-minute windows around FOMC, CPI, NFP
   - Contract roll dates and 3 preceding trading days

Rolling standardization ensures the score adapts to
structural shifts across the sample — a bar is classified
as informed relative to recent conditions, not to the full
sample distribution. All rolling estimates use only past
data — no lookahead bias.

Robustness checks on parameter choices:
- Lambda and Roll window: tested at 15 and 60 minutes
- Arrival rate window: tested at 2 and 10 minutes
- Forward return: tested with and without skipping one bar
  to account for bid-ask bounce in return measurement
- Regime operationalization: binary dummy (1 if all three
  components exceed 75th/25th percentile thresholds) tested
  as an alternative to the continuous RegimeScore; also
  tested at 70th/30th and 80th/20th percentile thresholds

**Regime detector validation:**

Before testing TFI predictability, validate that the regime
detector separates informed from uninformed trading:

1. Confirm realized volatility is significantly higher in
   high-RegimeScore bars — informed trading generates
   volatility even though volatility is not a regime
   condition.
2. Confirm RegimeScore is elevated in the 30 minutes before
   scheduled macro announcements — the period when informed
   traders with early signal access are most active.
3. Confirm price impact is more persistent in high-
   RegimeScore bars — informed trading produces permanent
   price impact while uninformed trading produces temporary
   impact that reverts.

**Primary test:**

Regression of forward return on TFI using RegimeScore as
a continuous moderator:

Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t

Where:
- Return_{t+1}: log return of the next 1-minute bar
- α: intercept — expected return when all variables are zero
- β₁: TFI slope when RegimeScore = 0 (uninformed baseline)
- β₂: return level shift per unit increase in RegimeScore,
  independent of TFI
- β₃: additional TFI slope per unit increase in RegimeScore
  — the primary test statistic; a positive and significant
  β₃ indicates TFI predicts returns more strongly as
  informed trading probability increases
- β₄: lagged return — controls for return autocorrelation
  and mean reversion
- β₅: lagged TFI — controls for TFI autocorrelation,
  ensuring β₃ reflects genuine predictability rather than
  signal persistence
- ε_t: residual — portion of Return_{t+1} unexplained by
  the model

Newey-West standard errors, maxlags=5.

**Effect size decomposition:**

Report the distribution of RegimeScore across the full
sample and within each sub-period — specifically the
fraction of bars with RegimeScore > 0.5 (more informed
than not) and RegimeScore > 0.75 (strongly informed). This
contextualizes economic significance — a highly predictive
signal active in 3% of bars has different practical
implications than one active in 30% of bars.

**Horizon analysis:**

Repeat primary test at 1-minute, 5-minute, and 15-minute
forward horizons. Plot β₃ as a function of horizon. The
decay structure implies the speed of information
incorporation — faster decay suggests more efficient
markets with respect to this signal.

**Subsample stability:**

Repeat primary test on three samples independently:
- Full in-sample: 2025-05-01 to 2025-12-30
- Sub-sample 1: 2025-05-01 to 2025-09-30 (stable regime)
- Sub-sample 2: 2025-10-01 to 2025-12-30 (volatile regime)

Consistency across sub-samples indicates a structural
property of ES futures rather than a sample-specific
artifact.

**Transaction cost analysis:**

Given the estimated β₃ coefficient, compute the predicted
return per bar at high RegimeScore levels. Compare against
ES futures round-trip transaction cost of one tick (0.25
index points, ~4 basis points of notional). Report whether
the signal survives transaction costs and compute the
annualized Sharpe ratio of a strategy that trades in the
direction of TFI when RegimeScore exceeds 0.5, accounting
for transaction costs.

**Regime robustness check:**

Replace RegimeScore with daily VPIN (Easley, Lopez de
Prado, and O'Hara, 2012). Test whether results are
consistent across regime indicator choices. Consistency
across two theoretically distinct indicators with different
failure modes strengthens the credibility of the finding.

**Out-of-sample validation:**

Apply the exact in-sample estimated model (coefficients
fixed, no re-estimation) to the held-out period:
2026-01-01 to 2026-03-09. Report in-sample versus
out-of-sample β₃ comparison. Graceful degradation —
weaker but same sign and direction — is the expected
and acceptable outcome.

**All regressions:** Newey-West standard errors, maxlags=5.

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
