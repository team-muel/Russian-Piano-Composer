# RC-013 Machine Validation Branch Exit Record

**Status**: CLOSED & ARCHIVED (NEGATIVE SCIENTIFIC RESULT)  
**Milestone**: RC-013 Confirmatory Corpus Acquisition  
**Decision**: Complete Exit from Machine-Only Source Validation Branch  
**Target Policy**: No Protocol V7 will be developed or evaluated  

---

## 1. Executive Summary

Over Protocols V1 through V6, the project investigated multiple distinct machine-only, automated verification architectures to determine whether optical music recognition (OMR), computer vision, or differential image comparison could serve as a standalone authority for source fidelity of historical piano scores.

The cumulative empirical evidence establishes a definitive negative scientific finding:

$$\mathbf{MACHINE\_ONLY\_SOURCE\_FIDELITY\_AUTHORITY = NOT\_ESTABLISHED}$$

Current image-based, OMR, and differential rendering methods cannot reliably distinguish subtle notation differences from historical engraving plate idiosyncrasies, raster noise, and layout deformation on dense piano music without human-in-the-loop oversight.

Furthermore, a fundamental governance conflict exists between the 3-score pilot structure and the preregistered RC-012 confirmatory requirement ($M_c \ge 10$). Therefore, the machine-validation research branch is formally closed as an archival negative result.

---

## 2. Chronological Trajectory of Verification Protocols (V1–V6)

| Protocol Version | Architectural Concept | Methodological Status | Empirical Finding |
| :--- | :--- | :--- | :--- |
| **Protocol V1** | Blind Triangulation (Channel A/B OMR + Channel C Pixel Diff) | **INVALIDATED** | Contaminated by ground-truth leakage and self-image comparison ($R_0 \equiv S$). |
| **Protocol V2** | External OMR Integration & Blind Sandbox | **INVALIDATED** | Pseudo-OMR heuristics rather than genuine external recognition engines. |
| **Protocol V3** | External OMR (Audiveris + homr) + Historical Real Scans | **INVALIDATED** | Incomplete calibration coverage; fixed hardcoded thresholds. |
| **Protocol V4** | Full-Score Historical Blind OMR Retranscription | **VALID NEGATIVE RESULT** | Established that full blind retranscription on historical dense piano scores fails (OMR-NED $> 0.40$). |
| **Protocol V5** | Candidate-Conditioned Falsification Prototype | **INVALIDATED PROTOTYPE** | Conceptual shift to falsification, but used synthetic `np.roll` pixel shifts and empty-measure shortcuts. |
| **Protocol V6** | Genuine Symbolic Single-Fault Counterfactual Verification | **VALID CALIBRATION FAIL** | True MusicXML mutations ($H_i$) and differential masks ($M_i$), but failed real-scan calibration gate. |

---

## 3. Forensic Analysis of Protocol V6 Failure Modes

Protocol V6 eliminated all synthetic pixel shortcuts and evaluated true symbolic MusicXML mutations rendered through MuseScore 4 against historical plate scans (Supraphon, Breitkopf & Härtel, Brandus, Peters).

### Key Empirical Failure Modes

1. **Plate Font and Engraving Layout Discrepancies**:
   Historical 19th-century engraving plates exhibit distinct font metrics, line weights, non-linear system justifications, and staff bowings. When compared to clean vector engraving (MuseScore 4), pixel-level L1 distances are dominated by global font geometry rather than symbolic pitch/rhythm differences.
2. **False Positive Rate on Positive Controls**:
   Pristine, correct transcriptions evaluated against historical scans yielded a **100.0% False Positive Rate** ($\Delta < 0$), as historical plate nuances exceeded counterfactual differential thresholds.
3. **Inadequate Real-Scan Mutation Sensitivity**:
   - Real-scan pitch step detection sensitivity: **42.9%** (requirement: $\ge 90.0\%$)
   - Real-scan accidental detection sensitivity: **28.6%** (requirement: $\ge 90.0\%$)
   - Real-scan octave detection sensitivity: **28.6%** (requirement: $\ge 90.0\%$)
4. **No-Op and Unengraved Mutation Artifacts**:
   Forensic audit revealed that 12/85 specimens were symbolic no-ops (`alter_1_to_1`, `octave_5_to_5`) and 20/85 duration mutations modified only `<duration>` divisions without changing `<type>` or `<dot>`, producing identical rendered bitmaps ($H_0 \equiv H_i$).

---

## 4. Formal Archival Decision

1. **Preserve `PROTOCOL_V6_CALIBRATION_FAIL`**:
   The Protocol V6 verdict remains permanently frozen as `FAIL`. It is not converted to `PARTIAL` or `PASS`.
2. **No Protocol V7**:
   No additional machine verifiers or threshold tunings will be constructed.
3. **Pilot Score Posture**:
   The nine RC-013 Russian pilot scores (Arensky Op. 36, Lyadov Op. 40/46, Lyapunov Op. 11) remain completely unvalidated by machine receipts.
4. **Exit from Machine Authority**:
   Source-fidelity verification must rely on scholarly edition provenance and independent human review or dual-source symbolic cross-checks, not uncalibrated machine vision.
