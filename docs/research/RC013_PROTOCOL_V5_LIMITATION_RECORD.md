# RC-013 Protocol V5 Limitation Record & Scientific Evaluation

**Date**: 2026-09-26  
**Status**: `PROTOCOL_V5_CALIBRATION_FAIL` (Formally Retained as Failed Exploratory Calibration)  
**Authority**: RC-013 Verification Architecture Group  

---

## 1. Overall Calibration Verdict

```text
PROTOCOL_V5_CALIBRATION_FAIL
```

Protocol V5 made a fundamental conceptual breakthrough by shifting the verification paradigm from **unassisted blind full-score OMR retranscription** (Protocols V1–V4) to **candidate-conditioned counterfactual falsification**. However, a rigorous forensic audit of the implementation has identified multiple methodological shortcuts and approximations that invalidate V5's specific performance claims.

---

## 2. Scientifically Retained Concepts

The following conceptual foundation of Protocol V5 remains valid and is carried forward into Protocol V6:

1. **Candidate-Conditioned Falsification Paradigm**: The core question is not whether an OMR engine can reconstruct an entire complex historical plate from scratch, but rather: *Given an authentic symbolic candidate and an authoritative historical scan, does the historical source support the candidate notation significantly more strongly than musically plausible competing hypotheses?*
2. **Discriminative Hypothesis Testing**: Formulating verification as a comparison between the null hypothesis $H_0$ (the candidate transcription) and alternative hypotheses $H_i$ (controlled counterfactual corruptions).
3. **Fail-Closed Gate Posture**: The overarching fail-closed principle ($N_{\text{Russian}} = 2$, `RC-012 RESUMPTION = BLOCKED`, no automated self-certification) is strictly preserved.

---

## 3. Invalidated Performance Claims in Protocol V5

The following empirical claims generated during Protocol V5 calibration are formally declared scientifically invalid:

1. **Claimed 27 / 27 (100.00%) True Real-Scan Counterfactual Sensitivity**:
   - *Reason for Invalidation*: Counterfactual hypotheses were generated via pixel image translation (`np.roll(..., shift_y, ...)`) rather than true symbolic notation rendering via MuseScore. An image shift does not reflect true glyph alterations, stem repositioning, accidental re-typesetting, or spacing dynamics.
2. **Claimed Dimension-Level Source-Fidelity Support**:
   - *Reason for Invalidation*: Single image shift tests were broadcast to multiple orthogonal musical dimensions (`pitch`, `accidental`, `octave`, `duration`, `rest`, `staff`, `voice`, `tie`, `meter`), violating dimension independence.
3. **Claimed 53-Descriptor Coverage & Dependency Audit**:
   - *Reason for Invalidation*: Evaluated an ad-hoc 53-feature subset rather than the exact frozen 56-descriptor specification defined in `docs/spec/STRUCTURAL_REPRESENTATION_SCHEMA_V1.md`.
4. **Empty Measure Auto-Support**:
   - *Reason for Invalidation*: Measures with no note events were assigned an automatic support margin (`best_margin = 0.50`, `SUPPORTED`) without empirical counterfactual testing.
5. **Real-Scan Counterfactual Benchmark Hash Lineage**:
   - *Reason for Invalidation*: The manifest benchmark hash hashed an empty payload (`e3b0c442...`) due to missing artifact persistence.

---

## 4. Specific Defect Inventory

| Defect ID | Description | Scientific Consequence |
|---|---|---|
| `DEF-V5-01` | `np.roll` image translation used as proxy for pitch/musical mutations | Fake visual counterfactuals; not rendered from modified symbolic notation. |
| `DEF-V5-02` | `_write_mutated_xml()` rebuilt simplified score rather than preserving original MusicXML byte structure | Risk of unintended global structural drift during single-event mutation. |
| `DEF-V5-03` | Proportional equal-width horizontal measure slicing | Inaccurate measure boundary localization on non-uniformly spaced historical systems. |
| `DEF-V5-04` | Single-measure result broadcast to all dimensions | False claim of multi-dimensional verification. |
| `DEF-V5-05` | Empty measures assigned `SUPPORTED` by default | Unvalidated musical space treated as verified. |
| `DEF-V5-06` | Feature dependency map based on 53 arbitrary descriptors | Schema mismatch with frozen RC-011 56-descriptor contract. |
| `DEF-V5-07` | Feature reliability coefficients defaulted to 1.0 | Uncalibrated downstream analysis eligibility claims. |
| `DEF-V5-08` | Benchmark bundle hash calculated over empty registry list | Cryptographic provenance broken in manifest. |

---

## 5. Protocol V6 Mandates

Protocol V6 directly resolves each of these limitations:
- True symbolic MusicXML single-fault mutations with strict XML delta isolation.
- Identical production engraving configuration for $H_0$ and $H_i$ via MuseScore 4.
- Exact differential-change masks ($M_i$) isolating the localized musical modification.
- Paired differential distance statistic $\Delta_i = D(S, R_i \mid M_i) - D(S, R_0 \mid M_i)$.
- Exact 56-descriptor dependency audit referencing `STRUCTURAL_REPRESENTATION_SCHEMA_V1.md`.
- Persisted benchmark specimens with complete cryptographic hashing.
- New untouched final holdout score (Dvořák Op. 8 No. 1) to replace previously observed Schumann Op. 15 No. 1.
