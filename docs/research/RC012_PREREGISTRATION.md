# Pre-Registration — RC-012 Independent External Composer Confirmation

**Status**: PREREGISTERED & FROZEN  
**Milestone**: RC-012 Independent External Composer Confirmation  
**Parent Milestone**: RC-011 Structural Music Representation (Validated)  
**Parent Commit SHA**: `a72ceda3415571646161d2fab6134012b2e987dc`

---

## 1. Primary Scientific Question

Does the frozen RC-011 56-feature structural representation contain a Russian-vs-Control structural signal that generalizes to never-before-seen composers who played zero role in representation development?

- **Inferential Unit**: Composer ($N = \text{number of independent composers}$).
- **Primary Metric**: Observed composer-level test statistic:
  $$T_{\text{obs}} = \frac{1}{N_{\text{Russian}}} \sum_{c \in \text{Russian}} S_c - \frac{1}{N_{\text{Control}}} \sum_{c \in \text{Control}} S_c$$
  where $S_c = \frac{1}{M_c} \sum_{i=1}^{M_c} z_i$ is the mean predictor decision score for composer $c$.
- **Primary Test**: Exact permutation test across all $C(N, N_{\text{Russian}})$ composer label assignments ($\alpha = 0.05$, one-sided).
- **Secondary Evaluation**: Stratified piece bootstrap (10,000 resamples) reporting 95% confidence intervals for AUROC, Brier score, and piece-level balanced accuracy.

---

## 2. Confirmatory Data Contract Standards & Pre-Condition Gate

To ensure statistical power and guard against pseudoreplication:
1. **Minimum Sample Size**: $\ge 4$ independent Russian late-Romantic composers and $\ge 4$ independent Control composers ($N \ge 8$).
2. **Minimum Piece Count**: $\ge 10$ eligible pieces per composer.
3. **Pre-Condition Gate Rule**:
   If the verified external corpus inventory contains fewer than 4 composers per class satisfying the data contract:
   $$\text{Contract Status} = \mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$
   Execution halts prior to unblinding or confirmatory testing, preserving the negative/inconclusive finding without data leakage or post-hoc threshold relaxation.

---

## 3. Pre-Condition Audit Result

As documented in [`RC012_CONFIRMATORY_CORPUS_INVENTORY.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC012_CONFIRMATORY_CORPUS_INVENTORY.md) and [`RC012A_EXHAUSTIVE_CORPUS_AUDIT.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC012A_EXHAUSTIVE_CORPUS_AUDIT.md):
- **Eligible Independent Control Composers ($\ge 10$ pieces)**:
  - *Edvard Grieg* ($M = 66$)
  - *Claude Debussy* ($M = 53$)
  - *Antonín Dvořák* ($M = 12$)
  - *Béla Bartók* ($M = 40$)
  - *Ludwig van Beethoven* ($M = 91$)
  - $\implies N_{\text{Control}} = 5 \ge 4$ (**SATISFIED**)
- **Eligible Independent Russian Composers ($\ge 10$ pieces)**:
  - *Alexander Scriabin* ($M = 207$)
  - *Modest Mussorgsky* ($M = 18$)
  - *Sergei Prokofiev* ($M = 4$), *Mily Balakirev* ($M = 2$), *Sergei Lyapunov* ($M = 1$), *Anton Rubinstein* ($M = 1$), *Anton Arensky* ($M = 0$), *Aleksandr Glazunov* ($M = 0$), *Anatoly Lyadov* ($M = 0$), *Sergei Taneyev* ($M = 0$), *César Cui* ($M = 0$): Surveyed across open symbolic repositories; none contain $\ge 10$ verified, machine-readable solo piano scores.
  - $\implies N_{\text{Russian}} = 2 < 4$ (**FAILED**)

**Formal Contract Decision**:
$$\mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$
The primary external confirmatory hypothesis is **NOT TESTED** due to **DATA AVAILABILITY FAILURE**.

---

## 4. Frozen Development Predictor Specification

For complete reproducibility and archival closure, the development predictor is fitted on the 141 development scores (from `data/features/structural_v1/structural_matrix.parquet`, verified against `STRUCTURAL_MATRIX_HASH = 7e141a62bed72d10a894d7fa3123619aacce85797b1953423fd8de2b5b069bc0`):
- **Model**: Logistic Regression ($C = 1.0$, $L_2$ regularization, L-BFGS solver, `random_state = 42`).
- **Sample Weights**: Composer-balanced weights $w_{c, i} = \frac{1}{6 \cdot N_c}$ across the 6 development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*).
- **Scaler**: `StandardScaler` fitted exclusively on the weighted development distribution.
- **Predictor Artifact**: To be frozen into `RC012_FROZEN_PREDICTOR_BUNDLE_HASH`.
