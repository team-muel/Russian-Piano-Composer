"""
True Two-Process Reproducibility Verification Script for RC-010 Style Discrimination.

Launches two independent Python subprocess workers.
Each worker independently loads the manifest, loads all 141 scores from disk,
builds role-blind feature matrices, executes 9-fold outer composer-held-out evaluation,
runs exact 20-composer permutation testing for MODEL_C, and produces a complete canonical payload JSON.
Compares exact detailed outputs, complete fold records, lineage hashes, and empirical status between Process A and Process B.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

WORKER_SCRIPT = """
import hashlib
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.style_analysis.evaluation import evaluate_model_across_folds
from russian_piano_composer.style_analysis.features import build_role_blind_feature_matrices
from russian_piano_composer.style_analysis.lineage import compute_style_analysis_lineage
from russian_piano_composer.style_analysis.permutation import run_exact_composer_permutation_test
from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    build_pair_holdout_plan,
    normalize_composer_name,
)
from russian_piano_composer.style_analysis.statistics import compute_feature_statistics


def run_worker(out_json_path: str) -> None:
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

    scores_by_id: dict[str, CanonicalScore] = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    if len(scores_by_id) != 141:
        raise RuntimeError(f"Expected 141 pieces, got {len(scores_by_id)}")

    # Construct role-blind matrices before attaching labels
    matrices = build_role_blind_feature_matrices(scores_by_id, manifest_hash=manifest_hash)
    mat_a = matrices["MODEL_A"]
    mat_b = matrices["MODEL_B"]
    mat_c = matrices["MODEL_C"]

    piece_composers: dict[str, str] = {}
    piece_class_labels: dict[str, int] = {}
    for piece_id, score in scores_by_id.items():
        comp_norm = normalize_composer_name(score.composer)
        piece_composers[piece_id] = comp_norm
        piece_class_labels[piece_id] = 1 if comp_norm in RUSSIAN_COMPOSERS else 0

    eval_a = evaluate_model_across_folds(mat_a, piece_composers, piece_class_labels)
    eval_b = evaluate_model_across_folds(mat_b, piece_composers, piece_class_labels)
    eval_c = evaluate_model_across_folds(mat_c, piece_composers, piece_class_labels)

    perm_res = run_exact_composer_permutation_test(mat_c, piece_composers, eval_c)
    feat_stats = compute_feature_statistics(mat_c, piece_composers, eval_c)

    lineage = compute_style_analysis_lineage(
        manifest_hash=manifest_hash,
        matrix_c=mat_c,
        piece_class_labels=piece_class_labels,
        eval_c=eval_c,
        perm_result=perm_res,
    )

    permutation_fold_plans = [
        {
            "assignment_index": pr.assignment_index,
            "folds": [
                {
                    "fold_index": f.fold_index,
                    "held_out_class_1": f.held_out_class_1,
                    "held_out_class_0": f.held_out_class_0,
                    "training_class_1": list(f.training_class_1),
                    "training_class_0": list(f.training_class_0),
                }
                for f in build_pair_holdout_plan(pr.class_1_composers, pr.class_0_composers).folds
            ],
        }
        for pr in perm_res.permutation_records
    ]

    payload = {
        "manifest_hash": manifest_hash,
        "piece_count": len(scores_by_id),
        "piece_ids": sorted(list(scores_by_id.keys())),
        "matrix_a_hash": mat_a.compute_matrix_hash(),
        "matrix_b_hash": mat_b.compute_matrix_hash(),
        "matrix_c_hash": mat_c.compute_matrix_hash(),
        "model_a_macro_auc": eval_a.macro_pair_auc,
        "model_b_macro_auc": eval_b.macro_pair_auc,
        "model_c_macro_auc": eval_c.macro_pair_auc,
        "delta_c_minus_a": round(eval_c.macro_pair_auc - eval_a.macro_pair_auc, 6),
        "delta_c_minus_b": round(eval_c.macro_pair_auc - eval_b.macro_pair_auc, 6),
        "composer_held_out_auc": eval_c.composer_held_out_auc,
        "exact_p_value": perm_res.exact_p_value,
        "extreme_count": perm_res.extreme_count,
        "total_assignments": perm_res.total_assignments,
        "observed_rank": perm_res.observed_rank,
        "observed_rank_min": perm_res.observed_rank_min,
        "observed_rank_max": perm_res.observed_rank_max,
        "observed_rank_interval": perm_res.observed_rank_interval,
        "tied_rank_count": perm_res.tied_rank_count,
        "minimum_attainable_p_value": perm_res.minimum_attainable_p_value,
        "empirical_status": perm_res.empirical_status.value,
        "all_permutation_aucs": list(perm_res.all_permutation_aucs),
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
            for pr in perm_res.permutation_records
        ],
        "permutation_fold_plans": permutation_fold_plans,
        "fold_results_c": [
            {
                "fold_index": fr.fold_index,
                "held_out_russian": fr.held_out_russian,
                "held_out_control": fr.held_out_control,
                "roc_auc": fr.roc_auc,
                "balanced_accuracy": fr.balanced_accuracy,
                "sensitivity": fr.sensitivity,
                "specificity": fr.specificity,
                "brier_score": fr.brier_score,
                "coefs": list(fr.coefs),
            }
            for fr in eval_c.fold_results
        ],
        "feature_statistics": [
            {
                "feature_id": r.feature_id,
                "family": r.feature_family,
                "observed_contrast": r.observed_contrast,
                "exact_p_value": r.exact_p_value,
                "fdr_q_value": r.fdr_q_value,
                "median_coefficient": r.median_coefficient,
                "is_directionally_stable": r.is_directionally_stable,
            }
            for r in feat_stats
        ],
        "lineage": {
            "master_baseline_sha": lineage.master_baseline_sha,
            "manifest_hash": lineage.manifest_hash,
            "rc009a_feature_schema_semantic_hash": lineage.rc009a_feature_schema_semantic_hash,
            "rc009a_feature_policy_hash": lineage.rc009a_feature_policy_hash,
            "rc009b_candidate_set_hash": lineage.rc009b_candidate_set_hash,
            "rc009b_discovery_policy_hash": lineage.rc009b_discovery_policy_hash,
            "ctu_schema_semantic_hash": lineage.ctu_schema_semantic_hash,
            "representation_semantic_hash": lineage.representation_semantic_hash,
            "similarity_semantic_hash": lineage.similarity_semantic_hash,
            "style_feature_schema_hash": lineage.style_feature_schema_hash,
            "model_a_schema_hash": lineage.model_a_schema_hash,
            "model_b_schema_hash": lineage.model_b_schema_hash,
            "model_c_schema_hash": lineage.model_c_schema_hash,
            "role_blind_feature_matrix_hash": lineage.role_blind_feature_matrix_hash,
            "label_assignment_hash": lineage.label_assignment_hash,
            "composer_split_plan_hash": lineage.composer_split_plan_hash,
            "model_spec_hash": lineage.model_spec_hash,
            "composer_weighting_policy_hash": lineage.composer_weighting_policy_hash,
            "permutation_plan_hash": lineage.permutation_plan_hash,
            "evaluation_result_hash": lineage.evaluation_result_hash,
            "bundle_hash": lineage.compute_bundle_hash(),
        },
    }

    payload_encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["process_payload_hash"] = hashlib.sha256(payload_encoded).hexdigest()

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    run_worker(sys.argv[1])
"""


def main() -> None:
    print("--- Running True Two-Process Style Discrimination Reproducibility Audit ---")
    sys.stdout.flush()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        worker_code_path = tmp_path / "worker.py"
        out_a_path = tmp_path / "out_a.json"
        out_b_path = tmp_path / "out_b.json"

        worker_code_path.write_text(WORKER_SCRIPT, encoding="utf-8")

        import os

        worker_env = os.environ.copy()
        worker_env["PYTHONPATH"] = "src"

        # Launch Worker Process A
        print("Launching Worker Process A...")
        sys.stdout.flush()
        proc_a = subprocess.run(
            [sys.executable, "-u", str(worker_code_path), str(out_a_path)],
            capture_output=True,
            text=True,
            check=False,
            env=worker_env,
        )
        if proc_a.returncode != 0:
            print(f"Process A FAILED:\n{proc_a.stderr}")
            sys.exit(1)

        # Launch Worker Process B
        print("Launching Worker Process B...")
        sys.stdout.flush()
        proc_b = subprocess.run(
            [sys.executable, "-u", str(worker_code_path), str(out_b_path)],
            capture_output=True,
            text=True,
            check=False,
            env=worker_env,
        )
        if proc_b.returncode != 0:
            print(f"Process B FAILED:\n{proc_b.stderr}")
            sys.exit(1)

        # Load both payloads
        payload_a = json.loads(out_a_path.read_text(encoding="utf-8"))
        payload_b = json.loads(out_b_path.read_text(encoding="utf-8"))

        # Direct structural equality comparison of complete payloads before comparing hashes
        payload_a_clean = {k: v for k, v in payload_a.items() if k != "process_payload_hash"}
        payload_b_clean = {k: v for k, v in payload_b.items() if k != "process_payload_hash"}

        if payload_a_clean != payload_b_clean:
            print("REPRODUCIBILITY ERROR: Process A and Process B complete clean payloads do NOT match!")
            sys.exit(1)

        print("  Process A Complete Payload == Process B Complete Payload: TRUE")

        hash_a = payload_a.get("process_payload_hash")
        hash_b = payload_b.get("process_payload_hash")

        print("\n--- Payload Hash Comparison ---")
        print(f"  Process A Payload Hash: {hash_a}")
        print(f"  Process B Payload Hash: {hash_b}")

        if hash_a != hash_b:
            print("REPRODUCIBILITY ERROR: Process A and Process B payload hashes do NOT match!")
            sys.exit(1)

        print("\n--- TRUE TWO-PROCESS STYLE DISCRIMINATION REPRODUCIBILITY AUDIT: PASS ---")
        print(f"  Processed Pieces:           {payload_a['piece_count']} / 141")
        print(f"  Matrix C Hash:              {payload_a['matrix_c_hash']}")
        print(f"  MODEL_C MACRO_PAIR_AUC:     {payload_a['model_c_macro_auc']:.4f}")
        print(f"  Exact Permutation p-value:  {payload_a['exact_p_value']:.4f}")
        print(f"  Empirical Status:           {payload_a['empirical_status']}")
        print(f"  Lineage Bundle Hash:        {payload_a['lineage']['bundle_hash']}")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
