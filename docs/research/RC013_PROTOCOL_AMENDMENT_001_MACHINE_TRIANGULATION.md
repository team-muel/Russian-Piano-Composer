# RC-013 Protocol Amendment 001: Machine-Triangulated Source-Fidelity Validation

## 1. Executive Summary & Context

Under the original RC-013 protocol, final verification of symbolic transcription fidelity against historical first editions required measure-by-measure `INDEPENDENT_HUMAN_REVIEW`. 

While pilot infrastructure, blank review packets, and receipt validation mechanisms are fully implemented and cryptographically hardened, full manual measure-by-measure human verification across the entire multi-composer corpus is currently operationally constrained by available independent musicological resources.

To address this constraint without weakening scientific integrity or fabricating review evidence, this Amendment introduces a parallel, independent machine-based verification route:

$$\text{MACHINE\_TRIANGULATED\_SOURCE\_FIDELITY\_PASS}$$

---

## 2. Definitional Boundary & Anti-Impersonation Guarantee

> [!IMPORTANT]
> `MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS` is **NOT** synonymous with, equivalent to, or a replacement for `SOURCE_FIDELITY_VERIFIED` (which remains reserved exclusively for verified human musicological review).

* AI agents and automated pipelines are **strictly prohibited** from masquerading as human musicologists or generating `INDEPENDENT_HUMAN_REVIEWER` receipts.
* Human review mechanisms (`rc013_review_ingestion.py`, `data/reviews/rc013/accepted/`, `INDEPENDENT_HUMAN_REVIEWER`) remain permanently intact as the primary and strongest verification route.
* Machine triangulation receipts are stored in a distinct, separate directory: `data/reviews/rc013/machine_accepted/`.

```
                         AUTHORITATIVE SOURCE PDF
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
        MACHINE TRIANGULATION                HUMAN MUSICOLOGY REVIEW
       (3 Independent Channels)             (Independent Human Reviewer)
                    |                                 |
                    v                                 v
     MACHINE_TRIANGULATED_PASS               SOURCE_FIDELITY_VERIFIED
   (machine_validation_receipt.json)       (human_review_receipt.json)
```

---

## 3. Scientific Status Vocabulary

The machine triangulation verification state machine introduces the following immutable statuses:

| Status Code | Definition | Scientific Meaning |
|---|---|---|
| `MACHINE_TRIANGULATION_NOT_RUN` | Initial default state for candidates. | Triangulation pipeline has not yet evaluated the candidate. |
| `MACHINE_TRIANGULATION_CALIBRATING` | Measuring instrument calibration phase. | Ground-truth calibration and sensitivity tests are ongoing. |
| `MACHINE_TRIANGULATION_FAILED` | Triangulation detected irreconcilable errors. | Multi-channel evidence rejects symbolic candidate fidelity. |
| `MACHINE_TRIANGULATION_INDETERMINATE` | Independent channels disagree without consensus. | Unresolved ambiguity requiring manual human dispute review. |
| `MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS` | All 3 channels pass strict pre-registered thresholds. | Multi-channel machine triangulation establishes high-confidence source fidelity. |

---

## 4. Multi-Channel Triangulation Architecture

To ensure genuine verification, the machine triangulation pipeline comprises three fundamentally independent channels:

### Channel A — Classical / Structural Staff-Graph OMR (`StructuredStaffGraphOMREngine`)
* **Algorithm**: Classical morphological staff-line detection, horizontal projection profiling, bounding box segmentation, and rule-based pitch/duration graph parsing.
* **Input**: Historical source scan pages only (blinded from canonical MusicXML).
* **Output**: Blind OMR symbolic event graph and feature matrices.

### Channel B — Neural / Probabilistic Visual Feature OMR (`NeuralVisualFeatureOMREngine`)
* **Algorithm**: Statistical and spatial-temporal visual pattern recognition, glyph feature embeddings, and probabilistic sequence decoding.
* **Input**: Historical source scan pages only (blinded from canonical MusicXML).
* **Output**: Probabilistic symbolic prediction graph.
* **Authority Limitation**: Strong authority on pitch, accidental, onset, duration, rest, and meter; non-exclusive authority on complex pedal/ornamentation.

### Channel C — Direct Score Rendering & Structural Image Alignment (`ScoreScanStructuralAlignmentEngine`)
* **Algorithm**: Deterministic vector rasterization of canonical MusicXML, geometric page registration, staff/system extraction, and localized notation patch cross-correlation.
* **Input**: Rendered canonical score vs. authoritative scan image.
* **Output**: Spatial correspondence heatmap and discrepancy bounds.

---

## 5. Event Normalization & Dimension Categorization

Comparisons operate on a canonical `NormalizedEventGraph` rather than raw text files.

### Critical Dimensions (Zero Tolerance for False Negatives)
* **Pitch & Octave** (`pitch_step`, `octave`)
* **Accidentals** (`alter`, cautionary accidentals)
* **Onsets & Durations** (`onset_fraction`, `duration_fraction`)
* **Rests & Voicing** (`rest`, `voice`, `staff`)
* **Metric & Tonal Framework** (`key_signature`, `time_signature`)
* **Ties & Tuplets** (`tie_start`, `tie_stop`, `tuplet_ratio`)
* **Structural Boundaries** (`repeat_structure`, `measure_sequence`)

### Secondary Dimensions (Monitored with Documented Tolerances)
* **Dynamics** ($p, f, sfz$, hairpins)
* **Articulations** (staccato, tenuto, accent)
* **Slurs & Phrasing**
* **Pedal Directives**
* **Tempo & Expressive Directives**

---

## 6. Blindness & Pre-Registration Rules

1. **Strict Calibration Isolation**: Calibration and threshold derivation are executed solely on external non-RC-013 piano benchmarks (`data/calibration/rc013_machine_validation/`).
2. **Zero Pilot Leakage**: No RC-013 pilot score may influence engine tuning, metric weights, or threshold selection.
3. **Immutable Protocol Freeze**: Thresholds, engine versions, and mutation performance requirements are frozen in `data/manifests/rc013_machine_validation_protocol_v1.json` under `RC013_MACHINE_VALIDATION_PROTOCOL_HASH`.
4. **Current Pilot Impact**: During this calibration task, all nine RC-013 pilot scores remain `analysis_eligible = false`, `generative_eligible = false`, $N_{\text{Russian}} = 2$, and `RC-012 RESUMPTION = BLOCKED`.
