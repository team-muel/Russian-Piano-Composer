# RC-013 Score-Entry Unit Policy & Rights Firewall

**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Status**: APPROVED & ACTIVE  
**Date**: 2026-09-20  

---

## 1. Purpose & Scientific Scope

The purpose of RC-013 is to acquire, digitize, and validate a notation-level, provenance-preserving symbolic piano score corpus for previously under-digitized Russian composers (*Sergei Lyapunov*, *Anton Arensky*, *Anatoly Lyadov*). This will expand the qualified Russian confirmatory set from $N_{\text{Russian}}=2$ (Scriabin, Mussorgsky) to $N_{\text{Russian}} \ge 4$ independent composers with $M_c \ge 10$ eligible pieces each, enabling a rigorous future resumption of the RC-012 external confirmation milestone under a future pre-registration amendment.

This document establishes the strict score-entry unit definitions, segmentation boundaries, and legal rights firewall governing all materials ingested into RC-013.

---

## 2. Score-Entry Unit Definition

To prevent arbitrary fragmentation, data leakage, artificial score inflation, and cherry-picking, the definition of an eligible score-entry unit is strictly delimited:

### 2.1 Permitted Units
A valid score-entry unit $S_i$ MUST be one of the following:
1. **Complete Standalone Solo Piano Work**:
   - An independent musical composition conceived, titled, and published as a single standalone piece for solo piano (e.g., concert étude, standalone prelude, valse, toccata, impromptu).
2. **Authentic Source-Level Movement / Piece of a Multi-Movement Cycle**:
   - A distinct, authorially conceived movement or numbered piece within an authorized opus, suite, cycle, or collection of character pieces (e.g., individual études in an étude collection, individual pieces within a set of character pieces, individual movements of a sonata or suite).
   - The movement/piece must possess an identifiable beginning and end (double bar line / final cadence) designated by the composer in the original published edition.

### 2.2 Prohibited Units (Strictly Disallowed)
The following practices are explicitly forbidden:
- **Arbitrary Fragmentation**: Splitting a piece into arbitrary sections, phrase fragments, expositions, development sections, or periods.
- **Page-Level Splitting**: Dividing a piece based on page turns, line breaks, or system boundaries.
- **Multiple Editions of the Same Composition**: Ingesting alternative editions or duplicate arrangements of the identical piece within the confirmatory candidate pool. In the event of multiple source editions, exactly ONE primary historical edition must be selected.
- **Arrangements of Non-Piano Works**: Piano transcriptions or reductions of orchestral, vocal, chamber, or operatic works by the same or different composers (unless explicitly written by the original composer as an authentic autonomous piano concert fantasy and pre-registered as such).
- **Incomplete Fragments**: Sketches, unfinished drafts, or truncated excerpts.

---

## 3. Musical Notation Preservation Requirements

Every digitized symbolic score ingested into RC-013 must strictly preserve musical notation integrity at the XML/syntax level:

1. **Measure Boundaries**:
   - Every bar line, measure index, and measure duration must reflect the original score. Pickup bars (anacrusis) must be explicitly encoded with fractional duration attributes.
2. **Pitch Spelling**:
   - Enharmonic spellings (e.g., $D\sharp$ vs $E\flat$, $F\times$ vs $G$, $B\sharp$ vs $C$) must strictly mirror the authoritative print edition. No automatic enharmonic normalization or flattening is permitted.
3. **Sounding Rests & Silences**:
   - All rests in all voices and staves must be explicitly encoded. No silent gaps between note offsets may exist without explicit rest elements.
4. **Staves & Polyphonic Voices**:
   - Dual-staff piano layout (Upper Staff: Treble/G-clef; Lower Staff: Bass/F-clef, or appropriate historical clef changes) must be preserved.
   - Independent contrapuntal voices within each staff must retain distinct voice tags.
5. **Key & Time Signatures**:
   - Initial and internal key/time signature changes must be encoded precisely at the measures designated in the print source.
6. **Ties & Expressive Markings**:
   - Rhythmic ties across beats or bar lines must maintain complete start-stop graph connectivity.
   - Slurs, dynamics, articulation, and tempo designations should be transcribed faithfully without editorial invention.

---

## 4. Rights & Provenance Firewall

All materials utilized in RC-013 must satisfy an absolute, fail-closed rights firewall separating composition status, scan provenance, and symbolic encoding licenses:

| Layer | Status Requirement | Acceptable Values | Verification Protocol |
|---|---|---|---|
| **Composition Public Domain** | Expired copyright worldwide | $p_{\text{death}} \le 1955$ (Lifetime + 70 years rule) | Biographical audit of composer death date (Lyapunov $\dagger 1924$, Arensky $\dagger 1906$, Lyadov $\dagger 1914$). |
| **Source Scan Reuse Status** | Public domain scan / open access | Historic first/early editions published prior to 1928 (U.S. Public Domain) or non-copyrightable digitized public scans (IMSLP, Sibley, BNF Gallica). | Plate number, publication date, library watermark inspection. |
| **Encoding License** | Permissive open scientific license | `CC0-1.0`, `CC-BY-4.0`, or `Public Domain Mark 1.0` | Clear license declaration in file metadata and manifest. |
| **Analysis Eligibility** | Fully cleared for computational musicology | `ANALYSIS_ELIGIBLE = TRUE` | Requires all upstream layers to be cleared. |
| **Generative Eligibility** | Cleared for synthetic training / derivative models | `GENERATIVE_ELIGIBLE = TRUE` | Unencumbered open license. |

### Fail-Closed Principle
If any ambiguity exists regarding the publication date, edition copyright, or scan status of a source document, the candidate item MUST be flagged with `EXCLUDED: RIGHTS_AMBIGUITY` and withheld from the canonical corpus.

---

## 5. Provenance Tags

Each digitized score must carry exactly one primary provenance tag indicating its construction methodology:
- `OMR_RAW`: Direct optical music recognition output without human verification (prohibited from final canonical status).
- `OMR_CORRECTED`: OMR scan output with exhaustive measure-by-measure manual proofreading and correction against the reference plate scan.
- `MANUALLY_TRANSCRIBED`: Directly transcribed by hand in notation software (e.g. MuseScore/LilyPond/music21) from the reference print scan.
- `INDEPENDENTLY_VERIFIED`: Proofread and audited by a secondary automated or human review process against the source scan.

Only scores bearing `OMR_CORRECTED` or `MANUALLY_TRANSCRIBED` + `INDEPENDENTLY_VERIFIED` are eligible for canonical inclusion in the RC-013 corpus.
