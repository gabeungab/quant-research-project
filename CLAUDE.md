# CLAUDE.md — Project Context

## What this project is
Original empirical research on ES futures tick data from CME Globex.
Studying a market microstructure/factor phenomenon using a trades-only
dataset with aggressor side (B/S/N). Research question TBD in Phase 2
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
Phase 0, Stream A. Completed:
- working load_day(), load_all_days(), resample_to_bars(),
  remove_outliers(), compute_tfi() in src/data_loader.py

---

## Project structure
quant-research-project/
    /data        — data documentation only, no raw files
    /notebooks   — exploratory Jupyter notebooks (not started)
    /src         — clean reusable Python modules
        data_loader.py  — all data loading and signal functions
    /results     — saved figures and output tables (not started)
    /paper       — LaTeX research paper (not started)
    JOURNAL.md   — running research log
    CLAUDE.md    — this file

## Data
- Source: Databento, GLBX.MDP3, Trades schema
- In-sample: 2025-05-01 to 2025-12-31
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
