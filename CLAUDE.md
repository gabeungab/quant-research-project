# CLAUDE.md — Project Context

## What this project is
Studying the regime-conditioned price impact of Trade Flow
Imbalance (TFI) in ES futures. The regime detector is the primary
contribution — a two-component composite (Kyle's lambda + trade
arrival rate) that identifies periods of elevated information
asymmetry in real time from trades-only data. TFI serves two
explicitly separated roles: (1) a contemporaneous characterization
of adverse selection amplification, framed as a confounded market
maker calibration (not an empirical finding), and (2) a forward
return predictability test, which produced a null result
(β₃ = 0.0001, p = 0.570) — the primary empirical finding,
interpreted as an efficiency result about information incorporation
speed in ES futures.

Key design constraint: with trades-only data, a fully orthogonal
regime detector is impossible — any detector derived from aggressor-
side volume shares informational content with TFI. Lambda + TAR is
the least circular available detector given this constraint. We
deliberately sacrifice some detection accuracy (per Ahern, 2018,
the most accurate trades-only detector uses TFI variants directly)
for research design cleanliness. This tradeoff and its implications
are stated explicitly in the paper's limitations section.

Final deliverables:
- Clean GitHub repository with fully reproducible code
- 12-15 page research paper in LaTeX/PDF

## Research goals and standards
This project targets quant researcher and trader internship
applications at top firms. It must be defensible in a technical
interview — every line of code, every methodological choice,
every result.

The project has two layers:
- Layer 1: Regime detector construction and validation. Does the
  detector correctly identify periods of elevated information
  asymmetry? Validated via contemporaneous TFI-return amplification
  (confounded calibration, explicitly framed as such) and the T+1
  null efficiency finding.
- Layer 2: Market maker implications — quantified using the
  contemporaneous dynamic amplification formula and the p% intra-bar
  framework (empirically derived weight schedule for applying the
  amplification coefficient to evolving mid-bar TFI).

---

## Project phases
- Phase 0: Foundations — Python (Stream A), Statistics (Stream B),
  Microstructure (Stream C).
- Phase 1: Data familiarization — load full sample, clean,
  descriptive stats
- Phase 2: Research question selection and literature review
- Phase 3: Exploratory analysis of chosen phenomenon
- Phase 4: Formal statistical analysis, in/out-of-sample testing
- Phase 5: Market maker implications (Layer 2)
- Phase 6: Paper writing and code polish

## Current status
Phase 4 being rerun with updated regime detector and exclusion
windows. Phase 5 not started. Five research angles under evaluation.

Phase 0 Stream A completed:
- load_day(), load_all_days(), resample_to_bars(),
  remove_outliers(), compute_tfi(), compute_returns(),
  run_ols(), test_autocorrelation(), plot_overview(),
  plot_phase1() in src/data_loader.py
- EXCLUDED_DATES constant in load_all_days() for holiday exclusions
- Stream B and C: not yet started — begin in parallel with Phase 3

Phase 1 completed:
- Final clean dataset: ~58.8M RTH trades, 169 trading days
- Data quality checks complete: calendar spreads filtered,
  price outliers removed (114,413 trades, 0.19%),
  duplicate timestamps confirmed legitimate
- compute_daily_stats() complete, five exploratory plots saved
- PAPER.md Section 3 (Data) complete

Key findings from Phase 1:
- Buy/sell volume ratio: 1.003 — balanced across sample
- Trade sizes highly right-skewed: median 1, max 1,968 contracts
- Two activity regimes: stable ~1M contracts/day May-Sep,
  elevated and volatile Oct-Dec
- Intraday volume and trade arrival: modified inverse-J shape
  with massive MOC-driven close spike
- Intraday volatility: open spike only, flat through close —
  diverges from volume due to uninformed MOC order flow

Phase 2 completed:
- Research question finalized: does TFI predict returns more
  strongly in informed trading regimes?
- Primary signal: TFI at 1-minute resolution
- Regime detector: continuous RegimeScore ∈ [0,1] constructed
  from Kyle's lambda (30-min rolling), Roll spread (30-min
  rolling), trade arrival rate (5-min rolling), combined via
  rolling z-score standardization and logistic transformation
- Exclusions: final 10 min (MOC), 30 min around FOMC/CPI/NFP,
  contract roll dates + 3 preceding trading days
- Primary regression: interaction of TFI × RegimeScore with
  lagged return and lagged TFI as controls; Newey-West SE
- Additional tests: horizon analysis (1/5/15-min), effect size
  decomposition, subsample stability, transaction cost analysis,
  out-of-sample validation
- Robustness checks: binary regime dummy (75th/25th percentile),
  alternative thresholds (70th/30th, 80th/20th), alternative
  windows (15/60-min lambda/Roll, 2/10-min arrival rate),
  forward return skip, daily VPIN as alternative regime indicator
- paper/phase2_development.md complete
- PAPER.md Sections 3 and 4 complete

Phase 3 completed:
- src/signal_construction.py: compute_lambda, compute_roll_spread,
  compute_arrival_rate, compute_regime_score, compute_exclusion_mask
- src/plot_signals.py: 16 exploratory component plots + 3
  TFI-by-regime plots saved to results/phase3/
- src/test_signals.py: end-to-end sanity checks
- Key stats: exclusion mask 7,487 bars (2.1%); RegimeScore 55,171
  non-NaN RTH bars; lambda NaN rate 31.5% from zero-variance flow
- Exploratory finding: contemporaneous TFI slope 1.87x larger in
  high-regime — confirmed as confounded calibration, not independent
  contribution. Retired from paper.

Phase 4 initial run completed (numbers will update after rerun):
- src/formal_analysis.py: full regression pipeline
- N = 53,787 regression bars, 169 trading days
- Primary result: β₃ = 0.0001, p = 0.570 at T+1 — null, genuine
  efficiency finding, primary empirical result
- Contemporaneous: β₃ = 0.0015, z = 7.214, p < 0.001 —
  confounded calibration, almost certainly overestimates true
  causal amplification. Dynamic: dReturn/dTFI = β₁ + β₃ × RegimeScore
- Horizon: no regime interaction at T+5 or T+15
- Subsample: null consistent across May-Sep and Oct-Dec
- All outputs saved to results/phase4/

Phase 4 pending changes (rerun required):
- Drop Roll spread from regime detector. New detector: lambda + TAR
  only. Roll is non-orthogonal to lambda, fails in one-sided markets,
  and is redundant with TAR.
- Change announcement exclusion from ±30 min to +30 min post-event
  only. Pre-announcement window may contain genuine informed leakage
  and should remain in analysis.
- PAPER.md, phase2_development.md, CLAUDE.md to be updated after
  rerun with new β₃ values.

Five research angles under evaluation before Phase 5:
1. Lagged regime conditioning (RegimeScore_{t-1} on T+1 returns)
2. Time-of-day interaction (midday window 11:00-13:00)
3. Asymmetric TFI quintile interaction
4. Regime transition dynamics
5. Volume-conditioned TFI (absolute imbalance)

---

## Project structure
quant-research-project/
    /data        — data documentation only, no raw files
    /notebooks   — exploratory Jupyter notebooks (not started)
    /src         — clean reusable Python modules
        data_loader.py       — data loading, cleaning, stats, plotting
        formal_analysis.py   — Phase 4 formal regression analysis
        plot_signals.py      — Phase 3 component plots
        signal_construction.py — signal and regime score functions
        test_load.py         — Phase 1 data loading and stats checks
        test_signals.py      — sanity checks for signal outputs
    /results
        /phase1              — Phase 1 outputs
            daily_stats.csv
            daily_volume_over_time.png
            intraday_trade_arrival.png
            intraday_volume.png
            intraday_volatility.png
            trade_size_distribution.png
        /phase3              — Phase 3 exploratory plots
            lambda_timeseries.png
            lambda_intraday.png
            lambda_distribution.png
            lambda_individual_days.png
            roll_timeseries.png
            roll_intraday.png
            roll_distribution.png
            roll_individual_days.png
            arrival_timeseries.png
            arrival_intraday.png
            arrival_distribution.png
            arrival_individual_days.png
            regime_score_timeseries.png
            regime_score_intraday.png
            regime_score_distribution.png
            regime_score_individual_days.png
        /phase4              — Phase 4 formal analysis outputs
            primary_regression.txt
            contemporaneous_regression.txt
            horizon_t5_regression.txt
            horizon_t15_regression.txt
            subsample_full_regression.txt
            subsample_may_sep_regression.txt
            subsample_oct_dec_regression.txt
            key_coefficients.csv
            transaction_cost_analysis.txt
    /paper       — working paper and research documents
        PAPER.md              — formal working paper draft
        phase2_development.md — Phase 2 research development
    JOURNAL.md   — running research log (dated session entries)
    NOTES.md     — general technical concept reference
    CLAUDE.md    — this file

## Markdown file purposes and language standards

JOURNAL.md — chronological session log. Contains: session
summary, findings specific to this project and dataset,
open questions, AI usage, next steps. Language is informal
and personal. Findings section captures project-specific
empirical observations and debugging discoveries — not
general concepts.

NOTES.md — general technical concept reference. Contains
concepts learned during the project that apply universally
— statistics, Python syntax, market microstructure mechanics.
Language explains concepts from first principles. This is
where general knowledge lives, not project-specific results.

PAPER.md — formal working paper draft. Contains only content
that belongs in the final research paper. Language is formal
and calibrated for graduate-level quants and quant recruiters.
Connects findings to known concepts without explaining them.
Every claim is supported by a number from the analysis.
Sections added incrementally as phases complete.

The distinction: if a concept applies to any project, it goes
in NOTES. If it is specific to this dataset and analysis, it
goes in JOURNAL (findings) or PAPER.md (if paper-ready).
PAPER.md never contains explanations of standard concepts —
only empirical observations connected to those concepts.

## Research design summary

**Signal:** TFI_t = (BuyVol_t − SellVol_t) / (BuyVol_t + SellVol_t)
Computed at 1-minute resolution from aggressor side field.

**Regime score:**
RegimeScore_t = 1 / (1 + exp(−(z_lambda + z_arrival)))
Two components only: Kyle's lambda (30-min rolling OLS) and trade
arrival rate (5-min rolling). Roll spread removed — non-orthogonal
to lambda, fails in one-sided markets, redundant with TAR.
All z-scores rolling, past data only. Set to 0 in exclusion windows.

**Exclusion windows:**
- Final 10 min of session (MOC uninformed flow)
- +30 min POST-announcement only (FOMC, CPI, NFP) — pre-
  announcement window retained as potentially informed
- Contract roll dates + 3 preceding trading days

**Contemporaneous characterization:**
Return_t = α + β₁·TFI_t + β₂·RegimeScore_{t-1} +
           β₃·(TFI_t × RegimeScore_{t-1}) +
           β₅·TFI_{t-1} + ε_t
Uses lagged RegimeScore_{t-1} — regime fully predetermined before
bar t's trades begin. TFI-Return confounding within the bar remains
(both constructed from same bar's trades); used for market maker 
calibration only, NOT a primary empirical finding. β₃ almost 
certainly overestimates true causal amplification. Dynamic 
amplification: dReturn/dTFI = β₁ + β₃ × RegimeScore_{t-1}.

**Primary regression:**
Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t
β₃ is the primary test statistic.
Formal result: β₃ = 0.0001, p = 0.570 — null result.

**Contemporaneous characterization:**
Return_t = α + β₁·TFI_t + β₂·RegimeScore_t +
           β₃·(TFI_t × RegimeScore_t) +
           β₅·TFI_{t-1} + ε_t
Validates regime detector — not a predictive test.
Formal result: β₃ = 0.0015, z = 7.214, p < 0.001.

**Key papers:**
- Kyle (1985) — Econometrica — lambda and informed trading
- Glosten and Milgrom (1985) — JFE — adverse selection framework
- Cont, Kukanov, Stoikov (2014) — JFEC — OFI predicting returns
- Roll (1984) — JF — implicit spread estimator
- Easley, Lopez de Prado, O'Hara (2012) — RFS — VPIN
- Ahern (2018) — NBER — informed trading detection; absolute order
  imbalance and negative TFI autocorrelation are most accurate

## Data
- Source: Databento, GLBX.MDP3, Trades schema
- In-sample: 2025-05-01 to 2025-12-30 (169 trading days)
  Location: ~/Desktop/Quant Research Project/raw-data/
            GLBX-20250501-20251231/
- Out-of-sample: 2026-01-01 to 2026-03-09
  Location: ~/Desktop/Quant Research Project/raw-data/
            GLBX-20260101-20260309/
- Fields used: ts_event_et (Eastern time), price, size,
  side (B/A/N)
- Fields ignored: rtype, publisher_id, instrument_id, action,
  depth, flags, ts_in_delta, sequence (all constant or
  irrelevant)
- Symbol rolls: ESM5 (May-Jun) → ESU5 (Jul-Sep) →
  ESZ5 (Oct-Dec) → ESH6 (Jan-Mar 2026)
- Excluded dates: 2025-05-26, 2025-07-04, 2025-09-01,
  2025-11-27 (holidays/half-sessions)

## Tech stack
Python 3.13, pandas, NumPy, scipy, statsmodels, matplotlib,
databento library

---

## Standards for Claude Code to enforce
- Train/test split is time-based: in-sample 2025, out-of-sample
  2026. Never suggest touching out-of-sample data before Phase 4.
- Methodology must be pre-registered before formal tests. Flag
  if tests run before plan is documented in JOURNAL.md.
- All regressions require Newey-West standard errors (maxlags=5).
  Flag if default OLS standard errors are used.
- Flag if multiple hypothesis tests run without Bonferroni
  correction.
- Transaction cost analysis required before any result claim.
  ES futures tick size = 0.25 index points (~4 basis points).
- RegimeScore must be set to 0 in all exclusion windows before
  any regression — flag if exclusions are not applied.
- All rolling estimates must use only past data. Flag any
  lookahead bias in rolling window construction.
- All results must be reproducible from /src code on raw data.

## Rules for Claude Code in this project
- Help debug code I wrote — do not write code for me
- Explain concepts I am trying to understand
- Point out methodological errors or oversights
- Do not generate analysis, write paper sections, or interpret
  results
- When I show you an error, explain what caused it before giving
  the fix
  