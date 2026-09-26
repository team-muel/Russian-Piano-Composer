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
| **2. Local Source Materialization Authority** | Permission to download and ephemeral-clone public repositories to local scratch for automated analysis. | `VERIFIED` (Deterministic shallow clone and Git blob verification). | **`RESEARCH_FAIR_USE_PENDING_APPROVAL`**. |
| **3. Derived Feature Extraction Authority** | Permission to parse notation and extract abstract musical descriptors (e.g. pitch/interval histograms). | `VERIFIED` (56 role-blind structural descriptors extracted in memory). | **`TRANSFORMATIVE_ANALYSIS_PENDING_APPROVAL`**. |
| **4. Derived Feature Retention Authority** | Permission to persist extracted numerical feature vectors and bundle hashes in the project repository. | `VERIFIED` (JSON feature cache manifest hashed and isolated from scores). | **`HUMAN_DECISION_REQUIRED`**. |
| **5. Derived Feature Distribution Authority** | Permission to publish aggregate statistical models, embeddings, and research outputs derived from features. | `N/A` (No models or statistics trained/published on confirmatory corpus). | **`HUMAN_DECISION_REQUIRED`**. |

---

## 3. Evidence Audit by Source Class

### 3.1 Underlying Musical Compositions
* **Anton Rubinstein (1829–1894)**: All 11 candidate works (Op. 75 published 1866; Op. 24 published 1854–1856) are in the **Public Domain worldwide** (Life + 70, Life + 80, and US 95-year terms expired).
* **Sergei Prokofiev (1891–1953)**: The 10 candidate works (Op. 2 No. 4 [1909], Op. 3 No. 3 [1907], Op. 11 [1912], Op. 12 Nos. 2 & 7 [1913], Op. 22 Nos. 1, 2, 3, 5, 10 [1915–1917, pub. 1918]) were published prior to 1929 and are in the **Public Domain worldwide** (US Pre-1929 rule + EU Life + 70 term expired Dec 31, 2023).

### 3.2 Digital Encodings & Upstream Status
* **Tonal-Piano-Corpus (`hectorbellmann-art/Tonal-Piano-Corpus`)**:
  - Root License: `UNDECLARED` (No `LICENSE` file in repository).
  - Upstream Dispatch: [`docs/research/RC014B_UPSTREAM_PERMISSION_REQUEST.md`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/research/RC014B_UPSTREAM_PERMISSION_REQUEST.md) status is **`PENDING_DISPATCH`**.
* **Humdrum KernScores Mirror (`automata/ana-music`)**:
  - Root License: `UNDECLARED` in mirror; CCARH / KernScores upstream typically maintains non-commercial academic attribution guidelines.
  - License Status: **`SUPPLEMENT_LICENSE_PENDING`**.

---

## 4. Human Decision Routing

Prior to unblinding RC-012 confirmatory statistics, the project oversight must record a human decision under one of three formal routes:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Formal Governance Routes                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route A: Explicit Upstream Permission Obtained                                                  │
│   - Formal written license waiver or explicit open-source license adopted by upstream authors. │
│   - Enables full vendoring or unrestricted non-vendored reference caching.                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route B: Formally Approved Non-Vendored Transformative Research Policy                          │
│   - Institutional determination that non-vendored ephemeral materialization and retention of    │
│     abstract 56-descriptor numerical representations complies with academic fair use /          │
│     text-and-data-mining research exceptions, with raw redistribution strictly prohibited.     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Route C: Authority Insufficient                                                                 │
│   - Confirmatory promotion blocked. Rubinstein and Prokofiev excluded from confirmation.       │
│   - Live confirmatory pool remains N_Russian = 2 (Scriabin + Mussorgsky).                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Human Decision Record

* **Current Milestone Outcome**: `RC014C_CORPUS_FROZEN_AWAITING_HUMAN_ACCESS_APPROVAL`
* **Authorized Signatory**: `[ PENDING HUMAN OVERSIGHT REVIEW ]`
* **Decision Date**: `[ PENDING ]`
* **Selected Route**: `[ PENDING: Route A | Route B | Route C ]`
* **Live Production Pool Gate**: **`BLOCKED`** ($N_{\text{Russian}} = 2$ remains active; RC-012 evaluation remains strictly prohibited until human authorization is logged).
