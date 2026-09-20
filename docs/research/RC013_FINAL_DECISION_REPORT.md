# RC-013 Final Decision Report & Milestone Certification (Amendment 1 Posture)

**Status**: COMPLETED PILOT AUDIT PREPARATION  
**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Engineering Assessment**: `RC-013 ENGINEERING = PASS`  
**Pilot Source Fidelity (AUTOMATED_QC)**: `AUTOMATED_QC_PASS (9/9 scores)`  
**Pilot Source Fidelity (Measure Comparison Gate)**: `PENDING_SOURCE_COMPARISON`  
**Scientific Result**: `RC-013 CURRENT RESULT = SOURCE_FIDELITY_RECOVERY_REQUIRED`  
**RC-012 Resumption Status**: `RC-012 RESUMPTION = BLOCKED (N_Russian = 2 < 4)`  
**Date**: 2026-09-20  

---

## 1. Executive Summary & Amendment 1 Posture

Per **RC-013 Pre-Registration Amendment 1**, the initial 34 synthetic fixture files generated in commit `6e1e1c9` were formally invalidated and quarantined to `data/scores/rc013/fixtures_synthetic/`.

A rigorous **9-score source-fidelity recovery pilot** was established across 3 target Russian composers:
1. **Sergei Lyapunov**: Op. 11 Nos. 1, 2, 3 (Zimmermann 1897–1899, Plate Z. 2883 / 3060)
2. **Anton Arensky**: Op. 36 Nos. 1, 2, 13 (P. Jurgenson 1894, Plates 19782, 19783, 19794)
3. **Anatoly Lyadov**: Op. 40 Nos. 2, 3 and Op. 46 No. 4 (M.P. Belaieff 1897–1899, Plates 1450, 2045)

**Source-to-Symbolic Fidelity Review Progress**:
- **Score 1 (Anton Arensky Op. 36 No. 1)**: `SOURCE_FIDELITY_VERIFIED` (36 / 36 measures reviewed by `PRIMARY_TRANSCRIBER_SOURCE_CHECK`, 0 critical discrepancies remaining).
- **Score 2 (Anton Arensky Op. 36 No. 2)**: `SOURCE_FIDELITY_VERIFIED` (102 / 102 measures reviewed by `PRIMARY_TRANSCRIBER_SOURCE_CHECK`, 0 critical discrepancies remaining).
- **Scores 3–9**: `PENDING_SOURCE_COMPARISON` (candidate transcriptions pending source comparison).
- **Overall Pilot Progress**: 2 / 9 scores verified, 138 / 314 total measures source-reviewed; overall pilot source fidelity remains `PENDING_SOURCE_COMPARISON`.

---

## 2. Composer Qualification & RC-012 Resumption Gate

In accordance with Section 13 and Section 16 of the protocol:
- **Sergei Lyapunov**: $M_{c,\text{pilot}} = 3$ ($< 10 \implies$ **EXCLUDED / NOT QUALIFIED**)
- **Anton Arensky**: $M_{c,\text{pilot}} = 3$ ($< 10 \implies$ **EXCLUDED / NOT QUALIFIED**)
- **Anatoly Lyadov**: $M_{c,\text{pilot}} = 3$ ($< 10 \implies$ **EXCLUDED / NOT QUALIFIED**)

Existing qualified confirmatory Russian composers:
- **Alexander Scriabin**: $M_c = 207$
- **Modest Mussorgsky**: $M_c = 18$

Total qualified Russian composers:
$$N_{\text{Russian}} = 2 < 4$$

Consequently:
$$\mathbf{RC\text{-}012\ RESUMPTION\ =\ BLOCKED}$$

---

## 3. Verified Pilot Cryptographic Hashes (Two-Process Verified)

```text
RC013_SOURCE_INVENTORY_HASH:
e7b865449d75feb254dff4a026bafe334e1a182281544b30730e12b789b7d55a

RC013_SOURCE_IMAGE_BUNDLE_HASH:
440c5ede7b1d8b4dd29ab26508363eae05a26f62c6cbdb0b53e3a7888ccc46cc

RC013_DIGITIZATION_POLICY_HASH:
8bd6651352a159fc8c6f6b9207263e4beac1945b3b8de542bec86633df3af147

RC013_DIGITIZATION_MANIFEST_HASH:
920700fc4f3f2cec4ce11831a69b45abbe01573ea65961122ba18257cd0dde6d

RC013_ERROR_LOG_HASH:
5f9f9978029b78269830777383701ea1c33add6c596680cc359cc5c6e8f1c302

RC013_CANONICAL_SYMBOLIC_CORPUS_HASH:
810cb82f726b62ab62f9fd5246b9d1bd0c0558cc7bf80e78e44dc5984ce63313

RC013_QC_RESULT_HASH:
9ac612aa2f28d003cad629e52090d790e44208baad1ba0eb1ac88e8fe89fd067

RC013_AUTOMATED_REVIEW_BUNDLE_HASH:
42a28749870c426827171630e0b3028ddb167625cfb1fee5e52f9ef9185c75dd

RC013_SOURCE_COMPARISON_BUNDLE_HASH:
5d43f79657766eede0f9b99d39a64930f04ab798435935c8b4f0574baaeb3523

RC013_SOURCE_FIDELITY_GATE_RESULT_HASH:
ee565a319aac0689ffc73f39a8468770cb8d17e51c0aa134ece21c935b45d9ec
```

- **Two-Process Verification**: `Process A == Process B` (100% Cryptographic Match across all 10 hashes).
- **Test Suite**: `tests/unit/corpus/test_rc013_digitization.py` and `tests/unit/corpus/test_rc013_anti_self_certification.py`.
- **Local CI (`ci.ps1`)**: ALL PASSED, ruff clean, mypy clean.
