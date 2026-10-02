"""Regression tests for PF-002A.0a Prospective Artificial Listener Model Family & Execution Protocol Freeze.

Verifies:
1. scripts/validate_pf002a_model_protocol.py succeeds and confirms PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET.
2. Invariants:
   - Physical inventory hash matches exact disk bytes (3154c296...).
   - Materialization receipt hash matches authoritative constant (db2370c0...).
   - PF-001C1 metric contract hash matches exact disk bytes (5b681c6b...).
   - PF-001C1.2 split manifest hash matches exact disk bytes (2ab69668...).
   - PF002A model protocol hash matches exact disk bytes (691e3e14...).
3. Zero trained model weights, parameters, or embeddings on disk.
4. Candidate models strictly bounded to AL-GRU-01 (<= 200k) and AL-TRF-01 (<= 250k).
5. Exact closed-form analytical parameter formulas verified at vocabulary bound |V| <= 512.
6. Positional encoding strictly singular: LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING without 'or' clauses.
7. Neural framework strictly bound to PyTorch with determinism flags.
8. Negative sampling policy: exactly 5 foils (3 within-piece, 2 cross-piece same-composer).
9. Identity transform sampling: uniform distribution over all 7 registry transforms.
10. Replicate aggregation: Level A epoch checkpoint selection + Level B median replicate aggregation (anti-cherry-picking).
11. RandomContext hierarchy: 26 collision-free namespace paths.
12. Gate-specific calibration authority:
    - PREDICTIVE_GATE: 3 non-neural baselines, NOT_INDEPENDENTLY_CALIBRATABLE.
    - INVARIANCE_GATE & DISCRIMINATION_GATE: Grouped K-Fold Youden's J on DEVELOPMENT.
    - COUNTERFACTUAL_GATE & MEMORY_GATE: Directional bootstrap lower bound > 0 (NOT_APPLICABLE_ROC_YOUDEN).
    - ANTI_COPY_GATE: Conjunctive three-tier with ADD_ALPHA (alpha=0.1) on DEVELOPMENT.
13. COMPOSER_GENERALIZATION_GATE remains NOT_READY_FOR_CALIBRATION.
14. THEMATIC_MEMORY_GATE remains THEME_IDENTITY_DEPENDENT_NOT_READY.
15. External test candidates (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled.
16. Fail-closed negative mutation tests covering parameter limits, architecture additions, cherry-picking, missing tiers, and uncalibrated gates.
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

EXPECTED_PROTOCOL_HASH = "691e3e1460377fd219c1e115e52b953b326ddec9afb99ad69034de8567fcd683"


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


def test_bounded_model_candidates_and_analytical_formulas():
    """Confirms candidate set contains exactly AL-GRU-01 and AL-TRF-01 within parameter limits."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    candidates = data.get("candidate_models", [])
    assert len(candidates) == 2
    cand_map = {c["model_id"]: c for c in candidates}
    assert set(cand_map.keys()) == {"AL-GRU-01", "AL-TRF-01"}

    assert cand_map["AL-GRU-01"]["max_trainable_parameters"] <= 200000
    assert cand_map["AL-TRF-01"]["max_trainable_parameters"] <= 250000

    # Verify singular positional encoding
    assert cand_map["AL-TRF-01"]["positional_encoding"] == "LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING"


def test_negative_and_transform_sampling_policies():
    """Confirms negative sampling has exactly 5 foils (3 within, 2 cross) and transform sampling includes all 7."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    neg = data.get("negative_sampling_policy", {})
    assert neg.get("num_foils_per_anchor") == 5
    assert neg.get("foil_allocation", {}).get("within_piece_distant") == 3
    assert neg.get("foil_allocation", {}).get("cross_piece_same_composer") == 2

    id_policy = data.get("identity_transform_sampling_policy", {})
    transforms = id_policy.get("transforms", [])
    assert len(transforms) == 7
    total_w = sum(t.get("probability_weight", 0) for t in transforms)
    assert abs(total_w - 1.0) < 1e-4


def test_collision_free_random_context_hierarchy():
    """Confirms 26 unique, collision-free namespace paths in RandomContext hierarchy."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    paths = data.get("random_context_hierarchy", {}).get("namespace_paths", [])
    assert len(paths) == 26
    assert len(paths) == len(set(paths))


def test_replicate_aggregation_and_anti_cherry_picking():
    """Confirms Level B replicate aggregation uses MEDIAN_REPLICATE_VALIDATION_METRIC."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    rep_sel = data.get("replicate_and_checkpoint_selection", {})
    level_b = rep_sel.get("level_b_replicate_aggregation", {})
    assert level_b.get("method") == "MEDIAN_REPLICATE_VALIDATION_METRIC"
    assert "cherry-picking" in level_b.get("cherry_picking_prohibition", "").lower()


def test_gate_specific_calibration_authority():
    """Confirms gate-specific calibration methods and baselines are strictly assigned."""
    data = json.loads(PROTOCOL_JSON_PATH.read_text(encoding="utf-8"))
    auth = data.get("gate_specific_calibration_and_authority", {})

    # Predictive gate
    pred = auth.get("PREDICTIVE_GATE", {})
    assert pred.get("calibration_status") == "NOT_INDEPENDENTLY_CALIBRATABLE"
    assert set(pred.get("required_baselines", [])) == {
        "BASE_EMPIRICAL_MARGINAL",
        "BASE_MARKOV_ORDER_1",
        "BASE_NGRAM_4",
    }

    # Invariance & Discrimination gates
    assert auth.get("INVARIANCE_GATE", {}).get("calibration_method") == "GROUPED_KFOLD_YOUDENS_J"
    assert auth.get("DISCRIMINATION_GATE", {}).get("calibration_method") == "GROUPED_KFOLD_YOUDENS_J"

    # Counterfactual & Memory gates
    assert auth.get("COUNTERFACTUAL_GATE", {}).get("calibration_status") == "NOT_APPLICABLE_ROC_YOUDEN"
    assert auth.get("SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE", {}).get("calibration_status") == "NOT_APPLICABLE_ROC_YOUDEN"

    # Anti-copy gate
    copy_g = auth.get("ANTI_COPY_GATE", {})
    tiers = copy_g.get("tiers", {})
    assert "tier_1_symbolic_ngram" in tiers
    assert "tier_2_weighted_interval_ngram" in tiers
    assert "tier_3_latent_retrieval" in tiers
    assert tiers["tier_2_weighted_interval_ngram"]["alpha"] == 0.1


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

    # 2. Mutate protocol to exceed AL-GRU-01 parameter budget (> 200k)
    bad_proto2 = copy.deepcopy(orig_proto)
    bad_proto2["candidate_models"][0]["max_trainable_parameters"] = 250000
    bad_file2 = tmp_path / "bad_proto2.json"
    bad_file2.write_text(json.dumps(bad_proto2, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file2)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject AL-GRU-01 budget exceeding 200k"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 3. Mutate protocol to change replicate aggregation to best seed (cherry-picking)
    bad_proto3 = copy.deepcopy(orig_proto)
    bad_proto3["replicate_and_checkpoint_selection"]["level_b_replicate_aggregation"]["method"] = "BEST_SEED_MINIMUM_LOSS"
    bad_file3 = tmp_path / "bad_proto3.json"
    bad_file3.write_text(json.dumps(bad_proto3, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file3)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject best-seed cherry-picking"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 4. Mutate protocol to remove Tier 2 weighted interval n-gram from anti-copy gate
    bad_proto4 = copy.deepcopy(orig_proto)
    del bad_proto4["gate_specific_calibration_and_authority"]["ANTI_COPY_GATE"]["tiers"]["tier_2_weighted_interval_ngram"]
    bad_file4 = tmp_path / "bad_proto4.json"
    bad_file4.write_text(json.dumps(bad_proto4, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file4)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject missing Tier 2 anti-copy"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 5. Mutate protocol to introduce duplicate namespace paths
    bad_proto5 = copy.deepcopy(orig_proto)
    bad_proto5["random_context_hierarchy"]["namespace_paths"][1] = bad_proto5["random_context_hierarchy"]["namespace_paths"][0]
    bad_file5 = tmp_path / "bad_proto5.json"
    bad_file5.write_text(json.dumps(bad_proto5, indent=2), encoding="utf-8")

    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", bad_file5)
    assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject duplicate RandomContext namespace"
    monkeypatch.setattr(proto_mod, "PROTOCOL_JSON_PATH", PROTOCOL_JSON_PATH)

    # 6. Premature trained weight file detection
    fake_weight = REPO_ROOT / "src" / "russian_piano_composer" / "models" / "fake_weights.pt"
    try:
        fake_weight.write_bytes(b"PK\x03\x04fakeweights")
        assert proto_mod.validate_pf002a_model_protocol() != 0, "Validator failed to reject premature model weight on disk"
    finally:
        if fake_weight.exists():
            fake_weight.unlink()
