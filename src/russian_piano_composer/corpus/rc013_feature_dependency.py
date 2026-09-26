"""Feature-Dependency and Downstream Structural Analysis Fidelity Contract for RC-013 (Protocol V5).

Comprehensive audit of all 53 registered RC-011 and RC-012 structural descriptors (Category A piece
features and Category B CTU style features) mapped to their exact symbolic notation requirements.
Evaluates empirical dimension reliability, coverage, and derives fit status:
FIT_FOR_RC012_STRUCTURAL_ANALYSIS, PARTIALLY_FIT_FOR_RC012_STRUCTURAL_ANALYSIS, or NOT_FIT_FOR_RC012_STRUCTURAL_ANALYSIS.
"""

from __future__ import annotations

from typing import Any

# Comprehensive Audit of all 53 RC-011 / RC-012 Descriptors and their notation dependencies
FULL_DESCRIPTOR_FEATURE_DEPENDENCY_MAP: dict[str, dict[str, Any]] = {
    # 1. Pitch Category A Features (8 descriptors)
    "pitch_range_semitones": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "max(midi) - min(midi) across note attacks.",
    },
    "pitch_mean_midi": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Arithmetic mean of MIDI note numbers.",
    },
    "pitch_std_midi": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of MIDI note numbers.",
    },
    "pitch_median_midi": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Median MIDI pitch value.",
    },
    "pitch_class_entropy": {
        "required_dimensions": ["pitch", "accidental"],
        "optional_dimensions": ["key_signature"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Shannon entropy across 12 chromatic pitch classes.",
    },
    "pitch_class_count": {
        "required_dimensions": ["pitch", "accidental"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Number of distinct pitch classes present.",
    },
    "pitch_lowest_midi": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Lowest MIDI pitch in score.",
    },
    "pitch_highest_midi": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Highest MIDI pitch in score.",
    },

    # 2. Interval Category A Features (7 descriptors)
    "interval_mean_abs_semitones": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean consecutive melodic interval size.",
    },
    "interval_std_abs_semitones": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of melodic interval sizes.",
    },
    "interval_max_abs_semitones": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Largest melodic leap in semitones.",
    },
    "interval_leap_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Ratio of melodic leaps (> 2 semitones) to all intervals.",
    },
    "interval_step_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Ratio of stepwise intervals (1-2 semitones) to all intervals.",
    },
    "interval_direction_change_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Frequency of melodic direction reversals.",
    },
    "interval_unison_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Ratio of pitch repetitions to all intervals.",
    },

    # 3. Rhythm Category A Features (8 descriptors)
    "rhythm_duration_mean": {
        "required_dimensions": ["duration"],
        "optional_dimensions": ["tie"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean note attack duration in quarter lengths.",
    },
    "rhythm_duration_std": {
        "required_dimensions": ["duration"],
        "optional_dimensions": ["tie"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of note attack durations.",
    },
    "rhythm_duration_median": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Median duration in quarter lengths.",
    },
    "rhythm_distinct_durations": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Count of distinct duration values.",
    },
    "rhythm_dotted_ratio": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Proportion of dotted rhythmic values.",
    },
    "rhythm_shortest_duration": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Shortest duration in score.",
    },
    "rhythm_longest_duration": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Longest duration in score.",
    },
    "rhythm_duration_range_ratio": {
        "required_dimensions": ["duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Ratio of longest to shortest duration.",
    },

    # 4. Contour Category A Features (4 descriptors)
    "contour_ascending_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Proportion of rising melodic segments.",
    },
    "contour_descending_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Proportion of falling melodic segments.",
    },
    "contour_repeat_ratio": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Proportion of stationary contour points.",
    },
    "contour_arc_score": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Arch-like polynomial contour curvature score.",
    },

    # 5. Density & Polyphony Category A Features (7 descriptors)
    "density_notes_per_measure": {
        "required_dimensions": ["onset", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean note count per measure.",
    },
    "density_events_per_measure": {
        "required_dimensions": ["onset", "rest", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean note+rest event count per measure.",
    },
    "density_notes_per_quarter": {
        "required_dimensions": ["onset", "duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Note attack density per quarter note pulse.",
    },
    "density_rest_ratio": {
        "required_dimensions": ["rest", "duration"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Rest duration fraction of total duration.",
    },
    "density_grace_note_ratio": {
        "required_dimensions": ["onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Proportion of grace note attacks.",
    },
    "density_staff_count": {
        "required_dimensions": ["staff"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Number of active staves.",
    },
    "density_voice_count": {
        "required_dimensions": ["voice", "staff"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Number of distinct voices across staves.",
    },

    # 6. Meter Category A Features (5 descriptors)
    "meter_primary_numerator": {
        "required_dimensions": ["time_signature"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Primary meter beat count.",
    },
    "meter_primary_denominator": {
        "required_dimensions": ["time_signature"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Primary meter beat division.",
    },
    "meter_change_count": {
        "required_dimensions": ["time_signature", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Count of time signature changes.",
    },
    "meter_has_pickup": {
        "required_dimensions": ["duration", "time_signature", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Detection of anacrusis / pickup measure.",
    },
    "meter_total_measures": {
        "required_dimensions": ["measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Total measure count in score.",
    },

    # 7. CTU Style Category B Features (14 descriptors)
    "ctu_discovery_score_mean": {
        "required_dimensions": ["pitch", "accidental", "duration", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean discovery score of extracted Characteristic Thematic Units.",
    },
    "ctu_discovery_score_std": {
        "required_dimensions": ["pitch", "accidental", "duration", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of CTU discovery scores.",
    },
    "ctu_discovery_score_max": {
        "required_dimensions": ["pitch", "accidental", "duration", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Maximum CTU saliency score.",
    },
    "ctu_span_length_mean": {
        "required_dimensions": ["duration", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Average measure span of retained CTUs.",
    },
    "ctu_span_length_std": {
        "required_dimensions": ["duration", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of CTU measure spans.",
    },
    "ctu_melodic_abs_interval_mean": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean absolute melodic step within CTU motifs.",
    },
    "ctu_melodic_interval_diversity": {
        "required_dimensions": ["pitch", "accidental", "octave", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Interval entropy / distinct interval ratio within CTUs.",
    },
    "ctu_rhythm_ratio_abs_deviation_mean": {
        "required_dimensions": ["duration", "onset"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Rhythmic ratio deviation within CTU structures.",
    },
    "ctu_texture_attack_mean": {
        "required_dimensions": ["onset", "staff", "voice"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Mean simultaneous attacks during CTU playback.",
    },
    "ctu_texture_attack_std": {
        "required_dimensions": ["onset", "staff", "voice"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Standard deviation of texture density in CTUs.",
    },
    "ctu_pitchclass_entropy": {
        "required_dimensions": ["pitch", "accidental"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Pitch class entropy restricted to CTU boundaries.",
    },
    "ctu_pitchclass_max_share": {
        "required_dimensions": ["pitch", "accidental"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Prominence of modal tonic / dominant pitch class in CTUs.",
    },
    "ctu_active_voice_stream_mean": {
        "required_dimensions": ["voice", "staff"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Average polyphonic voice count within thematic units.",
    },
    "ctu_attack_density_per_measure_mean": {
        "required_dimensions": ["onset", "measure_sequence"],
        "optional_dimensions": [],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Thematic attack density per measure.",
    },
}

# Aliases for backward-compatibility
DESCRIPTOR_FEATURE_DEPENDENCY_MAP = FULL_DESCRIPTOR_FEATURE_DEPENDENCY_MAP


def evaluate_feature_dependency_coverage(
    extracted_dimensions: set[str],
    dimension_reliability: dict[str, dict[str, float]] | None = None,
    min_reliability_threshold: float = 0.50,
) -> dict[str, Any]:
    """Evaluates which downstream RC-011/RC-012 descriptors are supported based on extracted dimensions and empirical reliability."""
    supported_core: list[str] = []
    partially_supported_core: list[str] = []
    unsupported_core: list[str] = []
    descriptor_details: dict[str, Any] = {}

    for desc, details in FULL_DESCRIPTOR_FEATURE_DEPENDENCY_MAP.items():
        reqs = set(details["required_dimensions"])
        is_name_present = reqs.issubset(extracted_dimensions)
        f_class = details["fidelity_class"]

        # Check empirical reliability if provided
        empirical_pass = True
        dimension_scores: dict[str, float] = {}
        if dimension_reliability:
            for r in reqs:
                if r in dimension_reliability:
                    rec = dimension_reliability[r].get("recall", 0.0)
                    dimension_scores[r] = rec
                    if rec < min_reliability_threshold:
                        empirical_pass = False
                else:
                    dimension_scores[r] = 0.0
                    empirical_pass = False
        else:
            dimension_scores = {r: 1.0 for r in reqs}

        if is_name_present and empirical_pass:
            supported_core.append(desc)
            status = "MACHINE_SUPPORTED"
        elif is_name_present:
            partially_supported_core.append(desc)
            status = "PARTIALLY_SUPPORTED"
        else:
            unsupported_core.append(desc)
            status = "UNSUPPORTED"

        descriptor_details[desc] = {
            "fidelity_class": f_class,
            "status": status,
            "required_dimensions": list(reqs),
            "dimension_reliability": dimension_scores,
            "rationale": details["rationale"],
        }

    if len(unsupported_core) == 0 and len(partially_supported_core) == 0:
        fit_status = "FIT_FOR_RC012_STRUCTURAL_ANALYSIS"
    elif len(supported_core) > 0:
        fit_status = "PARTIALLY_FIT_FOR_RC012_STRUCTURAL_ANALYSIS"
    else:
        fit_status = "NOT_FIT_FOR_RC012_STRUCTURAL_ANALYSIS"

    return {
        "fit_status": fit_status,
        "fit_for_rc012_structural_analysis": fit_status == "FIT_FOR_RC012_STRUCTURAL_ANALYSIS",
        "total_descriptors_audited": len(FULL_DESCRIPTOR_FEATURE_DEPENDENCY_MAP),
        "supported_core_descriptors": supported_core,
        "partially_supported_core_descriptors": partially_supported_core,
        "unsupported_core_descriptors": unsupported_core,
        "descriptor_details": descriptor_details,
    }
