# RC-007 Symbolic Score Ingestion Report (v1) & Data Integrity Audit (RC-007A)

## Executive Summary
This report documents the completion of **RC-007 — Verified Corpus Acquisition and Symbolic Score Ingestion** and its formal acceptance audit **RC-007A**.

All six registered corpus sources (3 Russian generative-role, 3 Non-Russian control-role) were acquired at their exact 40-character Git commit SHAs, streaming SHA-256 inventoried, and ingested into canonical symbolic score representation with 100% inventory completeness and zero data corruption.

$$\boxed{141 \text{ Score Entries Expected} \rightarrow 141 \text{ Score Entries Ingested} \rightarrow 0 \text{ Mismatches / Failures}}$$

- **Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`  
- **Runtime Environment**:
  - Python: `3.12.10`
  - ms3: `2.6.4`
  - pandas: `2.2.3`
  - pyarrow: `19.0.1`
  - Canonical Schema Version: `1`

---

## 1. Corpus Acquisition & Canonical Metrics

### Corpus-Level Canonical Counts Table

| Corpus ID | Role | Expected Entries | Ingested Pieces | Measures | Events | Notes | Rests | Grace Notes | Ties | Canonical Corpus Hash |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `dcml_medtner_tales` | `GENERATIVE_RUSSIAN` | 19 | 19 | 2,474 | 46,288 | 42,959 | 3,329 | 848 | 3,214 | `3c79868ab27e22979aac743fba684541bf44ee1fc989e154ef90edb9ed10ee01` |
| `dcml_rachmaninoff_op42` | `GENERATIVE_RUSSIAN` | 22 | 22 | 417 | 11,313 | 10,087 | 1,226 | 89 | 412 | `b2e6a0552912c662a2f3f2e1cf29a7a827738bf0e1f13e4d6d1215601aea2d91` |
| `dcml_tchaikovsky_seasons` | `GENERATIVE_RUSSIAN` | 12 | 12 | 1,252 | 21,459 | 18,751 | 2,708 | 82 | 1,146 | `02fc810b812b631c16c8cd830650d312d90ea1789af128d8cf3875ae2b13f08a` |
| `dcml_chopin_mazurkas` | `CONTROL_NON_RUSSIAN` | 56 | 56 | 4,977 | 61,586 | 57,986 | 3,600 | 945 | 2,610 | `9bb2c3b2b0a68fd680fd57fb7fd18a2e931bd81b59799845a14e5afaf5c7b147` |
| `dcml_liszt_annees` | `CONTROL_NON_RUSSIAN` | 19 | 19 | 2,640 | 69,167 | 59,534 | 9,633 | 316 | 1,918 | `064ef54a0e35c0c333a7e8178b07f458eaf3d790561be294c877a1acbb28cabc` |
| `dcml_schumann_kinderszenen` | `CONTROL_NON_RUSSIAN` | 13 | 13 | 406 | 5,678 | 5,276 | 402 | 44 | 504 | `3380d578f068b617e9d8055eade605ad188a43c1406f5c39cb8c231aa98f8a1f` |

### Role Aggregates

- **`GENERATIVE_RUSSIAN`**: 3 Corpora, 53 Pieces, 4,143 Measures, 79,060 Events, 71,797 Notes, 7,263 Rests, 1,019 Grace Notes, 4,772 Ties.
- **`CONTROL_NON_RUSSIAN`**: 3 Corpora, 88 Pieces, 8,023 Measures, 136,431 Events, 122,796 Notes, 13,635 Rests, 1,305 Grace Notes, 5,032 Ties.
- **Grand Total**: 6 Corpora, 141 Pieces, 12,166 Measures, 215,491 Events, 194,593 Notes, 20,898 Rests, 2,324 Grace Notes, 9,804 Ties.

---

## 2. Ingestion Integrity Audit Results

1. **Acquisition Idempotency**:
   - Execution of `scripts/acquire_corpus.py --all` returned `SKIPPED_ALREADY_VERIFIED` for all 6 corpora. Zero raw file modifications, zero HEAD shifts, zero receipt tampering.
2. **Acquisition Receipt Audit**:
   - Verified 6/6 receipts. Expected Commit == Actual Commit for all 6 corpora. Artifact mismatch count = 0.
3. **Local Git Commit Identity**:
   - Verified local Git HEADs in `data/raw/*`:
     - `dcml_medtner_tales`: `1d2e58ba8d329463829e45e75900af43be4256bf`
     - `dcml_rachmaninoff_op42`: `a73f3246a764215863000357c81309b210a43f15`
     - `dcml_tchaikovsky_seasons`: `5af15033c5f9c282f38fcf71234b86349e61e8c3`
     - `dcml_chopin_mazurkas`: `5931135e614985023b96de2a291c74b7ef90b287`
     - `dcml_liszt_annees`: `f1cfd308adba5763aad3a18885eac48d42449fc4`
     - `dcml_schumann_kinderszenen`: `ee929c1556bc937fe1ea7303cac4476e37caa4d1`
   - All 6 local working trees clean.
4. **Exact Inventory Equality**:
   - Missing: 0, Extra: 0, Duplicate: 0. Exact set equality confirmed (`141 / 141`).
5. **Pitch / MIDI Preservation**:
   - Checked 194,593 note events across all 6 corpora. Pitch/MIDI mismatch count = 0.
6. **Timing Rational Integrity**:
   - Float-only timing fields = 0. All durations, onsets, offsets use exact integer numerators and denominators (`*_num`, `*_den`).
   - Fraction denominator > 0 violations = 0.
7. **Per-Piece Non-Empty Invariant**:
   - Enforced in `CanonicalScore.__post_init__` and regression tested. All 141 pieces have `measures > 0`, `events > 0`, `notes > 0`.
8. **Repeat Policy**:
   - Written measures == Canonical measures. No playback duplication introduced by repeat unfolding.
9. **Staff Is Not Hand**:
   - `STAFF_TO_HAND_ASSUMPTION = none`. Staffs represent score staves (e.g. staff 1, staff 2), not physical hands.
10. **Canonical Parquet Schema**:
    - `onset_num`, `onset_den`, `offset_num`, `offset_den`, `duration_num`, `duration_den`: `int64`
    - `pitch_letter`, `pitch_alteration`, `pitch_octave`, `midi`: `string` / `int64`
    - `staff`, `voice`, `event_kind`: `int64` / `string`
11. **Git Isolation**:
    - `git ls-files data/raw data/interim data/processed` returned 0 files. All payload data properly gitignored.
12. **Rights Boundary Audit**:
    - All 6 corpora remain `rights_review_required: true`, `rights_status: REVIEW_REQUIRED`, `generative_eligible: false`. Technical ingestion does not alter rights flags.
13. **Acquisition Receipt Tamper Verification**:
    - Sandboxed tamper test confirmed that mutating a raw score file triggers immediate SHA-256 mismatch detection.

---

## 3. Upstream TSV Cross-Validation

Cross-validated canonical measure counts against upstream DCML `measures.tsv` facets for lexicographically first score entries:

| Corpus ID | Score Entry ID | Canonical Measures | Upstream TSV Measures | Mismatch Count | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `dcml_medtner_tales` | `op08n01` | 118 | 118 | 0 | `MATCH` |
| `dcml_rachmaninoff_op42` | `op42_01a` | 16 | 16 | 0 | `MATCH` |
| `dcml_tchaikovsky_seasons` | `op37a01` | 105 | 105 | 0 | `MATCH` |
| `dcml_chopin_mazurkas` | `BI105-1op30-1` | 64 | 64 | 0 | `MATCH` |
| `dcml_liszt_annees` | `160.01_Chapelle_de_Guillaume_Tell` | 156 | 156 | 0 | `MATCH` |
| `dcml_schumann_kinderszenen` | `n01` | 22 | 22 | 0 | `MATCH` |

---

## 4. Deterministic Sample Audits

### Sample 1: `dcml_medtner_tales` — `op08n01`
- **Source Path**: `MS3/op08n01.mscx`
- **Source SHA-256**: `6e47e30d7b27814b78a994ef0a430ad8a514d241d7ceb10c5dfb5d1e2e92c2b3`
- **Canonical Piece ID**: `dcml_medtner_tales::op08n01`
- **Measures**: 118, **Events**: 1,642 (Notes: 1,514, Rests: 128, Grace: 14)
- **Piece Semantic Hash**: `9447ed5dcdceb78c80ad342e47854eb132a0c64998782a1ae5dcd5a898b8cbbf`
- **First 10 Canonical Events**:
  1. `m:0, staff:1, v:1, onset:0/1, dur:1/4, NOTE: C#5 (MIDI 73), tie:NONE, grace:False, loc:op08n01:m0:ev0`
  2. `m:0, staff:1, v:1, onset:1/4, dur:1/8, NOTE: E5 (MIDI 76), tie:NONE, grace:False, loc:op08n01:m0:ev1`
  3. `m:0, staff:1, v:1, onset:3/8, dur:1/8, NOTE: G#5 (MIDI 80), tie:NONE, grace:False, loc:op08n01:m0:ev2`
  4. `m:1, staff:1, v:1, onset:0/1, dur:3/8, NOTE: C#6 (MIDI 85), tie:NONE, grace:False, loc:op08n01:m1:ev3`
  5. `m:1, staff:1, v:1, onset:3/8, dur:1/8, NOTE: B5 (MIDI 83), tie:NONE, grace:False, loc:op08n01:m1:ev4`
  6. `m:1, staff:1, v:1, onset:1/2, dur:1/8, NOTE: A#5 (MIDI 82), tie:NONE, grace:False, loc:op08n01:m1:ev5`
  7. `m:1, staff:1, v:1, onset:5/8, dur:1/8, NOTE: G#5 (MIDI 80), tie:NONE, grace:False, loc:op08n01:m1:ev6`
  8. `m:1, staff:1, v:1, onset:3/4, dur:1/8, NOTE: F##5 (MIDI 79), tie:NONE, grace:False, loc:op08n01:m1:ev7`
  9. `m:1, staff:1, v:1, onset:7/8, dur:1/8, NOTE: G#5 (MIDI 80), tie:NONE, grace:False, loc:op08n01:m1:ev8`
  10. `m:1, staff:2, v:1, onset:0/1, dur:1/4, REST, tie:NONE, grace:False, loc:op08n01:m1:ev9`

### Sample 2: `dcml_rachmaninoff_op42` — `op42_01a`
- **Source Path**: `MS3/op42_01a.mscx`
- **Source SHA-256**: `38ad549301eb52055628b0304aa2ae018f27fb6eb5f9bc64e43e26bb96409ca2`
- **Canonical Piece ID**: `dcml_rachmaninoff_op42::op42_01a`
- **Measures**: 16, **Events**: 268 (Notes: 254, Rests: 14, Grace: 0)
- **Piece Semantic Hash**: `ad559385bfab0d4bb8cb16b3cf7fdf9e51c888e1781bd4398bc6719dd990c74b`

### Sample 3: `dcml_tchaikovsky_seasons` — `op37a01`
- **Source Path**: `MS3/op37a01.mscx`
- **Source SHA-256**: `75e01c9aeaeecdcbe3a7fef4db6a978ca76e8ea969a531e21bcfbc41c59c5d14`
- **Canonical Piece ID**: `dcml_tchaikovsky_seasons::op37a01`
- **Measures**: 105, **Events**: 1,124 (Notes: 1,028, Rests: 96, Grace: 8)
- **Piece Semantic Hash**: `b57a5303c2bb6f9c8942ea7ebcce1129b69b61dbd756ae4a0dc01b7a2d480cb1`

### Sample 4: `dcml_chopin_mazurkas` — `BI105-1op30-1`
- **Source Path**: `MS3/BI105-1op30-1.mscx`
- **Source SHA-256**: `5eefbb3511c5fdf7a52fbd1e6ed15ee9d8fec8a21146747b0a70f3f2d250882e`
- **Canonical Piece ID**: `dcml_chopin_mazurkas::BI105-1op30-1`
- **Measures**: 64, **Events**: 512 (Notes: 480, Rests: 32, Grace: 4)
- **Piece Semantic Hash**: `fa8730b1b16c879d7499691ab1a123a1ef5dcf4a7bc9910d5acfb7f0c13bb12d`

### Sample 5: `dcml_liszt_annees` — `160.01_Chapelle_de_Guillaume_Tell`
- **Source Path**: `MS3/160.01_Chapelle_de_Guillaume_Tell.mscx`
- **Source SHA-256**: `14ab1cb239dfc829e0cb78f8eb5430ab24bcbc0045e75127efed045dfef08912`
- **Canonical Piece ID**: `dcml_liszt_annees::160.01_Chapelle_de_Guillaume_Tell`
- **Measures**: 156, **Events**: 2,310 (Notes: 2,180, Rests: 130, Grace: 12)
- **Piece Semantic Hash**: `64a8b8efd824d5218ba132454b5df6792ed7153b6a987ef1c0800a747cfbb859`

### Sample 6: `dcml_schumann_kinderszenen` — `n01`
- **Source Path**: `MS3/n01.mscx`
- **Source SHA-256**: `87ef042125bb90efcae5436e2978cfbb201844ec10f01ba325bcbc41235bc078`
- **Canonical Piece ID**: `dcml_schumann_kinderszenen::n01`
- **Measures**: 22, **Events**: 284 (Notes: 268, Rests: 16, Grace: 0)
- **Piece Semantic Hash**: `d45b79147ebc7908bcac351239aa86790562e84bc7801df9cb8199b5120150ab`

---

## 5. Dependency Audit (`pyproject.toml`)

RC-007 modified `pyproject.toml` to add `"pyarrow>=15.0"` as a direct dependency.

- **What changed**: Added `"pyarrow>=15.0"` under project dependencies.
- **Why needed**: Ingestion directly imports `pyarrow` (`import pyarrow as pa`, `import pyarrow.parquet as pq`) for Parquet serialization and exact schema enforcement.
- **Direct vs Transitive**: Previously transitive through pandas; now explicitly represented as a direct dependency per project rules.

---

## 6. Formal Invariant Confirmations

- **FINAL ACQUISITION IS IDEMPOTENT** (`SKIPPED_ALREADY_VERIFIED`)
- **ALL 141 EXPECTED SCORE ENTRIES ARE NON-EMPTY CANONICAL SCORES**
- **EXPECTED == RESOLVED == INGESTED SCORE ENTRY SETS** (Missing = 0, Extra = 0, Duplicate = 0)
- **ALL CANONICAL NOTE SPELLINGS REPRODUCE THEIR MIDI** (0 Pitch/MIDI Mismatches)
- **NO FLOAT-ONLY CANONICAL TIMING** (0 Rational timing violations)
- **NO SOURCE DATA MUTATION**
- **NO RAW OR GENERATED CORPUS PAYLOAD IS TRACKED BY GIT**
- **NO STAFF-TO-HAND ASSUMPTION**
- **NO RIGHTS STATUS WAS UPGRADED**
- **NO RC-008 OR LATER IMPLEMENTATION PERFORMED**

$$\boxed{\text{RC-007 = ACCEPTED}}$$
