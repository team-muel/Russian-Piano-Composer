# RC-011 Preregistration Amendment 1: Structural Representation Scientific Contract Repair

**Document Version**: 1.0.0  
**Timestamp**: 2026-09-19T21:30:00Z  
**Preregistration Target**: RC-011 Theory-Grounded Structural Music Representation Foundation  
**Preceding Preregistration Commit**: `ad3299e0f36f4fb028a2f5125a88b19361504d27`  
**Master Baseline**: `53fcecef76598c50e62d7f6cac6c86d9730cedbf`  
**Canonical Manifest SHA-256**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`  

---

## 1. Trigger, Motivation & Scientific Integrity Declaration

This amendment was triggered by a rigorous scientific contract audit of the initial RC-011 implementation.
In strict accordance with the project's scientific integrity charter:
1. **Zero Style/Label Inspection**: No Russian vs. Control labels, composer nationalities, corpus roles, or style metadata were inspected or referenced during this repair.
2. **Zero Predictive Optimization**: No classifier metrics, feature selection procedures, ROC-AUC values, or classification coefficients motivated any algorithmic or parameter change.
3. **Invalidation of Provisional Extraction**: The provisional full-corpus RC-011 run (Matrix Hash: `5c537aa7fc...`, Validation Hash: `7329424d...`) is hereby **formally invalidated and superseded**.
4. **Pre-Execution Freeze**: All repaired semantics, formulas, policies, fixture definitions, and metamorphic invariants documented below are frozen in git ancestry **prior** to executing the repaired 141-piece full-corpus extraction.

---

## 2. Repaired Family Semantics & Frozen Policy Contracts

### 2.1 Family A — Tonal / Harmonic Center Proxies (8 Features)
- **Tonal Center Estimation**: Uses 24 Krumhansl-Kessler key profiles (12 major, 12 minor) with duration-weighted pitch-class distributions.
- **Local Tonal Window**: 8 measures with 1-measure stride.
- **Policy Parameters**:
  - `window_size_measures`: 8
  - `window_stride_measures`: 1
- **Transposition Invariance**: Strictly invariant under pitch-class transpositions $k \in \{-7, -5, +3, +5\}$.

### 2.2 Family B — Vertical Sonority & Harmonic Motion (8 Features)
- **Active Sounding Note Set**: At every note onset timepoint $t$, the active sounding note set is constructed using exact `Fraction` timing:
  $$\text{Active}(t) = \{n \in \text{Score} \mid n.\text{global\_onset} \le t < n.\text{global\_onset} + n.\text{duration}\}$$
  This includes sustained notes sounding across previous onsets.
- **Duration-Weighted Integration**: The duration of each vertical sonority slice is the exact time interval until the subsequent onset $t_{k+1} - t_k$ (or the final sounding note release for the last onset). Overlapping durations are never double-counted.
- **Mathematical Bounding**: All ratio and share features (`sonority_stable_duration_share`, `sonority_ic1_semitone_share`, `sonority_ic6_tritone_share`) are mathematically bounded to $[0.0, 1.0]$.
- **Bass-Relative Variety**: Normalized by distinct pitch-class intervals relative to bass, bounded in $[0.0, 1.0]$.
- **Policy Parameters**:
  - `top_pc_sets_count`: 3

### 2.3 Family C — Cadential & Boundary Proxies (6 Features)
- **Observable Boundary Criterion**: Evaluated at note onsets based on inter-onset interval (IOI) elongation and rest evidence:
  - $\text{IOI}(t) \ge 1.5 \times \text{LocalMedianIOI}(t)$ (local window of $\pm 4$ measures) OR presence of explicit rest $\ge 0.5$ quarter notes OR final measure event.
- **Local Tonal-Center Proxy**: Resolution scale-degree checks ($\hat{5} \to \hat{1}$ authentic resolution, $\hat{5} \to \hat{6}$ deceptive resolution) are evaluated relative to the local tonal center estimated in the preceding 4-measure window $[m-4, m]$.
- **Boundary Gap Rule**: `min_measure_boundary_gap = 1.0` measure. When multiple candidates occur within 1 measure, the highest-strength candidate is retained.
- **No Categorical Ground Truth**: Outputs are continuous rates and strength scores, avoiding categorical PAC/IAC labeling.
- **Policy Parameters**:
  - `boundary_ioi_ratio_threshold`: 1.5
  - `min_measure_boundary_gap`: 1.0

### 2.4 Family D — Formal Recurrence & Sectional Architecture (8 Features)
- **SSM Embedding Representation**: Measure-level embedding is strictly 12-dimensional pitch-class duration distribution:
  $$\vec{v}_m \in \mathbb{R}^{12}, \quad \vec{v}_m[p] = \sum_{n \in \text{Measure } m, \text{pc}(n)=p} \text{duration}(n)$$
  (Normalized to unit Euclidean length for cosine similarity).
- **Terminology Neutrality**: The initial formal region is designated `initial_reference_end_fraction = 0.20` (neutral, non-categorical naming).
- **CTU Formal Recurrence Across Full Piece**:
  - In RC-009B, discovery was restricted to the first 60% ($\tau \le 0.60$).
  - For each retained CTU $c$, the full piece ($100\%$) is scanned for non-overlapping matching segments using the frozen RC-009B multi-channel representation and similarity metric ($\text{sim} \ge 0.82$).
  - `form_ctu_first_occurrence_mean`: Mean discovery position $\tau_0 \in [0, 1]$.
  - `form_ctu_recurrence_dispersion`: Standard deviation of all occurrence positions across the full piece.
  - `form_ctu_late_return_presence`: $1.0$ if any non-overlapping matching occurrence starts in $\tau \ge 0.70$ (the final 30%), else $0.0$.
- **Policy Parameters**:
  - `similarity_threshold`: 0.80
  - `novelty_kernel_size`: 4
  - `late_return_start_fraction`: 0.70
  - `initial_reference_end_fraction`: 0.20

### 2.5 Family E — Voice-Leading Geometry (8 Features)
- **Deterministic Minimal Assignment Metric**: Minimal voice-leading distance between pitch-class sets $A$ and $B$ is computed via exact minimal bipartite matching / permutation assignment over $\mathbb{Z}_{12}$:
  $$D(A, B) = \min_{\pi} \frac{1}{\max(|A|, |B|)} \sum_i d_{\mathbb{Z}_{12}}(a_i, b_{\pi(i)})$$
  where for unequal cardinalities, the smaller set is duplicated / padded symmetrically.
  This satisfies symmetry $D(A, B) = D(B, A)$, zero identity $D(A, A) = 0$, and transposition equivariance $D(A+k, B+k) = D(A, B)$.
- **Outer Voice Motion Classification**: Parallel, contrary, and oblique motions are classified between soprano (highest) and bass (lowest) pitch lines.
- **Policy Parameters**:
  - `step_interval_max`: 2 semitones

### 2.6 Family F — Piano Texture & Registral Architecture (10 Features)
- **Arpeggiation Detector & Scale Control**:
  - `arpeggio_max_ioi`: $0.5$ quarter notes (`Fraction(1, 2)`).
  - Figuration runs require: $\ge 4$ attacks, intra-run $\text{IOI} \le 0.5$, pitch span $\ge 12$ semitones, and non-stepwise interval structure (runs with all adjacent intervals $\le 2$ semitones are classified as scalar runs and excluded from arpeggio counts).
- **Repeated-Note Attacks**: Consecutive note attacks on identical pitches are counted only when $\Delta t \le 0.5$ quarter notes (using exact `Fraction` timing).
- **Policy Parameters**:
  - `arpeggio_min_attacks`: 4
  - `arpeggio_min_span_semitones`: 12
  - `arpeggio_max_ioi`: 0.5

### 2.7 Family G — Normalized Temporal Trajectories (8 Features)
- **Precondition & Explicit Availability Rule**: The piece timeline is partitioned into 8 equal bins.
  If any bin contains 0 sounding notes (i.e. populated bins $< 8$), trajectory features require explicit `AvailabilityStatus.STRUCTURAL_ZERO` with reason string `"Only K/8 bins populated"`.
  Silent imputation of global means or zero values with `AVAILABLE` status is strictly prohibited.
- **Policy Parameters**:
  - `bin_count`: 8

---

## 3. Synthetic Fixture Suite (Fixtures A through T)

The synthetic fixture registry comprises exactly 20 deterministic fixtures:
1. **Fixture A**: Stable C-major I-IV-V-I progression (Tonal baseline)
2. **Fixture B**: Transposed equivalent of Fixture A (+7 semitones)
3. **Fixture C**: Tonal center transition (C major $\to$ G major)
4. **Fixture D**: Strongly chromatic cluster passage
5. **Fixture E**: Authentic cadence boundary proxy (V $\to$ I resolution with IOI lengthening)
6. **Fixture F**: Deceptive motion boundary proxy (V $\to$ VI resolution)
7. **Fixture G**: Homophonic block-chord texture
8. **Fixture H**: Arpeggiated version of Fixture G pitch material
9. **Fixture I**: Motoric repeated-note texture ($\Delta t \le 0.5$ quarters)
10. **Fixture J**: Multi-octave doubling texture
11. **Fixture K**: Parallel outer-voice motion (parallel tenths)
12. **Fixture L**: Contrary outer-voice motion (soprano ascends, bass descends)
13. **Fixture M**: Oblique outer-voice motion (soprano moves, bass pedal point)
14. **Fixture N**: ABA formal recurrence (A theme in M0-3, B contrast in M4-7, A return in M8-11)
15. **Fixture O**: Through-composed non-return formal control
16. **Fixture P**: Ascending registral trajectory (monotonic pitch centroid ascent across 8 bins)
17. **Fixture Q**: Descending registral trajectory (monotonic pitch centroid descent across 8 bins)
18. **Fixture R**: Stable registral trajectory (constant pitch centroid across 8 bins)
19. **Fixture S**: Sparse $\to$ Dense texture trajectory (attack density increases across 8 bins)
20. **Fixture T**: Dense $\to$ Sparse texture trajectory (attack density decreases across 8 bins)

Each fixture has a deterministic semantic hash and explicit, family-owned assertion records.
Per-family acceptance status (`PASS` / `PARTIAL` / `FAIL`) is dynamically computed from these assertion records.

---

## 4. Metamorphic Invariance Contract

Every feature $f \in [1..56]$ has an explicit behavioral contract across 6 transformation classes:
1. **Transposition** ($\Delta k \in \{-7, -5, +3, +5\}$): `texture_register_centroid_mean` is `EQUIVARIANT` (shifts by $k$); all other 55 features are `INVARIANT`.
2. **Time Dilation** ($\times 2$): All measure-normalized and dimensionless features are `INVARIANT`.
3. **Piece ID Rename**: All 56 features are `INVARIANT`.
4. **Source Relative Path Rename**: All 56 features are `INVARIANT`.
5. **Voice ID Rename**: All 56 features are `INVARIANT`.
6. **Staff Swap**: `texture_interstaff_gap_mean` is `SENSITIVE_BY_DESIGN` (inverts sign); all other 55 features are `INVARIANT`.

---

## 5. Summary of Amendment Hashes & Provenance

This document, once committed, establishes the cryptographic boundary for RC-011A.
The complete extraction pipeline will be executed cleanly against committed HEAD.
