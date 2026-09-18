# Specification — Candidate Thematic Unit (CTU) Schema V1

## 1. Executive Summary

Candidate Thematic Unit (CTU) Schema V1 defines an unsupervised, operational computational object for discovering and validating symbolic thematic recurrence in polyphonic piano scores.

CTUs are **NOT** human-adjudicated themes, musicological ground truths, or primary/secondary theme labels. CTU candidate generation, recurrence scoring, non-maximum suppression (NMS) deduplication, and held-out future-reuse validation operate in a strictly role-blind, annotation-free manner.

---

## 2. Core Domain Models & Schema Invariants

* **`CTU_SCHEMA_VERSION = 1`**
* **`SegmentPosition`**: Zero-based measure index and exact rational offset (`Fraction`).
* **`SegmentSpan`**: Exact score interval defined by start and end `SegmentPosition`.
* **`SegmentRepresentation`**: Multi-channel symbolic feature tuple maintaining separate evidence streams:
  1. **Melodic / Interval Channel**: `(staff, voice)` stream single-note step intervals (adjacent single-note onsets only; no interval bridging across chords).
  2. **Rhythm Channel**: Inter-onset interval (IOI) ratios $r_i = \text{IOI}_{i+1} / \text{IOI}_i$.
  3. **Texture Channel**: Note attack count per onset simultaneity sequence.
  4. **Pitch Class Channel**: 12-bin pitch-class attack distribution histogram.
* **`CTUCandidate`**: Binds `piece_id`, `corpus_id`, `canonical_piece_hash`, `span`, `representation`, `discovery_score`, `tier`, `ctu_schema_version`, `representation_hash`, `discovery_policy_hash`, and `manifest_hash`.
* **`MatchedControlPair`**: Binds `target_candidate_id`, `target_ctu`, `control_candidate` (or `None` if `CONTROL_UNAVAILABLE`), and `validation_policy_hash`.

---

## 3. Sparse-Sequence Similarity Semantics

Sequence similarity across melodic, rhythmic, and texture channels evaluates ordered 2-gram multiset Jaccard with single-element 1-gram fallback under the following exact rules:
- **Both sequences empty**: Channel unavailable (`None`); composite score renormalized across available weights.
- **One sequence empty, one non-empty**: Similarity = `0.0`.
- **Both sequence lengths $\ge 2$**: Ordered 2-gram multiset Jaccard similarity.
- **Both sequence lengths $= 1$**: Ordered 1-gram multiset Jaccard fallback similarity.
- **Length mismatch (one length $= 1$, other $\ge 2$)**: Similarity = `0.0`.

---

## 4. Temporal Anti-Leakage & Held-Out Design

1. **Temporal Split**: Each score is split at an exact measure boundary:
   * **Discovery Region**: First 60% of complete measures (`[0, discovery_measures)`).
   * **Future Validation Region**: Last 40% of complete measures (`[discovery_measures, total_measures)`).
2. **Eligibility Boundary**: Scores with total measures `< 12` are classified as ineligible and excluded from future-reuse statistical inference.
3. **Anti-Leakage Guarantee**: No candidate window starting or ending at or past `discovery_measures` may be generated or evaluated during discovery. Future-region information is strictly forbidden from influencing candidate ranking, representations, or hyperparameter selection.

---

## 5. Evidence Tiers

| Evidence Tier | Code Name | Description |
| :--- | :--- | :--- |
| **Tier 0** | `E0_CANDIDATE_ONLY` | Raw multi-scale candidate window prior to recurrence scoring. |
| **Tier 1** | `E1_DISCOVERY_RECURRENCE` | Candidate showing discovery recurrence score $S_{\text{disc}} \ge 0.30$. |

*(Note: Tiers E2 and E3 are not implemented in Schema V1 and are omitted.)*

---

## 6. Statistical Inference & Fail-Closed Pairing

Held-out validation matches each retained CTU to an activity-matched control segment using `CTUValidationPolicy`. If no valid control exists (`CONTROL_UNAVAILABLE`), that exact pair is excluded from validation.

Piece-level paired difference:

$$\Delta_{\text{piece}} = \text{Mean CTU Future Reuse (matched pairs)} - \text{Mean Control Future Reuse (same matched pairs)}$$

Corpus-level evaluation applies:
* Two-sided paired sign-flip permutation test (10,000 iterations) with Monte Carlo correction $p = \frac{\text{extreme\_count} + 1}{\text{iterations} + 1}$.
* Bootstrap 95% confidence interval for mean difference (10,000 resamples).
* Cohen's $d_z$ effect size with sample SD ($n-1$).

Empirical Outcome Status evaluates to:
* `EMPIRICAL CTU STATUS = CTU_VALIDATED`
* `EMPIRICAL CTU STATUS = CTU_NOT_VALIDATED`
* `EMPIRICAL CTU STATUS = CTU_INCONCLUSIVE`
