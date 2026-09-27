# RC-014C.2 Source Authority Completion Report

## 1. Overview & Forensic Resolution

This document records the final source authority status across all 483 pieces and 9 composers comprising the full confirmatory corpus under **RC-014C.2**.

In RC-014C.1, while 21 newly acquired pieces (Anton Rubinstein + Sergei Prokofiev) had complete cryptographic source hashes, the remaining 462 baseline pieces retained `"None"` or missing source hashes in the manifest. Under RC-014C.2, every single score entry across all 483 pieces is bound to its immutable Git blob SHA, canonical source file SHA-256 byte checksum, canonical score semantic hash, and derived feature bundle hash.

---

## 2. Source Repositories & Ingestion Adapters

| Composer | Pieces | Upstream Repository / Dataset | Pinned Commit / Version | Ingestion Parser Adapter |
| :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | 207 | `craigsapp/scriabin` | `7daa1136a4edfaf8d2bfadee973c33f3b76b6760` | `parse_humdrum_to_canonical` (music21 **kern) |
| **Modest Mussorgsky** | 18 | `SyMuPe/PERiScoPe` | `v1.1` (Hugging Face archive) | `parse_m21_mxl_to_canonical` (music21 MXL) |
| **Anton Rubinstein** | 11 | `hectorbellmann-art/Tonal-Piano-Corpus` | `3f5a08e9b2360c11aea5d6d384eb84e7845b793c` | `parse_xml_to_canonical` (ElementTree/xml) |
| **Sergei Prokofiev** | 10 | 8 TPC + 2 `automata/ana-music` | `3f5a08e9...` / `335cbdc6...` | `parse_xml_to_canonical` / `parse_humdrum_to_canonical` |
| **Edvard Grieg** | 66 | `DCMLab/grieg_lyric_pieces` | `91a304563521f3f273b8c0aadec1ce2ede2d1384` | `ingest_score_entry_from_ms3` (ms3) |
| **Claude Debussy** | 54 | 7 DCMLab repositories | Various pinned commits | `ingest_score_entry_from_ms3` (ms3) |
| **Ludwig van Beethoven** | 91 | `DCMLab/beethoven_piano_sonatas` | `ea7181bff88abc8713257234f7ec4033178c57a9` | `ingest_score_entry_from_ms3` (ms3) |
| **Béla Bartók** | 14 | `DCMLab/bartok_bagatelles` | `c6221f6ecb4dbcd476e827f6bf8705bdcb15c8a9` | `ingest_score_entry_from_ms3` (ms3) |
| **Antonín Dvořák** | 12 | `DCMLab/dvorak_silhouettes` | `f228006fcd8696c809cfc8e701ed215cec3d07f1` | `ingest_score_entry_from_ms3` (ms3) |

---

## 3. Cryptographic Binding Verification Summary

- **Total Confirmatory Works**: 483
- **Works with Git Blob SHA Bound**: 483 / 483 (100%)
- **Works with Canonical Source File SHA-256 Bound**: 483 / 483 (100%)
- **Works with Canonical Score Semantic Hash Bound**: 483 / 483 (100%)
- **Works with Derived Feature Bundle Hash Bound**: 483 / 483 (100%)
- **Missing / Placeholder Hashes**: 0

---

## 4. Governance Contract & Invalidation Rules

- **Strict Invalidation Trigger**: Any modification to upstream score bytes, parser versions, or feature extractor routines alters `RC014C2_CONFIRMATORY_CORPUS_FREEZE_HASH` and `FEATURE_CACHE_MATRIX_SHA256`, automatically invalidating downstream confirmatory statistics.
- **Fail-Closed Gate**: Live $N_{\text{Russian}}$ remains strictly 2 and RC-012 execution remains `BLOCKED` until explicit human governance authorization is provided.
