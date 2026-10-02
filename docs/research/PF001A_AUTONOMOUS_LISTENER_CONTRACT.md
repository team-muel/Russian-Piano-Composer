# PF-001A: Autonomous Artificial Listener Contract Specification
## Autonomous Classical Representation Learning, Structural Invariance, and Multi-Scale Listener Modeling

**Document Type:** Scientific Architecture & Autonomous Contract  
**Milestone:** PF-001A  
**Project:** Russian Piano Composer  
**Status:** AUTONOMOUS_LISTENER_CONTRACT_FROZEN_READY_FOR_CORPUS_FEASIBILITY  
**Governing Standard:** Corpus-Observable Structural Supervision & Counterfactual Listener Verification  

---

### Executive Statement & Scientific Inversion

PF-001A updates and clarifies the foundational contract of the **Perception-First Classical Composition** architecture:

> **Core Principle:** Human participant listening studies are **not** required as the Stage-0 training or gating prerequisite.  
> The primary teacher is the **corpus of human-composed classical music itself**.

The governing autonomous loop is defined as:
$$\text{HUMAN CLASSICAL CORPUS} \longrightarrow \text{SELF-SUPERVISED REPRESENTATION LEARNER} \longrightarrow \text{ARTIFICIAL LISTENER}$$
$$\longrightarrow \text{STRUCTURAL WORLD MODEL} \longrightarrow \text{COMPOSER} \longrightarrow \text{COUNTERFACTUAL CRITIC} \longrightarrow \text{REVISION}$$

Human listening studies are reclassified as an **`OPTIONAL_EXTERNAL_VALIDATION`** layer. They are strictly required only when making an explicit claim regarding human subjective experience (e.g., *"human listeners judge this passage as tense"*), but autonomous structural model development, representation learning, and composer criticism do not depend on human participant data collection.

```mermaid
flowchart TD
    CC["Human Classical Corpus<br/>(19th-Century Russian Repertoire)"] --> RL["Self-Supervised & Weakly-Supervised<br/>Representation Learner"]
    RL --> AL["Autonomous Artificial Listener<br/>(Stage-0 Structural Model)"]
    AL --> SWM["Structural World Model<br/>(Multi-Scale Syntactic Dynamics)"]
    SWM --> COMP["Composer<br/>(Symbolic Plan & Generation)"]
    COMP --> CCrit["Counterfactual Critic<br/>(Perturbation Deficit Verification)"]
    CCrit --> REV["Iterative Revision Loop"]

    subgraph Optional Human Layer
        HE["Optional External Human Studies<br/>(EXP-001 - EXP-005)"]
    end
    AL -.->|Optional Subjective Benchmark| HE
```

---

### 1. Stage-0 Autonomous State Variables & Mathematical Formulations

To preserve scientific truthfulness, internal model variables are strictly designated as **structural quantities** rather than making unverified claims of human perceptual equivalence:

| State Variable | Notation | Mathematical Definition | Corpus Supervision Source | Multi-Scale Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Structural Expectation** | $E_s(t)$ | $P(x_{t+1} \mid x_{\le t})$ | Corpus token/event sequences; self-supervised masked & causal autoregression | Event, Motif, Phrase, Section |
| **Structural Uncertainty** | $U_s(t)$ | $H\left[P(x_{t+1} \mid x_{\le t})\right] = -\sum_k p_k \log_2 p_k$ | Derived informational entropy of conditional predictive distribution | Event, Motif, Phrase |
| **Structural Surprise** | $S_s(t)$ | $-\log_2 P(x_t \mid x_{<t})$ | Derived negative log-likelihood of observed event under prior context | Event, Chord, Cadence |
| **Structural Closure** | $C_s(t)$ | $P(\text{boundary} \mid x_{\le t}) \in [0, 1]$ | Corpus-observable cadential, phrase, and formal boundaries | Phrase, Section, Piece |
| **Motif Identity** | $R_m(t)$ | $\text{sim}(z(M), z(T(M))) = \frac{z(M) \cdot z(T(M))}{\|z(M)\|\|z(T(M)\|}$ | Self-supervised contrastive learning with synthetic morphological transformations | Motif, Sub-phrase |
| **Structural Memory** | $M_s(t)$ | $m_k(t) = \text{sim}(z(M_k), h_t)$ | Memory buffer attention / associative retrieval trace over preceding context | Phrase, Section, Whole-Piece |

#### 1.1 Structural Expectation ($E_s(t)$)
The predictive model must learn conditional distributions across multiple musical hierarchies:
$$E_s(t) = \left\{ P_{\text{event}}(e_{t+1} \mid e_{\le t}), P_{\text{motif}}(m_{k+1} \mid m_{\le k}), P_{\text{phrase}}(\phi_{j+1} \mid \phi_{\le j}), P_{\text{section}}(S_{r+1} \mid S_{\le r}) \right\}$$
Prediction is not restricted to raw MIDI pitch-onsets; it operates over hierarchical syntactic entities (tonal roots, voice-leading intervals, harmonic functions, metric accent classes).

#### 1.2 Structural Uncertainty ($U_s(t)$) & Structural Surprise ($S_s(t)$)
- $U_s(t)$ measures the dispersion across predictive space under the learned model. A high $U_s(t)$ signifies that the corpus distribution contains multiple viable syntactic paths (e.g., developmental sequential modulations). It does not assert that a human listener feels psychological anxiety.
- $S_s(t)$ measures the information-theoretic surprisal of realized transitions.

#### 1.3 Structural Closure ($C_s(t)$)
Trained as a weakly-supervised boundary detector using corpus-observable structural markers:
1. Cadential signatures: Perfect authentic cadences (PAC), imperfect authentic cadences (IAC), half cadences (HC), deceptive cadences (DC).
2. Metrical hypermetric phrase terminations (e.g. 4-bar, 8-bar boundaries with harmonic resolution).
3. Sectional double barlines and formal recapitulation entries.
*Invariant:* Structural closure must not be equated with low tension. A peaceful, harmonically open modal passage has zero closure despite low tension; an authentic cadence preceding an urgent fermata has maximal closure.

#### 1.4 Motif Identity & Representation Learning ($R_m(t)$)
The motif encoder $z(\cdot)$ must satisfy a formal **Invariance-to-Discrimination Contrastive Contract**:
1. **Invariance:** For any identity-preserving transformation $T \in \mathcal{T}_{\text{id}}$:
   $$\| z(M) - z(T(M)) \| \le \epsilon_{\text{inv}}$$
   where $\mathcal{T}_{\text{id}}$ includes exact transposition, octave/register displacement, rhythmic augmentation/diminution, controlled melodic ornamentation (passing notes, appoggiaturas), and polyphonic accompaniment variations.
2. **Discriminability:** For any distinct negative motif foil $M_{\text{neg}}$ or identity-destroying chromatic scrambling $T_{\text{destr}}$:
   $$\| z(M) - z(M_{\text{neg}}) \| \ge \delta_{\text{disc}} \gg \epsilon_{\text{inv}}$$
   This dual requirement guarantees that the representation space does not collapse into a degenerate trivial constant.

#### 1.5 Long-Range Structural Memory Trace ($M_s(t)$)
Under PF-001C1, Stage-0 evaluates **`SOURCE_SEGMENT_STRUCTURAL_MEMORY`** ($m_A(t) = \text{sim}(z(A), h_t)$ across literal and $T_{\text{ID}}$ recurrences of source segment $A$), while full human `THEMATIC_MEMORY_GATE` remains `THEME_IDENTITY_DEPENDENT_NOT_READY`.
The model must pass prospective persistence tests:
- *Disappearance:* $m_A(t)$ decays toward baseline during unexposed development episodes.
- *Partial Hint:* An incipit cue produces an intermediate activation spike.
- *Transformed Recurrence:* Recurrence of $A$ under diminution or transposition reactivates $m_A(t) \ge \tau_{\text{memory}}$ (calibrated prospectively via Youden's $J$).
- *Full Recurrence:* Full literal recurrence restores $m_A(t) \ge \tau_{\text{memory}}$.

---

### 2. Autonomous Theme Fertility ($T_I(M)$)

Rather than optimizing an arbitrary subjective quality score, **Autonomous Theme Fertility** is formalized as the volume and diversity of the admissible transformation space under the frozen motif representation:

$$T_I(M; \tau) = \left\{ M' \in \mathcal{T}(M) : \text{sim}\left( z(M), z(M') \right) \ge \tau \right\}$$

$$\text{Fertility}(M) = \text{Coverage}\left( T_I(M; \tau) \right) = \mathbb{E}_{T \sim \mathcal{T}}\left[ \mathbb{I}\left( \text{sim}(z(M), z(T(M))) \ge \tau \right) \cdot \text{Diversity}(T) \right]$$

*Scientific Invariant:* Theme Fertility is defined strictly for measurement, analysis, and ranking in PF-001A. Automatic optimization of fertility during composition is **prohibited** until Stage-0 listener models pass all validation gates.

---

### 3. Multi-Scale Representation Contract

The Artificial Listener must maintain explicit representation streams or probes across five hierarchical timescales:
1. **Event Scale ($\sim 100 - 500\text{ ms}$):** Pitch, duration, voice, velocity, melodic interval.
2. **Motif Scale ($\sim 1 - 4\text{ seconds}$):** Melodic contour, rhythmic motif, harmonic cell.
3. **Phrase Scale ($\sim 4 - 16\text{ seconds}$):** Antecedent-consequent pairing, cadential arrival, phrase breath.
4. **Section Scale ($\sim 30 - 120\text{ seconds}$):** Thematic exposition, episodic modulation, climactic buildup.
5. **Whole-Piece Scale ($\sim 2 - 15\text{ minutes}$):** Global tonality arc, cyclic thematic return, formal sonata/rondo architecture.

Compressing all temporal hierarchies into an unstratified single latent vector without scale identity violates the multi-scale contract.

---

### 4. Autonomous Scientific Validation Gates & Readiness

Candidate Artificial Listener models are evaluated across the authoritative scientific gates established in PF-001C1:

```mermaid
graph TD
    subgraph S0_ACTIVE["Active Stage-0 Autonomous Gates (Calibrated Prospectively via Youden's J)"]
        G1["1. PREDICTIVE_GATE<br/>tau_perplexity vs non-neural baselines"]
        G2["2. INVARIANCE_GATE<br/>tau_identity across T_id transforms"]
        G3["3. DISCRIMINATION_GATE<br/>tau_discrimination AUROC & margin vs foils"]
        G4["4. COUNTERFACTUAL_GATE<br/>tau_counterfactual directional contrasts > 0"]
        G5["5. SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE<br/>tau_memory & MemoryContrast > 0"]
        G6["6. ANTI_COPY_GATE<br/>tau_copy 3-tier de-plagiarism checks"]
    end

    subgraph UNREADY["Gating Excluded From Stage-0 Pass/Fail"]
        G7["7. COMPOSER_GENERALIZATION_GATE<br/>(NOT_READY_FOR_CALIBRATION)"]
        G8["THEMATIC_MEMORY_GATE<br/>(THEME_IDENTITY_DEPENDENT_NOT_READY)"]
    end

    G1 & G2 & G3 & G4 & G5 & G6 --> ALL_ACTIVE_PASS{"All 6 Active Stage-0<br/>Gates Passed?"}
    ALL_ACTIVE_PASS -- Yes --> APPROVED["Stage-0 Autonomous Listener Certified"]
    ALL_ACTIVE_PASS -- No --> BLOCKED["Fail-Closed: Retrain / Refine Architecture"]
```

> [!NOTE]
> **Threshold Authority & Calibration Protocol (PF-001C1):**
> Active gate descriptions use **symbolic threshold identifiers** ($\tau_{\text{perplexity}}, \tau_{\text{identity}}, \tau_{\text{discrimination}}, \tau_{\text{counterfactual}}, \tau_{\text{memory}}, \tau_{\text{copy}}$). Numerical operational cutoffs are **NOT** predefined authoritative constants; they are prospectively calibrated in **PF-002A** using grouped $K=5$-fold Youden's $J$ optimization clustered at `piece_id` with 2,000 bootstrap resamples on the `development` corpus.

1. **`PREDICTIVE_GATE`:** Negative log-likelihood, bits/token, and perplexity on held-out compositions within the `validation` pool exceeding frozen non-neural baselines (`BASE_EMPIRICAL_MARGINAL`, `BASE_MARKOV_ORDER_1`, `BASE_NGRAM_4`) by threshold $\tau_{\text{perplexity}}$.
2. **`INVARIANCE_GATE`:** Mean cosine similarity across identity-preserving transformations satisfying $\mathbb{E}[\text{sim}(z(A), z(T_{\text{id}}(A)))] \ge \tau_{\text{identity}}$.
3. **`DISCRIMINATION_GATE`:** Separation against negative foils evaluated via $\text{AUROC} \ge \tau_{\text{discrimination}}$ and cosine margin separation.
4. **`COUNTERFACTUAL_GATE`:** Directional contrast statistics satisfying $\tau_{\text{counterfactual}}$:
   - Cadence disruption: $\text{ClosureContrast} = C_c - C_t > 0$ (`CF-CLOSURE`).
   - Controlled surprise perturbation: $\text{SurpriseContrast} = S_{\text{target}} - S_{\text{control}} > 0$ (`CF-SURPRISE`).
   - Source-segment recurrence-cue disruption: $\text{MemoryContrast} = M_{\text{control}} - M_{\text{target}} > 0$ (`CF-SOURCE-SEGMENT-MEMORY`).
5. **`SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE` (formerly `LONG_RANGE_MEMORY_GATE`):** Reactivation of source-segment representation across intervening musical context satisfying $m_A(t) \ge \tau_{\text{memory}}$ and directional cue-disruption contrast.
6. **`ANTI_COPY_GATE`:** Multi-tier de-plagiarism filter satisfying threshold $\tau_{\text{copy}}$ across:
   - Tier 1: Symbolic contiguous n-gram overlap ($L_{\max} \le \tau_{\text{ngram}}$).
   - Tier 2: Information-weighted melodic interval n-gram score under single `ADD_ALPHA` ($\alpha=0.1$) estimator ($W(G) \le \tau_{\text{infocopy}}$).
   - Tier 3: Latent space nearest-neighbor cosine distance ($D_{\min} \ge \tau_{\text{latent\_dist}}$).
7. **`COMPOSER_GENERALIZATION_GATE`:** Governed strictly as **`NOT_READY_FOR_CALIBRATION`**. Degradation on disjoint validation composers is monitored for exploratory analysis but is **not** an operational gating requirement for Stage-0 listener certification.

---

### 5. Anti-Copying & De-Plagiarism Policy

A model that reproduces classical structures must not operate as an associative lookup table of memorized human pieces. The system implements a three-tier programmatic anti-copy battery:
1. **Tier 1 (Melodic N-Gram Overlap):** Longest common contiguous pitch-interval subsequence between model generation/prediction and training corpus must not exceed symbolic threshold $\tau_{\text{ngram}}$ (calibrated against human baseline corpora).
2. **Tier 2 (Information-Weighted Melodic N-Gram):** Information-weighted interval n-gram metric evaluated using the single frozen `ADD_ALPHA` estimator ($\alpha = 0.1$) on development data must not exceed $\tau_{\text{infocopy}}$.
3. **Tier 3 (Nearest-Neighbor Training Retrieval):** Latent space nearest-neighbor distance $D_{\min}(G, \mathcal{D}_{\text{dev}}) \ge \tau_{\text{latent\_dist}}$ ensuring generated/predicted excerpts do not retrieve training examples with degenerate proximity.

---

### 5.1 Historical Provisional Targets (Non-Authoritative Archive)

> [!WARNING]
> **Status: `HISTORICAL_PROVISIONAL_NONAUTHORITATIVE` (`PROVISIONAL_UNCALIBRATED_TARGET`)**
> The numerical quantities below represent historical planning estimates from initial PF-001 conceptual drafts prior to physical corpus materialization (PF-001B) and metric contract formalization (PF-001C / PF-001C1).
> - They are **NOT** valid PF-002A operational thresholds.
> - They are **NOT** model-selection or checkpoint-selection criteria.
> - They are **NOT** Stage-0 pass/fail criteria.
> - They are **NOT** calibration outputs.
> Active PF-002A validation strictly uses the prospective Youden's $J$ calibration procedure on frozen symbolic parameters (calibrated in PF-001C / PF-002A).
>
> *Historical Reference Values:*
> - Historical Invariance target: $\text{sim} \ge 0.85$.
> - Historical Discrimination target: $\text{sim} \le 0.30$, $\text{AUROC} \ge 0.95$.
> - Historical Counterfactual shifts: closure shift $\ge 0.40$, memory reduction $\ge 0.50$, surprise surge $\ge 2.5\text{ bits}$.
> - Historical Long-Range Memory ratio: $\ge 1.80$.
> - Historical Composer Degradation: $\le 15\%$.
> - Historical Anti-Copy heuristic cutoffs: $L_{\max} = 12\text{ notes}$, latent distance $< 0.05$.

---

### 6. Fail-Closed Protocol & Prohibited Activities

The following activities remain strictly **prohibited** in PF-001A:
- Building or training a new composition generator model.
- Defining or training an overall scalar "musical quality" reward function.
- Reinforcement learning with human feedback (RLHF) against unvalidated preferences.
- Prematurely unblinding the frozen RC-012 483-piece corpus as a new test cohort (including Scriabin's 207 pieces, which are designated `PREVIOUSLY_EXPOSED_IN_RC012`, `EXCLUDED_FROM_PF_DEVELOPMENT_BY_LINEAGE_POLICY`, and `NOT_ELIGIBLE_AS_UNTOUCHED_EXTERNAL_DATA`).
- Freezing candidate external composer cohorts before a physical machine-readable corpus feasibility audit is certified.

