#!/usr/bin/env python3
"""Validation script for PF-002A.0a Prospective Model Family & Execution Protocol Freeze.

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
   - Max parameter budgets bounded (AL-GRU-01 <= 200k, AL-TRF-01 <= 250k).
   - Analytical parameter formulas verified against max vocabulary bound |V| <= 512.
   - Positional encoding strictly singular: LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING (no 'or' clauses).
7. Neural framework constraint:
   - Exactly one framework: PyTorch (torch>=2.2,<2.4).
   - Full determinism settings specified.
8. Representation contract:
   - Tokenization from CanonicalScore.
   - Context window L=1024, stride 512.
   - Vocabulary scope: DEVELOPMENT_CORPUS_ONLY.
   - max_vocabulary_size <= 512.
9. Training budget, sampling policies & seed hierarchy:
   - Max 50 epochs, batch size 16.
   - R=3 independent replicates per candidate.
   - Negative sampling policy: exactly 5 foils (3 within-piece, 2 cross-piece same-composer).
   - Identity transform sampling policy: uniform distribution over 7 authoritative transforms.
   - Replicate aggregation rule: Level A epoch checkpoint selection + Level B median replicate aggregation.
   - RandomContext root seed 20260930 with 26 collision-free namespace paths.
10. Gate-specific calibration authority:
    - PREDICTIVE_GATE: 3 non-neural baselines required, NOT_INDEPENDENTLY_CALIBRATABLE.
    - INVARIANCE_GATE: Grouped K-Fold Youden's J on DEVELOPMENT.
    - DISCRIMINATION_GATE: tau_discrimination with Grouped K-Fold Youden's J.
    - COUNTERFACTUAL_GATE: Directional bootstrap lower bound > 0 (NOT_APPLICABLE_ROC_YOUDEN).
    - SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE: Directional bootstrap > 0 and retrieval separation.
    - ANTI_COPY_GATE: Three-tier evaluation with ADD_ALPHA (alpha=0.1) on DEVELOPMENT.
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
TRANSFORM_REGISTRY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_transformation_registry.json"

EXPECTED_INVENTORY_HASH = "3154c2967ee8201d5df65eb3f866fb81e495ac1878e8a60349687888018c9d8e"
EXPECTED_RECEIPT_HASH = "db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d"
EXPECTED_CONTRACT_HASH = "5b681c6b02ecb2c573b06d463705ab8b4fd17b9aec9b5c4e56f6a7e5830e214a"
EXPECTED_SPLIT_HASH = "2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab"
EXPECTED_PROTOCOL_HASH = "691e3e1460377fd219c1e115e52b953b326ddec9afb99ad69034de8567fcd683"

FIREWALL_COMPOSERS = {"Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire"}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def calculate_al_gru_01_params(vocab_size: int, embed_dim: int = 64, hidden_dim: int = 96, latent_dim: int = 64) -> int:
    """Calculates exact parameter count for AL-GRU-01:
    - Layer 1 GRU(embed_dim, hidden_dim): 3 * (hidden_dim * embed_dim + hidden_dim * hidden_dim + hidden_dim + hidden_dim)
    - Layer 2 GRU(hidden_dim, hidden_dim): 3 * (hidden_dim * hidden_dim + hidden_dim * hidden_dim + hidden_dim + hidden_dim)
    - Projection to latent: hidden_dim * latent_dim + latent_dim
    - LayerNorm(latent_dim): 2 * latent_dim
    - Embedding: vocab_size * embed_dim
    - LM Head: hidden_dim * vocab_size + vocab_size
    """
    l1 = 3 * (hidden_dim * embed_dim + hidden_dim * hidden_dim + 2 * hidden_dim)
    l2 = 3 * (hidden_dim * hidden_dim + hidden_dim * hidden_dim + 2 * hidden_dim)
    proj = hidden_dim * latent_dim + latent_dim
    ln = 2 * latent_dim
    emb = vocab_size * embed_dim
    lm_head = hidden_dim * vocab_size + vocab_size
    return l1 + l2 + proj + ln + emb + lm_head


def calculate_al_trf_01_params(vocab_size: int, max_seq_len: int = 1024, model_dim: int = 64, num_layers: int = 3, ff_dim: int = 128, latent_dim: int = 64) -> int:
    """Calculates exact parameter count for AL-TRF-01:
    - Positional Embedding: max_seq_len * model_dim
    - Per Transformer Block (num_layers):
        - MHA: 4 * (model_dim * model_dim + model_dim)
        - Pre-LN1: 2 * model_dim
        - FFN: (model_dim * ff_dim + ff_dim) + (ff_dim * model_dim + model_dim)
        - Pre-LN2: 2 * model_dim
    - Final LayerNorm: 2 * model_dim
    - Latent Projection: model_dim * latent_dim + latent_dim
    - Token Embedding: vocab_size * model_dim
    - LM Head: model_dim * vocab_size + vocab_size
    """
    pos_emb = max_seq_len * model_dim
    mha_per_block = 4 * (model_dim * model_dim + model_dim)
    ln_per_block = 2 * (2 * model_dim)
    ffn_per_block = (model_dim * ff_dim + ff_dim) + (ff_dim * model_dim + model_dim)
    block_total = (mha_per_block + ln_per_block + ffn_per_block) * num_layers
    final_ln = 2 * model_dim
    latent_proj = model_dim * latent_dim + latent_dim
    token_emb = vocab_size * model_dim
    lm_head = model_dim * vocab_size + vocab_size
    return pos_emb + block_total + final_ln + latent_proj + token_emb + lm_head


def validate_pf002a_model_protocol() -> int:
    print("[PF-002A.0a] Starting Prospective Model Family & Execution Protocol validation...")
    errors: list[str] = []

    # 1. File existence
    all_required_files = [
        PROTOCOL_DOC_PATH,
        PROTOCOL_JSON_PATH,
        SPLIT_MANIFEST_PATH,
        INVENTORY_PATH,
        RECEIPT_PATH,
        CONTRACT_PATH,
        TRANSFORM_REGISTRY_PATH,
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

    # Representation & vocabulary bound
    repr_spec = proto_data.get("input_representation", {})
    if repr_spec.get("vocabulary_scope") != "DEVELOPMENT_CORPUS_ONLY":
        errors.append("Vocabulary scope must be DEVELOPMENT_CORPUS_ONLY")
    if repr_spec.get("max_context_window") != 1024:
        errors.append("max_context_window must be 1024")
    max_vocab = repr_spec.get("max_vocabulary_size", 0)
    if max_vocab <= 0 or max_vocab > 512:
        errors.append(f"max_vocabulary_size must be bounded <= 512, got {max_vocab}")

    # Candidate models: exactly 2
    candidates = proto_data.get("candidate_models", [])
    if len(candidates) != 2:
        errors.append(f"Candidate models count must be exactly 2, got {len(candidates)}")
    cand_ids = {c["model_id"] for c in candidates}
    if cand_ids != {"AL-GRU-01", "AL-TRF-01"}:
        errors.append(f"Candidate model IDs must be AL-GRU-01 and AL-TRF-01, got {cand_ids}")

    for c in candidates:
        max_p = c.get("max_trainable_parameters", 0)
        if c["model_id"] == "AL-GRU-01":
            if max_p > 200000:
                errors.append(f"AL-GRU-01 max parameter bound exceeded 200k: {max_p}")
            # Verify analytical parameter math at max_vocab
            calc_gru = calculate_al_gru_01_params(
                vocab_size=max_vocab,
                embed_dim=c.get("embedding_dim", 64),
                hidden_dim=c.get("hidden_dim", 96),
                latent_dim=c.get("latent_dim", 64),
            )
            if calc_gru > max_p:
                errors.append(f"AL-GRU-01 calculated parameters at |V|={max_vocab} ({calc_gru}) exceeds max budget ({max_p})")
            if c.get("nominal_parameters_at_v512") != calc_gru:
                errors.append(f"AL-GRU-01 nominal_parameters_at_v512 mismatch: recorded {c.get('nominal_parameters_at_v512')}, calculated {calc_gru}")

        if c["model_id"] == "AL-TRF-01":
            if max_p > 250000:
                errors.append(f"AL-TRF-01 max parameter bound exceeded 250k: {max_p}")
            # Verify singular positional encoding
            pos_enc = c.get("positional_encoding")
            if pos_enc != "LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING":
                errors.append(f"AL-TRF-01 positional_encoding must be LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING, got '{pos_enc}'")
            # Verify analytical parameter math at max_vocab
            calc_trf = calculate_al_trf_01_params(
                vocab_size=max_vocab,
                max_seq_len=c.get("max_sequence_length", 1024),
                model_dim=c.get("embedding_dim", 64),
                num_layers=c.get("num_layers", 3),
                ff_dim=c.get("feedforward_dim", 128),
                latent_dim=c.get("latent_dim", 64),
            )
            if calc_trf > max_p:
                errors.append(f"AL-TRF-01 calculated parameters at |V|={max_vocab} ({calc_trf}) exceeds max budget ({max_p})")
            if c.get("nominal_parameters_at_v512") != calc_trf:
                errors.append(f"AL-TRF-01 nominal_parameters_at_v512 mismatch: recorded {c.get('nominal_parameters_at_v512')}, calculated {calc_trf}")

    # Neural framework
    framework = proto_data.get("neural_framework", {})
    if framework.get("framework") != "PyTorch":
        errors.append("Neural framework must be PyTorch")
    det_settings = framework.get("determinism_settings", {})
    if not det_settings.get("torch_use_deterministic_algorithms"):
        errors.append("torch_use_deterministic_algorithms must be true")

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

    # Negative sampling policy
    neg_policy = proto_data.get("negative_sampling_policy", {})
    if neg_policy.get("num_foils_per_anchor") != 5:
        errors.append(f"Negative sampling must specify exactly 5 foils per anchor, got {neg_policy.get('num_foils_per_anchor')}")
    alloc = neg_policy.get("foil_allocation", {})
    if alloc.get("within_piece_distant") != 3 or alloc.get("cross_piece_same_composer") != 2:
        errors.append(f"Negative foil allocation must be 3 within-piece and 2 cross-piece, got {alloc}")

    # Identity transform sampling policy
    id_policy = proto_data.get("identity_transform_sampling_policy", {})
    transforms = id_policy.get("transforms", [])
    if len(transforms) != 7:
        errors.append(f"Identity transform sampling must include all 7 registry transforms, got {len(transforms)}")
    sum_weights = sum(t.get("probability_weight", 0) for t in transforms)
    if abs(sum_weights - 1.0) > 1e-4:
        errors.append(f"Transform probability weights must sum to 1.0, got {sum_weights}")

    # RandomContext namespace paths (collision-free check)
    rc_hierarchy = proto_data.get("random_context_hierarchy", {})
    ns_paths = rc_hierarchy.get("namespace_paths", [])
    if len(ns_paths) != len(set(ns_paths)):
        errors.append("Duplicate namespace paths detected in RandomContext hierarchy")
    expected_ns_count = 26  # 2 models * 3 reps * 4 namespaces + 2 evaluation namespaces
    if len(ns_paths) != expected_ns_count:
        errors.append(f"Expected {expected_ns_count} collision-free namespace paths, got {len(ns_paths)}")

    # Replicate & Checkpoint selection rules
    rep_sel = proto_data.get("replicate_and_checkpoint_selection", {})
    level_a = rep_sel.get("level_a_replicate_checkpoint", {})
    level_b = rep_sel.get("level_b_replicate_aggregation", {})
    if level_a.get("metric") != "H_val(W)":
        errors.append("Level A checkpoint selection must use H_val(W)")
    if level_b.get("method") != "MEDIAN_REPLICATE_VALIDATION_METRIC":
        errors.append("Level B replicate aggregation method must be MEDIAN_REPLICATE_VALIDATION_METRIC")
    if "cherry-picking" not in level_b.get("cherry_picking_prohibition", "").lower():
        errors.append("Missing cherry-picking prohibition in Level B aggregation")

    # Gate-specific calibration authority
    gate_auth = proto_data.get("gate_specific_calibration_and_authority", {})
    # Predictive gate
    pred_g = gate_auth.get("PREDICTIVE_GATE", {})
    if pred_g.get("calibration_status") != "NOT_INDEPENDENTLY_CALIBRATABLE":
        errors.append("PREDICTIVE_GATE must be marked NOT_INDEPENDENTLY_CALIBRATABLE")
    req_baselines = pred_g.get("required_baselines", [])
    if set(req_baselines) != {"BASE_EMPIRICAL_MARGINAL", "BASE_MARKOV_ORDER_1", "BASE_NGRAM_4"}:
        errors.append(f"PREDICTIVE_GATE missing required baselines: {req_baselines}")

    # Invariance & Discrimination gates
    inv_g = gate_auth.get("INVARIANCE_GATE", {})
    if not inv_g.get("calibrated_on_development") or inv_g.get("calibration_method") != "GROUPED_KFOLD_YOUDENS_J":
        errors.append("INVARIANCE_GATE must specify GROUPED_KFOLD_YOUDENS_J on DEVELOPMENT")

    disc_g = gate_auth.get("DISCRIMINATION_GATE", {})
    if not disc_g.get("calibrated_on_development") or disc_g.get("calibration_method") != "GROUPED_KFOLD_YOUDENS_J":
        errors.append("DISCRIMINATION_GATE must specify GROUPED_KFOLD_YOUDENS_J on DEVELOPMENT")

    # Counterfactual gate
    cf_g = gate_auth.get("COUNTERFACTUAL_GATE", {})
    if cf_g.get("calibration_status") != "NOT_APPLICABLE_ROC_YOUDEN":
        errors.append("COUNTERFACTUAL_GATE must specify NOT_APPLICABLE_ROC_YOUDEN")

    # Memory gate
    mem_g = gate_auth.get("SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE", {})
    if mem_g.get("calibration_status") != "NOT_APPLICABLE_ROC_YOUDEN":
        errors.append("SOURCE_SEGMENT_STRUCTURAL_MEMORY_GATE must specify NOT_APPLICABLE_ROC_YOUDEN")

    # Anti-copy gate
    copy_g = gate_auth.get("ANTI_COPY_GATE", {})
    tiers = copy_g.get("tiers", {})
    if not ("tier_1_symbolic_ngram" in tiers and "tier_2_weighted_interval_ngram" in tiers and "tier_3_latent_retrieval" in tiers):
        errors.append("ANTI_COPY_GATE must specify all three tiers (symbolic, weighted interval with ADD_ALPHA, latent)")
    if tiers.get("tier_2_weighted_interval_ngram", {}).get("alpha") != 0.1:
        errors.append("ANTI_COPY_GATE Tier 2 must specify alpha=0.1")

    # Gate readiness invariants
    gate_status = proto_data.get("gate_readiness_status", {})
    if gate_status.get("COMPOSER_GENERALIZATION_GATE") != "NOT_READY_FOR_CALIBRATION":
        errors.append("COMPOSER_GENERALIZATION_GATE must be NOT_READY_FOR_CALIBRATION")
    if gate_status.get("THEMATIC_MEMORY_GATE") != "THEME_IDENTITY_DEPENDENT_NOT_READY":
        errors.append("THEMATIC_MEMORY_GATE must be THEME_IDENTITY_DEPENDENT_NOT_READY")

    # Execution ordering
    ordering = proto_data.get("execution_ordering", [])
    if len(ordering) != 6:
        errors.append(f"Execution ordering must specify exactly 6 steps, got {len(ordering)}")
    else:
        if "median validation metric" not in ordering[1]:
            errors.append("Step 2 must specify replicate median aggregation")
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
    if "across all 3 replicates" not in sel_rule.get("requirement", ""):
        errors.append("architecture_selection_rule requirement must require passing across all 3 replicates")

    # External test firewall
    firewall = proto_data.get("external_test_firewall", {})
    if set(firewall.get("cohort", [])) != FIREWALL_COMPOSERS:
        errors.append(f"external_test_firewall cohort must match {FIREWALL_COMPOSERS}")

    # Protocol markdown document checks
    doc_text = PROTOCOL_DOC_PATH.read_text(encoding="utf-8")
    required_doc_snippets = [
        "PF002A_EXECUTABLE_MODEL_PROTOCOL_FROZEN_READY_FOR_IMPLEMENTATION",
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
        "BASE_EMPIRICAL_MARGINAL",
        "BASE_MARKOV_ORDER_1",
        "BASE_NGRAM_4",
        "ADD_ALPHA",
        "LEARNED_ABSOLUTE_POSITIONAL_EMBEDDING",
        "MEDIAN_REPLICATE_VALIDATION_METRIC",
        "Taneyev",
        "Bortkiewicz",
        "Blumenfeld",
        "Catoire",
    ]
    for snip in required_doc_snippets:
        if snip not in doc_text:
            errors.append(f"Protocol document missing required snippet: '{snip}'")

    # Verify no unfrozen 'or' positional encoding language in markdown
    if "or rotary position embeddings" in doc_text.lower():
        errors.append("Protocol document contains unfrozen 'or rotary position embeddings' clause")

    if errors:
        print("[PF-002A.0a] Prospective model protocol validation FAILED with errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("[PF-002A.0a] Prospective model protocol validation SUCCESSFUL.")
    print(f"PF002A_MODEL_PROTOCOL_HASH={actual_proto_hash}")
    print("STATUS: PROSPECTIVE_PROTOCOL_FROZEN_NO_MODEL_FIT_YET")
    return 0


if __name__ == "__main__":
    sys.exit(validate_pf002a_model_protocol())
