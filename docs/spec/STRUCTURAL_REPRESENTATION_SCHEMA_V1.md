# STRUCTURAL_REPRESENTATION_SCHEMA_V1 Specification

## 1. Overview
The **`STRUCTURAL_REPRESENTATION_SCHEMA_V1`** defines 56 frozen symbolic music descriptors across 7 foundational families of music theory, cognitive musicology, and piano performance.

Schema Version: `1`  
Structural Schema Hash: `924a19913f831c4f0ffba2dfa88188b88e598af635046b05e580e5b807355282`  
Invariance Contract Hash: `31ce0651691d6c21edd28cc3d6a4abdee8e6dd9145efd18eeea67fd1b2b8fa10`

---

## 2. Feature Families & Descriptors

| Family | Feature ID | Unit / Scale | Invariance | Provenance | Availability Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TONAL** | `tonal_global_confidence` | Correlation $[-1, 1]$ | Invariant | LITERATURE | $\ge 1$ sounding note |
| **TONAL** | `tonal_local_confidence_mean` | Correlation $[-1, 1]$ | Invariant | LITERATURE | $\ge 1$ window |
| **TONAL** | `tonal_local_confidence_std` | Dispersion | Invariant | LITERATURE | $\ge 2$ windows |
| **TONAL** | `tonal_center_change_rate` | Changes / measure | Invariant | HYPOTHESIS | $\ge 2$ windows |
| **TONAL** | `tonal_circle5_distance_mean` | Fifths $[0, 6]$ | Invariant | HYPOTHESIS | $\ge 1$ key change |
| **TONAL** | `tonal_circle5_distance_max` | Fifths $[0, 6]$ | Invariant | HYPOTHESIS | $\ge 1$ key change |
| **TONAL** | `tonal_chromatic_duration_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ sounding note |
| **TONAL** | `tonal_mode_switch_rate` | Transitions / measure | Invariant | HYPOTHESIS | $\ge 2$ windows |
| **SONORITY** | `sonority_pc_cardinality_mean` | Count $[1, 12]$ | Invariant | OBSERVED | $\ge 1$ onset |
| **SONORITY** | `sonority_pc_cardinality_std` | Dispersion | Invariant | OBSERVED | $\ge 2$ onsets |
| **SONORITY** | `sonority_change_rate` | Changes / measure | Invariant | HYPOTHESIS | $\ge 1$ onset |
| **SONORITY** | `sonority_stable_duration_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ onset |
| **SONORITY** | `sonority_ic1_semitone_share` | Ratio $[0, 1]$ | Invariant | OBSERVED | $\ge 1$ dyad |
| **SONORITY** | `sonority_ic6_tritone_share` | Ratio $[0, 1]$ | Invariant | OBSERVED | $\ge 1$ dyad |
| **SONORITY** | `sonority_bass_interval_variety` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ onset |
| **SONORITY** | `sonority_harmonic_rhythm_volatility` | Measures (std) | Invariant | HYPOTHESIS | $\ge 2$ transitions |
| **CADENCE** | `cadence_boundary_candidate_rate` | Candidates / measure | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ onset |
| **CADENCE** | `cadence_boundary_strength_mean` | Score $[0, 1]$ | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ candidate |
| **CADENCE** | `cadence_tonic_resolution_rate` | Resolutions / measure | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ onset |
| **CADENCE** | `cadence_dominant_tonic_proxy_rate` | Resolutions / measure | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ onset |
| **CADENCE** | `cadence_deceptive_proxy_rate` | Motions / measure | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ onset |
| **CADENCE** | `cadence_resolution_strength_mean` | Score $[0, 1]$ | Sensitive by design (dilated: rest threshold) | HYPOTHESIS | $\ge 1$ candidate |
| **FORM** | `form_ssm_recurrence_density` | Density $[0, 1]$ | Invariant | HEURISTIC | $\ge 2$ measures |
| **FORM** | `form_novelty_peak_rate` | Peaks / measure | Invariant | LITERATURE | $\ge 8$ measures |
| **FORM** | `form_novelty_mean` | Score $[0, 1]$ | Invariant | LITERATURE | $\ge 8$ measures |
| **FORM** | `form_return_late_strength` | Similarity $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 2$ measures |
| **FORM** | `form_recurrence_distance_mean` | Measures | Invariant | HYPOTHESIS | $\ge 1$ recurrence |
| **FORM** | `form_ctu_first_occurrence_mean` | Normalized $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ CTU |
| **FORM** | `form_ctu_recurrence_dispersion` | Dispersion $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 2$ CTUs |
| **FORM** | `form_ctu_late_return_presence` | Binary $\{0, 1\}$ | Invariant | HYPOTHESIS | $\ge 1$ CTU |
| **VOICE_LEADING** | `vl_outer_parallel_motion_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ outer motion |
| **VOICE_LEADING** | `vl_outer_contrary_motion_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ outer motion |
| **VOICE_LEADING** | `vl_outer_oblique_motion_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ outer motion |
| **VOICE_LEADING** | `vl_soprano_step_resolution_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ soprano motion |
| **VOICE_LEADING** | `vl_bass_step_motion_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ bass motion |
| **VOICE_LEADING** | `vl_semitone_approach_rate` | Approaches / measure | Invariant | HYPOTHESIS | $\ge 2$ onsets |
| **VOICE_LEADING** | `vl_common_tone_retention_rate` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 2$ onsets |
| **VOICE_LEADING** | `vl_min_voice_leading_distance_mean` | Semitones | Invariant | LITERATURE | $\ge 2$ onsets |
| **TEXTURE** | `texture_register_centroid_mean` | MIDI Pitch $[0, 127]$ | Equivariant ($+N$) | OBSERVED | $\ge 1$ note |
| **TEXTURE** | `texture_register_centroid_std` | Semitones | Invariant | OBSERVED | $\ge 2$ measures |
| **TEXTURE** | `texture_register_span_mean` | Semitones | Invariant | OBSERVED | $\ge 1$ onset |
| **TEXTURE** | `texture_register_span_max` | Semitones | Invariant | OBSERVED | $\ge 1$ onset |
| **TEXTURE** | `texture_interstaff_gap_mean` | Semitones | Invariant | OBSERVED | $\ge 1$ 2-staff onset |
| **TEXTURE** | `texture_simultaneity_attack_mean` | Attacks / onset | Invariant | OBSERVED | $\ge 1$ onset |
| **TEXTURE** | `texture_block_chord_share` | Ratio $[0, 1]$ | Invariant | HYPOTHESIS | $\ge 1$ onset |
| **TEXTURE** | `texture_arpeggiation_proxy_rate` | Runs / measure | Sensitive by design (dilated) | HYPOTHESIS | $\ge 1$ measure |
| **TEXTURE** | `texture_octave_doubling_share` | Ratio $[0, 1]$ | Invariant | OBSERVED | $\ge 1$ onset |
| **TEXTURE** | `texture_repeated_note_attack_rate` | Repetitions / measure | Sensitive by design (dilated) | OBSERVED | $\ge 1$ measure |
| **TRAJECTORY** | `traj_register_center_slope` | Slope / piece | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_register_span_slope` | Slope / piece | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_attack_density_slope` | Slope / piece | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_attack_density_curvature` | Curvature | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_chromaticity_slope` | Slope / piece | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_sonority_cardinality_slope` | Slope / piece | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_density_early_late_contrast` | Density diff | Invariant | HEURISTIC | $\ge 1$ note |
| **TRAJECTORY** | `traj_register_volatility` | Semitones (std) | Invariant | HEURISTIC | $\ge 1$ note |

---

## 3. Missingness Policy & Availability Rules
Every extracted value provides a typed status:
- `AVAILABLE`: Valid musical construct successfully computed.
- `STRUCTURAL_ZERO`: The construct was checked against valid score observations and evaluated to zero (e.g., zero octave doublings in a monophonic line).
- `UNAVAILABLE`: Preconditions for measurement were not met (e.g., fewer measures than the window parameter or zero sounding notes).
- **Strictly No Silent Zero Imputation**: Downstream algorithms and models must not conflate `STRUCTURAL_ZERO` with missing/unobserved phenomena.
