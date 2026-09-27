# RC-012 Pre-Execution Implementation Lock & Statistical Contract Freeze

## 1. Executive Summary & Governance Authority

This document defines the formal prospective implementation lock and exact mathematical/algorithmic statistical contract for the one-shot confirmatory execution of RC-012.

**Operational Status**: `ARMED_NOT_EXECUTED`  
**Starting HEAD**: `6ee93c80aa6ccb884f1355b44926f45d3caefc84`  
**Execution Authority Record**: [`data/reviews/rc014/rc014_human_access_governance_decision.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/reviews/rc014/rc014_human_access_governance_decision.json)  
**Selected Governance Route**: `Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE`  
**Resumption Status**: `READY_FOR_SEPARATE_ONE_SHOT_EXECUTION`  

### 1.1 Confirmatory Repertoire

The confirmatory evaluation is locked to 9 distinct composers ($N=9$) and 483 pieces ($M=483$):

* **Russian Class ($N_{\text{Russian}} = 4$, $M_{\text{Russian}} = 246$)**:
  1. *Alexander Scriabin* ($M_c = 207$)
  2. *Modest Mussorgsky* ($M_c = 18$)
  3. *Anton Rubinstein* ($M_c = 11$)
  4. *Sergei Prokofiev* ($M_c = 10$)
* **Control Class ($N_{\text{Control}} = 5$, $M_{\text{Control}} = 237$)**:
  1. *Edvard Grieg* ($M_c = 66$)
  2. *Claude Debussy* ($M_c = 54$)
  3. *Ludwig van Beethoven* ($M_c = 91$)
  4. *Béla Bartók* ($M_c = 14$)
  5. *Antonín Dvořák* ($M_c = 12$)

All 9 composers strictly satisfy the preregistered minimum threshold of $M_c \ge 10$ pieces.

---

## 2. Immutable Cryptographic Hash Ledger

| Artifact Description | Canonical File Location | Immutable SHA-256 Hash Binding |
|---|---|---|
| **Confirmatory Corpus Master Freeze** | `data/reviews/rc014/rc014c2a_preunblinding_integrity_audit.json` | `ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e` |
| **Real Feature Cache Matrix** | `data/manifests/rc014c2a_complete_role_blind_feature_cache.json` | `6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7` |
| **Frozen Predictor Bundle** | `models/rc012_predictor/frozen_predictor_bundle.json` | `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926` |
| **Human Access Decision Record** | `data/reviews/rc014/rc014_human_access_governance_decision.json` | `4b50a007e2824ee1223f58a793de993b4537f4db3aa3dd006a17dc7e36ad1b31` |
| **One-Shot Execution Lock Plan** | `data/reviews/rc012/rc012_one_shot_execution_lock.json` | `11685bb1217e67a64c5b610f4cc9afd96436fcb12da79fcbc921d1120e8fe962` |

---

## 3. Mathematical & Algorithmic Statistical Specification

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            RC-012 Confirmatory Statistical Protocol                         │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
      ┌────────────────────────────────────────┴────────────────────────────────────────┐
      ▼                                                                                 ▼
┌───────────────────────────────────────────┐                     ┌───────────────────────────────────────────┐
│           Primary Hypothesis              │                     │     Secondary Classification & CI         │
│                                           │                     │                                           │
│  1. Feature Standardization (56-D)        │                     │  1. Predicted Probability: p_i = σ(z_i)   │
│  2. Piece Logit Scoring: z_i              │                     │  2. Decision Threshold: y_hat = [z_i >= 0]│
│  3. Equal Composer Aggregation: S_c       │                     │  3. AUROC (continuous piece logits)      │
│  4. Primary Statistic: T_obs              │                     │  4. Balanced Accuracy (threshold 0.5)     │
│  5. Exact Permutation Test: C(9,4) = 126  │                     │  5. Brier Score: (1/N) * sum((p_i - y)^2) │
│  6. Exact p-value (one-sided, α = 0.05)   │                     │  6. Within-Composer Bootstrap (B=10,000)  │
└───────────────────────────────────────────┘                     └───────────────────────────────────────────┘
```

### 3.1 Feature Ordering & Standardization
Let $X \in \mathbb{R}^{483 \times 56}$ denote the feature matrix extracted from the 483 pieces in the role-blind feature cache. The column projection and feature sequence match `predictor.feature_names` identically.

For each piece $i \in \{1, \dots, 483\}$ and descriptor $j \in \{1, \dots, 56\}$:
$$x_{\text{scaled}, i, j} = \frac{x_{i, j} - \mu_j}{\sigma_j}$$
where $\mu_j$ is `scaler.mean[j]` and $\sigma_j$ is `scaler.scale[j]` from the frozen predictor bundle.

### 3.2 Piece-Level Decision Score (Logit)
The continuous linear decision score (logit) $z_i$ is computed via:
$$z_i = \beta_0 + \sum_{j=1}^{56} \beta_j \, x_{\text{scaled}, i, j}$$
where $\beta_0$ is `intercept` and $\beta_j$ is `coefficients[j]`.

### 3.3 Composer-Level Aggregation ($S_c$)
To eliminate piece-count pseudoreplication and guarantee that high-piece composers (such as Scriabin or Beethoven) do not dominate the statistical test, piece scores are aggregated with equal weighting per composer:
$$S_c = \frac{1}{M_c} \sum_{i \in \mathcal{P}_c} z_i \quad \text{for } c \in \{1, \dots, 9\}$$
where $\mathcal{P}_c$ is the set of pieces by composer $c$, and $M_c = |\mathcal{P}_c|$.

### 3.4 Primary Test Statistic ($T_{\text{obs}}$)
The primary confirmatory test statistic $T_{\text{obs}}$ is the difference between the mean Russian composer score and the mean Control composer score:
$$T_{\text{obs}} = \bar{S}_{\text{Russian}} - \bar{S}_{\text{Control}} = \frac{1}{4} \sum_{c \in \text{Russian}} S_c - \frac{1}{5} \sum_{c \in \text{Control}} S_c$$
The directional alternative hypothesis posits $T_{\text{obs}} > 0$.

### 3.5 Exact Permutation Test ($C(9,4) = 126$)
Because $N=9$ is computationally small, the null distribution is evaluated via exact full combinatorial enumeration across all $\binom{9}{4} = 126$ partitions of the 9 composer scores $\{S_c\}_{c=1}^9$ into 4 "Russian" and 5 "Control":
$$T_k = \frac{1}{4} \sum_{c \in A_k} S_c - \frac{1}{5} \sum_{c \notin A_k} S_c \quad \text{for } k = 1, \dots, 126$$
The exact one-sided $p$-value is defined without pseudo-count:
$$p_{\text{exact}} = \frac{1}{126} \sum_{k=1}^{126} \mathbb{I}(T_k \ge T_{\text{obs}})$$
Statistical significance is declared if $p_{\text{exact}} \le 0.05$.

### 3.6 Secondary Classification Metrics
1. **Predicted Probabilities**: $p_i = \sigma(z_i) = \frac{1}{1 + e^{-z_i}}$
2. **Binary Predictions**: $\hat{y}_i = \mathbb{I}(p_i \ge 0.5) = \mathbb{I}(z_i \ge 0)$
3. **AUROC**: Area Under the Receiver Operating Characteristic curve evaluated on continuous piece logits $z_i$ against true labels $y_i \in \{0, 1\}$.
4. **Balanced Accuracy**: $\frac{1}{2} (\text{TPR} + \text{TNR})$ at fixed threshold 0.5.
5. **Brier Score**: $\frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)^2$.

### 3.7 Within-Composer Stratified Bootstrap
To construct valid 95% confidence intervals while respecting composer cluster structure:
* **Stratification**: `WITHIN_COMPOSER`
* **Replicates**: $B = 10{,}000$
* **Random Seed**: `42`
* **Resampling Procedure**: For each replicate $b \in \{1, \dots, 10000\}$ and each composer $c \in \{1, \dots, 9\}$, draw $M_c$ piece indices uniformly with replacement from $\{1, \dots, M_c\}$. Concatenate to form a resampled cohort of $N=483$ pieces. Evaluate AUROC, Balanced Accuracy, and Brier score.
* **Confidence Interval**: 95% Percentile Interval $[Q_{0.025}, Q_{0.975}]$ from the empirical bootstrap distribution.

### 3.8 Exclusion of 56-Feature Significance Battery
The 56 individual feature hypotheses are explicitly excluded from the one-shot primary/secondary unblinding run to prevent alpha inflation and false discovery. Individual feature diagnostic summaries are reserved for separate exploratory research following confirmatory unblinding.

---

## 4. Pre-Execution Safety & Verification Gates

1. **Deterministic Preflight Verification**: `scripts/verify_rc012_one_shot_preflight.py` executes all cryptographic hash assertions, repertoire sanity checks, and leakage gates.
2. **Regression Test Suite**: `tests/regression/test_rc012_one_shot_lock.py` exercises all statistical formulas on synthetic dummy matrices with 0 real confirmatory score exposure.
3. **Fail-Closed Execution Gate**: Predictor execution on confirmatory data requires exact match on all 5 binding hashes.
