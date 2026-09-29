# PF-001C1: Autonomous Listener Metric Definitions & Prospective Calibration-Procedure Freeze

## 1. Executive Summary & Authoritative Status

Milestone **PF-001C1** establishes the scientific and mathematical foundations for the Autonomous Artificial Listener evaluation framework. Following the completion and verification of the 62-piece physical corpus and canonical parser verification in **PF-001B.2**, this milestone freezes:

1. **Exact Mathematical Metric Formulations**: Unambiguous definitions of predictive, invariant, discriminatory, counterfactual, memory, and anti-copy metrics.
2. **Evaluation Units & Strict Independence**: Enforcement of the musical piece (`piece_id`) as the non-negotiable primary cluster unit.
3. **Identity-Preserving Transformation Registry**: 7 rigorously defined transformations ($T_{\text{ID}}$) preserving musicological invariants.
4. **Counterfactual Perturbation & Control Registry**: 3 perturbation families paired with matched neutral controls and directional contrast statistics ($ClosureContrast, MemoryContrast, SurpriseContrast$).
5. **Theme vs. Segment Identity Audit**: Strict certification of `THEME_MOTIF_IDENTITY_NOT_READY` and restriction of operational scope to `SOURCE_SEGMENT_IDENTITY_ONLY`.
6. **Prospective Calibration Algorithm**: Grouped $K$-fold cross-validation optimizing Youden's $J$ statistic for empirical threshold discovery in PF-002A.
7. **Provisional Numerical Threshold Freeze**: All 10 numerical gate thresholds remain designated `PROVISIONAL_UNCALIBRATED_TARGET` or `NOT_READY_FOR_CALIBRATION`. No numerical values are prematurely fixed.

---

## 2. Invariant Scientific Lineage & Immutability

This contract strictly adheres to the upstream invariants:

- **RC-012 Confirmatory Baseline**: All historical result files (`rc012_one_shot_confirmatory_result.json`, `rc012_one_shot_bootstrap_replicates.json`, `rc012_one_shot_execution_receipt.json`) remain byte-for-byte immutable.
- **Physical Corpus Feasibility (PF-001B.2)**: The 62-piece physical inventory (`pf001_physical_corpus_inventory.json`) and the remote materialization receipt (`pf001b_remote_materialization_receipt.json`) with hash `db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d` are fully preserved.
- **External Test Firewall**: The external test cohort (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remains strictly blinded and firewalled.

---

## 3. Evaluation Units & Statistical Clustering

### 3.1 Primary Unit of Statistical Independence: `piece_id`
A fundamental error in music representation learning is treating slices, measures, or segments as independent observations. In this protocol:
$$\text{Cluster Unit} \equiv \text{piece\_id}$$
Every measure, segment, transformed variant, and counterfactual pair originating from a score inherits that score's `piece_id`. In all cross-validation fold splitting and bootstrap resampling, entire pieces are sampled or assigned. Segment counts must **never** be treated as independent degrees of freedom.

### 3.2 Evaluation Windows
- **`segment_4m`**: Contiguous 4-measure window aligned to score barlines (primary unit for invariance and discrimination).
- **`segment_8m`**: Contiguous 8-measure window aligned to score barlines (primary unit for phrase closure and surprise contrasts).
- **`section_window`**: Formal structural section (Exposition, Recapitulation, Variation) used for long-range memory reactivation.

---

## 4. Metric Definitions & Formulas

### 4.1 Predictive Metric: Cross-Entropy & Perplexity
For a held-out symbolic piece sequence $W = (w_1, w_2, \dots, w_N)$:
$$\text{PPL}(W) = \exp\left(-\frac{1}{N} \sum_{i=1}^N \ln P(w_i \mid w_{<i})\right)$$
$$\text{Bitrate } H(W) = \log_2(\text{PPL}(W)) = -\frac{1}{N} \sum_{i=1}^N \log_2 P(w_i \mid w_{<i}) \quad (\text{bits/token})$$

### 4.2 Representation Similarity: Cosine Similarity
For normalized latent representation vectors $u, v \in \mathbb{R}^d$:
$$\text{cos\_sim}(u, v) = \frac{\langle u, v \rangle}{\|u\|_2 \|v\|_2}$$

### 4.3 Counterfactual Contrast Statistics
Each counterfactual test evaluates the differential listener response between a targeted construct perturbation $P_{\text{target}}$ and a matched neutral control perturbation $P_{\text{ctl}}$:

1. **Closure Contrast**:
   $$\text{ClosureContrast}(S, P_{\text{cad}}, P_{\text{ctl}}) = \text{ListenerClosureScore}(S \circ P_{\text{cad}}) - \text{ListenerClosureScore}(S \circ P_{\text{ctl}})$$
   *Hypothesis*: $\text{ClosureContrast} > 0$ with 95% bootstrap CI lower bound $> 0$.

2. **Surprise Contrast**:
   $$\text{SurpriseContrast}(S, P_{\text{dis}}, P_{\text{ctl}}) = \text{ListenerSurpriseScore}(S \circ P_{\text{dis}}) - \text{ListenerSurpriseScore}(S \circ P_{\text{ctl}})$$
   *Hypothesis*: $\text{SurpriseContrast} > 0$ with 95% bootstrap CI lower bound $> 0$.

3. **Long-Range Memory Reactivation Ratio**:
   $$\text{ReactivationRatio}(S_{\text{reprise}}, S_{\text{novel}}, S_{\text{theme}}) = \frac{\text{cos\_sim}(h(S_{\text{reprise}}), h(S_{\text{theme}}))}{\text{cos\_sim}(h(S_{\text{novel}}), h(S_{\text{theme}}))}$$
   *Hypothesis*: $\text{ReactivationRatio} > 1.0$.

### 4.4 Anti-Copy Multi-Tier Evaluation
Preventing verbatim or near-verbatim memorization of the training corpus requires three orthogonal tiers:
1. **Tier 1 (Symbolic Contiguous Overlap)**:
   $$L_{\max} = \max \{ |g| : g \in \text{Ngrams}(G) \cap \text{Ngrams}(\mathcal{D}_{\text{train}}) \}$$
2. **Tier 2 (Information-Weighted Melodic Interval N-Gram)**:
   $$W(G) = \sum_{g \in \text{Ngrams}_k(G) \cap \text{Ngrams}_k(\mathcal{D})} w(g), \quad \text{where } w(g) = -\log_2 P_{\mathcal{D}}(g)$$
   Smoothed via add-$\alpha$ or Good-Turing strictly on the development corpus.
3. **Tier 3 (Latent Space Nearest-Neighbor Cosine Distance)**:
   $$D_{\min}(G, \mathcal{D}) = \min_{S \in \mathcal{D}} (1 - \text{cos\_sim}(h(G), h(S)))$$

---

## 5. Non-Neural Baseline Models

The Artificial Listener's predictive performance must be benchmarked against standard non-neural references:
1. **`BASE_EMPIRICAL_MARGINAL`**: Unigram pitch-class and duration marginal distributions.
2. **`BASE_MARKOV_ORDER_1`**: First-order Markov chain over (pitch-class $\times$ duration) state space.
3. **`BASE_NGRAM_4`**: Kneser-Ney smoothed 4-gram symbolic event language model.

---

## 6. Hard-Negative Foil Construction

To prevent representation collapse, positive pairs ($S, T_{\text{ID}}(S)$) are contrasted against carefully matched hard negative foils:
1. **`WITHIN_PIECE_DISTANT`**: Segment from the same piece separated by $\ge 16$ measures, matching tempo, meter, and key.
2. **`CROSS_PIECE_SAME_COMPOSER`**: Segment from a different piece by the same composer with matching meter and primary key.
3. **`CROSS_COMPOSER_MATCHED_GENRE`**: Segment from another development composer matched by genre (e.g. Prelude) and event density.

Matching tolerances:
- Measure duration difference: 0 measures.
- Event density tolerance: $\pm 15\%$.
- Pitch register mean MIDI tolerance: $\pm 6.0$ semitones.

---

## 7. Closure Label Provenance Hierarchy

Ground truth boundaries for closure calibration are stratified into 4 strict provenance levels:
1. **`EXPLICIT_SCORE_BOUNDARY`**: Double barlines, fine barlines, final score barlines, repeat signs.
2. **`CADENCE_RULE_DERIVED`**: Rule-based harmonic cadences (PAC, IAC, HC) validated against Roman numeral annotations.
3. **`FORMAL_METADATA_DERIVED`**: Movement and variation boundary markers from catalog metadata.
4. **`HEURISTIC_WEAK_LABEL`**: Algorithmic root-position tonic arrivals preceded by dominant chords with rests/fermatas.

---

## 8. Prospective Calibration Algorithm (Grouped K-Fold Youden's $J$)

Numerical operational thresholds (e.g. $\tau_{\text{inv}}, \tau_{\text{foil}}$) will be calibrated empirically in **PF-002A** using the following frozen deterministic procedure:

1. **Partition**: Group the development pieces into $K=5$ folds, grouped strictly by `piece_id`.
2. **Fold ROC Evaluation**: In each fold $k \in \{1, \dots, 5\}$, evaluate the empirical True Positive Rate ($\text{TPR}_k(\tau)$) on positive transformation pairs and False Positive Rate ($\text{FPR}_k(\tau)$) on matched negative foils across a grid $\tau \in [-1.0, 1.0]$ with step $0.005$.
3. **Youden's $J$ Optimization**:
   $$J_k(\tau) = \text{TPR}_k(\tau) - \text{FPR}_k(\tau)$$
   $$\tau_k^* = \arg\max_\tau J_k(\tau)$$
   *Tie-breaking rule*: If multiple values of $\tau$ achieve maximal $J$, select the higher $\tau$ (favoring specificity over sensitivity).
4. **Aggregate Threshold**:
   $$\tau^* = \text{median}(\tau_1^*, \dots, \tau_5^*)$$
5. **Uncertainty Bounds**: 95% confidence intervals are computed using 2,000 piece-clustered bootstrap resamples.

---

## 9. Gate Readiness Ledger Summary

| Scientific Gate | Milestone Status | Operational Scope |
| :--- | :--- | :--- |
| **PREDICTIVE_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | Perplexity vs empirical & Markov baselines |
| **INVARIANCE_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | Cosine similarity under $T_{\text{ID}}$ transforms |
| **DISCRIMINATION_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | AUROC & cosine margin vs matched foils |
| **COUNTERFACTUAL_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | Directional contrast ($ClosureContrast, SurpriseContrast > 0$) |
| **LONG_RANGE_MEMORY_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | Reactivation ratio & section memory divergence |
| **ANTI_COPY_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | 3-tier: max contiguous n-gram, info weight, latent NN |
| **COMPOSER_GENERALIZATION_GATE** | `NOT_READY_FOR_CALIBRATION` | Blocked pending Stage-1 Composer generation |
| **SOURCE_SEGMENT_INVARIANCE** | `PROVISIONAL_UNCALIBRATED_TARGET` | Calibrated via Youden's $J$ on $T_{\text{ID}}$ transforms |
| **THEME_MOTIF_IDENTITY** | `THEME_MOTIF_IDENTITY_NOT_READY` | Restricted to `SOURCE_SEGMENT_IDENTITY_ONLY` |

---

## 10. Conclusion & Handoff Token

Milestone **PF-001C1** is fully satisfied. The metrics, registries, algorithms, and validation suites are deterministically frozen.

**Readiness Token**:
`PF001C1_METRIC_AND_CALIBRATION_PROCEDURE_FROZEN_READY_FOR_PF002A`
