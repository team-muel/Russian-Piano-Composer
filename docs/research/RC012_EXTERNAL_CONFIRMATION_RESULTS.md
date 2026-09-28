# RC-012 External Confirmation Results & Scientific Findings

> [!NOTE]
> **HISTORICAL_PRE_RC014_STATE**: This document records the historical outcome of the initial pre-RC014 baseline execution attempt where $N_{\text{Russian}} = 2 < 4$ triggered `CONFIRMATORY_DATA_CONTRACT_FAILED` (DATA AVAILABILITY FAILURE; hypothesis NOT TESTED).
> This historical state has been formally superseded by the RC-014 confirmatory corpus acquisition and Route B Human Access Governance Decision (`data/reviews/rc014/rc014_human_access_governance_decision.json`), which established $N_{\text{Russian}} = 4$ ($N_{\text{Total}} = 9$, $M=483$) under active execution lock (`data/reviews/rc012/rc012_one_shot_execution_lock.json`).

**Status**: HISTORICAL BASELINE RECORD (SUPERSEDED BY RC-014)  
**Milestone**: RC-012 Independent External Composer Confirmation  
**Historical Scientific Outcome**: `CONFIRMATORY_DATA_CONTRACT_FAILED`

---

## 1. Scientific Governance & Evaluation Summary

RC-012 posed the central confirmatory hypothesis:
> Does the completely frozen RC-011 56-feature structural representation contain a Russian-vs-Control structural signal that generalizes to never-before-seen composers who played zero role in representation development?

To prevent false discovery, data leakage, and pseudoreplication, the pre-registered protocol mandated:
1. **Confirmatory Data Contract Pre-Condition Gate**:
   - Minimum sample size: $\ge 4$ independent Russian composers and $\ge 4$ independent Control composers ($N \ge 8$).
   - Minimum piece count per composer: $\ge 10$ eligible symbolic scores.
   - Fail-closed gate rule: If fewer than 4 composers per class satisfy the data contract, declare `CONFIRMATORY_DATA_CONTRACT_FAILED` ex ante and stop prior to hypothesis testing.
2. **Empirical Inventory & Feasibility Findings**:
   - **Control Candidates**: 5 distinct composers satisfied all criteria ($N_{\text{Control}} = 5 \ge 4$):
     - Edvard Grieg ($M_c=66$, `DCMLab/grieg_lyric_pieces`)
     - Claude Debussy ($M_c=54$, DCMLab 7 repos: `suite_bergamasque`, `preludes`, `etudes`, `pour_le_piano`, `estampes`, `deux_arabesques`, `childrens_corner`)
     - Antonín Dvořák ($M_c=12$, `DCMLab/dvorak_silhouettes`)
     - Béla Bartók ($M_c=14$, `DCMLab/bartok_bagatelles`)
     - Ludwig van Beethoven ($M_c=91$, `DCMLab/beethoven_piano_sonatas`)
   - **Russian Candidates**: 2 distinct composers satisfied all criteria ($N_{\text{Russian}} = 2 < 4$):
     - Alexander Scriabin ($M_c=207$, CCARH `craigsapp/scriabin` / ASAP / PERiScoPe)
     - Modest Mussorgsky ($M_c=18$, PERiScoPe / ATEPP / KernScores: 15 movements of *Pictures at an Exhibition* + 3 standalone pieces: *Impromptu passionné*, *Memories of Childhood*, *The Seamstress*)
     - All other Russian late-Romantic / early-modern candidates (*Prokofiev* $M_c=4$, *Balakirev* $M_c=2$, *Lyapunov* $M_c=1$, *Rubinstein* $M_c=1$, *Arensky* $M_c=0$, *Glazunov* $M_c=0$, *Lyadov* $M_c=0$, *Taneyev* $M_c=0$, *Cui* $M_c=0$) lack curated, machine-readable open symbolic score collections with $\ge 10$ pieces in public repositories.
3. **Formal Precondition Gate Decision**:
   $$\mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$
   Per Section 3 of the pre-registration, the confirmatory evaluation halted ex ante due to **DATA AVAILABILITY FAILURE** ($N_{\text{Russian}} = 2 < 4$).
   The primary external hypothesis is **NOT TESTED**.
   This is NOT a negative scientific finding about music or the absence of a Russian structural signal; it is strictly a data availability failure under open symbolic corpus constraints.

---

## 2. Frozen Development Predictor Benchmark

For archival completeness, the primary development predictor was fitted on the 141 canonical development pieces across the 6 development composers (*Medtner*, *Rachmaninoff*, *Tchaikovsky*, *Chopin*, *Liszt*, *Schumann*):
- **Development Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`
- **Development Matrix Hash**: `7e141a62bed72d10a894d7fa3123619aacce85797b1953423fd8de2b5b069bc0`
- **Predictor Bundle Hash**: `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`
- **Model Family**: Logistic Regression ($C=1.0$, $L_2$ penalty, `solver="lbfgs"`, `random_state=42`)
- **Weighted Training Accuracy**: 73.24%
- **Unweighted Training Accuracy**: 79.43%

---

## 3. Data Leakage & Lineage Audit

- **Composer Intersection**: Development $\cap$ Confirmatory Candidates $= \emptyset$ (Disjoint).
- **Predictor Training Isolation**: Predictor weights trained strictly on the 6 development composers. Zero confirmatory candidate scores or labels were exposed.
- **Audit Script**: `scripts/audit_rc012_leakage.py` PASS.
- **Reproducibility Script**: `scripts/verify_rc012_confirmatory_reproducibility.py` PASS.

---

## 4. Scientific Significance for Russian Piano Composer Project

1. **Strict Data Contract Preserved**:
   A data availability contract failure prevents false discovery. By refusing to compromise sample size thresholds ($N \ge 4$), the study prevents false positive or pseudoreplicated claims based on an underpowered sample of $N_{\text{Russian}}=2$ composers.
   The primary confirmatory hypothesis remains strictly **NOT TESTED**.
2. **Corpus Ecosystem Discovery**:
   Highlights a critical structural limitation in computational musicology: open, machine-readable symbolic piano corpora are heavily Euro-centric / German-French dominated, while late-Romantic Russian masters beyond Tchaikovsky, Rachmaninoff, Medtner, Scriabin, and Mussorgsky remain severely under-digitized.
3. **Relation to Prior Milestones**:
   RC-010 established `RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED` on the exploratory set. RC-011 established `STRUCTURAL_REPRESENTATION_VALIDATED` for mathematical and structural representation integrity across the canonical 141-piece development corpus. RC-011 is not validated for Russian stylistic guidance or classification, as confirmatory testing was halted due to data availability failure.

---

# POST-RC014 AUTHORIZED ONE-SHOT CONFIRMATORY EXECUTION

**Status**: `COMPLETED_AUTHORITATIVE`  
**Execution Timestamp**: `2026-09-28T15:10:56Z`  
**Runner Commit**: `e2af2110d754a90c57b625821ad2952fd5970721`  
**Governance Route**: `Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE` (`APPROVED`)  
**Primary Inferential Outcome**: `PRIMARY_TEST_DOES_NOT_REJECT_NULL`  

---

## 5. Confirmatory Repertoire & Aggregated Scores

The complete confirmatory repertoire comprises 9 composers and 483 pieces ($M_c \ge 10$ for all composers):

### 5.1 Russian Class ($N_{\text{Russian}} = 4$, $M_{\text{Russian}} = 246$)
| Russian Composer | Eligible Pieces ($M_c$) | Mean Decision Score ($S_c$) |
|---|---|---|
| **Alexander Scriabin** | 207 | $+0.655906$ |
| **Modest Mussorgsky** | 18 | $-0.096404$ |
| **Anton Rubinstein** | 11 | $-2.209582$ |
| **Sergei Prokofiev** | 10 | $-1.340187$ |
| **Russian Class Mean ($\bar{S}_{\text{Russian}}$)** | **246** | **$-0.747567$** |

### 5.2 Control Class ($N_{\text{Control}} = 5$, $M_{\text{Control}} = 237$)
| Control Composer | Eligible Pieces ($M_c$) | Mean Decision Score ($S_c$) |
|---|---|---|
| **Edvard Grieg** | 66 | $-0.196844$ |
| **Claude Debussy** | 54 | $+0.051932$ |
| **Ludwig van Beethoven** | 91 | $-0.007708$ |
| **Béla Bartók** | 14 | $+0.182508$ |
| **Antonín Dvořák** | 12 | $-0.096054$ |
| **Control Class Mean ($\bar{S}_{\text{Control}}$)** | **237** | **$-0.013233$** |

---

## 6. Primary Hypothesis Testing Results

* **Observed Test Statistic**:
  $$T_{\text{obs}} = \bar{S}_{\text{Russian}} - \bar{S}_{\text{Control}} = -0.747567 - (-0.013233) = \mathbf{-0.734333}$$
* **Preregistered Alternative Hypothesis**: $T_{\text{obs}} > 0$ (One-sided $\alpha = 0.05$).
* **Exact Permutation Test ($C(9,4) = 126$ combinatorial assignments)**:
  - Total Permutations: $126$
  - Extreme Count ($\mathbb{I}(T_k \ge T_{\text{obs}})$): $110 / 126$
  - Strictly Greater Count ($\mathbb{I}(T_k > T_{\text{obs}})$): $109 / 126$
  - Tie Count ($\mathbb{I}(T_k = T_{\text{obs}})$): $1$
  - Observed Assignment Rank: $110$ of $126$
  - **Exact $p$-value**:
    $$p_{\text{exact}} = \frac{110}{126} = \mathbf{0.873016}$$
* **Primary Inferential Decision**:
  $$\mathbf{PRIMARY\_TEST\_DOES\_NOT\_REJECT\_NULL}$$

The primary confirmatory hypothesis that Russian piano compositions exhibit systematically higher scores on the frozen structural linear predictor than control compositions is **NOT supported**. The observed difference is in fact negative ($T_{\text{obs}} = -0.734333$), placing the observed assignment in the bottom quartile ($110 / 126$) of the permutation null distribution.

---

## 7. Secondary Classification & Bootstrap Confidence Intervals

Whole-sample piece-level classification performance across all 483 pieces:

| Metric | Point Estimate | 95% Percentile Bootstrap CI ($B=10{,}000$) |
|---|---|---|
| **AUROC** (continuous $z_i$) | `0.5113` | `[0.4620, 0.5605]` |
| **Balanced Accuracy** (threshold 0.5) | `0.5161` | `[0.4728, 0.5576]` |
| **Brier Score** ($p_i = \sigma(z_i)$) | `0.2660` | `[0.2551, 0.2768]` |

* **Bootstrap Configuration**: Within-composer stratified resampling, $B = 10{,}000$ replicates, `RandomState(42)`, linear percentile method.
* **Secondary Metric Finding**: The receiver operating characteristic and balanced accuracy confidence intervals tightly span the $0.50$ chance level.

---

## 8. Immutable Execution & Reproducibility Ledger

| Ledger Entry | SHA-256 Hash Binding |
|---|---|
| **Authoritative Result Artifact** (`rc012_one_shot_confirmatory_result.json`) | `a933ac2b21fe50cff9c0a43e8216ee37593acded32e22ecb0e9502b231cffded` |
| **Piece-Score Ledger (483 Pieces)** (`piece_ledger_sha256`) | `66513dc4901b48ee865ba826cb4dad824f448b242b94834fd25202d39c5aa634` |
| **10,000 Replicate Matrix** (`bootstrap_replicate_matrix_sha256`) | `d606705dd1621a4b0fef85c1dbec2f2f1347891c8576a2162e64ac9306b5b739` |
| **Two-Process Independent Reproducibility Audit** | **`PASS`** (`rc012_one_shot_reproducibility_audit.json`) |
| **Anti-Rerun Execution Guard** | **`ENFORCED`** (`RC012_ALREADY_EXECUTED`) |


