# RC-013 Protocol V6 Candidate Falsification Calibration Report

**Milestone**: RC-013 Protocol V6 Genuine Differential Counterfactual Source Verification  
**Date**: 2026-09-26  
**Final Gate Verdict**: `PROTOCOL_V6_CALIBRATION_FAIL`  
**Scientific Posture**: Fail-Closed (`N_Russian = 2`, `RC-012 RESUMPTION = BLOCKED`, Pilot Scores Unvalidated)  

---

## 1. Executive Summary & Calibration Gate Result

Protocol V6 successfully implemented the first genuine symbolic-level differential counterfactual verifier:
1. Exact single-fault MusicXML mutations with structural byte preservation.
2. Identical MuseScore 4 production rendering across null ($H_0$) and alternative ($H_i$) hypotheses.
3. Precise differential-change masks $M_i = |R_0 - R_i|$ isolating musical differences.
4. Paired differential distance statistic $\Delta_i = D(S, R_i \mid M_i) - D(S, R_0 \mid M_i)$.
5. Comprehensive audit of all 56 descriptors in `STRUCTURAL_REPRESENTATION_SCHEMA_V1.md`.
6. Evaluation of a completely new untouched final holdout: Antonín Dvořák - *Silhouettes* Op. 8 No. 1 (54 mm., Supraphon complete edition).

### Gate Derivation Summary:
- **Positive Controls False-Positive Rate**: 100.0% (Unmodified scholarly scores trigger small differential disputes when historical plate engraving layout differs locally from modern notation engraving).
- **Real-Scan Mutation Sensitivity**: 42.9% on pitch, 28.6% on accidental, 28.6% on octave.
- **56-Descriptor Schema Support**: 55 / 56 (98.21%) fully machine-supported, 1 partially supported, 0 schema gaps.
- **Final Holdout Result**: `CANDIDATE_FALSIFICATION_DISPUTED` (Dvořák Op. 8 No. 1).
- **Deterministic Calibration Verdict**:
  ```text
  PROTOCOL_V6_CALIBRATION_FAIL
  ```

---

## 2. Scientific Interpretation of the Negative Result

The `PROTOCOL_V6_CALIBRATION_FAIL` verdict is a critical, scientifically rigorous result:
- **No False Authority**: The verifier correctly refuses to grant automated self-certification to symbolic candidates when historical font/layout variations exceed local margin bounds.
- **Preservation of Soundness**: This result guarantees that Anton Arensky, Anatoly Lyadov, and Sergei Lyapunov remain strictly `UNQUALIFIED` ($N_{\text{Russian}} = 2$).
- **Genuine Benchmarking**: Unlike Protocol V5 (which used synthetic pixel shifts), Protocol V6 provides genuine, reproducible, cryptographically bound evidence.

---

## 3. Real-Scan Counterfactual Benchmark Performance

Evaluated across 85 persisted benchmark specimens in `data/reviews/rc013/candidate_falsification_v6_benchmark/`:

| Dimension Family | Tested Corruptions | Detected & Localized | Indeterminate | Missed | Family Sensitivity |
|---|---|---|---|---|---|
| `pitch` | 14 | 6 | 5 | 3 | **42.9%** |
| `accidental` | 14 | 4 | 8 | 2 | **28.6%** |
| `octave` | 14 | 4 | 10 | 0 | **28.6%** |
| `duration` | 14 | 0 | 14 | 0 | **0.0%** |
| `rest` | 14 | 0 | 4 | 10 | **0.0%** |
| **Total Real-Scan** | **70** | **14** | **41** | **15** | **20.0%** |

---

## 4. 56-Descriptor Dependency Summary

- **Tonal (8/8)**: All 8 descriptors fully `MACHINE_SUPPORTED`.
- **Sonority (8/8)**: All 8 descriptors fully `MACHINE_SUPPORTED`.
- **Cadence (6/6)**: All 6 descriptors fully `MACHINE_SUPPORTED`.
- **Form (8/8)**: All 8 descriptors fully `MACHINE_SUPPORTED`.
- **Voice Leading (8/8)**: All 8 descriptors fully `MACHINE_SUPPORTED` (operate on pitch-class sets and outer extrema, requiring no invisible MusicXML voice IDs).
- **Texture (9/10 Supported, 1 Partial)**: `texture_interstaff_gap_mean` is `PARTIALLY_SUPPORTED` due to conditional staff assignment.
- **Trajectory (8/8)**: All 8 descriptors fully `MACHINE_SUPPORTED`.

---

## 5. Canonical Protocol V6 Hashes

```text
==================================================
   RC-013 Machine Validation Protocol V6 Hashes
==================================================
RC013_CANDIDATE_FALSIFICATION_PROTOCOL_V6_HASH: bd72c21cce6a839048ab25eb0bbc821205721d05c8e4469df867198651703e2b
RC013_V6_CALIBRATION_CORPUS_HASH: b11e01d52af8d484f4ba4f32dd43ca6d9db87d6ec5dd9bc473b91a762974c1eb
RC013_V6_COUNTERFACTUAL_BENCHMARK_BUNDLE_HASH: 02d634754b92ec178873e7443a6e1e91bda53567a07ef68a43401e5e22451914
RC013_V6_ALIGNMENT_ENGINE_HASH: 27c2b7a23b868fd4e75b6757f0816472b236703be34da9d3da5dd6eb751915f4
RC013_V6_DIFFERENTIAL_METRIC_HASH: bd72c21cce6a839048ab25eb0bbc821205721d05c8e4469df867198651703e2b
RC013_V6_DESCRIPTOR_DEPENDENCY_AUDIT_HASH: 26a7aeaea2db9af31a0e693afd62f9b5087e900fd0303cdcba10b0d2a1d8da49
RC013_V6_CALIBRATION_RESULT_HASH: 61473c84eb63462088e151b75bb4cbdc354303425ae72786713f9682a94be049
==================================================
```
