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
   - **Control Candidates**: Abundantly satisfied across academic corpora ($N_{\text{Control}} = 5 \ge 4$):
     - *Edvard Grieg*: 66 pieces (`DCMLab/grieg_lyric_pieces`, commit `91a304563521f3f273b8c0aadec1ce2ede2d1384`).
     - *Claude Debussy*: 54 pieces across 7 DCMLab repositories (Suite Bergamasque, Preludes, Études, Pour le piano, Estampes, Deux Arabesques, Children's Corner).
     - *Antonín Dvořák*: 12 pieces (`DCMLab/dvorak_silhouettes`, commit `f228006fcd8696c809cfc8e701ed215cec3d07f1`).
     - *Béla Bartók*: 14 pieces (`DCMLab/bartok_bagatelles`, commit `8209355be326f582ae446e1e813a8f1ffb853e5e`).
     - *Ludwig van Beethoven*: 91 movements (`DCMLab/beethoven_piano_sonatas`, commit `ea7181bff88abc8713257234f7ec4033178c57a9`).
   - **Russian Candidates**: Only 2 composers satisfied all eligibility criteria ($N_{\text{Russian}} = 2 < 4$):
     - *Alexander Scriabin*: Fully satisfied. Complete solo piano works Op. 1 to Op. 74 (207 pieces in CCARH Humdrum `**kern`, `craigsapp/scriabin`, commit `7daa1136a4edfaf8d2bfadee973c33f3b76b6760`).
     - *Modest Mussorgsky*: Satisfied with 18 pieces (PERiScoPe / ATEPP / KernScores: 15 movements of *Pictures at an Exhibition* + 3 standalone pieces: *Impromptu passionné*, *Memories of Childhood*, *The Seamstress*).
     - *Sergei Prokofiev*, *Mily Balakirev*, *Sergei Lyapunov*, *Anton Rubinstein*, *Anton Arensky*, *Aleksandr Glazunov*, *Anatoly Lyadov*, *Sergei Taneyev*, *César Cui*:
       - Exhaustive survey of open repositories (DCMLab, kernScores, ASAP, ATEPP, PERiScoPe, music21, PianoCoRe) revealed only isolated single pieces or small fragments below the 10-piece threshold (*Prokofiev* $M_c=4$, *Balakirev* $M_c=2$, *Lyapunov* $M_c=1$, *Rubinstein* $M_c=1$; others $M_c=0$).
       - PianoCoRe 2026 was audited: while it provides performance/score MIDI, score MIDI files lacking explicit measure, key signature, staff, and voice notation are classified as `SOURCE_INCOMPATIBLE_FOR_RC011`.

3. **Definitive Contract Evaluation**:
   - Verified Russian independent composers meeting the $\ge 10$ pieces threshold: **$N_{\text{Russian}} = 2$** (*Alexander Scriabin*, *Modest Mussorgsky*).
   - Required minimum threshold: **$N_{\text{Russian}} \ge 4$**.
   - Verified Control independent composers meeting the $\ge 10$ pieces threshold: **$N_{\text{Control}} = 5 \ge 4$**.
   - Result: The physical external corpus landscape cannot satisfy the minimum $4+4$ composer-level sample size ($N_{\text{Russian}} = 2 < 4$).
   - In accordance with the preregistration rules:
     $$\text{Status} = \mathbf{CONFIRMATORY\_DATA\_CONTRACT\_FAILED}$$
   - Primary external hypothesis is **NOT TESTED**. This is strictly a **DATA AVAILABILITY FAILURE**, not a negative finding about musical style or the presence/absence of structural signal.

---

## 2. Exhaustive Source Verification Table

| Composer | Tradition | Repository / Source | Format | Piece Count ($M_c$) | $\ge 10$ Pieces? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | Russian | `craigsapp/scriabin` / ASAP / PERiScoPe | `**kern`/MusicXML | 207 | **YES** | **ELIGIBLE** |
| **Modest Mussorgsky** | Russian | PERiScoPe / ATEPP / CCARH KernScores | MusicXML/`**kern` | 18 | **YES** | **ELIGIBLE** |
| **Sergei Prokofiev** | Russian | ASAP / PERiScoPe / CCARH KernScores | `**kern`/MusicXML | 4 | NO | INELIGIBLE ($M_c < 10$) |
| **Mily Balakirev** | Russian | ASAP dataset / PERiScoPe | MusicXML | 2 | NO | INELIGIBLE ($M_c < 10$) |
| **Sergei Lyapunov** | Russian | PERiScoPe | MusicXML | 1 | NO | INELIGIBLE ($M_c < 10$) |
| **Anton Rubinstein** | Russian | PERiScoPe | MusicXML | 1 | NO | INELIGIBLE ($M_c < 10$) |
| **Anton Arensky** | Russian | GiantMIDI (MIDI only), no symbolic corpus | MIDI/None | 0 | NO | INELIGIBLE ($M_c=0$) |
| **Aleksandr Glazunov** | Russian | KernScores / PDMX / ATEPP | None | 0 | NO | INELIGIBLE ($M_c=0$) |
| **Anatoly Lyadov** | Russian | KernScores / PDMX / ATEPP | None | 0 | NO | INELIGIBLE ($M_c=0$) |
| **Sergei Taneyev** | Russian | KernScores / PDMX / ATEPP | None | 0 | NO | INELIGIBLE ($M_c=0$) |
| **César Cui** | Russian | KernScores / PDMX / ATEPP | None | 0 | NO | INELIGIBLE ($M_c=0$) |
| **Edvard Grieg** | Control | `DCMLab/grieg_lyric_pieces` | MuseScore | 66 | **YES** | **ELIGIBLE** |
| **Claude Debussy** | Control | DCMLab (7 repos) | MuseScore | 54 | **YES** | **ELIGIBLE** |
| **Antonín Dvořák** | Control | `DCMLab/dvorak_silhouettes` | MuseScore | 12 | **YES** | **ELIGIBLE** |
| **Béla Bartók** | Control | `DCMLab/bartok_bagatelles` | MuseScore | 14 | **YES** | **ELIGIBLE** |
| **Ludwig van Beethoven** | Control | `DCMLab/beethoven_piano_sonatas` | MuseScore | 91 | **YES** | **ELIGIBLE** |

---

## 3. Scientific Integrity & Governance Ledger

- **Zero Post-Hoc Tuning**: We refuse to lower the composer threshold to $N_{\text{Russian}}=2$ or split single composers into pseudo-independent units, as that would violate the preregistered inferential unit (Composer) and cause pseudoreplication.
- **Fail-Closed Principle**: Rather than manufacturing or scraping unverified data, the scientific integrity protocol requires registering the exact state of external evidence and declaring `CONFIRMATORY_DATA_CONTRACT_FAILED` due to data availability failure.
- **Significance for Russian Piano Composer**: This finding formally documents that public symbolic music corpora suffer from an acute geographic and stylistic representation bias: Western classical and German/French romantic piano repertoires are heavily digitized and annotated (Beethoven, Chopin, Schumann, Liszt, Debussy, Grieg), whereas the broader Russian late-Romantic school outside of Tchaikovsky, Rachmaninoff, Medtner, Scriabin, and Mussorgsky remains largely unencoded in open symbolic formats.
- **Preservation of Prior Findings**: RC-010 established `RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED`. RC-011 established `STRUCTURAL_REPRESENTATION_VALIDATED` for structural metric calculation across canonical development pieces. RC-011 is not validated for Russian stylistic guidance or classification.
