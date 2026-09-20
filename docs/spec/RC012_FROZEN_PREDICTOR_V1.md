# RC-012 Frozen Predictor V1 Specification

**Version**: `RC012_FROZEN_PREDICTOR_V1`  
**Parent Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`  
**Parent Structural Matrix Hash**: `7e141a62bed72d10a894d7fa3123619aacce85797b1953423fd8de2b5b069bc0`  
**Bundle Artifact**: `models/rc012_predictor/frozen_predictor_bundle.json`  
**Bundle SHA-256 Hash**: `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`

---

## 1. Specification Overview

This specification freezes the mathematical predictor fitted on the development corpus to serve as the immutable evaluator for confirmatory testing.

### Training Set
- 141 canonical pieces from the 6 development composers:
  - Russian: *Medtner* ($N=19$), *Rachmaninoff* ($N=22$), *Tchaikovsky* ($N=12$)
  - Control: *Chopin* ($N=56$), *Liszt* ($N=19$), *Schumann* ($N=13$)
- Total pieces: 141 (53 Russian, 88 Control)

### Weighting & Standardization
- Composer-balanced sample weights:
  $$w_{c, i} = \frac{1}{6 \cdot N_c}$$
- Features standardized using weighted sample moments:
  $$\mu_j = \sum_i w_i X_{i, j}, \quad \sigma_j = \sqrt{\sum_i w_i (X_{i, j} - \mu_j)^2}$$
  $$z_{i, j} = \frac{X_{i, j} - \mu_j}{\sigma_j}$$

### Model Architecture & Hyperparameters
- Model family: `LogisticRegression`
- Loss / Regularization: $L_2$ penalty, $C = 1.0$
- Optimization solver: `lbfgs` (`random_state = 42`)
- Intercept: $0.0033883722$
- Weighted training accuracy: $73.24\%$
- Unweighted training accuracy: $79.43\%$

---

## 2. Invariance & Integrity Guarantee

The predictor operates on the 56 frozen RC-011 structural features. The model weights and scaling parameters are strictly immutable and cryptographically bound to `RC012_FROZEN_PREDICTOR_BUNDLE_HASH = 4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`.
