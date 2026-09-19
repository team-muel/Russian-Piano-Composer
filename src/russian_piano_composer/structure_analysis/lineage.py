"""
Lineage Tracking & Scientific Provenance for RC-011 Structural Representation.

Binds Master baseline SHA, canonical manifest hash, RC-009A/B hashes,
structural schema hash, family policy hashes, matrix hash, and validation hash.
"""

import hashlib
import json
from dataclasses import dataclass

from russian_piano_composer.ctu.models import (
    compute_ctu_schema_semantic_hash,
    compute_segment_representation_semantic_hash,
    compute_similarity_semantic_hash,
)
from russian_piano_composer.domain.features import (
    compute_schema_semantic_hash as compute_rc009a_schema_hash,
)
from russian_piano_composer.features import FEATURE_REGISTRY
from russian_piano_composer.features.policy import FeatureExtractionPolicy
from russian_piano_composer.structure_analysis.extractor import StructuralExtractionPolicy
from russian_piano_composer.structure_analysis.matrix import StructuralRepresentationMatrix
from russian_piano_composer.structure_analysis.schema import compute_structural_schema_hash
from russian_piano_composer.structure_analysis.validation import ValidationResult
from russian_piano_composer.style_analysis.features import (
    ACCEPTED_RC009B_CANDIDATE_SET_HASH,
    ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
)

MASTER_BASELINE_SHA: str = "53fcecef76598c50e62d7f6cac6c86d9730cedbf"
PREREGISTRATION_COMMIT_SHA: str = "ad3299e0f36f4fb028a2f5125a88b19361504d27"


@dataclass(frozen=True, slots=True)
class StructuralRepresentationLineage:
    """Immutable lineage hash bundle for RC-011 Structural Music Representation."""

    master_baseline_sha: str
    preregistration_commit_sha: str
    manifest_hash: str
    rc009a_feature_schema_semantic_hash: str
    rc009a_feature_policy_hash: str
    rc009b_candidate_set_hash: str
    rc009b_discovery_policy_hash: str
    ctu_schema_semantic_hash: str
    representation_semantic_hash: str
    similarity_semantic_hash: str
    structural_schema_hash: str
    tonal_policy_hash: str
    sonority_policy_hash: str
    cadence_policy_hash: str
    form_policy_hash: str
    vl_policy_hash: str
    texture_policy_hash: str
    trajectory_policy_hash: str
    structural_matrix_hash: str
    validation_result_hash: str

    def compute_bundle_hash(self) -> str:
        """Deterministic SHA-256 hash of complete RC-011 lineage bundle."""
        canonical = {
            "master_baseline_sha": self.master_baseline_sha,
            "preregistration_commit_sha": self.preregistration_commit_sha,
            "manifest_hash": self.manifest_hash,
            "rc009a_feature_schema_semantic_hash": self.rc009a_feature_schema_semantic_hash,
            "rc009a_feature_policy_hash": self.rc009a_feature_policy_hash,
            "rc009b_candidate_set_hash": self.rc009b_candidate_set_hash,
            "rc009b_discovery_policy_hash": self.rc009b_discovery_policy_hash,
            "ctu_schema_semantic_hash": self.ctu_schema_semantic_hash,
            "representation_semantic_hash": self.representation_semantic_hash,
            "similarity_semantic_hash": self.similarity_semantic_hash,
            "structural_schema_hash": self.structural_schema_hash,
            "tonal_policy_hash": self.tonal_policy_hash,
            "sonority_policy_hash": self.sonority_policy_hash,
            "cadence_policy_hash": self.cadence_policy_hash,
            "form_policy_hash": self.form_policy_hash,
            "vl_policy_hash": self.vl_policy_hash,
            "texture_policy_hash": self.texture_policy_hash,
            "trajectory_policy_hash": self.trajectory_policy_hash,
            "structural_matrix_hash": self.structural_matrix_hash,
            "validation_result_hash": self.validation_result_hash,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def compute_structural_representation_lineage(
    manifest_hash: str,
    matrix: StructuralRepresentationMatrix,
    val_result: ValidationResult,
    policy: StructuralExtractionPolicy | None = None,
) -> StructuralRepresentationLineage:
    """Construct the immutable RC-011 Lineage Bundle."""
    if policy is None:
        policy = StructuralExtractionPolicy()

    return StructuralRepresentationLineage(
        master_baseline_sha=MASTER_BASELINE_SHA,
        preregistration_commit_sha=PREREGISTRATION_COMMIT_SHA,
        manifest_hash=manifest_hash,
        rc009a_feature_schema_semantic_hash=compute_rc009a_schema_hash(FEATURE_REGISTRY),
        rc009a_feature_policy_hash=FeatureExtractionPolicy().compute_policy_hash(),
        rc009b_candidate_set_hash=ACCEPTED_RC009B_CANDIDATE_SET_HASH,
        rc009b_discovery_policy_hash=ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
        ctu_schema_semantic_hash=compute_ctu_schema_semantic_hash(),
        representation_semantic_hash=compute_segment_representation_semantic_hash(),
        similarity_semantic_hash=compute_similarity_semantic_hash(),
        structural_schema_hash=compute_structural_schema_hash(),
        tonal_policy_hash=policy.tonal_policy.compute_policy_hash(),
        sonority_policy_hash=policy.sonority_policy.compute_policy_hash(),
        cadence_policy_hash=policy.cadence_policy.compute_policy_hash(),
        form_policy_hash=policy.form_policy.compute_policy_hash(),
        vl_policy_hash=policy.vl_policy.compute_policy_hash(),
        texture_policy_hash=policy.texture_policy.compute_policy_hash(),
        trajectory_policy_hash=policy.trajectory_policy.compute_policy_hash(),
        structural_matrix_hash=matrix.compute_matrix_hash(),
        validation_result_hash=val_result.validation_hash,
    )
