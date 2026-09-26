"""Feature-Dependency and Downstream Structural Analysis Empirical Fidelity Contract for RC-013 (Protocol V4).

Maps RC-011 and RC-012 structural descriptors to their strict notation feature dependencies.
Evaluates empirical dimension reliability, coverage, and derives fit status:
FIT_FOR_RC012_STRUCTURAL_ANALYSIS, PARTIALLY_FIT_FOR_RC012_STRUCTURAL_ANALYSIS, or NOT_FIT_FOR_RC012_STRUCTURAL_ANALYSIS.
"""

from __future__ import annotations

from typing import Any

# Mapping of RC-011/RC-012 structural features to notation element dependencies
DESCRIPTOR_FEATURE_DEPENDENCY_MAP: dict[str, dict[str, Any]] = {
    "pitch_class_entropy": {
        "required_dimensions": ["pitch", "accidental", "octave"],
        "optional_dimensions": ["key_signature"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Measures distribution of spelled pitch classes; sensitive to pitch/accidental misclassification.",
    },
    "voice_leading_cross_entropy": {
        "required_dimensions": ["pitch", "accidental", "octave", "voice_staff"],
        "optional_dimensions": ["tie"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Tracks horizontal voice transitions; requires accurate voice and staff assignment.",
    },
    "harmonic_root_motion": {
        "required_dimensions": ["pitch", "accidental", "duration"],
        "optional_dimensions": ["key_signature"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Computes Roman numeral and root progression; depends on vertical pitch simultaneities.",
    },
    "metric_accent_syncopation": {
        "required_dimensions": ["duration", "time_signature"],
        "optional_dimensions": ["tuplet", "tie"],
        "fidelity_class": "CORE_SYMBOLIC_FIDELITY",
        "rationale": "Calculates metric grid alignment and offbeat syncopations.",
    },
    "phrase_boundary_density": {
        "required_dimensions": ["duration", "rest"],
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
        "required_dimensions": ["articulation"],
        "optional_dimensions": ["accent", "slur"],
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
    dimension_reliability: dict[str, dict[str, float]] | None = None,
    min_reliability_threshold: float = 0.50,
) -> dict[str, Any]:
    """Evaluates which downstream RC-011/RC-012 descriptors are supported based on extracted dimensions and empirical reliability."""
    supported_core: list[str] = []
    partially_supported_core: list[str] = []
    unsupported_core: list[str] = []
    supported_performance: list[str] = []
    unsupported_performance: list[str] = []
    descriptor_details: dict[str, Any] = {}

    for desc, details in DESCRIPTOR_FEATURE_DEPENDENCY_MAP.items():
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

        if f_class == "CORE_SYMBOLIC_FIDELITY":
            if is_name_present and empirical_pass:
                supported_core.append(desc)
                status = "SUPPORTED"
            elif is_name_present:
                partially_supported_core.append(desc)
                status = "PARTIALLY_SUPPORTED"
            else:
                unsupported_core.append(desc)
                status = "UNSUPPORTED"
        else:
            if is_name_present and empirical_pass:
                supported_performance.append(desc)
                status = "SUPPORTED"
            else:
                unsupported_performance.append(desc)
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
    elif len(supported_core) > 0 or len(partially_supported_core) > 0:
        fit_status = "PARTIALLY_FIT_FOR_RC012_STRUCTURAL_ANALYSIS"
    else:
        fit_status = "NOT_FIT_FOR_RC012_STRUCTURAL_ANALYSIS"

    return {
        "fit_status": fit_status,
        "fit_for_rc012_structural_analysis": fit_status == "FIT_FOR_RC012_STRUCTURAL_ANALYSIS",
        "supported_core_descriptors": supported_core,
        "partially_supported_core_descriptors": partially_supported_core,
        "unsupported_core_descriptors": unsupported_core,
        "supported_performance_descriptors": supported_performance,
        "unsupported_performance_descriptors": unsupported_performance,
        "descriptor_details": descriptor_details,
    }
