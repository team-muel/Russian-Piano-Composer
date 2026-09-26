# RC-014B.2 Humdrum Supplement Provenance, Invariance, and License Chain Audit

## 1. Overview & Context

During RC-014A and RC-014B, the public repository `hectorbellmann-art/Tonal-Piano-Corpus` (TPC) was qualified as a candidate source for Russian piano compositions, providing:
* **Anton Rubinstein**: 11 source-linked MusicXML pieces ($M_{\text{Rubinstein}} = 11 \ge 10$).
* **Sergei Prokofiev**: 12 MusicXML pieces, of which 8 are pre-1931 public domain works.

To satisfy the frozen RC-012 preregistration requirement of $M_{\text{Prokofiev}} \ge 10$ exclusively with public domain works, two supplementary pieces from *Visions Fugitives*, Op. 22 were identified:
1. **Op. 22 No. 2 (*Andante*)**
2. **Op. 22 No. 3 (*Allegretto*)**

This audit establishes the frozen repository identity, encoder lineage, canonical conversion invariance, feature extraction reproducibility, and licensing posture for these Humdrum supplements.

---

## 2. Pinned Repository Identity & Score Hashes

* **External Repository**: `automata/ana-music` (`https://github.com/automata/ana-music.git`)
* **Frozen Commit SHA**: `335cbdc617c919d29e9384c4e490cabca5736f73`
* **Root Tree SHA**: `a7f14da4844b47ac3484b01d5d3da2a0029e4b6a`

### Pinned Supplement Records:

| Metric / Field | Op. 22 No. 2 (*Andante*) | Op. 22 No. 3 (*Allegretto*) |
|---|---|---|
| **Piece Identifier** | `prokofiev_op22_no02` | `prokofiev_op22_no03` |
| **Relative Path** | `corpus/classical/users/craig/classical/prokofiev/op22/visions22-2.krn` | `corpus/classical/users/craig/classical/prokofiev/op22/visions22-3.krn` |
| **Git Blob SHA** | `8ecec739bc4c7f561e2c7c141aff1cf40d9d3c0d` | `d7554373b3d67e4606f9f2f5f79b34608a000b12` |
| **File SHA-256** | `944d176184b7311f3a9faee8726fb2583287fce0caf984e7118d37c4c37d71a3` | `5d8d2a84e7b39df25553c4175fdf56ea52a655fa1ca58abc9aaf68db30848399` |
| **Canonical Score Hash** | `d55701ebe75dbe6b44266a8642218e4709f00610d2e1cfbe644c3506d9980eb7` | `8f0e835d0c317be57839ef5bc536af52c379400bc25f007796a71d125dfa2f47` |
| **Derived Feature Bundle Hash** | `caabe00c9a7e607e320b67c7b5e9a0721d517c3c8535f1aee39bd88af51e0f15` | `4dc22a99e8408e949ce144d05ae7482ab570f15dbc03daf59cfcd76329ce6051` |
| **Measures Count** | 24 | 28 |
| **Canonical Events Count** | 281 | 310 |

---

## 3. Embedded Source Metadata & Provenance Lineage

Direct extraction from the `**kern` file headers yields:

```text
Op. 22 No. 2:
!!!COM: Prokofiev, Sergey
!!!CDT: 1891/04/23/-1953/03/05/
!!!OTL@@RU: Mimoletnosti 
!!!OTL@EN:  Visions fugitives
!!!ONB: set of 20 pieces
!!!ODT: 1915///-1917///
!!!OPS: Op. 22
!!!ONM: No. 2
!!!OMD: Andante
!!!ENC: Craig Stuart Sapp
!!!END: 2004/12/09/

Op. 22 No. 3:
!!!COM: Prokofiev, Sergey
!!!CDT: 1891/04/23/-1953/03/05/
!!!OTL@@RU: Mimoletnosti 
!!!OTL@EN:  Visions fugitives
!!!ONB: set of 20 pieces
!!!ODT: 1915///-1917///
!!!OPS: Op. 22
!!!ONM: No. 3
!!!OMD: Allegretto
!!!ENC: Craig Stuart Sapp
!!!END: 2004/12/09/
```

### Upstream Lineage Verification:
* **Repository Role**: `automata/ana-music` is an automated mirror / corpus aggregation of the Stanford Center for Computer Assisted Research in the Humanities (CCARH) KernScores repository (`https://kern.humdrum.org`, directory `users/craig/classical/prokofiev/op22`).
* **Encoder**: Dr. Craig Stuart Sapp (Stanford CCARH).
* **Encoding Date**: December 9, 2004.

### Provenance Symmetry with Accepted Scriabin Baseline:

| Dimension | Accepted Scriabin Baseline (`craigsapp/scriabin`) | Candidate Prokofiev Supplements (`ana-music` Op. 22) | Symmetry Evaluation |
|---|---|---|---|
| **Transcriber / Encoder** | Craig Stuart Sapp | Craig Stuart Sapp | **IDENTICAL** |
| **Institutional Lineage** | Stanford CCARH / KernScores | Stanford CCARH / KernScores | **IDENTICAL** |
| **Source Data Format** | Humdrum `**kern` | Humdrum `**kern` | **IDENTICAL** |
| **Editorial Architecture** | Explicit spine polyphony & measure tags | Explicit spine polyphony & measure tags | **IDENTICAL** |
| **Provenance Verdict** | `VERIFIED_SOURCE` | `VERIFIED_SOURCE` | **`SAME_PROVENANCE_CLASS`** |

**Conclusion**: The Prokofiev Op. 22 Nos. 2 & 3 Humdrum scores belong to the **exact same provenance class** as the accepted Scriabin confirmatory corpus.

---

## 4. Converter Resolution & Correction of `ms3` Claim

In the RC-014B.1 report, a reference to an `ms3 Humdrum converter` was mistakenly included due to reporting conflation with the DCML MuseScore parsing pipeline.

* **Actual Converter**: `music21` (version `10.5.0`)
* **API Entrypoint**: `music21.converter.parse(krn_path)`
* **Classification Outcome**: `MUSIC21_HUMDRUM_USED` (Correction of prior reporting error).

---

## 5. Canonical Conversion Invariant Audit

The Humdrum-to-Canonical conversion adapter (`scripts/materialize_rc014_prokofiev_supplements.py:parse_humdrum_to_canonical`) guarantees the following notation invariants:
1. **Measure Counts & Labels**:
   - Op. 22 No. 2: Exactly 24 measures (numbered 1–24, 0 pickups).
   - Op. 22 No. 3: Exactly 28 measures (numbered 1–28, 0 pickups).
2. **Pitch Events & De-chording**:
   - Single notes and chord elements are decomposed into `CanonicalScoreEvent` objects.
   - Spelled pitches are parsed into `SpelledPitch(letter, alteration, octave)` with exact MIDI verification (`midi == pitch.midi`).
3. **Rational Timings & Durations**:
   - Global onsets and durations are represented as exact `Fraction` quarter lengths limited to denominator 1920 (no floating-point rounding errors).
4. **Meter Changes**:
   - Op. 22 No. 2 maintains constant 4/4 meter throughout.
   - Op. 22 No. 3 accurately tracks meter shifts: 4/4 $\rightarrow$ 2/4 in M16 $\rightarrow$ 4/4 in M17 $\rightarrow$ 2/4 in M20 $\rightarrow$ 4/4 in M21–M28.
5. **Ties & Polyphony**:
   - `music21` tie types (`start`, `continue`, `stop`) are mapped directly to `TieState` enum values.
   - Polyphonic spines are mapped to staff indices (Staff 1, Staff 2, Staff 3).
6. **No Silent Loss**:
   - All notes, chords, and rests are accounted for without structural loss.

---

## 6. Frozen 56-Descriptor Feature Extraction

Both supplement scores were processed with the frozen RC-011 structural feature extractor (`STRUCTURAL_REPRESENTATION_SCHEMA_V1`):
* **Schema Hash**: `924a19913f831c4f0ffba2dfa88188b88e598af635046b05e580e5b807355282`
* **Op. 22 No. 2**: 56 / 56 descriptors extracted (**PASS**)
* **Op. 22 No. 3**: 56 / 56 descriptors extracted (**PASS**)
* **Classifier Execution**: **NONE** (No RC-012 model predictions evaluated; feature extraction performed in strict role blindness).

---

## 7. Digital Licensing & Access Governance

* **Supplement Repository Digital License**: `SUPPLEMENT_DIGITAL_LICENSE = UNDECLARED` (No root `LICENSE` file present in `automata/ana-music`).
* **Underlying Musical Composition**: `PUBLIC_DOMAIN` globally (Prokofiev Op. 22 composed 1915–1917, published 1918 by Gutheil; pre-1931 US PD + Life+70 EU PD).
* **Two-Axis Representation**:
  - **Technical Reproducibility**: `TECHNICALLY_VALID` (Ephemeral non-vendored pipeline verified).
  - **Legal / Redistribution Authority**: `LEGAL_AUTHORITY_PENDING` (`raw_file_redistribution_permitted: false`).
* **Derived Feature Extraction & Retention**:
  - `derived_feature_extraction_technically_supported = true`
  - `derived_feature_retention_authority = "PENDING"`

---

## 8. Two-Clean-Room Reproducibility Audit

The non-vendored materialization and feature extraction pipelines were executed across two independent clean-room runs:
1. `scripts/materialize_rc014_external_corpus.py` (23 TPC scores): **100% bit-exact across runs**.
2. `scripts/materialize_rc014_prokofiev_supplements.py` (2 Humdrum supplements): **100% bit-exact across runs**.

All generated receipts are persisted in `data/reviews/rc014/`.

---

## 9. Technical Candidate Counts & Live Governance State

* **Anton Rubinstein**: **$M_{\text{technical}} = 11 \ge 10$** (11 source-linked TPC pieces).
* **Sergei Prokofiev**: **$M_{\text{technical}} = 10 \ge 10$** (8 pre-1931 TPC pieces + 2 verified Humdrum supplements: Op. 22 Nos. 2 & 3).
* **Live Registered Russian Confirmatory Pool**: **$N_{\text{Russian}} = 2$** (*Alexander Scriabin*, *Modest Mussorgsky*).
* **RC-012 Resumption Gate**: **`BLOCKED`**.

---

## 10. Primary Outcome Verdict

$$\mathbf{RC014B2\_TECHNICAL\_CORPUS\_READY\_LEGAL\_AUTHORITY\_PENDING}$$
