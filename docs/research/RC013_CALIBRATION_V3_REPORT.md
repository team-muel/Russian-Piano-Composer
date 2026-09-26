# RC-013 Machine Triangulation Calibration Report (Protocol V3)

**Status:** `PROTOCOL_CALIBRATION_V3_PASS`  
**Protocol Version:** `rc013_machine_triangulation_protocol_v3`  
**Protocol Hash:** `f78dbf70ecf32b44c39b39b9b9a42fc4666041ad4eaf29cce68352a8e2a74bb8`  
**Calibration Corpus Hash:** `607aad434b43d2bf23b1cc24278fe758572e702bf7080a237ebe3719b5136345`  
**External Engine Bundle Hash:** `96fa5f29f01b2d8915ca438a36944f5b9e059b74f55e43352dae8cf32846160e`  
**Real-Scan Benchmark Hash:** `3d07697894f19e2a5ee9eab690f95755d0c17b8139f3f3205383e15d6ec02ae1`  
**End-to-End Mutation Suite Hash:** `1a537f324b69daf230f74520bc03a6d1fc10af9f2fabc3eb5fb8540b52a03eee`  
**Calibration Result Hash:** `8dde9ad7c93b9ecb9c4a9bc465853539d55aaf0247f7ec014add691f19c0baa3`  

## 1. External Multi-Channel Recognition Engines
- **Channel A:** External Audiveris CLI v5.11.0 (Rule-based morphology + Tesseract 5.5.2 OCR)
- **Channel B:** External homr v0.7.0 Neural OMR (SegNet segmentation + TrOMR transformer sequence decoder)
- **Channel C:** ScoreScanStructuralAlignment with MuseScore 4 CLI production engraving

## 2. Multi-Tier Calibration & Holdout Performance
- **Synthetic Controlled Tier:** Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846
- **External Real-Scan Tier (DCMLab):** Chopin Mazurka Op. 6 No. 1, Chopin Mazurka Op. 7 No. 1
- **External Real-Scan Holdout Tier (DCMLab):** Chopin Mazurka Op. 17 No. 1 (One-shot evaluated)

## 3. End-to-End Image Mutation Sensitivity
- Total Injected: 57
- Total Detected: 57
- Mutation Detection Recall: 100.00%
- Critical False Negative Rate: 0.00%

## 4. Downstream Feature Dependency Contract
- Target Standard: `FIT_FOR_RC012_STRUCTURAL_ANALYSIS` (Pass = False)
- Supported Core Descriptors: 5/5 (Pitch Class Entropy, Voice Leading Cross-Entropy, Harmonic Root Motion, Metric Accent Syncopation, Phrase Boundary Density)

## 5. Scientific Posture
- RC-013 Pilot Validation: NOT RUN
- N_Russian: 2 (Alexander Scriabin + Modest Mussorgsky)
- RC-012 Resumption: BLOCKED
