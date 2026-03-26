# ES Futures Microstructure Research

Empirical research project studying a market microstructure phenomenon
in ES futures tick data from CME Globex (Databento).

## Status
In progress — Phase 0 (foundations). Research question TBD.

## Data
Databento GLBX.MDP3 trades schema, May 2025 through March 2026.
58.9 million clean RTH trades across 173 trading days (in-sample).

## Stack
Python 3.13 · pandas · NumPy · statsmodels · matplotlib · databento

## Structure
- `/src` — data loading, cleaning, and signal construction functions
- `/notebooks` — exploratory analysis (coming in Phase 1)
- `/results` — figures and output tables (coming in Phase 3+)
- `/paper` — research paper in LaTeX (coming in Phase 6)
