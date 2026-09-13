# Architecture Decision Record: Polyphonic Descriptive Feature Semantics (ADR-008)

- **Status**: Accepted
- **Date**: 2026-09-13
- **Context**: RC-009A-A Scientific Feature Semantics & Polyphonic Validity Audit

---

## 1. Context and Problem Statement

RC-009A introduced 39 initial numerical features for descriptive score analysis across pitch, interval, rhythm, contour, density, and meter domains. However, polyphonic piano scores introduce complex structural patterns (multiple staves/voices, simultaneous chord tones, tie continuations, grace notes, anacrusis measures) that render global note ordering and unweighted heuristic features scientifically invalid or ambiguous.

Before any statistical analysis or Candidate Thematic Unit (CTU) discovery can take place, every feature's mathematical and musical semantics must be precisely defined, audited, and bound to an explicit feature schema version (`FEATURE_SCHEMA_VERSION = 2`).

---

## 2. Decision Outcomes

### A. Polyphonic Melodic Streams & Melodic Transition Policy
- **Global Note Ordering Invalidity**: Melodic intervals and contour codes must **never** be computed by sorting all notes globally by onset across the entire score. Global sorting produces false leaps between independent register parts (e.g. left-hand bass vs right-hand soprano) or simultaneous chord tones.
- **Voice-Aware Stream Partitioning**: Melodic transitions are evaluated independently within each canonical `(staff, voice)` stream.
- **Staff != Hand Principle**: `staff` represents score visual layout, not physical hand assignment. Extractor features must never assume `staff 1` is "right hand" or `staff 2` is "left hand".
- **Strict Single-Note Monophonic Transition Rule**: A melodic transition within a `(staff, voice)` stream is eligible **only** when consecutive onset groups each contain **exactly one attacked pitch**.
- **Chord Tone Exclusion**: Onsets containing multiple simultaneous chord pitches within the same voice are excluded from core monophonic melodic interval/contour statistics unless explicitly handled by a separate voice-leading model.
- **Diagnostic Coverage Tracking**: Extracted feature metadata tracks `eligible_melodic_transition_count`, `possible_voice_transition_count`, and `melodic_transition_coverage`. If no eligible melodic transitions exist (e.g. Liszt *Gondoliera* where no voice contains single-note transitions), melodic features return explicit `null` (never `0`).

### B. Tie Continuation Policy
- Tie continuations (`tie_state` in `[CONTINUE, STOP]`) represent sustained sound from a prior onset, **not** new melodic attacks.
- Onset-based melodic interval transitions, pitch-class counts, contour codes, and note-attack density calculations **must ignore tie continuations** so they do not fabricate false unison attacks.

### C. Grace-Note Policy
- Grace notes (`is_grace == True`) are excluded from core structural pitch, interval, rhythm, contour, and density features.
- Grace notes are analyzed separately via `density_grace_note_ratio`.

### D. Notation-Derived Features & Schema Constraints
- **Dotted Ratio & Tuplet Ratio**: Canonical Score Schema v1 stores exact rational timing (`Fraction`) without preserving raw notation glyphs (dots, tuplet brackets). Guessing tuplet status from rational denominators (e.g. `den % 3 == 0`) or dotted status from duration alone is scientifically ungrounded.
- **Action**: `rhythm_dotted_ratio` and `rhythm_tuplet_ratio` are classified as `UNSUPPORTED_FROM_CANONICAL_SCHEMA` (Category D) and excluded from analysis-ready feature sets.

### E. Rest & Silence Distinction
- `density_rest_ratio` measures the proportion of explicit `REST` events relative to total events.
- It does **not** represent acoustic silence, as other polyphonic voices or staves may be sounding during a voice rest.

### F. Primary Meter & Pickup Detection
- **Primary Meter**: Defined deterministically as the `(numerator, denominator)` time signature occupying the greatest cumulative metric duration (whole-note units) across all measures, with tie-breaking by earliest occurrence.
- **Pickup Measure**: Anacrusis is detected when measure 0 has `actual_duration < expected_duration` or explicit `dont_count == True`.

### G. Feature Schema Versioning & Deterministic Lineage
- Upgraded `FEATURE_SCHEMA_VERSION` from `1` to `2`.
- `CorpusFeatureMatrix` computes a deterministic `feature_matrix_semantic_hash` over all piece IDs, canonical piece hashes, feature schema version, and feature values.

---

## 3. Scientific Audit Classifications (39 Registered Descriptors)

| Feature ID | Category | Status | Notes |
| :--- | :---: | :---: | :--- |
| `pitch_range_semitones` | **A** | Analysis-Ready | Non-grace note attack observed |
| `pitch_mean_midi` | **A** | Analysis-Ready | Non-grace note attack mean |
| `pitch_std_midi` | **A** | Analysis-Ready | Non-grace note attack std dev |
| `pitch_median_midi` | **A** | Analysis-Ready | Non-grace note attack median |
| `pitch_class_entropy` | **A** | Analysis-Ready | 12-bin pitch class entropy (bits) |
| `pitch_class_count` | **B** | Usable w/ Limitation | Raw count; requires normalization for comparison |
| `pitch_lowest_midi` | **A** | Analysis-Ready | Minimum attacked pitch |
| `pitch_highest_midi` | **A** | Analysis-Ready | Maximum attacked pitch |
| `interval_mean_abs_semitones` | **A** | Analysis-Ready | Voice-aware monophonic transition mean |
| `interval_std_abs_semitones` | **A** | Analysis-Ready | Voice-aware monophonic transition std dev |
| `interval_max_abs_semitones` | **A** | Analysis-Ready | Voice-aware monophonic max interval |
| `interval_leap_ratio` | **A** | Analysis-Ready | Voice-aware fraction (>2 semitones) |
| `interval_step_ratio` | **A** | Analysis-Ready | Voice-aware fraction (<=2 semitones) |
| `interval_direction_change_ratio` | **A** | Analysis-Ready | Voice-aware direction change fraction |
| `interval_unison_ratio` | **A** | Analysis-Ready | Voice-aware unison fraction |
| `rhythm_duration_mean` | **A** | Analysis-Ready | Quarter-note unit mean duration |
| `rhythm_duration_std` | **A** | Analysis-Ready | Quarter-note unit std dev duration |
| `rhythm_duration_median` | **A** | Analysis-Ready | Quarter-note unit median duration |
| `rhythm_distinct_durations` | **B** | Usable w/ Limitation | Distinct duration count |
| `rhythm_dotted_ratio` | **D** | Unsupported | Notation dot metadata not in canonical schema v1 |
| `rhythm_shortest_duration` | **A** | Analysis-Ready | Minimum non-grace duration |
| `rhythm_longest_duration` | **A** | Analysis-Ready | Maximum non-grace duration |
| `rhythm_duration_range_ratio` | **A** | Analysis-Ready | Max / Min duration ratio |
| `contour_ascending_ratio` | **A** | Analysis-Ready | Voice-aware Parsons U fraction |
| `contour_descending_ratio` | **A** | Analysis-Ready | Voice-aware Parsons D fraction |
| `contour_repeat_ratio` | **A** | Analysis-Ready | Voice-aware Parsons R fraction |
| `contour_arc_score` | **C** | Diagnostic Only | Pearson correlation with ideal arch template |
| `density_notes_per_measure` | **B** | Usable w/ Limitation | Meter-confounded across 3/4 vs 4/4 |
| `density_events_per_measure` | **B** | Usable w/ Limitation | Meter-confounded across 3/4 vs 4/4 |
| `density_notes_per_quarter` | **A** | Analysis-Ready | Duration-normalized note attack density |
| `density_rest_ratio` | **A** | Analysis-Ready | Event-level rest proportion (not silence) |
| `density_grace_note_ratio` | **A** | Analysis-Ready | Grace note proportion |
| `density_staff_count` | **A** | Analysis-Ready | Distinct staves count |
| `density_voice_count` | **A** | Analysis-Ready | Distinct (staff, voice) streams count |
| `meter_primary_numerator` | **A** | Analysis-Ready | Duration-weighted primary numerator |
| `meter_primary_denominator` | **A** | Analysis-Ready | Duration-weighted primary denominator |
| `meter_change_count` | **A** | Analysis-Ready | Adjacent time signature transition count |
| `meter_has_pickup` | **A** | Analysis-Ready | Anacrusis measure flag |
| `meter_total_measures` | **B** | Usable w/ Limitation | Total piece measure count |

---

## 4. Category Summary
- **Category A (Analysis-Ready)**: 28 features
- **Category B (Usable with Limitation)**: 8 features
- **Category C (Diagnostic Only)**: 1 feature (`contour_arc_score`)
- **Category D (Unsupported / Disabled)**: 2 features (`rhythm_dotted_ratio`, `rhythm_tuplet_ratio` [reserved])
