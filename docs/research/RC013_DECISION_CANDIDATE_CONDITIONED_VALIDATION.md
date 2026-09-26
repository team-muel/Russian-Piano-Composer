# Scientific Decision Record: Candidate-Conditioned Source-Fidelity Falsification Protocol (V5)

## 1. Problem Definition & Lineage
Full blind optical music recognition (OMR) calibration across Protocols V1 through V4 established a rigorous, reproducible scientific finding:
- Fully independent end-to-end OMR transcription of 19th-century dense piano plates by existing open-source recognition engines (Audiveris v5.11.0, homr v0.7.0 ONNX) cannot achieve the holistic measure-by-measure fidelity required to serve as an autonomous symbolic transcription authority.
- Protocol V4 explicitly derived `PROTOCOL_V4_CALIBRATION_FAIL` (not due to an execution error, but due to real-scan historical noise, dense multi-voice polyphony, and engraving differences).

## 2. Scientific Need & Core Reorientation
RC-013 already possesses recovered candidate MusicXML transcriptions for its target works. The scientific question required for corpus acceptance is not:
> *"Can an AI OMR engine reconstruct a multi-page 19th-century piano score from scratch?"*

The necessary and sufficient question is:
> *"Given a candidate symbolic transcription and an authoritative historical source scan, can an automated verifier detect whether the candidate contains a scientifically material transcription error?"*

## 3. Methodological Shift (Protocol V5)
Protocol V5 replaces blind retranscription with **Candidate-Conditioned Counterfactual Falsification**:
1. **Candidate as Null Hypothesis ($H_0$):** The candidate MusicXML is rendered deterministically via MuseScore 4 production engraving.
2. **Local Structural Correspondence:** Systems and measure regions are aligned between the historical scan and the candidate render using staff geometry, barlines, and spatial visual features (not full-page pixel grids).
3. **Adversarial Counterfactual Hypotheses ($H_1, H_2, \dots, H_n$):** Musically plausible transcription errors (pitch shifts, accidental alterations, octave displacement, duration changes, rest swaps, voice swaps, missing notes, etc.) are generated locally.
4. **Local Falsification Discrimination:** The verifier measures whether the historical source image $S$ supports the candidate $H_0$ over all counterfactual variants $H_i$:
   $$\Delta_i = \text{Distance}(H_i, S) - \text{Distance}(H_0, S)$$
   A correct candidate exhibits $\Delta_i > 0$ across all tested counterfactuals.

## 4. Methodological Boundaries & Anti-Self-Certification
- **Candidate-Conditioned Evidence:** Because the candidate score is provided to the verifier, this protocol is **not** independent retranscription and must strictly be labeled `MACHINE_CANDIDATE_SOURCE_FIDELITY_SUPPORTED` / `CANDIDATE_FALSIFICATION_*`.
- **Vocabulary Ban:** Do NOT use `HUMAN_SOURCE_FIDELITY_VERIFIED` or any terminology implying human review.
- **Fail-Closed Invariance:**
  - RC-013 Pilot Validation: `NOT RUN` during protocol development and calibration.
  - $N_{\text{Russian}} = 2$ (Alexander Scriabin + Modest Mussorgsky).
  - RC-012 Resumption: `BLOCKED`.
  - Anton Arensky, Anatoly Lyadov, Sergei Lyapunov: `UNQUALIFIED`.
