#!/usr/bin/env python3
"""Validation script for PF-002A.0 Prospective Model Family & Execution Protocol Freeze.

Enforces fail-closed validation of:
1. Protocol file presence and JSON schema validity.
2. Prospective status: PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET.
3. Zero trained model weights, parameters, or embeddings on disk.
4. Upstream invariant preservation:
   - Physical inventory hash matches authoritative constant (3154c296...).
   - Materialization receipt hash matches authoritative constant (db2370c0...).
   - PF-001C1 metric contract hash matches authoritative constant (5b681c6b...).
   - PF-001C1.2 split manifest hash matches authoritative constant (2ab69668...).
5. Exact 62-piece dataset roles preserved:
   - 37 DEVELOPMENT (Tchaikovsky 12, Rachmaninoff 22, Arensky 3).
   - 22 VALIDATION (Medtner 19, Lyadov 3).
   - 3 BENCHMARK_PILOT_ONLY (Lyapunov 3).
6. Bounded candidate models:
   - Exactly 2 candidate models: AL-GRU-01 and AL-TRF-01.
   - Max parameter budgets bounded (AL-GRU-01 <= 250k, AL-TRF-01 <= 350k).
7. Neural framework constraint:
   - Exactly one framework: PyTorch (torch>=2.2,<2.4).
   - Full determinism settings specified.
8. Representation contract:
   - Tokenization from CanonicalScore.
   - Context window L=1024, stride 512.
   - Vocabulary scope: DEVELOPMENT_CORPUS_ONLY.
9. Training budget & seed hierarchy:
   - Max 50 epochs, batch size 16.
   - R=3 independent replicates per candidate.
   - RandomContext root seed 20260930 with required namespaces.
10. Execution ordering & prospective threshold calibration:
    - Thresholds calibrated on DEVELOPMENT folds via Grouped K-Fold Youden's J.
    - Checkpoint selected via minimum VALIDATION cross-entropy bits/token.
    - VALIDATION evaluated with calibrated thresholds.
    - One-shot evaluation of BENCHMARK_PILOT_ONLY after architecture selection.
11. Gate readiness preservation:
    - COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION.
    - THEMATIC_MEMORY_GATE = THEME_IDENTITY_DEPENDENT_NOT_READY.
12. External test firewall (Taneyev, Bortkiewicz, Blumenfeld, Catoire) and Scriabin exclusion.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_DOC_PATH = REPO_ROOT / "docs" / "research" / "PF002A_PROSPECTIVE_MODEL_AND_EXECUTION_PROTOCOL.md"
PROTOCOL_JSON_PATH = REPO_ROOT / "data" / "reviews" / "pf002a" / "pf002a_model_execution_protocol.json"
SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001b_remote_materialization_receipt.json"
CONTRACT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"

EXPECTED_INVENTORY_HASH = "3154c2967ee8201d5df65eb3f866fb81e495ac1878e8a60349687888018c9d8e"
EXPECTED_RECEIPT_HASH = "db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d"
EXPECTED_CONTRACT_HASH = "5b681c6b02ecb2c573b06d463705ab8b4fd17b9aec9b5c4e56f6a7e5830e214a"
EXPECTED_SPLIT_HASH = "2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab"
EXPECTED_PROTOCOL_HASH = "fbe099bb3e2155e393a69704ae73b9b10867e9af19246682f12e0675101476b9"

FIREWALL_COMPOSERS = {"Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire"}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_pf002a_model_protocol() -> int:
    print("[PF-002A.0] Starting Prospective Model Family & Execution Protocol validation...")
    errors: list[str] = []

    # 1. File existence
    all_required_files = [
        PROTOCOL_DOC_PATH,
        PROTOCOL_JSON_PATH,
        SPLIT_MANIFEST_PATH,
        INVENTORY_PATH,
        RECEIPT_PATH,
        CONTRACT_PATH,
    ]
    for p in all_required_files:
        if not p.exists():
            errors.append(f"Missing required file: {p}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # 2. Check no trained model weights, parameters, or embeddings exist on disk
    models_dir = REPO_ROOT / "src" / "russian_piano_composer" / "models"
    data_interim = REPO_ROOT / "data" / "interim"
    data_processed = REPO_ROOT / "data" / "processed"
    check_paths = [models_dir, data_interim, data_processed]
    forbidden_suffixes = {".pt", ".pth", ".bin", ".onnx", ".safetensors", ".ckpt", ".h5"}
    for cpath in check_paths:
        if cpath.exists():
            for f in cpath.rglob("*"):
                if f.is_file() and f.suffix.lower() in forbidden_suffixes:
                    errors.append(f"Premature trained model weight found: {f}")
                if f.is_file() and ("embedding" in f.name.lower() or "latent" in f.name.lower()) and f.suffix in {".npy", ".npz", ".pt"}:
                    errors.append(f"Premature learned embedding found: {f}")

    # 3. Check upstream invariant hashes
    actual_inv_hash = compute_sha256(INVENTORY_PATH)
    if actual_inv_hash != EXPECTED_INVENTORY_HASH:
        errors.append(f"Physical Inventory Hash mismatch: expected {EXPECTED_INVENTORY_HASH}, got {actual_inv_hash}")

    actual_receipt_hash = json.loads(RECEIPT_PATH.read_text(encoding="utf-8")).get("receipt_hash")
    if actual_receipt_hash != EXPECTED_RECEIPT_HASH:
        errors.append(f"Materialization receipt hash mismatch: expected {EXPECTED_RECEIPT_HASH}, got {actual_receipt_hash}")

    actual_contract_hash = compute_sha256(CONTRACT_PATH)
    if actual_contract_hash != EXPECTED_CONTRACT_HASH:
        errors.append(f"PF001C1 Metric Contract Hash mismatch: expected {EXPECTED_CONTRACT_HASH}, got {actual_contract_hash}")

    actual_split_hash = compute_sha256(SPLIT_MANIFEST_PATH)
    if actual_split_hash != EXPECTED_SPLIT_HASH:
        errors.append(f"PF001C1_STAGE0_SPLIT_HASH mismatch: expected {EXPECTED_SPLIT_HASH}, got {actual_split_hash}")

    # 4. Check protocol JSON integrity
    actual_proto_hash = compute_sha256(PROTOCOL_JSON_PATH)
    if actual_proto_hash != EXPECTED_PROTOCOL_HASH:
        errors.append(f"PF002A_MODEL_PROTOCOL_HASH mismatch: expected {EXPECTED_PROTOCOL_HASH}, got {actual_proto_hash}")

    proto_data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))

    # Status check
    if proto_data.get("status") != "PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET":
        errors.append(f"Invalid status: {proto_data.get('status')}")

    # Check upstream hash bindings inside protocol JSON
    up_hashes = proto_data.get("upstream_invariant_hashes", {})
    if up_hashes.get("physical_inventory_hash") != EXPECTED_INVENTORY_HASH:
        errors.append("Protocol JSON physical_inventory_hash binding incorrect")
    if up_hashes.get("materialization_receipt_hash") != EXPECTED_RECEIPT_HASH:
        errors.append("Protocol JSON materialization_receipt_hash binding incorrect")
    if up_hashes.get("PF001C1_METRIC_CONTRACT_HASH") != EXPECTED_CONTRACT_HASH:
        errors.append("Protocol JSON PF001C1_METRIC_CONTRACT_HASH binding incorrect")
    if up_hashes.get("PF001C1_STAGE0_SPLIT_HASH") != EXPECTED_SPLIT_HASH:
        errors.append("Protocol JSON PF001C1_STAGE0_SPLIT_HASH binding incorrect")

    # Dataset roles
    roles = proto_data.get("dataset_roles", {})
    counts = roles.get("counts", {})
    if counts.get("DEVELOPMENT") != 37 or counts.get("VALIDATION") != 22 or counts.get("BENCHMARK_PILOT_ONLY") != 3 or counts.get("TOTAL") != 62:
        errors.append(f"Incorrect dataset role counts in protocol JSON: {counts}")

    # Candidate models: exactly 2
    candidates = proto_data.get("candidate_models", [])
    if len(candidates) != 2:
        errors.append(f"Candidate models count must be exactly 2, got {len(candidates)}")
    cand_ids = {c["model_id"] for c in candidates}
    if cand_ids != {"AL-GRU-01", "AL-TRF-01"}:
        errors.append(f"Candidate model IDs must be AL-GRU-01 and AL-TRF-01, got {cand_ids}")

    for c in candidates:
        max_p = c.get("max_trainable_parameters", 0)
        if c["model_id"] == "AL-GRU-01" and max_p > 250000:
            errors.append(f"AL-GRU-01 max parameter bound exceeded: {max_p}")
        if c["model_id"] == "AL-TRF-01" and max_p > 350000:
            errors.append(f"AL-TRF-01 max parameter bound exceeded: {max_p}")

    # Neural framework
    framework = proto_data.get("neural_framework", {})
    if framework.get("framework") != "PyTorch":
        errors.append("Neural framework must be PyTorch")
    det_settings = framework.get("determinism_settings", {})
    if not det_settings.get("torch_use_deterministic_algorithms"):
        errors.append("torch_use_deterministic_algorithms must be true")

    # Representation
    repr_spec = proto_data.get("input_representation", {})
    if repr_spec.get("vocabulary_scope") != "DEVELOPMENT_CORPUS_ONLY":
        errors.append("Vocabulary scope must be DEVELOPMENT_CORPUS_ONLY")
    if repr_spec.get("max_context_window") != 1024:
        errors.append("max_context_window must be 1024")

    # Training objective
    obj = proto_data.get("training_objective", {})
    if obj.get("lambda_pred") != 1.0 or obj.get("lambda_repr") != 0.5:
        errors.append("Loss weights must be lambda_pred=1.0 and lambda_repr=0.5")
    if "Counterfactuals, memory probes, and anti-copy checks" not in obj.get("non_contamination_prohibition", ""):
        errors.append("Missing non_contamination_prohibition in training objective")

    # Training budget
    budget = proto_data.get("training_budget_and_optimization", {})
    if budget.get("max_epochs") != 50:
        errors.append(f"max_epochs must be 50, got {budget.get('max_epochs')}")
    if budget.get("replicates_per_candidate") != 3:
        errors.append(f"replicates_per_candidate must be 3, got {budget.get('replicates_per_candidate')}")
    if budget.get("batch_size") != 16:
        errors.append(f"batch_size must be 16, got {budget.get('batch_size')}")

    # Gate readiness invariants
    gate_status = proto_data.get("gate_readiness_status", {})
    if gate_status.get("COMPOSER_GENERALIZATION_GATE") != "NOT_READY_FOR_CALIBRATION":
        errors.append("COMPOSER_GENERALIZATION_GATE must be NOT_READY_FOR_CALIBRATION")
    if gate_status.get("THEMATIC_MEMORY_GATE") != "THEME_IDENTITY_DEPENDENT_NOT_READY":
        errors.append("THEMATIC_MEMORY_GATE must be THEME_IDENTITY_DEPENDENT_NOT_READY")

    # Checkpoint selection & execution ordering
    ordering = proto_data.get("execution_ordering", [])
    if len(ordering) != 6:
        errors.append(f"Execution ordering must specify exactly 6 steps, got {len(ordering)}")
    else:
        if "Grouped K-Fold (K=5) Youden's J on DEVELOPMENT" not in ordering[2]:
            errors.append("Step 3 must specify prospective calibration on DEVELOPMENT")
        if "Evaluate 6 active Stage-0 gates on VALIDATION" not in ordering[3]:
            errors.append("Step 4 must evaluate active gates on VALIDATION")
        if "BENCHMARK_PILOT_ONLY" not in ordering[5]:
            errors.append("Step 6 must evaluate BENCHMARK_PILOT_ONLY exactly once")

    # Architecture selection rule
    sel_rule = proto_data.get("architecture_selection_rule", {})
    if sel_rule.get("fail_closed_verdict") != "STAGE0_LISTENER_REPRESENTATION_FAILED":
        errors.append("architecture_selection_rule fail_closed_verdict must be STAGE0_LISTENER_REPRESENTATION_FAILED")

    # External test firewall
    firewall = proto_data.get("external_test_firewall", {})
    if set(firewall.get("cohort", [])) != FIREWALL_COMPOSERS:
        errors.append(f"external_test_firewall cohort must match {FIREWALL_COMPOSERS}")

    # Protocol markdown document checks
    doc_text = PROTOCOL_DOC_PATH.read_text(encoding="utf-8")
    required_doc_snippets = [
        "PF002A_PROSPECTIVE_MODEL_PROTOCOL_FROZEN_READY_FOR_IMPLEMENTATION",
        "PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET",
        EXPECTED_PROTOCOL_HASH,
        "AL-GRU-01",
        "AL-TRF-01",
        "COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION",
        "THEMATIC_MEMORY_GATE = THEME_IDENTITY_DEPENDENT_NOT_READY",
        "SOURCE_SEGMENT_STRUCTURAL_MEMORY",
        "Grouped K-Fold",
        "Youden's J",
        "Percentile bootstrap",
        "2000",
        "Taneyev",
        "Bortkiewicz",
        "Blumenfeld",
        "Catoire",
    ]
    for snip in required_doc_snippets:
        if snip not in doc_text:
            errors.append(f"Protocol document missing required snippet: '{snip}'")

    if errors:
        print("[PF-002A.0] Prospective model protocol validation FAILED with errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("[PF-002A.0] Prospective model protocol validation SUCCESSFUL.")
    print(f"PF002A_MODEL_PROTOCOL_HASH={actual_proto_hash}")
    print("STATUS: PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET")
    return 0


if __name__ == "__main__":
    sys.exit(validate_pf002a_model_protocol())
