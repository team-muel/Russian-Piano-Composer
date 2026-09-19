# Russian-vs-Control Discriminative Music Science Evaluation (V1)
## RC-010 Scientific Research Report

---

### 1. Lineage & Canonical Hash Registry

| Lineage Attribute | Hash / Identifier |
| :--- | :--- |
| **Master Baseline Commit** | `2aed82a4f13aa161743b25e30ad879baadc68b3f` |
| **Canonical Corpus Manifest Hash** | `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212` |
| **RC-009A Schema Semantic Hash** | `55a388b490dda3089d3073463818edcbc60abf0bcbc9dd114cd5a28032976516` |
| **RC-009A Policy Hash** | `46ac0709d3b34b8e930b6f2d09723ca658cd7f29c204f235b0814f8c2a86150e` |
| **RC-009B Candidate Set Hash** | `43fda7ba9503df0650fa4e2fb03ff897452a90adf225650d2d785d71a6f6ba8d` |
| **RC-009B Discovery Policy Hash** | `df0810aa9601131df59e1341d6281ce339e1d97b8c993d0baf453fa4a31f0367` |
| **CTU Schema Semantic Hash** | `03e8103ae9d7d534ded951b781ee6d43269a046fc787c543029c5f9ce3dd0ec1` |
| **Representation Semantic Hash** | `967c42a2f47e16dbc6ce3b160ff56284298c73524b46133b6df116ef06db3539` |
| **Similarity Semantic Hash** | `9cdd0387050e9c4aa7025f333da975ed02e453b345ebda3622266343fdb475e2` |
| **CTU Style Feature Schema V1 Hash** | `3806cd743b1c97230c015c25136849f8694235814ed0083935ed78f9fe92dca4` |
| **MODEL_A Schema Hash** | `a825ea8f33a88fa6588e1bb4e6c9644c9c12c79824c6e9eca8eb7e162b531550` |
| **MODEL_B Schema Hash** | `9a2839f33a90fbfed7c487474f6dd6d399a1603921af1759966d89b9061506d4` |
| **MODEL_C Composite Schema Hash** | `cb15c54c1253003f248cffe0d5442fe45da05984fea3c2b07bf74306247bf6df` |
| **Role-Blind Feature Matrix Hash (MODEL_C)** | `e7216079e62eb610c9e8f69442535742d08e23c0158f939ae2443e6a9c6da440` |
| **Composer Label Assignment Hash** | `a9af08f4360b0d11abc7e416a12f6695778d15adccb9efed762a141ebf2502cb` |
| **9-Fold Composer Split Plan Hash** | `4ad2aa5f089ec8d0ea9ea5db84f5c4aeebd32d7356402147466ef3631216df8d` |
| **Primary Model Specification Hash** | `5535389cfca255e67f7a8e38dd933d59740a012ff33327c9cc541dcab7ff8db9` |
| **Composer Weighting Policy Hash** | `12500a37a7949fdb812ab34044cb2db3b99fe490d1cbbd113bb39be8b3f37786` |
| **20-Composer Permutation Plan Hash** | `20011b5f8c4b6c5e4483165daae34dea70649cf4c79a4c238c77b1839d4c37f5` |
| **Evaluation Result Hash** | `3387923be44a665c526f3187c951dd9b658c614e88d1fa1bf5c5373557ead4ea` |
| **Bundle Lineage Hash** | `ed0749b81d897089715d3b8a013b0d7dafcbc5bc4fd0849cd2b4abe6174c5247` |

---

### 2. Executive Summary & Primary Empirical Status

```text
EMPIRICAL STYLE STATUS = RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED
```

When entire composers are held out during model fitting, symbolic musical information (including RC-009A category A piece-level features and RC-009B thematic CTU structural features) fails to distinguish the Russian composer corpus (Medtner, Rachmaninoff, Tchaikovsky) from the non-Russian control corpus (Chopin, Liszt, Schumann).

- **Primary MODEL_C MACRO_PAIR_AUC**: `0.2964` (below chance level `0.5000`)
- **Folds with AUC > 0.50**: `1` of `9` (Fold 5: Rachmaninoff vs Schumann, `AUC = 0.5315`)
- **Exact 20-Permutation Rank**: `18` / `20` (Observed Rank Interval: `17-18` / `20`, tied with complement assignment)
- **Tied Assignments Count**: `2`
- **Exact Permutation $p$-value**: `0.9000` (Extreme count `18` / `20`)
- **Minimum Attainable $p$-value**: `0.1000` (due to label-inversion complement symmetry across the 10 complement pairs)
- **Primary Missing Values**: `0` (Strict fail-closed verified across all 141 pieces)

---

### 3. Outer 9-Fold Composer-Held-Out Evaluation Matrix

| Fold | Held-Out Russian | Held-Out Control | Rus Test | Ctrl Test | MODEL_A AUC | MODEL_B AUC | MODEL_C AUC | MODEL_C BalAcc |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | Medtner | Chopin | 19 | 56 | 0.1288 | 0.5479 | 0.2030 | 0.3924 |
| 1 | Medtner | Liszt | 19 | 19 | 0.2327 | 0.4820 | 0.2742 | 0.3684 |
| 2 | Medtner | Schumann | 19 | 13 | 0.1822 | 0.3603 | 0.2024 | 0.2328 |
| 3 | Rachmaninoff | Chopin | 22 | 56 | 0.4229 | 0.2776 | 0.3377 | 0.3604 |
| 4 | Rachmaninoff | Liszt | 22 | 19 | 0.2847 | 0.4689 | 0.2799 | 0.3900 |
| 5 | Rachmaninoff | Schumann | 22 | 13 | 0.5385 | 0.5839 | 0.5315 | 0.5559 |
| 6 | Tchaikovsky | Chopin | 12 | 56 | 0.4479 | 0.4747 | 0.3958 | 0.4643 |
| 7 | Tchaikovsky | Liszt | 12 | 19 | 0.1053 | 0.1974 | 0.0965 | 0.1776 |
| 8 | Tchaikovsky | Schumann | 12 | 13 | 0.4038 | 0.4103 | 0.3462 | 0.3077 |
| **Macro** | **All 9 Folds** | **Combined** | **53** | **88** | **0.3052** | **0.4226** | **0.2964** | **0.3610** |

---

### 4. Model Feature Set Ablation Comparison

| Feature Model | Description | Feature Count | MACRO_PAIR_AUC | Mean BalAcc | Mean Sens | Mean Spec | Mean Brier |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **MODEL_A** | RC-009A Category A Piece Features Only | 32 | 0.3052 | 0.3681 | 0.2223 | 0.5138 | 0.2743 |
| **MODEL_B** | CTU Structural Style Features V1 Only | 14 | 0.4226 | 0.4402 | 0.3644 | 0.5160 | 0.2589 |
| **MODEL_C** | Primary Combined Feature Model (A + B) | 46 | 0.2964 | 0.3610 | 0.2330 | 0.4890 | 0.2748 |

- **$\Delta(\text{MODEL\_C} - \text{MODEL\_A})$**: `-0.0088`
- **$\Delta(\text{MODEL\_C} - \text{MODEL\_B})$**: `-0.1262`

---

### 5. Exhaustive 20-Composer Permutation Test Distribution & Complement Symmetry

Each of the 20 exact partitions constructs its own dynamic assignment-specific $3 \times 3$ outer split plan ($9$ outer folds per assignment, $180$ folds evaluated in total). Under L2-regularized logistic regression with symmetric z-scoring, label inversion ($0 \leftrightarrow 1$) yields identical ROC AUC curves ($\text{AUC}(A) = \text{AUC}(A')$), forming $10$ exact complement pairs.

| Assign Index | Complement Index | Class 1 Composers | Class 0 Composers | MACRO_PAIR_AUC | Folds > 0.50 | Observed Assignment |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: |
| 0 | 19 | Chopin, Liszt, Medtner | Rachmaninoff, Schumann, Tchaikovsky | 0.7036 | 8 | No |
| 1 | 18 | Chopin, Liszt, Rachmaninoff | Medtner, Schumann, Tchaikovsky | 0.6170 | 7 | No |
| 2 | 17 | Chopin, Liszt, Schumann | Medtner, Rachmaninoff, Tchaikovsky | 0.2964 | 1 | No (Complement) |
| 3 | 16 | Chopin, Liszt, Tchaikovsky | Medtner, Rachmaninoff, Schumann | 0.7734 | 9 | No |
| 4 | 15 | Chopin, Medtner, Rachmaninoff | Liszt, Schumann, Tchaikovsky | 0.5042 | 4 | No |
| 5 | 14 | Chopin, Medtner, Schumann | Liszt, Rachmaninoff, Tchaikovsky | 0.5771 | 6 | No |
| 6 | 13 | Chopin, Medtner, Tchaikovsky | Liszt, Rachmaninoff, Schumann | 0.6623 | 8 | No |
| 7 | 12 | Chopin, Rachmaninoff, Schumann | Liszt, Medtner, Tchaikovsky | 0.4958 | 4 | No |
| 8 | 11 | Chopin, Rachmaninoff, Tchaikovsky | Liszt, Medtner, Schumann | 0.5810 | 6 | No |
| 9 | 10 | Chopin, Schumann, Tchaikovsky | Liszt, Medtner, Rachmaninoff | 0.6623 | 8 | No |
| 10 | 9 | Liszt, Medtner, Rachmaninoff | Chopin, Schumann, Tchaikovsky | 0.6623 | 8 | No |
| 11 | 8 | Liszt, Medtner, Schumann | Chopin, Rachmaninoff, Tchaikovsky | 0.5810 | 6 | No |
| 12 | 7 | Liszt, Medtner, Tchaikovsky | Chopin, Rachmaninoff, Schumann | 0.4958 | 4 | No |
| 13 | 6 | Liszt, Rachmaninoff, Schumann | Chopin, Medtner, Tchaikovsky | 0.6623 | 8 | No |
| 14 | 5 | Liszt, Rachmaninoff, Tchaikovsky | Chopin, Medtner, Schumann | 0.5771 | 6 | No |
| 15 | 4 | Liszt, Schumann, Tchaikovsky | Chopin, Medtner, Rachmaninoff | 0.5042 | 4 | No |
| 16 | 3 | Medtner, Rachmaninoff, Schumann | Chopin, Liszt, Tchaikovsky | 0.7734 | 9 | No |
| 17 | 2 | Medtner, Rachmaninoff, Tchaikovsky | Chopin, Liszt, Schumann | 0.2964 | 1 | **YES (Observed)** |
| 18 | 1 | Medtner, Schumann, Tchaikovsky | Chopin, Liszt, Rachmaninoff | 0.6170 | 7 | No |
| 19 | 0 | Rachmaninoff, Schumann, Tchaikovsky | Chopin, Liszt, Medtner | 0.7036 | 8 | No |

- **Observed MACRO_PAIR_AUC**: `0.2964`
- **Observed Rank**: `18` / `20`
- **Observed Rank Interval (Ties)**: `17-18` / `20`
- **Tied Assignments Count**: `2`
- **Extreme Count ($\text{AUC} \ge 0.2964$)**: `18` / `20`
- **Exact $p$-value**: `0.9000`
- **Minimum Attainable $p$-value**: `0.1000`

---

### 6. Feature-Level Descriptive Analysis & Stability

| Feature ID | Family | Rus Mean | Ctrl Mean | Contrast | Exact $p$ | FDR $q$ | Med Coef | Stable |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `contour_ascending_ratio` | MODEL_A | 0.4715 | 0.4304 | +0.0411 | 0.2000 | 1.0000 | +0.0818 | YES |
| `contour_descending_ratio` | MODEL_A | 0.4430 | 0.4629 | -0.0198 | 0.2000 | 1.0000 | -0.0514 | YES |
| `contour_repeat_ratio` | MODEL_A | 0.0622 | 0.0893 | -0.0270 | 0.2000 | 1.0000 | -0.0463 | YES |
| `density_grace_note_ratio` | MODEL_A | 0.0050 | 0.0047 | +0.0003 | 1.0000 | 1.0000 | +0.0253 | NO |
| `density_notes_per_quarter` | MODEL_A | 1.5267 | 1.2591 | +0.2676 | 0.4000 | 1.0000 | +0.0369 | NO |
| `density_rest_ratio` | MODEL_A | 0.1005 | 0.0830 | +0.0174 | 0.6000 | 1.0000 | +0.0660 | NO |
| `density_staff_count` | MODEL_A | 2.0000 | 2.0000 | +0.0000 | 1.0000 | 1.0000 | -0.0336 | NO |
| `density_voice_count` | MODEL_A | 4.3333 | 4.3333 | +0.0000 | 1.0000 | 1.0000 | +0.0266 | NO |
| `interval_direction_change_ratio` | MODEL_A | 0.4421 | 0.4138 | +0.0283 | 0.4000 | 1.0000 | +0.0121 | NO |
| `interval_leap_ratio` | MODEL_A | 0.5281 | 0.4800 | +0.0482 | 0.8000 | 1.0000 | +0.0040 | NO |
| `interval_max_abs_semitones` | MODEL_A | 21.8333 | 24.3333 | -2.5000 | 0.7000 | 1.0000 | -0.0320 | NO |
| `interval_mean_abs_semitones` | MODEL_A | 3.8921 | 3.6308 | +0.2613 | 0.7000 | 1.0000 | -0.0037 | NO |
| `interval_std_abs_semitones` | MODEL_A | 3.5733 | 3.5576 | +0.0157 | 1.0000 | 1.0000 | -0.0395 | NO |
| `interval_step_ratio` | MODEL_A | 0.4719 | 0.5200 | -0.0482 | 0.8000 | 1.0000 | -0.0040 | NO |
| `interval_unison_ratio` | MODEL_A | 0.0622 | 0.0893 | -0.0270 | 0.2000 | 1.0000 | -0.0463 | YES |
| `meter_change_count` | MODEL_A | 0.0000 | 0.3333 | -0.3333 | 1.0000 | 1.0000 | +0.0153 | NO |
| `meter_has_pickup` | MODEL_A | 0.0000 | 0.3333 | -0.3333 | 1.0000 | 1.0000 | -0.0624 | YES |
| `meter_primary_denominator` | MODEL_A | 4.0000 | 4.0000 | +0.0000 | 1.0000 | 1.0000 | +0.0443 | YES |
| `meter_primary_numerator` | MODEL_A | 3.6667 | 3.0000 | +0.6667 | 0.7000 | 1.0000 | +0.0285 | NO |
| `pitch_class_entropy` | MODEL_A | 3.2972 | 3.2260 | +0.0712 | 0.6000 | 1.0000 | +0.0743 | YES |
| `pitch_highest_midi` | MODEL_A | 90.5000 | 87.1667 | +3.3333 | 0.5000 | 1.0000 | +0.0359 | NO |
| `pitch_lowest_midi` | MODEL_A | 30.0000 | 30.1667 | -0.1667 | 1.0000 | 1.0000 | -0.0005 | NO |
| `pitch_mean_midi` | MODEL_A | 61.8977 | 62.4062 | -0.5086 | 0.7000 | 1.0000 | -0.0049 | NO |
| `pitch_median_midi` | MODEL_A | 62.1667 | 63.0000 | -0.8333 | 0.5000 | 1.0000 | -0.0093 | NO |
| `pitch_range_semitones` | MODEL_A | 61.1667 | 56.1667 | +5.0000 | 0.5000 | 1.0000 | +0.0362 | NO |
| `pitch_std_midi` | MODEL_A | 11.4500 | 10.4799 | +0.9701 | 0.2000 | 1.0000 | +0.0458 | NO |
| `rhythm_duration_mean` | MODEL_A | 2.3972 | 2.8252 | -0.4279 | 0.4000 | 1.0000 | -0.0391 | YES |
| `rhythm_duration_median` | MODEL_A | 2.0000 | 2.6667 | -0.6667 | 1.0000 | 1.0000 | -0.0979 | YES |
| `rhythm_duration_range_ratio` | MODEL_A | 16.0000 | 16.6667 | -0.6667 | 1.0000 | 1.0000 | +0.0096 | NO |
| `rhythm_duration_std` | MODEL_A | 1.6891 | 1.7590 | -0.0699 | 0.7000 | 1.0000 | -0.0163 | NO |
| `rhythm_longest_duration` | MODEL_A | 12.0000 | 12.0000 | +0.0000 | 1.0000 | 1.0000 | -0.0602 | NO |
| `rhythm_shortest_duration` | MODEL_A | 0.8333 | 0.8333 | +0.0000 | 1.0000 | 1.0000 | -0.0294 | NO |
| `ctu_active_voice_stream_mean` | MODEL_B | 2.8667 | 2.5000 | +0.3667 | 0.3000 | 1.0000 | +0.0438 | YES |
| `ctu_attack_density_per_measure_mean` | MODEL_B | 16.8944 | 13.3222 | +3.5722 | 0.4000 | 1.0000 | +0.0179 | NO |
| `ctu_discovery_score_max` | MODEL_B | 0.9992 | 1.0000 | -0.0008 | 1.0000 | 1.0000 | -0.0781 | YES |
| `ctu_discovery_score_mean` | MODEL_B | 0.9623 | 1.0000 | -0.0377 | 0.4000 | 1.0000 | -0.0704 | NO |
| `ctu_discovery_score_std` | MODEL_B | 0.0248 | 0.0000 | +0.0248 | 0.4000 | 1.0000 | +0.0415 | NO |
| `ctu_melodic_abs_interval_mean` | MODEL_B | 2.8807 | 2.9397 | -0.0590 | 0.9000 | 1.0000 | -0.0441 | YES |
| `ctu_melodic_interval_diversity` | MODEL_B | 0.2233 | 0.2404 | -0.0170 | 0.7000 | 1.0000 | -0.0448 | YES |
| `ctu_pitchclass_entropy` | MODEL_B | 2.9194 | 2.7770 | +0.1423 | 0.3000 | 1.0000 | +0.0367 | YES |
| `ctu_pitchclass_max_share` | MODEL_B | 0.2475 | 0.2563 | -0.0088 | 0.9000 | 1.0000 | -0.0370 | YES |
| `ctu_rhythm_ratio_abs_deviation_mean` | MODEL_B | 0.2175 | 0.2720 | -0.0544 | 0.9000 | 1.0000 | -0.0663 | YES |
| `ctu_span_length_mean` | MODEL_B | 1.3000 | 1.2667 | +0.0333 | 1.0000 | 1.0000 | +0.0108 | NO |
| `ctu_span_length_std` | MODEL_B | 0.5338 | 0.5963 | -0.0624 | 1.0000 | 1.0000 | +0.0068 | NO |
| `ctu_texture_attack_mean` | MODEL_B | 2.3271 | 2.2873 | +0.0398 | 1.0000 | 1.0000 | -0.0163 | NO |
| `ctu_texture_attack_std` | MODEL_B | 1.2340 | 1.1410 | +0.0930 | 0.6000 | 1.0000 | -0.0023 | NO |

---

### 7. Composer-Level Generalization Held-Out Performance

| Composer | Corpus Role / Class | Piece Count | Held-Out Mean ROC AUC |
| :--- | :--- | :---: | :---: |
| **Medtner** | Russian (Class 1) | 19 | 0.2266 |
| **Rachmaninoff** | Russian (Class 1) | 22 | 0.3830 |
| **Tchaikovsky** | Russian (Class 1) | 12 | 0.2795 |
| **Chopin** | Control (Class 0) | 56 | 0.3122 |
| **Liszt** | Control (Class 0) | 19 | 0.2169 |
| **Schumann** | Control (Class 0) | 13 | 0.3600 |

---

### 8. Scientific Interpretation & Mandatory Limitations Statement

#### Scientific Interpretation
Under rigorous composer-held-out validation, models trained on subset composers fail to generalize style boundary distinctions to unseen held-out composers. Instead of learning a shared "Russian" vs "Control" style signal, linear models fit composer-specific idiosyncrasies that do not transfer across composer boundaries. The primary model (MODEL_C) achieves a MACRO_PAIR_AUC of `0.2964`, which is below 0.50 in composer-held-out evaluation. Furthermore, under exact 20-assignment permutation testing ($p = 0.9000$, rank interval `17-18 / 20`), the observed partition received one of the lower MACRO_PAIR_AUC values among the 20 exact label assignments (tied with its label-inversion complement).

#### Mandatory Scientific Limitations
1. Only six composers are represented in the canonical corpus (Medtner, Rachmaninoff, Tchaikovsky vs. Chopin, Liszt, Schumann).
2. Composer identity and national/style class are structurally confounded in source corpora.
3. Composer-pair hold-out reduces memorization risk but does not create independent evidence from unseen historical traditions.
4. Exact permutation inference has 20 composer-label assignments with 10 complement pairs (minimum attainable two-sided $p$-value = 0.10 under label-inversion symmetry; $p \le 0.05$ is structurally unattainable for $N=6$).
5. RC-010 tests discriminability within the canonical six-composer corpus, not a universal definition of Russian music.
6. Human aesthetic judgment is not validated here.
7. Successful discrimination does not by itself justify generative composition (and here, discrimination is NOT supported).

