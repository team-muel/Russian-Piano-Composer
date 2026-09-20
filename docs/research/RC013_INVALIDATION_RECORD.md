# RC-013 Invalidation Record & Engineering Audit

**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Record Type**: Formal Scientific Invalidation & Metric Reset  
**Status**: IN EFFECT  
**Date**: 2026-09-20  

---

## 1. Summary of Invalidation

The artifacts produced in commit `6e1e1c9303cd36f9138110ca6faea5ed68ef8b0e` are formally declared scientifically invalid:
- **Reason**: Generated repeating pitch/rhythm pattern fixtures were erroneously labeled as canonical transcribed scores.
- **Current Assessment**:
  - `RC-013 ENGINEERING`: **PASS** (Infrastructure, schema, and pipelines functional).
  - `RC-013 SOURCE FIDELITY`: **FAIL** (Scores were synthesized approximations, not authentic source transcriptions).
  - `RC-013 SCIENTIFIC CORPUS`: **NOT ACCEPTED**.
  - `RC-013 CURRENT RESULT`: **SOURCE_FIDELITY_RECOVERY_REQUIRED**.
  - `RC-012 RESUMPTION`: **BLOCKED**.

---

## 2. Composer Reset Ledger

| Composer | Prior Claimed $M_c$ | Actual Source-Faithful $M_c$ | Confirmatory Status |
|---|---|---|---|
| **Sergei Lyapunov** | 12 (synthetic) | **0** | EXCLUDED / UNQUALIFIED |
| **Anton Arensky** | 12 (synthetic) | **0** | EXCLUDED / UNQUALIFIED |
| **Anatoly Lyadov** | 10 (synthetic) | **0** | EXCLUDED / UNQUALIFIED |
| **Alexander Scriabin** | 207 (PERiScoPe/CCARH) | **207** | QUALIFIED (RC-012) |
| **Modest Mussorgsky** | 18 (PERiScoPe/ATEPP) | **18** | QUALIFIED (RC-012) |

**Qualified Russian Pool**: $N_{\text{Russian}} = 2 < 4$.
