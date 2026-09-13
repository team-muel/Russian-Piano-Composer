# Feature Catalog V1 — Objective Descriptive Music Science

> [!NOTE]
> All features in V1 are classified as **OBSERVED** provenance.
> No feature is labeled "Russian" or "non-Russian" at extraction time.
> Normative style classification occurs downstream in EXP-C01.

## Overview

| Category | Feature Count |
|----------|:---:|
| Pitch Statistics | 8 |
| Interval Statistics | 7 |
| Rhythm Statistics | 8 |
| Contour Features | 4 |
| Density Features | 7 |
| Meter Features | 5 |
| **Total** | **39** |

---

## Pitch Statistics

Computed from all NOTE events across all staves and voices.

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `pitch_range_semitones` | Pitch Range | max(midi) − min(midi) | semitones | int |
| `pitch_mean_midi` | Mean MIDI Pitch | Arithmetic mean of MIDI note numbers | midi | float |
| `pitch_std_midi` | Pitch Std Dev | Population std dev of MIDI note numbers | midi | float |
| `pitch_median_midi` | Median MIDI Pitch | Median MIDI note number | midi | float |
| `pitch_class_entropy` | Pitch Class Entropy | Shannon entropy of 12-bin PC histogram (base-2) | bits | float |
| `pitch_class_count` | Pitch Class Count | Distinct pitch classes (0–11) used | count | int |
| `pitch_lowest_midi` | Lowest MIDI Pitch | Minimum MIDI note number | midi | int |
| `pitch_highest_midi` | Highest MIDI Pitch | Maximum MIDI note number | midi | int |

---

## Interval Statistics

Computed from successive staff-1/voice-1 NOTE events (treble melody voice), sorted by onset.

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `interval_mean_abs_semitones` | Mean Absolute Interval | Mean of \|semitone interval\| | semitones | float |
| `interval_std_abs_semitones` | Interval Std Dev | Population std dev of \|semitone interval\| | semitones | float |
| `interval_max_abs_semitones` | Largest Absolute Interval | Maximum \|semitone interval\| | semitones | int |
| `interval_leap_ratio` | Leap Ratio | Fraction with \|semitones\| > 2 | ratio | float |
| `interval_step_ratio` | Step Ratio | Fraction with \|semitones\| ≤ 2 | ratio | float |
| `interval_direction_change_ratio` | Direction Change Ratio | Fraction of consecutive pairs with direction change | ratio | float |
| `interval_unison_ratio` | Unison Ratio | Fraction with semitones = 0 | ratio | float |

---

## Rhythm Statistics

Computed from all non-grace NOTE events. Durations expressed in quarter-note units.

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `rhythm_duration_mean` | Mean Duration | Arithmetic mean of note durations | quarter notes | float |
| `rhythm_duration_std` | Duration Std Dev | Population std dev of durations | quarter notes | float |
| `rhythm_duration_median` | Median Duration | Median note duration | quarter notes | float |
| `rhythm_distinct_durations` | Distinct Durations | Count of distinct duration values | count | int |
| `rhythm_dotted_ratio` | Dotted Note Ratio | Fraction matching standard dotted values | ratio | float |
| `rhythm_shortest_duration` | Shortest Duration | Minimum note duration | quarter notes | float |
| `rhythm_longest_duration` | Longest Duration | Maximum note duration | quarter notes | float |
| `rhythm_duration_range_ratio` | Duration Range Ratio | longest / shortest | ratio | float |

---

## Contour Features

Computed from staff-1/voice-1 NOTE events (treble melody voice).

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `contour_ascending_ratio` | Ascending Ratio | Fraction of Parsons U (up) transitions | ratio | float |
| `contour_descending_ratio` | Descending Ratio | Fraction of Parsons D (down) transitions | ratio | float |
| `contour_repeat_ratio` | Repeat Ratio | Fraction of Parsons R (same pitch) transitions | ratio | float |
| `contour_arc_score` | Arch Contour Score | Pearson correlation with ideal arch shape | correlation | float |

---

## Density Features

Computed from all events across all staves and voices.

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `density_notes_per_measure` | Notes/Measure | Total NOTE events / measures | count/measure | float |
| `density_events_per_measure` | Events/Measure | Total events / measures | count/measure | float |
| `density_notes_per_quarter` | Notes/Quarter | NOTE events / total duration in quarters | count/quarter | float |
| `density_rest_ratio` | Rest Ratio | REST events / total events | ratio | float |
| `density_grace_note_ratio` | Grace Note Ratio | Grace notes / total NOTE count | ratio | float |
| `density_staff_count` | Staff Count | Distinct staves used | count | int |
| `density_voice_count` | Voice Count | Distinct (staff, voice) combinations | count | int |

---

## Meter Features

Computed from measure metadata.

| Feature ID | Name | Description | Unit | Dtype |
|-----------|------|-------------|------|-------|
| `meter_primary_numerator` | Primary Numerator | Most common time signature numerator | beats | int |
| `meter_primary_denominator` | Primary Denominator | Most common time signature denominator | beat unit | int |
| `meter_change_count` | Meter Changes | Number of time-signature transitions | count | int |
| `meter_has_pickup` | Has Pickup | 1 if first measure is anacrusis, else 0 | boolean | int |
| `meter_total_measures` | Total Measures | Total measure count | count | int |

---

## Provenance

All 39 features are classified as:

```
provenance: OBSERVED
```

This means every feature value is derived directly from corpus data with no musicological assumptions. Features may later be reclassified as `LITERATURE` or `HYPOTHESIS` when combined with external scholarship during EXP-C01.

## Voice Extraction Convention

Melodic features (intervals, contour) use **staff-1/voice-1** as the primary melody voice. This is a pragmatic engineering choice for DCML MuseScore encodings where the treble staff is typically staff 1.

Full-corpus aggregate features (pitch, rhythm, density, meter) operate across **all staves and voices**.
