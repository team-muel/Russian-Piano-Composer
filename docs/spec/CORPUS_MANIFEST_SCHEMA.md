# Corpus Manifest Schema Specification

## Overview
This document specifies the canonical schema, role semantics, readiness status, rights requirements, and validation rules for `data/manifests/corpus_manifest.yaml` in the **Russian Piano Composer** project.

## Schema Version
Current schema version: `manifest_version: 1`.

## Corpus Roles vs Readiness Status
- **`role`**: Describes the scientific role of the corpus in the research pipeline.
- **`readiness_status`**: Controls whether the source may be downloaded or ingested into the pipeline.

### Scientific Roles (`role`)
| Role | Meaning | Generative Pipeline Eligible |
| :--- | :--- | :--- |
| `GENERATIVE_RUSSIAN` | Target Russian late-Romantic / early-modern solo piano repertoire | **YES** (if `rights_status == VERIFIED`, `rights_review_required == false`, and `readiness_status == PROVENANCE_READY`) |
| `CONTROL_NON_RUSSIAN` | Non-Russian evaluation data for style discrimination & controls | **NO** (Strictly excluded from generation) |
| `PROVISIONAL` | Repertoire under study; pending rights or scope verification | **NO** |
| `EXCLUDED` | Documented source deliberately excluded from research pipeline | **NO** |

### Readiness Status (`readiness_status`)
| Status | Meaning |
| :--- | :--- |
| `PROVENANCE_READY` | Upstream repository pin, license, and score inventory are 100% verified. Ready for acquisition. |
| `REVIEW_REQUIRED` | Upstream license conflict, NC clause, or unverified claims present. **Blocked from acquisition/ingestion.** |
| `UNVERIFIED` | Upstream pin or metadata incomplete. **Blocked from acquisition/ingestion.** |
| `BLOCKED` | Explicitly blocked due to legal, rights, or provenance issues. |

## Source Commit SHA Validation
Every source pin (`source_commit` and `meta_repository_commit`) must be an exact **40-character lowercase hexadecimal Git commit SHA** matching:
```regex
^[0-9a-f]{40}$
```
Synthetic placeholder patterns (such as `a1b2c3d4...`, `c1c2c3c4...`, `l1l2...`, `s1s2...`, or `00000000...`) are strictly prohibited and fail schema validation.

## License Evidence & NonCommercial Tracking
Each registered `CorpusSource` records multi-source evidence via `license_claims`:

- `source_type`: Upstream metadata file (`README`, `LICENSE`, `CITATION_CFF`, `ZENODO`).
- `value`: License string observed in that specific file (e.g., `CC BY-NC-SA 4.0`, `CC-BY-NC-4.0`).
- `source_url`: URL to the upstream metadata file.
- `is_non_commercial`: Boolean flag explicitly indicating whether NonCommercial restrictions apply.

Where upstream files express conflicting license strings (e.g. `CC BY-NC-SA 4.0` in `README` vs `CC-BY-NC-4.0` in `CITATION.cff`), `rights_status` is set to `REVIEW_REQUIRED` and `rights_review_required` is set to `true`. This causes `generative_eligible` to fail closed (`False`).

## Precise Count Metrics
- `score_entry_count`: Number of distinct score entries / TSV rows / movement folders (e.g. 19 for Medtner, 22 for Rachmaninoff Op. 42).
- `musical_piece_count`: Count of distinct musical pieces/variations (e.g. 20 variations for Rachmaninoff Op. 42, 26 for Liszt).
- `work_cycle_count`: Count of overall opus/work cycles (e.g. 7 for Medtner, 1 for Rachmaninoff Op. 42).
- `source_file_count`: Total raw score files in source repository (e.g. 135 for Medtner, 24 for Rachmaninoff Op. 42).
- `representative_of_full_composer_output`: Explicit flag indicating whether dataset represents composer's full piano output.

## Fail-Closed Principles
1. **No Defaulting**: Missing or unknown roles raise immediate validation errors. An unknown source NEVER defaults to `GENERATIVE_RUSSIAN`.
2. **Rights Gate**: Pending rights review (`rights_review_required: true` or `readiness_status != PROVENANCE_READY`) blocks acquisition and generative pipeline eligibility.
3. **Unique Identifiers**: `corpus_id` must be non-empty, lowercase ASCII, and unique across the manifest.
4. **Strict Top-Level Key Validation**: Unknown top-level keys in `corpus_manifest.yaml` trigger validation failures.

## Logical Manifest Hash
The logical manifest hash is computed deterministically:
$$\text{Hash} = \text{SHA256}(\text{CanonicalJSON}(\text{ManifestData}))$$
This fingerprint is a full 64-character lowercase hexadecimal string recorded in experiment lineage to detect dataset definition changes regardless of YAML formatting/whitespace modifications.
