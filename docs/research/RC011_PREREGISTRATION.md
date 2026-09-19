# Pre-Registration — RC-011 Structural Music Representation Schema V1

## 1. Pre-Registration Statement & Scope
This document pre-registers the exact mathematical formulas, window parameters, normalizations, invariance expectations, missingness rules, and acceptance criteria for the **`STRUCTURAL_REPRESENTATION_SCHEMA_V1`**.

In accordance with strict scientific governance:
- All feature definitions are frozen **prior to executing full-corpus analysis** on the 141-piece canonical dataset.
- Zero national or composer-group style labels are used in designing, selecting, or evaluating features.
- No parameter or threshold may be tuned post-hoc based on Russian-vs-Control discrimination.

---

## 2. Frozen Configuration & Parameter Registry

| Parameter Key | Frozen Value | Scope / Rationale |
| :--- | :--- | :--- |
| `TONAL_LOCAL_WINDOW_MEASURES` | `8` | Local window size for local tonal center correlation. |
| `TONAL_LOCAL_WINDOW_STRIDE` | `1` | Stride across measures for local tonal center evaluation. |
| `KRUMHANSL_MAJOR_PROFILE` | `(6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)` | Standard Krumhansl-Kessler 12-PC major key weights. |
| `KRUMHANSL_MINOR_PROFILE` | `(6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)` | Standard Krumhansl-Kessler 12-PC minor key weights. |
| `CADENCE_BOUNDARY_IOI_RATIO` | `1.5` | Ratio of current onset IOI to local median IOI indicating boundary lengthening. |
| `FORM_SSM_MEASURE_EMBED_DIM` | `12` | Pitch-class distribution per measure used for self-similarity. |
| `FORM_NOVELTY_KERNEL_SIZE` | `4` | Checkerboard kernel width (in measures) for Foote novelty detection. |
| `TEXTURE_ARPEGGIO_MIN_ATTACKS` | `4` | Minimum sequential attacks within a measure to qualify as arpeggio proxy. |
| `TEXTURE_ARPEGGIO_MAX_IOI` | `0.5` | Maximum IOI (in quarter notes) between arpeggio attacks. |
| `TEXTURE_OCTAVE_SEMITONE_MOD` | `12` | Modulo 12 semitone check for simultaneous octave doubling. |
| `TRAJECTORY_BIN_COUNT` | `8` | Exactly 8 equal normalized score-position bins $[0, 1/8), \dots, [7/8, 1]$. |

---

## 3. Structural Feature Schema Catalog (56 Core Descriptors)

### Family A: Tonal / Harmonic Center Proxies (8 Features)
1. `tonal_global_confidence`: Pearson correlation $r_{\text{max}}$ of global duration-weighted PC distribution to best Krumhansl profile. (Units: correlation $[-1, 1]$, Invariance: Transposition-Invariant, Provenance: LITERATURE).
2. `tonal_local_confidence_mean`: Mean $r_{\text{max}}$ across all 8-measure sliding windows. (Units: correlation, Invariance: Transposition-Invariant, Provenance: LITERATURE).
3. `tonal_local_confidence_std`: Standard deviation of local window key correlations. (Units: dispersion, Invariance: Transposition-Invariant, Provenance: LITERATURE).
4. `tonal_center_change_rate`: Frequency of local window key estimate changes per measure. (Units: changes/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
5. `tonal_circle5_distance_mean`: Mean circle-of-fifths distance between consecutive local key estimates. (Units: fifths $[0, 6]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
6. `tonal_circle5_distance_max`: Maximum circle-of-fifths distance between consecutive local key estimates. (Units: fifths $[0, 6]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
7. `tonal_chromatic_duration_share`: Share of total piece duration sounding non-diatonic pitch classes relative to the inferred global key. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
8. `tonal_mode_switch_rate`: Frequency of parallel/relative major-minor mode transitions per measure. (Units: transitions/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).

### Family B: Sonority & Harmonic Motion (8 Features)
9. `sonority_pc_cardinality_mean`: Mean sounding pitch-class set cardinality per distinct onset. (Units: count $[1, 12]$, Invariance: Transposition-Invariant, Provenance: OBSERVED).
10. `sonority_pc_cardinality_std`: Standard deviation of sounding pitch-class cardinality. (Units: count, Invariance: Transposition-Invariant, Provenance: OBSERVED).
11. `sonority_change_rate`: Number of distinct sounding pitch-class set transitions per measure. (Units: changes/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
12. `sonority_stable_duration_share`: Share of total piece duration spent in the top 3 most frequent pitch-class sets. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
13. `sonority_ic1_semitone_share`: Share of interval-class 1 (semitones) in all sounding vertical dyads. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: OBSERVED).
14. `sonority_ic6_tritone_share`: Share of interval-class 6 (tritones) in all sounding vertical dyads. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: OBSERVED).
15. `sonority_bass_interval_variety`: Ratio of distinct bass-relative interval classes to total onsets. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
16. `sonority_harmonic_rhythm_volatility`: Standard deviation of measures elapsed between pitch-class set changes. (Units: measures, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).

### Family C: Cadential & Boundary Proxies (6 Features)
17. `cadence_boundary_candidate_rate`: Frequency of rhythmic/metric boundary candidates per measure. (Units: candidates/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
18. `cadence_boundary_strength_mean`: Mean composite boundary strength score (duration elongation + rest presence + metric weight). (Units: score $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
19. `cadence_tonic_resolution_rate`: Frequency of boundary events with $\hat{5} \to \hat{1}$ or $\hat{7} \to \hat{1}$ motion relative to local tonal center. (Units: resolutions/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
20. `cadence_dominant_tonic_proxy_rate`: Frequency of dominant-type to tonic-type sonority resolutions at detected boundaries. (Units: resolutions/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
21. `cadence_deceptive_proxy_rate`: Frequency of $\hat{5} \to \hat{6}$ bass motions at detected boundaries. (Units: motions/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
22. `cadence_resolution_strength_mean`: Mean cadential strength score across all detected candidates. (Units: score $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).

### Family D: Formal Recurrence & Sectional Architecture (8 Features)
23. `form_ssm_recurrence_density`: Fraction of off-diagonal measure pairs in the self-similarity matrix with cosine similarity $> 0.80$. (Units: density $[0, 1]$, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
24. `form_novelty_peak_rate`: Number of significant Foote novelty peaks per measure. (Units: peaks/measure, Invariance: Transposition-Invariant, Provenance: LITERATURE).
25. `form_novelty_mean`: Mean value of the Foote novelty curve across measures. (Units: score $[0, 1]$, Invariance: Transposition-Invariant, Provenance: LITERATURE).
26. `form_return_late_strength`: Maximum similarity between initial 20% measures and final 30% measures (capturing ABA return). (Units: similarity $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
27. `form_recurrence_distance_mean`: Mean measure distance between recurrences ($S_{i,j} > 0.80$). (Units: measures, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
28. `form_ctu_first_occurrence_mean`: Normalized score position $[0, 1]$ of first CTU candidate appearance. (Units: normalized position, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
29. `form_ctu_recurrence_dispersion`: Normalized standard deviation of CTU occurrence positions across the score. (Units: normalized dispersion, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
30. `form_ctu_late_return_presence`: Binary indicator (0.0 or 1.0) whether any CTU recurs in the final 30% of the score. (Units: binary flag, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).

### Family E: Voice-Leading Geometry (8 Features)
31. `vl_outer_parallel_motion_share`: Share of consecutive outer-voice motions that are parallel (same direction & interval). (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
32. `vl_outer_contrary_motion_share`: Share of consecutive outer-voice motions in contrary directions. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
33. `vl_outer_oblique_motion_share`: Share of consecutive outer-voice motions where one voice is stationary. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
34. `vl_soprano_step_resolution_share`: Share of soprano voice transitions moving by step ($\le 2$ semitones). (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
35. `vl_bass_step_motion_share`: Share of bass voice transitions moving by step ($\le 2$ semitones). (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
36. `vl_semitone_approach_rate`: Rate of half-step melodic approaches in outer voices per measure. (Units: approaches/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
37. `vl_common_tone_retention_rate`: Frequency of retaining $\ge 1$ pitch class between successive onsets. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
38. `vl_min_voice_leading_distance_mean`: Mean minimal total semitone displacement between successive pitch-class sets. (Units: semitones, Invariance: Transposition-Invariant, Provenance: LITERATURE).

### Family F: Piano Texture & Registral Architecture (10 Features)
39. `texture_register_centroid_mean`: Mean sounding MIDI pitch across all attacks. (Units: MIDI pitch, Invariance: Transposition-Equivariant ($\Delta p = +N$), Provenance: OBSERVED).
40. `texture_register_centroid_std`: Standard deviation of sounding pitch centroid across measures. (Units: semitones, Invariance: Transposition-Invariant, Provenance: OBSERVED).
41. `texture_register_span_mean`: Mean vertical span (highest minus lowest sounding MIDI pitch) per onset. (Units: semitones, Invariance: Transposition-Invariant, Provenance: OBSERVED).
42. `texture_register_span_max`: Maximum vertical span observed in the piece. (Units: semitones, Invariance: Transposition-Invariant, Provenance: OBSERVED).
43. `texture_interstaff_gap_mean`: Mean semitone distance between lowest right-hand pitch and highest left-hand pitch. (Units: semitones, Invariance: Transposition-Invariant, Provenance: OBSERVED).
44. `texture_simultaneity_attack_mean`: Mean number of synchronous note attacks per onset timepoint. (Units: count $\ge 1.0$, Invariance: Transposition-Invariant, Provenance: OBSERVED).
45. `texture_block_chord_share`: Share of onsets with $\ge 3$ synchronous attacks across both staves. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
46. `texture_arpeggiation_proxy_rate`: Frequency of detected figurative arpeggiation patterns per measure. (Units: arpeggios/measure, Invariance: Transposition-Invariant, Provenance: HYPOTHESIS).
47. `texture_octave_doubling_share`: Share of onsets containing synchronous octave-doubled pitch classes. (Units: ratio $[0, 1]$, Invariance: Transposition-Invariant, Provenance: OBSERVED).
48. `texture_repeated_note_attack_rate`: Rate of immediate repeated-pitch attacks ($\Delta t \le 0.5$ quarter notes) per measure. (Units: attacks/measure, Invariance: Transposition-Invariant, Provenance: OBSERVED).

### Family G: Normalized Temporal Trajectories (8 Features)
49. `traj_register_center_slope`: Linear regression slope of 8-bin register centroid progression. (Units: semitones/normalized unit, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
50. `traj_register_span_slope`: Linear regression slope of 8-bin register span progression. (Units: semitones/normalized unit, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
51. `traj_attack_density_slope`: Linear regression slope of 8-bin note attack density progression. (Units: attacks/measure per normalized unit, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
52. `traj_attack_density_curvature`: Second-order polynomial coefficient (curvature) of 8-bin note attack density. (Units: curvature, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
53. `traj_chromaticity_slope`: Linear regression slope of 8-bin non-diatonic duration share. (Units: slope, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
54. `traj_sonority_cardinality_slope`: Linear regression slope of 8-bin mean PC cardinality. (Units: slope, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
55. `traj_density_early_late_contrast`: Mean attack density in bins 6-7 minus mean attack density in bins 0-1. (Units: difference in attacks/measure, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).
56. `traj_register_volatility`: Standard deviation of the 8-bin mean register centroids. (Units: semitones, Invariance: Transposition-Invariant, Provenance: ENGINEERING_HEURISTIC).

---

## 4. Invariance & Metamorphic Contract
- **Transposition Invariance**: 55 of 56 features must yield identical floating-point values ($\Delta < 10^{-5}$) under uniform global pitch transposition by $N \in \{-7, -5, +3, +5\}$ semitones. Only `texture_register_centroid_mean` is equivariant ($\Delta = +N$).
- **Time-Scale Invariance**: Ratio-based and normalized quantities must remain identical under uniform duration dilation ($\times 2.0$).
- **Identity Invariance**: Renaming piece ID, file path, voice IDs, or staff IDs (for staff-agnostic features) must yield 100% identical outputs.

---

## 5. Missingness & Availability Policy
- Every feature returns an explicit tuple `(value: float, availability: AvailabilityStatus, reason: str)`.
- `STRUCTURAL_ZERO`: The musical construct was evaluated over valid observations and quantitatively evaluated to 0.0 (e.g., zero octave doublings observed in a purely monophonic piece).
- `UNAVAILABLE`: The preconditions for evaluation were absent (e.g., piece has fewer measures than the local window size or zero valid onsets).
- **Strictly No Silent Zero Imputation**: Downstream consumers must inspect availability status.
