# RC-014A Historical Errata & Provenance Correction Record

**Status**: FORMALLY RECORDED & FROZEN  
**Correction Date**: 2026-09-26  
**Target Artifacts**:
- [`docs/research/RC014A_NEW_SYMBOLIC_SOURCE_DISCOVERY_RECORD.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC014A_NEW_SYMBOLIC_SOURCE_DISCOVERY_RECORD.md)
- [`docs/research/RC014A_TONAL_PIANO_CORPUS_QUALIFICATION_AUDIT.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC014A_TONAL_PIANO_CORPUS_QUALIFICATION_AUDIT.md)
- [`data/manifests/rc014a_rights_and_license_audit.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/manifests/rc014a_rights_and_license_audit.json)
- [`data/manifests/rc014a_source_authority_comparison.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/manifests/rc014a_source_authority_comparison.json)

---

## 1. External Git Tree SHA Correction

### Erroneous RC-014A Text:
```text
Root Tree SHA:
3f5a08e Update Readme.md
```
*(Note: `3f5a08e` is the truncated commit object SHA, not the git tree object SHA).*

### Correct Immutable Provenance Identifiers:
* **External Repository**: `https://github.com/hectorbellmann-art/Tonal-Piano-Corpus`
* **Frozen Commit SHA**: `3f5a08e9b2360c11aea5d6d384eb84e7845b793c`
* **Actual Root Git Tree SHA**: `2e86805f11040570d1f2f45bc0f03be408ca4997`

---

## 2. Frozen RC-011 Descriptor Family Counts Correction

### Erroneous RC-014A Text:
RC-014A report prose stated:
```text
Family A (Tonal): 8
Family B (Sonority): 8
Family C (Cadence): 8  <-- INCORRECT
Family D (Form): 8
Family E (Voice-Leading): 8
Family F (Texture): 8  <-- INCORRECT
Family G (Trajectory): 8
Total: 56
```

### Correct Frozen Catalog Specification:
In accordance with `src/russian_piano_composer/structure_analysis/schema.py` and `docs/spec/STRUCTURAL_REPRESENTATION_SCHEMA_V1.md`:
* **Family A (TONAL)**: **8 descriptors**
* **Family B (SONORITY)**: **8 descriptors**
* **Family C (CADENCE)**: **6 descriptors** (`cadence_arrival_rate`, `cadence_perfect_authentic_rate`, `cadence_imperfect_authentic_rate`, `cadence_half_rate`, `cadence_deceptive_rate`, `cadence_plagal_rate`)
* **Family D (FORM)**: **8 descriptors**
* **Family E (VOICE_LEADING)**: **8 descriptors**
* **Family F (TEXTURE_REGISTER)**: **10 descriptors** (`texture_voice_count_mean`, `texture_voice_count_max`, `texture_simultaneous_notes_mean`, `texture_simultaneous_notes_max`, `texture_span_semitones_mean`, `texture_span_semitones_max`, `texture_bass_register_mean`, `texture_treble_register_mean`, `texture_arpeggiation_rate`, `texture_repeated_note_rate`)
* **Family G (TEMPORAL_TRAJECTORY)**: **8 descriptors**
* **Total Frozen Descriptors**: **Exactly 56**

*(Note: Feature extraction execution in RC-014A correctly evaluated all 56 descriptors; the error was strictly in summary report prose).*

---

## 3. Legal Rights Taxonomy & Status Deprecation

### Deprecated Broad Statuses:
1. `RIGHTS_CLEAR_FOR_SCIENTIFIC_EVALUATION` $\rightarrow$ **DEPRECATED**. Replaced by multidimensional rights classification distinguishing underlying work, printed edition, and digital encoding license.
2. `READY_FOR_VENDORING` $\rightarrow$ **DEPRECATED & WITHDRAWN**. An external corpus without an explicit root license cannot be labeled "ready for vendoring."
3. Broad assertions of "factual non-creative reproduction under fair use" as general permission $\rightarrow$ **DEPRECATED**. Replaced with strict recognition that digital encodings without explicit upstream licenses require permission or a non-vendored access architecture.

---

## 4. US Public Domain Cutoff Logic Correction

### Erroneous RC-014A Text:
Hardcoded cutoff: `pre-1929`.

### Correct Rule (Execution Year 2026):
Under US copyright law for published works (95 years from publication):
* **Works published before January 1, 1931** are in the US public domain as of 2026.
* **Prokofiev Early Works in Corpus**:
  * Op. 2 No. 4 (1909 / 1911) $\rightarrow$ US Public Domain
  * Op. 3 No. 3 (1908 / 1911) $\rightarrow$ US Public Domain
  * Op. 11 (1912) $\rightarrow$ US Public Domain
  * Op. 12 Nos. 2, 7 (1913) $\rightarrow$ US Public Domain
  * Op. 22 Nos. 1, 5, 10 (1915–1917) $\rightarrow$ US Public Domain
  * Total Pre-1931 pieces = **8 pieces**.
* **Prokofiev Later Works in Corpus**:
  * Op. 65 (1935, 3 pieces) $\rightarrow$ US Copyright Protected until 2031 (95-year term).
  * Op. 75 (1937, 1 piece) $\rightarrow$ US Copyright Protected until 2033 (95-year term).
