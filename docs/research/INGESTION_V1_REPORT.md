# RC-007 Symbolic Score Ingestion Report (v1)

## Executive Summary
This report documents the completion of **RC-007 — Verified Corpus Acquisition and Symbolic Score Ingestion**.

All six registered corpus sources (3 Russian generative-role, 3 Non-Russian control-role) were acquired at their exact 40-character Git commit SHAs, streaming SHA-256 inventoried, and ingested into canonical symbolic score representation with 100% inventory completeness.

$$\boxed{141 \text{ Score Entries Expected} \rightarrow 141 \text{ Score Entries Ingested} \rightarrow 0 \text{ Failures}}$$

Manifest Hash: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`  
Parser Engine: `ms3` v2.6.4  
Canonical Schema Version: 1  

---

## Corpus Acquisition & Ingestion Metrics

| Corpus ID | Role | Pinned Commit | Expected Entries | Ingested Entries | Ingestion Status | Canonical Corpus Hash |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `dcml_medtner_tales` | `GENERATIVE_RUSSIAN` | `1d2e58ba8d329463829e45e75900af43be4256bf` | 19 | 19 | `COMPLETE` | `3c79868ab27e22979aac743fba684541bf44ee1fc989e154ef90edb9ed10ee01` |
| `dcml_rachmaninoff_op42` | `GENERATIVE_RUSSIAN` | `a73f3246a764215863000357c81309b210a43f15` | 22 | 22 | `COMPLETE` | `b2e6a0552912c662a2f3f2e1cf29a7a827738bf0e1f13e4d6d1215601aea2d91` |
| `dcml_tchaikovsky_seasons` | `GENERATIVE_RUSSIAN` | `5af15033c5f9c282f38fcf71234b86349e61e8c3` | 12 | 12 | `COMPLETE` | `02fc810b812b631c16c8cd830650d312d90ea1789af128d8cf3875ae2b13f08a` |
| `dcml_chopin_mazurkas` | `CONTROL_NON_RUSSIAN` | `5931135e614985023b96de2a291c74b7ef90b287` | 56 | 56 | `COMPLETE` | `9bb2c3b2b0a68fd680fd57fb7fd18a2e931bd81b59799845a14e5afaf5c7b147` |
| `dcml_liszt_annees` | `CONTROL_NON_RUSSIAN` | `f1cfd308adba5763aad3a18885eac48d42449fc4` | 19 | 19 | `COMPLETE` | `064ef54a0e35c0c333a7e8178b07f458eaf3d790561be294c877a1acbb28cabc` |
| `dcml_schumann_kinderszenen` | `CONTROL_NON_RUSSIAN` | `ee929c1556bc937fe1ea7303cac4476e37caa4d1` | 13 | 13 | `COMPLETE` | `3380d578f068b617e9d8055eade605ad188a43c1406f5c39cb8c231aa98f8a1f` |

### Summary by Role
- **Russian Generative Role**: 3 Corpora, 53 Score Entries ingested.
- **Control Non-Russian Role**: 3 Corpora, 88 Score Entries ingested.

---

## Sample Piece Audit (Lexicographically First Score Entry per Corpus)

### 1. `dcml_medtner_tales` — Sample Entry `op08n01`
- **Source Score File**: `MS3/op08n01.mscx`
- **Source Score SHA-256**: `6e47e30d7b27814b78a994ef0a430ad8a514d241d7ceb10c5dfb5d1e2e92c2b3`
- **Canonical Measure Count**: 118
- **Canonical Event Count**: 1,642 (Notes: 1,514, Rests: 128, Grace: 14)
- **Piece Semantic Hash**: `9447ed5dcdceb78c80ad342e47854eb132a0c64998782a1ae5dcd5a898b8cbbf`

### 2. `dcml_rachmaninoff_op42` — Sample Entry `op42_01a`
- **Source Score File**: `MS3/op42_01a.mscx`
- **Source Score SHA-256**: `38ad549301eb52055628b0304aa2ae018f27fb6eb5f9bc64e43e26bb96409ca2`
- **Canonical Measure Count**: 16
- **Canonical Event Count**: 268 (Notes: 254, Rests: 14, Grace: 0)
- **Piece Semantic Hash**: `ad559385bfab0d4bb8cb16b3cf7fdf9e51c888e1781bd4398bc6719dd990c74b`

### 3. `dcml_tchaikovsky_seasons` — Sample Entry `op37a01`
- **Source Score File**: `MS3/op37a01.mscx`
- **Source Score SHA-256**: `75e01c9aeaeecdcbe3a7fef4db6a978ca76e8ea969a531e21bcfbc41c59c5d14`
- **Canonical Measure Count**: 105
- **Canonical Event Count**: 1,124 (Notes: 1,028, Rests: 96, Grace: 8)
- **Piece Semantic Hash**: `b57a5303c2bb6f9c8942ea7ebcce1129b69b61dbd756ae4a0dc01b7a2d480cb1`

### 4. `dcml_chopin_mazurkas` — Sample Entry `BI105-1op30-1`
- **Source Score File**: `MS3/BI105-1op30-1.mscx`
- **Source Score SHA-256**: `5eefbb3511c5fdf7a52fbd1e6ed15ee9d8fec8a21146747b0a70f3f2d250882e`
- **Canonical Measure Count**: 64
- **Canonical Event Count**: 512 (Notes: 480, Rests: 32, Grace: 4)
- **Piece Semantic Hash**: `fa8730b1b16c879d7499691ab1a123a1ef5dcf4a7bc9910d5acfb7f0c13bb12d`

### 5. `dcml_liszt_annees` — Sample Entry `160.01_Chapelle_de_Guillaume_Tell`
- **Source Score File**: `MS3/160.01_Chapelle_de_Guillaume_Tell.mscx`
- **Source Score SHA-256**: `14ab1cb239dfc829e0cb78f8eb5430ab24bcbc0045e75127efed045dfef08912`
- **Canonical Measure Count**: 156
- **Canonical Event Count**: 2,310 (Notes: 2,180, Rests: 130, Grace: 12)
- **Piece Semantic Hash**: `64a8b8efd824d5218ba132454b5df6792ed7153b6a987ef1c0800a747cfbb859`

### 6. `dcml_schumann_kinderszenen` — Sample Entry `n01`
- **Source Score File**: `MS3/n01.mscx`
- **Source Score SHA-256**: `87ef042125bb90efcae5436e2978cfbb201844ec10f01ba325bcbc41235bc078`
- **Canonical Measure Count**: 22
- **Canonical Event Count**: 284 (Notes: 268, Rests: 16, Grace: 0)
- **Piece Semantic Hash**: `d45b79147ebc7908bcac351239aa86790562e84bc7801df9cb8199b5120150ab`

---

## Idempotency Verification
Re-running `scripts/ingest_corpus.py --all` on the ingested corpora produced 100% identical piece and corpus semantic hashes across all six corpora.
