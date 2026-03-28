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

Glosten and Milgrom (1985) [CITE] model the bid-ask spread as
compensation for adverse selection; market makers who trade with
informed counterparties lose money on average because the informed
trader knows something they do not. To break even, market makers
widen spreads in proportion to the probability that any given
trade is informed. A key implication is that spread width reflects
the market's expectation of informed trading activity — wider
spreads signal higher information asymmetry.

Kyle (1985) [CITE] models how informed traders behave given this
environment. Rather than trading aggressively and immediately
revealing their information, informed traders disguise their
positions by spreading orders over time. Price moves gradually
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
developed by Easley, Lopez de Prado, and O'Hara (2012) [CITE], 
directly estimates the proportion of informed trading from order 
flow. VPIN divides trading into fixed-volume buckets and measures 
the average absolute imbalance across buckets as a proxy for the 
probability that any given trade is informed.

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
primary regime indicator due to these limitations. Daily VPIN 
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
without observing quotes directly [CITE: Roll 1984].

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

Two sources of high lambda are not addressable from
trades-only data: market maker inventory pressure and
mechanical order clustering. Both introduce noise rather
than systematic bias — they increase misclassification
of uninformed periods as informed, diluting the regime
signal and biasing against finding a significant result.

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
