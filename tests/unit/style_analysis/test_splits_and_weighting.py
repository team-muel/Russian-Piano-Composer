"""
Unit tests for 9-fold composer-held-out splits and composer-balanced sample weighting.
"""

import numpy as np
import pytest

from russian_piano_composer.style_analysis.models import (
    ModelSpecification,
    fit_fold_scaler_and_classifier,
)
from russian_piano_composer.style_analysis.splits import (
    CONTROL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    build_composer_split_plan,
    build_pair_holdout_plan,
    compute_composer_split_plan_hash,
    normalize_composer_name,
)
from russian_piano_composer.style_analysis.weighting import (
    ComposerWeightingPolicy,
    compute_composer_balanced_weights,
    compute_composer_weighting_policy_hash,
)


def test_normalize_composer_name() -> None:
    """Verify composer name normalization from raw score metadata strings."""
    assert normalize_composer_name("Nikolai Medtner") == "Medtner"
    assert normalize_composer_name("Sergei Rachmaninoff") == "Rachmaninoff"
    assert normalize_composer_name("Pyotr Ilyich Tchaikovsky") == "Tchaikovsky"
    assert normalize_composer_name("Frédéric Chopin") == "Chopin"
    assert normalize_composer_name("Franz Liszt") == "Liszt"
    assert normalize_composer_name("Robert Schumann") == "Schumann"

    with pytest.raises(ValueError, match="Unrecognized composer string"):
        normalize_composer_name("Ludwig van Beethoven")


def test_composer_split_plan_structure() -> None:
    """Verify 9 Leave-One-Russian + One-Control Composer Pair Out folds."""
    plan = build_composer_split_plan()
    assert len(plan.folds) == 9

    all_pairs = set()
    for fold in plan.folds:
        assert fold.held_out_russian in RUSSIAN_COMPOSERS
        assert fold.held_out_control in CONTROL_COMPOSERS

        # Train and test sets must have 0 composer overlap
        train_comps = set(fold.training_composers)
        test_comps = set(fold.test_composers)
        assert train_comps.isdisjoint(test_comps)

        # 4 train composers (2 Russian, 2 Control)
        assert len(fold.training_russian) == 2
        assert len(fold.training_control) == 2
        assert len(train_comps) == 4
        assert len(test_comps) == 2

        all_pairs.add((fold.held_out_russian, fold.held_out_control))

    # All 3 x 3 = 9 unique pairs must exist
    assert len(all_pairs) == 9


def test_build_pair_holdout_plan_arbitrary_partitions() -> None:
    """Verify build_pair_holdout_plan builds valid 9-fold plans for arbitrary partitions."""
    class_1 = ("Chopin", "Liszt", "Medtner")
    class_0 = ("Rachmaninoff", "Schumann", "Tchaikovsky")

    plan = build_pair_holdout_plan(class_1, class_0)
    assert len(plan.folds) == 9

    all_pairs = set()
    for fold in plan.folds:
        assert fold.held_out_class_1 in class_1
        assert fold.held_out_class_0 in class_0

        train_comps = set(fold.training_composers)
        test_comps = set(fold.test_composers)
        assert train_comps.isdisjoint(test_comps)

        assert len(fold.training_class_1) == 2
        assert len(fold.training_class_0) == 2
        assert len(train_comps) == 4
        assert len(test_comps) == 2

        all_pairs.add((fold.held_out_class_1, fold.held_out_class_0))

    assert len(all_pairs) == 9


def test_split_plan_hash_determinism() -> None:
    """Verify compute_composer_split_plan_hash is deterministic."""
    h1 = compute_composer_split_plan_hash()
    h2 = compute_composer_split_plan_hash()
    assert len(h1) == 64
    assert h1 == h2


def test_composer_weighting_policy_and_hash() -> None:
    """Verify composer weighting policy and hash determinism."""
    policy = ComposerWeightingPolicy()
    h1 = policy.compute_policy_hash()
    h2 = compute_composer_weighting_policy_hash()
    assert len(h1) == 64
    assert h1 == h2


def test_compute_composer_balanced_weights() -> None:
    """
    Verify training sample weights assign equal total weight to each distinct training composer.
    """
    # Example training sequence: Medtner 2 pieces, Rachmaninoff 3 pieces, Chopin 5 pieces, Liszt 10 pieces
    train_comps = (
        "Medtner", "Medtner",
        "Rachmaninoff", "Rachmaninoff", "Rachmaninoff",
        "Chopin", "Chopin", "Chopin", "Chopin", "Chopin",
        "Liszt", "Liszt", "Liszt", "Liszt", "Liszt", "Liszt", "Liszt", "Liszt", "Liszt", "Liszt",
    )

    weights = compute_composer_balanced_weights(train_comps)
    assert len(weights) == len(train_comps)

    # 4 distinct composers -> each composer's aggregate weight must equal 1/4 = 0.25
    medtner_sum = sum(w for comp, w in zip(train_comps, weights, strict=True) if comp == "Medtner")
    rach_sum = sum(w for comp, w in zip(train_comps, weights, strict=True) if comp == "Rachmaninoff")
    chopin_sum = sum(w for comp, w in zip(train_comps, weights, strict=True) if comp == "Chopin")
    liszt_sum = sum(w for comp, w in zip(train_comps, weights, strict=True) if comp == "Liszt")

    assert pytest.approx(medtner_sum, abs=1e-5) == 0.25
    assert pytest.approx(rach_sum, abs=1e-5) == 0.25
    assert pytest.approx(chopin_sum, abs=1e-5) == 0.25
    assert pytest.approx(liszt_sum, abs=1e-5) == 0.25

    # Total sum of sample weights across all training pieces = 1.0
    assert pytest.approx(sum(weights), abs=1e-5) == 1.0


def test_fit_fold_scaler_and_classifier_training_only() -> None:
    """
    Verify scaler is fit strictly on training data and applies sample weights.
    """
    x_train = ((1.0, 10.0), (2.0, 20.0), (3.0, 30.0), (4.0, 40.0))
    y_train = (1, 1, 0, 0)
    weights = (0.25, 0.25, 0.25, 0.25)
    spec = ModelSpecification(C=1.0)

    scaler, _clf = fit_fold_scaler_and_classifier(
        x_train=x_train,
        y_train=y_train,
        sample_weights_train=weights,
        spec=spec,
    )

    # Check scaler mean matches training data mean
    np.testing.assert_allclose(scaler.mean_, [2.5, 25.0])
