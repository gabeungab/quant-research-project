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

β₃ is the primary test statistic throughout. A significant positive
β₃ would indicate the regime amplifies TFI's forward predictive
power. All reported p-values use HAC standard errors.

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
increased from 53,787 to 55,634 — the additional bars come from
retaining pre-announcement windows (previously excluded) and
removing Roll's NaN propagation.

---

## 2. Primary Regression — Forward Return (T+1)

**Specification:** Primary specification above. RegimeScore_t is
contemporaneous with TFI_t and predetermined relative to
Return_{t+1}.

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
significant and stable throughout, replicating the Cont, Kukanov,
and Stoikov (2014) finding that order flow imbalance predicts
short-term returns. However this effect does not concentrate in
high-regime conditions — the interaction β₃ is indistinguishable
from zero.

The dominant control is lag_return (β₄ = -0.488), capturing the
well-known mean reversion in 1-minute returns from bid-ask bounce.
This R² of 0.236 is driven almost entirely by this control. Without
lag_return, R² is below 0.01, confirming the regime-TFI interaction
does not explain return variation in any meaningful way.

**Confounding status:** This regression is non-confounded.
Return_{t+1} is not in lambda's estimation window and is not known
when TFI_t or RegimeScore_t are observed. The null result is a
genuine efficiency finding.

---

## 3. Contemporaneous Characterization — Same-Bar Return (T+0)

**Specification:** Uses lagged RegimeScore_{t-1} to remove regime-
level simultaneity, since Return_t and RegimeScore_t share bar t's
time window. TFI_t and Return_t remain confounded (both constructed
from bar t's trades — irreducible with trades-only data).

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
thresholds (α = 0.05). This is a major change from the initial
Phase 4 run (β₃ = 0.0015, z = 7.214, p < 0.001) and is
informative about the nature of the prior finding.

Two changes were made simultaneously: (1) Roll was removed from
the regime detector, and (2) RegimeScore is now lagged (t-1 rather
than t). The collapse from highly significant to marginally
insignificant under this cleaner specification is itself evidence
that the initial finding was substantially driven by circularity
rather than genuine causal amplification. With the regime
predetermined and Roll removed, the mechanical relationship between
signed flow and same-bar prices is broken and the result largely
disappears.

**Confounding status:** This regression retains TFI-Return
confounding within bar t — both are constructed from the same bar's
trades. This cannot be removed with trades-only single-instrument
data. The regime-level simultaneity is removed by using lagged
RegimeScore. The result is still not a causal finding and should
not be interpreted as validating the regime detector's ability to
detect genuine adverse selection amplification. Given that β₃ is
not significant, the market maker calibration application based on
the initial 2.7x amplification estimate is no longer empirically
supported. This finding is presented as a specification sensitivity
result: the contemporaneous signal is fragile and disappears under
cleaner conditioning.

---

## 4. Horizon Analysis — T+5 and T+15

**Specification:** Cumulative log return over next h bars
(same-day only, cross-day windows nulled out). Same X matrix as
primary regression.

**Results:**

| Horizon | β₃ | z-stat | p-value | N |
|---|---|---|---|---|
| T+5 | 0.000012 | 0.050 | 0.960 | 54,789 |
| T+15 | -0.000098 | -0.373 | 0.709 | 53,099 |

Unconditional TFI β₁ remains significant at both horizons
(~0.00071-0.00078, p < 0.001).

**Interpretation:**

No regime interaction at any horizon beyond T+1. Information
incorporation is confirmed within one 1-minute bar — there is no
residual regime-conditioned predictability at 5 or 15 bar horizons.
The unconditional TFI effect persists but does not vary with regime,
consistent with the primary null result.

---

## 5. Subsample Stability

**Specification:** Primary regression restricted to each subsample.

**Results:**

| Subsample | N | β₃ | p-value |
|---|---|---|---|
| Full (May-Dec) | 55,634 | 0.000203 | 0.335 |
| May-Sep 2025 | 35,001 | 0.000177 | 0.524 |
| Oct-Dec 2025 | 20,633 | 0.000251 | 0.399 |

**Interpretation:**

The null result is stable across both activity regimes. May-Sep
represents the stable low-volume period (~1M contracts/day) and
Oct-Dec the elevated volatile period. β₃ is indistinguishable from
zero in both subsamples. The unconditional TFI β₁ is also stable
(0.000606-0.000680) across subsamples, confirming the base
predictability finding is not period-specific.

---

## 6. Out-of-Sample Validation — 2026

**Specification:** Primary regression applied to held-out 2026 data
(2026-01-02 through 2026-03-06). Regime detector applied using
2026-specific announcement dates (FOMC: Jan 28, Mar 18; CPI:
Jan 13, Feb 11, Mar 11; NFP: Jan 9, Feb 11, Mar 6). No parameters
refit — same specification applied to new data.

**Results:**

β₃ = 0.000239, z = 2.908, p = 0.004, N = 14,774.

**Interpretation:**

The OOS result is significant at α = 0.01, which is the opposite
of what the in-sample null result would predict.

The in-sample period (169 days) shows no regime-conditioned
forward predictability. The OOS period (46 days, January-March
2026) shows a statistically significant positive β₃. Several
explanations must be considered.

First, sample size and episode dominance: 46 trading days is
substantially smaller than 169 days. A few high-regime informed
trading episodes in the OOS period — potentially related to the
unusual macro environment (government shutdown affecting data
releases, elevated geopolitical uncertainty, Fed communication in
an unusual policy transition period) — could drive a significant
result that would not persist over a longer horizon.

Second, structural difference: The January-March 2026 period
represents a distinct market environment from May-December 2025.
If regime-conditioned TFI predictability genuinely varies across
market environments, the OOS period may represent a regime in which
the detector's signal is more informative.

Third, false positive risk: With N = 14,774 and a single test, the
probability of a false positive at α = 0.01 is not negligible,
particularly given the unusual macro context of the OOS period.

The OOS result does not overturn the in-sample null. It raises the
possibility that regime-conditioned TFI predictability may emerge
episodically in specific market environments, which is itself an
interesting finding. However it cannot be interpreted as strong
evidence of genuine forward predictability given the sample size
and contextual differences. The paper presents this finding
transparently with all three interpretations acknowledged.

---

## 7. Lagged Regime Conditioning

**Specification:** Primary regression with RegimeScore_{t-1} and
TFI_t × RegimeScore_{t-1} replacing contemporaneous regime terms.
Fully predetermined — no simultaneity between any variables.

**Results:**

β₃ (tfi_x_regime_lag) = -0.000089, z = -0.417, p = 0.677,
N = 55,634.

**Interpretation:**

Null result under fully predetermined regime conditioning. Knowing
the market was in an informed regime one bar ago does not amplify
TFI's predictive power for the next bar. This is the cleanest
possible test — no circularity of any kind — and the null is
unambiguous. This strengthens the efficiency finding: regime-
conditioned adverse selection is fully resolved within one bar,
leaving no carry-forward effect that a market participant could
exploit using prior-bar regime information.

This result belongs in the robustness section of the paper. It
confirms the primary null under the most stringent non-simultaneous
conditioning structure tested.

---

## 8. Midday Subsample Analysis (11:00-13:00 ET)

**Specification:** Primary regression restricted to bars with
timestamps between 11:00 and 12:59 ET. This window is where the
regime detector operates most accurately: lambda estimation is
most stable (full 30-bar window of current-session data), TAR
z-score is most informative (lowest baseline activity), and
structural contamination from open and close dynamics is absent.

**Results:**

β₃ = 0.000549, z = 1.398, p = 0.162, N = 20,279.

**Interpretation:**

Not significant. However the coefficient (0.000549) is meaningfully
larger than the full-sample result (0.000203) and the z-statistic
(1.398) approaches but does not reach conventional thresholds.
The result is directionally consistent with the hypothesis that
the regime detector's signal quality is better in the midday window
— the effect is larger here — but the magnitude is insufficient to
produce statistical significance.

Two interpretations exist. Under the genuine signal interpretation,
the midday window reveals a stronger underlying effect that the
full-sample test dilutes with open and close noise. Under the
circularity interpretation, midday has stronger lambda estimation
stability, which could produce a tighter mechanical relationship
between lambda-derived RegimeScore and TFI. However circularity
predicts the worst effects at the open (highest lambda variance,
strongest signed flow), not midday, making the circularity
explanation less compelling for a midday-specific result.

Both interpretations are acknowledged. The midday result is
presented as directionally interesting but not significant —
preserving the efficiency narrative while noting the suggestive
pattern.

---

## 9. TFI Quintile Interaction

**Specification:** Replaces the single continuous TFI interaction
term with four quintile dummy interactions (quintile 3 as omitted
reference). Tests whether the regime interaction concentrates in
specific TFI ranges rather than being linear throughout. Bonferroni
correction applied: α = 0.01 per quintile test (family-wise
α = 0.05 across five tests).

**Results:**

| Quintile | Coefficient | z-stat | p-value | Bonferroni |
|---|---|---|---|---|
| Q1 (most negative TFI) | -0.000013 | -0.382 | 0.702 | — |
| Q2 | -0.000025 | -1.000 | 0.317 | — |
| Q4 | 0.000047 | 1.811 | 0.070 | — |
| Q5 (most positive TFI) | 0.000071 | 1.984 | 0.047 | — |

No quintile survives Bonferroni correction (threshold: p < 0.01).

**Interpretation:**

No quintile interaction survives the corrected significance
threshold. The null result in the primary regression is not a
consequence of forcing linearity — even when the regime interaction
is allowed to vary freely across TFI quintiles, no significant
concentration emerges.

The directional pattern (Q4 and Q5 showing nominally larger
coefficients) is consistent with higher positive TFI having a
slightly larger regime interaction, but this pattern does not reach
significance after correction. Q5 (p = 0.047) would be nominally
significant at α = 0.05 without correction but fails the corrected
threshold, and given five simultaneous tests this is not surprising
by chance alone.

The pattern is not hump-shaped — if anything it is monotonic across
quintiles from Q1 to Q5 — which is more consistent with the
circularity explanation (higher |TFI| → higher lambda → higher
RegimeScore → larger interaction mechanically) than with genuine
informed trading concentration in moderate quintiles. This is
acknowledged.

---

## 10. Regime Transition Dynamics

**Specification:** Adds a transition dummy interaction to the
primary regression. TransitionToHigh_t = 1 if RegimeScore_t > 0.5
and RegimeScore_{t-1} ≤ 0.5, and the prior bar was not in an
exclusion window (to prevent false transitions from exclusion
resets). 4,376 transition bars identified.

```
Return_{t+1} = α + β₁·TFI_t + β₂·RegimeScore_t
             + β₃·(TFI_t × RegimeScore_t)
             + β₄·(TFI_t × TransitionToHigh_t)
             + β₅·Return_t + β₆·TFI_{t-1} + ε_t
```

**Results:**

| Term | Coefficient | p-value |
|---|---|---|
| Sustained: tfi_x_regime (β₃) | 0.000140 | 0.512 |
| Transition: tfi_x_transition (β₄) | 0.000275 | 0.018 |

N = 55,634.

**Interpretation:**

The transition-specific effect is significant (p = 0.018) while the
sustained high-regime effect remains null (p = 0.512). This is the
most novel finding in Phase 4. TFI is more predictive of next-bar
returns at the first bar of a regime transition than during
sustained high-regime conditions.

This is consistent with Kyle (1985) optimal informed trader timing:
informed traders may concentrate their order flow precisely as
the market transitions into an informed state, creating the
transition itself and generating detectable TFI-return predictability
at the transition moment before the market fully adjusts.

Two interpretations are stated explicitly in the paper. Under the
genuine signal interpretation, informed traders front-run regime
shifts. Under the circularity interpretation, the first bar of a
transition has a large delta in RegimeScore by construction, which
could mechanically inflate the interaction term. However, the
exclusion window fix prevents false transitions from exclusion resets,
and circularity predicts a smooth continuous level effect — not a
discrete effect concentrated at the 0.5 threshold crossing. The
transition-specific result is qualitatively different from what
circularity predicts, making it more consistent with genuine signal.

Important caveats: p = 0.018 is significant at α = 0.05 but not
at α = 0.01. With 4,376 transition bars out of 55,634 total bars
(7.9%), the transition subgroup is reasonably sized but the result
is marginal. This finding is presented as the most interesting
result in the additional tests, with both interpretations fully
acknowledged and without overclaiming.

---

## 11. Transaction Cost Analysis

Mean ES price: 6,460.55. One-way cost: 0.387 bps. Round-trip: 0.774 bps.

The T+1 specification does not survive round-trip costs even under
the most favorable TFI values — the null result eliminates any
trading application regardless of costs.

The contemporaneous characterization (β₃ = 0.000425, p = 0.067)
is not statistically significant under the lagged regime
specification, which means the break-even TFI analysis from the
initial run (which used the confounded specification) is no longer
empirically grounded. The market maker calibration application is
reframed accordingly — the contemporaneous amplification is
fragile to specification and cannot be presented as a calibrated
quantitative input.

---

## 12. Summary of All Key Results

| Test | β₃ | p-value | Verdict |
|---|---|---|---|
| Primary T+1 (main) | 0.000203 | 0.335 | Null |
| Contemporaneous T+0 (lagged regime) | 0.000425 | 0.067 | Not significant |
| Horizon T+5 | 0.000012 | 0.960 | Null |
| Horizon T+15 | -0.000098 | 0.709 | Null |
| Subsample May-Sep | 0.000177 | 0.524 | Null |
| Subsample Oct-Dec | 0.000251 | 0.399 | Null |
| Out-of-sample 2026 | 0.000239 | 0.004 | Significant — interpret carefully |
| Lagged regime conditioning | -0.000089 | 0.677 | Null |
| Midday subsample | 0.000549 | 0.162 | Null (directionally consistent) |
| Quintile interaction | — | — | No quintile survives Bonferroni |
| Transition dynamics (sustained) | 0.000140 | 0.512 | Null |
| Transition dynamics (transition) | 0.000275 | 0.018 | Marginal — interpret carefully |
| Unconditional TFI (all specs) | ~0.0006 | < 0.001 | Consistently significant |

---

## 13. Research Design Decisions and Limitations

**Regime detector orthogonality:** With trades-only data, a fully
orthogonal regime detector is impossible — any detector derived from
aggressor-side volume shares informational content with TFI.
Lambda + TAR is the least circular available detector given this
constraint, chosen deliberately over more accurate alternatives
(per Ahern, 2018) to maximize research design cleanliness. The
remaining circularity is acknowledged in all contemporaneous
results.

**Exclusion windows:** Post-announcement only (+30 min after FOMC,
CPI, NFP). Pre-announcement windows are retained as potentially
informed. Unscheduled market stress events (flash crashes, circuit
breakers) are not excluded — this is acknowledged as a limitation
since such events contaminate lambda estimates with non-informed
price impact.

**Roll removal:** Roll spread was removed from the regime detector
because it is non-orthogonal to lambda (both spike at the same
directional price episodes), fails precisely in one-sided informed
markets (the condition of interest), and is redundant with TAR for
ruling out thin markets as a source of high lambda.

**Contemporaneous finding sensitivity:** The collapse of the
contemporaneous β₃ from 0.0015 (initial run, confounded spec) to
0.000425 (lagged regime, not significant) under the cleaner
specification is the most important methodological finding of
Phase 4. It demonstrates that the apparent contemporaneous
amplification in the initial run was substantially driven by
circularity. The cleaner specification produces a result that is
neither significant nor large enough to support a quantitative
market maker calibration.

**Future research:** A truly orthogonal test would require a
regime detector derived from limit order book data (bid-ask
dynamics, cancellation rates, depth changes) that shares no
informational content with TFI. Sub-minute TFI testing with an
LOB-based orthogonal detector is the natural extension.
