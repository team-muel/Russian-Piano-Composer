# PF-001B.2: Physical Classical Corpus Feasibility Audit
## Canonical Parser Verification, Dual-Hash Source Provenance, and Readiness Freeze

**Document Type:** Empirical Corpus Feasibility & Provenance Audit  
**Milestone:** PF-001B.2  
**Project:** Russian Piano Composer (`team-muel/Russian-Piano-Composer`)  
**Status:** CANONICAL_PARSE_AND_DUAL_HASH_PROVENANCE_AUDITED  
**Governing Rule:** Anti-RC-013 Physical Source Verification & Canonical Parser Invariant  

---

### Executive Summary

Milestone **PF-001B.2** closes the canonical parser and dual-hash provenance semantics across the verified physical corpus:
1. **Separation of Syntax from Musical Validity:** XML syntactic well-formedness is designated strictly as `XML_WELL_FORMED_VERIFIED`. It is decoupled from canonical music notation parsing.
2. **Canonical Music Parser Verification (`CANONICAL_PARSE_PASS`):**
   - For all 53 DCML MuseScore `.mscx` scores, canonical parsing is verified via the project's internal parser stack (`ms3.Score` and `ingest_score_entry_from_ms3`). Every score proves non-zero measure count, non-zero musical events, valid note/rest distributions, rational onsets/durations, valid staves/voices, and valid spelled pitches into `CanonicalScore`.
   - For all 9 tracked RC-013 MusicXML scores, canonical parsing is verified via `RC013ScoreValidator.validate_file()` backed by `music21`, certifying notation well-formedness, structural staves, note counts, and bar-duration integrity (`valid == True`).
3. **Dual-Hash Provenance & Explicit Canonicalization Policy:**
   - Upstream immutable bytes and downstream materialized working bytes are explicitly decoupled.
   - For externally materialized scores (DCMLab), `upstream_raw_sha256` records the exact byte identity from the upstream git commit, while `canonical_materialized_sha256` records the local working file after applying the declared `LF_TO_CRLF` policy.
   - For tracked repository scores, `repository_blob_or_commit_identity` and `canonical_materialized_sha256` are recorded under an `IDENTITY` policy.
4. **Machine-Readable Remote Materialization Receipt:**
   - A complete audit receipt is serialized at [`data/reviews/pf001/pf001b_remote_materialization_receipt.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/reviews/pf001/pf001b_remote_materialization_receipt.json) covering all 4 source families and 62 physical score artifacts, sealed with a deterministic SHA-256 receipt hash.
5. **Readiness Scope for PF-001C1:**
   - Declares readiness strictly for `METRIC_DEFINITION_AND_CALIBRATION_PROCEDURE_FREEZE`.
   - Composer Generalization Gate remains strictly `NOT_READY_FOR_CALIBRATION`.

---

### 1. Repertoire Contrast: Estimated vs. Physically Verified

The following table records the audited physical inventory $M_{c,\text{verified}}$ (all 62 pieces achieving `CANONICAL_PARSE_PASS`):

| Composer | Cohort | PF-001A Est. Candidate | PF-001A Est. Usable | $M_{c,\text{files}}$ (Physical) | $M_{c,\text{eligible}}$ (Solo Piano) | $M_{c,\text{xml}}$ (Well-Formed) | $M_{c,\text{canonical}}$ (Parse Pass) | Canonical Parser & Version | Feasibility Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Pyotr Ilyich Tchaikovsky** | Development | 138 | 90 | 12 | 12 | 12 | 12 | `ms3` 2.6.4 | `FEASIBLE_SUBSET_VERIFIED` |
| **Sergei Rachmaninoff** | Development | 84 | 48 | 22 | 22 | 22 | 22 | `ms3` 2.6.4 | `FEASIBLE_SUBSET_VERIFIED` |
| **Alexander Scriabin** | Development | 180 | 120 | 0* | 0* | 0* | 0* | N/A (*Lineage Excluded) | `BLOCKED_PENDING_INDEPENDENT_ACQUISITION` |
| **Anton Arensky** | Development | 72 | 36 | 3 | 3 | 3 | 3 | `music21` 10.5.0 | `MARGINALLY_FEASIBLE_PILOT` |
| **Nikolai Medtner** | Validation | 65 | 22 | 19 | 19 | 19 | 19 | `ms3` 2.6.4 | `FEASIBLE_SUBSET_VERIFIED` |
| **Mily Balakirev** | Validation | 45 | 18 | 0 | 0 | 0 | 0 | None | `BLOCKED_UNTIL_DIGITIZED` |
| **Anatoly Liadov** | Validation | 60 | 32 | 3 | 3 | 3 | 3 | `music21` 10.5.0 | `MARGINALLY_FEASIBLE_PILOT` |
| **Reinhold Glière** | Validation | 55 | 16 | 0 | 0 | 0 | 0 | None | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Taneyev** | External Held-Out | 28 | 7 | 0 | 0 | 0 | 0 | None | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Bortkiewicz** | External Held-Out | 42 | 12 | 0 | 0 | 0 | 0 | None | `BLOCKED_PENDING_RIGHTS_AUDIT` |
| **Felix Blumenfeld** | External Held-Out | 40 | 8 | 0 | 0 | 0 | 0 | None | `BLOCKED_UNTIL_DIGITIZED` |
| **Georgy Catoire** | External Held-Out | 25 | 5 | 0 | 0 | 0 | 0 | None | `BLOCKED_UNTIL_DIGITIZED` |
| **Sergei Lyapunov** | Benchmark Pilot | N/A | N/A | 3 | 3 | 3 | 3 | `music21` 10.5.0 | `BENCHMARK_PILOT_VERIFIED` |
| **Total** | | **754** | **414** | **62** | **62** | **62** | **62** | — | — |

*\*Lineage Classification of Alexander Scriabin:*
Scriabin's 207 solo piano works in the repository are governed by the strict scientific lineage policy:
- `PREVIOUSLY_EXPOSED_IN_RC012`
- `EXCLUDED_FROM_PF_DEVELOPMENT_BY_LINEAGE_POLICY`
- `NOT_ELIGIBLE_AS_UNTOUCHED_EXTERNAL_DATA`

Because RC-012 confirmatory analysis evaluated Scriabin within its confirmatory baseline, these pieces cannot serve as an untouched held-out evaluation cohort for the Perception-First Artificial Listener, nor can they be used for development/tuning without explicit lineage isolation.

---

### 2. Multi-Stage Pipeline Audit Findings

#### 2.1 Five-Stage Verification Pipeline
The verification protocol enforces five distinct mechanical stages:
1. `SOURCE_IDENTITY_VERIFIED`: Immutable repository URL, commit hash, and expected cryptographic hashes bound (62 / 62).
2. `SOURCE_BYTES_MATERIALIZED`: Physical file present on disk with non-zero byte size (62 / 62).
3. `DUAL_HASH_AND_POLICY_VERIFIED`: Upstream raw bytes and canonical materialized bytes match declared hashes under explicit `canonicalization_policy` (`IDENTITY` or `LF_TO_CRLF`) (62 / 62).
4. `XML_WELL_FORMED_VERIFIED`: XML syntactic parseability and element well-formedness verified via `xml.etree.ElementTree` (62 / 62).
5. `CANONICAL_PARSE_PASS`: Full musical score parse into canonical event representations via `ms3` and `RC013ScoreValidator` (`music21`) (62 / 62).

#### 2.2 Canonical Music Parser Stack & Diagnostics
- **DCML MuseScore (`.mscx`):**
  - Parser: `ms3` (v2.6.4) & `ingest_score_entry_from_ms3`.
  - Diagnostics verified per score: non-zero measures (range: 24 to 289), non-zero notes (range: 226 to 5,283), rational onsets and durations, staves 1 & 2, voices 1 & 2, scientific pitch representations.
  - Zero parse failures or unhandled exceptions across all 53 DCML files.
- **RC-013 MusicXML (`.musicxml`):**
  - Parser: `music21` (v10.5.0) via `RC013ScoreValidator`.
  - Diagnostics verified per score: `valid == True`, positive measure counts (range: 26 to 142), positive notes (range: 309 to 3,091), staves/parts aligned.
  - Zero validation defects.

#### 2.3 Dual-Hash Provenance Ledger
- All 53 DCML files record both `upstream_raw_sha256` and `canonical_materialized_sha256` alongside `canonicalization_policy: LF_TO_CRLF`.
- All 9 RC-013 canonical MusicXML files record `repository_blob_or_commit_identity` and `canonical_materialized_sha256` alongside `canonicalization_policy: IDENTITY`.
- The remote materialization receipt at `data/reviews/pf001/pf001b_remote_materialization_receipt.json` holds a deterministic receipt hash:
  `db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d`.

#### 2.4 Solo-Piano Eligibility
- All 62 verified physical scores represent unreduced, original solo-piano compositions.

#### 2.5 Rights and Access Governance
- All compositions are verified public domain or open research licenses (CC-BY-NC-SA-4.0).
- Sergei Bortkiewicz remains blocked pending post-1952 rights clearance.

---

### 3. Threshold De-Provisionalization Architecture (PF-001B.2 → PF-001C1)

In `docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md`, all numerical targets in the autonomous validation gates remain explicitly classified as:
$$\texttt{PROVISIONAL\_UNCALIBRATED\_TARGET}$$

#### Calibration Scope & Composer Generalization Gate:
- **`calibration_scope`:** `METRIC_DEFINITION_AND_CALIBRATION_PROCEDURE_FREEZE`
  - *Readiness Scope:* Ready to freeze the mathematical metric definitions, background frequency distributions, and calibration protocols in PF-001C1. Numerical threshold values will NOT be chosen before the Listener model is instantiated.
- **`COMPOSER_GENERALIZATION_GATE`:** `NOT_READY_FOR_CALIBRATION`
  - *Rationale:* Current verified composer counts (Tchaikovsky: 12, Rachmaninoff: 22, Medtner: 19, plus 9 canonical pilot movements) are too sparse across disjoint partitions to justify final composer-transfer threshold calibration.

---

### 4. Firewall Invariant for External-Test Cohort

The external test cohort comprising:
- Sergei Taneyev
- Sergei Bortkiewicz
- Felix Blumenfeld
- Georgy Catoire

remains **strictly firewalled**:
- Exactly **0** physical files exist or are materialized in the repository.
- Zero musical tokens, feature representations, or latent state probes from these composers may be used during Listener architecture selection, representation pre-training, or gate calibration.

---

### 5. Final Audit Verdict

$$\textbf{Outcome Token: } \texttt{PF001B\_CANONICAL\_PARSE\_AND\_PROVENANCE\_CLOSED\_READY\_FOR\_PF001C1}$$

The physical classical corpus inventory [`data/reviews/pf001/pf001_physical_corpus_inventory.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/reviews/pf001/pf001_physical_corpus_inventory.json) contains exactly 62 verified physical scores backed by retrievable machine-readable artifacts, zero placeholder rows, dual-hash provenance records, explicit canonicalization policies, XML syntactic well-formedness, and certified canonical music parsing.
