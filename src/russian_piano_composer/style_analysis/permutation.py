"""
Exact 20-composer-level permutation test and primary empirical decision rule for RC-010.

Enumerates all C(6, 3) = 20 ways to assign 3 composers to Russian class (1) and 3 to Control class (0).
For each assignment, runs the exact same 9-fold composer-held-out evaluation design.
Evaluates the exact p-value p = count(MACRO_PAIR_AUC >= observed) / 20.
"""

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from itertools import combinations

from russian_piano_composer.style_analysis.evaluation import (
    ComposerHeldOutEvaluation,
    evaluate_model_across_folds,
)
from russian_piano_composer.style_analysis.features import RoleBlindFeatureMatrix
from russian_piano_composer.style_analysis.models import ModelSpecification
from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    ComposerSplitPlan,
    build_composer_split_plan,
)


class EmpiricalStyleStatus(StrEnum):
    """Final empirical outcome status for Russian-vs-Control style discrimination."""

    RUSSIAN_CONTROL_SIGNAL_SUPPORTED = "RUSSIAN_CONTROL_SIGNAL_SUPPORTED"
    RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED = "RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED"
    RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE = "RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE"


@dataclass(frozen=True, slots=True)
class ComposerPermutationAssignment:
    """A single assignment of 3 composers to Russian class (1) and 3 to Control class (0)."""

    assignment_index: int
    russian_composers: tuple[str, ...]
    control_composers: tuple[str, ...]
    is_observed_assignment: bool


@dataclass(frozen=True, slots=True)
class PermutationResultRecord:
    """Evaluation output for a single composer-label permutation."""

    assignment_index: int
    russian_composers: tuple[str, ...]
    control_composers: tuple[str, ...]
    macro_pair_auc: float
    num_folds_auc_gt_050: int
    is_observed_assignment: bool


@dataclass(frozen=True, slots=True)
class ExactComposerPermutationResult:
    """
    Exhaustive 20-composer-level permutation test result for MODEL_C.
    """

    observed_macro_pair_auc: float
    all_permutation_aucs: tuple[float, ...]
    permutation_records: tuple[PermutationResultRecord, ...]
    extreme_count: int
    total_assignments: int  # Always 20
    exact_p_value: float
    observed_rank: int
    empirical_status: EmpiricalStyleStatus
    permutation_plan_hash: str


def generate_all_composer_label_permutations() -> tuple[ComposerPermutationAssignment, ...]:
    """
    Enumerate all C(6, 3) = 20 exact ways to partition the 6 composers into Russian and Control classes.
    """
    all_sorted = tuple(sorted(ALL_COMPOSERS))
    combos = list(combinations(all_sorted, 3))

    assignments: list[ComposerPermutationAssignment] = []
    for idx, rus_tuple in enumerate(combos):
        ctrl_tuple = tuple(c for c in all_sorted if c not in rus_tuple)
        is_obs = (set(rus_tuple) == set(RUSSIAN_COMPOSERS))
        assignments.append(
            ComposerPermutationAssignment(
                assignment_index=idx,
                russian_composers=rus_tuple,
                control_composers=ctrl_tuple,
                is_observed_assignment=is_obs,
            )
        )

    return tuple(assignments)


def compute_permutation_plan_hash() -> str:
    """
    Deterministic SHA-256 hash of the 20 exact composer-label permutations.
    """
    perms = generate_all_composer_label_permutations()
    canonical = {
        "total_assignments": len(perms),
        "assignments": [
            {
                "assignment_index": p.assignment_index,
                "russian_composers": list(p.russian_composers),
                "control_composers": list(p.control_composers),
                "is_observed": p.is_observed_assignment,
            }
            for p in perms
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evaluate_empirical_style_status(
    macro_pair_auc: float,
    exact_p_value: float,
    num_folds_auc_gt_050: int,
) -> EmpiricalStyleStatus:
    """
    Frozen primary empirical decision rule:
    SUPPORTED iff ALL are true:
      1. MODEL_C MACRO_PAIR_AUC > 0.50
      2. exact_p_value <= 0.05
      3. at least 6 of 9 held-out folds have AUC > 0.50
    Otherwise:
      If MACRO_PAIR_AUC <= 0.50 -> NOT_SUPPORTED
      Else -> INCONCLUSIVE
    """
    if macro_pair_auc <= 0.50:
        return EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED

    if (
        macro_pair_auc > 0.50
        and exact_p_value <= 0.05
        and num_folds_auc_gt_050 >= 6
    ):
        return EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_SUPPORTED

    return EmpiricalStyleStatus.RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE


def run_exact_composer_permutation_test(
    matrix: RoleBlindFeatureMatrix,
    piece_composers: dict[str, str],
    observed_eval: ComposerHeldOutEvaluation,
    split_plan: ComposerSplitPlan | None = None,
    model_spec: ModelSpecification | None = None,
) -> ExactComposerPermutationResult:
    """
    Execute exhaustive exact 20-composer-level permutation test across all C(6, 3) = 20 label assignments.
    """
    if split_plan is None:
        split_plan = build_composer_split_plan()
    if model_spec is None:
        model_spec = ModelSpecification()

    assignments = generate_all_composer_label_permutations()

    perm_records: list[PermutationResultRecord] = []
    perm_aucs: list[float] = []

    for assign in assignments:
        if assign.is_observed_assignment:
            auc = observed_eval.macro_pair_auc
            n_gt_050 = observed_eval.num_folds_auc_gt_050
        else:
            # Create synthetic class labels for this permutation
            perm_class_labels = {
                pid: (1 if piece_composers[pid] in assign.russian_composers else 0)
                for pid in matrix.piece_ids
            }
            eval_res = evaluate_model_across_folds(
                matrix=matrix,
                piece_composers=piece_composers,
                piece_class_labels=perm_class_labels,
                split_plan=split_plan,
                model_spec=model_spec,
            )
            auc = eval_res.macro_pair_auc
            n_gt_050 = eval_res.num_folds_auc_gt_050

        perm_aucs.append(round(auc, 6))
        perm_records.append(
            PermutationResultRecord(
                assignment_index=assign.assignment_index,
                russian_composers=assign.russian_composers,
                control_composers=assign.control_composers,
                macro_pair_auc=round(auc, 6),
                num_folds_auc_gt_050=n_gt_050,
                is_observed_assignment=assign.is_observed_assignment,
            )
        )

    obs_auc = observed_eval.macro_pair_auc
    extreme_count = sum(1 for a in perm_aucs if a >= obs_auc)
    total_assignments = len(assignments)

    # Exact p-value without Monte Carlo approximation: extreme / total
    exact_p = extreme_count / float(total_assignments)

    # Rank among 20 assignments (1 = highest AUC)
    sorted_aucs = sorted(perm_aucs, reverse=True)
    rank = sorted_aucs.index(obs_auc) + 1

    status = evaluate_empirical_style_status(
        macro_pair_auc=obs_auc,
        exact_p_value=exact_p,
        num_folds_auc_gt_050=observed_eval.num_folds_auc_gt_050,
    )

    return ExactComposerPermutationResult(
        observed_macro_pair_auc=round(obs_auc, 6),
        all_permutation_aucs=tuple(perm_aucs),
        permutation_records=tuple(perm_records),
        extreme_count=extreme_count,
        total_assignments=total_assignments,
        exact_p_value=round(exact_p, 4),
        observed_rank=rank,
        empirical_status=status,
        permutation_plan_hash=compute_permutation_plan_hash(),
    )
