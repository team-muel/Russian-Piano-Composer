# ADR-006: Canonical Symbolic Score Ingestion Layer

## Context
The Russian Piano Composer project requires high-precision symbolic music input for downstream late-Romantic Russian style analysis, voice leading, and theme generation.
Upstream notation files contain polyphony, multiple staves and voices, spelled pitches, pickup measures, meter changes, ties, and grace notes.

To prevent silent information loss or corruption:
1. Musical timing must be represented rationally without float rounding errors.
2. Pitch spelling ($C\sharp 4 \neq D\flat 4$) must be preserved.
3. Raw corpus sources must remain read-only scientific evidence.
4. Score repeat notation must not be unfolded into duplicated performance playback events.

## Decision
We establish a canonical symbolic score layer (`CanonicalScore`, `CanonicalMeasure`, `CanonicalScoreEvent`) enforcing:
- **Pinned Immutable Source + SHA-256 Receipts**: Raw scores are cloned to `data/raw/<corpus_id>/<commit>/repository/` and verified with streaming SHA-256 receipts.
- **Exact Rational Timing (`Fraction`)**: All global onsets, offsets in measure, measure durations, and event durations use exact rational numbers. No float timing leakage is permitted in canonical storage.
- **Spelled Pitch Preservation (`SpelledPitch`)**: Pitch identity is defined by `(letter, alteration, octave)` retaining musical spelling. MIDI is stored as a derived invariant cross-check ($0 \le MIDI \le 127, MIDI == pitch.midi$).
- **Polyphony, Staff, & Voice Tracking**: Polyphonic events across multiple staves and voices are preserved as distinct simultaneous `CanonicalScoreEvent`s. Staff identity is preserved without assuming hand assignments.
- **Notation Order Over Performance Unfolding**: Canonical scores preserve written notation order. Volta endings and repeat signs are stored as measure metadata without duplicating events.
- **Isolated Parser Adapter**: All `ms3` calls are isolated inside `src/russian_piano_composer/corpus/adapters/dcml_ms3.py`.
- **Deterministic Semantic Hashes**: Every piece and corpus computes a deterministic logical SHA-256 hash.

## Rejected Alternatives
1. **MIDI-Only Canonical Representation**: Rejected. Erases pitch spelling ($C\sharp$ vs $D\flat$), staves, and notation ties essential for voice leading and harmonic analysis.
2. **Floating-Point Canonical Timing**: Rejected. Accumulates rounding errors across complex meters, tuplets, and dotted rhythms.
3. **Enharmonic Normalization**: Rejected. Converts $C\sharp$ to $D\flat$ or vice versa, destroying late-Romantic chromatic modulation semantics.
4. **Performance Unfolding of Repeats**: Rejected. Distorts statistical feature counts by duplicating repeated measures.
5. **Editing Raw Upstream Files**: Rejected. Violates scientific immutability and provenance traceability.

## Status
Accepted and verified in RC-007.
