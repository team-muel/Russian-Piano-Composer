# RC-013 Machine Validation Protocol V2 Invalidation Record

## 1. Executive Summary

| Attribute | Value |
| :--- | :--- |
| **Protocol Identification** | `rc013_machine_triangulation_protocol_v2` |
| **Former Status** | `PROTOCOL_CALIBRATION_V2_PASS` |
| **New Status** | `INVALIDATED_CALIBRATION_EVIDENCE` |
| **Invalidation Date** | 2026-09-26 |
| **RC-013 Pilot Scores Exposed** | 0 (Zero Russian pilot scores exposed) |
| **RC-013 Canonical Corpus Impact** | None (`N_Russian = 2`, `RC-012 RESUMPTION = BLOCKED`) |

---

## 2. Forensic Audit Findings & Invalidation Reasons

A forensic methodology and scientific integrity audit identified five fundamental defects in the Protocol V2 calibration and architecture:

### Reason 1: `PSEUDO_OMR_CHANNEL_A` (Classical Staff-Graph Heuristic Fallback)
* **Finding:** Channel A was implemented as an internal morphological heuristic class (`StructuredStaffGraphOMREngine`) rather than an authentic optical music recognition system.
* **Specific Defects:**
  1. Measure segmentation utilized a fixed/approximate 4-measures-per-system assumption rather than recognizing actual barlines across varying layouts.
  2. Pitch detection was inferred geometrically from contour centroid offsets relative to staff bounding boxes, with hardcoded scale-step arrays.
  3. Note duration was effectively fixed to quarter notes, omitting rhythmic parsing (beams, flags, dots, rests).
  4. Accidentals, key signatures, time signatures, ties, tuplets, and multi-voice counterpoint were not recognized from optical features.

### Reason 2: `PSEUDO_NEURAL_CHANNEL_B` (Sobel Spatial Convolution Lacked Trained Neural Network)
* **Finding:** Channel B was named `NeuralVisualFeatureOMREngine` and described as a neural visual decoder, but contained no trained deep neural network, no model weights, no checkpoint, and no learned sequence decoder.
* **Specific Defects:**
  1. The implementation relied purely on hand-crafted Sobel filter gradients and vertical projection profile peak clustering.
  2. The OMR classification cannot be described scientifically as neural OMR without a verified learned model architecture (e.g. TrOMR, SegNet, CRNN).

### Reason 3: `SYNTHETIC_DATA_MISCLASSIFIED_AS_REAL_SCAN`
* **Finding:** Calibration items in the `REAL_SCAN_THRESHOLD_CALIBRATION` and `CALIBRATION_V2_FINAL_HOLDOUT` splits (Beethoven Op. 119 No. 1, Mozart K. 545, Schumann Op. 15 No. 1, Clementi Op. 36 No. 1) were synthesized in-repository using Matplotlib and PIL Gaussian blur, but were misclassified as real scans in registry schemas.
* **Scientific Standard:** Synthetic and degraded renders may serve as unit-test and perturbation benchmarks, but cannot establish empirical performance on authentic historical piano prints.

### Reason 4: `APPROXIMATE_RENDERER_NOT_NOTATION_COMPLETE`
* **Finding:** The Channel C renderer (`DeterministicScoreRenderer`) was an ad-hoc Matplotlib sketch generator that rendered notehead circles and stems on fixed lines, ignoring beams, accidentals, clefs, dynamics, tuplets, and standard engraving layout.
* **Defect:** An approximate sketch cannot serve as an authoritative symbolic-to-visual reference for historical scan alignment.

### Reason 5: `CALIBRATION_NOT_REPRESENTATIVE_OF_HISTORICAL_PIANO_SCORES`
* **Finding:** The calibration corpus lacked genuine multi-voice, polyphonic, historical engraved score scans with independent ground-truth provenance.

---

## 3. Preserved Historical Hashes for Protocol V2

The following historical cryptographic hashes are preserved for full auditability:

```text
RC013_MACHINE_PROTOCOL_V2_HASH:        acee81f522377acf6d10cf6ef00ad11b72137da6d3bf144262ac6f2833e2c6b9
RC013_CALIBRATION_V2_CORPUS_HASH:      f82964d2ef9d52706e29c6171c9300533266e4dab4c2a048fbf6c14e1a54863a
RC013_END_TO_END_MUTATION_SUITE_HASH: caa82e0fe685e40a4e3257993ebc68f643dda19d87be4cc605048a1a5d035754
RC013_CALIBRATION_V2_RESULT_HASH:      79a04c4969a1ae48c22251036a0e11c04cb3eaf2ae2818d3cd7f90a166cdb336
```

---

## 4. Remediation Directives for Protocol V3

1. Channel A must execute genuine external Audiveris OMR binary (`Audiveris.exe` v5.11.0) with full process execution receipts.
2. Channel B must execute genuine external `homr` neural OMR (SegNet + TrOMR transformer onnx models) with immutable model SHA binding.
3. Channel C must use MuseScore 4 CLI for notation-complete symbolic score engraving.
4. Calibration corpus must incorporate authentic historical print scans and independent symbolic ground truth from authoritative external corpora (e.g. DCMLab / OpenScore).
5. All 9 RC-013 Russian pilot scores remain strictly unexposed, unvalidated, and fail-closed (`N_Russian = 2`).
