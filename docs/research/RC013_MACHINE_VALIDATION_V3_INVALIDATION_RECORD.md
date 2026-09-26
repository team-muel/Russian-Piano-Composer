# RC-013 Protocol V3 Calibration Invalidation Record

This formal invalidation record documents the retraction of the `PROTOCOL_CALIBRATION_V3_PASS` verdict and details the methodological defects identified during scientific audit.

---

## 1. Metadata and Formal Retraction Status

* **Protocol Version**: `rc013_machine_triangulation_protocol_v3`
* **Former Result**: `PROTOCOL_CALIBRATION_V3_PASS`
* **New Scientific Status**: `INVALIDATED_CALIBRATION_EVIDENCE`
* **Retraction Date**: `2026-09-26T02:25:00Z`
* **RC-013 Pilot Scores Evaluated**: `0` (Strict invariant preserved: all 9 pilot scores remain uninspected, unvalidated, and fail-closed)

---

## 2. Component Disposition Summary

| Architecture Component | Status | Disposition & Scientific Rationale |
| :--- | :--- | :--- |
| **External Engine Integration** (`ExternalAudiverisOMREngine`, `ExternalHomrNeuralOMREngine`) | **VALID_COMPONENT** | Retained. Real external OMR executables (Audiveris v5.11.0 CLI, homr v0.7.0 ONNX models) are valid independent recognition engines. |
| **Notation Rendering Engine** (`MuseScoreProductionScoreRenderer`) | **VALID_COMPONENT** | Retained. Real MuseScore 4 CLI generates full-fidelity vector engraving plates. |
| **Blindness Firewall** (`BlindOMRFirewall`) | **VALID_COMPONENT** | Retained. Subprocess isolation and rejection of symbolic ground truth within OMR working directories is verified. |
| **Historical Data Acquisition Toolchain** | **PARTIALLY_VALID_COMPONENT** | Requires repair. Sourcing from DCMLab is valid, but single-page PDF extraction failed to cover full multi-page historical movements. |
| **Protocol V3 Calibration Verdict** | **INVALIDATED** | Defective. Hard-coded string return without inspectable gate derivation, measure-aware alignment, or complete historical page coverage. |

---

## 3. Specific Methodological Defects Identified

### 1. `CALIBRATION_VERDICT_HARDCODED`
The Protocol V3 calibration script returned `"calibration_verdict": "PROTOCOL_CALIBRATION_V3_PASS"` as a static string rather than computing the verdict through a deterministic, inspectable multi-condition gate function.

### 2. `INCOMPLETE_HISTORICAL_PAGE_COVERAGE` & `FULL_SCORE_GT_VS_SINGLE_PAGE_SCAN_MISMATCH`
The Protocol V3 dataset builder extracted only page 2 (`pdf_page_index = 2`) of multi-page historical PDF editions. Consequently, full-movement symbolic ground truth scores (e.g., Chopin Op. 6 No. 1 with 72 measures spanning 3 pages) were evaluated against only a single opening page scan (measures 1–28).

### 3. `COVERAGE_METRIC_NOT_MEASURE_AWARE`
Coverage in V3 was calculated as a simple unaligned event-count ratio:
$$\text{coverage}_{\text{V3}} = \frac{\text{len}(\text{recognized\_events})}{\text{len}(\text{reference\_events})}$$
This metric is uncalibrated: hallucinated events artificially inflate coverage, missing middle measures are not localized, and no upper bound ($\le 1.0$) was enforced.

### 4. `MIN_COVERAGE_THRESHOLD_NOT_EMPIRICALLY_DERIVED`
The 20% event-count threshold was arbitrary and insufficiently stringent to ensure that historical piano scores have sufficient notation evidence for downstream structural and harmonic analysis.

### 5. `CHANNEL_C_UNMATCHED_PAGES_NOT_PENALIZED`
Channel C visual alignment computed discrepancies across `min(len(rendered), len(scans))`, silently ignoring trailing pages when page counts differed between rendered scores and historical scans.

### 6. `MULTIPAGE_MEASURE_NUMBER_COLLISION_RISK`
When processing multi-page scans page-by-page, local measure numbering restarting at measure 1 on each page caused collisions when flatly concatenating event lists.

### 7. `FEATURE_FIT_NOT_EMPIRICALLY_ESTABLISHED`
`FIT_FOR_RC012_STRUCTURAL_ANALYSIS` was evaluated by testing whether dimension names existed in a static list rather than testing whether recognition engines achieved empirical recall and precision on each required dimension (`pitch`, `duration`, `voice`, `staff`, `accidental`, `meter`).

### 8. `CALIBRATION_REPORT_STATE_CONTRADICTION`
A contradiction was discovered where user execution summaries reported `FIT_FOR_RC012_STRUCTURAL_ANALYSIS = True` (95/95 mutations) while the persisted `RC013_CALIBRATION_V3_REPORT.md` recorded `FIT_FOR_RC012_STRUCTURAL_ANALYSIS = False` (57/57 mutations).

### 9. `PROVENANCE_METADATA_ERRORS`
Upstream licenses and repository identities were collapsed or conflated (e.g., conflating DCML CC BY-NC-SA 4.0 data licensing with public domain Joseffy scan status, and incomplete PyPI/upstream GitHub metadata for `homr`).

---

## 4. Preservation of Historical Hashes

Protocol V3 hashes remain recorded as historical hashes of invalidated artifacts. They must not be erased, but are superseded by Protocol V4.
