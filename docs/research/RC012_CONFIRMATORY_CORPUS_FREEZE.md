# RC-012 Confirmatory Corpus Freeze Specification & Manifest Ledger

**Status**: FROZEN & RECORDED  
**Milestone**: RC-012 Independent External Composer Confirmation  
**Precondition Decision**: `CONFIRMATORY_DATA_CONTRACT_FAILED` (Documented in [`RC012_CONFIRMATORY_CORPUS_INVENTORY.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC012_CONFIRMATORY_CORPUS_INVENTORY.md))

---

## 1. Scope & Objective

This document records the exact frozen configuration and hashes for the RC-012 Confirmatory Corpus and Predictor Freeze (Commit B).

Because the external corpus landscape failed the preregistered minimum sample size standard of $\ge 4$ independent Russian composers with $\ge 10$ pieces each ($N_{\text{Russian}} = 1$ vs. required $\ge 4$), the confirmatory manifest records the audited eligible corpus state and locks the pipeline fail-closed to prevent uncontrolled execution on an underpowered, pseudoreplicated sample.

---

## 2. Frozen Development Predictor

The primary development predictor was fitted on the 141 canonical development pieces across the 6 development composers:
- **Parent Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`
- **Parent Structural Matrix Hash**: `7e141a62bed72d10a894d7fa3123619aacce85797b1953423fd8de2b5b069bc0`
- **Predictor Model**: Logistic Regression ($C = 1.0$, $L_2$ penalty, L-BFGS solver, `random_state = 42`)
- **Weighting**: Composer-balanced ($w_{c, i} = \frac{1}{6 \cdot N_c}$)
- **Weighted Training Accuracy**: 73.24%
- **Unweighted Training Accuracy**: 79.43%
- **Predictor Intercept**: `0.0033883722`
- **`RC012_FROZEN_PREDICTOR_BUNDLE_HASH`**:
  `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`

---

## 3. Confirmatory Candidate Inventory & Manifest State

The surveyed candidate corpus comprises:
- **Russian Candidate**: Alexander Scriabin (`craigsapp/scriabin` / CCARH, 207 works, commit `7daa1136a4edfaf8d2bfadee973c33f3b76b6760`)
- **Control Candidates**:
  - Edvard Grieg (`DCMLab/grieg_lyric_pieces`, 66 works, commit `91a304563521f3f273b8c0aadec1ce2ede2d1384`)
  - Claude Debussy (`DCMLab/debussy_suite_bergamasque` + `debussy_preludes`, 28 works)
  - Antonín Dvořák (`DCMLab/dvorak_silhouettes`, 12 works, commit `f228006fcd8696c809cfc8e701ed215cec3d07f1`)
  - Béla Bartók (`DCMLab/bartok_bagatelles`, 14 works, commit `c6221f6ecb4dbcd476e827f6bf8705bdcb15c8a9`)

Because $N_{\text{Russian}} = 1 < 4$, the confirmatory data contract halts ex ante, and no scores are unblinded or evaluated for hypothesis testing.
