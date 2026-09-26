# RC-013 Machine Triangulation Calibration Report (Protocol V4)

**Status:** `PROTOCOL_V4_CALIBRATION_FAIL`  
**Protocol Version:** `rc013_machine_triangulation_protocol_v4`  
**Protocol Hash:** `ef9edd06e3383de1df27cd6b4cb6eb5d96a73fcf435fbc9e76998844fbf521cc`  
**Calibration Corpus Bundle Hash:** `f03f23723e08af74df91e3255c346a99151013a4a1ec4d7ec4c0852935882e1d`  
**External Engine Bundle Hash:** `e696e41ea25329bd2f5c8642421c085a2c8d71fbfa0aa40ddb8956f7e196b51f`  
**Real-Scan Benchmark Hash:** `5e732f103b9ba9c06b6f64d3d4701f502707d3de19f040ae92c0220334a51946`  
**End-to-End Mutation Suite Hash:** `1a537f324b69daf230f74520bc03a6d1fc10af9f2fabc3eb5fb8540b52a03eee`  
**Calibration Result Hash:** `df75babd348df2715f9d79b9f749303d8f5dc25827a8c46d0e37252663181835`  

## 1. External Multi-Channel Recognition Engines
- **Channel A:** External Audiveris CLI v5.11.0 (Page-aware measure offset tracking)
- **Channel B:** External homr v0.7.0 Neural OMR (SegNet + TrOMR Vision Transformer ONNX models)
- **Channel C:** ScoreScanStructuralAlignment with MuseScore 4 CLI production engraving

## 2. Multi-Page Full-Movement Calibration & Holdout Set
- **Synthetic Controlled Tier:** Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846
- **External Real-Scan Tier (DCMLab):** Chopin Mazurka Op. 6 No. 1 (3 pages, 75 measures), Chopin Mazurka Op. 7 No. 1 (2 pages, 67 measures), Chopin Mazurka Op. 17 No. 1 (2 pages, 61 measures)
- **Untouched Final Holdout Tier (DCMLab):** Grieg Lyric Pieces Op. 12 No. 1 (1 page, 23 measures)

## 3. End-to-End Image-Level Mutation Sensitivity
- Total Injected: 57
- Total Detected: 57
- Mutation Detection Recall: 100.00%
- Critical False Negative Rate: 0.00%

## 4. Empirical Downstream Feature Dependency Contract
- Target Standard: `FIT_FOR_RC012_STRUCTURAL_ANALYSIS` (Status = `PARTIALLY_FIT_FOR_RC012_STRUCTURAL_ANALYSIS`)
- Supported Core Descriptors: 0/5
- Partially Supported Core Descriptors: 4/5

## 5. Inspectable Calibration Gate Conditions
- `external_engines_available`: `True`
- `real_scan_bytes_valid`: `True`
- `reference_bytes_valid`: `True`
- `complete_source_page_coverage`: `False`
- `required_mutation_recall_satisfied`: `True`
- `synthetic_controls_pass`: `False`
- `empirical_feature_fit_satisfied`: `False`

## 6. Scientific Posture
- RC-013 Pilot Validation: NOT RUN
- N_Russian: 2 (Alexander Scriabin + Modest Mussorgsky)
- RC-012 Resumption: BLOCKED
