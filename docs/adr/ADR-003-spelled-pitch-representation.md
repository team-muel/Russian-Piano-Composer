### Title: ADR-003: Canonical Spelled Pitch and Interval Representation

### Status: Accepted
### Date: 2026-09-13

### Context
Russian late-Romantic piano music heavily relies on chromatic voice leading, enharmonic reinterpretation, diminished-seventh and augmented-sixth harmonies, and subtle thematic transformations. Reducing pitches to anonymous 12-tone pitch classes or MIDI numbers discards harmonic spelling information ($C\sharp \neq D\flat$), leading to ambiguous voice-leading analysis, incorrect MusicXML notation export, and loss of harmonic intent.

### Decision
1. **Canonical Pitch Representation**: `SpelledPitch` is the canonical representation across domain/theory layers. It retains written `PitchLetter` (C, D, E, F, G, A, B), integer accidental `alteration` (e.g. -2 for double flat, +1 for sharp), and scientific `octave`.
2. **Sounding Information**: Sounding MIDI values and pitch classes are derived properties ($MIDI = 12(octave + 1) + natural\_pc(letter) + alteration$).
3. **Enharmonic Equivalence**: Structural equality (`__eq__`) preserves musical spelling ($C\sharp 4 \neq D\flat 4$). Sounding pitch equality is available explicitly via `same_sounding_pitch()`.
4. **Canonical Interval Representation**: `DirectedInterval` preserves both diatonic step displacement and chromatic semitone distance. Interval quality (`P`, `M`, `m`, `A`, `d`) is mathematically derived from diatonic step class and semitone deviation.
5. **Transposition**: Transposition by a `DirectedInterval` preserves diatonic target letter and derives exact accidental alterations.

### Rejected Alternatives
- **MIDI-only canonical pitch representation**: Rejected because it loses enharmonic identity ($C\sharp 4 == D\flat 4 == 61$) and prevents accurate chromatic voice-leading analysis.
- **Pitch class integer (0..11) canonical representation**: Rejected because pitch classes lack octave register and fail to distinguish enharmonic pitch spellings.

### Consequences
- **Pros**:
  - Exact preservation of musical spelling ($C\sharp \neq D\flat$).
  - Rigorous directed interval calculations and mathematical quality derivation for simple and compound intervals.
  - Reliable voice-leading analysis and clean MusicXML export.
- **Cons**:
  - More complex than naive MIDI/pitch-class arithmetic.
  - Exporters and performance engines must explicitly access `.midi` for sounding output.
