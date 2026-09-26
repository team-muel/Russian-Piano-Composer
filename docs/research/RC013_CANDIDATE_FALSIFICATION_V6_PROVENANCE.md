# RC-013 Protocol V6 Provenance & Calibration Audit Trail

**Milestone**: RC-013 Protocol V6 Genuine Differential Counterfactual Source Verification  
**Date**: 2026-09-26  
**Status**: `PROTOCOL_V6_CALIBRATION_FAIL` (Fail-Closed Valid Negative Scientific Gate)  
**Schema Version**: 1 (56 Frozen Descriptors across 7 Families)  

---

## 1. Protocol Hashes & Digital Lineage

All hashes are derived deterministically from persisted bytes on disk:

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

---

## 2. Calibration Targets Provenance

| Artifact ID | Composer | Work | Edition / Source | Split | Measures |
|---|---|---|---|---|---|
| `chopin_op28_no07` | F. Chopin | Prélude Op. 28 No. 7 | Controlled Baseline | Synthetic Baseline | 16 |
| `chopin_op28_no20` | F. Chopin | Prélude Op. 28 No. 20 | Controlled Baseline | Synthetic Baseline | 13 |
| `bach_bwv846_prelude` | J. S. Bach | WTC I Prelude BWV 846 | Controlled Baseline | Synthetic Baseline | 35 |
| `chopin_mazurka_op06_no01` | F. Chopin | Mazurka Op. 6 No. 1 | Joseffy / Schirmer 1915 | Real Scan Calibration | 75 |
| `chopin_mazurka_op07_no01` | F. Chopin | Mazurka Op. 7 No. 1 | Joseffy / Schirmer 1915 | Real Scan Calibration | 64 |
| `chopin_mazurka_op17_no01` | F. Chopin | Mazurka Op. 17 No. 1 | Joseffy / Schirmer 1915 | Real Scan Calibration | 61 |
| `grieg_lyric_pieces_op12_no01` | E. Grieg | Arietta Op. 12 No. 1 | Peters Gesamtausgabe | Real Scan Calibration | 23 |
| `schumann_kinderszenen_op15_no01` | R. Schumann | Op. 15 No. 1 | Clara Schumann / B&H 1879 | Real Scan Calibration | 22 |
| `dvorak_silhouettes_op08_no01` | A. Dvořák | Silhouettes Op. 8 No. 1 | Complete Edition / Supraphon | **New Final Holdout** | 54 |

---

## 3. Persisted Counterfactual Benchmark Artifacts

The Protocol V6 benchmark bundle is persisted under `data/reviews/rc013/candidate_falsification_v6_benchmark/` containing 85 individual JSON specimens. Every specimen cryptographically logs:
- `specimen_id`
- `base_score_id` & `base_score_sha256`
- `mutation_dimension`, `target_measure`, `original_value`, `mutated_value`
- `mutated_xml_sha256`, `h0_render_sha256`, `hi_render_sha256`
- `source_crop_sha256`, `difference_mask_sha256`
- `d0`, `di`, `delta`, `delta_norm`
- `predicted_status`, `ground_truth_mutation_status`, `is_correctly_localized`
