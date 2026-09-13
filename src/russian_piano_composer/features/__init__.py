"""
Unified feature extraction package for objective descriptive music science.

Provides a single entry point ``extract_piece_features()`` that delegates
to all registered feature extractors and returns a ``PieceFeatureSet``.
"""
from russian_piano_composer.domain.features import (
    FeatureDefinition,
    PieceFeatureSet,
)
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.features.contour_features import (
    CONTOUR_FEATURE_DEFINITIONS,
    extract_contour_features,
)
from russian_piano_composer.features.density_features import (
    DENSITY_FEATURE_DEFINITIONS,
    extract_density_features,
)
from russian_piano_composer.features.interval_features import (
    INTERVAL_FEATURE_DEFINITIONS,
    extract_interval_features,
)
from russian_piano_composer.features.meter_features import (
    METER_FEATURE_DEFINITIONS,
    extract_meter_features,
)
from russian_piano_composer.features.pitch_features import (
    PITCH_FEATURE_DEFINITIONS,
    extract_pitch_features,
)
from russian_piano_composer.features.policy import FeatureExtractionPolicy
from russian_piano_composer.features.rhythm_features import (
    RHYTHM_FEATURE_DEFINITIONS,
    extract_rhythm_features,
)

# Canonical ordering of all feature definitions
FEATURE_REGISTRY: tuple[FeatureDefinition, ...] = (
    *PITCH_FEATURE_DEFINITIONS,
    *INTERVAL_FEATURE_DEFINITIONS,
    *RHYTHM_FEATURE_DEFINITIONS,
    *CONTOUR_FEATURE_DEFINITIONS,
    *DENSITY_FEATURE_DEFINITIONS,
    *METER_FEATURE_DEFINITIONS,
)


def extract_piece_features(
    score: CanonicalScore,
    manifest_hash: str,
    policy: FeatureExtractionPolicy | None = None,
) -> PieceFeatureSet:
    """
    Extract all registered features from a single canonical score.

    Returns an immutable PieceFeatureSet with provenance and policy binding.
    """
    if policy is None:
        policy = FeatureExtractionPolicy()

    features: dict[str, float | int | None] = {}

    features.update(extract_pitch_features(score))
    features.update(extract_interval_features(score))
    features.update(extract_rhythm_features(score))
    features.update(extract_contour_features(score))
    features.update(extract_density_features(score))
    features.update(extract_meter_features(score))

    return PieceFeatureSet(
        piece_id=score.piece_id,
        corpus_id=score.corpus_id,
        corpus_role=score.corpus_role.value,
        features=features,
        manifest_hash=manifest_hash,
        canonical_piece_hash=score.compute_piece_hash(),
        feature_policy_hash=policy.compute_policy_hash(),
    )


__all__ = [
    "FEATURE_REGISTRY",
    "extract_piece_features",
]
