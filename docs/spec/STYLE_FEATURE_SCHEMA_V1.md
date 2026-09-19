# Specification — CTU Style Feature Schema V1 & Predictor Sets

## 1. Executive Summary

`CTU_STYLE_FEATURE_SCHEMA_VERSION = 1` defines a normalized, 14-feature structural representation derived from Candidate Thematic Units (CTUs) discovered under frozen RC-009B semantics.

CTU-style features evaluate normalized structural attributes of retained CTUs within the 60% discovery region of canonical scores. CTU feature extraction operates in a strictly role-blind manner without access to composer identity, title, repository paths, or style annotations.

---

## 2. CTU-Style Feature Registry (14 Features)

| Feature ID | Formula | Observation Unit | Normalization | Missing Value Rule | Provenance | Known Confounds | Semantic Version |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ctu_discovery_score_mean` | $\text{mean}(S_{\text{disc}})$ | `ctu_candidate` | `retained_ctu_count` | `0.0` if no retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_discovery_score_std` | $\text{std}(S_{\text{disc}})$ | `ctu_candidate` | `retained_ctu_count` | `0.0` if $<2$ retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_discovery_score_max` | $\max(S_{\text{disc}})$ | `ctu_candidate` | `none` | `0.0` if no retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_span_length_mean` | $\text{mean}(L_{\text{measures}})$ | `ctu_candidate` | `retained_ctu_count` | `0.0` if no retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_span_length_std` | $\text{std}(L_{\text{measures}})$ | `ctu_candidate` | `retained_ctu_count` | `0.0` if $<2$ retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_melodic_abs_interval_mean` | $\text{mean}(|\Delta p|)$ | `melodic_interval` | `total_melodic_intervals` | `0.0` if no melodic intervals | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_melodic_interval_diversity` | $\frac{\text{count}(\text{distinct}(\Delta p))}{\text{total}(\Delta p)}$ | `melodic_interval` | `total_melodic_intervals` | `0.0` if no melodic intervals | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_rhythm_ratio_abs_deviation_mean` | $\text{mean}(|r_i - 1.0|)$ | `ioi_rhythmic_ratio` | `total_rhythmic_ratios` | `0.0` if no rhythmic ratios | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_texture_attack_mean` | $\text{mean}(a(t))$ | `onset_simultaneity` | `total_onsets` | `0.0` if no texture profile | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_texture_attack_std` | $\text{std}(a(t))$ | `onset_simultaneity` | `total_onsets` | `0.0` if $<2$ texture onsets | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_pitchclass_entropy` | $-\sum p_i \log_2(p_i)$ | `sounding_pitchclass` | `total_attacks` | `0.0` if no pitch-class attacks | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_pitchclass_max_share` | $\max(p_i)$ | `sounding_pitchclass` | `total_attacks` | `0.0` if no pitch-class attacks | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_active_voice_stream_mean` | $\text{mean}(N_{\text{active\_streams}})$ | `ctu_candidate` | `retained_ctu_count` | `0.0` if no retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |
| `ctu_attack_density_per_measure_mean` | $\text{mean}(\frac{N_{\text{attacks}}}{L_{\text{measures}}})$ | `ctu_candidate` | `measure_span_count` | `0.0` if no retained CTUs | ENGINEERING_HEURISTIC | retained CTU count | v1.0 |

---

## 3. Predictor Model Sets & Frozen Schema Hashes

Predeclared predictor sets evaluated in RC-010:

1. **`MODEL_A`**: 32 Category-A `ANALYSIS_READY` piece-level features from RC-009A Feature Schema V2.
   - Schema Hash: `a825ea8f33a88fa6588e1bb4e6c9644c9c12c79824c6e9eca8eb7e162b531550`
2. **`MODEL_B`**: 14 CTU Style features (`CTU_STYLE_FEATURE_SCHEMA_V1`).
   - Schema Hash: `3806cd743b1c97230c015c25136849f8694235814ed0083935ed78f9fe92dca4`
3. **`MODEL_C`**: `MODEL_A` + `MODEL_B` combined (46 features total). **`MODEL_C` is the PRIMARY scientific model.**
   - Composite Schema Hash: `2e95c77615bf402a1245f8fd014da72c73839a5fac4dd299d2014f3e68a33b80`

---

## 4. Integrity Invariants & Metadata Exclusion

- **Zero Metadata Leakage**: Predictor matrices contain strictly zero composer, title, repository path, opus, or rights columns.
- **Strict Role-Blind Sequence**: Canonical scores $\to$ Role-blind features $\to$ Feature matrix freeze & SHA-256 hashing $\to$ Label attachment $\to$ Evaluation.
- **Strict Fail-Closed Policy**: Any `None`, `NaN`, `Inf` in Category-A or CTU features raises an immediate error. Missing values in canonical 141-piece dataset = `0`.
