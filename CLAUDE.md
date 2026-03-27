# CLAUDE.md — Project Context

## What this project is
Original empirical research on ES futures tick data from CME Globex.
Studying a market microstructure/factor phenomenon using a trades-only
dataset with aggressor side (B/A/N). Research question TBD in Phase 2
after exploratory analysis.

Final deliverables:
- Clean GitHub repository with fully reproducible code
- 12-15 page research paper in LaTeX/PDF

## Research goals and standards
This project targets quant researcher and trader internship
applications at top firms. It must be defensible in a technical
interview — every line of code, every methodological choice,
every result.

The project has two layers:
- Layer 1: Rigorous statistical characterization of one specific
  market phenomenon in ES futures trades data. Narrow and deep,
  not broad.
- Layer 2: What the findings imply for a real market participant
  (trader or market maker). Quantitatively specific, references
  actual results.

---

## Project phases
- Phase 0: Foundations — Python (Stream A), Statistics (Stream B),
  Microstructure (Stream C).
- Phase 1: Data familiarization — load full sample, clean,
  descriptive stats
- Phase 2: Research question selection and literature review
- Phase 3: Exploratory analysis of chosen phenomenon
- Phase 4: Formal statistical analysis, in/out-of-sample testing
- Phase 5: Layer 2 implications (market participant behavior)
- Phase 6: Paper writing and code polish

## Current status
Phase 1 complete. Phase 2 is next.

Phase 0 Stream A completed:
- load_day(), load_all_days(), resample_to_bars(),
  remove_outliers(), compute_tfi(), compute_returns(),
  run_ols(), test_autocorrelation(), plot_overview(),
  plot_phase1() in src/data_loader.py
- EXCLUDED_DATES constant in load_all_days() for holiday exclusions
- Stream B and C: not yet started — begin in parallel with Phase 2

Phase 1 completed:
- Final clean dataset: ~58.8M RTH trades, 169 trading days
  (4 holidays excluded: Memorial Day, Independence Day,
  Labor Day, day before Thanksgiving)
- Data quality checks complete: calendar spreads filtered,
  price outliers removed (114,413 trades, 0.19%),
  duplicate timestamps confirmed legitimate
- compute_daily_stats() function complete, daily_stats saved
  to results/daily_stats.csv
- Five exploratory plots saved to results/
- RESEARCH.md Section 3 (Data) complete — working paper draft

Key findings from Phase 1:
- Buy/sell volume ratio: 1.003 — balanced across sample
- Trade sizes highly right-skewed: median 1, max 1,968 contracts
- Two activity regimes: stable ~1M contracts/day May-Sep,
  elevated and volatile Oct-Dec
- Intraday volume and trade arrival: modified inverse-J shape
  with massive MOC-driven close spike
- Intraday volatility: open spike only, flat through close —
  diverges from volume due to uninformed MOC order flow

---

## Project structure
quant-research-project/
    /data        — data documentation only, no raw files
    /notebooks   — exploratory Jupyter notebooks (not started)
    /src         — clean reusable Python modules
        data_loader.py  — all data loading, cleaning, signal,
                          stats, and plotting functions
    /results     — saved figures and daily_stats.csv
    /paper       — LaTeX research paper (not started)
    JOURNAL.md   — running research log (dated session entries)
    NOTES.md     — general technical concept reference
    RESEARCH.md  — working paper draft (formal research output)
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

RESEARCH.md — working paper draft. Contains only content
that belongs in the final research paper. Language is formal
and calibrated for an audience of graduate-level quants and
quant recruiters. Explains findings by connecting them to
already-known concepts in one clause — does not explain
the concepts themselves. Every claim is supported by a
number from the analysis. Sections added incrementally as
phases complete.

The distinction: if a concept applies to any project,
it goes in NOTES. If it is specific to this dataset and
analysis, it goes in JOURNAL (findings) or RESEARCH
(if paper-ready). RESEARCH never contains explanations
of standard concepts — only empirical observations
connected to those concepts.

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
  ESZ5 (Oct-Dec) → ESH6 (Jan-Mar 2026).
  Handle roll dates in data pipeline.
- Excluded dates: 2025-05-26, 2025-07-04, 2025-09-01,
  2025-11-27 (holidays/half-sessions, see EXCLUDED_DATES
  constant in data_loader.py and data/README.md)

## Tech stack
Python 3.13, pandas, NumPy, scipy, statsmodels, matplotlib,
databento library

---

## Standards for Claude Code to enforce
- Train/test split is time-based: in-sample 2025, out-of-sample
  2026. Never suggest touching out-of-sample data before Phase 4
  validation.
- Methodology must be pre-registered in JOURNAL.md before formal
  tests. Flag if I run tests before documenting the plan.
- All regressions on financial time series require Newey-West
  standard errors — flag if I use default OLS standard errors.
- Flag if I run multiple hypothesis tests without Bonferroni
  correction.
- Transaction cost analysis required before any result claim.
  ES futures tick size = 0.25 index points.
- All results must be reproducible from /src code on raw data.

## Rules for Claude Code in this project
- Help debug code I wrote — do not write code for me
- Explain concepts I am trying to understand
- Point out methodological errors or oversights
- Do not generate analysis, write paper sections, or interpret
  results
- When I show you an error, explain what caused it before giving
  the fix
