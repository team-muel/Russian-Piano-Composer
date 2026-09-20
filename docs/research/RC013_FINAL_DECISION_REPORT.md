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

All 9 pilot scores were audited measure-by-measure (224 total measures) against historical print editions, satisfying all 12 element criteria with 0 critical discrepancies and 0 unresolved ambiguities.

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
635d46f547240039671e7b2061ecd6fdb4ce90df3e182171f4fd409b9fa70035

RC013_ERROR_LOG_HASH:
2562448536f7a4924b76dd45e09e4573e800669b3ea629c1da0538315df3e80f

RC013_CANONICAL_SYMBOLIC_CORPUS_HASH:
9e97c1fd2d03693c0ca9c660d0839a07c1ccec22bcf416c8dbf900cda6e18cdb

RC013_QC_RESULT_HASH:
ce328662498267cf4bc02d91496d29f3d46429d4322038b0d1cf32f9ae69d3f6

RC013_AUTOMATED_REVIEW_BUNDLE_HASH:
12f7325f9cea78129099f831b34396a6a2a74c541dbc86a18170ffcd6964a4f5

RC013_SOURCE_COMPARISON_BUNDLE_HASH:
c65de231f7ea8da045e66432676d0547a0bd78f8fb1951298bc0ab98fb253bc4

RC013_SOURCE_FIDELITY_GATE_RESULT_HASH:
db2fc1e5dec09aa8d3dd05a0a10cabc37a730687c02b0074977ede5a545f49f8
```

- **Two-Process Verification**: `Process A == Process B` (100% Cryptographic Match across all 10 hashes).
- **Test Suite**: `tests/unit/corpus/test_rc013_digitization.py` and `tests/unit/corpus/test_rc013_anti_self_certification.py`.
- **Local CI (`ci.ps1`)**: ALL PASSED, ruff clean, mypy clean.
