# RC-014B.1 Evidence-Corrected Prokofiev Supplementation & Visions Fugitives Coverage Audit

**Status**: COMPREHENSIVELY AUDITED & VERIFIED  
**Milestone**: RC-014B.1 Evidence Correction & Supplement Qualification  
**Execution Date**: 2026-09-26  
**Primary Manifest Artifact**: [`data/manifests/rc014b_prokofiev_symbolic_coverage.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/manifests/rc014b_prokofiev_symbolic_coverage.json)

---

## 1. Objective & Preregistration Gap Analysis

The frozen RC-012 preregistration requires $M_c \ge 10$ deduplicated, eligible solo piano pieces per composer.

In the conservative, strictly global public domain path (excluding US post-1930 works Op. 65 and Op. 75):
* `Tonal-Piano-Corpus` provides **8 pre-1931 works**:
  1. *Legend* Op. 12 No. 2 (1913)
  2. *Prelude 'Harp'* Op. 12 No. 7 (1913)
  3. *March* Op. 3 No. 3 (1908/1911)
  4. *Etude* Op. 2 No. 4 (1909/1911)
  5. *Toccata* Op. 11 (1912)
  6. *Visions Fugitives* Op. 22 No. 1 (1917)
  7. *Visions Fugitives* Op. 22 No. 5 (1915)
  8. *Visions Fugitives* Op. 22 No. 10 (1915)
* **Gap to $M_{\text{Prokofiev}} = 10$**: Exactly **2 additional pre-1931 pieces** are needed to establish an unassailable global public domain confirmatory set.

---

## 2. Evidence-Corrected Multi-Corpus Audit of *Visions Fugitives*, Op. 22 (All 20 Pieces)

A forensic cross-source verification was conducted across all 20 movements of *Visions Fugitives*, Op. 22:
- **ASAP Dataset**: Audited against actual frozen ASAP score tree $\rightarrow$ **ZERO Op. 22 scores present** (prior claims of full 20-piece ASAP coverage were unverified and are formally retracted).
- **PERiScoPe Dataset**: Lacks confirmed complete Op. 22 standalone symbolic callset $\rightarrow$ marked **UNVERIFIED**.
- **Craig Sapp / Humdrum Collection** (`automata/ana-music` pinned commit `335cbdc617c919d29e9384c4e490cabca5736f73`): Confirmed contains exactly **Nos. 1, 2, and 3** (`visions22-1.krn`, `visions22-2.krn`, `visions22-3.krn`).

### Exact 20-Piece Evidence Matrix:

| No. | Tempo / Character | Tonal-Piano-Corpus | Craig / Humdrum (`ana-music`) | ASAP Dataset | PERiScoPe | Verification Status & Usability |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | *Lentamente* | **PRESENT** (MusicXML+TIFF) | **PRESENT** (`visions22-1.krn`) | **ABSENT** | UNVERIFIED | **VERIFIED (TPC Base)** |
| **2** | *Andante* | ABSENT | **PRESENT** (`visions22-2.krn`) | **ABSENT** | UNVERIFIED | **VERIFIED SUPPLEMENT CANDIDATE** |
| **3** | *Allegretto* | ABSENT | **PRESENT** (`visions22-3.krn`) | **ABSENT** | UNVERIFIED | **VERIFIED SUPPLEMENT CANDIDATE** |
| **4** | *Animato* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **5** | *Molto giocoso* | **PRESENT** (MusicXML+TIFF) | ABSENT | **ABSENT** | UNVERIFIED | **VERIFIED (TPC Base)** |
| **6** | *Con eleganza* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **7** | *Pithesco* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **8** | *Commodo* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **9** | *Allegro tranquillo* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **10** | *Ridicolosamente* | **PRESENT** (MusicXML+TIFF) | ABSENT | **ABSENT** | UNVERIFIED | **VERIFIED (TPC Base)** |
| **11** | *Con vivacità* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **12** | *Assai moderato* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **13** | *Allegretto* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **14** | *Feroce* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **15** | *Inquieto* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **16** | *Dolente* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **17** | *Poetico* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **18** | *Con una dolce lentezza* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **19** | *Presto agitatissimo* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |
| **20** | *Lento irrealmente* | ABSENT | ABSENT | **ABSENT** | UNVERIFIED | UNVERIFIED |

---

## 3. Supplement Candidates Provenance & RC-011 Compatibility Testing

The two supplement candidates were retrieved from `automata/ana-music` (commit `335cbdc617c919d29e9384c4e490cabca5736f73`):
1. **Op. 22 No. 2 (*Andante*)**:
   - File: `corpus/classical/users/craig/classical/prokofiev/op22/visions22-2.krn`
   - SHA-256: `c60ed809b26e1ac0d6862aaf62ba8c89c9c857a6a14cdf9c269a324f735d74e6`
   - Encoder: Craig Stuart Sapp (encoded 2004/12/09)
   - Measures: 24
   - **RC-011 56-Descriptor Extraction**: **PASS (56/56 descriptors extracted without error)**
2. **Op. 22 No. 3 (*Allegretto*)**:
   - File: `corpus/classical/users/craig/classical/prokofiev/op22/visions22-3.krn`
   - SHA-256: `5895df19b433c3ddf4b424f6d0ecfa9b3bcb4cd0f902106c0b5ddea766c49de4`
   - Encoder: Craig Stuart Sapp (encoded 2004/12/09)
   - Measures: 28
   - **RC-011 56-Descriptor Extraction**: **PASS (56/56 descriptors extracted without error)**

### Supplement Source Authority Assessment:
* **Provenance Class**: Direct Humdrum encodings by Craig Stuart Sapp (Center for Computer Assisted Research in the Humanities / Stanford University).
* **Symmetry with Baseline**: Matches the accepted provenance class of `craigsapp/scriabin` (Stanford CCARH Humdrum data, accepted in RC-012 baseline).
* **Licensing Status**: `SUPPLEMENT_LICENSE_PENDING` (upstream repository has non-commercial / CC terms requiring formal policy freeze in RC-014C).

---

## 4. Conclusion & Technical $M_{\text{Prokofiev}}$ Feasibility

Combining the **8 pre-1931 works from `Tonal-Piano-Corpus`** with **2 verified Craig Humdrum supplements (Op. 22 Nos. 2 & 3)** yields an exact, deduplicated, 100% RC-011 compatible confirmatory set of **$M_{\text{Prokofiev}} = 10$ pieces**.
