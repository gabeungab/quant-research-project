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
- Problem: Calendar spread instruments (ESM5-ESU5, ESH6-ESM6, etc.) 
  were present in the raw data with spread prices in the 40-50 range, 
  which are not real futures prices. 
- Fix: After calendar spread removal (removing any symbols with 
  hyphens), prices ranged from 5596.00 to 7041.25 (consistent with 
  ES futures price history).

TFI computation bug (uint32 overflow)
- Problem: Initial TFI output showed values in the millions instead of 
  [-1, 1] because buy_volume and sell_volume columns were dtype
  uint32 (unsigned 32-bit integer). When sell > buy, the subtraction
  wraps around a huge positive number instead of going negative.
- Fix: After casting both columns to int64 before computing TFI, TFI 
  range correctly now [-1, 1].

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

## 2026-03-25

**Session Summary:**
- Wrote plot_overview() function in src/data_loader.py and generated 
  results/overview.png.
- Wrote compute_daily_stats() function in src/data_loader.py.
  - Found low-trade-count days and filtered them in load_all_days().
  - Found duplicate trades but confirmed they are valid (see 'Findings').
- Wrote plot_phase1() function in src/data_loader.py.
  - Analyzed the five plots to both understand my data more in depth
    and possibly find any research-worthy paths (see 'Findings').
- Learned about market making mechanics, profits, and risks (see 
  NOTES.md) and wrote RESEARCH.md (section 3.1 to 3.4).

**Findings:**
results/overview.png analysis
- TFI vs time quickly scatters around 0. Makes sense.
- Log returns vs time also scatters around 0, with one large spike
  down near market close (just before 16:00 EST). Also makes sense.
- Frequency vs TFI (TFI Distribution) is centered at zero with skinny 
  tails. Makes sense and follows that TFI vs time scatters around 0.
- Frequency vs Log Returns (Log Returns Distribution) is centered
  sharply around 0 with only 2 real outliers (|x|<0.01). Makes sense.
No real findings here; expected with such simple conditions.

compute_daily_stats() output analysis
- Found four days with abnormally low trade counts in 2025 data (see
  data/README.md) and found them to be bank holidays / half trading
  days. Filtered them out of dataset in the load_all_days() function.

Duplicate trades analysis
- From simlpe print statements in test_load.py, 2,856,579 trades were
  found to share timestamps with at least one other trade (duplicates). 
  Investigated and confirmed as legitimate multi-level fills — large 
  orders sweeping multiple price levels simultaneously. All trades 
  retained in sample. 

Plot analysis (intraday close volume/trade count vs. close volatility):
- Trade arrival rate and volume both show a modified U-shape: high at
  open (~4,000 trades/min, ~12,000 contracts/min), declining through
  midday, then a massive spike at close (~7,500 trades/min, ~52,000
  contracts/min). The close spike dominates, making the shape more
  like an inverse-J.
- Intraday volatility shows a different pattern: sharp spike at open
  (~0.0053) then flat and consistent through the rest of the day
  (~0.0015-0.002) including at close — a small normal-J shape with
  no close spike.
- Key difference: high volume and trade count at close does NOT
  produce high volatility — explained by adverse selection dynamics
  around MOC order flow (see NOTES.md - Market Making).
- Research implication: the close is a special regime where the
  volume-volatility relationship breaks down. I will probbably exclude
  the final 1-2 minutes from formal analysis depending on research
  question, or condition on time-of-day explicitly.
  - These findings don't particularly generate any paths to possible
    research ideas, which is expected for simple conditions like these.
    Markets having higher volatility / more informed trading at open
    versus at close is just a known market charactersitic and isn't unique
    to any IV (ex. TFI) and its predictive power on returns.

**Open questions:**
None

**AI Usage:**
- Claude helped identify errors during debugging.
- Claude helped me understand why there was no volatility spike
  at market close while still having a volume / trade count spike.

**Next step:**
Start phase 2 - Research Question Selection and Literature Review.

---

## 2026-03-26

**Session Summary:**
- 

**Findings:**
- 

**Open questions:**


**AI Usage:**
- 

**Next step:**


---
