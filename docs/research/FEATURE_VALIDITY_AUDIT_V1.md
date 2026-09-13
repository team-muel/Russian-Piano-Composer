# Feature Validity Audit V1 (RC-009A-B Corrected & Reconciled)

## Overview & Scientific Purpose
This document provides the complete, mechanically reconciled scientific feature semantics and polyphonic validity audit for all 39 registered score features in the **Russian Piano Composer** project.

- **Corpus Manifest Hash**: `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212`
- **Canonical Score Schema Version**: `1`
- **Feature Schema Version**: `2` (`FEATURE_SCHEMA_VERSION = 2`)
- **Feature Matrix Semantic Hash**: `14b4518c59ce4f9c67df29182945db06c064ca6f7c25a5083cc986acfe6d1755`
- **Audit Reconciliation Outcome**: Exactly 39 registered descriptors, 39 emitted matrix columns.
  - **Category A (Analysis-Ready)**: 32 features
  - **Category B (Usable with Limitation)**: 5 features
  - **Category C (Diagnostic Only)**: 1 feature (`contour_arc_score`)
  - **Category D (Unsupported / Disabled)**: 1 feature (`rhythm_dotted_ratio`)

---

## 1. Feature Set Reconciliation

| Feature Count Type | Definition | Count |
| :--- | :--- | :---: |
| **REGISTERED** | Feature descriptors defined in `FEATURE_REGISTRY` | **39** |
| **EMITTED** | Output feature columns in `corpus_features.parquet` | **39** |
| **ANALYSIS_READY** | Category A features (free of size/representation confounds) | **32** |

### Category Set Disjointness & Union
- **`A`**: `{pitch_range_semitones, pitch_mean_midi, pitch_std_midi, pitch_median_midi, pitch_class_entropy, pitch_lowest_midi, pitch_highest_midi, interval_mean_abs_semitones, interval_std_abs_semitones, interval_max_abs_semitones, interval_leap_ratio, interval_step_ratio, interval_direction_change_ratio, interval_unison_ratio, rhythm_duration_mean, rhythm_duration_std, rhythm_duration_median, rhythm_shortest_duration, rhythm_longest_duration, rhythm_duration_range_ratio, contour_ascending_ratio, contour_descending_ratio, contour_repeat_ratio, density_notes_per_quarter, density_rest_ratio, density_grace_note_ratio, density_staff_count, density_voice_count, meter_primary_numerator, meter_primary_denominator, meter_change_count, meter_has_pickup}` (32)
- **`B`**: `{pitch_class_count, rhythm_distinct_durations, density_notes_per_measure, density_events_per_measure, meter_total_measures}` (5)
- **`C`**: `{contour_arc_score}` (1)
- **`D`**: `{rhythm_dotted_ratio}` (1)

$$
A \cap B = A \cap C = A \cap D = B \cap C = B \cap D = C \cap D = \varnothing
$$

$$
|A| + |B| + |C| + |D| = 32 + 5 + 1 + 1 = 39 = |FEATURE\_REGISTRY|
$$

---

## 2. Corpus Piece & Row Integrity
- **Total Registered Pieces**: 141
- **Missing Pieces**: 0
- **Extra Pieces**: 0
- **Duplicate Pieces**: 0
- **Corpus Composition**:
  - `dcml_medtner_tales`: 19
  - `dcml_rachmaninoff_op42`: 22
  - `dcml_tchaikovsky_seasons`: 12
  - `dcml_chopin_mazurkas`: 56
  - `dcml_liszt_annees`: 19
  - `dcml_schumann_kinderszenen`: 13

---

## 3. Complete 39-Feature Audit Table

| Feature ID | Domain | Unit | Math / Logical Definition | Obs Unit | Weighting | Tie Policy | Grace Policy | Chord Policy | Provenance | Verdict | Comp Ready | Confounds |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pitch_range_semitones` | Pitch | semitones | `max(midi) - min(midi)` | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Pitch extreme outliers |
| `pitch_mean_midi` | Pitch | midi | Arithmetic mean of MIDI pitches | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Register bias |
| `pitch_std_midi` | Pitch | midi | Population std dev of MIDI pitches | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Polyphonic texture width |
| `pitch_median_midi` | Pitch | midi | Median MIDI pitch | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Register bias |
| `pitch_class_entropy` | Pitch | bits | $-\sum p_i \log_2 p_i$ (12 PC bins) | note_attack | attack-weighted | Exclude | Exclude | Individual | DERIVED | **Category A** | `true` | Chromaticism vs tonality |
| `pitch_class_count` | Pitch | count | Count of distinct pitch classes | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category B** | `false` | Piece length confound |
| `pitch_lowest_midi` | Pitch | midi | `min(midi)` | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Instrument compass limits |
| `pitch_highest_midi` | Pitch | midi | `max(midi)` | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Instrument compass limits |
| `interval_mean_abs_semitones` | Interval | semitones | Mean $|iv|$ across voice monophonic transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Voice density |
| `interval_std_abs_semitones` | Interval | semitones | Std dev $|iv|$ across voice transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Voice density |
| `interval_max_abs_semitones` | Interval | semitones | $\max(|iv|)$ across voice transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Ornamental leaps |
| `interval_leap_ratio` | Interval | ratio | Fraction of transitions with $|iv| > 2$ | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Melodic disjunction |
| `interval_step_ratio` | Interval | ratio | Fraction of transitions with $|iv| \le 2$ | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Scalic conjunct motion |
| `interval_direction_change_ratio` | Interval | ratio | Fraction of opposing sign interval pairs | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Melodic zigzag contour |
| `interval_unison_ratio` | Interval | ratio | Fraction of transitions with $iv = 0$ | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Repeated note attacks |
| `rhythm_duration_mean` | Rhythm | quarter_notes | Arithmetic mean note duration | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Tempo/notational unit |
| `rhythm_duration_std` | Rhythm | quarter_notes | Population std dev of note duration | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Duration variety |
| `rhythm_duration_median` | Rhythm | quarter_notes | Median note duration | note_attack | attack-weighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Principal metric unit |
| `rhythm_distinct_durations` | Rhythm | count | Distinct duration values count | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category B** | `false` | Piece length confound |
| `rhythm_dotted_ratio` | Rhythm | ratio | Disabled (notation dots not in v1 schema) | note_attack | unweighted | Exclude | Exclude | Individual | HEURISTIC | **Category D** | `false` | Schema missing dot metadata |
| `rhythm_shortest_duration` | Rhythm | quarter_notes | Minimum note duration | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Virtuosic fast notes |
| `rhythm_longest_duration` | Rhythm | quarter_notes | Maximum note duration | note_attack | unweighted | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Sustained pedal notes |
| `rhythm_duration_range_ratio` | Rhythm | ratio | `longest_duration / shortest_duration` | note_attack | unweighted | Exclude | Exclude | Individual | DERIVED | **Category A** | `true` | Rhythmic contrast |
| `contour_ascending_ratio` | Contour | ratio | Fraction of Parsons U transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Upward line tendency |
| `contour_descending_ratio` | Contour | ratio | Fraction of Parsons D transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Downward line tendency |
| `contour_repeat_ratio` | Contour | ratio | Fraction of Parsons R transitions | voice_transition | unweighted | Exclude | Exclude | Single-note | OBSERVED | **Category A** | `true` | Static pitch line tendency |
| `contour_arc_score` | Contour | correlation | Pearson $r$ with arch template | whole_piece | unweighted | Exclude | Exclude | Single-note | HEURISTIC | **Category C** | `false` | Heuristic template assumption |
| `density_notes_per_measure` | Density | count/measure | Note attacks / measure count | measure | measure-avg | Exclude | Exclude | Individual | OBSERVED | **Category B** | `false` | Time signature meter confound |
| `density_events_per_measure` | Density | count/measure | Total events / measure count | measure | measure-avg | Count | Include | Individual | OBSERVED | **Category B** | `false` | Time signature meter confound |
| `density_notes_per_quarter` | Density | count/quarter | Note attacks / total quarter duration | quarter_notes | duration-avg | Exclude | Exclude | Individual | OBSERVED | **Category A** | `true` | Polyphonic activity |
| `density_rest_ratio` | Density | ratio | REST events / total events | notated_event | unweighted | Count | N/A | N/A | OBSERVED | **Category A** | `true` | Event-level rests (not silence) |
| `density_grace_note_ratio` | Density | ratio | Grace notes / total NOTE count | note_attack | unweighted | Exclude | Count | Individual | OBSERVED | **Category A** | `true` | Ornamentation density |
| `density_staff_count` | Density | count | Count of distinct staves used | whole_piece | unweighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Grand staff layout |
| `density_voice_count` | Density | count | Count of (staff, voice) streams | whole_piece | unweighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Polyphonic voice complexity |
| `meter_primary_numerator` | Meter | beats | Great duration numerator | whole_piece | duration-weighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Metric pulse |
| `meter_primary_denominator` | Meter | beat_unit | Great duration denominator | whole_piece | duration-weighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Metric unit |
| `meter_change_count` | Meter | count | Adjacent meter change count | whole_piece | unweighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Metric instability |
| `meter_has_pickup` | Meter | boolean | First measure is pickup (0 or 1) | whole_piece | unweighted | N/A | N/A | N/A | OBSERVED | **Category A** | `true` | Anacrusis structure |
| `meter_total_measures` | Meter | count | Measure count | whole_piece | unweighted | N/A | N/A | N/A | OBSERVED | **Category B** | `false` | Piece length confound |
