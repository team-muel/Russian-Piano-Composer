### Title: ADR-005: Explicit Corpus Role and Provenance Boundary

### Status: Accepted (Updated RC-006A)
### Date: 2026-09-13

### Context
Statistical and generative models in the Russian Piano Composer system require training on authentic Russian late-Romantic / early-modern solo piano repertoire while evaluating style discrimination against non-Russian control datasets. Ingesting scores without explicit provenance or allowing control datasets to leak into generative training pipelines creates severe scientific risks. Furthermore, incorrect license assumptions (such as treating `CC BY-NC-SA 4.0` as unrestricted `CC-BY-4.0`) introduce legal and ethical risks.

### Decision
1. **Explicit Role Assignment**: Every musical dataset must be registered in `data/manifests/corpus_manifest.yaml` with an explicit `role`: `GENERATIVE_RUSSIAN`, `CONTROL_NON_RUSSIAN`, `PROVISIONAL`, or `EXCLUDED`.
2. **License Evidence & Rights Review Gate**: Each source records multi-file license evidence (`license_claims`). Upstream DCML sources are correctly recorded as `CC BY-NC-SA 4.0` with `is_non_commercial: true`. Sources with license string variations or unreviewed NC terms are flagged with `rights_review_required: true`.
3. **Fail-Closed Eligibility**: `generative_eligible` returns `True` strictly when `role == GENERATIVE_RUSSIAN`, `rights_status == VERIFIED`, and `rights_review_required == false`. Unreviewed or provisional sources fail closed (`generative_eligible == False`).
4. **Source-File vs Musical-Work Differentiation**: Manifest tracks `source_file_count`, `piece_count`, and `work_count` separately (e.g. 24 score files representing 20 variations for Rachmaninoff Op. 42).
5. **Full 64-Character Manifest Hash**: Experiment lineage records the full 64-character SHA-256 hex digest of the canonical logical manifest.

### Rejected Alternatives
- **Blanket CC-BY-4.0 assumption**: Rejected after RC-006A audit revealed DCML sources carry `CC BY-NC-SA 4.0` NonCommercial and ShareAlike terms.
- **Conflating score file count with musical piece count**: Rejected because split-file conventions in upstream repositories obscure musical work boundaries.
- **Defaulting unknown/unreviewed data to generative**: Rejected due to catastrophic contamination and compliance risks.

### Consequences
- **Pros**:
  - Accurate license evidence capturing NonCommercial restrictions.
  - Fail-closed rights review gate prevents unverified datasets from entering model training.
  - Full 64-character golden manifest SHA-256 hash guarantees experiment lineage reproducibility.
- **Cons**:
  - Russian generative candidates remain blocked from acquisition until rights review resolves NonCommercial model training status.
