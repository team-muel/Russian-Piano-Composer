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
)


class EmpiricalStyleStatus(StrEnum):
    """Final empirical outcome status for Russian-vs-Control style discrimination."""

    RUSSIAN_CONTROL_SIGNAL_SUPPORTED = "RUSSIAN_CONTROL_SIGNAL_SUPPORTED"
    RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED = "RUSSIAN_CONTROL_SIGNAL_NOT_SUPPORTED"
    RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE = "RUSSIAN_CONTROL_SIGNAL_INCONCLUSIVE"


@dataclass(frozen=True, slots=True)
class ComposerPermutationAssignment:
    """A single assignment of 3 composers to class 1 and 3 to class 0."""

    assignment_index: int
    class_1_composers: tuple[str, ...]
    class_0_composers: tuple[str, ...]
    complement_assignment_index: int
    is_observed_assignment: bool
    split_plan_hash: str

    @property
    def russian_composers(self) -> tuple[str, ...]:
        return self.class_1_composers

    @property
    def control_composers(self) -> tuple[str, ...]:
        return self.class_0_composers


@dataclass(frozen=True, slots=True)
class PermutationResultRecord:
    """Evaluation output for a single composer-label permutation."""

    assignment_index: int
    class_1_composers: tuple[str, ...]
    class_0_composers: tuple[str, ...]
    complement_assignment_index: int
    macro_pair_auc: float
    num_folds_auc_gt_050: int
    is_observed_assignment: bool
    split_plan_hash: str

    @property
    def russian_composers(self) -> tuple[str, ...]:
        return self.class_1_composers

    @property
    def control_composers(self) -> tuple[str, ...]:
        return self.class_0_composers


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
    minimum_attainable_p_value: float  # 2 / 20 = 0.10 for label-symmetric ROC AUC
    observed_rank_min: int
    observed_rank_max: int
    observed_rank_interval: str
    tied_rank_count: int
    symmetry_verified: bool
    empirical_status: EmpiricalStyleStatus
    permutation_plan_hash: str

    @property
    def observed_rank(self) -> int:
        """Compatibility property returning observed_rank_max."""
        return self.observed_rank_max


def generate_all_composer_label_permutations() -> tuple[ComposerPermutationAssignment, ...]:
    """
    Enumerate all C(6, 3) = 20 exact ways to partition the 6 composers into class 1 and class 0.
    Binds the complement assignment index and assignment-specific 9-fold split plan hash.
    """
    from russian_piano_composer.style_analysis.splits import build_pair_holdout_plan

    all_sorted = tuple(sorted(ALL_COMPOSERS))
    combos = list(combinations(all_sorted, 3))

    assignments: list[ComposerPermutationAssignment] = []
    for idx, c1_tuple in enumerate(combos):
        c0_list = [c for c in all_sorted if c not in c1_tuple]
        c0_tuple: tuple[str, str, str] = (c0_list[0], c0_list[1], c0_list[2])
        complement_idx = combos.index(c0_tuple)
        is_obs = (set(c1_tuple) == set(RUSSIAN_COMPOSERS))
        plan_hash = build_pair_holdout_plan(c1_tuple, c0_tuple).compute_plan_hash()

        assignments.append(
            ComposerPermutationAssignment(
                assignment_index=idx,
                class_1_composers=c1_tuple,
                class_0_composers=c0_tuple,
                complement_assignment_index=complement_idx,
                is_observed_assignment=is_obs,
                split_plan_hash=plan_hash,
            )
        )

    return tuple(assignments)


def compute_permutation_plan_hash() -> str:
    """
    Deterministic SHA-256 hash of the 20 exact composer-label permutations and assignment-specific plans.
    """
    from russian_piano_composer.style_analysis.splits import build_pair_holdout_plan

    perms = generate_all_composer_label_permutations()
    canonical = {
        "total_assignments": len(perms),
        "test_statistic": "MACRO_PAIR_AUC",
        "p_value_formula": "count(MACRO_PAIR_AUC >= observed) / 20.0",
        "minimum_attainable_p_value": 0.10,
        "complement_pairs_count": 10,
        "assignments": [
            {
                "assignment_index": p.assignment_index,
                "class_1_composers": list(p.class_1_composers),
                "class_0_composers": list(p.class_0_composers),
                "complement_assignment_index": p.complement_assignment_index,
                "split_plan_hash": p.split_plan_hash,
                "is_observed": p.is_observed_assignment,
                "folds": [
                    {
                        "fold_index": f.fold_index,
                        "held_out_class_1": f.held_out_class_1,
                        "held_out_class_0": f.held_out_class_0,
                        "training_class_1": list(f.training_class_1),
                        "training_class_0": list(f.training_class_0),
                    }
                    for f in build_pair_holdout_plan(p.class_1_composers, p.class_0_composers).folds
                ],
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

    Note on structural bounds:
      For N=6 composers under exact permutation testing with label-symmetric ROC AUC,
      the minimum attainable exact p-value is 2 / 20 = 0.10.
      Therefore, SUPPORTED is structurally unattainable for N=6 under the pre-registered
      p <= 0.05 threshold without expanding the composer corpus.
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
    model_spec: ModelSpecification | None = None,
) -> ExactComposerPermutationResult:
    """
    Execute exhaustive exact 20-composer-level permutation test across all C(6, 3) = 20 label assignments.
    Guarantees every permutation assignment uses its own valid assignment-specific 3x3 outer split plan.
    """
    from russian_piano_composer.style_analysis.splits import build_pair_holdout_plan

    if model_spec is None:
        model_spec = ModelSpecification()

    assignments = generate_all_composer_label_permutations()

    perm_records: list[PermutationResultRecord] = []
    perm_aucs: list[float] = []

    for assign in assignments:
        # Build assignment-specific 3x3 outer split plan
        assign_split_plan = build_pair_holdout_plan(
            class_1_composers=assign.class_1_composers,
            class_0_composers=assign.class_0_composers,
        )

        # Create class labels for this permutation
        perm_class_labels = {
            pid: (1 if piece_composers[pid] in assign.class_1_composers else 0)
            for pid in matrix.piece_ids
        }

        eval_res = evaluate_model_across_folds(
            matrix=matrix,
            piece_composers=piece_composers,
            piece_class_labels=perm_class_labels,
            split_plan=assign_split_plan,
            model_spec=model_spec,
        )
        auc = eval_res.macro_pair_auc
        n_gt_050 = eval_res.num_folds_auc_gt_050

        perm_aucs.append(round(auc, 6))
        perm_records.append(
            PermutationResultRecord(
                assignment_index=assign.assignment_index,
                class_1_composers=assign.class_1_composers,
                class_0_composers=assign.class_0_composers,
                complement_assignment_index=assign.complement_assignment_index,
                macro_pair_auc=round(auc, 6),
                num_folds_auc_gt_050=n_gt_050,
                is_observed_assignment=assign.is_observed_assignment,
                split_plan_hash=assign.split_plan_hash,
            )
        )

    obs_auc = observed_eval.macro_pair_auc

    # Verify complement symmetry for all 10 pairs
    symmetry_verified = True
    for rec in perm_records:
        comp_rec = perm_records[rec.complement_assignment_index]
        if abs(rec.macro_pair_auc - comp_rec.macro_pair_auc) > 1e-5:
            symmetry_verified = False
            raise RuntimeError(
                f"Complement symmetry violated between assignment {rec.assignment_index} "
                f"({rec.macro_pair_auc}) and {comp_rec.assignment_index} ({comp_rec.macro_pair_auc})!"
            )

    # Tie-aware rank and extreme count calculation
    extreme_count = sum(1 for a in perm_aucs if a >= obs_auc - 1e-9)
    strictly_better = sum(1 for a in perm_aucs if a > obs_auc + 1e-9)
    tied_count = sum(1 for a in perm_aucs if abs(a - obs_auc) < 1e-9)
    total_assignments = len(assignments)

    rank_min = strictly_better + 1
    rank_max = strictly_better + tied_count
    rank_interval = f"{rank_min}-{rank_max} / {total_assignments}" if rank_min != rank_max else f"{rank_min} / {total_assignments}"

    # Exact p-value: count(AUC >= observed) / 20.0
    exact_p = extreme_count / float(total_assignments)

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
        minimum_attainable_p_value=0.10,
        observed_rank_min=rank_min,
        observed_rank_max=rank_max,
        observed_rank_interval=rank_interval,
        tied_rank_count=tied_count,
        symmetry_verified=symmetry_verified,
        empirical_status=status,
        permutation_plan_hash=compute_permutation_plan_hash(),
    )
