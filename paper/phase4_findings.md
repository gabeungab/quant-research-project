# Phase 4 — Formal Statistical Analysis: Findings

## Overview

Phase 4 applies the regime detector constructed in Phase 3 to a
formal regression framework. All tests use the final two-component
multiplicative regime detector (Kyle's lambda × trade arrival rate,
Roll removed), post-only announcement exclusion windows (+30 min
after FOMC, CPI, NFP), and Newey-West HAC standard errors
(maxlags=5). The in-sample period is 2025-05-01 through 2025-12-30
(169 trading days, N = 55,634 regression bars after warmup and
boundary removal). The out-of-sample period is 2026-01-02 through
2026-03-06 (46 trading days, N = 14,774 bars).

**Detector formulation:** The final multiplicative formulation
(logistic(z_lambda) × logistic(z_arrival)) differs materially from
the earlier additive formulation (logistic(z_lambda + z_arrival)).
The two produce a Pearson correlation of 0.923 on in-sample data
with 69.0% bar-level classification agreement. Under the
multiplicative formulation 12.1% of bars are classified as
high-regime (RegimeScore > 0.5) versus 43.1% under the additive
formulation. All results in this document use the multiplicative
formulation unless explicitly noted.

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
- High-regime bars (RegimeScore > 0.5): 6,719 (12.1%)
- Low-regime bars (RegimeScore ≤ 0.5): 48,915 (87.9%)
- Date range: 2025-05-01 10:30 → 2025-12-30 15:58

**RegimeScore autocorrelation (multiplicative detector):**
- Lag-1: 0.8064 (lagging removes ~19% of circularity)
- Lag-5: 0.2477
- Lag-30: −0.0057

---

## 2. Regime Detector Validation

**Validation test — contemporaneous slope by regime:**
A formal regression of Return_t on TFI_t, a high-regime dummy
(RegimeScore_t > 0.5), and their interaction confirms the detector
identifies periods of elevated within-bar price impact:

- Low-regime TFI slope (β₁): 0.001193 (z = 17.907, p < 0.001)
- High-regime amplification (β₃): 0.001525 (z = 9.496, p < 0.001)
- High-regime slope (β₁ + β₃): 0.002717
- Amplification ratio: 2.278x

The detector correctly and significantly identifies periods of
elevated within-bar price impact. This test uses contemporaneous
RegimeScore_t — TFI-Return confounding is present and acknowledged.
It is a directional sanity check, not a causal test.

**Pre-announcement validation:** Infeasible with RTH-only data.
CPI and NFP releases occur at 8:30 AM before market open, leaving
only 6 observable FOMC pre-announcement windows — insufficient for
a meaningful test. Not pursued.

---

## 3. Primary Regression — Forward Return (T+1)

**Specification:** RegimeScore_t is contemporaneous with TFI_t and
fully predetermined relative to Return_{t+1}. Non-confounded in
the forward-return sense (Return_{t+1} not in lambda's estimation
window). Circularity at the interaction level remains — see
Section 9 for documentation.

**Results:**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −4.46×10⁻⁶ | −0.597 | 0.550 |
| tfi (β₁) | 0.000637 | 5.886 | <0.001 *** |
| regime_score (β₂) | 1.75×10⁻⁵ | 0.753 | 0.451 |
| tfi_x_regime (β₃) | 0.000371 | 1.191 | 0.234 |
| lag_return (β₄) | −0.488 | −53.865 | <0.001 *** |
| lag_tfi (β₅) | −4.96×10⁻⁵ | −0.902 | 0.367 |

R² = 0.236, N = 55,634.

**Interpretation:**

β₃ = 0.000371, p = 0.234. H₀ not rejected. ES futures incorporate
regime-conditioned TFI within one 1-minute bar. Primary efficiency
finding. The unconditional TFI effect (β₁ = 0.000637, p < 0.001)
replicates Cont, Kukanov, and Stoikov (2014) but does not survive
round-trip transaction costs (~0.774 bps) and carries no trading
application. R² = 0.236 driven almost entirely by lag_return
mean-reversion control.

**Estimation bias:** β₃ is upward-biased by mechanical co-elevation
of TFI and RegimeScore under the multiplicative formulation (high
signed flow elevates both simultaneously). The null holds under
estimation conditions favorable to H₁ — making the efficiency
conclusion a conservative bound.

---

## 4. Contemporaneous Characterization — Same-Bar Return (T+0)

**Specification:** Uses lagged RegimeScore_{t-1} to remove regime-
level simultaneity. TFI_t and Return_t remain confounded —
irreducible with trades-only data. Specification sensitivity result
only, not a predictive test.

```
Return_t = α + β₁·TFI_t + β₂·RegimeScore_{t-1}
         + β₃·(TFI_t × RegimeScore_{t-1})
         + β₅·TFI_{t-1} + ε_t
```

**Results:**

| Variable | Coefficient | z-stat | p-value |
|---|---|---|---|
| const | −8.16×10⁻⁶ | −1.214 | 0.225 |
| tfi (β₁) | 0.001200 | 10.238 | <0.001 *** |
| regime_score_lag (β₂) | 3.53×10⁻⁵ | 1.680 | 0.093 |
| tfi_x_regime_lag (β₃) | 0.000617 | 1.761 | 0.078 |
| lag_tfi (β₅) | −0.000105 | −1.769 | 0.077 |

R² = 0.008, N = 55,634.

**Interpretation:**

β₃ = 0.000617, p = 0.078. Not significant. RegimeScore lag-1
autocorrelation = 0.8064 under multiplicative formulation — lagging
removes ~19% of circularity, leaving substantial residual confounding
as the dominant explanation for p = 0.078. Genuine signal cannot be
ruled out but cannot be separated from confounding with trades-only
data. No empirically grounded market maker calibration can be
derived from this result.

---

## 5. Horizon Analysis — T+5 and T+15

**Results:**

| Horizon | β₃ | z-stat | p-value | N |
|---|---|---|---|---|
| T+5 | 0.000090 | 0.256 | 0.798 | 54,789 |
| T+15 | 0.000081 | 0.212 | 0.833 | 53,099 |

Unconditional TFI β₁ significant at both horizons
(~0.000696–0.000719, p < 0.001).

**Interpretation:** No regime interaction at any horizon.
Information incorporation confirmed within one bar.

---

## 6. Subsample Stability

**Results:**

| Subsample | N | β₃ | p-value |
|---|---|---|---|
| Full (May–Dec) | 55,634 | 0.000371 | 0.234 |
| May–Sep 2025 | 35,001 | 0.000283 | 0.495 |
| Oct–Dec 2025 | 20,633 | 0.000543 | 0.207 |

**Interpretation:** Null result stable across both activity regimes.
Directional pattern (higher β₃ in Oct–Dec) consistent with regime
detector operating better in elevated-volatility environments but
not confirmable from two non-significant p-values.

---

## 7. Out-of-Sample Validation — 2026

**Full OOS result (multiplicative detector):**
β₃ = 0.000371, z = 2.768, p = 0.006, N = 14,774.

Note: OOS β₃ equals the full in-sample β₃ by coincidence of
rounding. The OOS coefficient and its significance arise from the
late-period episode documented below.

### OOS Diagnostic Tests

Seven diagnostics targeting six candidate explanations for OOS
significance:

**Diagnostic 1 — HAC adequacy:** Residual autocorrelation lags
6–10: +0.001 to +0.020. Negligible. HAC maxlags=5 adequate.
Rules out standard error inflation.

**Diagnostic 2 — RegimeScore distribution:** OOS mean = 0.229
vs in-sample 0.215 (ratio 1.06x). High-regime fraction 12.8%
vs 12.1%. Rules out structural regime elevation.

**Diagnostic 3 — Realized volatility:** OOS mean |return| ratio
0.42x in-sample. Price ranges compatible. Lower OOS volatility
makes significance harder. Rules out volatility-mechanical
inflation.

**Diagnostic 4 — By month:** January 2026: β₃ = 0.000047,
p = 0.671. February 2026: β₃ = 0.000325, p = 0.162. Neither
individually significant.

**Diagnostic 5 — Rolling 10-day windows:** January through
mid-February: β₃ near zero, mostly null. Late February through
March 6: β₃ = 0.000559–0.000837, 7 consecutive significant
windows from February 26 onward. 7 of 37 windows significant,
all contiguous at the end of the period. Significance entirely
episodic.

**Diagnostic 6 — TFI distribution:** OOS extreme |TFI| > 0.3
fraction 1.3% vs 1.0% in-sample. Marginal. Does not explain
OOS significance.

**Diagnostic 7 — Permutation test (N=1,000):** Actual OOS β₃
in top 0.5% of permutation null distribution (permutation
p = 0.005, parametric p = 0.006). Late-period result is not
random noise.

### Late vs Early OOS Decomposition

| Period | β₃ | p-value | Return std (bps) | R² |
|---|---|---|---|---|
| Early OOS (Jan–Feb 22, N=11,484) | 0.000066 | 0.559 | 3.041 | 0.002 |
| Late OOS (Feb 23–Mar 6, N=3,290) | 0.000774 | 0.022 | 5.792 | 0.111 |

Late OOS had ~2x the realized volatility of early OOS. Early OOS
R² = 0.002 and lag_return coefficient −0.053 (vs in-sample −0.488)
indicate structurally different and unusually weak return dynamics
in the early period.

### Lambda Stability in Late vs Early OOS

- Early OOS mean lambda window std: 279.37 contracts
- Late OOS mean lambda window std: 287.60 contracts (ratio 1.029x)

Late OOS was marginally more unstable. Late OOS significance
concentrates in unstable lambda bars (β₃ = 0.001176, p = 0.150)
rather than stable ones (β₃ = 0.000576, p = 0.326) — neither
significant in the small subsample but the pattern is opposite
to the stable estimation hypothesis. The in-sample stable
condition finding and late OOS episodic significance have
different underlying mechanisms and cannot be unified.

### Final OOS Interpretation

The OOS significance (p = 0.006) is episodic, driven by a specific
two-week period (February 23 through March 6, 2026) of elevated
realized volatility (~2x the preceding period). January and
February individually are null. The permutation test confirms
the late-period result is not random noise. No orthogonal
conditioning variable explains or replicates it. The in-sample
efficiency finding stands unchanged.

---

## 8. Lagged Regime Conditioning

**Result:** β₃ (tfi_x_regime_lag) = −0.000152, z = −0.476,
p = 0.634, N = 55,634.

**Interpretation:** Null under fully predetermined conditioning
with zero simultaneity. Prior-bar regime information has no
carry-forward predictive value. Regime-conditioned adverse selection
resolves entirely within one bar. Cleanest possible test —
strengthens the efficiency finding.

---

## 9. Midday Subsample Analysis and Stable Regime Conditions

### 9A. Midday Subsample (11:00–13:00 ET)

**Result:** β₃ = 0.000812, z = 1.449, p = 0.147, N = 20,279.

**Interpretation:** Not significant. Coefficient 2.2x full-sample
(0.000371). Directionally consistent with detector quality
hypothesis. Circularity explanation constrained: coefficient
moves away from β₁ (not toward it), inconsistent with pure
mechanical inflation. Both interpretations remain possible.

### 9B. Stable Regime Conditions Test

**Specification:** Rolling signed-flow standard deviation in the
30-bar lambda window as stability proxy. Bottom tercile
(std ≤ 211 contracts) = most stable estimation conditions.
Threshold derived from in-sample distribution — post-hoc.

**Results:**

| Condition | N | β₃ | p-value |
|---|---|---|---|
| Full sample | 55,634 | 0.000371 | 0.234 |
| Stable lambda (bottom tercile) | 18,355 | 0.001016 | 0.033 |
| Unstable lambda (top tercile) | 18,355 | 0.000331 | 0.664 |

**Interpretation:**

Stable-condition β₃ = 0.001016, p = 0.033 — statistically
significant at α = 0.05 (z = 2.135). This is 2.7x the full-sample
estimate. Gradient is monotonic and strong. High-regime bars
constitute 16.5% of the stable sample vs 12.1% of full sample —
consistent with stable estimation windows correctly classifying
more bars as genuinely high-regime. Stable bars concentrate in
mid-to-late afternoon (13–14:xx peak).

**This is the strongest positive finding in Phase 4.** When lambda
estimation conditions are stable, the multiplicative regime
detector produces a statistically detectable amplification of
TFI's forward predictive power.

**Caveats:** Threshold is post-hoc and derived from in-sample
distribution. The finding does not replicate in the OOS period —
lambda stability does not differ materially between late and early
OOS (ratio 1.03x), and late OOS significance concentrates in
unstable rather than stable lambda bars. Presented as a genuine
finding with an exploratory threshold, pointing toward a specific
and testable future research direction.

**Afternoon subsample (13–14:xx):** β₃ = 0.000715, p = 0.131,
N = 19,842 — not significant, weaker than stable lambda. Afternoon
hours alone do not replicate the stability criterion effect.

---

## 10. TFI Quintile Interaction — Linearity and Circularity Evidence

**Specification:** Four quintile dummy interactions (Q3 omitted
reference). Bonferroni correction: α = 0.01 per test.

**Results:**

| Quintile | Coefficient | z-stat | p-value | Bonferroni |
|---|---|---|---|---|
| Q1 (most negative TFI) | −0.000020 | −0.362 | 0.717 | — |
| Q2 | −0.000038 | −0.786 | 0.432 | — |
| Q4 | 0.000081 | 1.684 | 0.092 | — |
| Q5 (most positive TFI) | 0.000126 | 2.076 | 0.038 | — |

No quintile survives Bonferroni correction (threshold: p < 0.01).

**Two findings:**

1. Linearity robustness: T+1 null is not a consequence of forcing
   linearity on the interaction term.

2. Second circularity layer: monotonic Q1→Q5 pattern confirms
   mechanical co-elevation at the regression interaction level.
   Under Kyle (1985), genuine informed trading should concentrate
   in moderate quintiles (hump-shaped). Monotonic pattern is
   inconsistent with this and consistent with mechanical inflation.

Both circularity layers fully documented:
1. Detector construction level: lambda derived from same signed
   flow as TFI
2. Regression interaction level: confirmed by monotonic quintile
   pattern

The upward bias from layer 2 makes the T+1 null a conservative
bound on the true causal effect.

---

## 11. Regime Transition Dynamics

**Specification:** TransitionToHigh_t = 1 if RegimeScore_t > 0.5,
RegimeScore_{t-1} ≤ 0.5, and prior bar not in exclusion window.

**Results (multiplicative detector):**
- Transition bars: 2,354 (4.2% of sample)
- Sustained β₃ (tfi_x_regime): 0.000143, p = 0.684
- Transition β₄ (tfi_x_transition): 0.000430, p = 0.061

**Interpretation:** The transition finding is outright null under
the multiplicative detector (p = 0.061). The detector's greater
selectivity (12.1% vs 43.1% high-regime) reduces low-to-high
crossings from 4,376 to 2,354 bars, and the apparent transition
effect does not reach conventional significance. Two diagnostics
confirm mechanical inflation is the correct explanation.

**Delta magnitude diagnostic:**

| Delta group | N | Transition β | p-value |
|---|---|---|---|
| Small delta (≤ median 0.270) | 1,177 | 0.000046 | 0.875 |
| Large delta (> median 0.270) | 1,177 | 0.000618 | 0.035 |

Large-delta β is 13.4x small-delta β. Extreme concentration in
large-delta transitions is inconsistent with genuine informed
trader timing and strongly consistent with mechanical inflation.

**Threshold robustness:**

| Threshold | Transition bars | Transition β | p-value |
|---|---|---|---|
| 0.4 | 2,868 | 0.000200 | 0.263 |
| 0.5 | 2,354 | 0.000430 | 0.061 |
| 0.6 | 1,684 | 0.000362 | 0.190 |

No threshold produces a significant result. The transition
specification is mechanically inflated and the null result is
the correct interpretation. Not evidence of genuine informed
trader timing.

---

## 12. Transaction Cost Analysis

Mean ES price: 6,460.55. One-way cost: 0.387 bps. Round-trip:
0.774 bps.

The T+1 null eliminates any directional trading application
regardless of costs. Contemporaneous β₃ = 0.000617 is not
statistically significant — the break-even TFI analysis is not
empirically grounded and is not reported as a finding.

---

## 13. Summary of All Key Results

| Test | β₃ | p-value | Final Verdict |
|---|---|---|---|
| **Primary: T+1 forward return** | **0.000371** | **0.234** | **Null — primary efficiency finding** |
| Contemporaneous T+0 (lagged regime) | 0.000617 | 0.078 | Not significant — spec sensitivity |
| Horizon T+5 | 0.000090 | 0.798 | Null |
| Horizon T+15 | 0.000081 | 0.833 | Null |
| Subsample May–Sep | 0.000283 | 0.495 | Null |
| Subsample Oct–Dec | 0.000543 | 0.207 | Null |
| OOS 2026 (full period) | 0.000371 | 0.006 | Episodic — final 2 weeks only |
| OOS early (Jan–Feb 22) | 0.000066 | 0.559 | Null |
| OOS late (Feb 23–Mar 6) | 0.000774 | 0.022 | Episodic, not replicable |
| Lagged regime conditioning | −0.000152 | 0.634 | Null — cleanest possible test |
| Midday subsample (11–12:xx) | 0.000812 | 0.147 | Directionally consistent, not significant |
| **Stable lambda (bottom tercile)** | **0.001016** | **0.033** | **Significant — strongest positive finding** |
| Afternoon subsample (13–14:xx) | 0.000715 | 0.131 | Not significant |
| Quintile interaction | — | — | No quintile survives Bonferroni |
| Transition dynamics (sustained) | 0.000143 | 0.684 | Null |
| Transition dynamics (transition) | 0.000430 | 0.061 | Null — circularity confirmed |
| Unconditional TFI (all specs) | ~0.0006 | <0.001 | Consistently significant |
| RegimeScore lag-1 autocorrelation | — | — | 0.8064 (multiplicative detector) |
| Validation test 1 (contemp slope) | — | — | β₃=0.001525, p<0.001 — PASSES |

---

## 14. Research Design Decisions and Limitations

**Detector formulation:** Final multiplicative formulation
(logistic(z_lambda) × logistic(z_arrival)) enforces hierarchical
structure — lambda provides the primary signal, TAR confirms or
suppresses it. 12.1% high-regime classification under multiplicative
vs 43.1% under additive. Material design choice.

**Two layers of circularity documented:**
(1) Detector construction level: lambda derived from rolling OLS
of price changes on signed order flow — the same aggressor-side
volume underlying TFI.
(2) Regression interaction level: high TFI bars mechanically have
elevated RegimeScore because high signed flow elevates lambda.
Confirmed by monotonic quintile pattern. Upward bias on β₃ makes
T+1 null a conservative bound.

**Regime detector choice:** Lambda + TAR multiplicative is the
least circular available detector from trades-only data, chosen
deliberately over more accurate alternatives (Ahern, 2018) to
maximize research design cleanliness. Remaining circularity is
fully documented.

**Exclusion windows:** Post-announcement only (+30 min after FOMC,
CPI, NFP). Pre-announcement retained as potentially informed.
Unscheduled market stress not excluded — acknowledged limitation.

**Roll removal:** Non-orthogonal to lambda, fails in one-sided
markets, redundant with TAR.

**Contemporaneous finding:** Collapse from initial confounded spec
(β₃ = 0.0015, p < 0.001) to lagged-regime multiplicative spec
(β₃ = 0.000617, p = 0.078) confirms initial finding was
substantially circularity-driven. RegimeScore lag-1 autocorrelation
= 0.8064 explains why lagging removes only ~19% of circularity.

**Stable regime conditions:** Significant result (p = 0.033) under
multiplicative detector. Threshold post-hoc, does not replicate
OOS. Strongest positive finding — motivates future LOB-based
confirmatory test.

**OOS finding:** Aggregate p = 0.006 is episodic, driven by the
final two weeks of the 46-day period. January and February
individually null. Permutation test confirms late-period result
is not noise. No orthogonal conditioning variable explains it.
In-sample efficiency finding unchanged.

---

## 15. Future Research Directions

**Direction 1: Orthogonal regime detector with LOB data**
Replace lambda + TAR with LOB-derived measures (bid-ask spread
dynamics, cancellation rates, depth changes) that share no
informational content with TFI. Removes both circularity layers.
The stable lambda gradient (β₃ = 0.001016, p = 0.033) generates
a specific testable hypothesis: an orthogonal LOB-based stability
criterion should produce significant β₃ in the primary T+1
regression. Sub-questions: (A) does regime-conditioned TFI predict
forward returns at 1-minute resolution with an orthogonal detector?
(B) does it predict at sub-minute resolution?

**Direction 2: p% intra-bar amplification framework**
If a future study finds significant contemporaneous amplification
with an orthogonal detector, compute TFI at fixed elapsed-time
intervals within each bar (10%...90% elapsed), regress bar-end
return on partial TFI conditioned on lagged RegimeScore_{t-1},
and derive the empirical weight schedule θ_p as a function of
bar completion percentage. Constructible from current tick data
but deferred pending a significant contemporaneous finding with
orthogonal data.
