# RC-012A — Comprehensive Confirmatory Corpus Inventory & Source Audit

**Status**: AUDITED & RECORDED  
**Milestone**: RC-012A Confirmatory Corpus Inventory Exhaustion  
**Evaluation Rule**: $N_{\text{Russian}} \ge 4$ and $N_{\text{Control}} \ge 4$ independent composers with $\ge 10$ unique, parseable, original solo-piano symbolic scores.

---

## 1. Audited Repositories & Collections

We conducted an exhaustive audit of all open symbolic music repositories and collections:
1. **KernScores / CCARH Humdrum**: Full crawl of Stanford CCARH collections (`users/craig/classical` across 68 composer directories, `musedata`, `osu`).
2. **PDMX (Public Domain MusicXML)**: Zenodo dataset (`10.5281/zenodo.15571083` / `10.5281/zenodo.13763756`) and GitHub repository (`pnlong/PDMX`).
3. **ATEPP v1.2**: Full metadata and MusicXML score inspection across 11,674 performance records and 25 composers (`tangjjbetsy/ATEPP`).
4. **PERiScoPe v1.1**: Full metadata and raw score inspection across 46,473 performance records (`SyMuPe/PERiScoPe`).
5. **ASAP Dataset v1.2**: Aligned Scores and Performances (`fosfrancesco/asap-dataset`).
6. **DCMLab (EPFL)**: All 65+ repository holdings (`distant_listening_corpus`, `romantic_piano_corpus`, individual repos).
7. **Music21 Built-in Corpus**: Core paths across 3,194 pieces and 35 sub-collections.

---

## 2. Composer-by-Source Eligibility & Feasibility Table

| Composer | Candidate Class | Primary Audited Sources | Raw Matches | Unique Movement / Comp | Original Solo Piano | Parseable Symbolic | License Clean | RC-011 Compatible | Final Eligible Count ($M_c$) | Meets $\ge 10$? | Primary Exclusion / Status Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | Russian | `craigsapp/scriabin` (CCARH) / PERiScoPe / ASAP | 212 | 207 | 207 | 207 | 207 | 207 | **207** | **YES** | **QUALIFIED** (Op. 1–74 in `craigsapp/scriabin`, commit `7daa1136a4edfaf8d2bfadee973c33f3b76b6760`) |
| **Modest Mussorgsky** | Russian | PERiScoPe / ATEPP / KernScores | 18 | 18 | 18 | 18 | 18 | 18 | **18** | **YES** | **QUALIFIED** (*Pictures at an Exhibition* 15 mvmts + 3 standalone) |
| **Sergei Prokofiev** | Russian | ASAP / PERiScoPe / CCARH KernScores | 4 | 3 | 3 | 3 | 3 | 3 | **3** | **NO** | Insufficient pieces ($M_c=3 < 10$: Toccata Op.11, Visions Fugitives Op. 22 Nos. 10 & 16) |
| **Anton Arensky** | Russian | PDMX / Kern / GiantMIDI / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic scores in open corpora (audited in query log) |
| **Mily Balakirev** | Russian | ASAP / PERiScoPe / Kern | 3 | 2 | 2 | 2 | 2 | 2 | **2** | **NO** | Insufficient pieces ($M_c=2 < 10$: *Islamey*, Toccata) |
| **Sergei Lyapunov** | Russian | PERiScoPe / Kern | 1 | 1 | 1 | 1 | 1 | 1 | **1** | **NO** | Insufficient pieces ($M_c=1 < 10$: *Transcendental Étude No. 1 Berceuse*) |
| **Alexander Glazunov** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora (audited in query log) |
| **Anatoly Lyadov** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora (audited in query log) |
| **Anton Rubinstein** | Russian | PERiScoPe / Kern | 1 | 1 | 1 | 1 | 1 | 1 | **1** | **NO** | Insufficient pieces ($M_c=1 < 10$: *Mélodie in F*, Op. 3 No. 1) |
| **Sergei Taneyev** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora (audited in query log) |
| **César Cui** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora (audited in query log) |
| **Edvard Grieg** | Control | `DCMLab/grieg_lyric_pieces` | 66 | 66 | 66 | 66 | 66 | 66 | **66** | **YES** | **QUALIFIED** (*Lyric Pieces*, DCMLab) |
| **Claude Debussy** | Control | DCMLab (7 repos: Suite Bergamasque, Preludes, Etudes, etc.) | 54 | 54 | 54 | 54 | 54 | 54 | **54** | **YES** | **QUALIFIED** (54 pieces across 7 DCMLab repos) |
| **Antonín Dvořák** | Control | `DCMLab/dvorak_silhouettes` | 12 | 12 | 12 | 12 | 12 | 12 | **12** | **YES** | **QUALIFIED** (*Silhouettes* Op. 8, DCMLab) |
| **Béla Bartók** | Control | `DCMLab/bartok_bagatelles` | 14 | 14 | 14 | 14 | 14 | 14 | **14** | **YES** | **QUALIFIED** (14 Bagatelles Op. 6, DCMLab) |
| **Ludwig van Beethoven**| Control | `DCMLab/beethoven_piano_sonatas` | 91 | 91 | 91 | 91 | 91 | 91 | **91** | **YES** | **QUALIFIED** (32 Piano Sonatas, DCMLab) |

---

## 3. Cross-Source Deduplication & Overlap

1. **Alexander Scriabin**:
   - `craigsapp/scriabin` (CCARH): 207 works (complete Op. 1–74).
   - ASAP: 5 works (cross-source duplicates sharing canonical IDs).
   - *Deduplicated Canonical Set*: `craigsapp/scriabin` prioritized as canonical source ($\mathbf{207}$ unique pieces).
2. **Modest Mussorgsky**:
   - PERiScoPe: 18 works (15 movements of *Pictures at an Exhibition* + *Impromptu passionné*, *Memories of Childhood*, *The Seamstress*).
   - *Deduplicated Canonical Set*: PERiScoPe prioritized as canonical source ($\mathbf{18}$ unique pieces).
3. **Sergei Prokofiev**:
   - PERiScoPe: 2 works (Toccata Op. 11, Visions Fugitives Op. 22 No. 10).
   - ASAP: 2 works (Toccata Op. 11 duplicate, Visions Fugitives Op. 22 No. 16).
   - *Deduplicated Canonical Set*: 3 unique works total ($3 < 10$).

---

## 4. Primary Data Gate Recheck

- **Required Thresholds**:
  - $N_{\text{Russian}} \ge 4$ independent composers with $\ge 10$ pieces.
  - $N_{\text{Control}} \ge 4$ independent composers with $\ge 10$ pieces.
- **Audited Qualified Independent Composers**:
  - **Russian Qualified ($N=2$)**:
    1. *Alexander Scriabin* ($M_c=207$)
    2. *Modest Mussorgsky* ($M_c=18$)
  - **Control Qualified ($N=5$)**:
    1. *Antonín Dvořák* ($M_c=12$)
    2. *Béla Bartók* ($M_c=14$)
    3. *Claude Debussy* ($M_c=54$)
    4. *Edvard Grieg* ($M_c=66$)
    5. *Ludwig van Beethoven* ($M_c=91$)
- **Gate Evaluation**:
  - $N_{\text{Control}} = 5 \ge 4$ (**SATISFIED**)
  - $N_{\text{Russian}} = 2 < 4$ (**UNSATISFIED**)

**Final Precondition Evaluation**:
$$\mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$

### Formal Meaning of Contract Outcome
This failure means:
> "Independent external confirmation could not be executed because the pre-registered minimum number of eligible new Russian composers ($\ge 4$) was unavailable in open symbolic corpora."

It does **NOT** mean:
> "The Russian structural signal was absent or that the classifier failed."

No confirmatory feature extraction, prediction, AUC calculation, or unblinding occurred.

---

## 5. Cryptographic Hash Traceability & Supersession Ledger

| Artifact / Entity | RC-012B Superseded Hash | RC-012C Canonical Hash | Status |
| :--- | :--- | :--- | :--- |
| `data/manifests/rc012_source_inventory.csv` | `40672c4fd54c3440e6c29db2e0c6f4aa5ffdb7dd7d88e020ff5eccaf015a9a12` | `4813102a193c38fc61ef4815a25895243c819b2527803f82e7020ac766627eb7` | **SUPERSEDED (RC-012C Real Evidence)** |
| `data/manifests/rc012_source_query_log.csv` | N/A | `7bfbcd4af8c0651d4b5b65190be4c65ff86645655b4ebdcfa0b343d08388f5de` | **CANONICAL** |
| `docs/research/RC012_SOURCE_POLICY.md` | `f9f4fe75dad8eea1de7ae3acd5d80818d1ec24d16999a525bfb0eacc7ba718fc` | `cc80e267c094cb2bbff04dc2d82bf6df8639113ad41d9bb4587a5e970b0cd24e` | **SUPERSEDED (RC-012C Policy Update)** |
| `data_gate_result_hash` | `a5e64cd3e0260250687d64f32915fd0fea8b84830a8c5bb2d1a3651a5cf4337b` | `5966e1386400a977e0412534e83df6b30667a544e5a431b8b05357dcdb409b7b` | **SUPERSEDED (RC-012C Dynamic Derivation)** |
| `RC012_FROZEN_PREDICTOR_BUNDLE_HASH` | `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926` | `4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926` | **FROZEN & UNCHANGED** |
