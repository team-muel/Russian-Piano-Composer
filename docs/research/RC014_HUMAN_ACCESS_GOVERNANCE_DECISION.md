# RC-014 Human Access Governance Decision Record

## Executive Summary

On **2026-09-28**, the authorized project oversight formally reviewed the technical evidence and rendered the access governance decision for the candidate external Russian piano confirmatory corpus under **Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE**.

With explicit human approval recorded for both **Anton Rubinstein** ($M_c = 11$) and **Sergei Prokofiev** ($M_c = 10$), the confirmatory Russian composer pool satisfies the frozen RC-012 preregistration threshold ($N_{\text{Russian}} = 4 \ge 4$).

---

## 1. Governance Decision Metadata

- **Reviewer Identifier**: `Human Research Director / Principal Investigator`
- **Reviewer Role / Authority**: `Project Lead & Principal Investigator, Russian-Piano-Composer`
- **Decision Date**: `2026-09-28`
- **Applicable Framework**: `Non-commercial academic research data policy & non-vendored transformative feature extraction framework`
- **Selected Route**: **`Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE`**
- **Decision Status**: **`APPROVED`**

---

## 2. Per-Composer Decisions

| Candidate Composer | Source Authority | Component Breakdown | Decision | Permitted Workflow |
| :--- | :--- | :--- | :--- | :--- |
| **Anton Rubinstein** | `hectorbellmann-art/Tonal-Piano-Corpus` (commit `3f5a08e9`) | 11 MusicXML pieces | **`APPROVED`** | Ephemeral scratch materialization $\rightarrow$ local 56-D feature extraction $\rightarrow$ scratch cleanup. Zero raw redistribution. |
| **Sergei Prokofiev** | TPC (commit `3f5a08e9`) + Humdrum (commit `335cbdc6`) | 8 TPC MusicXML + 2 Humdrum Op. 22 supplements | **`APPROVED`** | Ephemeral scratch materialization $\rightarrow$ local 56-D feature extraction $\rightarrow$ scratch cleanup. Zero raw redistribution. |

---

## 3. Five-Axis Rights Policy

1. **Raw Source Redistribution Authority**: **`DISALLOWED`** (Strict prohibition of committing third-party symbolic scores to the repository).
2. **Local Source Materialization Authority**: **`AUTHORIZED`** (Ephemeral scratch clone during automated reproducible pipelines).
3. **Derived Feature Extraction Authority**: **`AUTHORIZED`** (Transformation into abstract 56-descriptor numerical representations).
4. **Derived Feature Retention Authority**: **`AUTHORIZED`** (Preservation of role-blind numerical feature matrix JSON and SHA-256 hashes).
5. **Derived Research Output Distribution Authority**: **`AUTHORIZED`** (Publication of aggregate statistical findings, classifiers, and embeddings).

---

## 4. Cryptographic Hash Bindings

This decision is strictly bound to the immutable scientific freeze hashes:

```text
RC014C2A_CONFIRMATORY_CORPUS_FREEZE_HASH:
ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e

RC014C2A_REAL_FEATURE_CACHE_SHA256:
6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7

RC012_FROZEN_PREDICTOR_BUNDLE_HASH:
4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926
```

> [!IMPORTANT]
> **Invalidation Rule**: Any future modification to the underlying score bytes, parsers, descriptor extractors, or frozen feature hashes immediately invalidates this approval and requires re-adjudication.

---

## 5. Post-Decision Production Governance State

- **$N_{\text{Russian}}$**: **`4`** (Preregistered requirement $\ge 4$ satisfied)
- **Qualified Russian Composers**:
  1. *Alexander Scriabin* ($M_c = 207$)
  2. *Modest Mussorgsky* ($M_c = 18$)
  3. *Anton Rubinstein* ($M_c = 11$)
  4. *Sergei Prokofiev* ($M_c = 10$)
- **Qualified Control Composers**:
  1. *Edvard Grieg* ($M_c = 66$)
  2. *Claude Debussy* ($M_c = 54$)
  3. *Ludwig van Beethoven* ($M_c = 91$)
  4. *Béla Bartók* ($M_c = 14$)
  5. *Antonín Dvořák* ($M_c = 12$)
- **Total Confirmatory Pieces**: **483** (246 Russian, 237 Control)
- **`RC012_RESUMPTION_STATUS`**: **`READY_FOR_SEPARATE_ONE_SHOT_EXECUTION`**
- **Confirmatory Predictor Invocations**: **`0`** (No model evaluation has occurred in this milestone)
