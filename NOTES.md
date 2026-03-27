# Personal Notes

*Purpose: Tracking my notes on self-learned technical concepts*
*that I needed throughout this project.*

---

**TSS, RSS, and ESS**
- TSS (Total Sum of Squares): sum of squared distances from each
  observed y-value to the mean of all y-values. 
  Measures total variance in the dependent variable.
- RSS (Residual Sum of Squares): sum of squared distances from each
  observed y-value to the model's predicted y-value at that point.
  Measures variance the model failed to explain.
- ESS (Explained Sum of Squares): sum of squared distances from each
  model-predicted y-value to the mean of all y-values. Measures
  variance the model did explain, because ESS = TSS - RSS.

**R-squared**
- Represents the proportion of total variance in the dependent variable 
  explained by the independent variable(s) (R-square = 1 - RSS/TSS).
  - RSS = 0 | 0 variance the model failed to explain | model predicts 
    every point perfectly | R-squared = 1.
  - RSS = TSS | dependent variable variance = variance model failed 
    to explain model | model explains nothing | R-squared = 0.
  - Adjusted R-squared penalizes added independent variables by
    scaling RSS and TSS by their degrees of freedom, preventing
    R-squared from artificially rising when useless independent 
    variables are added. 

---

**F-statistic and Prob(F-statistic)**
- F-statistic: Tests if the whole model has any statistically significant 
  explanatory power -- whether at least one coefficient is non-zero.
- F = (ESS/k) / (RSS/(n-k-1)), where k is the number of independent
  variables used and n is the number of observed data points.
  - Numerator: explained variance per predictor used.
  - Denominator: unexplained variance per remaining degree of freedom.
    - Degrees of freedom: the number of independent pieces of information 
      remaining after estimating model parameters with the OLS formula. 
      Each parameter estimated consumes one degree of freedom. With n 
      observations and k predictors plus the intercept, dof = n-(k+1).
  - A large F means your model explains a lot per predictor relative
    to how much it fails to explain per observation — evidence of
    genuine predictive power.
- Prob(F-statistic): the p-value for the F-test. If the true
  coefficients were all zero (null hypothesis), this represents the 
  probability of observing an F-statistic this large by chance. 
  Below 0.05 is the conventional threshold for claiming significance.
    - y = mx+b+r, where m = coefficient of the independent variable.
      We add r because the model almost never perfectly predicts the
      dependent variable, so r = residual accounts for this disparity.
      Anyway, if m = 0, this means that the independent variable has no
      predictive power on y, and the model is useless.

**t-statistic and P>|t| (coefficient p-values)**
- For each individual coefficient, tests whether that coefficient 
  is statistically distinguishable from zero.
- t = coefficient / standard error.
  - Standard error: measures how much the coefficient estimate would 
    vary if I calculated its value with the OLS formula on different 
    datasets of the same size.
      - OLS Formula: given independent variable(s) and a dependent 
        variable, OLS finds the slope m of the regression line that 
        minimizes the sum of squared residuals across all observations. 
  - If the coefficient is large relative to its uncertainty, the
    t-statistic is large — the signal is strong relative to noise.
    If the coefficient is small relative to its uncertainty, the
    t-statistic is small — the signal is weak relative to noise.
  - The p-value converts the t-statistic into a probability: if the
    true coefficient were zero, what is the probability of observing
    a t-statistic this large by chance?
- With one predictor, F-test = t-test and p-values are equal.

**Confidence intervals**
- The range of coefficient values consistent with your data.
- CI = coefficient ± (1.96 × standard error). The 1.96 comes from
  the normal distribution — 95% (convention for CI) of a normal 
  distribution falls within 1.96 standard deviations of the mean.
  - On repeated studies with different samples, 95% of the confidence 
    intervals you computed would contain the true coefficient.
- Key rule: if the confidence interval contains zero, the coefficient
  is not statistically significant at the 5% level (p > 0.05).

**Durbin-Watson statistic**
- Durbin-Watson statistic: Tests for autocorrelation in regression 
  residuals specifically at lag 1 — whether consecutive residuals are
  correlated with each other.
  - Lag x = shifting all x-values (time) in a dataset back by x periods.
- DW = sum of (e_t - e_(t-1))^2 / sum of e_t^2, where e_t is the 
  residual at time t (ranges from 0 to 4).
  - If consecutive residuals are independent, the numerator and
    denominator are approximately equal → DW ≈ 2.
  - If residuals are positively correlated (each residual tends to be 
    the same sign as the previous residual), differences between them 
    are small → numerator is small → 0 < DW < 2.
  - If negatively correlated (each residual tends to be the opposite sign 
    as the previous residual), differences are large → 2 < DW < 4.
- Key point: OLS standard errors assume residuals are independent. 
  Autocorrelated residuals violate this assumption,making standard 
  errors and p-values unreliable. DW diagnoses this problem, motivating 
  the use of Newey-West standard errors.

**Newey-West standard errors (HAC)**
- OLS standard errors assume residuals have constant variance 
  (homoskedasticity) and are uncorrelated across observations. 
  Both are violated in financial data due to non-constant
  variance and autocorrelation in residuals. NW corrects this.
- With NW, coefficients/the constant estimates are unchanged from 
  the OLS formula; NW only changes standard errors, which changes 
  t-statistics (t = coefficient / standard error) and p-values 
  (which are derived directly from the t-statistic).
- maxlags=5: accounts for residual autocorrelation up to 5 lags 
  (convention for 1min financial data).
- Always use Newey-West for any regression on financial time series.

---

## Python Syntax and Patterns

**Bracket notation vs dot notation**
- Bracket notation object['key']: selects from dictionaries and
  DataFrames. Use when accessing a column or key by name.
- Dot notation object.attribute: accesses attributes of class
  objects. Use when accessing built-in properties (methods or
  attributes) of an object.
- For example, tfi['tfi'] selects the tfi column from the pandas 
  DataFrame, while results.resid accesses residuals from a 
  statsmodels RegressionResults object.

---

## Market Making — Mechanics, Profit, and Risk

**Core role:**
Market makers continuously post bid and ask quotes, simultaneously
willing to buy at the bid and sell at the ask. The spread between
them is their gross compensation for providing liquidity. At any
moment, the best bid and ask in the order book are set by the most
competitive market maker quotes. Price discovery happens as market
makers update these quotes in response to order flow.

**How market makers profit:**
They collect the spread on every round trip — buy at bid, sell at
ask, pocket the difference. On ES futures, the minimum spread is
one tick (0.25 index points = $12.50 per contract). This profit
exists because the spread is the fundamental compensation for
liquidity provision on any asset.

**Two sources of risk:**
Inventory risk: random order flow imbalances push the market maker
to accumulate a net position. If they've sold 1,000 contracts net
and price rises, they lose on that inventory regardless of whether
any trader was informed.

Adverse selection risk: market makers don't know the true value of
the asset — they estimate it and post quotes around that estimate.
If their estimate is wrong, informed traders systematically hit
their stale quotes and extract the mispricing, and the market maker
accumulates size in the wrong direction relative to true value.
This is the fundamental source of market maker risk — uncertainty
about true asset value. To protect against this, market makers
widen spreads and update quotes defensively when they infer
incoming order flow may be informed.

**Why MOC orders are low-risk for market makers:**
MOC imbalances are publicly announced via exchange feeds in the
final minutes of trading. The market knows the order is purely
operational — not based on private information about future price
direction. With no adverse selection risk, market makers compete
aggressively to provide liquidity, tightening quotes to capture
the flow. Multiple liquidity providers stepping in simultaneously
absorbs large MOC volume without price movement — each collects
the spread with no expected loss to informed flow.

However, MOC liquidity provision is not risk-free. The inventory
accumulated by absorbing a large MOC imbalance must be unwound
in the subsequent session. If the market gaps against that
position overnight, the market maker loses. Robust overnight
risk management is required.

**Connection to price impact and volatility:**
Price moves when market makers defensively update their quotes
in response to order flow they believe is informed — not because
trades mechanically push price. This is the core mechanism of
the Kyle (1985) and Glosten-Milgrom (1985) models. Uninformed
flow (MOC, retail noise) generates high volume with minimal
price impact. Informed flow generates both high volume and high
volatility through adverse selection. This explains the
volume-volatility divergence at the market open versus close
observed in ES futures RTH data.

---

## Regression Diagnostics — Connections and Interactions

**OLS p-value vs. residual autocorrelation**
- OLS p-value reflects if my independent variable (IV) is significant 
  in predicting the dependent variable (DV) (higher = less evidence 
  that the IV has predictive power on the DV).
- Residual autocorrelation reflects if my model captures all the 
  systematic patterns in the DV (higher = model missing more systematic 
  patterns in the DV).
  - Residual autocorrelation = (DV autocorrelation on itself) - (what the 
  model explained). In tis case, since the model explained nothing 
  (model R-square=0), then residual autocorrelation = DV autocorrelation.
- The two are actually independent; meaning, if a model has a low OLS
  p-value, but high residual autocorrelation, you can account for this
  by adding lagged-dependent variable as a IV. However, this causes two 
  things; residuals become less correlated (good), but now the IV coefficient
  will change (and therefore its standard error, its t-statistic, and unique
  p-value based on the DV) because now the confounding influence of DV 
  autocorrelation is absorbed by the lagged-DV IV, isolating the IV 
  coefficient estimate, which may have been inflating/deflating the IV p-value.
- Newey-West (HAC) addresses this problem by simply returning p-values 
  that reflect the uncertainty from residual autocorrelation (from corrected 
  standard error), but doesn't actually change the model itself to remove 
  residual autocorrelation entirely.
  - Newey-West correction still must be used if residual autocorrelation 
    is dealth with because of second failed assumption (variance is constant; 
    basically never the case in financial markets).
