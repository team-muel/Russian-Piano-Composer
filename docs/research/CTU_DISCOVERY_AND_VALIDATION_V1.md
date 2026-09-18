# Unsupervised Candidate Thematic Unit (CTU) Discovery & Held-Out Future-Reuse Validation (V1)

## Executive Summary

This document presents the design, mathematical formulation, empirical protocol, and empirical findings for **Candidate Thematic Unit (CTU) Schema V1** under **RC-009B**. 

CTUs are operational computational objects discovered purely from canonical symbolic score data without human theme annotations, role-conditioning, or generative labels.

---

## 1. Scientific Objective & Integrity Safeguards

The goal of RC-009B is to discover operational thematic units within symbolic piano scores and empirically evaluate whether these candidate units show statistically significant higher **future recurrence and developmental reuse** in a temporally held-out region compared to activity-matched random negative control segments from the same piece.

### Integrity & Independence Invariants
1. **Zero Human Ground Truth Leakage**: Human theme annotations (e.g. from RC-008) were **NOT** used for training, hyperparameter tuning, candidate selection, thresholding, or validation.
2. **Temporal Split Anti-Leakage**: Each piece with at least 12 complete measures is chronologically split into:
   - **Discovery Region**: First 60% of complete measures ($[0, \text{discovery\_measures})$).
   - **Future Validation Region**: Last 40% of complete measures ($[\text{discovery\_measures}, \text{total\_measures})$).
   No information from the future validation region influenced candidate generation, similarity weights, candidate filtering, or ranking.
3. **Role-Blind Discovery**: Scores were processed without composer, style, or group labels. Corpus metadata was attached solely post-hoc for summary reporting.
4. **Polyphonic Texture Respect**: Pitch and interval evidence maintains separate `(staff, voice)` streams without collapsing multi-voice textures into a single top-note pseudo-melody or assuming `staff == hand`. Melodic transitions are restricted strictly to consecutive single-note attacked onsets per voice stream (adjacent single-note onsets only; no interval bridging across chords).
5. **Fail-Closed Activity Control Matching**: Negative controls require exact piece, measure length, discovery region placement, $\text{IoU} < 0.50$ with the target CTU and all retained CTUs, and activity matching within $\pm 25\%$ of note attack count and distinct onset count. Unconditional fallbacks are strictly prohibited. If no valid control exists, `CONTROL_UNAVAILABLE` is assigned and the pair is excluded from paired difference statistics.

---

## 2. Mathematical Formulations & Component Definitions

### A. Candidate Generation & Multi-Scale Sliding Windows
For a piece with $M_{\text{disc}}$ discovery measures, candidate segments are generated across multi-scale measure durations $W \in \{1, 2, 3, 4, 6, 8\}$ with stride $s = 1$ measure:
$$
\text{Candidate Span } S = [m_{\text{start}}, m_{\text{end}}) \quad \text{where } m_{\text{end}} - m_{\text{start}} \in W, \; m_{\text{end}} \le M_{\text{disc}}
$$

### B. Segment Representation Vector $\mathbf{R}(S)$
Each candidate segment $S$ is converted to a multi-channel symbolic representation:
1. **Melodic Interval Channel**: Vector of pitch interval transitions $\Delta p = p_{i+1} - p_i$ between consecutive single-note attacked onsets within each `(staff, voice)` stream.
2. **IOI Rhythm Channel**: Vector of consecutive Inter-Onset-Interval ratios $r_i = \text{IOI}_{i+1} / \text{IOI}_i$.
3. **Texture Profile Channel**: Ordered sequence of note attack simultaneities $a(t)$ at each distinct onset time $t$.
4. **Sounding Pitch-Class Channel**: 12-dimensional pitch class distribution vector ($midi \pmod{12}$) normalized by total attacks.

### C. Pairwise Recurrence & Composite Discovery Score
For two non-overlapping discovery segments $S_A, S_B \subset [0, M_{\text{disc}})$, component similarities are computed:
- **Melodic Similarity** $Sim_{\text{mel}}$: Symmetric bipartite match of 2-gram multiset Jaccard similarity across active voice streams.
- **Rhythmic Similarity** $Sim_{\text{rhy}}$: Symmetric bipartite match of 2-gram multiset Jaccard similarity across IOI ratio sequences.
- **Texture Profile Similarity** $Sim_{\text{tex}}$: Ordered 2-gram multiset Jaccard similarity over note attack simultaneity sequences.
- **Sounding Pitch-Class Similarity** $Sim_{\text{pc}}$: Cosine similarity over 12-bin pitch-class vectors.

The composite discovery recurrence score is defined as:
$$
S_{\text{disc}}(S_A, S_B) = w_{\text{mel}} Sim_{\text{mel}} + w_{\text{rhy}} Sim_{\text{rhy}} + w_{\text{tex}} Sim_{\text{tex}} + w_{\text{pc}} Sim_{\text{pc}}
$$
where $w_{\text{mel}}=0.40, w_{\text{rhy}}=0.30, w_{\text{tex}}=0.15, w_{\text{pc}}=0.15$ (all declared as `ENGINEERING_HEURISTIC`). Available evidence channels are renormalized if any channel lacks evidence. Minimum evidence rule requires composite discovery score $S_{\text{disc}} \ge E_1 = 0.30$.

The discovery recurrence score for a candidate $S_i$ is its maximum non-overlapping recurrence score across all valid comparison windows in the discovery region:
$$
\text{RecurrenceScore}(S_i) = \max_{S_j \cap S_i = \emptyset} S_{\text{disc}}(S_i, S_j)
$$

### D. Overlap Suppression (NMS)
To prevent shifted sliding-window copies from dominating, candidates are sorted by $\text{RecurrenceScore}$ descending. A candidate $S_k$ is retained only if its temporal measure overlap (IoU) with any higher-ranked retained candidate $S_r$ is below threshold $\theta_{\text{NMS}} = 0.50$:
$$
\text{IoU}(S_k, S_r) = \frac{|S_k \cap S_r|}{|S_k \cup S_r|} < 0.50
$$

### E. Matched Random Negative Controls
For each retained CTU $S_i$ of length $L_i$ measures in the discovery region, a matched random control segment $C_i$ is sampled from the discovery region using a deterministic `RandomContext.child()` generator such that:
- $\text{Length}(C_i) = L_i$
- $C_i \subset [0, M_{\text{disc}})$
- $\text{IoU}(C_i, S_i) < 0.50$
- $\text{IoU}(C_i, S_r) < 0.50$ for all retained CTUs $S_r$
- $| \text{attack\_count}(C_i) - \text{attack\_count}(S_i) | / \text{attack\_count}(S_i) \le 0.25$
- $| \text{onset\_count}(C_i) - \text{onset\_count}(S_i) | / \text{onset\_count}(S_i) \le 0.25$
- $C_i$ satisfies `min_event_count` activity eligibility.

---

## 3. Held-Out Future-Reuse Validation Protocol

After discovery decisions are frozen, each retained CTU $S_i$ and its matched control $C_i$ are compared against all non-overlapping windows in the **Future Validation Region** $[M_{\text{disc}}, M_{\text{total}})$.

The **Held-Out Future-Reuse Score** for candidate $X$ (where $X \in \{S_i, C_i\}$) is:
$$
\text{FutureReuse}(X) = \max_{V \subset [M_{\text{disc}}, M_{\text{total}})} S_{\text{disc}}(X, V)
$$

### Piece-Level Aggregation & Statistical Tests
To prevent pseudoreplication from correlated candidates within the same score, results are aggregated at the piece level first:
1. $\bar{F}_{\text{ctu}, p} = \text{mean}_{i} \text{FutureReuse}(S_{i, p})$
2. $\bar{F}_{\text{ctrl}, p} = \text{mean}_{i} \text{FutureReuse}(C_{i, p})$
3. $\Delta_p = \bar{F}_{\text{ctu}, p} - \bar{F}_{\text{ctrl}, p}$

Statistical hypothesis testing across eligible pieces:
- **Paired Effect Size**: Cohen's $d_z = \frac{\bar{\Delta}}{s_{\Delta}}$ using sample standard deviation ($n-1$).
- **Bootstrap 95% Confidence Interval**: 10,000 resamples of piece-level paired differences $\Delta_p$.
- **Two-Sided Paired Permutation Test**: Monte Carlo corrected $p = \frac{\text{extreme\_count} + 1}{\text{iterations} + 1}$ over 10,000 sign-flip permutations of $\Delta_p$.

---

## 4. Empirical Corpus Results

### Pipeline Execution Summary
- **Canonical Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`
- **Total Ingested Pieces**: 141
- **Eligible Pieces ($\ge 12$ measures)**: 141
- **Ineligible Pieces ($< 12$ measures)**: 0
- **Raw Candidate Windows Generated**: 40,837
- **Post-NMS Retained CTUs**: 705 (5 CTUs per piece retained)
- **Requested Control Pairs**: 705
- **Valid Matched Control Pairs**: 660
- **Unavailable Control Pairs**: 45
- **Fallback Count**: 0 (Strict 0)

### Statistical Validation Outcome
- **Mean CTU Future Reuse Score**: **0.7167**
- **Mean Control Future Reuse Score**: **0.6498**
- **Mean Paired Difference ($\bar{\Delta}$)**: **+0.0669**
- **Paired Effect Size (Cohen's $d_z$)**: **0.3497**
- **95% Bootstrap Confidence Interval**: **[0.0349, 0.0991]**
- **Permutation Test Iterations**: **10,000**
- **Permutation Extreme Count**: **1**
- **Exact Corrected Permutation p-value**: **0.0002** ($p = (1 + 1) / (10000 + 1) = 2 / 10001 \approx 0.0002$)
- **Positive Effect Fraction**: **64.75%** (90 out of 139 eligible pieces with matched controls showed higher CTU future reuse than matched controls)

---

## 5. Lineage Hashes

| Lineage Component | Hash / Identifier |
| :--- | :--- |
| **Canonical Manifest Hash** | `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212` |
| **CTU Schema Version** | `1` |
| **CTU Schema Semantic Hash** | `03e8103ae9d7d534ded951b781ee6d43269a046fc787c543029c5f9ce3dd0ec1` |
| **Segment Representation Hash** | `967c42a2f47e16dbc6ce3b160ff56284298c73524b46133b6df116ef06db3539` |
| **Similarity Semantic Hash** | `9cdd0387050e9c4aa7025f333da975ed02e453b345ebda3622266343fdb475e2` |
| **Discovery Policy Hash** | `df0810aa9601131df59e1341d6281ce339e1d97b8c993d0baf453fa4a31f0367` |
| **Validation Semantic Hash** | `cb62e4587e415f8500dc52ece0e5ecec68e42c72c7cc7a81b5937d233f877466` |
| **Validation Policy Hash** | `de1fcc0804270f62f104e50958e490d8c3b617b800b578797dee637a7a246e30` |
| **Candidate Set Hash** | `43fda7ba9503df0650fa4e2fb03ff897452a90adf225650d2d785d71a6f6ba8d` |
| **Control Pair Set Hash** | `2f7e25aca378bafffb8efeccaabf682eb84487ea0cbbebc69b56fafae519c96e` |
| **Validation Result Hash** | `4f6878a1cd0e79ca8aa79e44d0ea055fd022f160b773612df419331d27ceebf3` |
| **Process A Payload Hash** | `133f101a85b29b439abce7462dc2258c71290734b1e86c740f0b124e6898b0ae` |
| **Process B Payload Hash** | `133f101a85b29b439abce7462dc2258c71290734b1e86c740f0b124e6898b0ae` |

---

## 6. Official Scientific Outcome Statement

$$
\boxed{\mathbf{EMPIRICAL\ CTU\ STATUS = CTU\_VALIDATED}}
$$

### Scientific Interpretation
Unsupervised Candidate Thematic Units (CTUs) discovered solely within the initial 60% discovery region of canonical symbolic scores exhibit statistically significant higher future-reuse scores in the temporally held-out 40% region ($p = 0.0002, d_z = 0.3497, 95\%\text{ CI } [0.0349, 0.0991]$) compared to fail-closed activity-matched random negative control segments across all 141 pieces.

*Note: `CTU_VALIDATED` is an operational computational status confirming higher future recurrence/developmental reuse under frozen V1 semantics. It does NOT imply human musicological theme adjudication or ground truth consensus.*
