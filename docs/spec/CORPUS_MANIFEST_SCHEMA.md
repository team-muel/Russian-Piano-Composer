# Corpus Manifest Schema Specification

## Overview
This document specifies the canonical schema, role semantics, rights requirements, and validation rules for `data/manifests/corpus_manifest.yaml` in the **Russian Piano Composer** project.

## Schema Version
Current schema version: `manifest_version: 1`.

## Corpus Roles
Every registered corpus entry must explicitly declare a `role`:

| Role | Meaning | Generative Pipeline Eligible |
| :--- | :--- | :--- |
| `GENERATIVE_RUSSIAN` | Target Russian late-Romantic / early-modern solo piano repertoire | **YES** (if `rights_status == VERIFIED` and `rights_review_required == false`) |
| `CONTROL_NON_RUSSIAN` | Non-Russian evaluation data for style discrimination & controls | **NO** (Strictly excluded) |
| `PROVISIONAL` | Repertoire under study; pending rights or scope verification | **NO** |
| `EXCLUDED` | Documented source deliberately excluded from research pipeline | **NO** |

## License Evidence & NonCommercial Tracking
To prevent licensing ambiguity, each registered `CorpusSource` records multi-source evidence via `license_claims`:

- `source_type`: Upstream metadata file (`README`, `LICENSE`, `CITATION_CFF`, `ZENODO`).
- `value`: License string observed in that specific file (e.g., `CC BY-NC-SA 4.0`, `CC-BY-NC-SA-4.0`).
- `source_url`: URL to the upstream metadata file.
- `is_non_commercial`: Boolean flag explicitly indicating whether NonCommercial restrictions apply.

Where upstream files express conflicting license strings (e.g. `CC BY-NC-SA 4.0` in `README` vs `CC-BY-NC-4.0` in `CITATION.cff`), `rights_status` is set to `REVIEW_REQUIRED` and `rights_review_required` is set to `true`. This causes `generative_eligible` to fail closed (`False`).

## File Counts vs. Musical Work Counts
- `source_file_count`: Total count of source files in the dataset (e.g. 24 score files for Rachmaninoff Op. 42 due to split movement files).
- `piece_count`: Count of distinct musical movements/pieces (e.g. 20 variations for Rachmaninoff Op. 42).
- `work_count`: Count of overall opus/work cycles (e.g. 1 work cycle for Rachmaninoff Op. 42).
- `representative_of_full_composer_output`: Explicit flag indicating whether dataset represents composer's full piano output.

## Fail-Closed Principles
1. **No Defaulting**: Missing or unknown roles raise immediate validation errors. An unknown source NEVER defaults to `GENERATIVE_RUSSIAN`.
2. **Rights Gate**: Pending rights review (`rights_review_required: true`) blocks acquisition and generative pipeline eligibility.
3. **Unique Identifiers**: `corpus_id` must be non-empty, lowercase ASCII, and unique across the manifest.
4. **Strict Top-Level Key Validation**: Unknown top-level keys in `corpus_manifest.yaml` trigger validation failures.

## Logical Manifest Hash
The logical manifest hash is computed deterministically:
$$\text{Hash} = \text{SHA256}(\text{CanonicalJSON}(\text{ManifestData}))$$
This fingerprint is a full 64-character lowercase hexadecimal string recorded in experiment lineage to detect dataset definition changes regardless of YAML formatting/whitespace modifications.
