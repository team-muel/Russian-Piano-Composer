# PF-002A.0: Prospective Artificial Listener Model Family & Execution Protocol Freeze

## 1. Executive Summary & Authoritative Status

Milestone **PF-002A.0** establishes the prospective freeze of the Artificial Listener model candidate set, input representations, training objectives, stochastic seed hierarchy, training budget, checkpoint-selection rules, architecture-selection rules, threshold-calibration ordering, validation ordering, and fail-closed behavior.

Following the closure of **PF-001C1** (metric definitions and prospective calibration procedure) and **PF-001C1.2** / **PF-001C1.3b** (exact dataset roles and autonomous Stage-0 policy synchronization), this protocol ensures that **no model fitting, representation extraction, or threshold calibration occurs before all execution rules are mathematically frozen**.

### Core Governance Principles
1. **Prospective Model Freeze**: Exactly two compact causal neural architectures (`AL-GRU-01` and `AL-TRF-01`) are admitted. No architectural exploration, parameter expansion, or ad-hoc redesign is permitted after inspecting validation outcomes.
2. **Single Neural Framework**: **PyTorch** (`torch>=2.2,<2.4`) is specified as the sole neural framework, operating in full CPU/GPU determinism (`use_deterministic_algorithms=True`).
3. **Training Cohort Boundary**: Model parameters, representations, and vocabulary statistics are fitted strictly on the 37 `DEVELOPMENT` pieces. `VALIDATION` (22 pieces) and `BENCHMARK_PILOT_ONLY` (3 pieces) are strictly excluded from gradient updates, representation learning, and vocabulary estimation.
4. **Prospective Calibration Ordering**: Operational gate thresholds ($\tau$) are calibrated strictly on `DEVELOPMENT` cross-validation folds *before* evaluating `VALIDATION` performance.
5. **Single Frozen Checkpoint**: A single checkpoint per candidate architecture is selected based strictly on minimum `VALIDATION` cross-entropy bit-rate within a fixed 50-epoch budget.
6. **Firewall & Exclusion Enforcement**: External test candidates (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled. Historical Scriabin remains excluded by lineage policy.
7. **Composer Generalization Invariant**: `COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION` remains frozen.
8. **Theme Identity Invariant**: `THEMATIC_MEMORY_GATE = THEME_IDENTITY_DEPENDENT_NOT_READY` remains frozen; PF-002A operational memory is governed by `SOURCE_SEGMENT_STRUCTURAL_MEMORY`.

**Milestone Status**: `PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET`  
**Authoritative Protocol Hash**: `fbe099bb3e2155e393a69704ae73b9b10867e9af19246682f12e0675101476b9`

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
   - $\text{duration}$: Quantized rational duration tokens derived from score notation (e.g. sixteenth, eighth, dotted-eighth, quarter, half, whole, and tuplet equivalents).
   - $\text{metric\_pos}$: Rational offset within measure $m$ relative to active time signature.
   - $\text{bar\_flag}$: Explicit measure boundary token `⟨BAR⟩` separating measures.
   - Boundary tokens: `⟨BOS⟩` (beginning of sequence) and `⟨EOS⟩` (end of sequence).
3. **Context Window**: Maximum context length $L = 1024$ events. Pieces exceeding $L$ are framed via sliding windows of length $L$ with 50% overlap ($512$ events), strictly preserving measure boundaries.
4. **Vocabulary Fitting**: The token vocabulary $V$ and all empirical frequency marginals are fitted strictly on `DEVELOPMENT`. Unseen tokens in `VALIDATION` map to `⟨UNK⟩`.
5. **Lineage Preservation**: Every token sequence retains source score metadata: `piece_id`, `work_id`, `composer_id`, `source_role`, and `canonical_materialized_sha256`.

---

## 4. Prospective Model Candidate Set

To prevent post-hoc architecture selection and fishing, exactly **two** compact causal architectures are prospectively admitted:

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
          |  2-Layer Causal GRU  |        |  4-Layer Causal TRF  |
          |   Hidden Dim = 256   |        |   Model Dim = 128    |
          |   Param: ~210,000    |        |   Param: ~310,000    |
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
- **Embedding Dimension**: $d_{\text{embed}} = 128$.
- **Recurrent Layers**: 2 stacked GRU layers, hidden dimension $d_{\text{hidden}} = 256$.
- **Dropout**: $0.1$ applied between recurrent layers.
- **Latent Representation**: The hidden state of the final GRU layer at time $t$, $h_t \in \mathbb{R}^{256}$, serves as the frame-level latent embedding $z_t = \text{LayerNorm}(h_t)$.
- **Parameter Upper Bound**: $\le 250,000$ trainable parameters.

### 4.2 Candidate 2: `AL-TRF-01` (Causal Transformer Artificial Listener)
- **Architecture**: Compact causal autoregressive Transformer decoder.
- **Embedding Dimension**: $d_{\text{model}} = 128$.
- **Attention Layers**: 4 causal self-attention layers with causal attention mask.
- **Attention Heads**: 4 heads ($d_{\text{head}} = 32$).
- **Feed-Forward Dimension**: $d_{\text{ff}} = 512$, GELU activation.
- **Positional Encoding**: Learned absolute positional embeddings or rotary position embeddings (RoPE).
- **Normalization**: Pre-LayerNorm architecture, dropout $0.1$.
- **Latent Representation**: The final-layer output vector at time $t$, $z_t \in \mathbb{R}^{128}$, normalized via $\ell_2$-norm.
- **Parameter Upper Bound**: $\le 350,000$ trainable parameters.

---

## 5. Training Objective, Loss Hierarchy & Multi-Task Balance

Training is performed on `DEVELOPMENT` using a joint predictive and representation learning objective:

$$\mathcal{L}_{\text{total}} = \lambda_{\text{pred}} \mathcal{L}_{\text{pred}} + \lambda_{\text{repr}} \mathcal{L}_{\text{repr}}$$

1. **Predictive Loss ($\mathcal{L}_{\text{pred}}$)**:
   - Next-event autoregressive cross-entropy over vocabulary $V$:
     $$\mathcal{L}_{\text{pred}} = -\frac{1}{N} \sum_{i=1}^N \ln P(w_i \mid w_{<i})$$
   - Weight: $\lambda_{\text{pred}} = 1.0$.

2. **Self-Supervised Representation Loss ($\mathcal{L}_{\text{repr}}$)**:
   - Contrastive InfoNCE loss enforcing invariance under identity transformations ($T_{\text{ID}}$):
     $$\mathcal{L}_{\text{repr}} = -\log \frac{\exp(\text{sim}(z(A), z(T_{\text{ID}}(A))) / \tau_{\text{temp}})}{\exp(\text{sim}(z(A), z(T_{\text{ID}}(A))) / \tau_{\text{temp}}) + \sum_{j} \exp(\text{sim}(z(A), z(N_j)) / \tau_{\text{temp}})}$$
   - Temperature parameter: $\tau_{\text{temp}} = 0.07$.
   - Hard negatives ($N_j$) and transformations ($T_{\text{ID}}$) are sampled strictly from `DEVELOPMENT`.
   - Weight: $\lambda_{\text{repr}} = 0.5$.

3. **Intervention & Counterfactual Non-Contamination Rule**:
   - Counterfactual perturbations (`CF-CLOSURE`, `CF-SURPRISE`, `CF-SOURCE-SEGMENT-MEMORY`), memory probe tasks, and anti-copy checks are **strictly evaluation probes**. They must **never** be included in the training loss or gradient graph.

---

## 6. Stochastic Hierarchy, Optimization & Training Budget

### 6.1 Deterministic RNG Hierarchy
All stochastic operations (shuffling, batching, dropout initialization, weight initialization) derive from `RandomContext` (`root_seed = 20260930`):
- `pf002a/weights/<arch_id>/<replicate_id>`: Layer weight initialization.
- `pf002a/dataloader/<replicate_id>`: Batch ordering and sequence window slicing.
- `pf002a/augmentation/<replicate_id>`: Online $T_{\text{ID}}$ pair generation for $\mathcal{L}_{\text{repr}}$.
- `pf002a/evaluation/bootstrap`: Resampling folds and percentile bootstrap replicates ($B = 2000$).

### 6.2 Optimization Hyperparameters & Budget
- **Optimizer**: AdamW ($\beta_1 = 0.9, \beta_2 = 0.98, \epsilon = 10^{-8}$, weight decay $= 0.01$).
- **Learning Rate**: Peak learning rate $\eta_{\max} = 5 \times 10^{-4}$.
- **Warmup & Schedule**: 5 epochs linear warmup followed by cosine annealing to $\eta_{\min} = 1 \times 10^{-5}$.
- **Batch Size**: 16 sequence windows (clustered by piece to avoid within-batch cross-piece leakage).
- **Gradient Clipping**: Maximum gradient norm $1.0$.
- **Fixed Epoch Budget**: Exactly 50 epochs. No early stopping is permitted to introduce arbitrary termination dates.

### 6.3 Independent Replicates
Each candidate architecture is trained across $R = 3$ independent replicates:
- Replicate 0: `path = ("pf002a", "rep0")`
- Replicate 1: `path = ("pf002a", "rep1")`
- Replicate 2: `path = ("pf002a", "rep2")`

---

## 7. Prospective Checkpoint Selection & Evaluation Ordering

Execution follows an immutable linear order:

```
  STEP 1: TRAIN CANDIDATES
  Fit AL-GRU-01 and AL-TRF-01 across R=3 replicates on DEVELOPMENT (50 epochs).
           |
           v
  STEP 2: CHECKPOINT SELECTION (PER CANDIDATE)
  Identify checkpoint minimizing VALIDATION cross-entropy bits/token H(W).
  Freeze checkpoint weights into immutable .pt state_dict.
           |
           v
  STEP 3: PROSPECTIVE THRESHOLD CALIBRATION
  Apply Grouped K-Fold (K=5) Youden's J on DEVELOPMENT folds using frozen weights.
  Derive operating thresholds: tau_perplexity, tau_identity, tau_discrimination,
  tau_counterfactual, tau_memory, tau_copy.
           |
           v
  STEP 4: VALIDATION GATE EVALUATION
  Evaluate the 6 active Stage-0 gates on the 22 VALIDATION pieces using tau.
           |
           v
  STEP 5: ARCHITECTURE SELECTION
  Select winning candidate passing all 6 active gates (tie-break: lower validation H(W)).
           |
           v
  STEP 6: ONE-SHOT BENCHMARK EVALUATION
  Evaluate the selected frozen listener on BENCHMARK_PILOT_ONLY (Lyapunov, 3 pieces)
  exactly once. No parameter tuning or retry permitted.
```

### 7.1 Checkpoint Selection Rule
For each architecture, evaluate `VALIDATION` cross-entropy bit-rate $H(W)$ at each epoch boundary $e \in \{1, \dots, 50\}$.
Select the single checkpoint achieving minimal $H(W)$:
$$e^* = \arg\min_{e \in \{1, \dots, 50\}} H_{\text{val}}(W; \theta_e)$$
The checkpoint at $e^*$ is frozen and serialized to disk with its SHA-256 digest recorded.

### 7.2 Prospective Calibration Ordering
Before evaluating any operational pass/fail gates on `VALIDATION`, operational thresholds ($\tau$) must be computed strictly on `DEVELOPMENT`:
- $K = 5$ grouped folds by `piece_id`.
- Grid search over $\tau \in [-1.0, 1.0]$ with step $0.005$ optimizing Youden's $J = \text{TPR} - \text{FPR}$.
- Median fold threshold $\tau^* = \text{median}(\tau_1^*, \dots, \tau_5^*)$.
- Percentile bootstrap ($B = 2000$) 95% confidence intervals.

### 7.3 Active Stage-0 Gate Evaluation
The frozen candidate is evaluated against the 6 active gates on `VALIDATION`:
1. `PREDICTIVE_GATE`: $H_{\text{val}}(W) < H_{\text{Markov}}(W)$ and $H_{\text{val}}(W) \le \tau_{\text{perplexity}}$.
2. `INVARIANCE_GATE`: $\text{median}(\text{sim}(z(A), z(T_{\text{ID}}(A)))) \ge \tau_{\text{identity}}$.
3. `DISCRIMINATION_GATE`: $\text{AUROC} \ge \tau_{\text{auroc}}$ and foil similarity $\le \tau_{\text{foil}}$.
4. `COUNTERFACTUAL_GATE`: Lower 95% bootstrap CI of $\text{ClosureContrast} > 0$ and $\text{SurpriseContrast} > 0$.
5. `SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE`: Lower 95% bootstrap CI of $\text{MemoryContrast} > 0$ with separation over negative foil.
6. `ANTI_COPY_GATE`: Maximum contiguous match $L_{\max} \le \tau_{\text{copy\_ngram}}$ and latent distance $D_{\min} \ge \tau_{\text{copy\_latent}}$.

### 7.4 Architecture Selection Decision Rule
1. An architecture is qualified if and only if it passes all 6 active Stage-0 gates on `VALIDATION`.
2. If both `AL-GRU-01` and `AL-TRF-01` pass all 6 gates, the primary tie-breaker is lower `VALIDATION` bit-rate $H(W)$.
3. The secondary tie-breaker is lower trainable parameter count.
4. If neither architecture passes all 6 gates, the milestone terminates in fail-closed state (`STAGE0_LISTENER_REPRESENTATION_FAILED`).

### 7.5 One-Shot Benchmark Pilot Evaluation
Only the winning, frozen architecture is evaluated on the 3 `BENCHMARK_PILOT_ONLY` pieces (Lyapunov Op. 11 Nos. 1, 2, 3). This evaluation occurs **exactly once**. No iterative adjustment, parameter retraining, or threshold re-calibration is permitted based on Lyapunov performance.

---

## 8. Fail-Closed Scientific Decision Rules & Violations

The following conditions trigger an immediate hard stop:
- Any gradient update or parameter tuning on `VALIDATION` or `BENCHMARK_PILOT_ONLY` pieces.
- Any inspection, tokenization, or materialization of firewalled external composers (Taneyev, Bortkiewicz, Blumenfeld, Catoire).
- Altering the model candidate set (adding a third architecture or modifying layer dimensions) after inspecting validation performance.
- Any attempt to calculate gate thresholds on `VALIDATION` rather than `DEVELOPMENT`.
- Any promotion of `COMPOSER_GENERALIZATION_GATE` or `THEMATIC_MEMORY_GATE` to active operational status in PF-002A.
- Any non-reproducibility across independent runs under identical `RandomContext` seeds.

---

## 9. Conclusion & Protocol Freeze Token

Milestone **PF-002A.0** successfully freezes the prospective model family and execution protocol. All architectural, optimization, calibration, and selection parameters are locked prior to executing any trainable model.

**Authoritative Freeze Token**:
`PF002A_PROSPECTIVE_MODEL_PROTOCOL_FROZEN_READY_FOR_IMPLEMENTATION`
