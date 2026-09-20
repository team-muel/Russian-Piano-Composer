# RC-011 Preregistration Amendment 3: Semantic-Lineage Identity, Cadence Dilation Contract, and Non-Vacuous Metamorphic Testing

**Document Identifier**: `RC011_PREREGISTRATION_AMENDMENT_3`  
**Milestone**: RC-011 Theory-Grounded Structural Music Representation Foundation  
**Preceding Preregistration**: `docs/research/RC011_PREREGISTRATION.md` (`ad3299e0f36f4fb028a2f5125a88b19361504d27`)  
**Preceding Amendments**: 
- Amendment 1: `docs/research/RC011_PREREGISTRATION_AMENDMENT_1.md` (`d9881562a9a206629544681a96b13d99a819cf56`)
- Amendment 2: `docs/research/RC011_PREREGISTRATION_AMENDMENT_2.md` (`973ca6eddeba03163542a6d34293e261d67f0977`)  
**Branch**: `rc/011-theory-grounded-structural-representation`  
**Date**: 2026-09-20  

---

## 1. Scientific Integrity Declaration & Motivation

1. **Zero Class / Style Label Motivation**:
   No class, style, nationality, or corpus role (`GENERATIVE_RUSSIAN`, `CONTROL_NON_RUSSIAN`) information motivated this amendment. RC-011 remains strictly an objective, label-blind symbolic representation foundation.
2. **No Empirical Metric Optimization**:
   The feature values and corpus representation matrix computed in RC-011B are not being tuned, selected, or optimized for downstream discriminative separation or generative scoring.
3. **Purpose of Amendment 3**:
   This amendment addresses:
   - **Invariance Truthfulness**: The Cadence family contains an absolute sounding rest threshold ($\text{gap} \ge 0.5$ quarter notes), which causes boundary candidates to appear or disappear under uniform notation-duration dilation. Declaring these features universally invariant under time dilation was scientifically untruthful. They are formally preregistered as `SENSITIVE_BY_DESIGN` under `TIME_DILATION`.
   - **Elimination of Generic Auto-Pass**: Metamorphic checks for `SENSITIVE_BY_DESIGN` must verify explicit expected behavioral relations (such as predicted threshold-crossing direction) rather than using generic `passed = True` branches.
   - **Non-Vacuous Metamorphic Fixture Suite**: Trajectory and textural features are bound to dedicated synthetic fixtures with active, non-zero musical constructs (non-zero span slopes, chromatic gradients, density curvatures), and the test matrix mapping is frozen under `METAMORPHIC_TEST_MATRIX_HASH`.
   - **Deep Algorithm Semantic Hashes**: Disassociating numeric parameter policies from algorithmic semantics by introducing formal `SEMANTIC_HASH` descriptors for all 7 families, binding operational mathematical choices (e.g., Tymoczko LCM optimal transport, 12-D SSM recurrence, local-tonic authentic resolution).
   - **Implementation Source & Commit Lineage**: Cryptographically binding normalized source code bytes (`STRUCTURE_ANALYSIS_SOURCE_HASH`) and implementation commit SHAs (`RC011_IMPLEMENTATION_COMMIT_SHA`) into the lineage bundle.
4. **Superseded Hashes**:
   Previous RC-011B validation result hashes and lineage bundle hashes are formally superseded by the tightened contracts established herein.

---

## 2. Cadence Time-Dilation Contract Repair

In `cadence.py`, cadential boundaries are identified via two primary criteria:
1. Significant local IOI lengthening relative to local context.
2. Sounding rest gap $\ge 0.5$ quarter notes (`Fraction(1, 8)` in whole-note units).

Under uniform duration scaling ($t \mapsto \alpha t$ with $\alpha > 1$):
- Relative IOI ratios are invariant.
- Absolute rest durations scale by $\alpha$. A rest gap $g < 0.5$ quarter notes may become $\alpha g \ge 0.5$ quarter notes, creating a new cadential boundary candidate where none existed before.

### Truthful Contract
All 6 cadence features are declared `SENSITIVE_BY_DESIGN` under `TransformationType.TIME_DILATION`:
- `cadence_boundary_candidate_rate`
- `cadence_boundary_strength_mean`
- `cadence_tonic_resolution_rate`
- `cadence_dominant_tonic_proxy_rate`
- `cadence_deceptive_proxy_rate`
- `cadence_resolution_strength_mean`

### Adversarial Verification Fixture
An explicit synthetic fixture is preregistered containing a rest gap of $0.375$ quarter notes (below threshold) that, under dilation by $2\times$, scales to $0.75$ quarter notes (above threshold). The metamorphic test explicitly verifies that the candidate set and rates change predictably in response to crossing the threshold.

---

## 3. Strict Metamorphic Evaluation (No Auto-Pass)

For all metamorphic checks:
1. `INVARIANT`: $|v_{\text{trans}} - v_{\text{orig}}| < \epsilon$ and $\text{status}_{\text{trans}} == \text{status}_{\text{orig}}$.
2. `EQUIVARIANT`: $v_{\text{trans}} == v_{\text{orig}} + \Delta$ and $\text{status}_{\text{trans}} == \text{status}_{\text{orig}}$.
3. `SENSITIVE_BY_DESIGN`:
   - If evaluated on an adversarial threshold-crossing or sensitivity-proving fixture: the check MUST evaluate a concrete directional or difference assertion (e.g. $v_{\text{trans}} > v_{\text{orig}}$ or $|v_{\text{trans}} - v_{\text{orig}}| > 0$).
   - If evaluated on a general fixture where no deterministic constraint exists beyond possible change: the test record reports status `NOT_APPLICABLE` rather than auto-passing.

---

## 4. Non-Vacuous Metamorphic Test Matrix

The metamorphic suite assigns each feature to a fixture exhibiting the active musical construct:
- **Trajectory Features**: Evaluated on fixtures with distinct registral span expansion, chromatic saturation gradients, or parabolic attack densities (Fixtures P, Q, R, S, T, and dedicated trajectory/cadence fixtures U and V).
- The mapping between feature ID and fixture ID is frozen and cryptographically hashed:
  $$\text{METAMORPHIC\_TEST\_MATRIX\_HASH} = \text{SHA-256}(\text{canonical\_json}(\text{feature\_fixture\_map}))$$

---

## 5. Algorithmic Semantic Hashes vs. Parameter Policy Hashes

Lineage distinguishes between:
1. **Parameter Policy Hashes** (`PARAMETER_POLICY_HASH`): Hashes of configuration parameter dataclasses.
2. **Algorithm Semantic Hashes** (`SEMANTIC_HASH`): Canonical JSON descriptors specifying:
   - Algorithm version and mathematical framework.
   - Exact operational definitions and equations.
   - Core mathematical operators (e.g., Hungarian assignment, LCM expansion, Pearson correlation, Cosine SSM).
   - Normalization bases and windowing strategies.
   - Availability and structural-zero decision trees.

The seven semantic hashes are:
- `TONAL_SEMANTIC_HASH`
- `SONORITY_SEMANTIC_HASH`
- `CADENCE_SEMANTIC_HASH`
- `FORM_SEMANTIC_HASH`
- `VOICE_LEADING_SEMANTIC_HASH`
- `TEXTURE_SEMANTIC_HASH`
- `TRAJECTORY_SEMANTIC_HASH`

---

## 6. Implementation Source Hash & Two-Process Payload Integrity

To prevent silent divergence between specification and implementation:
1. **Source Hash**:
   $$\text{STRUCTURE\_ANALYSIS\_SOURCE\_HASH} = \text{SHA-256}\left(\bigoplus_{f \in \mathcal{F}} \text{read\_utf8\_crlf\_normalized}(f)\right)$$
   over `tonal.py`, `sonority.py`, `cadence.py`, `form.py`, `voice_leading.py`, `texture.py`, `trajectory.py`, `extractor.py`, and `schema.py`.
2. **Two-Process Verification**:
   The payload transmitted between independent subprocesses includes:
   - Full fixture records (fixture IDs, semantic hashes, canonical payloads).
   - All prior milestone dynamic hashes.
   - All seven family semantic hashes.
   - Metamorphic test matrix hash.
   - Structure analysis source hash.
   - Implementation commit SHA.
   Direct equality `payload_A == payload_B` is strictly asserted prior to hash comparison.
