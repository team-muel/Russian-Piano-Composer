"""
Structural Music Representation Package (RC-011).
"""

from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    AvailabilityStatus,
    FeatureFamily,
    FeatureValue,
    InvarianceClass,
    Provenance,
    StructuralFeatureDefinition,
    compute_structural_schema_hash,
)

__all__ = [
    "AvailabilityStatus",
    "FeatureFamily",
    "FeatureValue",
    "InvarianceClass",
    "Provenance",
    "STRUCTURAL_FEATURE_CATALOG",
    "StructuralFeatureDefinition",
    "compute_structural_schema_hash",
]
