# RC-012 Confirmatory Corpus Requirements & Preregistration Protocol

## 1. Motivation
The findings of RC-010 confirmed that statistical surface markers fail to separate Russian and Control corpora across held-out composers (`RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED`). RC-011 establishes a robust, 56-feature theory-grounded structural music representation.

RC-012 will conduct the first **confirmatory structural comparison** between Russian and Control corpora using the frozen `STRUCTURAL_REPRESENTATION_SCHEMA_V1`.

To avoid p-hacking, post-hoc metric selection, or data contamination, this document defines the prerequisite corpus and protocol requirements for RC-012.

---

## 2. Corpus Integrity Requirements

1. **Manifest Immutability**:
   - The canonical corpus manifest (`data/manifests/corpus_manifest.yaml`) and its SHA-256 hash `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212` must remain frozen.
   - Any corpus expansion must occur in a separate discovery/confirmatory split.

2. **Composer-Held-Out Split Design**:
   - Structural evaluation must maintain complete composer isolation.
   - No feature normalization or scaler may be fit across cross-validation boundaries.

3. **Multi-Hypothesis Correction**:
   - When testing all 56 structural features, Benjamini-Hochberg False Discovery Rate (FDR $q \le 0.05$) or permutation-based family-wise error rate control must be applied.

---

## 3. Structural Hypotheses for RC-012

| Hypothesis | Feature Family | Theoretical Rationale |
| :--- | :--- | :--- |
| **H1: Octave & Interstaff Expansion** | `TEXTURE_REGISTER` | Russian late-Romantic piano literature (Rachmaninoff, Medtner) exhibits wider registral spans and frequent multi-octave doubling compared to Western European control corpuses. |
| **H2: Metric & Cadential Ambiguity** | `CADENCE` / `TONAL` | Russian corpus exhibits delayed/weakened cadential resolutions and higher chromatic duration shares. |
| **H3: Contrapuntal Density & Inner Voice Motions** | `VOICE_LEADING` | Russian piano works feature denser polyphonic voice-leading and higher common-tone retention in chordal layers. |
| **H4: Formal Return Intensity** | `FORM` | Recapitulatory formal returns in Russian piano music exhibit distinct structural contrast compared to episodic structures. |

---

## 4. Governance & Reproducibility Gate
RC-012 must enforce:
- Zero retroactive modification of RC-011 feature definitions.
- Strict pre-registration commit prior to executing the statistical hypothesis battery.
- Mandatory two-process reproducibility audit for all permutation p-values and effect sizes.
