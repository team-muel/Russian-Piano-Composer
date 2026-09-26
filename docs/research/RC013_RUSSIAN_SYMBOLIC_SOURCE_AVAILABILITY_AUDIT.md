# RC-013 Russian Symbolic Source Feasibility & Availability Audit

**Status**: COMPREHENSIVELY AUDITED  
**Milestone**: RC-013 Confirmatory Corpus Acquisition  
**Execution Date**: 2026-09-26  
**Objective**: Audit the public symbolic-source landscape for candidate Russian external composers to determine feasibility of satisfying the frozen RC-012 confirmatory contract ($N_{\text{Russian}} \ge 4$, $M_c \ge 10$ each).

---

## 1. Audited Repositories & Corpus Classes

In accordance with the source tier hierarchy:
- **Tier 1 (Scholarly/Open Symbolic Corpora)**: MusicXML, MuseScore source files, Humdrum `**kern`, MEI.
- **Tier 2 (Independent Engravings with Provenance)**: Mutopia, OpenScore, CCARH, IMSLP symbolic contributions.
- **Tier 3 (Performance/Score MIDI)**: PianoCoRe, GiantMIDI, ASAP MIDI (used strictly for secondary corroboration, not satisfying RC-011 score notation alone).

### Surveyed Repositories:
1. **DCMLab (EPFL)**: 65+ repositories (Beethoven, Chopin, Schumann, Grieg, Dvořák, Bartók, Liszt, Debussy, Mozart). Zero Russian late-Romantic solo piano holdings outside Medtner/Tchaikovsky/Rachmaninoff.
2. **CCARH / KernScores (Stanford)**: Craig Sapp Scriabin corpus (`craigsapp/scriabin`, 207 works complete), Mussorgsky fragments, Prokofiev fragments.
3. **PERiScoPe v1.1 & ATEPP v1.2**: Comprehensive performance-aligned score datasets.
4. **PDMX (Zenodo / GitHub)**: Public Domain MusicXML dataset.
5. **ASAP Dataset v1.2**: Aligned Scores and Performances.
6. **Mutopia Project / OpenScore**: Open domain transcriptions.
7. **Music21 Built-in Corpus**: 35 composer sub-collections.

---

## 2. Piece-Level Qualification & Availability Table

| Candidate Russian Composer | Target Repertoire / Work | Repository / Source | Symbolic Format | Source Historical Authority | Deduplicated Pieces Available | Eligible Under RC-011? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexander Scriabin** | Complete Piano Works Op. 1–74 | `craigsapp/scriabin` / CCARH | `**kern` / MusicXML | Belaieff / Jurgenson / Muzyka | **207** | **YES** ($M_c \ge 10$) |
| **Modest Mussorgsky** | *Pictures at an Exhibition* (15) + 3 Standalone | PERiScoPe / ATEPP / KernScores | MusicXML | Bessel / Breitkopf & Härtel | **18** | **YES** ($M_c \ge 10$) |
| **Anton Arensky** | *24 Morceaux pour piano*, Op. 36 | RC-013 Pilot + IMSLP59514 | MusicXML / MSCX | P. Jurgenson (1894) | **3** (Nos. 1, 2, 13) | **NO** ($M_c = 3 < 10$) |
| **Anatoly Lyadov** | Preludes Op. 40, Op. 46, Op. 2 | RC-013 Pilot + Belaieff | MusicXML / MSCX | M.P. Belaieff (1897) | **3** (Op. 40/2, 40/3, 46/4) | **NO** ($M_c = 3 < 10$) |
| **Sergei Lyapunov** | *12 Études d'exécution transcendante*, Op. 11 | RC-013 Pilot + PERiScoPe | MusicXML / MSCX | J.H. Zimmermann (1900) | **3** (Op. 11 Nos. 1, 2, 3) | **NO** ($M_c = 3 < 10$) |
| **Sergei Prokofiev** | *Visions Fugitives* Op. 22 / Toccata Op. 11 / Sonatas | ASAP / PERiScoPe / Kern | MusicXML / `**kern` | Gutheil / Breitkopf | **4** | **NO** ($M_c = 4 < 10$) |
| **Mily Balakirev** | *Islamey*, Toccata in C-sharp minor | ASAP / PERiScoPe | MusicXML | Jurgenson / Gutheil | **2** | **NO** ($M_c = 2 < 10$) |
| **Anton Rubinstein** | *Soirées à Saint-Pétersbourg* Op. 44 / Melodie Op. 3 | PERiScoPe | MusicXML | Bote & Bock / Senff | **1** | **NO** ($M_c = 1 < 10$) |
| **Aleksandr Glazunov** | Preludes and Fugues Op. 62 / Theme and Variations Op. 72 | IMSLP / Open Corpora | None (PDF Scans only) | M.P. Belaieff | **0** | **NO** ($M_c = 0$) |
| **Sergei Taneyev** | Prelude and Fugue in G-sharp minor Op. 29 | IMSLP / Open Corpora | None (PDF Scans only) | P. Jurgenson | **0** | **NO** ($M_c = 0$) |
| **César Cui** | *25 Préludes*, Op. 64 | IMSLP / Open Corpora | None (PDF Scans only) | P. Jurgenson | **0** | **NO** ($M_c = 0$) |

---

## 3. Composer-Level Feasibility Table

| Composer | Raw Symbolic Count | Deduplicated Symbolic Count | Contract-Compatible Pieces ($M_c$) | Meets $M_c \ge 10$? | Remaining Gap to 10 | Feasible Path via RC-014? |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Alexander Scriabin** | 212 | 207 | **207** | **YES** | 0 | Already Qualified |
| **Modest Mussorgsky** | 18 | 18 | **18** | **YES** | 0 | Already Qualified |
| **Anton Arensky** | 3 | 3 | **3** | **NO** | 7 | **FEASIBLE** (Op. 36 contains 24 total morceaux in Jurgenson 1894 first edition) |
| **Anatoly Lyadov** | 3 | 3 | **3** | **NO** | 7 | **FEASIBLE** (Belaieff first editions contain Op. 40, Op. 46, Op. 2, Op. 32) |
| **Sergei Lyapunov** | 4 | 3 | **3** | **NO** | 7 | **FEASIBLE** (Op. 11 contains 12 complete transcendental études in Zimmermann 1900) |
| **Sergei Prokofiev** | 6 | 4 | **4** | **NO** | 6 | **FEASIBLE** (*Visions Fugitives* Op. 22 contains 20 complete miniatures) |
| **Mily Balakirev** | 3 | 2 | **2** | **NO** | 8 | Difficult (fragmented opus distribution) |
| **Anton Rubinstein** | 1 | 1 | **1** | **NO** | 9 | Difficult |
| **Aleksandr Glazunov** | 0 | 0 | **0** | **NO** | 10 | Difficult |

---

## 4. Independent Symbolic Cross-Check Opportunities

Where multiple independent digital encodings exist for the same piece, dual-source symbolic triangulation can verify source fidelity without manual note-by-note proofreading:

1. **Sergei Prokofiev — *Toccata in D minor*, Op. 11**:
   - Independent Source A: ASAP MusicXML encoding (`asap-dataset/Prokofiev/Op_11`).
   - Independent Source B: PERiScoPe MusicXML encoding (`PERiScoPe/Prokofiev_Toccata`).
   - Status: `INDEPENDENT_SYMBOLIC_CROSSCHECK_AVAILABLE`
2. **Sergei Prokofiev — *Visions Fugitives*, Op. 22 No. 10**:
   - Independent Source A: PERiScoPe MusicXML.
   - Independent Source B: CCARH Humdrum `**kern`.
   - Status: `INDEPENDENT_SYMBOLIC_CROSSCHECK_AVAILABLE`
3. **Modest Mussorgsky — *Pictures at an Exhibition***:
   - Independent Source A: PERiScoPe full suite.
   - Independent Source B: CCARH / KernScores full suite.
   - Status: `INDEPENDENT_SYMBOLIC_CROSSCHECK_AVAILABLE`

---

## 5. Formal Proposal for Milestone RC-014

### Proposal: RC-014 Source-Resolved Russian Corpus Expansion

If external acquisition resources are allocated, RC-014 can resolve the $N_{\text{Russian}} < 4$ gap using a strictly **source-first, human- or dual-source-verified** strategy:

1. **Target Composers (Source-First Selection)**:
   - **Anton Arensky**: Expand Op. 36 from 3 to 10 movements (Nos. 1–10) from Jurgenson 1894 first edition.
   - **Sergei Lyapunov**: Expand Op. 11 from 3 to 10 études (Nos. 1–10) from Zimmermann 1900 first edition.
   - **Anatoly Lyadov**: Expand Op. 40/46/2 from 3 to 10 pieces from Belaieff first editions.
   - **Sergei Prokofiev**: Acquire complete 20 *Visions Fugitives* Op. 22.
2. **Verification Protocol**:
   - Dual-source symbolic cross-checking where available (`INDEPENDENT_SYMBOLIC_CROSSCHECK_AVAILABLE`).
   - Independent musicologist measure-by-measure review for remaining pieces.
   - No uncalibrated machine-vision or OMR self-certification.

### Alternative Formal Closing: Preregistered Data Availability Failure

If RC-014 is not funded or executed:
$$\mathbf{RC012\_EXTERNAL\_CONFIRMATION = CLOSED\_AS\_DATA\_AVAILABILITY\_FAILURE}$$
$$\mathbf{PRIMARY\_EXTERNAL\_HYPOTHESIS = NOT\_TESTED}$$

This outcome preserves scientific validity, statistical power, and strict adherence to the preregistered protocol without post-hoc data manipulation.
