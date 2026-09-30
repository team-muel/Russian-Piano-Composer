# PF-001C1.1: Autonomous Listener Metric Definitions & Prospective Calibration-Procedure Freeze

## 1. Executive Summary & Authoritative Status

Milestone **PF-001C1.1** establishes semantic consistency and locks all operational constructs for the Autonomous Artificial Listener evaluation framework. Following the physical corpus feasibility and canonical parser verification of **PF-001B.2**, this milestone freezes:

1. **Exact Mathematical Metric Formulations**: Unambiguous definitions of predictive, invariant, discriminatory, counterfactual, memory, and anti-copy metrics.
2. **ClosureContrast Semantics**: Defined strictly as $C_c - C_t > 0$ (cadential disruption lowers closure more than the matched neutral perturbation).
3. **Single Anti-Copy Smoothing Estimator**: Frozen strictly to `ADD_ALPHA` ($\alpha = 0.1$) on the development corpus only.
4. **Single Bootstrap Uncertainty Procedure**: Frozen strictly to `PERCENTILE` confidence intervals ($B = 2000$ replicates, $\alpha = 0.05$, $[0.025, 0.975]$ quantiles) clustered at `piece_id`.
5. **Separation of Source-Segment Memory and Thematic Memory**: PF-002A evaluates `SOURCE_SEGMENT_STRUCTURAL_MEMORY` ($m_A(t) = \text{sim}(z(A), h_t)$ across literal and $T_{\text{ID}}$ recurrences) and `CF-SOURCE-SEGMENT-MEMORY`. `THEMATIC_MEMORY_GATE` is isolated as `THEME_IDENTITY_DEPENDENT_NOT_READY`.
6. **Listener-Only Composer Generalization**: Defined strictly as performance degradation of the frozen Listener on composer-disjoint human repertoire without involving generated repertoire.
7. **Two Admissible Theme-Identity Routes**: Route A (independently adjudicated annotations) and Route B (lineage-valid explicit recurrence metadata).
8. **Removal of Stale Numerical Authority Language**: Active gate descriptions use symbolic names ($\tau_{\text{identity}}, \tau_{\text{copy}}, \tau_{\text{generalization}}$); numerical estimates are confined to a historical appendix.

---

## 2. Invariant Scientific Lineage & Immutability

This contract strictly adheres to the upstream invariants:

- **RC-012 Confirmatory Baseline**: All historical result files (`rc012_one_shot_confirmatory_result.json`, `rc012_one_shot_bootstrap_replicates.json`, `rc012_one_shot_execution_receipt.json`) remain byte-for-byte immutable.
- **Physical Corpus Feasibility (PF-001B.2)**: The 62-piece physical inventory (`pf001_physical_corpus_inventory.json`) and the remote materialization receipt (`pf001b_remote_materialization_receipt.json`) with hash `db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d` are fully preserved.
- **Contract Hash History**: The initial PF-001C1 contract hash `243244eabd0e8c8e30690250f77ca7c1a44a6cc353bcc318544dbc0e503c2881` is formally recorded as `SUPERSEDED_BY_SEMANTIC_CLOSURE`.
- **External Test Firewall**: The external test cohort (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remains strictly blinded and firewalled.

---

## 3. Evaluation Units & Statistical Clustering

### 3.1 Primary Unit of Statistical Independence: `piece_id`
A fundamental principle of the measurement contract is that segment counts are not independent:
$$\text{Cluster Unit} \equiv \text{piece\_id}$$
Every measure, segment, transformed variant, and counterfactual pair originating from a score inherits that score's `piece_id`. In all cross-validation fold splitting and bootstrap resampling, entire pieces are sampled or assigned. Segment counts must **never** be treated as independent degrees of freedom.

### 3.2 Evaluation Windows
- **`segment_4m`**: Contiguous 4-measure window aligned to score barlines (primary unit for invariance, hard-negative discrimination, and baseline n-gram evaluation).
- **`segment_8m`**: Contiguous 8-measure window aligned to score barlines (primary unit for phrase closure, surprise contrasts, and formal boundaries).
- **`section_window`**: Formal structural section (Exposition, Recapitulation, Variation) used for long-range source-segment structural memory reactivation.

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

1. **Closure Contrast (`CF-CLOSURE`)**:
   Let $C_0 = \text{Closure}(X)$, $C_t = \text{Closure}(T_{\text{target\_disruption}}(X))$, and $C_c = \text{Closure}(T_{\text{matched\_control}}(X))$.
   $$\text{ClosureContrast}(X) = (C_0 - C_t) - (C_0 - C_c) = C_c - C_t$$
   *Directional Hypothesis*: $\text{ClosureContrast} > 0$ (cadential disruption lowers structural closure more than the matched neutral perturbation). Mean $\text{ClosureContrast} > 0$ with percentile bootstrap 95% CI lower bound $> 0$.

2. **Surprise Contrast (`CF-SURPRISE`)**:
   $$\text{SurpriseContrast}(X) = (\text{Surprise}(T_{\text{target}}(X)) - \text{Surprise}(X)) - (\text{Surprise}(T_{\text{control}}(X)) - \text{Surprise}(X)) = \text{Surprise}(T_{\text{target}}(X)) - \text{Surprise}(T_{\text{control}}(X))$$
   *Directional Hypothesis*: $\text{SurpriseContrast} > 0$ (chromatic foreign corruption increases surprise relative to matched in-key control).

3. **Source-Segment Structural Memory Contrast (`CF-SOURCE-SEGMENT-MEMORY`)**:
   $$\text{MemoryContrast}(X) = \text{Memory}(T_{\text{control}}(X)) - \text{Memory}(T_{\text{target}}(X))$$
   *Directional Hypothesis*: $\text{MemoryContrast} > 0$ (corruption of the source-segment recurrence cue reduces memory retrieval more than matched control perturbation outside the cue).

### 4.4 Source-Segment Structural Memory Evaluation
For source segment $A$, evaluate state dynamics:
$$m_A(t) = \text{sim}(z(A), h_t)$$
Evaluated across:
1. Literal source-segment recurrence: $A \to \text{intervening context} \to A$.
2. Transformed source-segment recurrence: $A \to \text{intervening context} \to T_{\text{ID}}(A)$.
3. Matched unrelated-segment negative foil.

### 4.5 Anti-Copy Multi-Tier Evaluation
1. **Tier 1 (Symbolic Contiguous Overlap)**:
   $$L_{\max} = \max \{ |g| : g \in \text{Ngrams}(G) \cap \text{Ngrams}(\mathcal{D}_{\text{dev}}) \}$$
2. **Tier 2 (Information-Weighted Melodic Interval N-Gram)**:
   $$W(G) = \sum_{g \in \text{Ngrams}_k(G) \cap \text{Ngrams}_k(\mathcal{D}_{\text{dev}})} w(g), \quad \text{where } w(g) = -\log_2 P_{\text{dev}}(g)$$
   *Single Estimator*: `ADD_ALPHA` with $\alpha = 0.1$ estimated strictly on development corpus:
   $$P_{\text{dev}}(g) = \frac{\text{count}(g) + 0.1}{N_{\text{dev}} + 0.1 \cdot |V|^k}$$
3. **Tier 3 (Latent Space Nearest-Neighbor Cosine Distance)**:
   $$D_{\min}(G, \mathcal{D}_{\text{dev}}) = \min_{S \in \mathcal{D}_{\text{dev}}} (1 - \text{cos\_sim}(h(G), h(S)))$$

---

## 5. Non-Neural Baseline Models

The Artificial Listener's predictive performance must be benchmarked against standard non-neural references:
1. **`BASE_EMPIRICAL_MARGINAL`**: Unigram pitch-class and duration marginal distributions.
2. **`BASE_MARKOV_ORDER_1`**: First-order Markov chain over (pitch-class $\times$ duration) state space.
3. **`BASE_NGRAM_4`**: Kneser-Ney smoothed 4-gram symbolic event language model.

---

## 6. Uncertainty Procedure: Single Bootstrap Method

- **Replicates**: $B = 2000$.
- **Cluster Unit**: `piece_id`.
- **Sampling Strategy**: Resample whole piece clusters with replacement.
- **Confidence Interval Method**: `PERCENTILE` bootstrap strictly.
- **Nominal Level**: $\alpha = 0.05$ (95% CI; empirical quantiles at 0.025 and 0.975).
- **RNG Binding**: Hierarchically bound to `RandomContext` stream `pf001c1/resampling` with root seed `20260930`.

---

## 7. Prospective Threshold Selection (Grouped K-Fold Youden's $J$)

Numerical operational thresholds (e.g. $\tau_{\text{identity}}$) will be calibrated empirically in **PF-002A** using the following frozen deterministic procedure:

1. **Partition**: Group the development pieces into $K=5$ folds, grouped strictly by `piece_id`.
2. **Fold ROC Evaluation**: In each fold $k \in \{1, \dots, 5\}$, evaluate the empirical True Positive Rate ($\text{TPR}_k(\tau)$) on positive transformation pairs and False Positive Rate ($\text{FPR}_k(\tau)$) on matched negative foils across a grid $\tau \in [-1.0, 1.0]$ with step $0.005$.
3. **Youden's $J$ Optimization**:
   $$J_k(\tau) = \text{TPR}_k(\tau) - \text{FPR}_k(\tau)$$
   $$\tau_k^* = \arg\max_\tau J_k(\tau)$$
   *Tie-breaking rule*: If multiple values of $\tau$ achieve maximal $J$, select the higher $\tau$ (favoring specificity).
4. **Aggregate Threshold**:
   $$\tau^* = \text{median}(\tau_1^*, \dots, \tau_5^*)$$
5. **Uncertainty Bounds**: 95% percentile confidence intervals are computed using 2,000 piece-clustered bootstrap resamples.

---

## 8. Gate Readiness Ledger Summary

| Scientific Gate | Milestone Status | Symbolic Threshold | Operational Scope |
| :--- | :--- | :--- | :--- |
| **PREDICTIVE_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{perplexity}}$ | Perplexity vs empirical & Markov baselines |
| **INVARIANCE_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{identity}}$ | Cosine similarity under $T_{\text{ID}}$ transforms |
| **DISCRIMINATION_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{discrimination}}$ | AUROC & cosine margin vs matched foils |
| **COUNTERFACTUAL_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{counterfactual}}$ | Directional contrast ($ClosureContrast, SurpriseContrast > 0$) |
| **SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{memory}}$ | Source-segment recurrence & $MemoryContrast > 0$ |
| **ANTI_COPY_GATE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{copy}}$ | 3-tier: contiguous n-gram, info weight (`ADD_ALPHA`), latent NN |
| **COMPOSER_GENERALIZATION_GATE** | `NOT_READY_FOR_CALIBRATION` | $\tau_{\text{generalization}}$ | Listener degradation on disjoint human repertoire |
| **SOURCE_SEGMENT_INVARIANCE** | `PROVISIONAL_UNCALIBRATED_TARGET` | $\tau_{\text{identity}}$ | Calibrated via Youden's $J$ on $T_{\text{ID}}$ transforms |
| **THEME_MOTIF_IDENTITY** | `THEME_MOTIF_IDENTITY_NOT_READY` | $\tau_{\text{thematic\_identity}}$ | Awaiting Route A or Route B evidence |
| **THEMATIC_MEMORY_GATE** | `THEME_IDENTITY_DEPENDENT_NOT_READY` | $\tau_{\text{thematic\_memory}}$ | Awaiting operational thematic identity |

---

## 9. Conclusion & Handoff Token

Milestone **PF-001C1.1** is semantically closed. The metrics, registries, single estimators, single uncertainty procedures, and validation suites are completely unambiguous.

**Readiness Token**:
`PF001C1_SEMANTIC_CONTRACT_CLOSED_READY_FOR_PF002A`
