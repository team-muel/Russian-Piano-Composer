"""
Unit tests for deterministic classifier specification, exact 20-composer permutations, and decision rule.
"""


from russian_piano_composer.style_analysis.evaluation import compute_roc_auc_safe
from russian_piano_composer.style_analysis.models import (
    ModelSpecification,
    compute_model_spec_hash,
)
from russian_piano_composer.style_analysis.permutation import (
    EmpiricalStyleStatus,
    compute_permutation_plan_hash,
    evaluate_empirical_style_status,
    generate_all_composer_label_permutations,
)


def test_model_specification_and_hash() -> None:
    """Verify ModelSpecification parameters, classifier creation, and hash determinism."""
    spec = ModelSpecification(C=1.0, penalty="l2", solver="lbfgs", random_state=42)
    assert spec.classifier_type == "LogisticRegression"
    assert spec.C == 1.0

    clf = spec.create_classifier()
    assert clf.C == 1.0
    assert clf.penalty == "l2"
    assert clf.solver == "lbfgs"
    assert clf.random_state == 42

    h1 = spec.compute_spec_hash()
    h2 = compute_model_spec_hash()
    assert len(h1) == 64
    assert h1 == h2


def test_generate_all_composer_label_permutations() -> None:
    """
    Verify generate_all_composer_label_permutations produces exactly C(6, 3) = 20 assignments,
    with observed assignment included exactly once.
    """
    perms = generate_all_composer_label_permutations()
    assert len(perms) == 20

    obs_count = sum(1 for p in perms if p.is_observed_assignment)
    assert obs_count == 1

    for p in perms:
        assert len(p.russian_composers) == 3
        assert len(p.control_composers) == 3
        assert set(p.russian_composers).isdisjoint(set(p.control_composers))


def test_permutation_plan_hash_determinism() -> None:
    """Verify compute_permutation_plan_hash is deterministic."""
    h1 = compute_permutation_plan_hash()
    h2 = compute_permutation_plan_hash()
    assert len(h1) == 64
    assert h1 == h2


def test_evaluate_empirical_style_status_supported() -> None:
    """Verify decision rule for RUSSIAN_CONTROL_SIGNAL_SUPPORTED."""
    status = evaluate_empirical_style_status(
        macro_pair_auc=0.75,
        exact_p_value=0.05,
        num_folds_auc_gt_050=7,
    )
    assert status == EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_SUPPORTED


def test_evaluate_empirical_style_status_not_supported() -> None:
    """Verify decision rule for RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED."""
    status = evaluate_empirical_style_status(
        macro_pair_auc=0.48,
        exact_p_value=0.50,
        num_folds_auc_gt_050=3,
    )
    assert status == EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED


def test_evaluate_empirical_style_status_inconclusive() -> None:
    """Verify decision rule for RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE."""
    # MACRO AUC > 0.50 but p-value > 0.05
    status1 = evaluate_empirical_style_status(
        macro_pair_auc=0.60,
        exact_p_value=0.15,
        num_folds_auc_gt_050=7,
    )
    assert status1 == EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE

    # MACRO AUC > 0.50, p <= 0.05, but < 6 folds with AUC > 0.50
    status2 = evaluate_empirical_style_status(
        macro_pair_auc=0.60,
        exact_p_value=0.05,
        num_folds_auc_gt_050=5,
    )
    assert status2 == EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE


def test_compute_roc_auc_safe() -> None:
    """Verify safe ROC AUC calculation handling single class edge cases."""
    assert compute_roc_auc_safe([1, 1, 1], [0.8, 0.9, 0.7]) == 0.50
    assert compute_roc_auc_safe([1, 0, 1, 0], [0.8, 0.2, 0.9, 0.1]) == 1.0
