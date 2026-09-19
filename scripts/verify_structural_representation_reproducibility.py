"""
True Two-Process Structural Representation Reproducibility Verification for RC-011.

Launches two independent Python subprocesses to execute full structural extraction,
dynamic RC-009B candidate set validation, synthetic fixture validation, and matrix generation,
requiring byte-for-byte and structural payload equality.
"""

import hashlib
import json
import subprocess
import sys

WORKER_SCRIPT = """
import json
import sys
import hashlib
from pathlib import Path
from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import compute_candidate_set_hash
from russian_piano_composer.structure_analysis.extractor import StructuralExtractionPolicy, extract_structural_representation
from russian_piano_composer.structure_analysis.matrix import build_structural_representation_matrix
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus
from russian_piano_composer.structure_analysis.validation import (
    FIXTURE_REGISTRY,
    compute_fixture_semantic_hash,
    run_synthetic_and_metamorphic_validation,
)
from russian_piano_composer.structure_analysis.lineage import (
    compute_structural_representation_lineage,
    verify_prior_milestone_hashes_fail_closed,
)

manifest_path = Path("data/manifests/corpus_manifest.yaml")
manifest = load_manifest(manifest_path)
manifest_hash = manifest.compute_manifest_hash()
interim_base = Path("data/interim/canonical") / manifest_hash

scores_by_id = {}
for source in manifest.sources:
    corpus_dir = interim_base / source.corpus_id
    for entry_id in source.score_entry_ids:
        piece_id = f"{source.corpus_id}:{entry_id}"
        scores_by_id[piece_id] = load_canonical_score_from_parquet(corpus_dir, piece_id)

policy = StructuralExtractionPolicy()

discovery_results = []
for pid, score in sorted(scores_by_id.items()):
    disc_res = discover_ctus_for_score(
        score, manifest_hash=manifest_hash, policy=policy.ctu_discovery_policy
    )
    discovery_results.append(disc_res)

dyn_candidate_set_hash = compute_candidate_set_hash(discovery_results)
verify_prior_milestone_hashes_fail_closed(
    manifest_hash=manifest_hash,
    dynamically_computed_candidate_set_hash=dyn_candidate_set_hash,
)

piece_representations = {}
for disc_res, (pid, score) in zip(discovery_results, sorted(scores_by_id.items()), strict=True):
    rep = extract_structural_representation(
        score, manifest_hash=manifest_hash, policy=policy, retained_ctus=disc_res.retained_ctus
    )
    piece_representations[pid] = rep.features

matrix = build_structural_representation_matrix(piece_representations, manifest_hash=manifest_hash)

avail_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.AVAILABLE)
sz_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.STRUCTURAL_ZERO)
unavail_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.UNAVAILABLE)

excl_path = Path("docs/research/RC011_EXCLUSION_LEDGER.md")
excl_hash = hashlib.sha256(excl_path.read_bytes()).hexdigest() if excl_path.exists() else "0" * 64

val_result = run_synthetic_and_metamorphic_validation(
    available_cells=avail_cnt,
    structural_zero_cells=sz_cnt,
    unavailable_cells=unavail_cnt,
    exclusion_ledger_hash=excl_hash,
)

lineage = compute_structural_representation_lineage(
    manifest_hash=manifest_hash,
    matrix=matrix,
    val_result=val_result,
    exclusion_ledger_hash=excl_hash,
    policy=policy,
    dynamically_computed_candidate_set_hash=dyn_candidate_set_hash,
)

fixture_records = []
for f in FIXTURE_REGISTRY:
    sc = f.builder()
    ev_list = [
        {
            "measure": e.measure_index,
            "onset": str(e.global_onset),
            "offset": str(e.offset_in_measure),
            "duration": str(e.duration),
            "midi": e.midi,
            "staff": e.staff,
            "voice": e.voice,
        }
        for e in sc.events
    ]
    fixture_records.append({
        "fixture_id": f.fixture_id,
        "name": f.name,
        "family": f.family_owner.value,
        "semantic_hash": compute_fixture_semantic_hash(sc),
        "events": ev_list,
    })

prior_dynamic_hashes = {
    "manifest_hash": manifest_hash,
    "rc009a_feature_schema_semantic_hash": lineage.rc009a_feature_schema_semantic_hash,
    "rc009a_feature_policy_hash": lineage.rc009a_feature_policy_hash,
    "rc009b_discovery_policy_hash": lineage.rc009b_discovery_policy_hash,
    "rc009b_candidate_set_hash": lineage.rc009b_candidate_set_hash,
    "rc009b_ctu_schema_semantic_hash": lineage.ctu_schema_semantic_hash,
    "rc009b_representation_semantic_hash": lineage.representation_semantic_hash,
    "rc009b_similarity_semantic_hash": lineage.similarity_semantic_hash,
    "dynamically_regenerated_candidate_set_hash": dyn_candidate_set_hash,
}

parameter_policy_hashes = {
    "tonal_policy_hash": lineage.tonal_policy_hash,
    "sonority_policy_hash": lineage.sonority_policy_hash,
    "cadence_policy_hash": lineage.cadence_policy_hash,
    "form_policy_hash": lineage.form_policy_hash,
    "vl_policy_hash": lineage.vl_policy_hash,
    "texture_policy_hash": lineage.texture_policy_hash,
    "trajectory_policy_hash": lineage.trajectory_policy_hash,
}

semantic_hashes = {
    "tonal_semantic_hash": lineage.tonal_semantic_hash,
    "sonority_semantic_hash": lineage.sonority_semantic_hash,
    "cadence_semantic_hash": lineage.cadence_semantic_hash,
    "form_semantic_hash": lineage.form_semantic_hash,
    "vl_semantic_hash": lineage.vl_semantic_hash,
    "texture_semantic_hash": lineage.texture_semantic_hash,
    "trajectory_semantic_hash": lineage.trajectory_semantic_hash,
    "metamorphic_test_matrix_hash": lineage.metamorphic_test_matrix_hash,
    "structure_analysis_source_hash": lineage.structure_analysis_source_hash,
    "rc011_implementation_commit_sha": lineage.rc011_implementation_commit_sha,
}

payload = {
    "manifest_hash": manifest_hash,
    "structural_schema_hash": lineage.structural_schema_hash,
    "structural_matrix_hash": lineage.structural_matrix_hash,
    "validation_result_hash": lineage.validation_result_hash,
    "lineage_bundle_hash": lineage.compute_bundle_hash(),
    "fixture_records": fixture_records,
    "prior_dynamic_hashes": prior_dynamic_hashes,
    "parameter_policy_hashes": parameter_policy_hashes,
    "semantic_hashes": semantic_hashes,
    "contract_hashes": {
        "synthetic_fixture_suite_hash": lineage.synthetic_fixture_suite_hash,
        "assertion_contract_hash": lineage.assertion_contract_hash,
        "invariance_contract_hash": lineage.invariance_contract_hash,
        "preregistration_amendment_hash": lineage.preregistration_amendment_hash,
        "exclusion_ledger_hash": lineage.exclusion_ledger_hash,
    },
    "piece_ids": list(matrix.piece_ids),
    "feature_names": list(matrix.feature_names),
    "matrix_data": [list(row) for row in matrix.data],
    "matrix_availability": [[st.value for st in r] for r in matrix.availability_matrix],
    "matrix_reasons": [list(r) for r in matrix.reasons_matrix],
    "fixture_count": val_result.fixture_count,
    "assertions": [
        {
            "assertion_id": a.assertion_id,
            "fixture_id": a.fixture_id,
            "family": a.family.value,
            "passed": a.passed,
            "condition": a.condition_description,
            "summary": a.actual_value_summary,
        }
        for a in val_result.assertion_records
    ],
    "metamorphic_records": [
        {
            "feature_id": m.feature_id,
            "fixture_id": m.fixture_id,
            "transformation": m.transformation.value,
            "transformation_parameter": str(m.transformation_parameter),
            "original_value": round(m.original_value, 6),
            "original_availability_status": m.original_availability_status.value,
            "original_reason": m.original_reason,
            "transformed_value": round(m.transformed_value, 6),
            "transformed_availability_status": m.transformed_availability_status.value,
            "transformed_reason": m.transformed_reason,
            "expected_behavior": m.expected_behavior.value,
            "expected_relation": m.expected_relation,
            "actual_relation": m.actual_relation,
            "passed": m.passed,
        }
        for m in val_result.metamorphic_records
    ],
    "family_statuses": [
        {
            "family": fs.family.value,
            "status": fs.status,
            "passed_assertions": fs.passed_assertions,
            "total_assertions": fs.total_assertions,
            "passed_metamorphic": fs.passed_metamorphic,
            "total_metamorphic": fs.total_metamorphic,
        }
        for fs in val_result.family_statuses
    ],
    "coverage": {
        "available_cells": avail_cnt,
        "structural_zero_cells": sz_cnt,
        "unavailable_cells": unavail_cnt,
    },
    "overall_status": val_result.overall_status,
}

print("JSON_START")
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
print("JSON_END")
"""


def _run_workers() -> tuple[dict, dict]:
    print("Launching Worker Process A and Worker Process B concurrently...")
    proc_a = subprocess.Popen(
        [sys.executable, "-c", WORKER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    proc_b = subprocess.Popen(
        [sys.executable, "-c", WORKER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout_a, stderr_a = proc_a.communicate()
    stdout_b, stderr_b = proc_b.communicate()
    if proc_a.returncode != 0:
        raise RuntimeError(f"Worker A failed with code {proc_a.returncode}:\n{stderr_a}")
    if proc_b.returncode != 0:
        raise RuntimeError(f"Worker B failed with code {proc_b.returncode}:\n{stderr_b}")

    def _parse(stdout: str, name: str) -> dict:
        if "JSON_START" not in stdout or "JSON_END" not in stdout:
            raise RuntimeError(f"Worker {name} output missing JSON delimiters:\n{stdout}")
        return json.loads(stdout.split("JSON_START")[1].split("JSON_END")[0].strip())

    return _parse(stdout_a, "A"), _parse(stdout_b, "B")


def main() -> None:
    print("--- Running True Two-Process Structural Representation Reproducibility Audit ---")

    payload_a, payload_b = _run_workers()

    # 1. Direct Structural Comparison
    is_structurally_equal = (payload_a == payload_b)
    print(f"  Process A Complete Payload == Process B Complete Payload: {str(is_structurally_equal).upper()}")
    if not is_structurally_equal:
        raise RuntimeError("True two-process payload inequality detected!")

    # 2. SHA-256 Payload Hash Comparison
    hash_a = hashlib.sha256(json.dumps(payload_a, sort_keys=True).encode("utf-8")).hexdigest()
    hash_b = hashlib.sha256(json.dumps(payload_b, sort_keys=True).encode("utf-8")).hexdigest()

    print("\n--- Payload Hash Comparison ---")
    print(f"  Process A Payload Hash: {hash_a}")
    print(f"  Process B Payload Hash: {hash_b}")

    if hash_a != hash_b:
        raise RuntimeError(f"Payload hash mismatch! A: {hash_a} != B: {hash_b}")

    print("\n--- TRUE TWO-PROCESS STRUCTURAL REPRODUCIBILITY AUDIT: PASS ---")
    print(f"  Structural Schema Hash: {payload_a['structural_schema_hash']}")
    print(f"  Structural Matrix Hash: {payload_a['structural_matrix_hash']}")
    print(f"  Validation Result Hash: {payload_a['validation_result_hash']}")
    print(f"  Lineage Bundle Hash:    {payload_a['lineage_bundle_hash']}")
    print(f"  Overall Status:         {payload_a['overall_status']}")


if __name__ == "__main__":
    main()
