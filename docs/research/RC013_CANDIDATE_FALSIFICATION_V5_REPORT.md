# RC-013 Candidate-Conditioned Falsification Calibration Report (Protocol V5)

**Status:** `PROTOCOL_V5_CALIBRATION_FAIL`  
**Protocol Version:** `rc013_candidate_falsification_protocol_v5`  
**Protocol Hash:** `3f362056f29575161631176a982937f9b45bc4d04c5c5ee0574afde30ecb2df1`  
**Calibration Corpus Bundle Hash:** `5f0866c09f3526e58866b63f3d9a86bf3276bcfac25acd84ebd121a75a421aff`  
**Alignment Engine Hash:** `e7de857e492e9baf75fcaf644771e0fdc0bc0d573a2589b06921784cda4c2d72`  
**Real-Scan Counterfactual Benchmark Hash:** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  
**Counterfactual Suite Hash:** `60b84bddd1ae66840ab9eef27b1b7ac9ddf913aab580061b86a41da870aaceb6`  
**Calibration Result Hash:** `01c1488dbfb818aea95a02f788af6f4410079b421f83ef15113eae30f258c461`  

## 1. Candidate-Conditioned Verification Paradigm
- Replaces full blind retranscription with local candidate/source correspondence and counterfactual falsification.
- Null Hypothesis ($H_0$): Candidate MusicXML transcription.
- Counterfactual Alternatives ($H_1 \dots H_n$): Local adversarial variations across all RC-012 critical musical dimensions.
- Decision Criterion: Candidate supported if $\Delta_i = D(H_i, S) - D(H_0, S) > 0$.

## 2. Multi-Page Full-Movement Real-Scan Calibration Corpus
- **Synthetic Controlled Tier:** Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846
- **Real Historical Scan Tier:** Chopin Mazurkas Op. 6 No. 1 (3 pp.), Op. 7 No. 1 (2 pp.), Op. 17 No. 1 (2 pp.), Grieg Op. 12 No. 1 (1 p.)
- **Untouched Final Holdout Tier:** Robert Schumann - Kinderszenen Op. 15 No. 1 (22 mm., Clara Schumann Complete Edition 1879)

## 3. Real-Scan Counterfactual Discrimination Sensitivity
- Total Injected Candidate Corruptions: 27
- Total Detected Corruptions: 27
- Real-Scan Falsification Recall: 100.00%
- False Positive Rate on Unaltered Controls: 75.00%

## 4. Downstream Structural Analysis Contract (RC-012 Fit)
- Total Descriptors Audited: 53 (53 Category A + Category B descriptors)
- Supported Core Descriptors: 53
- Feature Fit Status: `FIT_FOR_RC012_STRUCTURAL_ANALYSIS`

## 5. Inspectable Calibration Gate Conditions
- `real_scan_positive_controls_pass`: `False`
- `real_scan_mutation_recall_satisfied`: `True` (100.00%)
- `unmodified_false_positive_rate_satisfied`: `False` (75.00%)
- `all_required_dimensions_supported`: `True`
- `holdout_passed`: `False`
- `external_renderer_available`: `True`

## 6. Scientific Posture
- RC-013 Pilot Validation: NOT RUN
- N_Russian: 2 (Alexander Scriabin + Modest Mussorgsky)
- RC-012 Resumption: BLOCKED
