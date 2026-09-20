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

| Composer | Candidate Class | Primary Audited Sources | Raw Matches | Unique Movement / Comp | Original Solo Piano | Parseable Symbolic | License Clean | RC-011 Compatible | Final Eligible Count | Meets $\ge 10$? | Primary Exclusion / Status Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | Russian | CCARH Kern / PERiScoPe / ATEPP | 235 | 207 | 207 | 207 | 207 | 207 | **207** | **YES** | **QUALIFIED** (Op. 1–74 in KernScores / PERiScoPe) |
| **Modest Mussorgsky** | Russian | PERiScoPe / ATEPP / KernScores | 1,301 | 18 | 18 | 18 | 18 | 18 | **18** | **YES** | **QUALIFIED** (*Pictures at an Exhibition* 15 mvmts + 3 standalone) |
| **Sergei Prokofiev** | Russian | ATEPP / ASAP / PERiScoPe / Kern | 268 | 4 | 4 | 4 | 4 | 4 | **4** | **NO** | Insufficient pieces ($N=4 < 10$: Toccata Op.11, Visions Fugitives 3 mvmts) |
| **Anton Arensky** | Russian | PDMX / Kern / GiantMIDI / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic scores in open corpora (MIDI only in GiantMIDI) |
| **Mily Balakirev** | Russian | ASAP / PERiScoPe / Kern | 27 | 2 | 2 | 2 | 2 | 2 | **2** | **NO** | Insufficient pieces ($N=2 < 10$: *Islamey*, Toccata) |
| **Sergei Lyapunov** | Russian | PERiScoPe / Kern | 2 | 1 | 1 | 1 | 1 | 1 | **1** | **NO** | Insufficient pieces ($N=1 < 10$: *Transcendental Étude No. 1 Berceuse*) |
| **Alexander Glazunov** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora |
| **Anatoly Lyadov** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora |
| **Anton Rubinstein** | Russian | PERiScoPe / Kern | 2 | 1 | 1 | 1 | 1 | 1 | **1** | **NO** | Insufficient pieces ($N=1 < 10$: *Mélodie in F*, Op. 3 No. 1) |
| **Sergei Taneyev** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora |
| **César Cui** | Russian | Kern / PDMX / ATEPP | 0 | 0 | 0 | 0 | 0 | 0 | **0** | **NO** | Zero symbolic solo-piano scores in open corpora |
| **Edvard Grieg** | Control | DCMLab / PERiScoPe / ATEPP | 152 | 66 | 66 | 66 | 66 | 66 | **66** | **YES** | **QUALIFIED** (*Lyric Pieces*, DCMLab) |
| **Claude Debussy** | Control | DCMLab / PERiScoPe / ATEPP | 437 | 53 | 53 | 53 | 53 | 53 | **53** | **YES** | **QUALIFIED** (Suite Bergamasque, Preludes, Études) |
| **Antonín Dvořák** | Control | DCMLab / PERiScoPe | 20 | 12 | 12 | 12 | 12 | 12 | **12** | **YES** | **QUALIFIED** (*Silhouettes* Op. 8, DCMLab) |
| **Béla Bartók** | Control | DCMLab / PERiScoPe | 81 | 40 | 40 | 40 | 40 | 40 | **40** | **YES** | **QUALIFIED** (*Bagatelles*, etc., DCMLab/PERiScoPe) |
| **Ludwig van Beethoven**| Control | DCMLab / PERiScoPe / ATEPP | 3,730 | 91 | 91 | 91 | 91 | 91 | **91** | **YES** | **QUALIFIED** (32 Piano Sonatas, DCMLab) |

---

## 3. Cross-Source Deduplication & Overlap

1. **Alexander Scriabin**:
   - CCARH KernScores: 207 works (complete Op. 1–74).
   - PERiScoPe: 25 works (subsets of Op. 2, 8, 11, 16, 28, 42, 45, 53).
   - ATEPP: 3 works (Op. 8 No. 11, Op. 28, Op. 53).
   - *Deduplicated Canonical Set*: CCARH KernScores prioritized as canonical source ($\mathbf{207}$ unique pieces).
2. **Modest Mussorgsky**:
   - PERiScoPe: 18 works (15 movements of *Pictures at an Exhibition* + *Impromptu passionné*, *Memories of Childhood*, *The Seamstress*).
   - KernScores: 1 movement (*Promenade* from *Pictures at an Exhibition*).
   - *Deduplicated Canonical Set*: PERiScoPe prioritized as canonical source ($\mathbf{18}$ unique pieces).
3. **Sergei Prokofiev**:
   - PERiScoPe: 2 works (Toccata Op. 11, Visions Fugitives Op. 22 No. 10).
   - CCARH KernScores: 3 works (Visions Fugitives Op. 22 Nos. 1, 10, 16).
   - ASAP: 1 work (Toccata Op. 11).
   - *Deduplicated Canonical Set*: 4 unique works total ($4 < 10$).

---

## 4. Primary Data Gate Recheck

- **Required Thresholds**:
  - $N_{\text{Russian}} \ge 4$ independent composers with $\ge 10$ pieces.
  - $N_{\text{Control}} \ge 4$ independent composers with $\ge 10$ pieces.
- **Audited Qualified Independent Composers**:
  - **Russian Qualified ($N=2$)**:
    1. *Alexander Scriabin* ($M=207$)
    2. *Modest Mussorgsky* ($M=18$)
  - **Control Qualified ($N=5$)**:
    1. *Edvard Grieg* ($M=66$)
    2. *Claude Debussy* ($M=53$)
    3. *Antonín Dvořák* ($M=12$)
    4. *Béla Bartók* ($M=40$)
    5. *Ludwig van Beethoven* ($M=91$)
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
