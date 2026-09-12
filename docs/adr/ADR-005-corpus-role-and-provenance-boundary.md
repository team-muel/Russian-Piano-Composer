### Title: ADR-005: Explicit Corpus Role and Provenance Boundary

### Status: Accepted
### Date: 2026-09-13

### Context
Statistical and generative models in the Russian Piano Composer system require training on authentic Russian late-Romantic / early-modern solo piano repertoire while evaluating style discrimination against non-Russian control datasets. Ingesting scores without explicit provenance or allowing control datasets to leak into generative training pipelines creates severe scientific risks (data leakage, false attribution, and non-reproducible research).

### Decision
1. **Explicit Role Assignment**: Every musical dataset must be registered in `data/manifests/corpus_manifest.yaml` with an explicit `role`: `GENERATIVE_RUSSIAN`, `CONTROL_NON_RUSSIAN`, `PROVISIONAL`, or `EXCLUDED`.
2. **Fail-Closed Validation**: Loaders and pipeline tools must fail closed (`load_manifest()` raises validation errors on unknown roles, missing fields, or duplicate IDs). Unknown or unverified sources are NEVER treated as generative by default.
3. **Generative Pipeline Isolation**: `manifest.generative_sources()` returns strictly `GENERATIVE_RUSSIAN` sources with verified rights (`generative_eligible == True`). Control data is strictly isolated to evaluation tools (`control_sources()`).
4. **Solo Piano Preference**: Generative sources must explicitly target `PianoMedium.SOLO_PIANO`. Orchestral reductions, chamber music, and transcriptions are categorized as `PROVISIONAL` unless reviewed.
5. **No Score Ingestion Without Provenance**: No musical file enters raw or interim data directories without being registered in the manifest with pinned versioning (Git commit / release tag), rights status, and SHA-256 file hashing.

### Rejected Alternatives
- **Automatic nationality/role inference**: Rejected because repository titles, file names, or metadata strings do not reliably establish musical repertoire scope or rights.
- **Defaulting unknown data to generative**: Rejected due to catastrophic data contamination risks.
- **Unversioned repository URLs**: Rejected because upstream HEAD changes violate experiment reproducibility.

### Consequences
- **Pros**:
  - Absolute scientific isolation between Russian generative and non-Russian control data.
  - Fail-closed validation prevents accidental data contamination.
  - Reproducible dataset definition via canonical manifest SHA-256 hashing.
- **Cons**:
  - Repertoire requiring manual rights review cannot enter the generative pipeline until fully verified.
