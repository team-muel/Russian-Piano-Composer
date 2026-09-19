"""
Canonical lineage hashing and scientific provenance tracking for RC-010.

Binds canonical manifest hash, RC-009A/B semantic hashes, baseline master SHA,
role-blind feature matrix hash, split plan, model specification, weighting policy,
permutation plan, and evaluation results.
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
    compute_schema_semantic_hash as compute_feature_schema_semantic_hash,
)
from russian_piano_composer.features import FEATURE_REGISTRY
from russian_piano_composer.features.policy import FeatureExtractionPolicy
from russian_piano_composer.style_analysis.evaluation import ComposerHeldOutEvaluation
from russian_piano_composer.style_analysis.features import (
    ACCEPTED_RC009B_CANDIDATE_SET_HASH,
    ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
    RoleBlindFeatureMatrix,
    compute_model_a_schema_hash,
    compute_model_b_schema_hash,
    compute_model_c_schema_hash,
    compute_style_feature_schema_hash,
)
from russian_piano_composer.style_analysis.models import compute_model_spec_hash
from russian_piano_composer.style_analysis.permutation import (
    ExactComposerPermutationResult,
    compute_permutation_plan_hash,
)
from russian_piano_composer.style_analysis.splits import compute_composer_split_plan_hash
from russian_piano_composer.style_analysis.weighting import compute_composer_weighting_policy_hash

MASTER_BASELINE_SHA: str = "2aed82a4f13aa161743b25e30ad879baadc68b3f"


@dataclass(frozen=True, slots=True)
class StyleAnalysisLineage:
    """
    Immutable lineage hash bundle for RC-010 reproducibility.
    """

    master_baseline_sha: str
    manifest_hash: str
    rc009a_feature_schema_semantic_hash: str
    rc009a_feature_policy_hash: str
    rc009b_candidate_set_hash: str
    rc009b_discovery_policy_hash: str
    ctu_schema_semantic_hash: str
    representation_semantic_hash: str
    similarity_semantic_hash: str
    style_feature_schema_hash: str
    model_a_schema_hash: str
    model_b_schema_hash: str
    model_c_schema_hash: str
    role_blind_feature_matrix_hash: str
    label_assignment_hash: str
    composer_split_plan_hash: str
    model_spec_hash: str
    composer_weighting_policy_hash: str
    permutation_plan_hash: str
    evaluation_result_hash: str

    def compute_bundle_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the complete lineage bundle.
        """
        canonical = {
            "master_baseline_sha": self.master_baseline_sha,
            "manifest_hash": self.manifest_hash,
            "rc009a_feature_schema_semantic_hash": self.rc009a_feature_schema_semantic_hash,
            "rc009a_feature_policy_hash": self.rc009a_feature_policy_hash,
            "rc009b_candidate_set_hash": self.rc009b_candidate_set_hash,
            "rc009b_discovery_policy_hash": self.rc009b_discovery_policy_hash,
            "ctu_schema_semantic_hash": self.ctu_schema_semantic_hash,
            "representation_semantic_hash": self.representation_semantic_hash,
            "similarity_semantic_hash": self.similarity_semantic_hash,
            "style_feature_schema_hash": self.style_feature_schema_hash,
            "model_a_schema_hash": self.model_a_schema_hash,
            "model_b_schema_hash": self.model_b_schema_hash,
            "model_c_schema_hash": self.model_c_schema_hash,
            "role_blind_feature_matrix_hash": self.role_blind_feature_matrix_hash,
            "label_assignment_hash": self.label_assignment_hash,
            "composer_split_plan_hash": self.composer_split_plan_hash,
            "model_spec_hash": self.model_spec_hash,
            "composer_weighting_policy_hash": self.composer_weighting_policy_hash,
            "permutation_plan_hash": self.permutation_plan_hash,
            "evaluation_result_hash": self.evaluation_result_hash,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def compute_label_assignment_hash(piece_class_labels: dict[str, int]) -> str:
    """
    Deterministic SHA-256 hash of piece class labels.
    """
    canonical = {
        "labels": [
            {"piece_id": pid, "class_label": piece_class_labels[pid]}
            for pid in sorted(piece_class_labels.keys())
        ]
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_evaluation_result_hash(
    eval_c: ComposerHeldOutEvaluation,
    perm_result: ExactComposerPermutationResult,
) -> str:
    """
    Deterministic SHA-256 hash of complete primary evaluation results and all 20 permutation records.
    """
    canonical = {
        "model_name": eval_c.model_name,
        "macro_pair_auc": eval_c.macro_pair_auc,
        "num_folds_auc_gt_050": eval_c.num_folds_auc_gt_050,
        "fold_records": [
            {
                "fold_index": fr.fold_index,
                "held_out_russian": fr.held_out_russian,
                "held_out_control": fr.held_out_control,
                "n_test_russian_pieces": fr.n_test_russian_pieces,
                "n_test_control_pieces": fr.n_test_control_pieces,
                "roc_auc": fr.roc_auc,
                "balanced_accuracy": fr.balanced_accuracy,
                "sensitivity": fr.sensitivity,
                "specificity": fr.specificity,
                "brier_score": fr.brier_score,
            }
            for fr in eval_c.fold_results
        ],
        "composer_held_out_auc": eval_c.composer_held_out_auc,
        "permutation_records": [
            {
                "assignment_index": pr.assignment_index,
                "class_1_composers": list(pr.class_1_composers),
                "class_0_composers": list(pr.class_0_composers),
                "complement_assignment_index": pr.complement_assignment_index,
                "split_plan_hash": pr.split_plan_hash,
                "macro_pair_auc": pr.macro_pair_auc,
                "num_folds_auc_gt_050": pr.num_folds_auc_gt_050,
                "is_observed_assignment": pr.is_observed_assignment,
            }
            for pr in perm_result.permutation_records
        ],
        "all_permutation_aucs": list(perm_result.all_permutation_aucs),
        "extreme_count": perm_result.extreme_count,
        "exact_p_value": perm_result.exact_p_value,
        "observed_rank_min": perm_result.observed_rank_min,
        "observed_rank_max": perm_result.observed_rank_max,
        "observed_rank_interval": perm_result.observed_rank_interval,
        "tied_rank_count": perm_result.tied_rank_count,
        "minimum_attainable_p_value": perm_result.minimum_attainable_p_value,
        "symmetry_verified": perm_result.symmetry_verified,
        "empirical_status": perm_result.empirical_status.value,
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_style_analysis_lineage(
    manifest_hash: str,
    matrix_c: RoleBlindFeatureMatrix,
    piece_class_labels: dict[str, int],
    eval_c: ComposerHeldOutEvaluation,
    perm_result: ExactComposerPermutationResult,
) -> StyleAnalysisLineage:
    """
    Construct the full immutable lineage bundle for RC-010.
    """
    label_hash = compute_label_assignment_hash(piece_class_labels)
    eval_hash = compute_evaluation_result_hash(eval_c, perm_result)

    return StyleAnalysisLineage(
        master_baseline_sha=MASTER_BASELINE_SHA,
        manifest_hash=manifest_hash,
        rc009a_feature_schema_semantic_hash=compute_feature_schema_semantic_hash(FEATURE_REGISTRY),
        rc009a_feature_policy_hash=FeatureExtractionPolicy().compute_policy_hash(),
        rc009b_candidate_set_hash=ACCEPTED_RC009B_CANDIDATE_SET_HASH,
        rc009b_discovery_policy_hash=ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
        ctu_schema_semantic_hash=compute_ctu_schema_semantic_hash(),
        representation_semantic_hash=compute_segment_representation_semantic_hash(),
        similarity_semantic_hash=compute_similarity_semantic_hash(),
        style_feature_schema_hash=compute_style_feature_schema_hash(),
        model_a_schema_hash=compute_model_a_schema_hash(),
        model_b_schema_hash=compute_model_b_schema_hash(),
        model_c_schema_hash=compute_model_c_schema_hash(),
        role_blind_feature_matrix_hash=matrix_c.compute_matrix_hash(),
        label_assignment_hash=label_hash,
        composer_split_plan_hash=compute_composer_split_plan_hash(),
        model_spec_hash=compute_model_spec_hash(),
        composer_weighting_policy_hash=compute_composer_weighting_policy_hash(),
        permutation_plan_hash=compute_permutation_plan_hash(),
        evaluation_result_hash=eval_hash,
    )
