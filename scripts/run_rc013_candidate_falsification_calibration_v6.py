"""Execution Runner for Protocol V6 Genuine Differential Counterfactual Calibration.

Executes:
1. Positive controls on uncorrupted scholarly candidates (Chopin Mazurkas, Grieg Op. 12 No. 1, Schumann Op. 15 No. 1).
2. Deliberate single-fault candidate-corruption benchmark across core dimensions on real historical scans.
3. Untouched new final holdout evaluation: Antonín Dvořák - Silhouettes Op. 8 No. 1 (54 mm., Complete Edition / Supraphon, IMSLP59514).
4. Full 56-descriptor RC-011 feature-dependency fidelity audit.
5. Deterministic V6 calibration gate derivation and manifest freezing.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from typing import Any

from russian_piano_composer.corpus.rc013_bundle_hashing import (
    compute_calibration_v6_corpus_bundle_hash,
    compute_v6_counterfactual_benchmark_bundle_hash,
)
from russian_piano_composer.corpus.rc013_falsification_protocol import (
    PROTOCOL_VERSION,
    STATUS_DISPUTED,
    DifferentialEvidenceRecord,
    GenuineDifferentialVerifierV6,
    derive_v6_calibration_verdict,
)
from russian_piano_composer.corpus.rc013_feature_dependency import (
    audit_56_descriptor_dependencies,
)


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_v6_calibration() -> None:
    print("==================================================")
    print("   Running Protocol V6 Calibration Runner")
    print("==================================================")

    registry_path = "data/calibration/rc013_machine_validation/rc013_calibration_v6_registry.json"
    with open(registry_path, encoding="utf-8") as f:
        registry: list[dict[str, Any]] = json.load(f)

    verifier = GenuineDifferentialVerifierV6()
    benchmark_dir = "data/reviews/rc013/candidate_falsification_v6_benchmark"
    os.makedirs(benchmark_dir, exist_ok=True)

    positive_controls_results: list[dict[str, Any]] = []
    all_differential_records: list[DifferentialEvidenceRecord] = []

    # 1. Evaluate Positive Controls (Unaltered Scholarly Candidates)
    print("\n--- Step 1: Evaluating Positive Controls (Unmodified Candidates) ---")
    threshold_entries = [e for e in registry if e["split"] == "REAL_SCAN_THRESHOLD_CALIBRATION"]

    for entry in threshold_entries:
        s_id = entry["artifact_id"]
        xml_p = entry["ground_truth_path"]
        img_ps = entry["historical_page_image_paths"]

        eval_res = verifier.evaluate_candidate(
            candidate_musicxml_path=xml_p,
            source_image_paths=img_ps,
            score_id=s_id,
            benchmark_output_dir=benchmark_dir,
        )
        positive_controls_results.append(eval_res.to_dict())
        all_differential_records.extend(eval_res.differential_records)
        print(f"[{s_id}] Verdict: {eval_res.verdict} | Evaluated Measures: {eval_res.measures_evaluated}/{eval_res.measures_total}")
        for dim, st in eval_res.dimension_statuses.items():
            print(f"   -> {dim}: {st.status} (Tested: {st.mutations_tested}, Detected: {st.mutations_detected}, Mean Delta: {st.mean_delta:+.4f})")

    unmodified_fp_count = sum(1 for r in positive_controls_results if r["verdict"] == STATUS_DISPUTED)
    unmodified_fp_rate = unmodified_fp_count / max(len(positive_controls_results), 1)

    # 2. Evaluate Real-Scan Candidate Corruption Benchmark Sensitivity & Localization
    print("\n--- Step 2: Evaluating Real-Scan Candidate Corruption Benchmark ---")
    family_stats: dict[str, dict[str, Any]] = {}
    dimensions = ["pitch", "accidental", "octave", "duration", "rest"]

    for dim in dimensions:
        dim_records = [r for r in all_differential_records if r.mutation_dimension == dim]
        n_total = len(dim_records)
        n_detected = sum(1 for r in dim_records if r.delta > 0)
        n_wrong_loc = sum(1 for r in dim_records if r.delta > 0 and not r.is_correctly_localized)
        n_missed = sum(1 for r in dim_records if r.delta < 0)
        n_indet = sum(1 for r in dim_records if r.delta == 0)
        sens = (n_detected / n_total) if n_total > 0 else 0.0

        family_stats[dim] = {
            "n_total": n_total,
            "detected_and_localized": n_detected,
            "detected_wrong_localization": n_wrong_loc,
            "missed": n_missed,
            "indeterminate": n_indet,
            "sensitivity": round(sens, 4),
        }
        print(f"Family [{dim}]: {n_detected}/{n_total} detected ({sens*100:.1f}%) | Indeterminate: {n_indet} | Missed: {n_missed}")

    overall_tested = sum(s["n_total"] for s in family_stats.values())
    overall_detected = sum(s["detected_and_localized"] for s in family_stats.values())
    overall_sensitivity = (overall_detected / overall_tested) if overall_tested > 0 else 0.0

    # 3. Evaluate New Untouched Final Holdout (Dvorak Silhouettes Op. 8 No. 1)
    print("\n--- Step 3: Evaluating New Untouched Final Holdout (Dvorak Op. 8 No. 1) ---")
    holdout_entry = next(e for e in registry if e["split"] == "CALIBRATION_V6_FINAL_HOLDOUT")
    holdout_id = holdout_entry["artifact_id"]
    holdout_xml = holdout_entry["ground_truth_path"]
    holdout_imgs = holdout_entry["historical_page_image_paths"]

    holdout_res = verifier.evaluate_candidate(
        candidate_musicxml_path=holdout_xml,
        source_image_paths=holdout_imgs,
        score_id=holdout_id,
        benchmark_output_dir=benchmark_dir,
    )
    all_differential_records.extend(holdout_res.differential_records)
    print(f"[{holdout_id}] Verdict: {holdout_res.verdict} | Evaluated Measures: {holdout_res.measures_evaluated}/{holdout_res.measures_total}")
    for dim, st in holdout_res.dimension_statuses.items():
        print(f"   -> {dim}: {st.status} (Tested: {st.mutations_tested}, Detected: {st.mutations_detected}, Mean Delta: {st.mean_delta:+.4f})")

    holdout_passed = holdout_res.verdict != STATUS_DISPUTED

    # 4. Comprehensive 56-Descriptor Dependency Audit
    print("\n--- Step 4: Auditing 56 Descriptors from STRUCTURAL_REPRESENTATION_SCHEMA_V1 ---")
    schema_audit = audit_56_descriptor_dependencies()
    print(f"Total Descriptors: {schema_audit['schema_descriptor_count']}")
    print(f"Machine Supported: {schema_audit['machine_supported_count']} / 56 ({schema_audit['support_rate']*100:.2f}%)")
    print(f"Partially Supported: {schema_audit['partially_supported_count']} / 56")
    print(f"Unsupported Gaps: {schema_audit['unsupported_count']} / 56")

    # 5. Derive Final Calibration Gate Verdict
    print("\n--- Step 5: Deriving Protocol V6 Final Gate Verdict ---")
    final_verdict = derive_v6_calibration_verdict(
        positive_controls_fp_rate=unmodified_fp_rate,
        real_scan_sensitivity=overall_sensitivity,
        holdout_passed=holdout_passed,
        schema_support_rate=schema_audit["support_rate"],
    )
    print("==================================================")
    print(f"   PROTOCOL V6 CALIBRATION VERDICT: {final_verdict}")
    print("==================================================")

    # 6. Build Result Artifacts
    calib_bundle_hash = compute_calibration_v6_corpus_bundle_hash(registry_path)
    benchmark_bundle_hash = compute_v6_counterfactual_benchmark_bundle_hash(benchmark_dir)
    align_engine_hash = compute_file_sha256("src/russian_piano_composer/corpus/rc013_alignment.py")
    diff_metric_hash = compute_file_sha256("src/russian_piano_composer/corpus/rc013_falsification_protocol.py")
    audit_56_hash = compute_file_sha256("src/russian_piano_composer/corpus/rc013_feature_dependency.py")

    manifest_v6 = {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_hash": compute_file_sha256("src/russian_piano_composer/corpus/rc013_falsification_protocol.py"),
        "calibration_corpus_hash": calib_bundle_hash,
        "counterfactual_benchmark_bundle_hash": benchmark_bundle_hash,
        "alignment_engine_hash": align_engine_hash,
        "differential_metric_hash": diff_metric_hash,
        "descriptor_dependency_audit_hash": audit_56_hash,
        "calibrated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "operating_parameters": {
            "discrimination_rule": "delta_i = Di - D0 > 0",
            "normalized_delta_rule": "(Di - D0) / (Di + D0 + 1e-8)",
            "system_alignment_min_confidence": 0.60,
            "max_positive_control_fp_rate": 0.05,
            "min_real_scan_sensitivity": 0.90,
            "min_schema_support_rate": 0.95,
        },
        "final_holdout_score": {
            "artifact_id": holdout_id,
            "work": "Antonín Dvořák - Silhouettes Op. 8 No. 1",
            "measures_total": 54,
            "evaluation_verdict": holdout_res.verdict,
        },
        "calibration_gate_verdict": final_verdict,
        "downstream_authorities": {
            "candidate_falsification_receipts_can_qualify_composer": False,
            "rc012_resumption_permitted": False,
            "n_russian_derived": 2,
        },
    }

    manifest_p = "data/manifests/rc013_candidate_falsification_protocol_v6.json"
    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump(manifest_v6, f, indent=2)

    result_data = {
        "protocol_version": PROTOCOL_VERSION,
        "calibration_gate_verdict": final_verdict,
        "calibrated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "positive_controls": {
            "scores_evaluated": len(positive_controls_results),
            "false_positive_count": unmodified_fp_count,
            "false_positive_rate": unmodified_fp_rate,
            "results": positive_controls_results,
        },
        "counterfactual_benchmark_performance": {
            "overall_tested": overall_tested,
            "overall_detected": overall_detected,
            "overall_sensitivity": round(overall_sensitivity, 4),
            "family_breakdown": family_stats,
        },
        "final_holdout": holdout_res.to_dict(),
        "schema_dependency_audit": schema_audit,
    }

    result_p = "data/reviews/rc013/candidate_falsification_calibration_v6_result.json"
    with open(result_p, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2)

    print(f"Manifest written to: {manifest_p}")
    print(f"Result written to: {result_p}")


if __name__ == "__main__":
    run_v6_calibration()
