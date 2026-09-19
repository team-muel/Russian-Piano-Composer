# ADR-010 — Composer-Held-Out Generalization & Exact Composer-Level Permutation Validation

## Status

Accepted

## Context

Previous milestones established canonical score ingestion (RC-001 through RC-007), feature validity auditing (RC-009A), and unsupervised Candidate Thematic Unit (CTU) discovery & validation (RC-009B).

To evaluate whether a statistically significant, reproducible symbolic musical signal distinguishes the Russian piano corpus from non-Russian control corpora without overfitting to composer-specific memorization, a composer-held-out validation architecture is required. Because composer identity and class membership are nested (Medtner/Rachmaninoff/Tchaikovsky $\to$ Russian; Chopin/Liszt/Schumann $\to$ Control), random piece-level train/test splitting is scientifically invalid.

## Decision

1. **Role-Blind Feature Matrix**: Extract piece and CTU features strictly before attaching composer or class labels. Freeze matrix and compute `ROLE_BLIND_FEATURE_MATRIX_HASH`.
2. **Leave-One-Russian + One-Control Composer Pair Out**: Define 9 outer folds (3 Russian $\times$ 3 Control composers). In each fold, hold out exactly 1 Russian and 1 Control composer.
3. **Training-Composer-Balanced Sample Weights**: Assign weights within each training fold so each training composer contributes equal aggregate weight ($w_i = 1 / (N_{\text{pieces, comp}} \cdot N_{\text{comp, train}})$).
4. **Fold-Level Training-Only Standardization**: Fit `StandardScaler` strictly on training pieces per outer fold; held-out test pieces are transformed using training parameters.
5. **Deterministic Primary Classifier**: L2-regularized Logistic Regression ($C=1.0$, `lbfgs` solver, `random_state=42`).
6. **Primary Metric & Macro Aggregation**: Compute ROC AUC per outer fold; primary metric is `MACRO_PAIR_AUC` (mean of 9 fold AUCs).
7. **Exhaustive Exact 20-Composer Permutation Test**: Enumerate all $C(6, 3) = 20$ composer-label assignments and compute $p = \text{count}(\text{AUC} \ge \text{observed}) / 20.0$.
8. **Primary Decision Rule**: Status is `RUSSIAN_CONTROL_SIGNAL_SUPPORTED` iff `MACRO_PAIR_AUC > 0.50`, $p_{\text{exact}} \le 0.05$, and $\ge 6/9$ folds have AUC $> 0.50$.
9. **Primary Model Definition**: `MODEL_C` (`MODEL_A` + `MODEL_B`) is fixed as the primary model. `MODEL_A` and `MODEL_B` are pre-declared ablations.

## Consequences

* Eliminates composer-identity leakage across train and test folds.
* Prevents prolific composers (e.g. Chopin 56 pieces vs Tchaikovsky 12 pieces) from dominating training.
* Provides deterministic, two-process reproducible lineage tracking across all 141 canonical scores.
* Formally isolates empirical signal detection within the canonical 6-composer corpus without claiming universal musicological essence.
