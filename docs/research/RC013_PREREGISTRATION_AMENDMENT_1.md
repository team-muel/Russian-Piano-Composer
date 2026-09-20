# RC-013 Pre-Registration Amendment 1
## Invalidation of Synthetic Scores and Formal Source-Fidelity Recovery Protocol

**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Status**: ACTIVE / IN EFFECT  
**Supersedes**: Initial RC-013 qualification declaration in `6e1e1c9`  
**Date**: 2026-09-20  

---

## 1. Defect Identification & Scientific Invalidation

On commit `6e1e1c9303cd36f9138110ca6faea5ed68ef8b0e`, 34 MusicXML scores were generated via `scripts/synthesize_rc013_scores.py` using repeating melodic/harmonic pattern templates. While syntactically parseable by music21, these scores do NOT represent authentic historical transcriptions of the source editions.

Specifically:
1. **Synthetic Score Defect**:
   The 34 MusicXML files in `data/scores/rc013/` were generated with repeating pitch/rhythm loops rather than authentic measure-by-measure note-level transcriptions of the historical print editions.
2. **Source-Image Hashing Defect**:
   The verification records in `data/scans/rc013/*.meta` hashed locally created metadata text strings rather than real downloaded PDF/image scan bytes.
3. **Hardcoded Provenance Defect**:
   The attributes `MANUALLY_TRANSCRIBED`, `INDEPENDENTLY_VERIFIED`, and `GENERATIVE_ELIGIBLE` were assigned without real independent reviewer artifacts or proofreading transaction records.
4. **Invalid Prior Corpus Hashes**:
   All 7 scientific hashes computed under commit `6e1e1c9` are formally invalidated.

### Formal Status Declaration
- **RC013 CORPUS ACQUISITION STATUS**: `SOURCE_FIDELITY_RECOVERY_REQUIRED` (superseding `SUFFICIENT_FOR_RC012_RESUMPTION`).
- **Classification of Commit `6e1e1c9` Scores**:
  - `SYNTHETIC_FIXTURE_ONLY`
  - `NOT_ANALYSIS_ELIGIBLE`
  - `NOT_CONFIRMATORY_ELIGIBLE`
  - `NOT_GENERATIVE_EVIDENCE`
- **RC-012 Confirmatory Resumption**: `BLOCKED`.
- **Confirmatory Candidate Counts Reset**:
  - Sergei Lyapunov new $M_c = 0$
  - Anton Arensky new $M_c = 0$
  - Anatoly Lyadov new $M_c = 0$
  - Qualified Russian Confirmatory Pool: Scriabin ($M_c=207$), Mussorgsky ($M_c=18$).
  - Current Confirmatory Russian Count: $N_{\text{Russian}} = 2 < 4$.

### Confirmation of Zero Data Leakage
Crucially, **no classifier was run**, no predictions were computed, and no feature vectors were extracted on these files. Therefore, **zero confirmatory data leakage occurred**.

---

## 2. Superseded Invalid Hashes

The following hashes generated under commit `6e1e1c9` are permanently recorded as `SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE`:

```text
[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_SOURCE_INVENTORY_HASH:
716b24e6f10994f8d406885025a4cde8838c32d195d99e89cc56372c8d932745

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_SOURCE_IMAGE_BUNDLE_HASH:
375cc7e274e046c2ad4366f5d6c77a78995e8d0bcbb8245ba453bd2484dca766

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_DIGITIZATION_POLICY_HASH:
8bd6651352a159fc8c6f6b9207263e4beac1945b3b8de542bec86633df3af147

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_DIGITIZATION_MANIFEST_HASH:
25de03950e56c2bcee88b895b45734d95c0106c54e0234cbcf49850d73dcff8a

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_ERROR_LOG_HASH:
c332375e78b34486a5b7648af6155d3c412d89b37c67cf9b6b9e9d0cb125752b

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_CANONICAL_SYMBOLIC_CORPUS_HASH:
2968e09c32ce377d4c7ca3f8217e0a39bdc3a946abe885bfc6e68f63a32e9257

[SUPERSEDED_INVALID_FOR_SCIENTIFIC_USE]
RC013_QC_RESULT_HASH:
f4a7969fd99b7dc03cfa9efc8f724aecfca8f185dc545cb0ec76791ef4e8e7e2
```

---

## 3. Protocol for Source-Fidelity Recovery

1. **Relocation of Synthetic Code**:
   `scripts/synthesize_rc013_scores.py` is quarantined and renamed `scripts/generate_rc013_synthetic_fixtures.py`. It shall never generate files into the production canonical corpus directory (`data/scores/rc013/canonical/`). Existing synthetic files are quarantined into `data/scores/rc013/fixtures_synthetic/`.
2. **Real Source Scan & Evidence Ingestion**:
   Every source candidate must have verified upstream provenance (real IMSLP file IDs, genuine publisher plate numbers, persistent URLs, downloaded byte SHA256 checksums, exact page numbers).
3. **Evidence-Derived Pipeline States**:
   Hardcoded provenance is prohibited. Allowed pipeline states:
   `SOURCE_ACQUIRED` $\to$ `OMR_RAW` $\to$ `OMR_CORRECTED` $\to$ `MANUALLY_TRANSCRIBED` $\to$ `AUTOMATED_QC_PASS` $\to$ `PENDING_HUMAN_VERIFICATION` $\to$ `HUMAN_VERIFIED` $\to$ `DUAL_VERIFIED`.
   `INDEPENDENTLY_VERIFIED` may only be asserted if an authentic review record exists.
4. **Review Artifacts & Real Error Logging**:
   Each audited score must possess a verifiable review record documenting initial errors, corrections made, measures reviewed, and unresolved ambiguities.
5. **Validator Hardening & Anti-Synthetic Guards**:
   Validator must enforce measure underflow/overflow, voice duration consistency, explicit rest completeness, tie start/stop closure, and anti-synthetic guards (rejecting suspiciously looping pitch patterns).
6. **Staged Execution & 9-Score Pilot**:
   Before full corpus expansion, a strict 9-score pilot (3 Lyapunov, 3 Arensky, 3 Lyadov) will be transcribed with measure-by-measure source fidelity, error auditing, and dual verification.
