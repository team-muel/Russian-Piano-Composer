# RC-014C Confirmatory Corpus Governance Freeze Report

## 1. Executive Summary & Git Lineage

* **Repository**: `team-muel/Russian-Piano-Composer`
* **Target Branch**: `rc/013-confirmatory-corpus-acquisition`
* **Starting Remote & Local HEAD**: `5b3b6c9e4dddf9924c18fd65c31723c2bd7c9fa1`
* **Milestone Purpose**: Freeze the candidate confirmatory Russian piano corpus, lock external source identities and Git blob hashes, freeze the role-blind 56-descriptor feature cache, establish the five-axis legal governance decision routing, and compute the master pre-unblinding integrity hash prior to any execution of RC-012 statistics.

---

## 2. Exact-Head CI Fix & MyPy Quality Assurance

Prior to corpus freezing, CI typecheck failures in legacy RC-013 OMR inspection modules were resolved:
1. **Targeted Import Policy**: Added `cv2.*` to `[[tool.mypy.overrides]]` and added `opencv-python-headless>=4.8` to package dependencies in `pyproject.toml`.
2. **Type Narrowing**: Added explicit `np.asarray(img, dtype=np.uint8)` return narrowing in `rc013_falsification_protocol.py:_render_musicxml_to_image` to eliminate `no-any-return` warnings under strict MyPy mode.
3. **QA Verification**:
   - `ruff check src tests scripts`: **PASS** (0 errors)
   - `mypy src`: **PASS** (0 errors across 88 source files)
   - `pytest tests/`: **PASS** (451 passed, 0 failed)

---

## 3. Direct Humdrum Source-Token Census & Structural Sanity

To ensure no catastrophic parser omissions occurred during `music21` ingestion of the two Humdrum supplements, a bounded direct token census was conducted on the raw Git blob bytes:

| Metric / Token Class | Op. 22 No. 2 (*Andante*) Source Text | Op. 22 No. 2 `music21` Parsed | Op. 22 No. 3 (*Allegretto*) Source Text | Op. 22 No. 3 `music21` Parsed | Correspondence Verdict |
|---|---|---|---|---|---|
| **Barlines / Measures** | 24 | 24 | 28 | 28 | **100.0% EXACT** |
| **Strictly `**kern` Pitch Tokens** | 269 | 269 (185 single + 84 chord) | 588 | 588 (185 single + 403 chord) | **100.0% EXACT** |
| **Rest Tokens (`r`)** | 34 | 34 | 23 | 23 | **100.0% EXACT** |
| **Spine Splits / Joins** | 3 splits / 6 joins | 10 Voice substreams | 10 splits / 20 joins | 53 Voice substreams | **EXPLAINED** |
| **Meter Interpretations** | `*M4/4` | 4/4 | `*M4/4`, `*M2/4` | 4/4 $\leftrightarrow$ 2/4 shifts | **100.0% EXACT** |

### Terminology Precision:
* `SOURCE_TO_MUSIC21_STRUCTURAL_SANITY = PASS`
* `MUSIC21_PARSED_EVENT_CONSERVATION = 100.0% (PASS)`

---

## 4. Frozen Technical Source Authorities

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Immutable External Source Authorities                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Tonal-Piano-Corpus (TPC):                                                                               │
│   - Repository: hectorbellmann-art/Tonal-Piano-Corpus                                                   │
│   - Frozen Commit: 3f5a08e9b2360c11aea5d6d384eb84e7845b793c                                            │
│   - Root Tree SHA: 2e86805f11040570d1f2f45bc0f03be408ca4997                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Humdrum Supplement Repository:                                                                          │
│   - Repository: automata/ana-music                                                                      │
│   - Frozen Commit: 335cbdc617c919d29e9384c4e490cabca5736f73                                            │
│   - Root Tree SHA: a7f14da4844b47ac3484b01d5d3da2a0029e4b6a                                            │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Final Proposed Confirmatory Russian Pool

| Composer | Qualification Status | Target $M_c$ | Available $M_c$ | Provenance & Source Authority |
|---|---|---|---|---|
| **Alexander Scriabin** | `LIVE_QUALIFIED` | 10 | 207 | Stanford CCARH Humdrum (`craigsapp/scriabin`) |
| **Modest Mussorgsky** | `LIVE_QUALIFIED` | 10 | 10 | DCML *Pictures at an Exhibition* (`musescore/dcml`) |
| **Anton Rubinstein** | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 11 | 11 | `Tonal-Piano-Corpus` (8 Op. 75, 3 Op. 24) |
| **Sergei Prokofiev** | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 10 | 10 | 8 pre-1931 TPC works + 2 Craig Humdrum supplements (Op. 22 Nos. 2 & 3) |

**Deduplication Audit**: Audited potential collision for *Visions Fugitives* Op. 22 No. 1 (present in both TPC and Humdrum). Op. 22 No. 1 is retained exclusively from TPC; Humdrum provides only Nos. 2 & 3. **0 duplicate works exist across the confirmatory pool**.

---

## 6. Frozen Repertoire Specifications

### 6.1 Anton Rubinstein ($M = 11 \ge 10$)
All 11 works published 1854–1866 (Public Domain worldwide):
1. `tonal_piano_corpus:rubinstein_op75_no1_reverie` (Op. 75 No. 1, 1866)
2. `tonal_piano_corpus:rubinstein_op75_no2_torche_dance` (Op. 75 No. 2, 1866)
3. `tonal_piano_corpus:rubinstein_op75_no3_nocturne` (Op. 75 No. 3, 1866)
4. `tonal_piano_corpus:rubinstein_op75_no4_barcarolle` (Op. 75 No. 4, 1866)
5. `tonal_piano_corpus:rubinstein_op75_no5_valse_caprice` (Op. 75 No. 5, 1866)
6. `tonal_piano_corpus:rubinstein_op75_no6_romance` (Op. 75 No. 6, 1866)
7. `tonal_piano_corpus:rubinstein_op75_no7_toccata` (Op. 75 No. 7, 1866)
8. `tonal_piano_corpus:rubinstein_op75_no8_marche_funebre` (Op. 75 No. 8, 1866)
9. `tonal_piano_corpus:rubinstein_op24_no1_prelude` (Op. 24 No. 1, 1854)
10. `tonal_piano_corpus:rubinstein_op24_no2_prelude` (Op. 24 No. 2, 1856)
11. `tonal_piano_corpus:rubinstein_op24_no3_prelude` (Op. 24 No. 3, 1856)

### 6.2 Sergei Prokofiev ($M = 10 \ge 10$)
All 10 works published 1907–1918 (Public Domain worldwide):
1. `tonal_piano_corpus:prokofiev_op11_toccata` (Op. 11, 1912)
2. `tonal_piano_corpus:prokofiev_op12_no2_legend` (Op. 12 No. 2, 1913)
3. `tonal_piano_corpus:prokofiev_op12_no7_prelude_harp` (Op. 12 No. 7, 1913)
4. `tonal_piano_corpus:prokofiev_op3_no3_march` (Op. 3 No. 3, 1907)
5. `tonal_piano_corpus:prokofiev_op2_no4_etude` (Op. 2 No. 4, 1909)
6. `tonal_piano_corpus:prokofiev_op22_no1_lentamente` (Op. 22 No. 1, 1917, pub. 1918)
7. `tonal_piano_corpus:prokofiev_op22_no5_molto_giocoso` (Op. 22 No. 5, 1917, pub. 1918)
8. `tonal_piano_corpus:prokofiev_op22_no10_ridicolosamente` (Op. 22 No. 10, 1917, pub. 1918)
9. `ana_music:prokofiev_op22_no02` (Op. 22 No. 2, 1917, pub. 1918)
10. `ana_music:prokofiev_op22_no03` (Op. 22 No. 3, 1917, pub. 1918)

---

## 7. Role-Blind Feature Cache & Pre-Unblinding Freeze Hash

* **Master Feature Schema Hash**: `924a19913f831c4f0ffba2dfa88188b88e598af635046b05e580e5b807355282`
* **Feature Descriptor Count**: Exactly 56 descriptors per piece across all 21 candidates (0 NaNs, role-blind).
* **Role-Blind Feature Cache Matrix SHA-256**:
  $$\mathbf{f970fdb656700c842a3ac4fd361b3766d056bae663d62b1170242041cc1f2876}$$
* **Master Pre-Unblinding Confirmatory Corpus Freeze Hash**:
  $$\mathbf{RC014C\_CONFIRMATORY\_CORPUS\_FREEZE\_HASH} = \mathbf{782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8}$$

---

## 8. Invalidation Policy

Any subsequent modification to:
1. External repository commits, trees, or blob bytes;
2. MusicXML / Humdrum canonical parser implementations or conversion rules;
3. Master structural schema (`STRUCTURAL_REPRESENTATION_SCHEMA_V1`) or descriptor extraction algorithms;
4. Candidate piece membership or inclusion/exclusion filters;

shall immediately **invalidate** the RC-014C corpus freeze, all cached feature matrices, and any downstream confirmatory statistical evaluations derived therefrom.

---

## 9. Live Governance Gate & Final Outcome Verdict

* **Live Confirmatory Russian Pool**: $N_{\text{Russian}} = 2$ (*Alexander Scriabin*, *Modest Mussorgsky*).
* **RC-012 Unblinding / Execution Gate**: **`BLOCKED`** (No classifier evaluated, no Russian-vs-control statistics computed).
* **Outcome State**:

$$\mathbf{RC014C\_CORPUS\_FROZEN\_AWAITING\_HUMAN\_ACCESS\_APPROVAL}$$
