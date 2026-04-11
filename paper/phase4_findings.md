# Phase 4 — Formal Statistical Analysis: Findings

## Overview

Phase 4 applies the regime detector constructed in Phase 3 to a
formal regression framework. All tests use the updated two-component
regime detector (Kyle's lambda + trade arrival rate, Roll removed),
post-only announcement exclusion windows, and Newey-West standard
errors (maxlags=5). The in-sample period is 2025-05-01 through
2025-12-30 (169 trading days, N = 55,634 regression bars after
warmup and boundary removal). The out-of-sample period is
2026-01-02 through 2026-03-06 (46 trading days, N = 14,774 bars).

All regressions use the primary specification unless otherwise noted:

```
Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t
             + β₃·(TFI_t × RegimeScore_t)
             + β₄·Return_t + β₅·TFI_{t-1} + ε_t
```

β₃ is the primary test statistic throughout. All reported p-values
use HAC standard errors (Newey-West, maxlags=5).

---

## 1. Data Preparation

**Sample construction:**
- Raw trades: 58,874,430 clean RTH trades after outlier removal
  (114,413 trades removed, 0.194%)
- Regression bars after NaN/warmup/boundary removal: 55,634
- High-regime bars (RegimeScore > 0.5): 23,992 (43.1%)
- Low-regime bars (RegimeScore ≤ 0.5): 31,642 (56.9%)
- Date range: 2025-05-01 10:30 → 2025-12-30 15:58

**Change from initial Phase 4 run:**
The initial run used a three-component regime detector (lambda +
Roll + TAR) and ±30 min announcement exclusion. This rerun uses
lambda + TAR only and +30 min post-announcement exclusion. N
increased from 53,787 to 55,634 from retaining pre-announcement
windows and removing Roll's NaN propagation.

---

## 2. Primary Regression — Forward Return (T+1)

**Specification:** RegimeScore_t is contemporaneous with TFI_t and
fully predetermined relative to Return_{t+1}.

**Results:**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | -4.42e-06 | -0.486 | 0.627 |
| tfi (β₁) | 0.000628 | 4.695 | < 0.001 *** |
| regime_score (β₂) | 8.42e-06 | 0.562 | 0.574 |
| tfi_x_regime (β₃) | 0.000203 | 0.964 | 0.335 |
| lag_return (β₄) | -0.488 | -53.862 | < 0.001 *** |
| lag_tfi (β₅) | -4.99e-05 | -0.907 | 0.365 |

R² = 0.236, N = 55,634.

**Interpretation:**

β₃ = 0.000203, p = 0.335. The null hypothesis — that the regime
does not amplify TFI's forward predictive power — is not rejected.
ES futures prices incorporate regime-conditioned order flow
information within one 1-minute bar. This is the primary empirical
finding of the project.

The unconditional TFI effect (β₁ = 0.000628, p < 0.001) is
significant and stable throughout, replicating Cont, Kukanov, and
Stoikov (2014). This effect does not concentrate in high-regime
conditions — β₃ is indistinguishable from zero. R² = 0.236 is
driven almost entirely by the lag_return mean-reversion control.

**Confounding status:** Non-confounded. Return_{t+1} is not in
lambda's estimation window and is not known when TFI_t or
RegimeScore_t are observed. The null result is a genuine efficiency
finding.

**Note on estimation bias from quintile analysis (Section 9):**
β₃ inherits upward bias from mechanical co-elevation of TFI and
RegimeScore — high signed flow simultaneously elevates both. This
means the null result holds under conditions favorable to finding
a positive β₃, making it a conservative bound on the true causal
effect. The efficiency conclusion is strengthened by this finding.

---

## 3. Contemporaneous Characterization — Same-Bar Return (T+0)

**Specification:** Uses lagged RegimeScore_{t-1} to remove regime-
level simultaneity. TFI_t and Return_t remain confounded — both
constructed from bar t's trades, irreducible with trades-only data.

```
Return_t = α + β₁·TFI_t + β₂·RegimeScore_{t-1}
         + β₃·(TFI_t × RegimeScore_{t-1})
         + β₅·TFI_{t-1} + ε_t
```

**Results:**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | -8.26e-06 | -1.001 | 0.317 |
| tfi (β₁) | 0.001205 | 8.045 | < 0.001 *** |
| regime_score_lag (β₂) | 1.77e-05 | 1.288 | 0.198 |
| tfi_x_regime_lag (β₃) | 0.000425 | 1.830 | 0.067 |
| lag_tfi (β₅) | -0.000128 | -1.757 | 0.079 |

R² = 0.008, N = 55,634.

**Interpretation:**

β₃ = 0.000425, p = 0.067. Not significant at conventional
thresholds (α = 0.05). The collapse from the initial run
(β₃ = 0.0015, z = 7.214, p < 0.001) confirms the initial finding
was substantially circularity-driven.

The p = 0.067 is explained by two overlapping mechanisms. The
dominant explanation is residual confounding through regime
autocorrelation: RegimeScore lag-1 autocorrelation = 0.8427,
meaning lagging by one bar removes only ~16% of the circularity
since RegimeScore_{t-1} ≈ RegimeScore_t in most consecutive bars.
The secondary possibility is genuine predictive signal — these
two cannot be cleanly separated with trades-only data. Given the
autocorrelation magnitude, residual confounding is the more
parsimonious explanation.

**Confounding status:** Retains TFI-Return confounding within bar t.
This is a specification sensitivity result showing how much the
contemporaneous result depends on circularity. The initial 2.7x
amplification and the market maker calibration application based
on it are no longer empirically supported.

---

## 4. Horizon Analysis — T+5 and T+15

**Specification:** Cumulative log return over next h bars
(same-day only, cross-day windows nulled). Same X matrix as
primary regression.

**Results:**

| Horizon | β₃ | z-stat | p-value | N |
|---|---|---|---|---|
| T+5 | 0.000012 | 0.050 | 0.960 | 54,789 |
| T+15 | -0.000098 | -0.373 | 0.709 | 53,099 |

Unconditional TFI β₁ significant at both horizons (~0.00071-0.00078,
p < 0.001).

**Interpretation:** No regime interaction at any horizon.
Information incorporation confirmed within one bar with no residual
regime-conditioned predictability at 5 or 15 bar horizons.

---

## 5. Subsample Stability

**Specification:** Primary regression restricted to each subsample.

**Results:**

| Subsample | N | β₃ | p-value |
|---|---|---|---|
| Full (May-Dec) | 55,634 | 0.000203 | 0.335 |
| May-Sep 2025 | 35,001 | 0.000177 | 0.524 |
| Oct-Dec 2025 | 20,633 | 0.000251 | 0.399 |

**Interpretation:** Null result stable across both activity regimes.
The directional pattern (higher β₃ in Oct-Dec) is consistent with
the regime detector operating better in elevated-volatility
environments, but comparing two non-significant p-values cannot
confirm this. Presented as null result consistent across both
subsamples.

---

## 6. Out-of-Sample Validation — 2026

**Specification:** Primary regression on held-out 2026 data
(2026-01-02 through 2026-03-06). 2026-specific announcement dates
(FOMC: Jan 28, Mar 18; CPI: Jan 13, Feb 11, Mar 11; NFP: Jan 9,
Feb 11, Mar 6). No parameters refit.

**Full OOS result:** β₃ = 0.000239, z = 2.908, p = 0.004,
N = 14,774.

### OOS Diagnostic Tests

Seven diagnostic tests were run to determine whether the
significance is systematic or episodic.

**Diagnostic 1 — HAC adequacy:** Residual autocorrelation at lags
6-10 ranges from +0.001 to +0.020 — negligible. HAC maxlags=5
was adequate. Rules out standard error inflation.

**Diagnostic 2 — RegimeScore distribution:** OOS mean RegimeScore
= 0.4618 vs in-sample 0.4357 (ratio 1.06x). High-regime fraction
45.1% vs 43.1%. Well below the 1.1x concern threshold. Rules out
structural regime elevation.

**Diagnostic 3 — Realized volatility:** OOS mean |return| = 0.000224
vs in-sample 0.000533 (ratio 0.42x). Both price ranges in the
same ballpark (in-sample 5,596-7,041; OOS 6,716-7,072). Lower OOS
volatility makes significance harder to find, not easier. Rules
out volatility-mechanical inflation.

**Diagnostic 4 — Result by month:** January 2026: β₃ = 0.000060,
p = 0.412. February 2026: β₃ = 0.000169, p = 0.209. Neither
month is individually significant.

**Diagnostic 5 — Rolling 10-day windows:** January through
mid-February: β₃ mostly null (-0.000168 to +0.000200). Late
February through March 6: β₃ spikes to 0.000356-0.000531, with
7 consecutive significant windows from February 26 onward. 8 of
37 windows significant, all contiguous at the end of the period.
Significance is entirely episodic.

**Diagnostic 6 — TFI distribution:** OOS extreme |TFI| > 0.3
fraction 1.3% vs 1.0% in-sample — marginal. Does not explain
OOS significance.

**Diagnostic 7 — Permutation test (N=1000):** Actual OOS β₃ in
top 0.5% of permutation null distribution (permutation p = 0.005,
parametric p = 0.004). The late-period result is not random noise.

### Late vs Early OOS Decomposition

| Period | β₃ | p-value | Return std (bps) | R² |
|---|---|---|---|---|
| Early OOS (Jan-Feb 22, N=11,484) | 0.000046 | 0.515 | 3.041 | 0.002 |
| Late OOS (Feb 23-Mar 6, N=3,290) | 0.000531 | 0.012 | 5.792 | 0.112 |

Late OOS had approximately 2x the realized volatility of early
OOS. The early OOS R² = 0.002 and lag_return coefficient -0.053
(vs in-sample -0.488) indicate the early period had structurally
different — and unusually weak — return dynamics.

### Lambda Stability in Late vs Early OOS

Lambda window stability was compared to test whether the late OOS
significance connects to stable estimation conditions.

- Early OOS mean lambda window std: 279.37 contracts
- Late OOS mean lambda window std: 287.60 contracts (ratio 1.029x)

Late OOS was marginally more unstable. The late OOS significance
concentrates in unstable lambda bars (β₃ = 0.000874, p = 0.050)
rather than stable ones (β₃ = 0.000381, p = 0.365). The stable
estimation hypothesis does not explain the late OOS result. The
late OOS significance and the in-sample stable condition finding
have different underlying mechanisms and cannot be unified.

### Final OOS Interpretation

The OOS significance (p = 0.004) is episodic, driven by a specific
two-week period (February 23 through March 6, 2026) of elevated
realized volatility (~2x the preceding period). January and
February individually are null. The permutation test confirms the
late-period result is not random noise — a genuine cross-sectional
relationship existed during that episode. No orthogonal conditioning
variable explains or replicates it. The in-sample efficiency
finding stands unchanged.

---

## 7. Lagged Regime Conditioning

**Specification:** RegimeScore_{t-1} and TFI_t × RegimeScore_{t-1}
replace contemporaneous terms. Zero simultaneity — no circularity
of any kind.

**Result:** β₃ = -0.000089, z = -0.417, p = 0.677, N = 55,634.

**Interpretation:** Null under the cleanest possible conditioning
structure. Prior-bar regime information has no carry-forward
predictive value. Regime-conditioned adverse selection resolves
entirely within one bar. The higher p-value here (0.677 vs 0.335
in primary) does not indicate lagged regime is less predictive —
both are null and the difference is sampling variation.

---

## 8. Midday Subsample Analysis and Stable Regime Conditions

### 8A. Midday Subsample (11:00-13:00 ET)

**Specification:** Primary regression on bars timestamped 11:00-
12:59 ET. Pre-specified from theory before running: lambda
estimation most stable (full 30-bar window, no overnight gap),
TAR most informative (lowest baseline activity), structural
contamination absent. Not p-hacking.

**Result:** β₃ = 0.000549, z = 1.398, p = 0.162, N = 20,279.

**Interpretation:** Not significant. Coefficient is 2.7x larger
than full-sample and p is approximately 3x smaller. Directionally
consistent with the regime detector quality hypothesis.

The circularity explanation is less compelling here: under pure
circularity, the interaction coefficient should collapse toward
the unconditional TFI slope (β₁ ≈ 0.0006), not away from it.
The midday β₃ = 0.000549 moves away from β₁ — the opposite of
what mechanical inflation predicts. This is consistent with
genuine signal diluted by open and close noise, though both
interpretations remain possible.

### 8B. Stable Regime Conditions Test

**Specification:** Rolling signed-flow standard deviation in the
30-bar lambda window used as a direct stability proxy. Bottom
tercile (std ≤ 211 contracts) = most stable estimation conditions.
Threshold derived post-hoc — exploratory only.

**Results:**

| Condition | N | β₃ | p-value |
|---|---|---|---|
| Full sample | 55,634 | 0.000203 | 0.335 |
| Stable lambda (bottom tercile) | 18,355 | 0.000629 | 0.074 |
| Unstable lambda (top tercile) | 18,355 | 0.000239 | 0.587 |

Stable-condition β₃ = 0.000629 is 3.1x the full-sample result.
High-regime fraction higher in stable sample (51.6% vs 43.1%).
Stable bars concentrate in mid-to-late afternoon (13-14:xx peak),
not strictly in the midday window, meaning the time-based and
stability-based criteria capture partially overlapping but distinct
sets of bars.

**Afternoon subsample (13:xx-14:xx):** β₃ = 0.000375, p = 0.258
— weaker than midday and stable lambda. Afternoon hours do not
outperform midday.

**Final interpretation:** The stable lambda gradient is the
strongest directional in-sample finding: β₃ = 0.000629, p = 0.074
versus full-sample β₃ = 0.000203, p = 0.335. The coefficient
moves away from β₁ (ruling out pure circularity). However the
threshold was derived post-hoc and does not replicate OOS —
presented as exploratory only, as a hypothesis for future research.
With LOB data, a direct orthogonal stability criterion (bid-ask
spread variance, depth stability, cancellation rate) could replace
the signed-flow proxy and be tested confirmatorily on new data.

---

## 9. TFI Quintile Interaction — Linearity and Circularity Evidence

**Specification:** Four quintile dummy interactions replacing the
continuous TFI term (Q3 omitted reference). Bonferroni correction:
α = 0.01 per test (family-wise α = 0.05 across five tests).

**Results:**

| Quintile | Coefficient | z-stat | p-value | Bonferroni |
|---|---|---|---|---|
| Q1 (most negative TFI) | -0.000013 | -0.382 | 0.702 | — |
| Q2 | -0.000025 | -1.000 | 0.317 | — |
| Q4 | 0.000047 | 1.811 | 0.070 | — |
| Q5 (most positive TFI) | 0.000071 | 1.984 | 0.047 | — |

No quintile survives Bonferroni correction (threshold: p < 0.01).

**Two findings from one test:**

**Finding 1 — Linearity robustness:** The T+1 null is not a
consequence of forcing linearity on the regime interaction. Even
when the regime interaction is allowed to vary freely across TFI
ranges, no concentration emerges. The null is robust to functional
form.

**Finding 2 — Second circularity layer:** The monotonic pattern
(Q1→Q5 increasing coefficients) reveals circularity operating at
the regression interaction level, beyond the detector construction
level. The mechanism: higher |TFI| → higher signed flow → higher
lambda → higher RegimeScore → mechanically larger interaction term
(TFI × RegimeScore). Under Kyle (1985), genuine informed trading
should concentrate in moderate quintiles (hump-shaped) because
informed traders split orders. The monotonic pattern contradicts
this and is consistent with mechanical co-elevation.

Both circularity layers are now fully documented:
1. Detector construction level: lambda derived from same signed
   flow inputs as TFI
2. Regression interaction level: confirmed by monotonic quintile
   pattern

Neither layer invalidates the T+1 null. The upward bias in β₃
from layer 2 makes the null result more conservative — the
efficiency finding holds even under favorable estimation conditions
for the alternative hypothesis.

---

## 10. Regime Transition Dynamics — Retired as Primary Finding

**Specification:** TransitionToHigh_t = 1 if RegimeScore_t > 0.5
and RegimeScore_{t-1} ≤ 0.5, excluding bars where prior bar was
in exclusion window. 4,376 transition bars (7.9% of sample).

**Initial result:**

| Term | Coefficient | p-value |
|---|---|---|
| Sustained: tfi_x_regime (β₃) | 0.000140 | 0.512 |
| Transition: tfi_x_transition (β₄) | 0.000275 | 0.018 |

Appeared significant. Two diagnostics were run.

### Delta Magnitude Diagnostic

| Delta Group | N | Transition β | p-value |
|---|---|---|---|
| Small delta (below median 0.307) | 2,188 | 0.000063 | 0.633 |
| Large delta (above median 0.307) | 2,188 | 0.000414 | 0.016 |

Large-delta β is 6.6x small-delta β. Under genuine informed trader
timing, the effect should be consistent regardless of delta size.
The 6.6x concentration in large-delta transitions strongly supports
mechanical inflation: both the transition flag and the interaction
magnitude are driven by the same underlying directional signed
flow.

### Threshold Robustness

| Threshold | Transition bars | Transition β | p-value |
|---|---|---|---|
| 0.4 | 4,112 | 0.000400 | 0.001 |
| 0.5 | 4,376 | 0.000275 | 0.018 |
| 0.6 | 4,195 | 0.000174 | 0.154 |

Significant at 0.4 and 0.5, disappears at 0.6. Lower thresholds
produce more large-delta transitions mechanically. The threshold
dependence mirrors the delta magnitude finding and further
supports mechanical inflation.

### Final Interpretation

The transition finding is substantially explained by circularity.
Both diagnostics consistently support the mechanical inflation
explanation. Presented in the robustness section of the paper as
an illustration of how circularity manifests in dynamic
specifications — a transparency item showing rigorous diagnostic
work, not a positive secondary finding.

---

## 11. Transaction Cost Analysis

Mean ES price: 6,460.55. One-way cost: 0.387 bps. Round-trip:
0.774 bps.

The T+1 null eliminates any directional trading application
regardless of costs. The contemporaneous β₃ = 0.000425 is not
statistically significant, so the break-even TFI analysis from
the initial run is no longer empirically grounded.

---

## 12. Summary of All Key Results

| Test | β₃ | p-value | Final Verdict |
|---|---|---|---|
| **Primary: T+1 forward return** | **0.000203** | **0.335** | **Null — primary efficiency finding** |
| Contemporaneous T+0 (lagged regime) | 0.000425 | 0.067 | Not significant — specification sensitivity |
| Horizon T+5 | 0.000012 | 0.960 | Null |
| Horizon T+15 | -0.000098 | 0.709 | Null |
| Subsample May-Sep | 0.000177 | 0.524 | Null |
| Subsample Oct-Dec | 0.000251 | 0.399 | Null |
| OOS 2026 (full period) | 0.000239 | 0.004 | Episodic — final 2 weeks only |
| OOS early (Jan-Feb 22) | 0.000046 | 0.515 | Null |
| OOS late (Feb 23-Mar 6) | 0.000531 | 0.012 | Episodic, not replicable |
| Lagged regime conditioning | -0.000089 | 0.677 | Null — cleanest possible test |
| Midday subsample (11-12:xx) | 0.000549 | 0.162 | Directionally consistent, not significant |
| Stable lambda (bottom tercile) | 0.000629 | 0.074 | Directionally consistent, exploratory only |
| Afternoon subsample (13-14:xx) | 0.000375 | 0.258 | Null |
| Quintile interaction | — | — | No quintile survives Bonferroni |
| Transition dynamics (sustained) | 0.000140 | 0.512 | Null |
| Transition dynamics (transition) | 0.000275 | 0.018 | Retired — circularity confirmed |
| Unconditional TFI (all specs) | ~0.0006 | < 0.001 | Consistently significant |
| RegimeScore lag-1 autocorrelation | — | — | 0.8427 — residual confounding dominant |

---

## 13. Research Design Decisions and Limitations

**Two layers of circularity documented:**
(1) Detector construction level: lambda derived from rolling OLS
of price changes on signed order flow — the same aggressor-side
volume underlying TFI. Any regime detector built from trades-only
data shares this informational content with TFI.
(2) Regression interaction level: high TFI bars mechanically have
elevated RegimeScore because high signed flow elevates lambda. The
interaction term (TFI × RegimeScore) is therefore upward-biased
in extreme TFI bars, confirmed by the monotonic quintile pattern.
This bias makes the T+1 null result conservative.

**Regime detector choice:** Lambda + TAR is the least circular
available detector from trades-only data, chosen deliberately
over more accurate alternatives (Ahern, 2018) to maximize research
design cleanliness. Remaining circularity is fully documented.

**Exclusion windows:** Post-announcement only (+30 min after FOMC,
CPI, NFP). Pre-announcement retained as potentially informed.
Unscheduled market stress not excluded — acknowledged limitation.

**Roll removal:** Non-orthogonal to lambda (both spike at identical
directional price episodes), fails in one-sided markets, redundant
with TAR.

**Contemporaneous finding sensitivity:** Collapse from β₃=0.0015
(initial confounded spec) to β₃=0.000425 (lagged regime, not
significant) demonstrates the initial finding was substantially
circularity-driven. RegimeScore lag-1 autocorrelation = 0.8427
explains why lagging by one bar removes only ~16% of circularity.

**OOS finding:** Aggregate p = 0.004 is episodic, driven by the
final two weeks of a 46-day period. January and February are
individually null. The permutation test confirms the late-period
result is not random noise, but no orthogonal conditioning
variable explains or replicates it. The in-sample efficiency
finding is not overturned.

---

## 14. Future Research Directions

**Direction 1: Orthogonal regime detector with LOB data**
Replace lambda + TAR with LOB-derived measures (bid-ask spread
dynamics, cancellation rates, depth changes) that share no
informational content with TFI. Removes both circularity layers.
Sub-questions: (A) does regime-conditioned TFI predict forward
returns at 1-minute resolution with an orthogonal detector — if
yes, the in-sample null was a detection precision problem rather
than true market efficiency; (B) does it predict at sub-minute
resolution? The stable lambda gradient (β₃ = 0.000629, p = 0.074)
generates a specific testable hypothesis: an orthogonal LOB-based
stability criterion would produce a confirmatory test of whether
stable estimation conditions genuinely amplify TFI-return
predictability.

**Direction 2: p% intra-bar amplification framework**
If a future study finds significant contemporaneous amplification
with an orthogonal detector, the p% framework provides the correct
bridge to a real-time market maker application: compute TFI at
fixed elapsed-time intervals within each bar (10%...90% elapsed),
regress bar-end return on partial TFI conditioned on lagged
RegimeScore_{t-1}, and derive the empirical weight schedule θ_p
as a function of bar completion percentage. Not applicable with
current results. Constructible from current tick data but deferred
pending a significant contemporaneous finding with orthogonal data.
