# PF-002A.0: Prospective Artificial Listener Model Family & Execution Protocol Freeze

## 1. Executive Summary & Authoritative Status

Milestone **PF-002A.0** establishes the prospective freeze of the Artificial Listener model candidate set, input representations, training objectives, stochastic seed hierarchy, training budget, checkpoint-selection rules, replicate aggregation rules, architecture-selection rules, threshold-calibration authority, validation ordering, and fail-closed behavior.

Following the closure of **PF-001C1** (metric definitions and prospective calibration procedure) and **PF-001C1.2** / **PF-001C1.3b** (exact dataset roles and autonomous Stage-0 policy synchronization), this protocol ensures that **no model fitting, representation extraction, or threshold calibration occurs before all execution rules are mathematically frozen**.

### Core Governance Principles
1. **Prospective Model Freeze**: Exactly two compact causal neural architectures (`AL-GRU-01` and `AL-TRF-01`) are admitted. No architectural exploration, parameter expansion, or ad-hoc redesign is permitted after inspecting validation outcomes.
2. **Single Neural Framework**: **PyTorch** (`torch>=2.2,<2.4`) is specified as the sole neural framework, operating in full CPU/GPU determinism (`use_deterministic_algorithms=True`).
3. **Training Cohort Boundary**: Model parameters, representations, and vocabulary statistics are fitted strictly on the 37 `DEVELOPMENT` pieces. `VALIDATION` (22 pieces) and `BENCHMARK_PILOT_ONLY` (3 pieces) are strictly excluded from gradient updates, representation learning, and vocabulary estimation.
4. **Gate-Specific Calibration Authority**: Operating threshold calibration is strictly differentiated by gate type:
   - `INVARIANCE_GATE` ($\tau_{\text{identity}}$) and `DISCRIMINATION_GATE` ($\tau_{\text{discrimination}}$) are prospectively calibrated on `DEVELOPMENT` cross-validation folds via Grouped K-Fold ($K=5$) Youden's $J$.
   - `PREDICTIVE_GATE` is governed by outperforming three non-neural baselines (`BASE_EMPIRICAL_MARGINAL`, `BASE_MARKOV_ORDER_1`, `BASE_NGRAM_4`) on held-out pieces with percentile bootstrap 95% CI upper bound. Its threshold ($\tau_{\text{perplexity}}$) is marked `NOT_INDEPENDENTLY_CALIBRATABLE` (no arbitrary Youden grid).
   - `COUNTERFACTUAL_GATE` and `SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE` are directional hypothesis tests whose operating criterion is strictly that the lower bound of the piece-clustered percentile bootstrap 95% confidence interval exceeds zero ($> 0$), with memory retrieval separation over matched negative foils.
   - `ANTI_COPY_GATE` is evaluated via a conjunctive three-tier rule: Tier 1 symbolic contiguous n-gram ($L_{\max} \le 12$), Tier 2 information-weighted interval n-gram using the `ADD_ALPHA` ($\alpha = 0.1$) estimator on the `DEVELOPMENT` corpus ($\le \tau_{\text{infocopy}}$), and Tier 3 nearest-neighbor latent cosine distance ($D_{\min} \ge 0.05$).
5. **Two-Level Checkpoint & Replicate Aggregation (Anti-Cherry-Picking)**:
   - *Level A (Epoch Checkpoint Selection within Replicate)*: For each replicate $r \in \{0, 1, 2\}$, select the single epoch checkpoint minimizing validation cross-entropy bits/token $H_{\text{val}}(W)$.
   - *Level B (Replicate Aggregation to Candidate Architecture Score)*: Aggregate replicates using the **median** validation score:
     $$H_{\text{cand}} = \text{median}(H_{\text{val}}(e_0^*), H_{\text{val}}(e_1^*), H_{\text{val}}(e_2^*))$$
     Cherry-picking the single best seed or lowest validation loss among replicates is strictly prohibited. All 3 replicates must individually pass all 6 active Stage-0 gates on `VALIDATION`. The physical checkpoint corresponding to the median replicate is selected as the canonical representation for downstream benchmark evaluation.
6. **Firewall & Exclusion Enforcement**: External test candidates (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled. Historical Scriabin remains excluded by lineage policy.
7. **Composer Generalization Invariant**: `COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION` remains frozen.
8. **Theme Identity Invariant**: `THEMATIC_MEMORY_GATE = THEME_IDENTITY_DEPENDENT_NOT_READY` remains frozen; PF-002A operational memory is governed by `SOURCE_SEGMENT_STRUCTURAL_MEMORY`.

**Milestone Status**: `PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET`  
**Authoritative Protocol Hash**: `691e3e1460377fd219c1e115e52b953b326ddec9afb99ad69034de8567fcd683`

---

## 2. Invariant Cryptographic & Scientific Lineage

This execution protocol binds directly to the frozen upstream lineage:

| Milestone Artifact | Authoritative Path | Cryptographic SHA-256 Hash |
| :--- | :--- | :--- |
| **PF-001B Physical Inventory** | `data/reviews/pf001/pf001_physical_corpus_inventory.json` | `3154c2967ee8201d5df65eb3f866fb81e495ac1878e8a60349687888018c9d8e` |
| **PF-001B Materialization Receipt** | `data/reviews/pf001/pf001b_remote_materialization_receipt.json` | `db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d` |
| **PF-001C1 Metric Contract** | `data/reviews/pf001/pf001c1_metric_calibration_contract.json` | `5b681c6b02ecb2c573b06d463705ab8b4fd17b9aec9b5c4e56f6a7e5830e214a` |
| **PF-001C1.2 Stage-0 Split Manifest** | `data/reviews/pf001/pf001c1_stage0_split_manifest.json` | `2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab` |

### Exact Dataset Roles (62 Pieces Total)
- **DEVELOPMENT (37 pieces)**: Pyotr Ilyich Tchaikovsky (12), Sergei Rachmaninoff (22), Anton Arensky (3).
- **VALIDATION (22 pieces)**: Nikolai Medtner (19), Anatoly Lyadov (3).
- **BENCHMARK_PILOT_ONLY (3 pieces)**: Sergei Lyapunov (3).

---

## 3. Input Representation & Tokenization Contract

### 3.1 Serialization from `CanonicalScore`
The Artificial Listener takes as input discrete token sequences generated strictly from `CanonicalScore` domain objects (`src/russian_piano_composer/domain/score.py`):
1. **Event Sequence Ordering**: Events are ordered chronologically by `global_onset ASC`. Polyphonic simultaneous onsets are ordered deterministically by `(staff ASC, voice ASC, pitch DESC)`.
2. **Event Tuples**: Each musical event is discretized into a compound token tuple:
   $$e_t = (\text{kind}_t, \text{pitch}_t, \text{duration}_t, \text{metric\_pos}_t, \text{bar\_flag}_t)$$
   - $\text{kind} \in \{\text{NOTE}, \text{REST}\}$
   - $\text{pitch} \in \{21, 22, \dots, 108\} \cup \{\text{REST\_PITCH}\}$ (88 piano keys + rest indicator).
   - $\text{duration}$: Quantized rational duration tokens derived from score notation.
   - $\text{metric\_pos}$: Rational offset within measure relative to active time signature.
   - $\text{bar\_flag}$: Explicit measure boundary token `⟨BAR⟩` separating measures.
   - Boundary tokens: `⟨BOS⟩` (beginning of sequence) and `⟨EOS⟩` (end of sequence).
3. **Context Window**: Maximum context length $L = 1024$ events. Sliding windows have length $L$ with 50% stride ($512$ events), strictly preserving measure boundaries.
4. **Vocabulary Upper Bound**: Maximum vocabulary size is bounded at $|V| \le 512$ compound tokens.
5. **Vocabulary Fitting**: The token vocabulary $V$ and all empirical frequency marginals are fitted strictly on `DEVELOPMENT`. Unseen tokens in `VALIDATION` map to `⟨UNK⟩`.
6. **Lineage Preservation**: Every token sequence retains source score metadata: `piece_id`, `work_id`, `composer_id`, `source_role`, and `canonical_materialized_sha256`.

---

## 4. Prospective Model Candidate Set & Parameter Accounting

To prevent post-hoc architecture selection and fishing, exactly **two** compact causal architectures are prospectively admitted with closed-form parameter budgets:

```
                    +------------------------------------+
                    |        Input Token Sequence        |
                    |   (Pitch, Duration, Metric Pos)    |
                    +-----------------+------------------+
                                      |
                     +----------------+---------------+
                     |                                |
                     v                                v
          +----------------------+        +----------------------+
          |     AL-GRU-01        |        |     AL-TRF-01        |
          |  2-Layer Causal GRU  |        |  3-Layer Causal TRF  |
          |   Hidden Dim = 96    |        |   Model Dim = 64     |
          | Max Budget: 200,000  |        | Max Budget: 250,000  |
          +----------+-----------+        +----------+-----------+
                     |                                |
                     v                                v
          +------------------------------------------------------+
          |             Shared Output Heads & Loss:              |
          |  1. Next-Token Cross-Entropy Head (λ = 1.0)          |
          |  2. Contrastive Invariance InfoNCE Head (λ = 0.5)    |
          +------------------------------------------------------+
```

### 4.1 Candidate 1: `AL-GRU-01` (Gated Recurrent Artificial Listener)
- **Architecture**: Compact causal unidirectional Gated Recurrent Unit (GRU).
- **Embedding Dimension**: $d_{\text{embed}} = 64$.
- **Recurrent Layers**: 2 stacked GRU layers, hidden dimension $d_{\text{hidden}} = 96$.
- **Dropout**: $0.1$ applied between recurrent layers.
- **Latent Projection**: Linear projection from $d_{\text{hidden}} = 96$ to $d_{\text{latent}} = 64$ followed by LayerNorm, yielding frame-level latent embedding $z_t \in \mathbb{R}^{64}$.
- **Analytical Parameter Formula**:
  $$P_{\text{core}} = P_{\text{gru1}} + P_{\text{gru2}} + P_{\text{proj}} + P_{\text{ln}} = 46,656 + 55,872 + 6,208 + 128 = 108,864$$
  $$P_{\text{vocab}}(|V|) = |V| \times d_{\text{embed}} + (d_{\text{hidden}} \times |V| + |V|) = 64|V| + 97|V| = 161|V|$$
  $$P_{\text{total}}(|V|) = 108,864 + 161|V|$$
- At nominal $|V| = 512$: $P_{\text{total}} = 108,864 + 82,432 = 191,296 \le 200,000$.
- **Parameter Upper Bound**: $\le 200,000$ trainable parameters.

### 4.2 Candidate 2: `AL-TRF-01` (Causal Transformer Artificial Listener)
- **Architecture**: Compact causal autoregressive Transformer decoder.
- **Embedding Dimension**: $d_{\text{model}} = 64$.
- **Decoder Layers**: 3 Pre-LayerNorm causal self-attention blocks.
- **Attention Heads**: 4 heads ($d_{\text{head}} = 16$).
- **Feed-Forward Dimension**: $d_{\text{ff}} = 128$, GELU activation.
- **Positional Encoding**: Strictly frozen to **`LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING`** (Learned Absolute Positional Embeddings) for max context $L = 1024$ ($1024 \times 64 = 65,536$ parameters).
- **Latent Representation**: The final-layer output vector at time $t$, $z_t \in \mathbb{R}^{64}$, normalized via LayerNorm.
- **Analytical Parameter Formula**:
  - Per decoder block: Attention ($4 \times (64 \times 64 + 64) = 16,640$) + FFN ($64 \times 128 + 128 + 128 \times 64 + 64 = 16,576$) + 2 Pre-LN ($2 \times 128 = 256$) $= 33,472$.
  - 3 blocks: $3 \times 33,472 = 100,416$.
  - Learned position embeddings: $1024 \times 64 = 65,536$.
  - Final LayerNorm: $2 \times 64 = 128$.
  - Latent projection head: $64 \times 64 + 64 = 4,160$.
  - Core total: $P_{\text{core}} = 100,416 + 65,536 + 128 + 4,160 = 170,240$.
  - Token embedding & LM head: $P_{\text{vocab}}(|V|) = 64|V| + (64|V| + |V|) = 129|V|$.
  $$P_{\text{total}}(|V|) = 170,240 + 129|V|$$
- At nominal $|V| = 512$: $P_{\text{total}} = 170,240 + 66,048 = 236,288 \le 250,000$.
- **Parameter Upper Bound**: $\le 250,000$ trainable parameters.

---

## 5. Training Objective, Sampling Policies & Multi-Task Balance

Training is performed on `DEVELOPMENT` using a joint predictive and representation learning objective:

$$\mathcal{L}_{\text{total}} = \lambda_{\text{pred}} \mathcal{L}_{\text{pred}} + \lambda_{\text{repr}} \mathcal{L}_{\text{repr}}$$

1. **Predictive Loss ($\mathcal{L}_{\text{pred}}$)**:
   - Next-event autoregressive cross-entropy over vocabulary $V$:
     $$\mathcal{L}_{\text{pred}} = -\frac{1}{N} \sum_{i=1}^N \ln P(w_i \mid w_{<i})$$
   - Weight: $\lambda_{\text{pred}} = 1.0$.

2. **Self-Supervised Representation Loss ($\mathcal{L}_{\text{repr}}$)**:
   - Contrastive InfoNCE loss enforcing invariance under identity transformations ($T_{\text{ID}}$):
     $$\mathcal{L}_{\text{repr}} = -\log \frac{\exp(\text{sim}(z(A), z(T_{\text{ID}}(A))) / \tau_{\text{temp}})}{\exp(\text{sim}(z(A), z(T_{\text{ID}}(A))) / \tau_{\text{temp}}) + \sum_{j=1}^5 \exp(\text{sim}(z(A), z(N_j)) / \tau_{\text{temp}})}$$
   - Temperature parameter: $\tau_{\text{temp}} = 0.07$.
   - Weight: $\lambda_{\text{repr}} = 0.5$.

### 5.1 Negative Sampling Policy
- **Foil Count**: Exactly 5 negative foils ($N_j$) per positive anchor.
- **Sampling Pool**: Strictly from `DEVELOPMENT`.
- **Foil Allocation**:
  - 3 within-piece distant segments (separated by $\ge 16$ measures, matched for tempo, key signature, and register).
  - 2 cross-piece segments from the same composer (matched meter and key center).
- **Sampling Method**: Sampled without replacement per anchor.
- **Matching Constraints**: Measure tolerance $= 0$, event density tolerance $\le 15\%$, pitch register mean MIDI tolerance $\le 6.0$.

### 5.2 Identity-Transform ($T_{\text{ID}}$) Sampling Policy
- **Transform Count**: Exactly 1 positive transform sampled per anchor during contrastive training.
- **Sampling Mixture**: Uniform probability distribution ($p = 1/7 \approx 0.142857$ each) across the 7 authoritative transforms in `pf001c1_transformation_registry.json`:
  1. `T_ID_PITCH_TRANSPOSITION` (semitones: $[-7, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 7]$)
  2. `T_ID_OCTAVE_DISPLACEMENT` (octave shifts: $[-2, -1, 1, 2]$, voices: all, top, bottom)
  3. `T_ID_RHYTHMIC_AUGMENTATION` (scaling: $[2, 3]$)
  4. `T_ID_RHYTHMIC_DIMINUTION` (scaling: $[2, 3]$)
  5. `T_ID_LIMITED_ORNAMENT_INSERTION` (mordent, turn, grace note; density $\le 0.1$)
  6. `T_ID_LIMITED_ORNAMENT_DELETION` (max deletion $\le 0.1$)
  7. `T_ID_ACCOMPANIMENT_TEXTURE_VARIATION` (arpeggiation expansion, block chord consolidation)

### 5.3 Intervention Non-Contamination Rule
Counterfactual perturbations (`CF-CLOSURE`, `CF-SURPRISE`), memory probe tasks, and anti-copy checks are **strictly evaluation probes**. They must **never** enter training loss or the gradient graph.

---

## 6. Stochastic Hierarchy, Optimization & Training Budget

### 6.1 Collision-Free RandomContext Namespace Hierarchy
All stochastic operations derive deterministically from `RandomContext` (`root_seed = 20260930`) via distinct hierarchical paths:
- Weight initialization: `pf002a/model/<arch_id>/<rep_id>/init`
- DataLoader batching and windowing: `pf002a/model/<arch_id>/<rep_id>/dataloader`
- $T_{\text{ID}}$ augmentation sampling: `pf002a/model/<arch_id>/<rep_id>/augmentation`
- Negative foil sampling: `pf002a/model/<arch_id>/<rep_id>/negative_sampling`
- Evaluation resampling: `pf002a/evaluation/resampling`
- Evaluation percentile bootstrap: `pf002a/evaluation/bootstrap` (Percentile bootstrap, $B = 2000$ replicates)

### 6.2 Optimization Hyperparameters & Budget
- **Optimizer**: AdamW ($\beta_1 = 0.9, \beta_2 = 0.98, \epsilon = 10^{-8}$, weight decay $= 0.01$).
- **Learning Rate**: Peak learning rate $\eta_{\max} = 5 \times 10^{-4}$.
- **Warmup & Schedule**: 5 epochs linear warmup followed by cosine annealing to $\eta_{\min} = 1 \times 10^{-5}$.
- **Batch Size**: 16 sequence windows (clustered by piece to avoid within-batch cross-piece leakage).
- **Gradient Clipping**: Maximum gradient norm $1.0$.
- **Fixed Epoch Budget**: Exactly 50 epochs per replicate. No early stopping is permitted.

---

## 7. Replicate Aggregation, Gate-Specific Calibration & Execution Ordering

### 7.1 Two-Level Checkpoint & Replicate Aggregation
1. **Level A (Epoch Checkpoint Selection within Replicate)**:
   For replicate $r \in \{0, 1, 2\}$, select the single epoch checkpoint minimizing validation cross-entropy bits/token $H_{\text{val}}(W)$:
   $$e_r^* = \arg\min_{e \in \{1, \dots, 50\}} H_{\text{val}}(W; \theta_{e, r})$$
2. **Level B (Replicate Aggregation to Candidate Architecture Score)**:
   Candidate evaluation is aggregated using **`MEDIAN_REPLICATE_VALIDATION_METRIC`** (the **median** of the 3 replicate checkpoints):
   $$H_{\text{cand}} = \text{median}(H_{\text{val}}(e_0^*), H_{\text{val}}(e_1^*), H_{\text{val}}(e_2^*))$$
   *Anti-Cherry-Picking Rule*: Cherry-picking the single best seed or lowest validation loss among replicates is strictly prohibited. All 3 replicates must individually pass all 6 active Stage-0 gates on `VALIDATION`. The physical checkpoint corresponding to the median validation score replicate is selected as the canonical representation for downstream benchmark evaluation.

### 7.2 Gate-Specific Calibration Authority
Calibration and decision rules are strictly differentiated across the 6 active gates:

| Active Gate | Primary Metric | Threshold Symbol | Prospective Calibration Method | Decision Rule on VALIDATION |
| :--- | :--- | :--- | :--- | :--- |
| **`PREDICTIVE_GATE`** | $H_{\text{val}}(W)$ (bits/token) | $\tau_{\text{perplexity}}$ | Non-neural baselines comparison (`NOT_INDEPENDENTLY_CALIBRATABLE`) | $H_{\text{val}}(W) < \min(H_{\text{marginal}}, H_{\text{Markov}}, H_{\text{ngram4}})$ with 95% bootstrap CI upper bound |
| **`INVARIANCE_GATE`** | $\text{cos\_sim}(z(A), z(T_{\text{ID}}(A)))$ | $\tau_{\text{identity}}$ | Grouped K-Fold ($K=5$) Youden's $J$ on `DEVELOPMENT` | $\text{median}(\text{sim}(z(A), z(T_{\text{ID}}(A)))) \ge \tau_{\text{identity}}$ |
| **`DISCRIMINATION_GATE`** | Separation vs matched foils | $\tau_{\text{discrimination}}$ | Grouped K-Fold ($K=5$) Youden's $J$ on `DEVELOPMENT` | Separation margin satisfies $\tau_{\text{discrimination}}$ and AUROC $\ge 0.95$ with 95% bootstrap CI |
| **`COUNTERFACTUAL_GATE`** | ClosureContrast, SurpriseContrast | $\tau_{\text{counterfactual}}$ | Directional bootstrap lower bound (`NOT_APPLICABLE_ROC_YOUDEN`) | Lower bound of 95% percentile bootstrap CI $> 0$ for each family |
| **`SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE`** | $m_A(t) = \text{sim}(z(A), h_t)$, MemoryContrast | $\tau_{\text{memory}}$ | Retrieval separation & directional bootstrap (`NOT_APPLICABLE_ROC_YOUDEN`) | Retrieval similarity exceeds foil ($p < 0.05$) and lower bound of 95% bootstrap CI of $\text{MemoryContrast} > 0$ |
| **`ANTI_COPY_GATE`** | Three-tier evaluation | $\tau_{\text{copy}}$ | Explicit conjunctive specification | Simultaneous pass: Tier 1 ($L_{\max} \le 12$), Tier 2 ($W_{\text{ngram}} \le \tau_{\text{infocopy}}$, `ADD_ALPHA` $\alpha=0.1$), Tier 3 ($D_{\min} \ge 0.05$) |

### 7.3 Linear Execution Ordering
```
  STEP 1: TRAIN CANDIDATES
  Fit AL-GRU-01 and AL-TRF-01 across R=3 replicates on DEVELOPMENT (50 epochs).
           |
           v
  STEP 2: CHECKPOINT SELECTION & REPLICATE AGGREGATION
  Identify epoch checkpoint minimizing VALIDATION cross-entropy bits/token H(W) per replicate.
  Compute candidate score as median of replicates; select median replicate as canonical checkpoint.
           |
           v
  STEP 3: PROSPECTIVE THRESHOLD CALIBRATION
  Apply Grouped K-Fold (K=5) Youden's J on DEVELOPMENT to calibrate tau_identity and tau_discrimination.
           |
           v
  STEP 4: VALIDATION GATE EVALUATION
  Evaluate the 6 active Stage-0 gates on the 22 VALIDATION pieces across all 3 replicates.
           |
           v
  STEP 5: ARCHITECTURE SELECTION
  Select winning candidate passing all 6 active gates across all replicates (tie-break: lower median H(W)).
           |
           v
  STEP 6: ONE-SHOT BENCHMARK EVALUATION
  Evaluate the selected frozen listener on BENCHMARK_PILOT_ONLY (Lyapunov, 3 pieces) exactly once.
```

### 7.4 Architecture Selection Decision Rule
1. An architecture is qualified if and only if **all 3 replicates** pass all 6 active Stage-0 gates on `VALIDATION`.
2. If both `AL-GRU-01` and `AL-TRF-01` qualify, the primary tie-breaker is lower replicate median `VALIDATION` bit-rate $H(W)$.
3. The secondary tie-breaker is lower trainable parameter count.
4. If neither architecture qualifies, the milestone terminates in fail-closed state (`STAGE0_LISTENER_REPRESENTATION_FAILED`).

---

## 8. Fail-Closed Scientific Decision Rules & Violations

The following conditions trigger an immediate hard stop:
- Any gradient update or parameter tuning on `VALIDATION` or `BENCHMARK_PILOT_ONLY` pieces.
- Any inspection, tokenization, or materialization of firewalled external composers (Taneyev, Bortkiewicz, Blumenfeld, Catoire).
- Altering the model candidate set or modifying layer dimensions after inspecting validation performance.
- Cherry-picking the best replicate seed rather than using the median replicate rule.
- Any attempt to calculate gate thresholds on `VALIDATION` rather than `DEVELOPMENT`.
- Any promotion of `COMPOSER_GENERALIZATION_GATE` or `THEMATIC_MEMORY_GATE` to active operational status in PF-002A.
- Any non-reproducibility across independent runs under identical `RandomContext` seeds.

---

## 9. Conclusion & Protocol Freeze Token

Milestone **PF-002A.0a** successfully closes prospective protocol executability and gate semantics. All architectural budgets, singular positional encodings, gate-specific calibration mechanisms, replicate aggregation rules, sampling distributions, and namespace paths are mathematically locked prior to implementing any trainable model.

**Authoritative Freeze Token**:
`PF002A_EXECUTABLE_MODEL_PROTOCOL_FROZEN_READY_FOR_IMPLEMENTATION`
