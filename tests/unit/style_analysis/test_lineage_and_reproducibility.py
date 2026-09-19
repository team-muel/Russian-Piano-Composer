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


def test_model_b_and_c_schema_hash() -> None:
    """Verify compute_model_b_schema_hash and compute_model_c_schema_hash are valid hashes."""
    from russian_piano_composer.style_analysis.features import (
        compute_model_a_schema_hash,
        compute_model_b_schema_hash,
        compute_model_c_schema_hash,
        compute_style_feature_schema_hash,
    )

    hb = compute_model_b_schema_hash()
    hc = compute_model_c_schema_hash()
    ha = compute_model_a_schema_hash()
    hs = compute_style_feature_schema_hash()

    assert len(hb) == 64
    assert len(hc) == 64
    assert len(ha) == 64
    assert len(hs) == 64
    # MODEL_B is a composite schema and distinct from pure style feature schema hash
    assert hb != hs
    assert hc != hb
    assert hc != ha


def test_evaluation_result_hash_mutation_sensitivity() -> None:
    """Verify modifying any fold result or permutation record alters the evaluation result hash."""
    from russian_piano_composer.style_analysis.evaluation import (
        ComposerHeldOutEvaluation,
        FoldResult,
    )
    from russian_piano_composer.style_analysis.lineage import compute_evaluation_result_hash
    from russian_piano_composer.style_analysis.permutation import (
        EmpiricalStyleStatus,
        ExactComposerPermutationResult,
        PermutationResultRecord,
    )

    base_fold = FoldResult(
        fold_index=0,
        held_out_russian="tchaikovsky",
        held_out_control="beethoven",
        n_train_pieces=100,
        n_test_russian_pieces=10,
        n_test_control_pieces=10,
        roc_auc=0.5,
        balanced_accuracy=0.5,
        sensitivity=0.5,
        specificity=0.5,
        brier_score=0.25,
        coefs=(0.0,),
        y_test_true=(1, 0),
        y_test_prob=(0.5, 0.5),
    )

    base_perm_record = PermutationResultRecord(
        assignment_index=0,
        class_1_composers=("tchaikovsky", "rachmaninoff", "scriabin"),
        class_0_composers=("beethoven", "chopin", "brahms"),
        complement_assignment_index=19,
        split_plan_hash="a" * 64,
        macro_pair_auc=0.5,
        num_folds_auc_gt_050=4,
        is_observed_assignment=True,
    )

    base_eval = ComposerHeldOutEvaluation(
        model_name="MODEL_C",
        fold_results=(base_fold,),
        macro_pair_auc=0.5,
        num_folds_auc_gt_050=4,
        composer_held_out_auc={},
        mean_balanced_accuracy=0.5,
        mean_sensitivity=0.5,
        mean_specificity=0.5,
        mean_brier_score=0.25,
        matrix_hash="a" * 64,
        split_plan_hash="b" * 64,
        model_spec_hash="c" * 64,
        weighting_policy_hash="d" * 64,
    )

    base_perm = ExactComposerPermutationResult(
        observed_macro_pair_auc=0.5,
        all_permutation_aucs=(0.5,),
        permutation_records=(base_perm_record,),
        extreme_count=18,
        total_assignments=20,
        exact_p_value=0.9,
        minimum_attainable_p_value=0.1,
        observed_rank_min=17,
        observed_rank_max=18,
        observed_rank_interval="17-18/20",
        tied_rank_count=2,
        symmetry_verified=True,
        empirical_status=EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED,
        permutation_plan_hash="e" * 64,
    )

    base_hash = compute_evaluation_result_hash(base_eval, base_perm)
    assert len(base_hash) == 64

    # Mutate fold brier score
    mut_fold = FoldResult(
        fold_index=0,
        held_out_russian="tchaikovsky",
        held_out_control="beethoven",
        n_train_pieces=100,
        n_test_russian_pieces=10,
        n_test_control_pieces=10,
        roc_auc=0.5,
        balanced_accuracy=0.5,
        sensitivity=0.5,
        specificity=0.5,
        brier_score=0.26,
        coefs=(0.0,),
        y_test_true=(1, 0),
        y_test_prob=(0.5, 0.5),
    )
    mut_eval = ComposerHeldOutEvaluation(
        model_name="MODEL_C",
        fold_results=(mut_fold,),
        macro_pair_auc=0.5,
        num_folds_auc_gt_050=4,
        composer_held_out_auc={},
        mean_balanced_accuracy=0.5,
        mean_sensitivity=0.5,
        mean_specificity=0.5,
        mean_brier_score=0.25,
        matrix_hash="a" * 64,
        split_plan_hash="b" * 64,
        model_spec_hash="c" * 64,
        weighting_policy_hash="d" * 64,
    )
    assert compute_evaluation_result_hash(mut_eval, base_perm) != base_hash

    # Mutate permutation record macro AUC
    mut_perm_record = PermutationResultRecord(
        assignment_index=0,
        class_1_composers=("tchaikovsky", "rachmaninoff", "scriabin"),
        class_0_composers=("beethoven", "chopin", "brahms"),
        complement_assignment_index=19,
        split_plan_hash="a" * 64,
        macro_pair_auc=0.51,
        num_folds_auc_gt_050=4,
        is_observed_assignment=True,
    )
    mut_perm = ExactComposerPermutationResult(
        observed_macro_pair_auc=0.5,
        all_permutation_aucs=(0.5,),
        permutation_records=(mut_perm_record,),
        extreme_count=18,
        total_assignments=20,
        exact_p_value=0.9,
        minimum_attainable_p_value=0.1,
        observed_rank_min=17,
        observed_rank_max=18,
        observed_rank_interval="17-18/20",
        tied_rank_count=2,
        symmetry_verified=True,
        empirical_status=EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED,
        permutation_plan_hash="e" * 64,
    )
    assert compute_evaluation_result_hash(base_eval, mut_perm) != base_hash



