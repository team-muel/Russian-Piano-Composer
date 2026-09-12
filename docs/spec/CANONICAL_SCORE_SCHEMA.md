# Canonical Symbolic Score Schema Specification (v1)

## Overview
This document specifies the canonical symbolic score data model and Parquet storage schema for the Russian Piano Composer repository.

The canonical symbolic score layer sits directly downstream of raw notation score verification:
$$\boxed{\text{Pinned Source} \rightarrow \text{Verified Raw Artifact} \rightarrow \text{Canonical Symbolic Score}}$$

Every musical event preserves:
- Exact rational timing (`Fraction`) without floating-point rounding errors.
- Spelled pitch preservation (`SpelledPitch`, e.g. $C\sharp 4 \neq D\flat 4$).
- Polyphonic multi-staff and multi-voice tracking.
- Meter changes and pickup measure durations.
- Grace notes and notation tie states without repeat unfolding.

---

## Domain Data Models

### 1. `CanonicalScoreEvent`
- `piece_id: str`: Canonical piece identifier (`<corpus_id>:<score_entry_id>`).
- `event_id: str`: Deterministic event locator ID (`<piece_id>:evt_<index:06d>`).
- `event_index: int`: Zero-based sorted event index.
- `event_kind: EventKind`: Event type (`NOTE` or `REST`).
- `measure_index: int`: Zero-based measure index in score order.
- `source_measure_label: str`: Upstream measure label string.
- `staff: int`: 1-based staff number (notation staff, not physical hand assignment).
- `voice: int`: 1-based voice number.
- `global_onset: Fraction`: Exact global onset time in quarter-note units.
- `offset_in_measure: Fraction`: Exact offset from measure start in quarter-note units.
- `duration: Fraction`: Exact event duration in quarter-note units.
- `pitch: SpelledPitch | None`: Spelled pitch for `NOTE` events (`None` for `REST`).
- `midi: int | None`: Sounding MIDI pitch number in $[0, 127]$ (`None` for `REST`).
- `is_grace: bool`: Flag indicating grace note status (may have `duration == 0`).
- `tie_state: TieState`: Tie notation state (`NONE`, `START`, `CONTINUE`, `STOP`).
- `source_relative_path: str`: Relative path to raw score file.
- `source_event_locator: str`: Detailed locator string for upstream audit.

### 2. `CanonicalMeasure`
- `piece_id: str`: Canonical piece identifier.
- `measure_index: int`: Zero-based measure index.
- `source_measure_label: str`: Upstream measure label.
- `global_onset: Fraction`: Exact measure start onset.
- `actual_duration: Fraction`: Actual measure duration in quarter-note units.
- `time_signature: TimeSignature`: Active meter (`numerator`, `denominator`).
- `expected_duration: Fraction`: Nominal meter duration ($N \times \frac{4}{D}$).
- `is_pickup: bool`: Pickup / anacrusis measure flag.

### 3. `CanonicalScore`
- `piece_id: str`: Canonical piece identifier.
- `corpus_id: str`: Pinned corpus registration ID.
- `corpus_role: CorpusRole`: `GENERATIVE_RUSSIAN` or `CONTROL_NON_RUSSIAN`.
- `score_entry_id: str`: Registered score entry ID.
- `composer: str`: Composer full name.
- `title: str`: Work title.
- `source_repository: str`: Upstream Git repository path.
- `source_commit: str`: 40-character Git commit SHA pin.
- `source_relative_path: str`: Relative score path in repository.
- `source_sha256: str`: Streaming SHA-256 digest of source file.
- `manifest_hash: str`: Canonical manifest hash pin.
- `parser_name: str`: `"ms3"`.
- `parser_version: str`: Parser version string.
- `measures: tuple[CanonicalMeasure, ...]`: Ordered measure list.
- `events: tuple[CanonicalScoreEvent, ...]`: Deterministically sorted event list.
- `canonical_schema_version: int`: Schema version (1).

---

## Interim Parquet Storage Schema

Interim canonical tables are written to `data/interim/canonical/<manifest_hash>/<corpus_id>/`:

### `pieces.parquet`
Columns: `piece_id`, `corpus_id`, `corpus_role`, `score_entry_id`, `composer`, `title`, `source_relative_path`, `source_sha256`, `source_commit`, `manifest_hash`, `canonical_schema_version`, `parser_name`, `parser_version`, `measure_count`, `event_count`, `note_count`, `rest_count`, `grace_note_count`, `canonical_piece_hash`.

### `measures.parquet`
Columns: `piece_id`, `measure_index`, `source_measure_label`, `global_onset_num`, `global_onset_den`, `actual_duration_num`, `actual_duration_den`, `meter_numerator`, `meter_denominator`, `expected_duration_num`, `expected_duration_den`, `is_pickup`.

### `events.parquet`
Columns: `piece_id`, `corpus_id`, `corpus_role`, `event_id`, `event_index`, `event_kind`, `measure_index`, `source_measure_label`, `staff`, `voice`, `onset_num`, `onset_den`, `offset_num`, `offset_den`, `duration_num`, `duration_den`, `pitch_letter`, `pitch_alteration`, `pitch_octave`, `midi`, `is_grace`, `tie_state`, `source_relative_path`, `source_event_locator`.

---

## Deterministic Ordering and Hashing

### Event Sorting Key
Events within a `CanonicalScore` are ordered deterministically by:
1. `global_onset`
2. `measure_index`
3. `staff`
4. `voice`
5. `event_kind`
6. `source_event_locator`

### Semantic Hashes
- **Piece Hash**: SHA-256 digest over normalized text stream of headers, measures, and sorted events.
- **Corpus Hash**: SHA-256 digest over sorted `(score_entry_id, piece_hash)` tuples.
