# Corpus Sources V1 Research Documentation

## Verified Seed Datasets (RC-006B Provenance Integrity Audit)

Meta-Repository Pin: **`DCMLab/distant_listening_corpus` @ `12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d`**

| Corpus ID | Direct Repository | Pinned Commit SHA | Score Entries | Pieces | Works | Files | Upstream README Claim | CITATION.cff Claim | Zenodo Claim | Conflict Status | Role | Readiness | Rights Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `dcml_medtner_tales` | `DCMLab/medtner_tales` | `1d2e58ba8d329463829e45e75900af43be4256bf` | 19 | 19 | 7 | 135 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_rachmaninoff_op42` | `DCMLab/rachmaninoff_piano` | `a73f3246a764215863000357c81309b210a43f15` | 22 | 20 | 1 | 24 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_tchaikovsky_seasons` | `DCMLab/tchaikovsky_seasons` | `5af15033c5f9c282f38fcf71234b86349e61e8c3` | 12 | 12 | 1 | 97 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_chopin_mazurkas` | `DCMLab/chopin_mazurkas` | `5931135e614985023b96de2a291c74b7ef90b287` | 56 | 56 | 56 | 390 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_liszt_annees` | `DCMLab/liszt_pelerinage` | `f1cfd308adba5763aad3a18885eac48d42449fc4` | 19 | 26 | 3 | 134 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_schumann_kinderszenen` | `DCMLab/schumann_kinderszenen` | `ee929c1556bc937fe1ea7303cac4476e37caa4d1` | 13 | 13 | 1 | 92 | `CC BY-NC-SA 4.0` | `CC-BY-NC-4.0` | `CC-BY-NC-SA-4.0` | **CONFLICT** | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |

---

### Russian Generative Repertoire Candidates (`GENERATIVE_RUSSIAN`)

1. **`dcml_medtner_tales`**: Nikolai Medtner — Skazki (Fairy Tales) for Solo Piano
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **Meta-Repository Pin**: `DCMLab/distant_listening_corpus` @ `12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d`
   - **Submodule Commit SHA**: `1d2e58ba8d329463829e45e75900af43be4256bf`
   - **License Claim Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` whereas `README.md` and `.zenodo.json` state `CC BY-NC-SA 4.0`.
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`
   - **Scope & Coverage**: 19 score entries across 7 Skazki cycles for solo piano (Op. 8, Op. 14, Op. 26, Op. 34, Op. 35, Op. 42, Op. 48).

2. **`dcml_rachmaninoff_op42`**: Sergei Rachmaninoff — Variations on a Theme of Corelli, Op. 42
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **Meta-Repository Pin**: `DCMLab/distant_listening_corpus` @ `12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d`
   - **Submodule Commit SHA**: `a73f3246a764215863000357c81309b210a43f15`
   - **License Claim Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` whereas `README.md` and `.zenodo.json` state `CC BY-NC-SA 4.0`.
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`
   - **Scope & Coverage**: Sergei Rachmaninoff, Variations on a Theme of Corelli, Op. 42 (Solo Piano). 22 score entries representing 20 variations + Theme, Intermezzo, Coda across 24 score files. `representative_of_full_composer_output: false`.

3. **`dcml_tchaikovsky_seasons`**: Pyotr Ilyich Tchaikovsky — The Seasons, Op. 37b
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **Meta-Repository Pin**: `DCMLab/distant_listening_corpus` @ `12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d`
   - **Submodule Commit SHA**: `5af15033c5f9c282f38fcf71234b86349e61e8c3`
   - **License Claim Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` whereas `README.md` and `.zenodo.json` state `CC BY-NC-SA 4.0`.
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`
   - **Scope & Coverage**: Complete 12 character pieces (12 score entries, 97 total repository files).

---

### Non-Russian Control Repertoire (`CONTROL_NON_RUSSIAN`)

1. **`dcml_chopin_mazurkas`**: Frédéric Chopin — Mazurkas (Solo Piano)
   - **Submodule Commit SHA**: `5931135e614985023b96de2a291c74b7ef90b287`
   - **License Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` vs `README.md` `CC BY-NC-SA 4.0`.
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`

2. **`dcml_liszt_annees`**: Franz Liszt — Années de Pèlerinage (Solo Piano)
   - **Submodule Commit SHA**: `f1cfd308adba5763aad3a18885eac48d42449fc4`
   - **License Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` vs `README.md` `CC BY-NC-SA 4.0`.
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`

3. **`dcml_schumann_kinderszenen`**: Robert Schumann — Kinderszenen, Op. 15 (Solo Piano)
   - **Submodule Commit SHA**: `ee929c1556bc937fe1ea7303cac4476e37caa4d1`
   - **License Conflict**: `CITATION.cff` states `CC-BY-NC-4.0` vs `README.md` `CC BY-NC-SA 4.0`.
   - **Readiness & Rights Status**: `readiness_status: REVIEW_REQUIRED`, `rights_review_required: true`

---

## Provenance Integrity & Governance Policies

### 1. License Evidence vs Normalization
Observed license claims from `README`, `CITATION.cff`, and `.zenodo.json` are captured separately. Where upstream claims disagree (e.g., `CC-BY-NC-4.0` in `CITATION.cff` vs `CC BY-NC-SA 4.0` in `README.md`), the normalized license is marked as `UNRESOLVED` and `rights_review_required` remains `true`.

### 2. Readiness State vs Scientific Role
- **Corpus Role** (`GENERATIVE_RUSSIAN` vs `CONTROL_NON_RUSSIAN`) defines the musical function in research.
- **Readiness Status** (`PROVENANCE_READY`, `REVIEW_REQUIRED`, `UNVERIFIED`, `BLOCKED`) controls whether score files may be downloaded or ingested. All sources currently remain `REVIEW_REQUIRED`.

### 3. Absolute SHA Pinning
Every registered source must pin an exact 40-character lowercase hex Git SHA verified against the upstream repository. No floating branches, tags, or synthetic placeholder SHAs are permitted.

### 4. Zero Score Ingestion Policy
Until every acquisition source achieves `readiness_status: PROVENANCE_READY` (or explicit legal waiver), no score files will be downloaded to `data/raw` or ingested into the scientific data pipeline.
