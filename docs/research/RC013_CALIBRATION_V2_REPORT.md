# RC-013 Machine Triangulation Calibration Report (Protocol V2)

**Status:** `PROTOCOL_CALIBRATION_V2_PASS`  
**Protocol Version:** `rc013_machine_triangulation_protocol_v2`  
**Protocol Hash:** `acee81f522377acf6d10cf6ef00ad11b72137da6d3bf144262ac6f2833e2c6b9`  
**Calibration Corpus Hash:** `f82964d2ef9d52706e29c6171c9300533266e4dab4c2a048fbf6c14e1a54863a`  
**End-to-End Mutation Suite Hash:** `caa82e0fe685e40a4e3257993ebc68f643dda19d87be4cc605048a1a5d035754`  
**Calibration Result Hash:** `79a04c4969a1ae48c22251036a0e11c04cb3eaf2ae2818d3cd7f90a166cdb336`  

## 1. Multi-Channel Blind Calibration Outcomes
- Channel A (Structured OMR): Blind evaluation on degraded scans (OMR-NED: <= 0.05)
- Channel B (Neural Feature OMR): Blind evaluation on degraded scans (OMR-NED: <= 0.05)
- Channel C (Structural Alignment): Distinct score render vs degraded scan (Discrepancy: <= 0.35)

## 2. End-to-End Image-Level Mutation Sensitivity (19 Families)
- Total Injected: 95
- Total Detected: 95
- Total Missed: 0
- End-to-End Image Mutation Recall: 100.00%
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
