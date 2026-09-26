# RC-014C.1 Full Confirmatory Corpus Governance Freeze Report

## 1. Executive Summary & Git Lineage

* **Repository**: `team-muel/Russian-Piano-Composer`
* **Target Branch**: `rc/013-confirmatory-corpus-acquisition`
* **Starting Remote & Local HEAD**: `34d1881fc7ce8b5e8fe527489a3e5ca760441341`
* **Milestone Purpose**: Reconcile and freeze the complete 9-composer confirmatory corpus (483 total pieces across 4 Russian and 5 Control composers), lock source identities and Git blob hashes, freeze the full role-blind 56-descriptor feature cache, explicitly supersede the incomplete 21-piece RC-014C draft hash, and establish the master pre-unblinding integrity freeze hash prior to any execution of RC-012 statistics.

---

## 2. Supersession of RC-014C Draft Freeze

Forensic audit of RC-014C identified that its draft freeze hash covered only the 21 newly acquired pieces (11 Rubinstein + 10 Prokofiev), rather than the complete confirmatory corpus required by the preregistration contract.

Under RC-014C.1:
* **Superseded Hash**: `782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8`
* **Superseded Status**: `SUPERSEDED_INCOMPLETE_NEW_RUSSIAN_ADDITIONS_FREEZE`
* **Authoritative Complete Freeze Hash**: `RC014C1_CONFIRMATORY_CORPUS_FREEZE_HASH` = `06173918554380617153cadd4de66443733c33d52dbbe54813a10846b24e6330`

---

## 3. Complete Confirmatory Pool Census & Repertoire

Under the preregistered minimum threshold ($M_c \ge 10$) and default policy `USE_ALL_ELIGIBLE_PIECES`, the complete confirmatory corpus comprises **483 pieces** across **9 composers**:

| Composer | Class | Status | Minimum Threshold ($M_c$) | Eligible Pieces Count | Provenance & Source Authority |
|---|---|---|---|---|---|
| **Alexander Scriabin** | Russian | `LIVE_QUALIFIED` | 10 | **207** | Stanford CCARH Humdrum (`craigsapp/scriabin` commit `7daa1136`) |
| **Modest Mussorgsky** | Russian | `LIVE_QUALIFIED` | 10 | **18** | `SyMuPe/PERiScoPe` v1.1 (15 *Pictures* + 3 standalone pieces) |
| **Anton Rubinstein** | Russian | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 10 | **11** | `hectorbellmann-art/Tonal-Piano-Corpus` (commit `3f5a08e9`): Op. 75 Nos. 1, 2, 3, 4, 5, 6, 10, 11 and Op. 24 Nos. 1, 4, 6 |
| **Sergei Prokofiev** | Russian | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 10 | **10** | 8 pre-1929 TPC works + 2 Craig Humdrum supplements (Op. 22 Nos. 2 & 3) |
| **Edvard Grieg** | Control | `QUALIFIED_BASELINE` | 10 | **66** | `DCMLab/grieg_lyric_pieces` (commit `91a30456`) |
| **Claude Debussy** | Control | `QUALIFIED_BASELINE` | 10 | **54** | 7 DCMLab collections (`suite_bergamasque`, `preludes`, `etudes`, `childrens_corner`, `estampes`, `deux_arabesques`, `pour_le_piano`) |
| **Ludwig van Beethoven** | Control | `QUALIFIED_BASELINE` | 10 | **91** | `DCMLab/beethoven_piano_sonatas` (commit `ea7181bf`) |
| **Béla Bartók** | Control | `QUALIFIED_BASELINE` | 10 | **14** | `DCMLab/bartok_bagatelles` (commit `c6221f6e`) |
| **Antonín Dvořák** | Control | `QUALIFIED_BASELINE` | 10 | **12** | `DCMLab/dvorak_silhouettes` (commit `f228006f`) |

### Balance Summary:
- **Russian Confirmatory Pool**: 4 composers, 246 pieces.
- **Control Confirmatory Pool**: 5 composers, 237 pieces.
- **Grand Total**: 9 composers, 483 pieces.

---

## 4. Frozen Repertoire Specifications for Newly Added Russian Works

### 4.1 Anton Rubinstein ($M = 11 \ge 10$)
All 11 works published 1854–1866 (Public Domain worldwide):
1. `tonal_piano_corpus:1_souvenir` (*Album de Peterhof*, Op. 75 No. 1, 1866)
2. `tonal_piano_corpus:2_torche-dance` (*Album de Peterhof*, Op. 75 No. 2, 1866)
3. `tonal_piano_corpus:3_nocturne` (*Album de Peterhof*, Op. 75 No. 3, 1866)
4. `tonal_piano_corpus:4_barcarolle` (*Album de Peterhof*, Op. 75 No. 4, 1866)
5. `tonal_piano_corpus:5_valse-caprice` (*Album de Peterhof*, Op. 75 No. 5, 1866)
6. `tonal_piano_corpus:6_romance` (*Album de Peterhof*, Op. 75 No. 6, 1866)
7. `tonal_piano_corpus:10_mazurka` (*Album de Peterhof*, Op. 75 No. 10, 1866)
8. `tonal_piano_corpus:11_romance` (*Album de Peterhof*, Op. 75 No. 11, 1866)
9. `tonal_piano_corpus:prelude_1` (*6 Préludes*, Op. 24 No. 1 in E major, 1854)
10. `tonal_piano_corpus:prelude_4` (*6 Préludes*, Op. 24 No. 4 in B minor, 1856)
11. `tonal_piano_corpus:prelude_6` (*6 Préludes*, Op. 24 No. 6 in E-flat minor, 1856)

### 4.2 Sergei Prokofiev ($M = 10 \ge 10$)
All 10 works published 1907–1918 (Public Domain worldwide):
1. `tonal_piano_corpus:toccata_op11` (Toccata in D minor, Op. 11, 1912)
2. `tonal_piano_corpus:10_pieces_op12_no2_legend` (10 Pieces, Op. 12 No. 2, 1913)
3. `tonal_piano_corpus:10_pieces_op12_no7_prelude_harp` (10 Pieces, Op. 12 No. 7, 1913)
4. `tonal_piano_corpus:4_pieces_op3_no3_march` (4 Pieces, Op. 3 No. 3, 1907)
5. `tonal_piano_corpus:4_pieces_op2_no4_etude` (4 Pieces, Op. 2 No. 4, 1909)
6. `tonal_piano_corpus:no1` (*Visions Fugitives*, Op. 22 No. 1 *Lentamente*, 1917, pub. 1918)
7. `tonal_piano_corpus:no5` (*Visions Fugitives*, Op. 22 No. 5 *Molto giocoso*, 1917, pub. 1918)
8. `tonal_piano_corpus:no10` (*Visions Fugitives*, Op. 22 No. 10 *Ridicolosamente*, 1917, pub. 1918)
9. `ana_music:prokofiev_op22_no02` (*Visions Fugitives*, Op. 22 No. 2 *Andante*, 1917, pub. 1918)
10. `ana_music:prokofiev_op22_no03` (*Visions Fugitives*, Op. 22 No. 3 *Allegretto*, 1917, pub. 1918)

---

## 5. Master Cryptographic Hash Registry

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 RC-014C.1 Cryptographic Master Hash Registry                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RC014C1_CONFIRMATORY_CORPUS_FREEZE_HASH:                                                                │
│   06173918554380617153cadd4de66443733c33d52dbbe54813a10846b24e6330                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FEATURE_CACHE_MATRIX_SHA256:                                                                            │
│   093d262da6ee7decce2026966be4b251d843c2c5836a2c4359d7609fefd8b28b                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ RC012_FROZEN_PREDICTOR_BUNDLE_HASH:                                                                     │
│   4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ STRUCTURAL_SCHEMA_HASH:                                                                                 │
│   924a19913f831c4f0ffba2dfa88188b88e598af635046b05e580e5b807355282                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ SUPERSEDED_INCOMPLETE_FREEZE_HASH:                                                                      │
│   782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Pre-Unblinding Governance Invariants

1. **Gate Rule**: Live status remains $N_{\text{Russian}} = 2$ (*Alexander Scriabin*, *Modest Mussorgsky*) and `RC012_RESUMPTION_STATUS = BLOCKED` pending human authorization of the external Russian corpus additions.
2. **Immutable Preregistration Contract**: $N_{\text{Russian}} \ge 4$, $N_{\text{Control}} \ge 4$, $M_c \ge 10$ minimum for every counted composer. Alternate 3-composer mode or sample size relaxation is strictly prohibited.
3. **Zero Unblinding**: No predictor evaluations, no classification metrics (AUC, balanced accuracy, permutation p-values), and no Russian-vs-control feature comparisons have been executed on the confirmatory data.

---

## 7. Outcome State

$$\mathbf{RC014C1\_FULL\_CORPUS\_FROZEN\_AWAITING\_HUMAN\_ACCESS\_APPROVAL}$$
