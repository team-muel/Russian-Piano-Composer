# Comprehensive 56-Descriptor Dependency & Identifiability Audit for RC-011 and RC-013

**Milestone**: RC-013 Protocol V6 Genuine Differential Counterfactual Source Verification  
**Authority**: `docs/spec/STRUCTURAL_REPRESENTATION_SCHEMA_V1.md`  
**Schema Version**: 1 (56 Frozen Descriptors across 7 Families)  
**Status**: `AUDITED & FROZEN`  

---

## 1. Executive Summary

This audit establishes the exact mathematical, symbolic, and visual requirements for all 56 frozen descriptors of the RC-011 Structural Music Representation V1 specification.

| Metric | Value |
|---|---|
| **Total Frozen Descriptors** | **56** |
| **Directly Machine-Supported Descriptors** | **55** (98.21%) |
| **Partially Supported Descriptors** | **1** (`texture_interstaff_gap_mean` - 1.79%) |
| **Unsupported Descriptors / Schema Gaps** | **0** (0.00%) |
| **Underlying Required Dimensions** | `pitch`, `accidental`, `octave`, `onset`, `duration`, `rest`, `staff`, `measure_sequence` |

---

## 2. Symbolic Dimension Identifiability Classification

Every symbolic dimension required by the 56-descriptor confirmatory feature extraction pipeline has been classified by its physical and visual identifiability from historical printed piano notation:

| Symbolic Dimension | Identifiability Class | Visual Representation in Historical Print |
|---|---|---|
| **`pitch`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Vertical staff line/space location directly determines diatonic note step. |
| **`accidental`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Printed sharp, flat, double sharp, double flat, and natural glyphs preceding noteheads. |
| **`octave`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Clef assignment (Treble/Bass) + staff position + printed ottava lines ($8^{va}$, $8^{vb}$). |
| **`onset`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Proportional horizontal layout and metric subdivision across the measure sequence. |
| **`duration`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Notehead shape (black vs white), stem presence, flags, beams, and augmentation dots. |
| **`rest`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Distinct engraved rest glyphs (whole, half, quarter, 8th, 16th, etc.). |
| **`measure_sequence`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Printed barlines, double barlines, and system progression order. |
| **`time_signature`** | `DIRECTLY_VISUALLY_IDENTIFIABLE` | Numerals/symbols ($\mathbf{C}$, $\mathbf{4/4}$, $\mathbf{3/4}$, $\mathbf{6/8}$, etc.) at piece and meter boundaries. |
| **`staff`** | `CONDITIONALLY_IDENTIFIABLE` | Visually direct for standard grand-staff notes; conditionally complex in cross-staff beaming. |
| **`tie`** | `CONDITIONALLY_IDENTIFIABLE` | Curved tie arc between identical pitches; conditionally distinguished from phrasing slurs. |
| **`voice`** | `NOT_IDENTIFIABLE_FROM_PRINT` | Internal MusicXML numeric integer (`voice=1`, `voice=2`) is an invisible data structure label; only polyphonic stem directions and beam groups are printed. |

> [!IMPORTANT]
> **Zero Descriptors Depend on Invisible Voice Integer IDs**:
> The 8 Voice-Leading descriptors (`vl_*`) operate entirely on pitch-class sets and outer-voice extrema (highest pitch = soprano proxy, lowest pitch = bass proxy) computed at distinct sounding onsets. They **do not** require internal MusicXML voice integer labels. Therefore, the non-identifiability of raw voice IDs creates **zero schema gaps**.

---

## 3. Descriptor Catalog by Family

### Family A: TONAL (8 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/tonal.py` (`extract_tonal_features`)
1. `tonal_global_confidence`: Required `[pitch, accidental, duration]` -> `MACHINE_SUPPORTED`
2. `tonal_local_confidence_mean`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
3. `tonal_local_confidence_std`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
4. `tonal_center_change_rate`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
5. `tonal_circle5_distance_mean`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
6. `tonal_circle5_distance_max`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
7. `tonal_chromatic_duration_share`: Required `[pitch, accidental, duration]` -> `MACHINE_SUPPORTED`
8. `tonal_mode_switch_rate`: Required `[pitch, accidental, duration, onset, measure_sequence]` -> `MACHINE_SUPPORTED`

### Family B: SONORITY (8 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/sonority.py` (`extract_sonority_features`)
9. `sonority_pc_cardinality_mean`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
10. `sonority_pc_cardinality_std`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
11. `sonority_change_rate`: Required `[pitch, accidental, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
12. `sonority_stable_duration_share`: Required `[pitch, accidental, onset, duration]` -> `MACHINE_SUPPORTED`
13. `sonority_ic1_semitone_share`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
14. `sonority_ic6_tritone_share`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
15. `sonority_bass_interval_variety`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
16. `sonority_harmonic_rhythm_volatility`: Required `[pitch, accidental, onset, duration]` -> `MACHINE_SUPPORTED`

### Family C: CADENCE (6 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/cadence.py` (`extract_cadence_features`)
17. `cadence_boundary_candidate_rate`: Required `[onset, duration, rest, measure_sequence]` -> `MACHINE_SUPPORTED`
18. `cadence_boundary_strength_mean`: Required `[pitch, accidental, octave, onset, duration, rest]` -> `MACHINE_SUPPORTED`
19. `cadence_tonic_resolution_rate`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
20. `cadence_dominant_tonic_proxy_rate`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
21. `cadence_deceptive_proxy_rate`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
22. `cadence_resolution_strength_mean`: Required `[pitch, accidental, octave, onset, duration]` -> `MACHINE_SUPPORTED`

### Family D: FORM (8 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/form.py` (`extract_form_features`)
23. `form_ssm_recurrence_density`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
24. `form_novelty_peak_rate`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
25. `form_novelty_mean`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
26. `form_return_late_strength`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
27. `form_recurrence_distance_mean`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
28. `form_ctu_first_occurrence_mean`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
29. `form_ctu_recurrence_dispersion`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
30. `form_ctu_late_return_presence`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`

### Family E: VOICE_LEADING (8 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/voice_leading.py` (`extract_voice_leading_features`)
31. `vl_outer_parallel_motion_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
32. `vl_outer_contrary_motion_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
33. `vl_outer_oblique_motion_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
34. `vl_soprano_step_resolution_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
35. `vl_bass_step_motion_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
36. `vl_semitone_approach_rate`: Required `[pitch, accidental, octave, onset, measure_sequence]` -> `MACHINE_SUPPORTED`
37. `vl_common_tone_retention_rate`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
38. `vl_min_voice_leading_distance_mean`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`

### Family F: TEXTURE_REGISTER (10 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/texture.py` (`extract_texture_features`)
39. `texture_register_centroid_mean`: Required `[pitch, accidental, octave]` -> `MACHINE_SUPPORTED`
40. `texture_register_centroid_std`: Required `[pitch, accidental, octave, measure_sequence]` -> `MACHINE_SUPPORTED`
41. `texture_register_span_mean`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
42. `texture_register_span_max`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
43. `texture_interstaff_gap_mean`: Required `[pitch, accidental, octave, staff, onset]` -> `PARTIALLY_SUPPORTED` (Requires staff assignment)
44. `texture_simultaneity_attack_mean`: Required `[onset]` -> `MACHINE_SUPPORTED`
45. `texture_block_chord_share`: Required `[onset]` -> `MACHINE_SUPPORTED`
46. `texture_arpeggiation_proxy_rate`: Required `[pitch, accidental, octave, onset, duration, measure_sequence]` -> `MACHINE_SUPPORTED`
47. `texture_octave_doubling_share`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
48. `texture_repeated_note_attack_rate`: Required `[pitch, accidental, octave, onset, measure_sequence]` -> `MACHINE_SUPPORTED`

### Family G: TEMPORAL_TRAJECTORY (8 Descriptors)
- Implementation: `src/russian_piano_composer/structure_analysis/trajectory.py` (`extract_trajectory_features`)
49. `traj_register_center_slope`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
50. `traj_register_span_slope`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`
51. `traj_attack_density_slope`: Required `[onset]` -> `MACHINE_SUPPORTED`
52. `traj_attack_density_curvature`: Required `[onset]` -> `MACHINE_SUPPORTED`
53. `traj_chromaticity_slope`: Required `[pitch, accidental, duration, onset]` -> `MACHINE_SUPPORTED`
54. `traj_sonority_cardinality_slope`: Required `[pitch, accidental, onset]` -> `MACHINE_SUPPORTED`
55. `traj_density_early_late_contrast`: Required `[onset]` -> `MACHINE_SUPPORTED`
56. `traj_register_volatility`: Required `[pitch, accidental, octave, onset]` -> `MACHINE_SUPPORTED`

---

## 4. Scientific Verdict on Schema Compatibility

All 56 descriptors in the frozen RC-011 contract are either fully `MACHINE_SUPPORTED` (55/56) or `PARTIALLY_SUPPORTED` (1/56). There are **no schema support gaps** and no unmodeled semantic requirements.
