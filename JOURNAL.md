# Personal Research Journal

*Purpose: Running log of all work sessions (session summary, findings,*
*open questions, AI usage, and next steps for this project).*

---

## 2026-03-24

**Session Summary:**
- Learned more about quant landscape (HFT/MM firms, systematic funds).
- Formalized project direction and blueprint document: microstructure/
  factor research on ES futures trades data with statistical research
  + market participant implications analysis.
- Set up GitHub repo (quant-research-project), cloned locally to
  Desktop, opened in Cursor.
- Purchased ~9 months of ES tick/trade data through Databento
  (using free credit).
- See commits for repo work specifics (repo + markdown files setup).

**Findings:**
None

**Open questions:**
None

**AI Usage:**
- Used Claude for project brainstorming, workflow guidance, and
  generating blueprint document.

**Next step:**
Start Phase 0, Stream A.

---

## 2026-03-25

**Session Summary:**
- Successfully loaded one day of ES futures trades data into a pandas
  DataFrame using the Databento library.
- Wrote load_day(), load_all_days(), resample_to_bars(),
  remove_outliers(), compute_tfi(), compute_returns(), run_ols(),
  and test_autocorrelation() functions in src/data_loader.py.
- Wrote CLAUDE.md to provide stable project context to Claude Code.
- Wrote NOTES.md to store all my notes on learned technical concepts.
  Added sections "TSS, RSS, and ESS", "R-squared", "F-statistic and 
  Prob(F-statistic)", "t-statistic and P>|t|", "Confidence intervals", 
  "Durbin-Watson statistic", "Newey-West standard errors", and
  "Bracket notation vs dot notation".
- Analyzed run_ols() vs. test_autocorrelation() results and made
  logical connections between the two.

**Findings:**
Data cleaning bug (calendar spreads)
- Calendar spread instruments (ESM5-ESU5, ESH6-ESM6, etc.) were 
  present in the raw data with spread prices .
  in the 40-50 range, whcih are not real futures prices. Filtered 
  by removing any symbol containing a hyphen.
- After calendar spread removal, prices ranged from 5596.00 to 
  7041.25 (consistent with ES futures price history).

TFI computation bug (uint32 overflow)
- Initial TFI output showed values in the millions instead of [-1, 1]
  because buy_volume and sell_volume columns were dtype .
  uint32 (unsigned 32-bit integer). When sell > buy, the subtraction
  wraps around a huge positive number instead of going negative.
- After casting both columns to int64 before computing TFI, TFI range
  correctly now [-1, 1].

OLS + Ljung-Box results + connection:
- OLS showed TFI has no significant predictive power on forward
  returns (p=0.537, R-squared≈0).
- Ljung-Box revealed TFI is strongly autocorrelated at all lags
  (p≈0), meaning consecutive bars are not independent observations.
- Regression residuals are even more strongly autocorrelated
  (lb_stat≈14,500 at all lags), confirming the model left
  enormous systematic pattern unexplained (R-squared=0).
  - If the model had captured all systematic patterns in
  returns, residuals would be pure noise with no autocorrelation. 
  Since residuals are highly autocorrelated, the "unexplained part 
  of returns differing from the model" (return residuals) actually 
  have a pattern to them, meaning our model isn't picking up on 
  that said pattern.
  - Residuals of this model being autocorrelated doesn't mean we 
  actually found correlation between returns and TFI; this just
  confirms there is autocorrelation between residuals themselves.
  This is consistent with OLS p-value = 0.537 (TFI in not a 
  significant predictor of forward returns in this specification).

OLS p-value vs. residual autocorrelation
- Generalized to IV and DV, but here IV = TFI and DV = forward returns.
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

**Open questions:**
Note to self: get better at using Python imported ibraries and tools.

**AI Usage:**
- Claude helped identify errors during debugging (KeyError:
  'price', calendar spreads causing bad prices, uint32 overflow 
  in TFI, etc).

**Next step:**
Complete final Stream A skill: write plot_overview() function and
produce a clean 2x2 multi-panel matplotlib figure saved to 
/results/overview.png. Then move onto Stream B, C, and phase 1.

---
