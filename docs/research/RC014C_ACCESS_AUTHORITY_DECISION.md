# RC-014C Access Authority & Legal Governance Decision Record

## 1. Purpose & Governance Mandate

This document establishes the formal legal and governance framework for the candidate Russian piano confirmatory corpus acquired under RC-014.

**Core Principle**: Technical capability and mathematical reproducibility do not constitute legal authorization. An autonomous AI coding agent must not fabricate legal permission or make assumptions about institutional licensing rights. This document structures the evidence and provides a decision record requiring explicit human authorization prior to confirmatory unblinding.

---

## 2. Granular Five-Axis Rights Taxonomy

To prevent collapsing distinct legal questions into a single boolean, the project defines five independent governance axes:

```text
                                  ┌─────────────────────────────────────────────────────────────┐
                                  │           RC-014C Five-Axis Governance Taxonomy             │
                                  └─────────────────────────────────────────────────────────────┘
                                                                 │
         ┌──────────────────────┬──────────────────────┬─────────┴────────────┬──────────────────────┐
         ▼                      ▼                      ▼                      ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ 1. Raw Source    │   │ 2. Local Source  │   │ 3. Derived Feat. │   │ 4. Derived Feat. │   │ 5. Derived Feat. │
│ Redistribution   │   │ Materialization  │   │ Extraction       │   │ Retention        │   │ Distribution     │
│ Authority        │   │ Authority        │   │ Authority        │   │ Authority        │   │ Authority        │
└──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘   └──────────────────┘
```

| Governance Axis | Definition | Current Technical State | Current Governance Status |
|---|---|---|---|
| **1. Raw Source Redistribution Authority** | Permission to commit, vendor, or redistribute third-party symbolic score files (MusicXML, Kern, TIFF) in the repository. | `NOT_COMMITTED` (0 raw third-party score files in repository). | **`DISALLOWED`** (`raw_file_redistribution_permitted: false`). |
| **2. Local Source Materialization Authority** | Permission to download and ephemeral-clone public repositories to local scratch for automated analysis. | `VERIFIED` (Deterministic shallow clone and Git blob verification). | **`SUBJECT_TO_APPLICABLE_JURISDICTION_AND_INSTITUTIONAL_POLICY`**. |
| **3. Derived Feature Extraction Authority** | Permission to parse notation and extract abstract musical descriptors (e.g. pitch/interval histograms). | `VERIFIED` (56 role-blind structural descriptors extracted in memory). | **`SUBJECT_TO_APPLICABLE_JURISDICTION_AND_INSTITUTIONAL_POLICY`**. |
| **4. Derived Feature Retention Authority** | Permission to persist extracted numerical feature vectors and bundle hashes in the project repository. | `VERIFIED` (JSON feature cache manifest hashed and isolated from scores). | **`HUMAN_DECISION_RECORDED`**. |
| **5. Derived Feature Distribution Authority** | Permission to publish aggregate statistical models, embeddings, and research outputs derived from features. | `N/A` (No models or statistics trained/published on confirmatory corpus). | **`HUMAN_DECISION_RECORDED`**. |

---

## 3. Evidence Audit by Source Class

### 3.1 Underlying Musical Compositions
* **Anton Rubinstein (1829–1894)**:
  - `UNDERLYING_COMPOSITION_RIGHTS = JURISDICTION_DEPENDENT`
  - All 11 candidate works (Op. 75 published 1866; Op. 24 published 1854–1856) have expired author terms (Life + 70/80 years, US 95-year term).
* **Sergei Prokofiev (1891–1953)**:
  - `UNDERLYING_COMPOSITION_RIGHTS = JURISDICTION_DEPENDENT`
  - The 10 candidate works (Op. 2 No. 4 [1909], Op. 3 No. 3 [1907], Op. 11 [1912], Op. 12 Nos. 2 & 7 [1913], Op. 22 Nos. 1, 2, 3, 5, 10 [1915–1917, pub. 1918]) were published prior to 1929; terms are subject to local national copyright statutes.

### 3.2 Digital Encodings & Upstream Status
* **Tonal-Piano-Corpus (`hectorbellmann-art/Tonal-Piano-Corpus`)**:
  - Root Repository License: `UNDECLARED` (No root license file).
  - Raw Redistribution: **`DISALLOWED`**.
  - Upstream Dispatch: [`docs/research/RC014B_UPSTREAM_PERMISSION_REQUEST.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC014B_UPSTREAM_PERMISSION_REQUEST.md) status is **`PENDING_DISPATCH`**.
* **Humdrum KernScores Mirror (`automata/ana-music`)**:
  - Root Repository License: `UNDECLARED`.
  - Raw Redistribution: **`DISALLOWED`**.
  - License Status: **`SUPPLEMENT_LICENSE_PENDING`**.

---

## 4. Human Decision Routing

Prior to unblinding RC-012 confirmatory statistics, authorized human oversight was presented with three formal routes:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Formal Governance Routes                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route A: Explicit Upstream Permission Obtained (EXPLICIT_UPSTREAM_PERMISSION)                   │
│   - Formal written license waiver or explicit open-source license adopted by upstream authors. │
│   - Evidence recorded in repository.                                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route B: Authorized Non-Vendored Research Use (AUTHORIZED_NON_VENDORED_RESEARCH_USE)            │
│   - Determination by authorized reviewer that under applicable institutional policy and law,    │
│     the bounded workflow (public source → ephemeral materialization → 56-D feature extraction  │
│     → raw source deletion → 0 raw redistribution) is permitted for non-commercial research.     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route C: Authority Insufficient (AUTHORITY_INSUFFICIENT)                                        │
│   - Insufficient authority established. Candidate composers excluded from confirmation.         │
│   - Live confirmatory pool remains N_Russian = 2 (Scriabin + Mussorgsky).                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Governance State Transition

### 5.1 Pre-Decision State
* **Status**: `AWAITING_HUMAN_GOVERNANCE_DECISION`
* **Production Pool**: $N_{\text{Russian}} = 2$ (*Alexander Scriabin*, *Modest Mussorgsky*)
* **Resumption Gate**: `RC012 = BLOCKED`

### 5.2 Superseded By
* **Authoritative Record**: [`data/reviews/rc014/rc014_human_access_governance_decision.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/reviews/rc014/rc014_human_access_governance_decision.json)
* **Summary Report**: [`docs/research/RC014_HUMAN_ACCESS_GOVERNANCE_DECISION.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC014_HUMAN_ACCESS_GOVERNANCE_DECISION.md)

### 5.3 Final Human Decision
* **Selected Route**: `Route B = AUTHORIZED_NON_VENDORED_RESEARCH_USE`
* **Anton Rubinstein**: **`APPROVED`** (11 works from `hectorbellmann-art/Tonal-Piano-Corpus`)
* **Sergei Prokofiev**: **`APPROVED`** (10 works: 8 from `hectorbellmann-art/Tonal-Piano-Corpus` + 2 Humdrum Op. 22 supplements)

### 5.4 Post-Decision State
* **Production Pool**: $N_{\text{Russian}} = 4$ (*Alexander Scriabin*, *Modest Mussorgsky*, *Anton Rubinstein*, *Sergei Prokofiev*)
* **Resumption Gate**: **`RC012_RESUMPTION_STATUS = READY_FOR_SEPARATE_ONE_SHOT_EXECUTION`**

### 5.5 Decision Binding Hashes
* `RC014C2A_CONFIRMATORY_CORPUS_FREEZE_HASH`: `ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e`
* `RC014C2A_REAL_FEATURE_CACHE_SHA256`: `6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7`
* `RC012_FROZEN_PREDICTOR_BUNDLE_HASH`: `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926`
