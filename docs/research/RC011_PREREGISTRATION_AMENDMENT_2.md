# RC-011 Preregistration Amendment 2: Final Scientific Contract & Metamorphic Validation Repair

**Document Version**: 2.0.0  
**Timestamp**: 2026-09-19T23:55:00Z  
**Preregistration Target**: RC-011 Theory-Grounded Structural Music Representation Foundation (RC-011B)  
**Preceding Preregistration Commits**:
- Original Preregistration: `ad3299e0f36f4fb028a2f5125a88b19361504d27`
- Preregistration Amendment 1: `d9881562a9a206629544681a96b13d99a819cf56`  
**Master Baseline**: `53fcecef76598c50e62d7f6cac6c86d9730cedbf`  
**Canonical Manifest SHA-256**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`  

---

## 1. Trigger, Motivation & Scientific Integrity Declaration

This amendment was triggered by the final scientific contract audit of RC-011A.
While RC-011A corrected mathematical formulas and module dependencies, the audit identified critical contract gaps in validation design, time-dilation semantics, cadence boundary/resolution logic, voice-leading assignment metrics, and CTU recurrence selection.

In strict adherence to the project's scientific integrity charter:
1. **Amendment 1 Preserved**: Amendment 1 remains intact and preserved in git history.
2. **Zero Style/Label Inspection**: No Russian vs. Control labels, composer nationalities, corpus roles, or style metadata were inspected, conditioned upon, or referenced.
3. **Zero Predictive Optimization**: No classifier metrics, feature selection procedures, ROC-AUC values, or classification coefficients motivated any algorithmic or parameter change.
4. **Invalidation of RC-011A Results**: All RC-011A full-corpus matrices, validation result hashes, and lineage bundle hashes are formally **invalidated and superseded**.
5. **Fresh Complete Execution**: RC-011B is executed completely from scratch after this amendment is committed.

---

## 2. Metamorphic Test Matrix & Non-Vacuous Fixture Mapping

To eliminate vacuous validation (e.g., verifying `0.0 == 0.0` on unavailable or structural-zero features evaluated solely on Fixture A), RC-011B establishes an immutable `METAMORPHIC_TEST_MATRIX`. Every feature $\times$ transformation is mapped to a synthetic fixture where the targeted musical construct is actively present and meaningfully evaluable:

- **Family A (Tonal)**: Evaluated on **Fixture A** (baseline C major) and **Fixture C** (tonal modulation).
- **Family B (Sonority)**: Evaluated on **Fixture G** (block chords, dense sonorities), **Fixture D** (chromatic clusters, IC1/IC6 dyads), and **Fixture A** (harmonic rhythm).
- **Family C (Cadence)**: Evaluated on **Fixture E** (authentic cadence) and **Fixture F** (deceptive motion).
- **Family D (Form)**: Evaluated on **Fixture N** (ABA recurrence) and **Fixture O** (through-composed control).
- **Family E (Voice Leading)**: Evaluated on **Fixture K** (parallel motion), **Fixture L** (contrary motion), and **Fixture M** (oblique motion).
- **Family F (Texture & Register)**:
  - Arpeggiation evaluated on **Fixture H** (rapid figuration).
  - Repeated notes evaluated on **Fixture I** (rapid motoric repetitions).
  - Block chords evaluated on **Fixture G** (synchronous multi-voice attacks).
  - Octave doublings evaluated on **Fixture J** (multi-octave parallel doubling).
  - Interstaff gap evaluated on **Fixture G** (two-staff texture).
- **Family G (Temporal Trajectory)**: Evaluated on **Fixtures P, Q, R, S, T** (8-measure scores with full 8-bin population across ascending, descending, stable, sparse-to-dense, and dense-to-sparse profiles).

---

## 3. Corrected Time-Dilation Semantics & Invariance Contract

Under $\times 2$ time dilation, absolute-tempo/duration thresholds interact differently with continuous musical representations:
1. **Absolute IOI / Duration Threshold Features**:
   - `texture_arpeggiation_proxy_rate`: Employs an absolute threshold ($\text{IOI} \le 0.5$ quarter notes). Under $\times 2$ notation dilation, former eighth-note attacks become quarter-note attacks ($\text{IOI} = 1.0$), disqualifying them from the rapid figuration threshold. This feature is frozen as **`SENSITIVE_BY_DESIGN`** under `TIME_DILATION`.
   - `texture_repeated_note_attack_rate`: Employs an absolute threshold ($\Delta t \le 0.5$ quarter notes). Under $\times 2$ dilation, repetitions at $\text{IOI}=1.0$ quarter notes exceed the threshold. This feature is frozen as **`SENSITIVE_BY_DESIGN`** under `TIME_DILATION`.
2. **Cadence Family & Rest Cues**:
   - Boundary candidates evaluated with relative IOI lengthening ($\text{IOI} \ge 1.5 \times \text{local median IOI}$) are scale-invariant. However, absolute rest cues ($\ge 0.5$ quarter notes) are duration-sensitive. Boundary candidate rate and tonic resolution rate are frozen as **`INVARIANT`** on normalized relative fixtures without boundary-crossing rests, and **`SENSITIVE_BY_DESIGN`** where absolute rest thresholds apply.
3. **Measure-Normalized Timing Quantities**:
   - In `sonority.py` and `trajectory.py`, score measure position calculations strictly use normalized offset within the actual measure:
     $$\text{norm\_offset} = \frac{\text{offset\_in\_measure}}{\text{actual\_measure\_duration}}$$
     ensuring that binning and measure-relative transition distances remain mathematically invariant under dilation.

---

## 4. Sensitive-By-Design Validation Enforcement

No test may auto-pass with an unverified `passed = True`. For every contract marked `SENSITIVE_BY_DESIGN`:
- An explicit, dedicated verification relation is evaluated.
- **Staff Swap for `texture_interstaff_gap_mean`**: Evaluated on two-staff Fixture G. Because interstaff gap is defined as $\min(\text{Staff 1}) - \max(\text{Staff 2})$, swapping Staff 1 $\leftrightarrow$ Staff 2 inverts the vertical ordering. The test explicitly verifies that the value changes sign or shifts from positive to negative ($\text{val}_{\text{trans}} < 0 < \text{val}_{\text{orig}}$).
- **Time Dilation for `texture_arpeggiation_proxy_rate` and `texture_repeated_note_attack_rate`**: The test explicitly verifies that dilating $\text{IOI} = 0.5 \to 1.0$ causes the rate to drop strictly to $0.0$, confirming the absolute threshold gate operates as designed.

---

## 5. Rich Metamorphic Records & Comprehensive Validation Hash

Every metamorphic execution produces an immutable record containing:
- `feature_id`
- `fixture_id`
- `transformation`
- `transformation_parameter`
- `original_value`, `original_status`, `original_reason`
- `transformed_value`, `transformed_status`, `transformed_reason`
- `expected_behavior` (`INVARIANT`, `EQUIVARIANT`, `SENSITIVE_BY_DESIGN`, `NOT_APPLICABLE`)
- `expected_relation`
- `actual_relation`
- `passed` (boolean)

For `INVARIANT` features, passing strictly requires **both**:
1. Semantic value equality ($|\text{val}_{\text{orig}} - \text{val}_{\text{trans}}| < 10^{-4}$)
2. Availability status equality ($\text{status}_{\text{orig}} == \text{status}_{\text{trans}}$)

`VALIDATION_RESULT_HASH` cryptographically binds the complete list of assertion records, all metamorphic records, family statuses, coverage counts, and exclusion ledger hash. Any bit-flip or status mutation alters `VALIDATION_RESULT_HASH`.

---

## 6. Strengthened Synthetic Fixture Suite & Assertion Contract Hash

`SYNTHETIC_FIXTURE_SUITE_HASH` binds:
- Fixture IDs, measure counts, note counts
- Exact event lists (measure index, global onset, offset in measure, duration, midi, staff, voice)
- Family ownership
- Semantic hash of the fixture score

`SYNTHETIC_ASSERTION_CONTRACT_HASH` binds:
- Assertion IDs, fixture IDs, family ownership, condition descriptions, expected relational operators.

---

## 7. Cadence Contract Precision

1. **Measure-Based Local IOI Reference Window**:
   - Local median IOI is computed from all note onsets within the measure-distance window:
     $$|m - m_{\text{target}}| \le 4 \text{ measures}$$
     rather than arbitrary onset counts.
2. **Exact Fractional Rest Evidence**:
   - Rest evidence requires an explicit sounding gap $\ge 0.5$ quarter notes (`Fraction(1, 8)` score time in 4/4):
     $$\text{gap} = t_{\text{next\_onset}} - \max_{n \in \text{onset}}(n.\text{global\_onset} + n.\text{duration}) \ge \text{Fraction}(1, 8)$$
   - Minor positive gaps $< 0.5$ quarter notes do not trigger the rest cue.
3. **Local Tonal Degree Resolution**:
   - `cadence_tonic_resolution_rate` increments **only** when the bass moves to scale degree $\hat{1}$ from dominant degree $\hat{5}$ or leading tone $\hat{7}$ relative to the local tonic estimated in $[m-4, m]$. Arbitrary fourth/fifth bass movement outside a tonic-relative resolution is rejected.

---

## 8. Optimal Transport / Bipartite Voice-Leading Assignment

To adhere strictly to Tymoczko's minimal voice-leading displacement theory for unequal cardinalities without ad-hoc symmetric nearest-neighbor approximations:
- Let pitch-class sets be $A$ and $B$ with cardinalities $|A|=n_1, |B|=n_2$.
- Let $L = \text{lcm}(n_1, n_2)$.
- Expand multiset $A^*$ by repeating each element of $A$ exactly $L / n_1$ times.
- Expand multiset $B^*$ by repeating each element of $B$ exactly $L / n_2$ times.
- Solve the exact minimum-cost bipartite assignment on cost matrix $C_{ij} = d_{\mathbb{Z}_{12}}(a^*_i, b^*_j)$ using `scipy.optimize.linear_sum_assignment`.
- Normalize total assignment cost by $L$:
  $$D(A, B) = \frac{1}{L} \sum_{k=1}^L d_{\mathbb{Z}_{12}}(a^*_k, b^*_{\pi(k)})$$
- This provides an exact, symmetric, transposition-equivariant optimal transport distance over $\mathbb{Z}_{12}$.

---

## 9. Full-Piece CTU Occurrence Selection & Recurrence Dispersion

For every retained CTU from the initial 60% discovery partition:
1. Candidate matching windows of length `span_measures` are scanned across the entire score ($100\%$).
2. Candidate matches with similarity $\ge 0.82$ are ranked deterministically:
   - Similarity descending
   - Measure start position ascending
3. Non-overlapping suppression selects occurrences pairwise such that no two accepted occurrences overlap in measure span.
4. `form_ctu_recurrence_dispersion` computes the standard deviation of normalized start positions across all accepted occurrences.
5. **Availability Rule**: `form_ctu_recurrence_dispersion` is `AVAILABLE` if and only if $\ge 2$ occurrence positions exist across the score; otherwise it evaluates to `STRUCTURAL_ZERO` with reason `"Fewer than 2 CTU occurrences found"`.

---

## 10. Prior-Milestone Dynamic Verification & Lineage Binding

1. `CTUDiscoveryPolicy().compute_policy_hash()` is dynamically computed and verified against accepted hash `df0810aa9601131df59e1341d6281ce339e1d97b8c993d0baf453fa4a31f0367`.
2. Full candidate set hash is dynamically computed across all 141 scores and verified against `43fda7ba9503df0650fa4e2fb03ff897452a90adf225650d2d785d71a6f6ba8d`.
3. `PREREGISTRATION_AMENDMENT_HASH` is dynamically computed at runtime from the UTF-8 bytes of this file (`RC011_PREREGISTRATION_AMENDMENT_2.md`).
4. Two-process verification script transmits complete payloads (piece IDs, feature names, matrix data, availability statuses, availability reasons, fixture records, assertion records, all metamorphic records, family statuses, coverage counts, and lineage hashes) and asserts direct structural equality (`payload_a == payload_b`) before hash comparison.
