# Personal Notes

*Purpose: Tracking my notes on self-learned technical concepts*
*that I needed throughout this project.*

---

TSS, RSS, and ESS
- TSS (Total Sum of Squares): sum of squared distances from each
  observed y-value to the mean of all y-values. 
  Measures total variance in the dependent variable.
- RSS (Residual Sum of Squares): sum of squared distances from each
  observed y-value to the model's predicted y-value at that point.
  Measures variance the model failed to explain.
- ESS (Explained Sum of Squares): sum of squared distances from each
  model-predicted y-value to the mean of all y-values. Measures
  variance the model did explain, because ESS = TSS - RSS.

R-squared
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

F-statistic and Prob(F-statistic)
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

t-statistic and P>|t| (coefficient p-values)
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

Confidence intervals
- The range of coefficient values consistent with your data.
- CI = coefficient ± (1.96 × standard error). The 1.96 comes from
  the normal distribution — 95% (convention for CI) of a normal 
  distribution falls within 1.96 standard deviations of the mean.
  - On repeated studies with different samples, 95% of the confidence 
    intervals you computed would contain the true coefficient.
- Key rule: if the confidence interval contains zero, the coefficient
  is not statistically significant at the 5% level (p > 0.05).

Durbin-Watson statistic
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

Newey-West standard errors (HAC)
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

Bracket notation vs dot notation
- Bracket notation object['key']: selects from dictionaries and
  DataFrames. Use when accessing a column or key by name.
- Dot notation object.attribute: accesses attributes of class
  objects. Use when accessing built-in properties (methods or
  attributes) of an object.
- For example, tfi['tfi'] selects the tfi column from the pandas 
  DataFrame, while results.resid accesses residuals from a 
  statsmodels RegressionResults object.

---

Organize by concept categories later as this file grows
