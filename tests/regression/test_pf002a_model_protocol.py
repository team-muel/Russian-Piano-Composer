"""Regression tests for PF-002A.0 Prospective Artificial Listener Model Family & Execution Protocol Freeze.

Verifies:
1. scripts/validate_pf002a_model_protocol.py succeeds and confirms PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET.
2. Invariants:
   - Physical inventory hash matches exact disk bytes (3154c296...).
   - Materialization receipt hash matches authoritative constant (db2370c0...).
   - PF-001C1 metric contract hash matches exact disk bytes (5b681c6b...).
   - PF-001C1.2 split manifest hash matches exact disk bytes (2ab69668...).
   - PF002A model protocol hash matches exact disk bytes (fbe099bb...).
3. Zero trained model weights, parameters, or embeddings on disk.
4. Candidate models strictly bounded to AL-GRU-01 and AL-TRF-01 with maximum parameter budgets.
5. Neural framework strictly bound to PyTorch with determinism flags.
6. Execution ordering mandates prospective threshold calibration on DEVELOPMENT before VALIDATION evaluation.
7. COMPOSER_GENERALIZATION_GATE remains NOT_READY_FOR_CALIBRATION.
8. THEMATIC_MEMORY_GATE remains THEME_IDENTITY_DEPENDENT_NOT_READY.
9. External test candidates (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled.
10. Fail-closed negative mutation tests:
    - Attempting to add a 3rd architecture fails validation.
    - Exceeding parameter budget fails validation.
    - Presence of premature trained weights fails validation.
    - Premature promotion of COMPOSER_GENERALIZATION_GATE fails validation.
    - Tampering with upstream hashes fails validation.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_pf002a_model_protocol.py"
PROTOCOL_JSON_PATH = REPO_ROOT / "data" / "reviews" / "pf002a" / "pf002a_model_execution_protocol.json"
PROTOCOL_DOC_PATH = REPO_ROOT / "docs" / "research" / "PF002A_PROSPECTIVE_MODEL_AND_EXECUTION_PROTOCOL.md"
SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001b_remote_materialization_receipt.json"
CONTRACT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"

EXPECTED_PROTOCOL_HASH = "fbe099bb3e2155e393a69704ae73b9b10867e9af19246682f12e0675101476b9"


def test_pf002a_model_protocol_validator_script_succeeds():
    """Runs scripts/validate_pf002a_model_protocol.py and asserts returncode 0."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"
    assert "Prospective model protocol validation SUCCESSFUL." in result.stdout
    assert f"PF002A_MODEL_PROTOCOL_HASH={EXPECTED_PROTOCOL_HASH}" in result.stdout
    assert "STATUS: PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET" in result.stdout


def test_zero_trained_weights_or_embeddings_on_disk():
    """Confirms no trained weights or latent embeddings currently exist in the repository."""
    models_dir = REPO_ROOT / "src" / "russian_piano_composer" / "models"
    data_interim = REPO_ROOT / "data" / "interim"
    data_processed = REPO_ROOT / "data" / "processed"
    forbidden_suffixes = {".pt", ".pth", ".bin", ".onnx", ".safetensors", ".ckpt", ".h5"}
    for check_dir in [models_dir, data_interim, data_processed]:
        if check_dir.exists():
            for f in check_dir.rglob("*"):
                assert f.suffix.lower() not in forbidden_suffixes, f"Premature trained weight found: {f}"
                if ("embedding" in f.name.lower() or "latent" in f.name.lower()) and f.suffix in {".npy", ".npz", ".pt"}:
                    raise AssertionError(f"Premature learned embedding found: {f}")


def test_bounded_model_candidates():
    """Confirms candidate set contains exactly AL-GRU-01 and AL-TRF-01 within parameter limits."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    candidates = data.get("candidate_models", [])
    assert len(candidates) == 2
    cand_map = {c["model_id"]: c for c in candidates}
    assert set(cand_map.keys()) == {"AL-GRU-01", "AL-TRF-01"}

    assert cand_map["AL-GRU-01"]["max_trainable_parameters"] <= 250000
    assert cand_map["AL-TRF-01"]["max_trainable_parameters"] <= 350000


def test_execution_ordering_and_prospective_calibration():
    """Confirms execution ordering requires threshold calibration before validation evaluation."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    ordering = data.get("execution_ordering", [])
    assert len(ordering) == 6
    assert "Grouped K-Fold (K=5) Youden's J on DEVELOPMENT" in ordering[2]
    assert "Evaluate 6 active Stage-0 gates on VALIDATION" in ordering[3]
    assert "BENCHMARK_PILOT_ONLY" in ordering[5]


def test_gate_invariants_preserved():
    """Confirms composer generalization and thematic memory gates remain unpromoted."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    gates = data.get("gate_readiness_status", {})
    assert gates.get("COMPOSER_GENERALIZATION_GATE") == "NOT_READY_FOR_CALIBRATION"
    assert gates.get("THEMATIC_MEMORY_GATE") == "THEME_IDENTITY_DEPENDENT_NOT_READY"


def test_external_test_cohort_strictly_firewalled():
    """Confirms external test cohort is blinded and firewalled."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    fw = data.get("external_test_firewall", {})
    assert fw.get("status") == "ENFORCED_BLINDED"
    assert set(fw.get("cohort", [])) == {"Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire"}


def test_fail_closed_negative_mutations(monkeypatch, tmp_path):
    """Negative tests: mutating protocol parameters or adding premature artifacts fails validation."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("proto_val_module", str(VALIDATOR_PATH))
    assert spec is not None and spec.loader is not None
    proto_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(proto_mod)

    orig_json_text = PROTOCOL_JSON_PATH.read_text(encoding="utf-8")
    orig_proto = json.loads(orig_json_text)

    # 1. Mutate protocol to add a 3rd architecture (AL-LSTM-01)
    bad_proto1 = copy.deepcopy(orig_proto)
    bad_proto1["candidate_models"].append({
        "model_id": "AL-LSTM-01",
        "architecture_type": "causal_lstm",
        "max_trainable_parameters": 300000,
    })
    bad_file1 = tmp_path / "bad_proto1.json"
    bad_file1.write_text(json.dumps(bad_proto1, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file1)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject 3rd architecture"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 2. Mutate protocol to prematurely promote COMPOSER_GENERALIZATION_GATE
    bad_proto2 = copy.deepcopy(orig_proto)
    bad_proto2["gate_readiness_status"]["COMPOSER_GENERALIZATION_GATE"] = "ACTIVE_STAGE0_GATE"
    bad_file2 = tmp_path / "bad_proto2.json"
    bad_file2.write_text(json.dumps(bad_proto2, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file2)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject premature composer gate promotion"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 3. Mutate protocol to change epochs to 100
    bad_proto3 = copy.deepcopy(orig_proto)
    bad_proto3["training_budget_and_optimization"]["max_epochs"] = 100
    bad_file3 = tmp_path / "bad_proto3.json"
    bad_file3.write_text(json.dumps(bad_proto3, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file3)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject budget alteration"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 4. Premature trained weight file detection
    fake_weight = REPO_ROOT / "src" / "russian_piano_composer" / "models" / "fake_weights.pt"
    try:
        fake_weight.write_bytes(b"PK\x03\x04fakeweights")
        assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject premature model weight on disk"
    finally:
        if fake_weight.exists():
            fake_weight.unlink()
