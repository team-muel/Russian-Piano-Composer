"""Feature-Dependency and Downstream Structural Analysis Fidelity Contract for RC-013.

Maps RC-011 and RC-012 structural descriptors to their strict notation feature dependencies.
Distinguishes CORE_SYMBOLIC_FIDELITY (critical for analysis) from PERFORMANCE_NOTATION_FIDELITY.
"""

from __future__ import annotations

from typing import Any

# Mapping of RC-011/RC-012 structural features to notation element dependencies
DESCRIPTOR_FEATURE_DEPENDENCY_MAP: dict[str, dict[str, Any]] = {
    "pitch_class_entropy": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": ["clef"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Measures distribution of spelled pitch classes; sensitive to pitch/accidental misclassification.",
    },
    "voice_leading_cross_entropy": {
        "required_dimensions": ["pitch", "accidental", "octave", "voice", "staff"],
        "optional_dimensions": ["tie"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Tracks horizontal voice transitions; requires accurate voice and staff assignment.",
    },
    "harmonic_root_motion": {
        "required_dimensions": ["pitch", "accidental", "onset", "duration"],
        "optional_dimensions": ["key_signature"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Computes Roman numeral and root progression; depends on vertical pitch simultaneities.",
    },
    "metric_accent_syncopation": {
        "required_dimensions": ["onset", "duration", "time_signature", "tie"],
        "optional_dimensions": ["tuplet"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Calculates metric grid alignment and offbeat syncopations.",
    },
    "phrase_boundary_density": {
        "required_dimensions": ["onset", "duration", "rest", "measure_sequence"],
        "optional_dimensions": ["slur", "repeat_structure"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Detects cadential pauses and measure barlines.",
    },
    "dynamic_contrast_profile": {
        "required_dimensions": ["dynamic"],
        "optional_dimensions": ["hairpin"],
        "fidelity_class": "PERFORMANCE_NOTATION_FIDELITY",
        "rationale": "Performance expression markup; tracked separately from core pitch-time structural features.",
    },
    "articulation_density": {
        "required_dimensions": ["articulation", "slur", "staccato", "tenuto"],
        "optional_dimensions": ["accent"],
        "fidelity_class": "PERFORMANCE_NOTATION_FIDELITY",
        "rationale": "Surface performance nuance; not required for core pitch/rhythm grammar validation.",
    },
    "pedal_resonance_ratio": {
        "required_dimensions": ["pedal"],
        "optional_dimensions": [],
        "fidelity_class": "PERFORMANCE_NOTATION_FIDELITY",
        "rationale": "Pianistic sustain pedal markings.",
    },
}


def evaluate_feature_dependency_coverage(
    extracted_dimensions: set[str],
) -> dict[str, Any]:
    """Evaluates which downstream RC-011/RC-012 descriptors are fully supported by extracted notation dimensions."""
    supported_core: list[str] = []
    unsupported_core: list[str] = []
    supported_performance: list[str] = []
    unsupported_performance: list[str] = []

    for desc, details in DESCRIPTOR_FEATURE_DEPENDENCY_MAP.items():
        reqs = set(details["required_dimensions"])
        is_supported = reqs.issubset(extracted_dimensions)
        f_class = details["fidelity_class"]

        if f_class == "CORE_SYMBOLIC_FIDELITY":
            if is_supported:
                supported_core.append(desc)
            else:
                unsupported_core.append(desc)
        else:
            if is_supported:
                supported_performance.append(desc)
            else:
                unsupported_performance.append(desc)

    fit_for_rc012 = len(unsupported_core) == 0

    return {
        "fit_for_rc012_structural_analysis": fit_for_rc012,
        "supported_core_descriptors": supported_core,
        "unsupported_core_descriptors": unsupported_core,
        "supported_performance_descriptors": supported_performance,
        "unsupported_performance_descriptors": unsupported_performance,
    }
