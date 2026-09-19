"""
Style analysis package for RC-010 Russian-vs-Control Discriminative Music Science.

Provides role-blind feature matrix construction, composer-held-out splits,
composer-balanced sample weighting, deterministic classification models,
9-fold outer evaluation, exact 20-composer permutation testing, feature statistics,
and complete canonical lineage hashing.
"""

from russian_piano_composer.style_analysis.evaluation import (
    ComposerHeldOutEvaluation,
    evaluate_model_across_folds,
)
from russian_piano_composer.style_analysis.features import (
    CTU_STYLE_FEATURE_SCHEMA_VERSION,
    CTUStyleFeatureSchema,
    RoleBlindFeatureMatrix,
    build_role_blind_feature_matrices,
    compute_model_a_schema_hash,
    compute_model_b_schema_hash,
    compute_model_c_schema_hash,
    compute_style_feature_schema_hash,
)
from russian_piano_composer.style_analysis.lineage import (
    StyleAnalysisLineage,
    compute_style_analysis_lineage,
)
from russian_piano_composer.style_analysis.models import (
    ModelSpecification,
    compute_model_spec_hash,
)
from russian_piano_composer.style_analysis.permutation import (
    ExactComposerPermutationResult,
    run_exact_composer_permutation_test,
)
from russian_piano_composer.style_analysis.splits import (
    ComposerSplitPlan,
    build_composer_split_plan,
    build_pair_holdout_plan,
    compute_composer_split_plan_hash,
)
from russian_piano_composer.style_analysis.weighting import (
    ComposerWeightingPolicy,
    compute_composer_balanced_weights,
    compute_composer_weighting_policy_hash,
)

__all__ = [
    "CTU_STYLE_FEATURE_SCHEMA_VERSION",
    "CTUStyleFeatureSchema",
    "ComposerHeldOutEvaluation",
    "ComposerSplitPlan",
    "ComposerWeightingPolicy",
    "ExactComposerPermutationResult",
    "ModelSpecification",
    "RoleBlindFeatureMatrix",
    "StyleAnalysisLineage",
    "build_composer_split_plan",
    "build_pair_holdout_plan",
    "build_role_blind_feature_matrices",
    "compute_composer_balanced_weights",
    "compute_composer_split_plan_hash",
    "compute_composer_weighting_policy_hash",
    "compute_model_a_schema_hash",
    "compute_model_b_schema_hash",
    "compute_model_c_schema_hash",
    "compute_model_spec_hash",
    "compute_style_analysis_lineage",
    "compute_style_feature_schema_hash",
    "evaluate_model_across_folds",
    "run_exact_composer_permutation_test",
]
