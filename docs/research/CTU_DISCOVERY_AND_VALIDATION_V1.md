# Unsupervised Candidate Thematic Unit (CTU) Discovery & Held-Out Future-Reuse Validation (V1)

## Executive Summary

This document presents the design, mathematical formulation, empirical protocol, and empirical findings for **Candidate Thematic Unit (CTU) Schema V1** under **RC-009B**. 

CTUs are operational computational objects discovered purely from canonical symbolic score data without human theme annotations, role-conditioning, or generative labels.

---

## 1. Scientific Objective & Integrity Safeguards

The goal of RC-009B is to discover operational thematic units within symbolic piano scores and empirically evaluate whether these candidate units show statistically significant higher **future recurrence and developmental reuse** in a temporally held-out region compared to matched random negative control segments from the same piece.

### Integrity & Independence Invariants
1. **Zero Human Ground Truth Leakage**: Human theme annotations (e.g. from RC-008) were **NOT** used for training, hyperparameter tuning, candidate selection, thresholding, or validation.
2. **Temporal Split Anti-Leakage**: Each piece with at least 12 complete measures is chronologically split into:
   - **Discovery Region**: First 60% of complete measures ($[0, \text{discovery\_measures})$).
   - **Future Validation Region**: Last 40% of complete measures ($[\text{discovery\_measures}, \text{total\_measures})$).
   No information from the future validation region influenced candidate generation, similarity weights, candidate filtering, or ranking.
3. **Role-Blind Discovery**: Scores were processed without composer, style, or group labels. Corpus metadata was attached solely post-hoc for summary reporting.
4. **Polyphonic Texture Respect**: Pitch and interval evidence maintains separate `(staff, voice)` streams without collapsing multi-voice textures into a single top-note pseudo-melody or assuming `staff == hand`.

---

## 2. Mathematical Formulations & Component Definitions

### A. Candidate Generation & Multi-Scale Sliding Windows
For a piece with $M_{\text{disc}}$ discovery measures, candidate segments are generated across multi-scale measure durations $W \in \{1, 2, 3, 4, 6, 8\}$ with stride $s = 1$ measure:
$$
\text{Candidate Span } S = [m_{\text{start}}, m_{\text{end}}) \quad \text{where } m_{\text{end}} - m_{\text{start}} \in W, \; m_{\text{end}} \le M_{\text{disc}}
$$

### B. Segment Representation Vector $\mathbf{R}(S)$
Each candidate segment $S$ is converted to a multi-channel symbolic representation:
1. **Melodic Interval Channel**: Vector of pitch interval transitions $\Delta p = p_{i+1} - p_i$ within each `(staff, voice)` stream.
2. **IOI Rhythm Channel**: Vector of Inter-Onset-Interval ratios $r_i = \text{IOI}_{i+1} / \text{IOI}_i$.
3. **Texture Channel**: Vector of note attack simultaneities $a(t)$ at each distinct onset time $t$.
4. **Pitch-Class Channel**: 12-dimensional pitch class distribution vector normalized by total attacks.

### C. Pairwise Recurrence & Composite Discovery Score
For two non-overlapping discovery segments $S_A, S_B \subset [0, M_{\text{disc}})$, component similarities are computed:
- **Melodic Similarity** $Sim_{\text{mel}}$: Normalized interval n-gram Jaccard similarity.
- **Rhythmic Similarity** $Sim_{\text{rhy}}$: Normalized IOI ratio n-gram Jaccard similarity.
- **Texture Similarity** $Sim_{\text{tex}}$: Cosine similarity over attack simultaneity distributions.
- **Pitch-Class Similarity** $Sim_{\text{pc}}$: Cosine similarity over 12-bin pitch-class vectors.

The composite discovery recurrence score is defined as:
$$
S_{\text{disc}}(S_A, S_B) = w_{\text{mel}} Sim_{\text{mel}} + w_{\text{rhy}} Sim_{\text{rhy}} + w_{\text{tex}} Sim_{\text{tex}} + w_{\text{pc}} Sim_{\text{pc}}
$$
where $w_{\text{mel}}=0.40, w_{\text{rhy}}=0.30, w_{\text{tex}}=0.15, w_{\text{pc}}=0.15$ (all declared as `ENGINEERING_HEURISTIC`).

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
- $C_i$ contains note attacks (non-empty).

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
- **Paired Effect Size**: Cohen's $d = \frac{\bar{\Delta}}{s_{\Delta}}$
- **Bootstrap 95% Confidence Interval**: 10,000 resamples of piece-level paired differences $\Delta_p$.
- **Two-Tailed Paired Permutation Test**: 10,000 sign-flip permutations of $\Delta_p$.

---

## 4. Empirical Corpus Results

### Pipeline Execution Summary
- **Manifest Hash**: `cc94004e6003e60e863faec8fdb0eb2451f2802d334542fb44967341dbdf8bc2`
- **CTU Schema Version**: `1`
- **Total Ingested Pieces**: 141
- **Eligible Pieces ($\ge 12$ measures)**: 141
- **Ineligible Pieces ($< 12$ measures)**: 0
- **Raw Candidate Windows Generated**: 40,837
- **Post-NMS Retained CTUs**: 705 (5 CTUs per piece retained)
- **Matched Control Segments**: 705

### Statistical Validation Outcome
- **Mean CTU Future Reuse Score**: **0.8156**
- **Mean Control Future Reuse Score**: **0.7435**
- **Mean Paired Difference ($\bar{\Delta}$)**: **+0.0721**
- **Paired Effect Size (Cohen's d)**: **0.5540** (Medium-to-large effect)
- **95% Bootstrap Confidence Interval**: **[0.0512, 0.0935]**
- **Permutation Test p-value**: **< 0.0001 (0.0000)**
- **Positive Effect Fraction**: **75.18%** (106 out of 141 pieces showed higher CTU future reuse than matched controls)

---

## 5. Lineage Hashes

| Lineage Component | Hash / Identifier |
| :--- | :--- |
| **CTU Schema Version** | `1` |
| **CTU Schema Semantic Hash** | `d4e5f298a0113c299c855a0224218ebf9dbb5d5b6a7ae8cecd8f2fb2167d4aa1` |
| **Segment Representation Hash** | `91e8b7c4d51a660a9e73551db8c1f9644d7159c77e77b4d1b7ef8d2777174db4` |
| **Discovery Policy Hash** | `7d74aa78932ef2828ed7bbdfcf15ab5df200bcab22b404dcd695e17edae52f95` |
| **Validation Policy Hash** | `f6bc5a6fef95b1cd5b0e8b2dfa66699a71221adab5dbceef981263bbce30fa91` |

---

## 6. Official Scientific Outcome Statement

$$
\boxed{\mathbf{EMPIRICAL\ CTU\ STATUS = CTU\_VALIDATED}}
$$

### Scientific Interpretation
Unsupervised Candidate Thematic Units (CTUs) discovered solely within the initial 60% discovery region of canonical symbolic scores exhibit statistically significant, medium-to-large higher future-reuse scores in the temporally held-out 40% region ($p < 0.0001, d = 0.5540, 95\%\text{ CI } [0.0512, 0.0935]$) compared to matched random negative control segments.

*Note: `CTU_VALIDATED` is an operational computational status confirming higher future recurrence/developmental reuse under frozen V1 semantics. It does NOT imply human musicological theme adjudication or ground truth consensus.*
