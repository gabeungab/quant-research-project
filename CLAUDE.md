# CLAUDE.md — Project Context

## What this project is
Studying the regime-conditioned price impact of Trade Flow
Imbalance (TFI) in ES futures. The regime detector is the primary
contribution — a two-component composite (Kyle's lambda + trade
arrival rate) that identifies periods of elevated information
asymmetry in real time from trades-only data. TFI serves two
explicitly separated roles: (1) a contemporaneous characterization
of adverse selection amplification, framed as a confounded
specification sensitivity result (not an empirical finding), and
(2) a forward return predictability test, which produced a null
result (β₃ = 0.000203, p = 0.335) — the primary empirical finding,
interpreted as an efficiency result about information incorporation
speed in ES futures.

Key design constraint: with trades-only data, a fully orthogonal
regime detector is impossible — any detector derived from aggressor-
side volume shares informational content with TFI. Lambda + TAR is
the least circular available detector given this constraint. We
deliberately sacrifice some detection accuracy (per Ahern, 2018,
the most accurate trades-only detector uses TFI variants directly)
for research design cleanliness. Two layers of circularity are
documented: (1) detector construction level — lambda derived from
the same signed flow inputs as TFI; (2) regression interaction
level — high TFI bars mechanically have elevated RegimeScore,
confirmed by monotonic quintile pattern. Both are stated explicitly
in the paper's limitations section.

Final deliverables:
- Clean GitHub repository with fully reproducible code
- 12–15 page research paper in LaTeX/PDF

## Research goals and standards
This project targets quant researcher and trader internship
applications at top firms. It must be defensible in a technical
interview — every line of code, every methodological choice,
every result.

---

## Project phases
- Phase 0: Foundations — Python (Stream A), Statistics (Stream B),
  Microstructure (Stream C).
- Phase 1: Data familiarization — load full sample, clean,
  descriptive stats
- Phase 2: Research question selection and literature review
- Phase 3: Exploratory analysis of chosen phenomenon
- Phase 4: Formal statistical analysis, in/out-of-sample testing
- Phase 5: Paper writing — Sections 1 and 2 (Introduction and
  Literature Review)
- Phase 6: Code polish and final repository cleanup

## Current status

**Phase 4: COMPLETE. All findings finalized.**

formal_analysis.py is fully professionalized and all diagnostic
tests have been run and interpreted. phase4_findings.md contains
the complete final record. PAPER.md Sections 3–6 are updated and
draft-complete. All interpretations are locked.

**Phase 4 final results summary:**

Primary regression (T+1): β₃ = 0.000203, p = 0.335 — null.
ES futures incorporate regime-conditioned TFI within one bar.
Primary efficiency finding. Non-confounded. β₃ is upward-biased
by mechanical co-elevation of TFI and RegimeScore (confirmed by
quintile monotonicity), making the null result a conservative bound.

Contemporaneous (lagged regime spec): β₃ = 0.000425, p = 0.067
— not significant. Collapse from initial run (β₃ = 0.0015,
p < 0.001) confirms initial finding was substantially circularity-
driven. RegimeScore lag-1 autocorrelation = 0.8427 — lagging by
one bar removes only ~16% of circularity. Residual confounding is
the dominant explanation for p = 0.067. Market maker calibration
application not empirically supported.

Horizon analysis: null at T+5 (p = 0.960) and T+15 (p = 0.709).
Information incorporation confirmed within one bar.

Subsample stability: null in May–Sep (p = 0.524) and Oct–Dec
(p = 0.399). Null result is a structural property, not a sub-period
artifact.

OOS validation (2026 Jan–Mar, N = 14,774): full-period
β₃ = 0.000239, p = 0.004. Episodic — driven entirely by the final
two weeks (Feb 23–Mar 6). January (p = 0.412) and February
(p = 0.209) are individually null. Late-period β₃ = 0.000531,
p = 0.012; early-period β₃ = 0.000046, p = 0.515. Permutation
test confirms late-period result is not random noise. Lambda window
stability does not differ materially between late and early OOS
(ratio 1.03x). No orthogonal conditioning variable explains the
late-period significance. In-sample efficiency finding stands.

Lagged regime conditioning: β₃ = −0.000089, p = 0.677 — null under
fully predetermined conditioning with zero simultaneity. Cleanest
possible test.

Midday subsample: β₃ = 0.000549, p = 0.162 — not significant but
2.7x full-sample coefficient. Pre-specified from theory. Circularity
explanation constrained: coefficient moves away from β₁, not toward
it.

Stable regime conditions: bottom tercile of lambda window std
(threshold 211 contracts) produces β₃ = 0.000629, p = 0.074 vs
full-sample p = 0.335 and unstable p = 0.587. Monotonic gradient
consistent with detector quality hypothesis. Stable bars concentrate
in 13–14:xx. Does not replicate OOS. Exploratory only.

TFI quintile interaction: no quintile survives Bonferroni (α=0.01).
T+1 null is not a linearity artifact. Monotonic Q1→Q5 pattern
confirms second circularity layer at regression interaction level.

Regime transition dynamics: transition β₄ = 0.000275, p = 0.018
(4,376 bars). Retired as primary finding — both diagnostics support
circularity. Delta magnitude: large-delta β = 0.000414 (6.6x
small-delta β = 0.000063). Threshold robustness: significant at
0.4 and 0.5, disappears at 0.6.

**Next phase:** Phase 5 — write PAPER.md Sections 1 (Introduction)
and 2 (Literature Review). No additional analysis required.

---

## Project structure
quant-research-project/
    /data        — data documentation only, no raw files
    /notebooks   — exploratory Jupyter notebooks (not started)
    /src         — clean reusable Python modules
        data_loader.py         — data loading, cleaning, stats, plotting
        formal_analysis.py     — Phase 4 formal regression analysis
        plot_signals.py        — Phase 3 component plots
        signal_construction.py — signal and regime score functions
        test_load.py           — Phase 1 data loading and stats checks
        test_signals.py        — sanity checks for signal outputs
    /results
        /phase1              — Phase 1 outputs
            daily_stats.csv
            daily_volume_over_time.png
            intraday_trade_arrival.png
            intraday_volume.png
            intraday_volatility.png
            trade_size_distribution.png
        /phase3              — Phase 3 exploratory plots
            lambda_timeseries.png          lambda_intraday.png
            lambda_distribution.png        lambda_individual_days.png
            arrival_timeseries.png         arrival_intraday.png
            arrival_distribution.png       arrival_individual_days.png
            regime_score_timeseries.png    regime_score_intraday.png
            regime_score_distribution.png  regime_score_individual_days.png
        /phase4              — Phase 4 formal analysis outputs
            primary_regression.txt
            contemporaneous_regression.txt
            oos_primary_regression.txt
            lagged_regime_regression.txt
            midday_regression.txt
            quintile_interaction_regression.txt
            transition_dynamics_regression.txt
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
        phase4_findings.md    — Phase 4 complete findings record
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

phase4_findings.md — complete internal record of all Phase 4
test results, interpretations, diagnostic outputs, and design
decisions. More detailed than PAPER.md. Used as the source of
truth for paper writing.

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
Two components only: Kyle's lambda (30-bar rolling OLS) and trade
arrival rate (5-bar rolling). Roll spread removed — non-orthogonal
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
Uses lagged RegimeScore_{t-1}. TFI-Return confounding within the
bar remains irreducible with trades-only data. Presented as a
specification sensitivity result only — NOT a primary empirical
finding. β₃ = 0.000425, p = 0.067 (not significant).

**Primary regression:**
Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t +
               β₃·(TFI_t × RegimeScore_t) +
               β₄·Return_t + β₅·TFI_{t-1} + ε_t
β₃ is the primary test statistic.
Final result: β₃ = 0.000203, p = 0.335 — null efficiency finding.

**Key papers:**
- Kyle (1985) — Econometrica — lambda and informed trading
- Glosten and Milgrom (1985) — JFE — adverse selection framework
- Cont, Kukanov, Stoikov (2014) — JFEC — OFI predicting returns
- Roll (1984) — JF — implicit spread estimator (removed from detector)
- Easley, Lopez de Prado, O'Hara (2012) — RFS — VPIN
- Ahern (2018) — NBER — informed trading proxies; order imbalance
  and flow autocorrelation most accurate but circular with TFI
- Dufour and Engle (2000) — JF — inter-trade duration and
  informed trading; theoretical basis for TAR as regime component

## Data
- Source: Databento, GLBX.MDP3, Trades schema
- In-sample: 2025-05-01 to 2025-12-30 (169 trading days)
  Location: ~/Desktop/Quant Research Project/raw-data/
            GLBX-20250501-20251231/
- Out-of-sample: 2026-01-02 to 2026-03-06 (46 trading days)
  Location: ~/Desktop/Quant Research Project/raw-data/
            GLBX-20260101-20260309/
- Fields used: ts_event_et (Eastern time), price, size,
  side (B/A/N)
- Fields ignored: rtype, publisher_id, instrument_id, action,
  depth, flags, ts_in_delta, sequence (all constant or irrelevant)
- Symbol rolls: ESM5 (May–Jun) → ESU5 (Jul–Sep) →
  ESZ5 (Oct–Dec) → ESH6 (Jan–Mar 2026)
- Excluded dates: 2025-05-26, 2025-07-04, 2025-09-01,
  2025-11-27 (holidays/half-sessions)

## Tech stack
Python 3.13, pandas, NumPy, scipy, statsmodels, matplotlib,
databento library

---

## Standards for Claude Code to enforce
- Train/test split is time-based: in-sample 2025, out-of-sample
  2026. Never touch out-of-sample data for specification search.
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
- Point out methodological errors or oversights
- Do not generate analysis, write paper sections, or interpret
  results
- When I show you an error, explain what caused it before giving
  the fix
