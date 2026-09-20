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
PREREGISTRATION_AMENDMENT_3_COMMIT_SHA: str = "9495e1f8559a195bbac55f86984fad372383c2f0"
RC011_IMPLEMENTATION_COMMIT_SHA: str = "316ddf208ca814b3a20a067448886c393781867f"


def get_rc011_implementation_commit_sha(sha: str | None = None) -> str:
    """Get the implementation commit SHA bound to this RC-011 release."""
    if sha is not None:
        return sha
    return RC011_IMPLEMENTATION_COMMIT_SHA


def compute_preregistration_amendment_hash(path: Path | None = None) -> str:
    """Dynamically compute SHA-256 hash of RC011_PREREGISTRATION_AMENDMENT_3.md with canonical line-ending normalization."""
    if path is None:
        p = Path("docs/research/RC011_PREREGISTRATION_AMENDMENT_3.md")
        if not p.exists():
            p = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "research" / "RC011_PREREGISTRATION_AMENDMENT_3.md"
        path = p
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def compute_exclusion_ledger_hash(path: Path | None = None) -> str:
    """Dynamically compute SHA-256 hash of RC011_EXCLUSION_LEDGER.md with canonical line-ending normalization."""
    if path is None:
        p = Path("docs/research/RC011_EXCLUSION_LEDGER.md")
        if not p.exists():
            p = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "research" / "RC011_EXCLUSION_LEDGER.md"
        path = p
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Deep Algorithm Semantic Hashes for All 7 Theoretical Families
# ---------------------------------------------------------------------------

def compute_tonal_semantic_hash() -> str:
    """Deterministic hash of Family A algorithm operational semantics."""
    canonical = {
        "family": "TONAL",
        "semantic_version": "1.0.0",
        "key_profile_model": "krumhansl_schmuckler_temperley_hybrid",
        "major_profile": [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
        "minor_profile": [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
        "local_window_measures": 8,
        "step_size_measures": 2,
        "chromatic_threshold": 0.05,
        "circle5_distance_metric": "shortest_path_circle_of_fifths",
        "mode_switch_rule": "mode_difference_across_adjacent_local_windows",
        "availability_rules": {
            "minimum_measures": 1,
            "insufficient_notes_policy": "UNAVAILABLE",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_sonority_semantic_hash() -> str:
    """Deterministic hash of Family B algorithm operational semantics."""
    canonical = {
        "family": "SONORITY",
        "semantic_version": "1.0.0",
        "pc_cardinality_definition": "distinct_pitch_classes_per_sounding_slice",
        "sounding_slice_formation": "onset_and_release_time_slices",
        "interval_class_vector": "standard_forte_ic1_to_ic6",
        "bass_interval_variety": "unique_intervals_above_lowest_sounding_pitch",
        "harmonic_change_rate": "proportion_of_slices_with_pc_set_change",
        "harmonic_rhythm_volatility": "std_of_durations_between_sonority_changes",
        "availability_rules": {
            "minimum_slices": 1,
            "no_notes_policy": "UNAVAILABLE",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_cadence_semantic_hash() -> str:
    """Deterministic hash of Family C algorithm operational semantics."""
    canonical = {
        "family": "CADENCE",
        "semantic_version": "1.0.0",
        "boundary_criteria": {
            "local_ioi_lengthening_window": "measure_based",
            "ioi_ratio_threshold": 1.5,
            "rest_gap_threshold_quarters": 0.5,
            "metric_accent_weight": "downbeat_preference",
        },
        "resolution_rules": {
            "local_tonic_estimation": "local_window_key_center",
            "authentic_motion": "scale_degree_5_to_1_or_7_to_1",
            "deceptive_motion": "scale_degree_5_to_6",
            "non_cadential_fourth_fifth_suppression": True,
        },
        "availability_rules": {
            "zero_candidates_policy": "STRUCTURAL_ZERO",
            "zero_measures_policy": "UNAVAILABLE",
        },
        "invariance_contract": {
            "time_dilation": "SENSITIVE_BY_DESIGN_REST_THRESHOLD",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_form_semantic_hash() -> str:
    """Deterministic hash of Family D algorithm operational semantics."""
    canonical = {
        "family": "FORM",
        "semantic_version": "1.0.0",
        "ssm_representation": "12_dimensional_chroma_cosine_similarity",
        "novelty_kernel": "checkerboard_gaussian_derivative",
        "recurrence_density_threshold": 0.7,
        "ctu_matching": {
            "algorithm": "full_piece_occurrence_scanning",
            "overlap_handling": "pairwise_non_overlapping_suppression",
            "recapitulation_late_return_threshold": 0.67,
        },
        "availability_rules": {
            "dispersion_minimum_occurrences": 2,
            "fewer_than_minimum_policy": "STRUCTURAL_ZERO",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_voice_leading_semantic_hash() -> str:
    """Deterministic hash of Family E algorithm operational semantics."""
    canonical = {
        "family": "VOICE_LEADING",
        "semantic_version": "1.0.0",
        "outer_voice_motion": "soprano_bass_directed_intervals",
        "motion_classes": ["parallel", "contrary", "oblique", "similar"],
        "minimal_voice_leading_distance": {
            "framework": "tymoczko_geometric_voice_leading",
            "unequal_cardinality_expansion": "lcm_multiset_expansion",
            "assignment_algorithm": "scipy_linear_sum_assignment",
            "metric": "l1_pitch_class_modular_distance",
            "normalization": "divided_by_lcm_cardinality",
            "symmetry": "strictly_symmetric_d_A_B_equals_d_B_A",
        },
        "step_motion_threshold_semitones": 2,
        "semitone_approach_interval": 1,
        "common_tone_retention": "intersection_over_union_of_pitch_classes",
        "availability_rules": {
            "minimum_transitions": 1,
            "insufficient_notes_policy": "UNAVAILABLE",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_texture_semantic_hash() -> str:
    """Deterministic hash of Family F algorithm operational semantics."""
    canonical = {
        "family": "TEXTURE_REGISTER",
        "semantic_version": "1.0.0",
        "registral_centroids": "mean_and_std_of_sounding_midi_pitches",
        "registral_span": "max_minus_min_sounding_pitch",
        "interstaff_gap": "min_staff1_pitch_minus_max_staff2_pitch",
        "simultaneity_attack": "number_of_notes_per_unique_onset",
        "block_chord_threshold_notes": 3,
        "arpeggiation_proxy": {
            "max_ioi_quarters": 0.5,
            "minimum_consecutive_notes": 3,
            "contour_consistency": "monotonic_pitch_direction",
        },
        "repeated_note_proxy": {
            "max_ioi_quarters": 0.5,
            "identical_pitch_requirement": True,
        },
        "octave_doubling_interval": 12,
        "availability_rules": {
            "empty_score_policy": "UNAVAILABLE",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_trajectory_semantic_hash() -> str:
    """Deterministic hash of Family G algorithm operational semantics."""
    canonical = {
        "family": "TEMPORAL_TRAJECTORY",
        "semantic_version": "1.0.0",
        "bin_count": 8,
        "partitioning": "normalized_score_position_equal_bins",
        "linear_slope": "least_squares_regression_slope",
        "quadratic_curvature": "second_degree_polynomial_coefficient",
        "volatility": "sample_standard_deviation_across_bins",
        "early_late_contrast": "mean_bins_6_7_minus_mean_bins_0_1",
        "availability_rules": {
            "unpopulated_bins_policy": "STRUCTURAL_ZERO",
            "insufficient_notes_policy": "UNAVAILABLE",
        },
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_structure_analysis_source_hash(package_dir: Path | None = None) -> str:
    """Deterministic SHA-256 hash of canonical normalized source bytes for the 9 core modules."""
    p = Path(__file__).resolve().parent if package_dir is None else package_dir
    modules = [
        "cadence.py",
        "extractor.py",
        "form.py",
        "schema.py",
        "sonority.py",
        "texture.py",
        "tonal.py",
        "trajectory.py",
        "voice_leading.py",
    ]
    hasher = hashlib.sha256()
    for mod_name in sorted(modules):
        mod_path = p / mod_name
        content = mod_path.read_bytes().replace(b"\r\n", b"\n")
        hasher.update(mod_name.encode("utf-8"))
        hasher.update(b":")
        hasher.update(hashlib.sha256(content).digest())
    return hasher.hexdigest()


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
    rc011_implementation_commit_sha: str
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
    tonal_semantic_hash: str
    sonority_semantic_hash: str
    cadence_semantic_hash: str
    form_semantic_hash: str
    vl_semantic_hash: str
    texture_semantic_hash: str
    trajectory_semantic_hash: str
    synthetic_fixture_suite_hash: str
    assertion_contract_hash: str
    invariance_contract_hash: str
    metamorphic_test_matrix_hash: str
    structure_analysis_source_hash: str
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
            "rc011_implementation_commit_sha": self.rc011_implementation_commit_sha,
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
            "tonal_semantic_hash": self.tonal_semantic_hash,
            "sonority_semantic_hash": self.sonority_semantic_hash,
            "cadence_semantic_hash": self.cadence_semantic_hash,
            "form_semantic_hash": self.form_semantic_hash,
            "vl_semantic_hash": self.vl_semantic_hash,
            "texture_semantic_hash": self.texture_semantic_hash,
            "trajectory_semantic_hash": self.trajectory_semantic_hash,
            "synthetic_fixture_suite_hash": self.synthetic_fixture_suite_hash,
            "assertion_contract_hash": self.assertion_contract_hash,
            "invariance_contract_hash": self.invariance_contract_hash,
            "metamorphic_test_matrix_hash": self.metamorphic_test_matrix_hash,
            "structure_analysis_source_hash": self.structure_analysis_source_hash,
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
    rc011_implementation_commit_sha: str | None = None,
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
        preregistration_amendment_commit_sha=PREREGISTRATION_AMENDMENT_3_COMMIT_SHA,
        rc011_implementation_commit_sha=get_rc011_implementation_commit_sha(rc011_implementation_commit_sha),
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
        tonal_semantic_hash=compute_tonal_semantic_hash(),
        sonority_semantic_hash=compute_sonority_semantic_hash(),
        cadence_semantic_hash=compute_cadence_semantic_hash(),
        form_semantic_hash=compute_form_semantic_hash(),
        vl_semantic_hash=compute_voice_leading_semantic_hash(),
        texture_semantic_hash=compute_texture_semantic_hash(),
        trajectory_semantic_hash=compute_trajectory_semantic_hash(),
        synthetic_fixture_suite_hash=compute_synthetic_fixture_suite_hash(),
        assertion_contract_hash=val_result.assertion_contract_hash,
        invariance_contract_hash=compute_invariance_contract_hash(),
        metamorphic_test_matrix_hash=val_result.metamorphic_test_matrix_hash,
        structure_analysis_source_hash=compute_structure_analysis_source_hash(),
        preregistration_amendment_hash=preregistration_amendment_hash,
        exclusion_ledger_hash=exclusion_ledger_hash,
        structural_matrix_hash=matrix.compute_matrix_hash(),
        validation_result_hash=val_result.validation_hash,
    )
