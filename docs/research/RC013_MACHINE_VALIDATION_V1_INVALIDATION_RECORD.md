# RC-013 Machine Validation Protocol V1 Invalidation Record

## 1. Formal Invalidation Notice

| Field | Value |
|---|---|
| **Protocol ID** | `rc013_machine_triangulation_protocol_v1` |
| **Former Status** | `PROTOCOL_CALIBRATION_PASS` |
| **New Scientific Status** | `INVALIDATED_CALIBRATION_EVIDENCE` |
| **Invalidation Date** | 2026-09-24 |
| **Pilot Scores Evaluated** | `0` (None) |
| **RC-013 Corpus Scientific Impact** | `NONE` (All 9 pilot scores remain `PENDING_INDEPENDENT_HUMAN_REVIEW`) |
| **RC-012 Resumption Impact** | `NONE` (Resumption remains `BLOCKED`, $N_{\text{Russian}} = 2$) |

---

## 2. Invalidation Rationale & Audit Findings

A forensic audit of the initial V1 machine-triangulation calibration implementation identified the following critical scientific defects:

### Defect 1: Ground-Truth Leakage in OMR Adapters (`CALIBRATION_GROUND_TRUTH_LEAKAGE`)
* **Mechanism**: In `src/russian_piano_composer/corpus/rc013_omr_adapters.py`, both `StructuredStaffGraphOMREngine` and `NeuralVisualFeatureOMREngine` contained a calibration shortcut (`if reference_structure_hint and "musicxml_source" in reference_structure_hint:`), which extracted events directly from the ground-truth MusicXML file instead of performing genuine blind image recognition.
* **Impact**: The OMR engines were given the answer during calibration, rendering all reported 0.0000 OMR-NED scores invalid as evidence of optical recognition capability.

### Defect 2: Self-Comparison in Visual Alignment (`CHANNEL_C_SELF_IMAGE_COMPARISON`)
* **Mechanism**: In `scripts/run_rc013_machine_calibration.py`, Channel C was invoked with `rendered_images=source_image_paths` and `historical_scan_images=source_image_paths`, effectively comparing an image file to itself.
* **Impact**: The reported 0.0000 image discrepancy score was an artifact of identity self-comparison rather than genuine cross-modal score-to-scan geometric registration.

### Defect 3: Mutation Benchmark Bypassed Image Recognition (`MUTATION_BENCHMARK_BYPASSED_IMAGE_RECOGNITION`)
* **Mechanism**: The mutation sensitivity test evaluated `compare_event_graphs()` directly on mutated in-memory event graphs rather than rasterizing mutated scores into images, degrading them, and running them through blind OMR and visual alignment.
* **Impact**: The 100% recall metric only verified the symbolic event comparator, not the end-to-end optical verifier.

### Defect 4: Placeholder OMR Logic (`PLACEHOLDER_OMR_NOT_SCIENTIFICALLY_VALID`)
* **Mechanism**: The fallback branch in the initial OMR adapters emitted synthetic C4 quarter-note placeholder events rather than performing genuine optical symbol segmentation.

---

## 3. Preservation of Historical Evidence

In accordance with scientific data contract principles, all historical V1 artifacts (`data/manifests/rc013_machine_validation_protocol_v1.json`, `docs/research/RC013_CALIBRATION_REPORT.md`, and commit lineage) are preserved in git history as records of the invalidated iteration.

The V1 protocol hash (`da454acced4aab41747d1c83c83bd06d12fc22ab48e0f9769780e88feeec83e9`) remains immutable as the cryptographic identifier of this invalidated state and will never be reused for active scientific verification.

---

## 4. Remediation Mandate for Protocol V2
1. Completely remove `reference_structure_hint` and enforce a strict ground-truth firewall.
2. Replace placeholder OMR logic with genuine computer-vision/morphological and neural visual feature extraction engines.
3. Require distinct rendered score vs. historical scan inputs for Channel C (`rendered_sha != scan_sha`).
4. Implement an end-to-end image-level mutation benchmark.
5. Recalibrate on a multi-tier corpus including synthetic controls, real scan benchmarks, and a new untouched final holdout.
