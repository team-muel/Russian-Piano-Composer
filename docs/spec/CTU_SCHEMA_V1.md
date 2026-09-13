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
  1. **Melodic / Interval Channel**: `(staff, voice)` stream single-note step intervals.
  2. **Rhythm Channel**: Inter-onset interval (IOI) ratios relative to beat unit.
  3. **Texture Channel**: Note attack count per onset.
  4. **Pitch Class Channel**: 12-bin pitch-class attack distribution histogram.
* **`CTUCandidate`**: Binds `piece_id`, `corpus_id`, `canonical_piece_hash`, `span`, `representation`, `discovery_score`, `tier`, `ctu_schema_version`, `representation_hash`, `discovery_policy_hash`, and `manifest_hash`.

---

## 3. Temporal Anti-Leakage & Held-Out Design

1. **Temporal Split**: Each score is split at an exact measure boundary:
   * **Discovery Region**: First 60% of complete measures (`[0, discovery_measures)`).
   * **Future Validation Region**: Last 40% of complete measures (`[discovery_measures, total_measures)`).
2. **Eligibility Boundary**: Scores with total measures `< 12` are classified as `HELD_OUT_VALIDATION_INELIGIBLE` and excluded from future-reuse statistical inference.
3. **Anti-Leakage Guarantee**: No candidate window starting or ending at or past `discovery_measures` may be generated or evaluated during discovery. Future-region information is strictly forbidden from influencing candidate ranking, representations, or hyperparameter selection.

---

## 4. Evidence Tiers

| Evidence Tier | Code Name | Description |
| :--- | :--- | :--- |
| **Tier 0** | `E0_CANDIDATE_ONLY` | Raw multi-scale candidate window prior to recurrence scoring. |
| **Tier 1** | `E1_DISCOVERY_RECURRENCE` | Candidate showing positive non-overlapping recurrence in discovery region. |
| **Tier 2** | `E2_MULTICHANNEL_CONSENSUS` | Candidate exhibiting consensus across melodic, rhythmic, and texture streams. |
| **Tier 3** | `E3_HELDOUT_FUTURE_SUPPORTED` | Candidate demonstrating statistically superior future reuse in held-out region. |

---

## 5. Statistical Inference & Empirical Status

Held-out validation computes piece-level paired differences:

$$\Delta_{\text{piece}} = \text{Mean CTU Future Reuse} - \text{Mean Matched Control Future Reuse}$$

Corpus-level evaluation applies:
* Paired non-parametric permutation test (10,000 iterations).
* Bootstrap 95% confidence interval for mean difference.
* Cohen's d effect size.

Empirical Outcome Status must evaluate to one of:
* `EMPIRICAL CTU STATUS = CTU_VALIDATED`
* `EMPIRICAL CTU STATUS = CTU_NOT_VALIDATED`
* `EMPIRICAL CTU STATUS = CTU_INCONCLUSIVE`
