# RC-012 Confirmatory Corpus Inventory & Source Feasibility Assessment

**Status**: EVALUATED & RECORDED  
**Milestone**: RC-012 Independent External Composer Confirmation  
**Predeclared Contract Standard**: $\ge 4$ Russian and $\ge 4$ Control independent composers with $\ge 10$ eligible symbolic solo piano pieces each.

---

## 1. Executive Summary & Protocol Findings

Per the strict scientific contract governing RC-012:
1. **Confirmatory Composer Eligibility Criteria**:
   - Independent composers who played zero role in feature development or exploratory milestones (excludes development composers: *Nikolai Medtner*, *Sergei Rachmaninoff*, *Pyotr Ilyich Tchaikovsky*, *Frédéric Chopin*, *Franz Liszt*, *Robert Schumann*).
   - Minimum sample size threshold: $\ge 4$ independent Russian late-Romantic / early-modern composers AND $\ge 4$ independent Control composers.
   - Minimum piece threshold per composer: $\ge 10$ eligible pieces.
   - Symbolic notation requirements: High-fidelity, machine-readable symbolic scores with explicit pitch and metric/temporal definitions.
   - Scientific Integrity Rule: If fewer than 4 composers per class satisfy the predeclared data contract, declare `CONFIRMATORY_DATA_CONTRACT_FAILED` ex ante and stop without post-hoc data fabrication or relaxation of standards.

2. **Empirical Survey of Available Open Repositories**:
   - **Control Candidates**: Abundantly satisfied across academic corpora:
     - *Edvard Grieg*: 66 pieces (`DCMLab/grieg_lyric_pieces`, commit `91a304563521f3f273b8c0aadec1ce2ede2d1384`).
     - *Claude Debussy*: 53 pieces (`DCMLab/debussy_suite_bergamasque`, `DCMLab/debussy_preludes`, `DCMLab/debussy_etudes`).
     - *Antonín Dvořák*: 12 pieces (`DCMLab/dvorak_silhouettes`, commit `f228006fcd8696c809cfc8e701ed215cec3d07f1`).
     - *Béla Bartók*: 14 pieces (`DCMLab/bartok_bagatelles`, commit `c6221f6ecb4dbcd476e827f6bf8705bdcb15c8a9`).
     - *Ludwig van Beethoven*: 91 movements (`DCMLab/beethoven_piano_sonatas`, commit `ea7181bff88abc8713257234f7ec4033178c57a9`).
   - **Russian Candidates**:
     - *Alexander Scriabin*: Fully satisfied. Complete solo piano works Op. 1 to Op. 74 (207 pieces in CCARH Humdrum `**kern`, `craigsapp/scriabin` commit `7daa1136a4edfaf8d2bfadee973c33f3b76b6760` / `bel28kent/Mysterium` commit `fae8fa60a37e1f889be9c2e58fcdaade981198c1`).
     - *Anton Arensky*, *Mily Balakirev*, *Sergei Lyapunov*, *Aleksandr Glazunov*, *César Cui*, *Modest Mussorgsky*, *Sergei Prokofiev*:
       - Exhaustive survey of open repositories (DCMLab, kernScores, ASAP dataset, music21 corpus) revealed only isolated single pieces or small fragments (e.g. Mussorgsky: 1 movement Promenade; Prokofiev: 3 Visions Fugitives; ASAP: 1 Balakirev, 1 Glinka, 1 Prokofiev).
       - No curated, academically verified open collections with $\ge 10$ symbolic solo piano pieces exist for any other independent Russian composer.

3. **Definitive Contract Evaluation**:
   - Verified Russian independent composers meeting the $\ge 10$ pieces threshold: **$N_{\text{Russian}} = 1$** (*Alexander Scriabin*).
   - Required minimum threshold: **$N_{\text{Russian}} \ge 4$**.
   - Result: The physical external corpus landscape cannot satisfy the minimum $4+4$ composer-level sample size without post-hoc relaxation of sample thresholds or non-verifiable data collection.
   - In accordance with the preregistration rules:
     $$\text{Status} = \mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$

---

## 2. Exhaustive Source Verification Table

| Composer | Tradition | Repository / Source | Format | Piece Count | $\ge 10$ Pieces? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | Russian | `craigsapp/scriabin` / `bel28kent/Mysterium` | `**kern` | 207 | **YES** | **ELIGIBLE** |
| **Anton Arensky** | Russian | GiantMIDI (MIDI only), no symbolic corpus | MIDI/None | 0 | NO | INELIGIBLE |
| **Mily Balakirev** | Russian | ASAP dataset (1 score) | MusicXML | 1 | NO | INELIGIBLE |
| **Sergei Lyapunov** | Russian | KernScores (unindexed/isolated) | `**kern` | 0 | NO | INELIGIBLE |
| **Aleksandr Glazunov** | Russian | KernScores (unindexed/isolated) | `**kern` | 0 | NO | INELIGIBLE |
| **César Cui** | Russian | None | None | 0 | NO | INELIGIBLE |
| **Modest Mussorgsky** | Russian | CCARH KernScores | `**kern` | 1 | NO | INELIGIBLE |
| **Sergei Prokofiev** | Russian | CCARH KernScores / ASAP | `**kern`/MusicXML| 3 | NO | INELIGIBLE |
| **Edvard Grieg** | Control | `DCMLab/grieg_lyric_pieces` | MuseScore | 66 | **YES** | **ELIGIBLE** |
| **Claude Debussy** | Control | `DCMLab/debussy_suite_bergamasque` + `preludes` | MuseScore | 53 | **YES** | **ELIGIBLE** |
| **Antonín Dvořák** | Control | `DCMLab/dvorak_silhouettes` | MuseScore | 12 | **YES** | **ELIGIBLE** |
| **Béla Bartók** | Control | `DCMLab/bartok_bagatelles` | MuseScore | 14 | **YES** | **ELIGIBLE** |
| **Ludwig van Beethoven** | Control | `DCMLab/beethoven_piano_sonatas` | MuseScore | 91 | **YES** | **ELIGIBLE** |

---

## 3. Scientific Integrity & Governance Ledger

- **Zero Post-Hoc Tuning**: We refuse to lower the composer threshold to $N=1$ or split single composers into pseudo-independent units, as that would violate the preregistered inferential unit (Composer) and cause severe pseudoreplication.
- **Fail-Closed Principle**: Rather than manufacturing or scraping unverified data, the scientific integrity protocol requires registering the exact state of external evidence and declaring `CONFIRMATORY_DATA_CONTRACT_FAILED`.
- **Significance for Russian Piano Composer**: This finding formally documents that public symbolic music corpora suffer from an acute geographic and stylistic representation bias: Western classical and German/French romantic piano repertoires are heavily digitized and annotated (Beethoven, Chopin, Schumann, Liszt, Debussy, Grieg), whereas the broader Russian late-Romantic school outside of Tchaikovsky, Rachmaninoff, Medtner, and Scriabin remains largely unencoded in open symbolic formats.
