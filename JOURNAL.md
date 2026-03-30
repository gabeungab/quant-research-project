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

## 2026-03-26

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
Organize NOTES.md with logical ordering and clear heading.

---

## 2026-03-27

**Session Summary:**
- Wrote first three main sections of paper/phase2_develpoment.md by
  researching with Google Scholar / SSRN.com (see document for more info).

**Findings:**
- TFI in ES futures is theoretically motivated as an informed
  trading signal but is diluted by uninformed flow unconditionally.
  The research question requires conditioning TFI on an informed
  trading regime to isolate periods where TFI is most predictive.

- VPIN considered and rejected as primary regime indicator due to
  four violated assumptions: informed traders trade uni-directionally,
  uninformed traders arrive symmetrically, trade arrival follows
  stationary independent Poisson processes, and information events
  are one-sided. Daily VPIN retained as robustness check only.

- Kyle's lambda selected as primary regime indicator — measures
  actual price response to order flow rather than inferring informed
  trading from imbalance patterns. Theoretically grounded in Kyle
  (1985) and Glosten-Milgrom (1985).

- Lambda disambiguation problem identified: five alternative
  explanations for high lambda beyond informed trading — thin
  markets, market stress, inventory pressure, mechanical clustering,
  contract roll proximity.

- Three conditions selected to address the most significant
  alternatives: Low Roll spread (tightness), High trade arrival
  rate (depth), Exclusion windows (MOC, announcements, roll dates
  extended to 3 days before roll). Two alternatives remain
  unaddressable from trades-only data (inventory pressure,
  mechanical clustering) — acknowledged as limitations that
  bias against finding significant results. Still need to double 
  check this combination for improvement.

- Roll spread estimator has a known failure mode in strongly
  one-sided markets (bid-ask bounce disappears). Trade arrival
  rate compensates as it remains reliable regardless of flow
  directionality — the two conditions are complementary, not redundant.

- Other metrics, estimators, proxies, etc. were found while researching,
  but were either not possible to research with my data or I thought was
  too involved for this project (leading to a lower-quality final product).

**Open questions:**
Review sections 3.4 through 3.6 and continue research about a better 
combination of conditions (both more encompassing/efficient while not 
introducing unneccessary complexity with diminishing returns) that
deals with the ambiguity of high lambda being and informed trading.

**AI Usage:**
- Claude helped me connect conceptual ideas togther between research papers.

**Next step:**
Review and edit/polish sections 3.4 through 3.6.
- Add to sections 3.2 and 3.3 explicitly why VPIN assumptions could not 
  be handled the same way that Kyle's Lambda ambiguity is being handled.
- Fill out all citations with the correct format.
Then move onto completing the rest of phase2_development.md.

---

## 2026-03-28

**Session Summary:**
- Completed paper/phase2_development.md — all sections finalized
  including research question, methodology preview, and references.
- Finalized continuous RegimeScore construction replacing binary
  dummy as primary regime operationalization.
- Updated PAPER.md to include Section 4 (Signal Construction and
  Empirical Design) and Section 5 placeholder (Market Maker
  Implications).

**Findings:**
Research question finalized:
- Primary: Does TFI predict short-term returns in ES futures,
  and is this relationship stronger when RegimeScore is high —
  consistent with informed trading dominating order flow?
- Secondary: How does TFI predictive power decay across horizons
  (1/5/15-min) in high vs low RegimeScore periods, and what does
  this imply about information incorporation speed?

Regime detector design finalized:
- Continuous RegimeScore ∈ [0,1] constructed from rolling
  z-scores of Kyle's lambda, Roll spread (inverted), and trade
  arrival rate, combined via logistic transformation. Adapts
  to structural changes across sample period.
- Binary regime dummy (was the first planned regime dummy) 
  retained as robustness check only (75th/25th percentile 
  thresholds, also tested at 70/30 and 80/20).
- Daily VPIN retained as alternative regime indicator robustness
  check — different theoretical framework, different failure modes.

Primary regression specification:
- Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
                 β₃·(TFI_t × RegimeScore_t) +
                 β₄·Return_t + β₅·TFI_{t-1} + ε_t
- β₃ is the primary test statistic.
- Lagged return (β₄) and lagged TFI (β₅) added as controls
  for autocorrelation structure — ensures β₃ reflects genuine
  regime-conditioned predictability, not persistence.

Additional tests planned:
- Regime detector validation (volatility, announcement,
  price impact persistence) before primary test
- Horizon analysis at 1/5/15-minute forward returns
- Effect size decomposition (fraction of bars at high
  RegimeScore levels)
- Subsample stability across full sample and two activity
  sub-periods (May-Sep, Oct-Dec)
- Transaction cost analysis + annualized Sharpe ratio
- Out-of-sample validation on 2026 held-out period

Robustness checks pre-specified:
- Lambda/Roll window: 15 and 60 minutes
- Arrival rate window: 2 and 10 minutes
- Percentile thresholds for binary dummy: 70/30, 80/20
- Forward return: with and without one-bar skip (bid-ask
  bounce correction)

**Open questions:**
None

**AI Usage:**
- Claude helped me connect literature to research design
  decisions made throughout Phase 2.
- Claude helped me develop continuous RegimeScore construction
  logic and all the robustness checks and their structure.

**Next step:**
Deeply review entire project to make broad connections between 
everything I have done so far (understanding status more clearly).
Then start Phase 3 — Exploratory analysis of TFI and RegimeScore on 
the full in-sample dataset.

---

## 2026-03-29

**Session Summary:**
- Built src/signal_construction.py with five functions: compute_lambda,
  compute_roll_spread, compute_arrival_rate, compute_regime_score,
  compute_exclusion_mask.
- Built src/test_signals.py to sanity check all outputs end-to-end.
- Diagnosed and fixed three bugs in signal_construction.py:
  exclusion mask was incorrectly flagging non-RTH bars (119k instead
  of ~1.7k close bars), Roll spread was contaminated by overnight
  gaps at day boundaries, and compute_regime_score was not aligning
  the exclusion mask index before applying it.
- Investigated lambda NaN rate within RTH hours.

**Findings:**
Signal construction confirmed working — key output stats:
- Kyle's lambda: mean 0.0042, std 0.0088, range [-0.19, 0.14]
- Roll spread: mean 5.59 index points, std 14.05 — values are
  inflated at 1-minute resolution but used only as relative
  ranking via z-score, not absolute spread estimate
- Trade arrival rate: mean 168 trades/min, max 8,487 — consistent
  with Phase 1 intraday patterns
- Exclusion mask: 7,487 bars excluded (2.1% of total) — within
  expected range (~1,690 close + ~1,140 announcement + ~6,240 roll)
- RegimeScore: 55,171 non-NaN bars; 42.8% above 0.50,
  25.9% above 0.75; 13.6% set to zero by exclusion mask

Lambda NaN rate investigation:
- 31.5% of core RTH bars (10:00-15:50) have NaN lambda
- Confirmed entirely from zero-variance signed flow, NOT from
  window warmup — window=15 and window=30 produce identical NaN
  counts, ruling out warmup as the cause
- Zero-variance bars are self-selecting as uninformative: perfect
  balance between buyer and seller flow is itself evidence against
  an informed trading regime
- 55,171 valid RegimeScore bars across 169 days (~326 bars/day,
  ~5.4 hours of coverage) — sufficient for rigorous analysis

Roll spread limitations noted:
- Values inflated (~22 ticks mean vs ~1 tick true spread) due to
  1-minute resolution and large intraday price moves
- Day boundary fix applied — overnight gaps no longer contaminate
  serial covariance estimate
- Used only as relative indicator via z-score; absolute level
  does not affect regime score construction

Regime detector theoretical scope clarified:
- Operates most reliably during stable midday conditions where
  lambda is estimable and Roll is not in one-sided failure
- First 30 minutes of each session excluded by warmup (subsumed
  by zero-variance exclusion as confirmed empirically)
- Inventory pressure and mechanical clustering remain as
  unaddressable limitations biasing against finding results

**Open questions:**
None

**AI Usage:**
- Claude helped diagnose exclusion mask over-exclusion bug
  (RTH filter missing from all three exclusion categories).
- Claude helped diagnose lambda NaN source (zero-variance
  vs warmup) via window=15 vs window=30 comparison.
- Claude helped interpret Roll spread inflated values and
  confirm z-scoring makes absolute level acceptable.

**Next step:**
1. Review Task 1 findings before proceeding — rerun
   test_signals.py and verify all key stats match findings
   above + limitations. Specifically confirm:
   - Exclusion mask total: ~7,487 bars
   - RegimeScore non-NaN bars: ~55,171
   - Lambda NaN rate core RTH: ~31.5%
   - window=15 and window=30 lambda NaN counts are identical
2. Task 2 (Phase 3): Plot each component individually —
   lambda, Roll spread, arrival rate, RegimeScore. For each:
   time series across full sample, intraday average by time
   of day, distribution histogram, behavior on individual
   days (high-vol, low-vol, announcement, normal).

---

## 2026-03-30 (Phase 3 - C)

**Session Summary:**
- Finalized Task 1 of Phase 3 (Roll failure analysis + limitations).
- Completed Task 2: generated 16 exploratory plots (lambda, Roll,
  arrival rate, RegimeScore) saved to results/phase3/.
- Completed Tasks 3 and 5: TFI-by-regime plots and regime detector
  validation diagnostics.
- Reframed primary research question (see findings).
- Updated PAPER.md Sections 4.1, 4.4, 4.5 and phase2_development.md.

**Findings:**

Roll failure analysis (Task 1):
- Roll fails in one-sided flow (informed conditions) but does not
  reverse regime signal — lambda and arrival rate still push
  RegimeScore correctly. Effect is quantitative (lower magnitude),
  not qualitative (wrong direction).
- Contrast: lambda zero-variance NaN is genuinely uninformative
  (no directed flow), so NaN exclusion is justified. Roll failure
  in one-sided markets is more significant because it occurs during
  genuinely informed conditions.

16-plot exploratory analysis (Task 2):

Filtering decisions applied to all plots: distributions filter to
RTH bars only and exclude zeros (warmup/Roll-failure/exclusion-mask
artifacts). Lambda distribution keeps negatives (real signal).
Timeseries filter to trading days only. Individual days constrained
to 09:30-16:00 Eastern.

Lambda:
- Distribution: sharply peaked near zero, slight positive skew,
  tails to ±0.20. Three timeseries spikes at late June (~0.095),
  early September (~0.085), late December (~0.140) — all macro
  events. Baseline ~0.005-0.015.
- Intraday: flat after 30-bar warmup (~0.0042-0.0048), midday dip
  (~0.0025 at 12:00-12:30), afternoon recovery, sharp close drop
  consistent with MOC uninformed flow.
- Individual days: high-vol (±0.06) vs low-vol (0.001-0.005) is
  10-20x difference. FOMC day shows large negative lambda pre-
  announcement (13:00-14:00) — participants reducing directional
  exposure before statement.

Roll Spread:
- Distribution: heavily right-skewed, spike near zero from Roll
  failure in one-sided markets (genuine zero estimates, not NaN).
- Intraday: counterintuitive wave pattern (peaks ~11:30 and
  14:30-15:30) is artifact of directional price moves inflating
  serial covariance — not a genuine liquidity signal. Rolling
  z-score partially corrects.
- Timeseries spikes match lambda exactly (late June ~75, Sep ~85,
  Dec ~90) — correlated, reducing independence as regime indicators.
- Individual days: high-vol Roll 20-63 pts vs 0-3.5 on all other
  days. Low-vol values (0-1.4) plausible for ES true spread.

Trade Arrival Rate:
- Distribution (RTH, >0): right-skewed, peak 300-500 trades/min,
  tail to ~4,000+.
- Intraday: modified inverse-J — open ~1,700, midday ~400-500,
  close spike ~2,000. Open lower than Phase 1 (~4,000) due to
  5-bar rolling mean smoothing.
- Individual days: FOMC step change at exactly 14:00 reaching
  ~4,300 trades/min validates announcement date/time.

RegimeScore:
- Distribution (RTH, >0): clean U-shape with trough 0.4-0.6 —
  logistic transformation pushing toward extremes as intended.
- Intraday: zero 9:30-10:30 (warmup), jumps to ~0.53 at 10:30,
  flat ~0.40-0.60 through core hours, drops to zero at 15:50
  (close exclusion). FOMC exclusion visible as flat zero
  ~13:30-14:30 on 2025-07-30.
- Timeseries: daily mean 0.37-0.58, no structural trend — rolling
  z-score adapting correctly across both activity regimes.
- Individual days: rapid bar-by-bar oscillation between 0 and 1 on
  all days — correct behavior. Detector captures episodic informed
  trading at 1-min level, not sustained day-level regimes.

Cross-component: Roll and lambda spike together at all three macro
events — driven by the same price moves, reducing their independence.
Acknowledged limitation of the composite score.

TFI-by-regime plots (Task 3) — 53,967 aligned bars:
- High-regime: 23,602 (43.7%), Low-regime: 30,365 (56.3%).
- T+1 scatter: high-regime slope = -1.52e-04, low-regime = +1.94e-04.
  Sign reversal — high-regime mean reverts, low-regime momentum.
- TFI distributions nearly identical across regimes — detector
  selects on market state, not TFI magnitude.
- ACF: high-regime decays fast (below CI by lag 7-8), low-regime
  slow (elevated through lag 12) — consistent with faster vs slower
  information incorporation.

Regime detector validation (Task 5):
- Contemporaneous slope: high = 1.80e-03, low = 0.97e-03. 1.87x
  amplification confirms higher order flow informativeness in
  high-regime. Partially tautological — lambda in RegimeScore
  directly measures price impact. Not the primary contribution.
- Realized volatility: high std = 0.000998, low std = 0.002229.
  Paradox explained by exclusion mask — announcement/roll windows
  (highest volatility) zeroed into low-regime by construction.
  Decile analysis confirms detector directionally correct: decile 8
  std = 0.001172 elevated above middle deciles (~0.000900). Decile 0
  std = 0.003508 = exclusion mask zeros, not genuine low-regime.
- Multi-horizon slopes: mean reversion concentrated at lag 1. Lags
  2+ tiny and inconsistent. Information incorporated within 1-2 min.

Research question reframed: the primary finding is the sign reversal
at T+1, not the contemporaneous amplification. Reframe: "does the
TFI-return relationship reverse sign across regimes — momentum in
low-regime, mean reversion in high-regime — consistent with fast
information incorporation creating overshoot at high price-impact
moments?"

**Bugs fixed (plot_signals.py):**
- Non-trading day zeros in timeseries → ts_filter parameter.
- Non-RTH zeros in distributions → dist_filter parameter (lambda:
  none; Roll/arrival/RegimeScore: >0).
- Individual days UTC x-axis → tz_convert + tz_localize(None) +
  set_xlim(09:30, 16:00).
- Intraday tick overlap → min(350, n-41) / min(390, n-1).
- 2025-09-15 and 2025-09-17 flat zero RegimeScore → both in
  September roll exclusion window (ESU5→ESZ5 roll 2025-09-18).
  Replaced with 2025-06-13 (high-vol) and 2025-07-30 (FOMC).

**Open questions:**
- Does lag-1 sign reversal survive formal testing with Newey-West
  SE and full controls in Phase 4?
- Is mean reversion large enough to exceed transaction costs?

---

## 2026-03-30 (Phase 4 - IP)

**Session Summary:**
- Completed Phase 4 formal statistical analysis.
- Wrote src/formal_analysis.py — data preparation, primary
  regression, contemporaneous regression, horizon analysis,
  subsample stability, transaction cost analysis.
- Saved all outputs to results/phase4/.
- Reframed research contribution based on formal results.
- Updated PAPER.md Sections 4.1, 4.5, 4.6, 5 and
  phase2_development.md to reflect final findings.

**Findings:**

Regression sample: N = 53,787 bars after NaN/warmup/boundary
removal. High-regime: 23,601 (43.9%), Low-regime: 30,186 (56.1%).
Date range: 2025-05-01 10:30 to 2025-12-30 15:58. 169 trading days.

Primary regression (T+1):
- β₃ (tfi_x_regime) = 0.0001, z = 0.568, p = 0.570. Not
  significant. Regime does not amplify TFI's predictive power
  for next-bar returns.
- β₁ (tfi) = 0.0007, z = 5.121, p < 0.001. Unconditional TFI
  effect significant — consistent with Cont et al. (2014) — but
  does not strengthen in high-regime conditions.
- lag_return = -0.489, p < 0.001. Dominant mean reversion
  driving R² = 0.236 — microstructure bid-ask bounce, not alpha.

Contemporaneous regression (T+0):
- β₃ (tfi_x_regime) = 0.0015, z = 7.214, p < 0.001. Highly
  significant. At mean high-regime score (0.788), TFI slope =
  0.0007 + 0.0015 × 0.788 = 0.00188 — 2.7x amplification.
- This is a validation finding, not a predictive finding.
  Kyle's lambda is built into RegimeScore and is itself a
  contemporaneous price impact measure — partial circularity
  acknowledged. Serves as confirmation the regime detector
  measures what it claims to measure.

Horizon analysis:
- T+5: β₃ = -0.000027, p = 0.902. Not significant.
- T+15: β₃ = -0.000108, p = 0.659. Not significant.
- Unconditional β₁ remains significant at all horizons
  (~0.0007-0.0008, p < 0.001) but does not vary with regime.
- Conclusion: information incorporation in ES futures is complete
  within one 1-minute bar in high-regime conditions.

Subsample stability:
- May-Sep: β₃ = 0.0001, p = 0.704. Oct-Dec: β₃ = 0.0001,
  p = 0.639. Null result consistent across both activity regimes.
  Unconditional β₁ stable at 0.00064-0.00073 across subsamples.

Transaction cost analysis (contemporaneous spec):
- Mean ES price: 6,460.55. One-way cost: 0.387 bps.
  Round-trip: 0.774 bps.
- At p75 high-regime TFI (0.073): gross = 1.476 bps,
  net round-trip = 0.702 bps. Positive after costs.
- Break-even TFI (round-trip): 0.031 at mean high-regime
  RegimeScore of 0.788. ~75% of high-regime bars clear this.
- T+1 spec does not survive round-trip costs even if significant.

Final research framing:
- Primary hypothesis (T+1 predictability): null result.
  β₃ not significant. ES futures incorporate regime-conditioned
  order flow within one 1-minute bar.
- Secondary characterization (contemporaneous price impact):
  significant but partially circular. Primary value is as
  regime detector validation and market maker input.
- Key contribution: validated real-time regime detector for ES
  futures, quantified adverse selection amplification (2.7x at
  mean high-regime), confirmed information incorporation speed.
- Open questions answered from 3/30: sign reversal at T+1 did
  not survive formal testing with controls. Mean reversion was
  an artifact of unconditional exploratory slopes.

**Open questions:**
- Do robustness checks (binary regime dummy, VPIN, window
  lengths, skip-bar) change any conclusions?
- Out-of-sample validation on 2026 held-out data.

**Next step:**
Next couple days are busy (school wise), but the next couple
full work sessions should be analysis, not new work.
- Review all of Phase 3 and 4 findings and decisions made and
  try to find a new angle of research; null results are fine,
  but push harder to see if you can make any more real findings.
- Only until fully satisfied / path has been relatively exhausted,
  then move onto Phase 4 out-of-sample testing + robustness checks.
    - Very important to spend time here, because once out-of-sample 
      is used, theres no turning back.

---

## 2026-03-31

**Session Summary:**
- 

**Findings:**


**Open questions:**


**Next step:**


---
