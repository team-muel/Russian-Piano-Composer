"""
Primary execution script for RC-010 Russian-vs-Control Discriminative Music Science.

Runs 9-fold composer-held-out validation across MODEL_A, MODEL_B, and MODEL_C,
evaluates exact 20-composer-level permutation inference, feature-level contrasts,
and outputs complete scientific tables and lineage hashes.
"""

import sys
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest

if TYPE_CHECKING:
    from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.style_analysis.evaluation import evaluate_model_across_folds
from russian_piano_composer.style_analysis.features import build_role_blind_feature_matrices
from russian_piano_composer.style_analysis.lineage import compute_style_analysis_lineage
from russian_piano_composer.style_analysis.permutation import run_exact_composer_permutation_test
from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    normalize_composer_name,
)
from russian_piano_composer.style_analysis.statistics import compute_feature_statistics


def main() -> None:
    import warnings
    warnings.filterwarnings("ignore")

    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        print("Error: Canonical corpus parquet cache not found.")
        sys.exit(1)

    print("==========================================================================")
    print(" RC-010: Russian-vs-Control Discriminative Music Science Evaluation")
    print("==========================================================================")
    print(f"Canonical Manifest Hash: {manifest_hash}")

    # Step 1: Load scores without inspecting or attaching composer/role labels
    scores_by_id: dict[str, CanonicalScore] = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    if len(scores_by_id) != 141:
        raise RuntimeError(f"Expected 141 pieces, loaded {len(scores_by_id)}")

    # Step 2: Role-blind feature matrix construction BEFORE composer/role labels exist
    print("\n--- Constructing Role-Blind Feature Matrices ---")
    matrices = build_role_blind_feature_matrices(scores_by_id, manifest_hash=manifest_hash)
    mat_a = matrices["MODEL_A"]
    mat_b = matrices["MODEL_B"]
    mat_c = matrices["MODEL_C"]

    print(f"MODEL_A (Piece Features Only):  {len(mat_a.feature_names)} features | Matrix Hash: {mat_a.compute_matrix_hash()}")
    print(f"MODEL_B (CTU Features Only):    {len(mat_b.feature_names)} features | Matrix Hash: {mat_b.compute_matrix_hash()}")
    print(f"MODEL_C (Combined Primary):     {len(mat_c.feature_names)} features | Matrix Hash: {mat_c.compute_matrix_hash()}")

    # Check for missing values (fail-closed check)
    total_missing = 0
    for m in [mat_a, mat_b, mat_c]:
        for row in m.data:
            total_missing += sum(1 for v in row if v is None or (isinstance(v, float) and (v != v or abs(v) == float("inf"))))
    print(f"Missing Values in Primary Features: {total_missing} (Strict Fail-Closed Verified)")
    if total_missing > 0:
        raise RuntimeError(f"Found {total_missing} missing values in feature matrices!")

    # Step 3: Attach composer metadata and binary class labels for evaluation
    piece_composers: dict[str, str] = {}
    piece_class_labels: dict[str, int] = {}
    for piece_id, score in scores_by_id.items():
        comp_norm = normalize_composer_name(score.composer)
        piece_composers[piece_id] = comp_norm
        piece_class_labels[piece_id] = 1 if comp_norm in RUSSIAN_COMPOSERS else 0

    comp_counts = Counter(piece_composers.values())
    print("\nCorpus Composer Coverage:")
    for comp in ALL_COMPOSERS:
        print(f"  {comp}: {comp_counts[comp]} pieces")
    print(f"Total: {len(scores_by_id)} pieces")

    # Step 4: Outer 9-fold evaluation across models
    print("\n--- Running 9 Outer Composer-Pair Held-Out Folds ---")
    eval_a = evaluate_model_across_folds(mat_a, piece_composers, piece_class_labels)
    eval_b = evaluate_model_across_folds(mat_b, piece_composers, piece_class_labels)
    eval_c = evaluate_model_across_folds(mat_c, piece_composers, piece_class_labels)

    print("\n9-Fold Held-Out Evaluation Matrix:")
    print(f"{'Fold':<6} | {'Held-Out Russian':<12} | {'Held-Out Control':<16} | {'Rus Test':<8} | {'Ctrl Test':<9} | {'MODEL_A AUC':<11} | {'MODEL_B AUC':<11} | {'MODEL_C AUC':<11} | {'MODEL_C BalAcc':<14}")
    print("-" * 115)
    for fa, fb, fc in zip(eval_a.fold_results, eval_b.fold_results, eval_c.fold_results, strict=True):
        print(f"{fa.fold_index:<6} | {fa.held_out_russian:<12} | {fa.held_out_control:<16} | {fa.n_test_russian_pieces:<8} | {fa.n_test_control_pieces:<9} | {fa.roc_auc:<11.4f} | {fb.roc_auc:<11.4f} | {fc.roc_auc:<11.4f} | {fc.balanced_accuracy:<14.4f}")

    # Step 5: Model Ablation & Performance Comparison
    print("\n--- Model Ablation Comparison ---")
    print(f"MODEL_A MACRO_PAIR_AUC (Piece Features Only): {eval_a.macro_pair_auc:.4f}")
    print(f"MODEL_B MACRO_PAIR_AUC (CTU Features Only):   {eval_b.macro_pair_auc:.4f}")
    print(f"MODEL_C MACRO_PAIR_AUC (PRIMARY Combined):    {eval_c.macro_pair_auc:.4f}")
    delta_c_a = eval_c.macro_pair_auc - eval_a.macro_pair_auc
    delta_c_b = eval_c.macro_pair_auc - eval_b.macro_pair_auc
    print(f"Delta (MODEL_C - MODEL_A):                      {delta_c_a:+.4f}")
    print(f"Delta (MODEL_C - MODEL_B):                      {delta_c_b:+.4f}")

    print("\nComposer-Side Generalization Held-Out AUC:")
    for comp in ALL_COMPOSERS:
        print(f"  {comp:<14}: {eval_c.composer_held_out_auc[comp]:.4f}")

    # Step 6: Exact 20-Composer-Level Permutation Test (Dynamic Assignment Folds)
    print("\n--- Running Exact 20-Composer-Level Permutation Test ---")
    perm_res = run_exact_composer_permutation_test(mat_c, piece_composers, eval_c)
    print(f"Observed MODEL_C MACRO_PAIR_AUC: {perm_res.observed_macro_pair_auc:.4f}")
    print(f"Observed Rank (Standard):        {perm_res.observed_rank} / {perm_res.total_assignments}")
    print(f"Observed Rank Interval (Ties):   {perm_res.observed_rank_interval}")
    print(f"Tied Assignments Count:          {perm_res.tied_rank_count}")
    print(f"Extreme Count (AUC >= Observed): {perm_res.extreme_count} / {perm_res.total_assignments}")
    print(f"Exact Permutation p-value:       {perm_res.exact_p_value:.4f}")
    print(f"Minimum Attainable p-value:      {perm_res.minimum_attainable_p_value:.4f}")
    print(f"Folds with AUC > 0.50:           {eval_c.num_folds_auc_gt_050} / 9")

    # Step 7: Feature-Level Interpretation & Statistics
    print("\n--- Feature-Level Descriptive Analysis & Stability ---")
    feat_stats = compute_feature_statistics(mat_c, piece_composers, eval_c)

    print(f"{'Feature ID':<38} | {'Family':<7} | {'Rus Mean':<8} | {'Ctrl Mean':<9} | {'Contrast':<8} | {'Exact p':<7} | {'FDR q':<7} | {'Med Coef':<8} | {'Stable':<6}")
    print("-" * 115)
    for rec in feat_stats:
        stable_str = "YES" if rec.is_directionally_stable else "NO"
        print(f"{rec.feature_id:<38} | {rec.feature_family:<7} | {rec.russian_composer_mean:<8.4f} | {rec.control_composer_mean:<9.4f} | {rec.observed_contrast:<+8.4f} | {rec.exact_p_value:<7.4f} | {rec.fdr_q_value:<7.4f} | {rec.median_coefficient:<+8.4f} | {stable_str:<6}")

    # Step 8: Lineage Hashes
    lineage = compute_style_analysis_lineage(
        manifest_hash=manifest_hash,
        matrix_c=mat_c,
        piece_class_labels=piece_class_labels,
        eval_c=eval_c,
        perm_result=perm_res,
    )

    print("\n--- Lineage Hashes ---")
    print(f"  Master Baseline SHA:         {lineage.master_baseline_sha}")
    print(f"  Canonical Manifest Hash:     {lineage.manifest_hash}")
    print(f"  RC-009A Schema Sem. Hash:    {lineage.rc009a_feature_schema_semantic_hash}")
    print(f"  RC-009A Policy Hash:         {lineage.rc009a_feature_policy_hash}")
    print(f"  RC-009B Candidate Set Hash:  {lineage.rc009b_candidate_set_hash}")
    print(f"  RC-009B Disc. Policy Hash:   {lineage.rc009b_discovery_policy_hash}")
    print(f"  CTU Schema Semantic Hash:    {lineage.ctu_schema_semantic_hash}")
    print(f"  Representation Sem. Hash:    {lineage.representation_semantic_hash}")
    print(f"  Similarity Semantic Hash:    {lineage.similarity_semantic_hash}")
    print(f"  Style Feature Schema Hash:   {lineage.style_feature_schema_hash}")
    print(f"  MODEL_A Schema Hash:         {lineage.model_a_schema_hash}")
    print(f"  MODEL_B Schema Hash:         {lineage.model_b_schema_hash}")
    print(f"  MODEL_C Schema Hash:         {lineage.model_c_schema_hash}")
    print(f"  Role-Blind Matrix Hash:      {lineage.role_blind_feature_matrix_hash}")
    print(f"  Label Assignment Hash:       {lineage.label_assignment_hash}")
    print(f"  Composer Split Plan Hash:    {lineage.composer_split_plan_hash}")
    print(f"  Model Specification Hash:    {lineage.model_spec_hash}")
    print(f"  Weighting Policy Hash:       {lineage.composer_weighting_policy_hash}")
    print(f"  Permutation Plan Hash:       {lineage.permutation_plan_hash}")
    print(f"  Evaluation Result Hash:      {lineage.evaluation_result_hash}")
    print(f"  Bundle Lineage Hash:         {lineage.compute_bundle_hash()}")

    # Step 9: Scientific Limitations Statement
    print("\n--- Mandatory Scientific Limitations Statement ---")
    print("1. Only six composers are represented in the canonical corpus.")
    print("2. Composer identity and national/style class are structurally confounded in source corpora.")
    print("3. Composer-pair hold-out reduces memorization risk but does not create independent evidence from unseen historical traditions.")
    print("4. Exact permutation inference has 20 composer-label assignments with 10 complement pairs (min attainable p-value = 0.10 under label symmetry; p <= 0.05 structurally unattainable for N=6).")
    print("5. RC-010 tests discriminability within the canonical six-composer corpus, not a universal definition of Russian music.")
    print("6. Human aesthetic judgment is not validated here.")
    print("7. Successful discrimination does not by itself justify generative composition.")

    # Step 10: Final Empirical Status
    print("\n==========================================================================")
    print(f" EMPIRICAL STYLE STATUS = {perm_res.empirical_status.value}")
    print("==========================================================================")
    sys.stdout.flush()


if __name__ == "__main__":
    main()

