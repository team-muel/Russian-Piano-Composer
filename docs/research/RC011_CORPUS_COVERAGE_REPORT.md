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
| `dcml_tchaikovsky_seasons` | Pyotr Ilyich Tchaikovsky | GENERATIVE_RUSSIAN | 12 | 12 | 100% Complete |
| `dcml_rachmaninoff_op42` | Sergei Rachmaninoff | GENERATIVE_RUSSIAN | 22 | 22 | 100% Complete |
| `dcml_medtner_tales` | Nikolai Medtner | GENERATIVE_RUSSIAN | 19 | 19 | 100% Complete |
| `dcml_chopin_mazurkas` | Frédéric Chopin | CONTROL_NON_RUSSIAN | 56 | 56 | 100% Complete |
| `dcml_schumann_kinderszenen` | Robert Schumann | CONTROL_NON_RUSSIAN | 13 | 13 | 100% Complete |
| `dcml_liszt_annees` | Franz Liszt | CONTROL_NON_RUSSIAN | 19 | 19 | 100% Complete |
| **Total** | | | **141** | **141** | **100.0%** |

### Per-Composer Breakdown:
- **Pyotr Ilyich Tchaikovsky**: 12 scores
- **Sergei Rachmaninoff**: 22 scores
- **Nikolai Medtner**: 19 scores
- **Frédéric Chopin**: 56 scores
- **Robert Schumann**: 13 scores
- **Franz Liszt**: 19 scores
- **Total**: 141 scores (53 Russian, 88 Control)

---

## 3. Availability Matrix & Missingness Audit

- **Total Data Points**: $141 \times 56 = 7,896$ cells
- **`AVAILABLE` Cells**: 7,881 (99.81%)
- **`STRUCTURAL_ZERO` Cells**: 15 (0.19%)
- **`UNAVAILABLE` Cells**: 0 (0.00%)
- **Failed / Exception Pieces**: 0 (0.00%)

### Interpretation of `STRUCTURAL_ZERO` Cells:
1. `cadence_deceptive_proxy_rate` (13 instances): Scores with no observed deceptive ($\hat{5} \to \hat{6}$) cadential motions at metric boundaries.
2. `form_ctu_first_occurrence_mean` / `form_ctu_recurrence_dispersion` (2 instances): Scores where unsupervised CTU discovery produced 0 or 1 discovered units in the initial partition.

Zero cells resulted in `UNAVAILABLE`, demonstrating complete mathematical robustness across all 141 pieces in the canonical dataset.
