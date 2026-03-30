# CLAUDE.md — Project Context

## What this project is
Original empirical research on ES futures tick data from CME Globex.
Studying whether Trade Flow Imbalance (TFI) predicts short-term
returns in ES futures, and whether this predictive relationship is
stronger during periods of elevated information asymmetry —
characterized by high price impact, normal market liquidity, and
absence of known uninformed-flow events.

Final deliverables:
- Clean GitHub repository with fully reproducible code
- 12-15 page research paper in LaTeX/PDF

## Research goals and standards
This project targets quant researcher and trader internship
applications at top firms. It must be defensible in a technical
interview — every line of code, every methodological choice,
every result.

The project has two layers:
- Layer 1: Does TFI predict returns more strongly in high-
  RegimeScore periods? Narrow, rigorous, and empirically tested.
- Layer 2: What the findings imply for market maker quote
  adjustment — quantitatively specific, references actual results.

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
Phase 3 in progress — Task 1 complete.

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

Phase 3 Task 1 completed:
- src/signal_construction.py complete — compute_lambda,
  compute_roll_spread, compute_arrival_rate,
  compute_regime_score, compute_exclusion_mask
- src/test_signals.py complete — end-to-end sanity checks
- Key confirmed stats: exclusion mask 7,487 bars (2.1%);
  RegimeScore 55,171 non-NaN bars; lambda NaN rate 31.5%
  in core RTH from zero-variance signed flow (not warmup)
- Roll spread day-boundary fix applied
- PAPER.md Section 4.2 limitations updated

---

## Project structure
quant-research-project/
    /data        — data documentation only, no raw files
    /notebooks   — exploratory Jupyter notebooks (not started)
    /src         — clean reusable Python modules
        data_loader.py  — all data loading, cleaning, signal,
                          stats, and plotting functions
    /results     — saved figures and daily_stats.csv
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
RegimeScore_t = 1 / (1 + exp(−(z_lambda − z_roll + z_arrival)))
All z-scores computed over rolling 30-minute window (5-min for
arrival rate). Set to 0 in exclusion windows.

**Primary regression:**
Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t
β₃ is the primary test statistic.

**Key papers:**
- Kyle (1985) — Econometrica — lambda and informed trading
- Glosten and Milgrom (1985) — JFE — adverse selection framework
- Cont, Kukanov, Stoikov (2014) — JFEC — OFI predicting returns
- Roll (1984) — JF — implicit spread estimator
- Easley, Lopez de Prado, O'Hara (2012) — RFS — VPIN

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
  