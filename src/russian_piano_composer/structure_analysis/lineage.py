"""
Lineage Tracking & Scientific Provenance for RC-011 Structural Representation.

Binds Master baseline SHA, canonical manifest hash, accepted RC-009A/B hashes,
structural schema hash, family policy hashes, synthetic suite hash,
invariance contract hash, amendment hash, exclusion ledger hash,
matrix hash, and validation hash.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from russian_piano_composer.ctu.models import (
    compute_ctu_schema_semantic_hash,
    compute_segment_representation_semantic_hash,
    compute_similarity_semantic_hash,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.domain.features import (
    compute_schema_semantic_hash as compute_rc009a_schema_hash,
)
from russian_piano_composer.features import FEATURE_REGISTRY
from russian_piano_composer.features.policy import FeatureExtractionPolicy
from russian_piano_composer.structure_analysis.extractor import StructuralExtractionPolicy
from russian_piano_composer.structure_analysis.matrix import StructuralRepresentationMatrix
from russian_piano_composer.structure_analysis.schema import (
    compute_invariance_contract_hash,
    compute_structural_schema_hash,
)
from russian_piano_composer.structure_analysis.validation import (
    ValidationResult,
    compute_synthetic_fixture_suite_hash,
)
from russian_piano_composer.style_analysis.features import (
    ACCEPTED_RC009B_CANDIDATE_SET_HASH,
    ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
)

MASTER_BASELINE_SHA: str = "53fcecef76598c50e62d7f6cac6c86d9730cedbf"
PREREGISTRATION_COMMIT_SHA: str = "ad3299e0f36f4fb028a2f5125a88b19361504d27"
PREREGISTRATION_AMENDMENT_1_COMMIT_SHA: str = "d9881562a9a206629544681a96b13d99a819cf56"
PREREGISTRATION_AMENDMENT_2_COMMIT_SHA: str = "973ca6eddeba03163542a6d34293e261d67f0977"


def compute_preregistration_amendment_hash(path: Path | None = None) -> str:
    """Dynamically compute SHA-256 hash of RC011_PREREGISTRATION_AMENDMENT_2.md."""
    if path is None:
        p = Path("docs/research/RC011_PREREGISTRATION_AMENDMENT_2.md")
        if not p.exists():
            p = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "research" / "RC011_PREREGISTRATION_AMENDMENT_2.md"
        path = p
    return hashlib.sha256(path.read_bytes()).hexdigest()

# Accepted prior milestone constants for fail-closed checks
ACCEPTED_CANONICAL_MANIFEST_HASH: str = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"
ACCEPTED_RC009A_SCHEMA_HASH: str = "55a388b490dda3089d3073463818edcbc60abf0bcbc9dd114cd5a28032976516"
ACCEPTED_RC009A_POLICY_HASH: str = "46ac0709d3b34b8e930b6f2d09723ca658cd7f29c204f235b0814f8c2a86150e"
ACCEPTED_RC009B_CTU_SCHEMA_HASH: str = "03e8103ae9d7d534ded951b781ee6d43269a046fc787c543029c5f9ce3dd0ec1"
ACCEPTED_RC009B_REPRESENTATION_HASH: str = "967c42a2f47e16dbc6ce3b160ff56284298c73524b46133b6df116ef06db3539"
ACCEPTED_RC009B_SIMILARITY_HASH: str = "9cdd0387050e9c4aa7025f333da975ed02e453b345ebda3622266343fdb475e2"


@dataclass(frozen=True, slots=True)
class StructuralRepresentationLineage:
    """Immutable lineage hash bundle for RC-011 Structural Music Representation."""

    master_baseline_sha: str
    preregistration_commit_sha: str
    preregistration_amendment_commit_sha: str
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
    synthetic_fixture_suite_hash: str
    assertion_contract_hash: str
    invariance_contract_hash: str
    preregistration_amendment_hash: str
    exclusion_ledger_hash: str
    structural_matrix_hash: str
    validation_result_hash: str

    def compute_bundle_hash(self) -> str:
        """Deterministic SHA-256 hash of complete RC-011 lineage bundle."""
        canonical = {
            "master_baseline_sha": self.master_baseline_sha,
            "preregistration_commit_sha": self.preregistration_commit_sha,
            "preregistration_amendment_commit_sha": self.preregistration_amendment_commit_sha,
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
            "synthetic_fixture_suite_hash": self.synthetic_fixture_suite_hash,
            "assertion_contract_hash": self.assertion_contract_hash,
            "invariance_contract_hash": self.invariance_contract_hash,
            "preregistration_amendment_hash": self.preregistration_amendment_hash,
            "exclusion_ledger_hash": self.exclusion_ledger_hash,
            "structural_matrix_hash": self.structural_matrix_hash,
            "validation_result_hash": self.validation_result_hash,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def verify_prior_milestone_hashes_fail_closed(
    manifest_hash: str,
    dynamically_computed_candidate_set_hash: str | None = None,
) -> None:
    """Assert exact equality of all prior milestone lineage hashes. Fail-closed on mismatch."""
    if manifest_hash != ACCEPTED_CANONICAL_MANIFEST_HASH:
        raise ValueError(
            f"Manifest hash mismatch: expected {ACCEPTED_CANONICAL_MANIFEST_HASH}, got {manifest_hash}"
        )

    rc009a_schema = compute_rc009a_schema_hash(FEATURE_REGISTRY)
    if rc009a_schema != ACCEPTED_RC009A_SCHEMA_HASH:
        raise ValueError(
            f"RC-009A Schema hash mismatch: expected {ACCEPTED_RC009A_SCHEMA_HASH}, got {rc009a_schema}"
        )

    rc009a_policy = FeatureExtractionPolicy().compute_policy_hash()
    if rc009a_policy != ACCEPTED_RC009A_POLICY_HASH:
        raise ValueError(
            f"RC-009A Policy hash mismatch: expected {ACCEPTED_RC009A_POLICY_HASH}, got {rc009a_policy}"
        )

    ctu_policy = CTUDiscoveryPolicy().compute_policy_hash()
    if ctu_policy != ACCEPTED_RC009B_DISCOVERY_POLICY_HASH:
        raise ValueError(
            f"RC-009B CTU Discovery Policy hash mismatch: expected {ACCEPTED_RC009B_DISCOVERY_POLICY_HASH}, got {ctu_policy}"
        )

    ctu_schema = compute_ctu_schema_semantic_hash()
    if ctu_schema != ACCEPTED_RC009B_CTU_SCHEMA_HASH:
        raise ValueError(
            f"RC-009B CTU Schema hash mismatch: expected {ACCEPTED_RC009B_CTU_SCHEMA_HASH}, got {ctu_schema}"
        )

    rep_hash = compute_segment_representation_semantic_hash()
    if rep_hash != ACCEPTED_RC009B_REPRESENTATION_HASH:
        raise ValueError(
            f"RC-009B Representation hash mismatch: expected {ACCEPTED_RC009B_REPRESENTATION_HASH}, got {rep_hash}"
        )

    sim_hash = compute_similarity_semantic_hash()
    if sim_hash != ACCEPTED_RC009B_SIMILARITY_HASH:
        raise ValueError(
            f"RC-009B Similarity hash mismatch: expected {ACCEPTED_RC009B_SIMILARITY_HASH}, got {sim_hash}"
        )

    if dynamically_computed_candidate_set_hash is not None and dynamically_computed_candidate_set_hash != ACCEPTED_RC009B_CANDIDATE_SET_HASH:
        raise ValueError(
            f"Dynamically generated RC-009B Candidate Set hash mismatch: "
            f"expected {ACCEPTED_RC009B_CANDIDATE_SET_HASH}, got {dynamically_computed_candidate_set_hash}"
        )


def compute_structural_representation_lineage(
    manifest_hash: str,
    matrix: StructuralRepresentationMatrix,
    val_result: ValidationResult,
    preregistration_amendment_hash: str | None = None,
    exclusion_ledger_hash: str = "28b142e1bbef5eeff65ee3a62a94b55e55f88841c3b5954d763d098579eac9b3",
    policy: StructuralExtractionPolicy | None = None,
    dynamically_computed_candidate_set_hash: str | None = None,
) -> StructuralRepresentationLineage:
    """Construct the immutable RC-011 Lineage Bundle with fail-closed validation."""
    if policy is None:
        policy = StructuralExtractionPolicy()

    if preregistration_amendment_hash is None:
        preregistration_amendment_hash = compute_preregistration_amendment_hash()

    verify_prior_milestone_hashes_fail_closed(manifest_hash, dynamically_computed_candidate_set_hash)

    return StructuralRepresentationLineage(
        master_baseline_sha=MASTER_BASELINE_SHA,
        preregistration_commit_sha=PREREGISTRATION_COMMIT_SHA,
        preregistration_amendment_commit_sha=PREREGISTRATION_AMENDMENT_2_COMMIT_SHA,
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
        synthetic_fixture_suite_hash=compute_synthetic_fixture_suite_hash(),
        assertion_contract_hash=val_result.assertion_contract_hash,
        invariance_contract_hash=compute_invariance_contract_hash(),
        preregistration_amendment_hash=preregistration_amendment_hash,
        exclusion_ledger_hash=exclusion_ledger_hash,
        structural_matrix_hash=matrix.compute_matrix_hash(),
        validation_result_hash=val_result.validation_hash,
    )
