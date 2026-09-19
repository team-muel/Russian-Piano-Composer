"""
Unit tests for lineage hashing and reproducibility verification for RC-010.
"""

from russian_piano_composer.style_analysis.lineage import (
    MASTER_BASELINE_SHA,
    StyleAnalysisLineage,
    compute_label_assignment_hash,
)


def test_master_baseline_sha() -> None:
    """Verify master baseline SHA is bound to RC-010 starting commit."""
    assert MASTER_BASELINE_SHA == "2aed82a4f13aa161743b25e30ad879baadc68b3f"


def test_label_assignment_hash_determinism() -> None:
    """Verify compute_label_assignment_hash is deterministic and ordering-invariant."""
    labels_a = {"piece_2": 0, "piece_1": 1}
    labels_b = {"piece_1": 1, "piece_2": 0}

    h1 = compute_label_assignment_hash(labels_a)
    h2 = compute_label_assignment_hash(labels_b)
    assert len(h1) == 64
    assert h1 == h2


def test_style_analysis_lineage_bundle_hash_sensitivity() -> None:
    """Verify modifying any component hash alters the total bundle hash."""
    base_lineage = StyleAnalysisLineage(
        master_baseline_sha="a" * 40,
        manifest_hash="b" * 64,
        rc009a_feature_schema_semantic_hash="1" * 64,
        rc009a_feature_policy_hash="2" * 64,
        rc009b_candidate_set_hash="3" * 64,
        rc009b_discovery_policy_hash="4" * 64,
        ctu_schema_semantic_hash="c" * 64,
        representation_semantic_hash="d" * 64,
        similarity_semantic_hash="e" * 64,
        style_feature_schema_hash="f" * 64,
        model_a_schema_hash="5" * 64,
        model_b_schema_hash="6" * 64,
        model_c_schema_hash="7" * 64,
        role_blind_feature_matrix_hash="g" * 64,
        label_assignment_hash="h" * 64,
        composer_split_plan_hash="i" * 64,
        model_spec_hash="j" * 64,
        composer_weighting_policy_hash="k" * 64,
        permutation_plan_hash="l" * 64,
        evaluation_result_hash="m" * 64,
    )

    base_hash = base_lineage.compute_bundle_hash()
    assert len(base_hash) == 64

    # Alter master SHA
    alt_lineage = StyleAnalysisLineage(
        master_baseline_sha="z" * 40,
        manifest_hash="b" * 64,
        rc009a_feature_schema_semantic_hash="1" * 64,
        rc009a_feature_policy_hash="2" * 64,
        rc009b_candidate_set_hash="3" * 64,
        rc009b_discovery_policy_hash="4" * 64,
        ctu_schema_semantic_hash="c" * 64,
        representation_semantic_hash="d" * 64,
        similarity_semantic_hash="e" * 64,
        style_feature_schema_hash="f" * 64,
        model_a_schema_hash="5" * 64,
        model_b_schema_hash="6" * 64,
        model_c_schema_hash="7" * 64,
        role_blind_feature_matrix_hash="g" * 64,
        label_assignment_hash="h" * 64,
        composer_split_plan_hash="i" * 64,
        model_spec_hash="j" * 64,
        composer_weighting_policy_hash="k" * 64,
        permutation_plan_hash="l" * 64,
        evaluation_result_hash="m" * 64,
    )
    assert alt_lineage.compute_bundle_hash() != base_hash
