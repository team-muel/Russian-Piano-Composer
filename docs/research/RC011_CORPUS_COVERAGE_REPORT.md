# RC-011 Corpus Coverage & Missingness Audit Report

## 1. Corpus Summary
- **Total Ingested Canonical Scores**: 141
- **Total Evaluated Scores**: 141
- **Coverage Rate**: 100.0% (141 / 141)
- **Canonical Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`

---

## 2. Per-Corpus Coverage Breakdown

| Corpus Source ID | Composer | Role | Total Pieces | Extracted | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tchaikovsky_seasons` | Tchaikovsky | GENERATIVE_RUSSIAN | 12 | 12 | 100% Complete |
| `scriabin_preludes` | Scriabin | GENERATIVE_RUSSIAN | 24 | 24 | 100% Complete |
| `medtner_tales` | Medtner | GENERATIVE_RUSSIAN | 24 | 24 | 100% Complete |
| `chopin_preludes` | Chopin | CONTROL_NON_RUSSIAN | 24 | 24 | 100% Complete |
| `schumann_kinderszenen` | Schumann | CONTROL_NON_RUSSIAN | 13 | 13 | 100% Complete |
| `liszt_transcendental` | Liszt | CONTROL_NON_RUSSIAN | 12 | 12 | 100% Complete |
| `brahms_op116_119` | Brahms | CONTROL_NON_RUSSIAN | 20 | 20 | 100% Complete |
| `rachmaninoff_preludes` | Rachmaninoff | GENERATIVE_RUSSIAN | 12 | 12 | 100% Complete |
| **Total** | | | **141** | **141** | **100.0%** |

---

## 3. Availability Matrix & Missingness Audit

- **Total Data Points**: $141 \times 56 = 7,896$ cells
- **`AVAILABLE` Cells**: 7,782 (98.56%)
- **`STRUCTURAL_ZERO` Cells**: 114 (1.44%)
- **`UNAVAILABLE` Cells**: 0 (0.00%)
- **Failed / Exception Pieces**: 0 (0.00%)

### Interpretation of `STRUCTURAL_ZERO` Cells:
1. `tonal_circle5_distance_mean` / `tonal_circle5_distance_max` (42 instances): Short preludes that maintain a single unmodulated tonal center throughout.
2. `cadence_deceptive_proxy_rate` (28 instances): Brief vignettes with purely authentic or plagal cadential endings and no deceptive $\hat{5} \to \hat{6}$ motions.
3. `form_ctu_first_occurrence_mean` / `form_ctu_recurrence_dispersion` (44 instances): Pieces where unsupervised discovery found 0 or 1 thematic unit within the discovery region.

Zero cells resulted in `UNAVAILABLE`, demonstrating complete mathematical robustness across all 141 pieces in the canonical dataset.
