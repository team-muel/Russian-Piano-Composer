# RC-013 Machine Triangulation Calibration Report

**Status:** `PROTOCOL_CALIBRATION_PASS`  
**Protocol Version:** `rc013_machine_triangulation_protocol_v1`  
**Protocol Hash:** `da454acced4aab41747d1c83c83bd06d12fc22ab48e0f9769780e88feeec83e9`  
**Calibration Corpus Hash:** `a3ea61a87a6359b823b53521bb0548c7d6c3c1761ab2c8c7e10411e5f6aa4283`  
**Mutation Suite Hash:** `802be29ddf50353c45212dee7a124ef07b60bf1fb6106c382b182d08e9a6a6d9`  
**Calibration Result Hash:** `28eabe65778b630a427c40e37fdcaa925c68ec429fea3403089eff5982bd5408`  

## 1. Multi-Channel Calibration Outcomes
- Channel A (Structured OMR): PASS on all threshold and holdout scores (OMR-NED: 0.0000)
- Channel B (Neural OMR): PASS on all threshold and holdout scores (OMR-NED: 0.0000)
- Channel C (Structural Alignment): PASS on all threshold and holdout scores (Mean Discrepancy: 0.0000)

## 2. Adversarial Mutation Sensitivity (19 Families)
- Total Injected: 57
- Total Detected: 57
- Total Missed: 0
- Mutation Detection Recall: 100.00%
- Critical False Negative Rate: 0.00%

## 3. Frozen Acceptance Thresholds
- `max_omr_ned`: 0.05
- `max_critical_mismatches`: 0
- `max_image_discrepancy`: 0.35
- `required_mutation_recall`: 1.0

## 4. Scientific Posture
- RC-013 Pilot Validation: NOT RUN
- N_Russian: 2 (Alexander Scriabin + Modest Mussorgsky)
- RC-012 Resumption: BLOCKED
