# Feature Catalog V2 — Objective Descriptive Music Science (Polyphonic-Audited)

> [!IMPORTANT]
> Feature Schema Version: `FEATURE_SCHEMA_VERSION = 2`.
> This catalog documents breaking scientific semantic updates introduced in RC-009A-A, including voice-aware monophonic stream extraction, tie continuation filtering, grace-note isolation, duration-weighted primary meter, and explicit Category A/B/C/D validity auditing.
> Historical V1 specification is preserved in [FEATURE_CATALOG_V1.md](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/docs/spec/FEATURE_CATALOG_V1.md).

## 1. Overview & Summary Statistics

| Category | Definition | Feature Count |
| :--- | :--- | :---: |
| **Category A** | **Analysis-Ready**: Duration/count normalized, free of size/representation confounds. | 32 |
| **Category B** | **Usable with Limitation**: Valid observable; contains piece-length or meter confounds. | 5 |
| **Category C** | **Diagnostic Only**: Summary heuristic correlation template. | 1 |
| **Category D** | **Unsupported / Disabled**: Notation metadata (dots/tuplets) not in canonical v1 schema. | 1 |
| **Total Registered** | | **39** |

---

## 2. Polyphonic Extraction Policies

- **Melodic Transition Policy**: Computed within each canonical `(staff, voice)` stream independently. A transition is eligible **only** when consecutive onset groups within that voice each contain **exactly one attacked pitch**.
- **Tie Continuation Policy**: Tie continuations (`tie_state` in `[CONTINUE, STOP]`) are excluded from attack-based pitch, interval, contour, and density calculations.
- **Grace-Note Policy**: Grace notes (`is_grace == True`) are excluded from core structural pitch, interval, rhythm, contour, and density features.
- **Primary Meter Policy**: Duration-weighted primary time signature occupying maximum cumulative metric duration across all measures.

---

## 3. Complete Registered Feature Specifications

### A. Pitch Domain (8 Features)

1. `pitch_range_semitones`
   - **Name**: Pitch Range (semitones)
   - **Definition**: `max(midi) - min(midi)` across non-grace NOTE attacks
   - **Dtype**: `int` | **Unit**: `semitones` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

2. `pitch_mean_midi`
   - **Name**: Mean MIDI Pitch
   - **Definition**: Arithmetic mean of MIDI note numbers across non-grace NOTE attacks
   - **Dtype**: `float` | **Unit**: `midi` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

3. `pitch_std_midi`
   - **Name**: Pitch Std Dev (MIDI)
   - **Definition**: Population standard deviation of MIDI note numbers across non-grace NOTE attacks
   - **Dtype**: `float` | **Unit**: `midi` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

4. `pitch_median_midi`
   - **Name**: Median MIDI Pitch
   - **Definition**: Median MIDI note number across non-grace NOTE attacks
   - **Dtype**: `float` | **Unit**: `midi` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

5. `pitch_class_entropy`
   - **Name**: Pitch Class Entropy
   - **Definition**: Shannon entropy of the 12-bin pitch-class attack histogram ($-\sum p_i \log_2 p_i$)
   - **Dtype**: `float` | **Unit**: `bits` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

6. `pitch_class_count`
   - **Name**: Pitch Class Count
   - **Definition**: Number of distinct pitch classes (0-11) used
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category B — length-dependent)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

7. `pitch_lowest_midi`
   - **Name**: Lowest MIDI Pitch
   - **Definition**: Minimum MIDI note number across non-grace NOTE attacks
   - **Dtype**: `int` | **Unit**: `midi` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

8. `pitch_highest_midi`
   - **Name**: Highest MIDI Pitch
   - **Definition**: Maximum MIDI note number across non-grace NOTE attacks
   - **Dtype**: `int` | **Unit**: `midi` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

---

### B. Interval Domain (7 Features)

9. `interval_mean_abs_semitones`
   - **Name**: Mean Absolute Interval (semitones)
   - **Definition**: Mean $|iv|$ across eligible voice-aware single-note monophonic transitions
   - **Dtype**: `float` | **Unit**: `semitones` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

10. `interval_std_abs_semitones`
   - **Name**: Interval Std Dev (semitones)
   - **Definition**: Population std dev of $|iv|$ across eligible monophonic transitions
   - **Dtype**: `float` | **Unit**: `semitones` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

11. `interval_max_abs_semitones`
   - **Name**: Largest Absolute Interval
   - **Definition**: Maximum $|iv|$ across eligible monophonic transitions
   - **Dtype**: `int` | **Unit**: `semitones` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

12. `interval_leap_ratio`
   - **Name**: Leap Ratio
   - **Definition**: Fraction of eligible melodic transitions with $|iv| > 2$ semitones
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

13. `interval_step_ratio`
   - **Name**: Step Ratio
   - **Definition**: Fraction of eligible melodic transitions with $|iv| \le 2$ semitones
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

14. `interval_direction_change_ratio`
   - **Name**: Direction Change Ratio
   - **Definition**: Fraction of consecutive eligible interval pairs with opposing signs
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

15. `interval_unison_ratio`
   - **Name**: Unison Ratio
   - **Definition**: Fraction of eligible melodic transitions with $iv = 0$ semitones
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

---

### C. Rhythm Domain (8 Features)

16. `rhythm_duration_mean`
   - **Name**: Mean Note Duration
   - **Definition**: Arithmetic mean of non-grace note durations in quarter-note units
   - **Dtype**: `float` | **Unit**: `quarter_notes` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

17. `rhythm_duration_std`
   - **Name**: Duration Std Dev
   - **Definition**: Population standard deviation of note durations in quarter-note units
   - **Dtype**: `float` | **Unit**: `quarter_notes` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

18. `rhythm_duration_median`
   - **Name**: Median Note Duration
   - **Definition**: Median note duration in quarter-note units
   - **Dtype**: `float` | **Unit**: `quarter_notes` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `attack-weighted`

19. `rhythm_distinct_durations`
   - **Name**: Distinct Duration Count
   - **Definition**: Count of distinct non-grace duration values observed
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category B — length-dependent)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

20. `rhythm_dotted_ratio`
   - **Name**: Dotted Note Ratio (Unsupported)
   - **Definition**: Disabled: Notation dot metadata is not preserved in canonical score schema v1
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `ENGINEERING_HEURISTIC`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category D — set to `null`)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

21. `rhythm_shortest_duration`
   - **Name**: Shortest Duration
   - **Definition**: Minimum non-grace note duration in quarter-note units
   - **Dtype**: `float` | **Unit**: `quarter_notes` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

22. `rhythm_longest_duration`
   - **Name**: Longest Duration
   - **Definition**: Maximum non-grace note duration in quarter-note units
   - **Dtype**: `float` | **Unit**: `quarter_notes` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

23. `rhythm_duration_range_ratio`
   - **Name**: Duration Range Ratio
   - **Definition**: `longest_duration / shortest_duration`
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

---

### D. Contour Domain (4 Features)

24. `contour_ascending_ratio`
   - **Name**: Ascending Contour Ratio
   - **Definition**: Fraction of Parsons U (up) transitions in eligible monophonic voice streams
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

25. `contour_descending_ratio`
   - **Name**: Descending Contour Ratio
   - **Definition**: Fraction of Parsons D (down) transitions in eligible monophonic voice streams
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

26. `contour_repeat_ratio`
   - **Name**: Repeat Contour Ratio
   - **Definition**: Fraction of Parsons R (same pitch) transitions in eligible monophonic voice streams
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `voice_transition` | **Weighting**: `unweighted`

27. `contour_arc_score`
   - **Name**: Arch Contour Score
   - **Definition**: Pearson correlation of top-voice pitch sequence with ideal arch template
   - **Dtype**: `float` | **Unit**: `correlation` | **Provenance**: `ENGINEERING_HEURISTIC`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category C — heuristic template)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`

---

### E. Density Domain (7 Features)

28. `density_notes_per_measure`
   - **Name**: Notes Per Measure
   - **Definition**: Total NOTE attack events / total measures
   - **Dtype**: `float` | **Unit**: `count/measure` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category B — meter-confounded)
   - **Observation Unit**: `measure` | **Weighting**: `measure-avg`

29. `density_events_per_measure`
   - **Name**: Events Per Measure
   - **Definition**: Total events (NOTE + REST) / total measures
   - **Dtype**: `float` | **Unit**: `count/measure` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category B — meter-confounded)
   - **Observation Unit**: `measure` | **Weighting**: `measure-avg`

30. `density_notes_per_quarter`
   - **Name**: Notes Per Quarter Note
   - **Definition**: Total NOTE attack events / total piece duration in quarter-note units
   - **Dtype**: `float` | **Unit**: `count/quarter` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `quarter_notes` | **Weighting**: `duration-avg`

31. `density_rest_ratio`
   - **Name**: Rest Event Ratio
   - **Definition**: REST events / total events (event-level proportion, not acoustic silence)
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `notated_event` | **Weighting**: `unweighted`

32. `density_grace_note_ratio`
   - **Name**: Grace Note Ratio
   - **Definition**: Grace note count / total NOTE count
   - **Dtype**: `float` | **Unit**: `ratio` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `note_attack` | **Weighting**: `unweighted`

33. `density_staff_count`
   - **Name**: Staff Count
   - **Definition**: Count of distinct staves used
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`

34. `density_voice_count`
   - **Name**: Voice Count
   - **Definition**: Count of distinct (staff, voice) combinations used
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`

---

### F. Meter Domain (5 Features)

35. `meter_primary_numerator`
   - **Name**: Primary Time Signature Numerator
   - **Definition**: Numerator of time signature occupying greatest cumulative duration
   - **Dtype**: `int` | **Unit**: `beats` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `duration-weighted`

36. `meter_primary_denominator`
   - **Name**: Primary Time Signature Denominator
   - **Definition**: Denominator of time signature occupying greatest cumulative duration
   - **Dtype**: `int` | **Unit**: `beat_unit` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `duration-weighted`

37. `meter_change_count`
   - **Name**: Meter Change Count
   - **Definition**: Count of time-signature transitions between adjacent measures
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`

38. `meter_has_pickup`
   - **Name**: Has Pickup Measure
   - **Definition**: 1 if first measure is anacrusis, else 0
   - **Dtype**: `int` | **Unit**: `boolean` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `true` (Category A)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`

39. `meter_total_measures`
   - **Name**: Total Measure Count
   - **Definition**: Total measure count in piece
   - **Dtype**: `int` | **Unit**: `count` | **Provenance**: `OBSERVED`
   - **Status**: Registered: `true` | Emitted: `true` | Analysis-Ready: `false` (Category B — length-dependent)
   - **Observation Unit**: `whole_piece` | **Weighting**: `unweighted`
