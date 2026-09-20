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
- **Score 1 (Anton Arensky Op. 36 No. 1)**: `IDENTITY_REVALIDATION_REQUIRED` (Reopened for authoritative work identity and scan pagination binding; 36 measures in C major).
- **Score 2 (Anton Arensky Op. 36 No. 2)**: `IDENTITY_REVALIDATION_REQUIRED` (Reopened for authoritative work identity and scan pagination binding; 102 measures in C minor / *La Toupie*, bound to `Arensky_morceaux_op36-1.pdf` pp. 5–12).
- **Score 3 (Anton Arensky Op. 36 No. 13)**: `PENDING_SOURCE_COMPARISON` (Work identity resolved to *Étude in F-sharp major*, bound to `Arensky_Morceaux_op.36_No.13-18.pdf` pp. 1–5).
- **Scores 4–9 (Lyapunov Op. 11 & Lyadov Op. 40/46)**: `PENDING_SOURCE_COMPARISON` (Candidate transcriptions pending source comparison).
- **Overall Pilot Progress**: 0 / 9 scores verified (Scores 1 & 2 reopened pending identity revalidation, Scores 3–9 pending review); overall pilot source fidelity remains `PENDING_SOURCE_COMPARISON`.

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
45ecf2bf20ac332977420267b45d2e778468ce7322f24318109b1a22b23bedf7

RC013_SOURCE_IMAGE_BUNDLE_HASH:
6170cb5a5ebcc3468385edb4d52d154cd101dd68edd57690f17075f299ea1445

RC013_DIGITIZATION_POLICY_HASH:
8bd6651352a159fc8c6f6b9207263e4beac1945b3b8de542bec86633df3af147

RC013_DIGITIZATION_MANIFEST_HASH:
5b82f443b410363b2d83b32b5fb37fb2d14dcfb9a7d0686d8987e2acaf36c070

RC013_ERROR_LOG_HASH:
9b9dac42b8f2a6348bafb7e1e3d79d0f962f420584057350c7f34578ce7645a1

RC013_CANONICAL_SYMBOLIC_CORPUS_HASH:
d0a4c717c01d38e89bf14b4195bc4f3fda749f8ca16b02b3824f9cde3bcddc72

RC013_QC_RESULT_HASH:
e18dc02c655606415045ffd7ca54ef9a67b4a06c3ebcdf4b1618168442983513

RC013_AUTOMATED_REVIEW_BUNDLE_HASH:
2d203323178ceb590fa4b2c596e9f9a1131849bf7dd8b2b7dafcbedb9b77a7d3

RC013_SOURCE_COMPARISON_BUNDLE_HASH:
34087b72c4eb7cd27b43b67d0573dac15cdffbee56711e6b381a19ed71385699

RC013_SOURCE_FIDELITY_GATE_RESULT_HASH:
c04e3e4cc430fbe04446b82af6d6f7f01e1eb37946d213e5e1a0faaccad6bcc4
```

- **Two-Process Verification**: `Process A == Process B` (100% Cryptographic Match across all 10 hashes).
- **Test Suite**: `tests/unit/corpus/test_rc013_digitization.py` and `tests/unit/corpus/test_rc013_anti_self_certification.py`.
- **Local CI (`ci.ps1`)**: ALL PASSED, ruff clean, mypy clean.
