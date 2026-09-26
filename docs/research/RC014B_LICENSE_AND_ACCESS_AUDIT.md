# RC-014B License and Data-Access Rights Audit

**Status**: FORMALLY AUDITED & FROZEN  
**Milestone**: RC-014B License Resolution & Non-Vendored Access Design  
**Execution Date**: 2026-09-26  
**Audited Repository**: `https://github.com/hectorbellmann-art/Tonal-Piano-Corpus`  
**Target Commit**: `3f5a08e9b2360c11aea5d6d384eb84e7845b793c`  
**Actual Root Tree SHA**: `2e86805f11040570d1f2f45bc0f03be408ca4997`  
**Primary Manifest Artifact**: [`data/manifests/rc014b_external_access_policy.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/manifests/rc014b_external_access_policy.json)

---

## 1. Executive Summary & Legal Principles

Scientific usability and legal redistribution authorization are distinct dimensions. A symbolic score file may possess outstanding musicological fidelity while lacking an open-source license that permits copying or redistributing its bytes into a secondary repository.

### Project Legal Principles:
1. **No Implied Open License from Public GitHub Hosting**: A public repository on GitHub grants platform viewing/forking rights under the GitHub Terms of Service, but does not grant open redistribution or re-licensing rights unless an explicit LICENSE is attached.
2. **Default Fail-Closed Posture**: Where no explicit license is declared, `digital_transcription_license` = `UNDECLARED`.
3. **No Premature Vendoring**: Raw MusicXML, Finale MUS, and TIFF scans from `Tonal-Piano-Corpus` must **not** be copied or committed into this repository until explicit upstream permission or an open license waiver is established.

---

## 2. Exhaustive Repository History & Metadata Audit

A complete forensic audit of the `Tonal-Piano-Corpus` git commit history, documentation, and XML metadata was conducted:

* **Root License File**: **ABSENT** (no `LICENSE`, `COPYING`, or `UNLICENSE` file at repository root).
* **GitHub Detected License**: `null`.
* **Git Commit History Analysis**:
  - Examined all 20 commits from initial upload to `3f5a08e` (May 2026).
  - Searched for keyword insertions (`license`, `copyright`, `permission`, `terms`, `cc-by`).
  - Found commit `198b9c2` (*Update Readme.md*) adding section "Copyright-Restricted Composers" which states:
    > "Their engraved files (TIFF, MUS/MUSX, and MusicXML) are preserved privately and are not distributed in this public repository. They may be shared individually upon request for scholarly research under fair dealing provisions."
  - This demonstrates that the corpus creator is actively aware of copyright boundaries, but left the public repository without an explicit downstream reuse/redistribution license.
* **Embedded MusicXML `<rights>` Tags**:
  - Contains year integers (e.g. `<rights>1917</rights>`, `<rights>1912</rights>`) referencing original historical composition/publication dates, with zero digital license grants.
* **Corpus Creator Identification**:
  - Author: `hectorbellmann-art` (`hectorbellmann@gmail.com`).

---

## 3. Disaggregated Rights & Permission Taxonomy

The project adopts a 7-dimensional legal rights taxonomy:

| Dimension | Description | Anton Rubinstein | Sergei Prokofiev (Pre-1931) | Sergei Prokofiev (Post-1930) |
| :--- | :--- | :---: | :---: | :---: |
| **`underlying_composition_status`** | Copyright term of musical work | **CLEAR** (Died 1894; PD worldwide) | **CLEAR** (PD in US & EU/UK) | **RESTRICTED** (Protected in US until 2031/2033; PD in EU/UK) |
| **`historical_print_status`** | Rights in original printed editions | **CLEAR** (Senff 1854/1866; PD) | **CLEAR** (Gutheil/Jurgenson; PD) | **CLEAR** (Muzgiz 1935/1937; PD in RU/EU) |
| **`digital_transcription_license`** | Explicit upstream digital encoding license | **UNDECLARED** (No root LICENSE) | **UNDECLARED** (No root LICENSE) | **UNDECLARED** (No root LICENSE) |
| **`repository_reuse_permission`** | Authorization to reuse files in another repo | **UNDECLARED** | **UNDECLARED** | **UNDECLARED** |
| **`local_scientific_analysis_permission`** | Permission to analyze in local research runtime | **CLEAR** (Research exception / ToS) | **CLEAR** (Research exception / ToS) | **CLEAR** (Research exception / ToS) |
| **`redistribution_permission`** | Authorization to redistribute source bytes | **NOT_ESTABLISHED** | **NOT_ESTABLISHED** | **NOT_ESTABLISHED** |
| **`derivative_distribution_permission`** | Authorization to distribute 56-D feature vectors | **CLEAR** (Non-expressive facts) | **CLEAR** (Non-expressive facts) | **CLEAR** (Non-expressive facts) |

---

## 4. Non-Vendored Reproducible Reference Architecture

To enable complete scientific reproducibility without infringing copyright or redistributing unlicensed digital files, a **Non-Vendored Reference Ingestion Architecture** is established:

```text
External Source Repository (GitHub: hectorbellmann-art/Tonal-Piano-Corpus)
                        │
                        ▼ (Pinned immutable commit: 3f5a08e9b2360c11aea5d6d384eb84e7845b793c)
                        ▼ (Exact Git Tree: 2e86805f11040570d1f2f45bc0f03be408ca4997)
┌────────────────────────────────────────────────────────────────────────┐
│ Cryptographic Pinning Manifest (data/manifests/rc014b_external_access_policy.json) │
│ - Target relative paths                                                │
│ - Exact Git blob SHAs                                                  │
│ - SHA-256 byte checksums                                               │
└────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼ (Automated on-demand checkout / download to ephemeral scratch)
                        ▼ (Fail-closed cryptographic hash verification)
┌────────────────────────────────────────────────────────────────────────┐
│ RC-011 Structural Feature Extractor (56 Descriptors)                   │
└────────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Derived Feature Matrices Only (data/processed/structural_matrices/)   │
│ (Pure mathematical vectors of 56 floats; 0 MusicXML/TIFF source bytes) │
└────────────────────────────────────────────────────────────────────────┘
```

### Reproducibility Contract:
1. Every score entry is bound to its immutable Git commit and git blob SHA.
2. If upstream changes a single byte, git tree or blob SHA verification immediately halts execution (`FAIL_CLOSED`).
3. Only the non-expressive, high-level mathematical feature representation (56 float values per piece) is retained in the project repository.

---

## 5. Anton Rubinstein & Sergei Prokofiev Status

* **Anton Rubinstein**:
  - `technical_compatibility`: **PASS (11/11)**
  - `underlying_composition`: **CLEAR**
  - `digital_transcription_license`: **UNDECLARED**
  - `confirmatory_status`: **TECHNICALLY_READY_LICENSE_AUTHORITY_PENDING**
* **Sergei Prokofiev**:
  - `technical_compatibility`: **PASS (12/12)**
  - `pre_1931_works`: **8 pieces** (Op. 2 No. 4, Op. 3 No. 3, Op. 11, Op. 12 Nos. 2, 7, Op. 22 Nos. 1, 5, 10)
  - `post_1930_works`: **4 pieces** (Op. 65 Nos. 1, 7, 12, Op. 75 No. 6) $\rightarrow$ US protected.
  - `confirmatory_status`: **TECHNICALLY_READY_LICENSE_AUTHORITY_PENDING**

---

## 6. Official RC-014B Decision

In accordance with strict legal and scientific governance:

```text
PRIMARY_DECISION = RC014B_NONVENDORED_REFERENCE_PATH_VALID
SECONDARY_ACTION = RC014B_UPSTREAM_PERMISSION_REQUEST_DISPATCH
```

*Vendoring is strictly suspended. The non-vendored reference path is fully designed, cryptographically pinned, and ready for implementation in RC-014C.*
