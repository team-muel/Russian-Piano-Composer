"""Canonical 56-Descriptor Feature Dependency Audit for RC-011 and RC-013 (Protocol V6).

Audits the exact frozen 56-descriptor specification defined in:
docs/spec/STRUCTURAL_REPRESENTATION_SCHEMA_V1.md and
src/russian_piano_composer/structure_analysis/schema.py

Maps each descriptor to:
- feature_family (TONAL, SONORITY, CADENCE, FORM, VOICE_LEADING, TEXTURE, TRAJECTORY)
- implementation_module & function
- required symbolic dimensions
- machine identifiability classification:
  - DIRECTLY_VISUALLY_IDENTIFIABLE (pitch, accidental, octave, onset, duration, rest, measure_sequence, time_signature)
  - CONDITIONALLY_IDENTIFIABLE (staff - clean vs cross-staff; tie - clean slur/tie vs dense articulation)
  - NOT_IDENTIFIABLE_FROM_PRINT (voice integer ID - pure MusicXML metadata without engraved representation)
"""

from __future__ import annotations

from typing import Any

# Identifiability classification of symbolic dimensions
DIMENSION_IDENTIFIABILITY: dict[str, dict[str, Any]] = {
    "pitch": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Vertical staff line/space position directly determines diatonic note step.",
    },
    "accidental": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Engraved sharp, flat, or natural glyphs printed before noteheads.",
    },
    "octave": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Clef + staff line/space position + ottava brackets directly define octave register.",
    },
    "onset": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Horizontal alignment and metric subdivision within measure sequence define onset.",
    },
    "duration": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Notehead fill (black/white), stem, flags, beams, and augmentation dots directly define duration.",
    },
    "rest": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Engraved rest glyphs (whole, half, quarter, eighth, etc.) directly define rest durations.",
    },
    "measure_sequence": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Barlines and system reading order directly establish measure progression.",
    },
    "time_signature": {
        "status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "description": "Meter glyphs / numerals printed at score and section starts.",
    },
    "staff": {
        "status": "CONDITIONALLY_IDENTIFIABLE",
        "description": "Staff assignment (upper vs lower) is visually direct in ordinary notation, but conditionally ambiguous in cross-staff beaming.",
    },
    "tie": {
        "status": "CONDITIONALLY_IDENTIFIABLE",
        "description": "Curved tie arc between identical pitches is visually present, but conditionally ambiguous with phrasing slurs.",
    },
    "voice": {
        "status": "NOT_IDENTIFIABLE_FROM_PRINT",
        "description": "MusicXML voice integer (voice=1, voice=2) is an invisible serialization label; only stem direction and beam groupings are printed.",
    },
}

# The authoritative 56-descriptor feature dependency catalog from STRUCTURAL_REPRESENTATION_SCHEMA_V1.md
FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG: dict[str, dict[str, Any]] = {
    # 1. TONAL (8 descriptors) - src/russian_piano_composer/structure_analysis/tonal.py
    "tonal_global_confidence": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Global Krumhansl-Kessler correlation over pitch-class duration distribution.",
    },
    "tonal_local_confidence_mean": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean local key correlation across 8-measure sliding windows.",
    },
    "tonal_local_confidence_std": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Standard deviation of local key correlations across windows.",
    },
    "tonal_center_change_rate": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Frequency of estimated key changes per measure across sliding windows.",
    },
    "tonal_circle5_distance_mean": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean fifths distance between successive key estimations.",
    },
    "tonal_circle5_distance_max": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Maximum fifths distance between successive key estimations.",
    },
    "tonal_chromatic_duration_share": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Fraction of sounding duration belonging to non-diatonic chromatic pitches.",
    },
    "tonal_mode_switch_rate": {
        "family": "TONAL",
        "implementation_module": "src/russian_piano_composer/structure_analysis/tonal.py",
        "implementation_function": "extract_tonal_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Frequency of major/minor mode transitions per measure.",
    },

    # 2. SONORITY (8 descriptors) - src/russian_piano_composer/structure_analysis/sonority.py
    "sonority_pc_cardinality_mean": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean number of distinct pitch classes sounding at unique attack onsets.",
    },
    "sonority_pc_cardinality_std": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Standard deviation of pitch-class set cardinalities across attack onsets.",
    },
    "sonority_change_rate": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of pitch-class set transitions per measure.",
    },
    "sonority_stable_duration_share": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset", "duration"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of sounding duration occupied by stable harmonic sonorities.",
    },
    "sonority_ic1_semitone_share": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of vertical interval dyads having interval class 1 (semitone/major seventh).",
    },
    "sonority_ic6_tritone_share": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of vertical interval dyads having interval class 6 (tritone).",
    },
    "sonority_bass_interval_variety": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Variety of interval classes formed above the lowest sounding pitch at each onset.",
    },
    "sonority_harmonic_rhythm_volatility": {
        "family": "SONORITY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/sonority.py",
        "implementation_function": "extract_sonority_features",
        "required_dimensions": ["pitch", "accidental", "onset", "duration"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Standard deviation of inter-harmonic-change durations.",
    },

    # 3. CADENCE (6 descriptors) - src/russian_piano_composer/structure_analysis/cadence.py
    "cadence_boundary_candidate_rate": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["onset", "duration", "rest", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Frequency of phrase boundary candidates identified by rest gaps or long durations.",
    },
    "cadence_boundary_strength_mean": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "rest"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean metric and harmonic strength score across phrase boundaries.",
    },
    "cadence_tonic_resolution_rate": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of cadential resolutions arriving on tonic harmony per measure.",
    },
    "cadence_dominant_tonic_proxy_rate": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of authentic V-I / dominant-tonic cadential motions per measure.",
    },
    "cadence_deceptive_proxy_rate": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of deceptive V-vi cadential motions per measure.",
    },
    "cadence_resolution_strength_mean": {
        "family": "CADENCE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/cadence.py",
        "implementation_function": "extract_cadence_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean harmonic resolution strength score across detected cadential events.",
    },

    # 4. FORM (8 descriptors) - src/russian_piano_composer/structure_analysis/form.py
    "form_ssm_recurrence_density": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Density of off-diagonal recurrence in Self-Similarity Matrix across measures.",
    },
    "form_novelty_peak_rate": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of structural novelty peaks along SSM checkerboard kernel per measure.",
    },
    "form_novelty_mean": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean structural novelty score across piece timeline.",
    },
    "form_return_late_strength": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Similarity score between exposition material and final third reprise.",
    },
    "form_recurrence_distance_mean": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean distance in measures between recurring thematic segments.",
    },
    "form_ctu_first_occurrence_mean": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean normalized timeline position where thematic CTU units first appear.",
    },
    "form_ctu_recurrence_dispersion": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Dispersion of CTU unit recurrences throughout the score.",
    },
    "form_ctu_late_return_presence": {
        "family": "FORM",
        "implementation_module": "src/russian_piano_composer/structure_analysis/form.py",
        "implementation_function": "extract_form_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Binary indicator of whether initial thematic CTU recurs in the final third.",
    },

    # 5. VOICE_LEADING (8 descriptors) - src/russian_piano_composer/structure_analysis/voice_leading.py
    "vl_outer_parallel_motion_share": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of outer-voice motions where soprano and bass move in parallel intervals.",
    },
    "vl_outer_contrary_motion_share": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of outer-voice motions where soprano and bass move in contrary motion.",
    },
    "vl_outer_oblique_motion_share": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of outer-voice motions where one voice sustains while the other moves.",
    },
    "vl_soprano_step_resolution_share": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of highest-voice melodic motions that proceed stepwise (<= 2 semitones).",
    },
    "vl_bass_step_motion_share": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of lowest-voice bass motions that proceed stepwise (<= 2 semitones).",
    },
    "vl_semitone_approach_rate": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Frequency of semitone (leading tone / chromatic) melodic approaches per measure.",
    },
    "vl_common_tone_retention_rate": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Frequency with which at least one pitch class is retained across consecutive onsets.",
    },
    "vl_min_voice_leading_distance_mean": {
        "family": "VOICE_LEADING",
        "implementation_module": "src/russian_piano_composer/structure_analysis/voice_leading.py",
        "implementation_function": "extract_voice_leading_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean minimal voice-leading distance (Tymoczko optimal bipartite transport metric).",
    },

    # 6. TEXTURE_REGISTER (10 descriptors) - src/russian_piano_composer/structure_analysis/texture.py
    "texture_register_centroid_mean": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean MIDI pitch across all sounding note attacks.",
    },
    "texture_register_centroid_std": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Standard deviation of measure-level registral pitch centroids.",
    },
    "texture_register_span_mean": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean vertical pitch span (highest minus lowest pitch) at each sounding onset.",
    },
    "texture_register_span_max": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Maximum vertical pitch span observed across the score.",
    },
    "texture_interstaff_gap_mean": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "staff", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "CONDITIONALLY_IDENTIFIABLE",
        "support_status": "PARTIALLY_SUPPORTED",
        "rationale": "Mean pitch clearance between staff 1 lowest note and staff 2 highest note (depends on staff assignment).",
    },
    "texture_simultaneity_attack_mean": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Mean number of simultaneous note attacks per onset.",
    },
    "texture_block_chord_share": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of onsets featuring 3 or more simultaneous note attacks.",
    },
    "texture_arpeggiation_proxy_rate": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "duration", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of unidirectional arpeggiated runs exceeding one octave per measure.",
    },
    "texture_octave_doubling_share": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Proportion of onsets containing octave-doubled pitch classes.",
    },
    "texture_repeated_note_attack_rate": {
        "family": "TEXTURE",
        "implementation_module": "src/russian_piano_composer/structure_analysis/texture.py",
        "implementation_function": "extract_texture_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset", "measure_sequence"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Rate of rapid repeated note attacks on the exact same pitch per measure.",
    },

    # 7. TEMPORAL_TRAJECTORY (8 descriptors) - src/russian_piano_composer/structure_analysis/trajectory.py
    "traj_register_center_slope": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Linear slope of pitch registral centroid over piece timeline.",
    },
    "traj_register_span_slope": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Linear slope of vertical register span over piece timeline.",
    },
    "traj_attack_density_slope": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Linear slope of note attack density over piece timeline.",
    },
    "traj_attack_density_curvature": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Quadratic curvature parameter of note attack density profile.",
    },
    "traj_chromaticity_slope": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["pitch", "accidental", "duration", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Linear slope of non-diatonic chromatic duration share over piece timeline.",
    },
    "traj_sonority_cardinality_slope": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["pitch", "accidental", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Linear slope of harmonic pitch-class cardinality over piece timeline.",
    },
    "traj_density_early_late_contrast": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Contrast difference in attack density between first third and final third of piece.",
    },
    "traj_register_volatility": {
        "family": "TRAJECTORY",
        "implementation_module": "src/russian_piano_composer/structure_analysis/trajectory.py",
        "implementation_function": "extract_trajectory_features",
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "identifiability_status": "DIRECTLY_VISUALLY_IDENTIFIABLE",
        "support_status": "MACHINE_SUPPORTED",
        "rationale": "Standard deviation of pitch registral movements across windowed segments.",
    },
}


def audit_56_descriptor_dependencies() -> dict[str, Any]:
    """Evaluates full coverage and support statistics for all 56 RC-011 structural descriptors."""
    total = len(FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG)
    supported_count = sum(
        1 for d in FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG.values() if d["support_status"] == "MACHINE_SUPPORTED"
    )
    partial_count = sum(
        1 for d in FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG.values() if d["support_status"] == "PARTIALLY_SUPPORTED"
    )
    unsupported_count = sum(
        1 for d in FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG.values() if d["support_status"] == "UNSUPPORTED"
    )

    all_dims: set[str] = set()
    for d in FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG.values():
        all_dims.update(d["required_dimensions"])

    return {
        "schema_descriptor_count": total,
        "machine_supported_count": supported_count,
        "partially_supported_count": partial_count,
        "unsupported_count": unsupported_count,
        "support_rate": round(supported_count / total, 4),
        "required_symbolic_dimensions": sorted(all_dims),
        "dimension_identifiability": DIMENSION_IDENTIFIABILITY,
        "descriptors": FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG,
    }


def evaluate_feature_dependency_coverage(
    extracted_dimensions: set[str] | list[str],
) -> dict[str, Any]:
    """Evaluates which downstream RC-011/RC-012 descriptors are supported by extracted notation dimensions."""
    extracted_set = set(extracted_dimensions)

    # Combined catalog of 56 schema descriptors plus legacy style features
    descriptor_map: dict[str, list[str]] = {
        k: v["required_dimensions"] for k, v in FROZEN_56_DESCRIPTOR_DEPENDENCY_CATALOG.items()
    }
    # Add legacy style descriptors tested in compatibility suite
    descriptor_map.update({
        "pitch_class_entropy": ["pitch", "accidental", "octave"],
        "pitch_range_semitones": ["pitch", "accidental", "octave"],
        "ctu_discovery_score_mean": ["pitch", "accidental", "octave", "duration", "onset"],
        "density_notes_per_measure": ["onset", "duration"],
        "density_staff_count": ["staff"],
        "voice_leading_cross_entropy": ["pitch", "accidental", "octave", "voice", "staff"],
        "harmonic_root_motion": ["pitch", "accidental", "duration"],
        "metric_accent_syncopation": ["duration", "time_signature"],
        "phrase_boundary_density": ["duration", "rest"],
    })

    supported_core: list[str] = []
    unsupported_core: list[str] = []

    for desc, reqs in descriptor_map.items():
        if set(reqs).issubset(extracted_set):
            supported_core.append(desc)
        else:
            unsupported_core.append(desc)

    fit_for_rc012 = len(unsupported_core) == 0

    return {
        "fit_status": "FIT_FOR_RC012_STRUCTURAL_ANALYSIS" if fit_for_rc012 else "NOT_FIT_FOR_RC012_STRUCTURAL_ANALYSIS",
        "fit_for_rc012_structural_analysis": fit_for_rc012,
        "supported_core_descriptors": supported_core,
        "unsupported_core_descriptors": unsupported_core,
    }

