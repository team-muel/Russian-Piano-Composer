"""
Master Score Feature Extractor for RC-011 Structural Music Representation.
"""

from dataclasses import dataclass, field

from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import CTUCandidate
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.structure_analysis.cadence import (
    CadencePolicy,
    extract_cadence_features,
)
from russian_piano_composer.structure_analysis.form import FormPolicy, extract_form_features
from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    FeatureValue,
)
from russian_piano_composer.structure_analysis.sonority import (
    SonorityPolicy,
    extract_sonority_features,
)
from russian_piano_composer.structure_analysis.texture import (
    TexturePolicy,
    extract_texture_features,
)
from russian_piano_composer.structure_analysis.tonal import TonalPolicy, extract_tonal_features
from russian_piano_composer.structure_analysis.trajectory import (
    TrajectoryPolicy,
    extract_trajectory_features,
)
from russian_piano_composer.structure_analysis.voice_leading import (
    VoiceLeadingPolicy,
    extract_voice_leading_features,
)


@dataclass(frozen=True, slots=True)
class StructuralExtractionPolicy:
    """Master policy bundle for all 7 structural feature families."""

    tonal_policy: TonalPolicy = field(default_factory=TonalPolicy)
    sonority_policy: SonorityPolicy = field(default_factory=SonorityPolicy)
    cadence_policy: CadencePolicy = field(default_factory=CadencePolicy)
    form_policy: FormPolicy = field(default_factory=FormPolicy)
    vl_policy: VoiceLeadingPolicy = field(default_factory=VoiceLeadingPolicy)
    texture_policy: TexturePolicy = field(default_factory=TexturePolicy)
    trajectory_policy: TrajectoryPolicy = field(default_factory=TrajectoryPolicy)
    ctu_discovery_policy: CTUDiscoveryPolicy = field(default_factory=CTUDiscoveryPolicy)



@dataclass(frozen=True, slots=True)
class PieceStructuralRepresentation:
    """Computed structural representation for a single piece across all 56 descriptors."""

    piece_id: str
    manifest_hash: str
    features: dict[str, FeatureValue]

    def get_vector(self) -> tuple[float, ...]:
        """Return the sorted canonical feature vector of floats."""
        sorted_ids = sorted(d.feature_id for d in STRUCTURAL_FEATURE_CATALOG)
        return tuple(self.features[fid].value for fid in sorted_ids)


def extract_structural_representation(
    score: CanonicalScore,
    manifest_hash: str = "",
    policy: StructuralExtractionPolicy | None = None,
    retained_ctus: tuple[CTUCandidate, ...] | None = None,
) -> PieceStructuralRepresentation:
    """
    Extract all 56 frozen structural descriptors from a CanonicalScore.
    Operates in a strictly role-blind manner.
    """
    if policy is None:
        policy = StructuralExtractionPolicy()

    # If CTUs not provided, run frozen discovery
    if retained_ctus is None:
        disc_res = discover_ctus_for_score(
            score, manifest_hash=manifest_hash, policy=policy.ctu_discovery_policy
        )
        retained_ctus = disc_res.retained_ctus

    all_features: dict[str, FeatureValue] = {}

    all_features.update(extract_tonal_features(score, policy.tonal_policy))
    all_features.update(extract_sonority_features(score, policy.sonority_policy))
    all_features.update(extract_cadence_features(score, policy.cadence_policy))
    all_features.update(extract_form_features(score, retained_ctus=retained_ctus, policy=policy.form_policy))
    all_features.update(extract_voice_leading_features(score, policy.vl_policy))
    all_features.update(extract_texture_features(score, policy.texture_policy))
    all_features.update(extract_trajectory_features(score, policy.trajectory_policy))

    # Verify all 56 catalog features are present
    expected_ids = {d.feature_id for d in STRUCTURAL_FEATURE_CATALOG}
    actual_ids = set(all_features.keys())
    if actual_ids != expected_ids:
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        raise ValueError(f"Extracted feature mismatch! Missing: {missing}, Extra: {extra}")

    return PieceStructuralRepresentation(
        piece_id=score.piece_id,
        manifest_hash=manifest_hash,
        features=all_features,
    )
