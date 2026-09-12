# Corpus Sources V1 Research Documentation

## Verified Seed Datasets (RC-006C Finalized Count Semantics)

Meta-Repository Pin: **`DCMLab/distant_listening_corpus` @ `12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d`**

| Corpus ID | Direct Repository | Pinned Commit SHA | Score Entries | Variations | Pieces | Works / Catalog Groups | Notation Score Files | Tabular TSV Artifacts | Scope Completeness | Role | Readiness | Rights Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `dcml_medtner_tales` | `DCMLab/medtner_tales` | `1d2e58ba8d329463829e45e75900af43be4256bf` | 19 | — | 19 | 7 (`Op.8`..`Op.48`) | 19 (`.mscx`) | 76 (`.tsv`) | `COMPLETE_FOR_DECLARED_SCOPE` | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_rachmaninoff_op42` | `DCMLab/rachmaninoff_piano` | `a73f3246a764215863000357c81309b210a43f15` | 22 | 20 | — | 1 (`Op. 42`) | 24 (`.mscx`) | 88 (`.tsv`) | `COMPLETE_FOR_DECLARED_SCOPE` | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_tchaikovsky_seasons` | `DCMLab/tchaikovsky_seasons` | `5af15033c5f9c282f38fcf71234b86349e61e8c3` | 12 | — | 12 | 1 (`Op. 37b`) | 12 (`.mscx`) | 48 (`.tsv`) | `COMPLETE_FOR_DECLARED_SCOPE` | `GENERATIVE_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_chopin_mazurkas` | `DCMLab/chopin_mazurkas` | `5931135e614985023b96de2a291c74b7ef90b287` | 56 | — | 56 | — | 56 (`.mscx`) | 224 (`.tsv`) | `COMPLETE_FOR_DECLARED_SCOPE` | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_liszt_annees` | `DCMLab/liszt_pelerinage` | `f1cfd308adba5763aad3a18885eac48d42449fc4` | 19 | — | — | 3 (`S.160`, `S.161`, `S.162`) | 19 (`.mscx`) | 76 (`.tsv`) | `PARTIAL_FOR_DECLARED_SCOPE` | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |
| `dcml_schumann_kinderszenen` | `DCMLab/schumann_kinderszenen` | `ee929c1556bc937fe1ea7303cac4476e37caa4d1` | 13 | — | 13 | 1 (`Op. 15`) | 13 (`.mscx`) | 52 (`.tsv`) | `COMPLETE_FOR_DECLARED_SCOPE` | `CONTROL_NON_RUSSIAN` | `REVIEW_REQUIRED` | `true` |

---

### Count Metric Definitions

1. **`score_entry_count`**: Number of canonical encoded score IDs in the pinned source inventory (derived from `len(score_entry_ids)`).
2. **`variation_number_count`**: Count of numbered variations for variation cycles (e.g. 20 for Rachmaninoff Op. 42).
3. **`catalog_group_count`**: Count of distinct catalog groups (e.g. 7 for Medtner, 3 for Liszt S.160/S.161/S.162).
4. **`musical_piece_count`**: Count of distinct musical pieces where 1-to-1 piece mapping is unambiguous. (Omitted for Rachmaninoff Op. 42 and Liszt Années to avoid conflating formal movement sections or unencoded external repertoire).
5. **`work_cycle_count`**: Number of overall opus or work cycles.
6. **`notation_score_file_count`**: Count of MuseScore `.mscx`/`.mscz` notation score files in the source repository.
7. **`tabular_artifact_file_count`**: Count of tabular data TSV files (`.notes.tsv`, `.measures.tsv`, `.harmonies.tsv`, etc.).

---

### Scope Completeness vs. Repertoire Representation

- **`scope_completeness`**: Reflects whether the pinned source contains all pieces for its declared scope (e.g., `PARTIAL_FOR_DECLARED_SCOPE` for Liszt because S.163 is absent).
- **`representative_of_full_composer_output`**: Boolean flag indicating whether the dataset represents a composer's full piano output (e.g., `false` for Rachmaninoff Op. 42).
