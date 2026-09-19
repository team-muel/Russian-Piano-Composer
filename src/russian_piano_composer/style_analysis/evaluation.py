"""
Outer 9-fold composer-held-out evaluation pipeline for RC-010.

Evaluates MODEL_A, MODEL_B, or MODEL_C across 9 Leave-One-Russian + One-Control Composer Pair Out folds.
Computes ROC AUC per fold, MACRO_PAIR_AUC, secondary predictive metrics, and composer-side generalization.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from sklearn.metrics import brier_score_loss, roc_auc_score

from russian_piano_composer.style_analysis.features import RoleBlindFeatureMatrix
from russian_piano_composer.style_analysis.models import (
    ModelSpecification,
    fit_fold_scaler_and_classifier,
)
from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    ComposerSplitPlan,
    build_composer_split_plan,
)
from russian_piano_composer.style_analysis.weighting import compute_composer_balanced_weights


@dataclass(frozen=True, slots=True)
class FoldResult:
    """
    Evaluation metrics for a single held-out composer-pair fold.
    """

    fold_index: int
    held_out_russian: str
    held_out_control: str
    n_train_pieces: int
    n_test_russian_pieces: int
    n_test_control_pieces: int
    roc_auc: float
    balanced_accuracy: float
    sensitivity: float
    specificity: float
    brier_score: float
    coefs: tuple[float, ...]
    y_test_true: tuple[int, ...]
    y_test_prob: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class ComposerHeldOutEvaluation:
    """
    Complete 9-fold evaluation result for a predictor model matrix.
    """

    model_name: str
    fold_results: tuple[FoldResult, ...]
    macro_pair_auc: float
    num_folds_auc_gt_050: int
    composer_held_out_auc: dict[str, float]
    mean_balanced_accuracy: float
    mean_sensitivity: float
    mean_specificity: float
    mean_brier_score: float
    matrix_hash: str
    split_plan_hash: str
    model_spec_hash: str
    weighting_policy_hash: str


def compute_roc_auc_safe(y_true: Sequence[int], y_prob: Sequence[float]) -> float:
    """
    Calculate ROC AUC strictly requiring both binary classes to be present.
    Fails closed if binary classes are missing.
    """
    classes = set(y_true)
    if len(classes) != 2:
        raise ValueError(f"ROC AUC requires exactly 2 binary classes (0 and 1), got {classes}.")
    score = float(roc_auc_score(y_true, y_prob))
    return round(score, 6)


def evaluate_model_across_folds(
    matrix: RoleBlindFeatureMatrix,
    piece_composers: dict[str, str],
    piece_class_labels: dict[str, int] | None = None,
    split_plan: ComposerSplitPlan | None = None,
    model_spec: ModelSpecification | None = None,
) -> ComposerHeldOutEvaluation:
    """
    Run 9-fold Leave-One-Russian + One-Control Composer Pair Out evaluation on a feature matrix.

    Guarantees:
      - Scaler fit ONLY on training pieces per fold.
      - Training-composer-balanced sample weights applied per fold.
      - Zero train/test composer overlap.
      - Every fold MUST contain both binary classes in train and test sets (fails closed).
      - Full metric transparency.
    """
    if split_plan is None:
        split_plan = build_composer_split_plan()
    if model_spec is None:
        model_spec = ModelSpecification()

    if piece_class_labels is None:
        # Default classification labels: Russian = 1, Control = 0
        piece_class_labels = {
            pid: (1 if comp in RUSSIAN_COMPOSERS else 0)
            for pid, comp in piece_composers.items()
        }

    pid_to_row_idx = {pid: i for i, pid in enumerate(matrix.piece_ids)}

    fold_results: list[FoldResult] = []

    for fold in split_plan.folds:
        # Identify train and test pieces based on composer membership
        train_pids = [
            pid for pid in matrix.piece_ids
            if piece_composers[pid] in fold.training_composers
        ]
        test_pids = [
            pid for pid in matrix.piece_ids
            if piece_composers[pid] in fold.test_composers
        ]

        if not train_pids or not test_pids:
            raise ValueError(f"Fold {fold.fold_index} contains empty train or test set.")

        train_indices = [pid_to_row_idx[pid] for pid in train_pids]
        test_indices = [pid_to_row_idx[pid] for pid in test_pids]

        x_train = tuple(matrix.data[i] for i in train_indices)
        y_train = tuple(piece_class_labels[pid] for pid in train_pids)
        train_comps = tuple(piece_composers[pid] for pid in train_pids)

        x_test = tuple(matrix.data[i] for i in test_indices)
        y_test = tuple(piece_class_labels[pid] for pid in test_pids)

        # Fail closed if training data does not contain both classes
        if len(set(y_train)) != 2:
            raise ValueError(
                f"Fold {fold.fold_index} training labels must contain exactly 2 classes, got {set(y_train)}."
            )
        if set(train_comps) != set(fold.training_composers):
            raise ValueError(
                f"Fold {fold.fold_index} training composers do not match fold specification."
            )

        # Fail closed if test data does not contain both classes
        if len(set(y_test)) != 2:
            raise ValueError(
                f"Fold {fold.fold_index} test labels must contain exactly 2 classes, got {set(y_test)}. "
                f"Single-class test folds are strictly invalid."
            )

        # Calculate training-composer-balanced sample weights
        train_weights = compute_composer_balanced_weights(train_comps)

        # Fit scaler on train only and fit classifier
        scaler, clf = fit_fold_scaler_and_classifier(
            x_train=x_train,
            y_train=y_train,
            sample_weights_train=train_weights,
            spec=model_spec,
        )

        # Scale test data using training-fitted scaler
        x_test_scaled = scaler.transform(list(x_test))
        probs = clf.predict_proba(x_test_scaled)[:, 1]
        probs_tuple = tuple(round(float(p), 6) for p in probs)

        auc = compute_roc_auc_safe(y_test, probs_tuple)

        # Secondary metrics at threshold 0.5
        preds = [1 if p >= 0.5 else 0 for p in probs]
        tp = sum(1 for yt, yp in zip(y_test, preds, strict=True) if yt == 1 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_test, preds, strict=True) if yt == 0 and yp == 0)

        n_rus = sum(1 for yt in y_test if yt == 1)
        n_ctrl = sum(1 for yt in y_test if yt == 0)

        sens = (tp / float(n_rus)) if n_rus > 0 else 0.0
        spec = (tn / float(n_ctrl)) if n_ctrl > 0 else 0.0
        bal_acc = (sens + spec) / 2.0

        try:
            brier = float(brier_score_loss(y_test, probs))
        except ValueError:
            brier = 0.0

        coef_vals = tuple(round(float(c), 6) for c in clf.coef_[0])

        fold_results.append(
            FoldResult(
                fold_index=fold.fold_index,
                held_out_russian=fold.held_out_russian,
                held_out_control=fold.held_out_control,
                n_train_pieces=len(train_pids),
                n_test_russian_pieces=n_rus,
                n_test_control_pieces=n_ctrl,
                roc_auc=auc,
                balanced_accuracy=round(bal_acc, 6),
                sensitivity=round(sens, 6),
                specificity=round(spec, 6),
                brier_score=round(brier, 6),
                coefs=coef_vals,
                y_test_true=y_test,
                y_test_prob=probs_tuple,
            )
        )

    # Calculate MACRO_PAIR_AUC (mean of the 9 fold AUCs)
    macro_auc = sum(fr.roc_auc for fr in fold_results) / len(fold_results)
    num_gt_050 = sum(1 for fr in fold_results if fr.roc_auc > 0.50)

    # Composer-side generalization performance
    comp_auc: dict[str, float] = {}
    for comp in ALL_COMPOSERS:
        relevant_folds = [
            fr.roc_auc for fr in fold_results
            if fr.held_out_russian == comp or fr.held_out_control == comp
        ]
        if relevant_folds:
            comp_auc[comp] = round(sum(relevant_folds) / len(relevant_folds), 6)
        else:
            comp_auc[comp] = 0.50

    mean_bal_acc = sum(fr.balanced_accuracy for fr in fold_results) / len(fold_results)
    mean_sens = sum(fr.sensitivity for fr in fold_results) / len(fold_results)
    mean_spec = sum(fr.specificity for fr in fold_results) / len(fold_results)
    mean_brier = sum(fr.brier_score for fr in fold_results) / len(fold_results)

    from russian_piano_composer.style_analysis.weighting import (
        compute_composer_weighting_policy_hash,
    )

    return ComposerHeldOutEvaluation(
        model_name=matrix.model_name,
        fold_results=tuple(fold_results),
        macro_pair_auc=round(macro_auc, 6),
        num_folds_auc_gt_050=num_gt_050,
        composer_held_out_auc=comp_auc,
        mean_balanced_accuracy=round(mean_bal_acc, 6),
        mean_sensitivity=round(mean_sens, 6),
        mean_specificity=round(mean_spec, 6),
        mean_brier_score=round(mean_brier, 6),
        matrix_hash=matrix.compute_matrix_hash(),
        split_plan_hash=split_plan.compute_plan_hash(),
        model_spec_hash=model_spec.compute_spec_hash(),
        weighting_policy_hash=compute_composer_weighting_policy_hash(),
    )
