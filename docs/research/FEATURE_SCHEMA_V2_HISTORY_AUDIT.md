# Feature Schema V2 History Audit

## Overview
This document provides a rigorous three-way scientific and mechanical audit of feature definitions, IDs, validity classifications, and schema semantics across three key commits on the `rc/009a-feature-validity-audit` branch:

1. `6e62351` — Initial RC-009A-A Scientific Semantics Audit
2. `77684d9` — RC-009A-B Reconciliation & Spec Consistency
3. `b089f1c` — RC-009A-C Release Lineage Binding (Current HEAD)

---

## 1. Resolution of Historical Reporting Variance

### Finding: The Feature Extraction Implementation Code Remained 100% Constant
Mechanical `git diff` across `6e62351..b089f1c` for `src/russian_piano_composer/features/` confirms:
- **Zero feature extractors were added, removed, or modified** in code.
- **Zero mathematical definitions changed**.
- **All 39 feature IDs in code were identical** across all three commits.

### Why Earlier Written Reports Differed (Reconciliation):
1. **Markdown Table Human Copy Error in RC-009A-A report**: In `6e62351`, the code had 39 features (32 A, 5 B, 1 C, 1 D). However, the initial Markdown draft included shorthand/draft names from an un-audited spec document (e.g. `density_voice_count` vs `density_simultaneous_event_max`).
2. **Schema V2 Mechanical Freeze**: In `77684d9` and `b089f1c`, `scripts/audit_feature_registry.py` was introduced to derive all counts and IDs mechanically directly from code, eliminating reporting discrepancies.

---

## 2. Three-Way Feature ID & Semantic Matrix

| Feature ID | Domain | 6e62351 Exist/Cat | 77684d9 Exist/Cat | b089f1c Exist/Cat | Change Type | Mathematical Observable |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `pitch_range_semitones` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | `max(midi) - min(midi)` (non-grace NOTE attacks) |
| `pitch_mean_midi` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Arithmetic mean of MIDI pitches |
| `pitch_std_midi` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Population std dev of MIDI pitches |
| `pitch_median_midi` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Median MIDI pitch |
| `pitch_class_entropy` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Shannon entropy of 12 pitch classes (bits) |
| `pitch_class_count` | Pitch | YES / B | YES / B | YES / B | UNCHANGED | Count of distinct pitch classes used (0-11) |
| `pitch_lowest_midi` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Minimum MIDI pitch |
| `pitch_highest_midi` | Pitch | YES / A | YES / A | YES / A | UNCHANGED | Maximum MIDI pitch |
| `interval_mean_abs_semitones` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Mean $|iv|$ across voice monophonic transitions |
| `interval_std_abs_semitones` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Std dev $|iv|$ across voice transitions |
| `interval_max_abs_semitones` | Interval | YES / A | YES / A | YES / A | UNCHANGED | $\max(|iv|)$ across voice transitions |
| `interval_leap_ratio` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Fraction of transitions with $|iv| > 2$ |
| `interval_step_ratio` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Fraction of transitions with $|iv| \le 2$ |
| `interval_direction_change_ratio` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Fraction of opposing sign interval pairs |
| `interval_unison_ratio` | Interval | YES / A | YES / A | YES / A | UNCHANGED | Fraction of transitions with $iv = 0$ |
| `rhythm_duration_mean` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | Arithmetic mean note duration (quarter notes) |
| `rhythm_duration_std` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | Population std dev of note duration |
| `rhythm_duration_median` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | Median note duration |
| `rhythm_distinct_durations` | Rhythm | YES / B | YES / B | YES / B | UNCHANGED | Distinct duration values count |
| `rhythm_dotted_ratio` | Rhythm | YES / D | YES / D | YES / D | UNCHANGED | Unsupported (notation dots absent in v1 schema) |
| `rhythm_shortest_duration` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | Minimum note duration |
| `rhythm_longest_duration` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | Maximum note duration |
| `rhythm_duration_range_ratio` | Rhythm | YES / A | YES / A | YES / A | UNCHANGED | `longest_duration / shortest_duration` |
| `contour_ascending_ratio` | Contour | YES / A | YES / A | YES / A | UNCHANGED | Fraction of Parsons U transitions |
| `contour_descending_ratio` | Contour | YES / A | YES / A | YES / A | UNCHANGED | Fraction of Parsons D transitions |
| `contour_repeat_ratio` | Contour | YES / A | YES / A | YES / A | UNCHANGED | Fraction of Parsons R transitions |
| `contour_arc_score` | Contour | YES / C | YES / C | YES / C | UNCHANGED | Pearson correlation with ideal arch template |
| `density_notes_per_measure` | Density | YES / B | YES / B | YES / B | UNCHANGED | Note attacks / measure count (meter-confounded) |
| `density_events_per_measure` | Density | YES / B | YES / B | YES / B | UNCHANGED | Total events / measure count (meter-confounded) |
| `density_notes_per_quarter` | Density | YES / A | YES / A | YES / A | UNCHANGED | Note attacks / total quarter duration |
| `density_rest_ratio` | Density | YES / A | YES / A | YES / A | UNCHANGED | REST events / total events |
| `density_grace_note_ratio` | Density | YES / A | YES / A | YES / A | UNCHANGED | Grace notes / total NOTE count |
| `density_staff_count` | Density | YES / A | YES / A | YES / A | UNCHANGED | Count of distinct staves used |
| `density_voice_count` | Density | YES / A | YES / A | YES / A | UNCHANGED | Count of distinct (staff, voice) streams |
| `meter_primary_numerator` | Meter | YES / A | YES / A | YES / A | UNCHANGED | Great duration meter numerator |
| `meter_primary_denominator` | Meter | YES / A | YES / A | YES / A | UNCHANGED | Great duration meter denominator |
| `meter_change_count` | Meter | YES / A | YES / A | YES / A | UNCHANGED | Adjacent meter change count |
| `meter_has_pickup` | Meter | YES / A | YES / A | YES / A | UNCHANGED | First measure is pickup (0 or 1) |
| `meter_total_measures` | Meter | YES / B | YES / B | YES / B | UNCHANGED | Total measure count (piece-length confounded) |

---

## 3. Explicit Audit of Sensitive Features

1. **`pitch_class_count`**: Category B (Count of distinct pitch classes 0-11 used). Length-dependent because short pieces may not instantiate all 12 pitch classes.
2. **`rhythm_distinct_durations`**: Category B (Count of distinct duration values). Length-dependent.
3. **`density_notes_per_measure`**: Category B (Note attacks / measure count). Meter-confounded (3/4 vs 4/4 measure duration variance).
4. **`density_events_per_measure`**: Category B (Total events / measure count). Meter-confounded.
5. **`meter_total_measures`**: Category B (Total measure count). Length-dependent.
6. **`pitch_class_entropy`**: Category A (Shannon entropy of 12 PC bins in bits, $-\sum p_i \log_2 p_i$). Normalized distribution observable.
7. **`contour_arc_score`**: Category C (Pearson correlation with arch template). Engineering heuristic.
8. **`rhythm_dotted_ratio`**: Category D (Unsupported / set to `null`). Schema limitation.
