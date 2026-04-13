# ES Futures Microstructure: Regime-Conditioned Order Flow Predictability

Empirical microstructure study of whether an informed trading regime
detector amplifies the forward return predictability of Trade Flow
Imbalance in E-mini S&P 500 futures using trades-only data.

---

## Research Question and Motivation

Does conditioning Trade Flow Imbalance on a real-time informed trading
regime — identified from Kyle's lambda and trade arrival rate — amplify
its predictive power for next-bar returns in ES futures? If so, a market
maker observing accumulating order flow in a high-regime state has a
quantifiable measure of elevated adverse selection exposure.

The primary finding is a null result: regime-conditioned TFI does not
significantly predict forward returns at any horizon from T+1 through
T+15, implying that ES futures incorporate regime-conditioned order flow
information within one 1-minute bar. A key secondary finding is that
when the regime detector's lambda estimation window is stable — defined
by low rolling signed-flow variance — the regime-TFI interaction
produces a statistically significant forward return amplification
(β₃ = 0.001016, p = 0.033), motivating a future test with an orthogonal
limit order book detector.

---

## Methodology

- **Signal:** Trade Flow Imbalance (TFI) — normalized buyer- vs
  seller-initiated volume per 1-minute bar from aggressor side field
- **Regime detector:** Multiplicative composite of Kyle's lambda
  (30-bar rolling OLS) and trade arrival rate (5-bar rolling),
  combined as `logistic(z_lambda) × logistic(z_arrival)`. Lambda
  identifies elevated price impact; TAR confirms active market
  participation, suppressing misclassification of illiquid episodes
- **Primary regression:** `Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t + β₃·(TFI_t × RegimeScore_t) + β₄·Return_t + β₅·TFI_{t-1} + ε_t`
  with Newey-West HAC standard errors (maxlags=5)
- **Key design constraint:** With trades-only data, a fully orthogonal
  regime detector is impossible — lambda and TFI share signed order
  flow as a common input. Two layers of circularity are documented and
  their directional effect on all estimates is analyzed explicitly
- **Sample:** 58.8M clean RTH trades, 169 trading days, N = 55,634
  regression bars after warmup and boundary removal

---

## Key Results

| Test | β₃ | p-value | Result |
|---|---|---|---|
| Primary T+1 forward return | 0.000371 | 0.234 | Null — primary efficiency finding |
| Stable lambda conditions | 0.001016 | 0.033 | Significant — strongest positive finding |
| Lagged regime conditioning | −0.000152 | 0.634 | Null — cleanest possible test |
| OOS full period (2026) | 0.000371 | 0.006 | Episodic — driven by final 2 weeks only |
| Contemporaneous T+0 | 0.000617 | 0.078 | Not significant — confounded |
| Horizon T+5 | 0.000090 | 0.798 | Null |
| Horizon T+15 | 0.000081 | 0.833 | Null |
| Detector validation (contemp. slope) | — | <0.001 | 2.278x amplification in high-regime bars |

---

## Repository Structure

```
quant-research-project/
├── src/
│   ├── data_loader.py          # Data loading, cleaning, TFI, returns
│   ├── signal_construction.py  # Kyle's lambda, TAR, regime score
│   ├── formal_analysis.py      # Full Phase 4 regression pipeline
│   ├── plot_signals.py         # Phase 3 signal component plots
│   ├── test_load.py            # Phase 1 data loading checks
│   └── test_signals.py         # Signal output sanity checks
├── results/
│   ├── phase1/                 # Descriptive statistics and plots
│   ├── phase3/                 # Signal component exploratory plots
│   └── phase4/                 # Regression output files and CSVs
├── paper/
│   ├── PAPER.md                # Working paper draft (Sections 3–8 complete)
│   └── phase4_findings.md      # Complete internal findings record
├── data/                       # Data documentation only — no raw files
├── JOURNAL.md                  # Chronological research session log
└── CLAUDE.md                   # Project context and design decisions
```

---

## Data

Trade-level data from CME Globex via Databento (schema: GLBX.MDP3,
Trades). Raw data files are not included in this repository.

- **In-sample:** 2025-05-01 through 2025-12-30 (169 trading days)
- **Out-of-sample:** 2026-01-02 through 2026-03-06 (46 trading days)
- **Instrument:** ES (E-mini S&P 500 futures), front-month contract,
  Regular Trading Hours only (9:30 AM – 4:00 PM ET)

To obtain the data, create a Databento account at
[databento.com](https://databento.com) and download the GLBX.MDP3
Trades feed for the date ranges above. Place the resulting `.dbn.zst`
files in the following directories:

```
~/Desktop/Quant Research Project/raw-data/GLBX-20250501-20251231/
~/Desktop/Quant Research Project/raw-data/GLBX-20260101-20260309/
```

Or update the `DATA_DIR` and `OOS_DATA_DIR` paths at the top of
`src/formal_analysis.py` to match your local directory structure.

---

## Reproducing Results

**Setup**

Requires Python 3.13. Install all dependencies with:

```bash
pip install pandas numpy scipy statsmodels matplotlib databento
```

**Steps**

1. Obtain and place data as described above
2. Run the full Phase 4 regression pipeline:
   ```bash
   python3 src/formal_analysis.py
   ```
3. All regression summaries, coefficient tables, and diagnostic outputs
   are saved to `results/phase4/`

To reproduce Phase 3 signal component plots:

```bash
python3 src/plot_signals.py
```

---

## Working Paper

The working paper draft is available at `paper/PAPER.md`. All 8 sections
(Introduction, Literature Review, Data, Signal Construction, Results, 
Robustness, Market Maker Implications, Future Research) are complete. 

---

## Author

Gabriel Ungab — Georgia Tech, Mathematics (Probability & Statistics), 
Class of 2029. Targeting quantitative research and trading roles.
