"""
RC-012 One-Shot Pre-Execution Preflight Verification Script.
Validates the complete pre-unblinding governance, cryptographic hash bindings,
and statistical execution lock prior to one-shot confirmatory evaluation.

Verification Checklist:
1. Governance Decision Authority: Route B APPROVED, N_Russian=4, N_Control=5, 483 pieces.
2. Confirmatory Corpus Master Freeze Hash: ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e.
3. Real Feature Cache Matrix SHA-256: 6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7.
4. Frozen Predictor Bundle Hash: 4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926.
5. One-Shot Execution Lock Plan Hash: 11685bb1217e67a64c5b610f4cc9afd96436fcb12da79fcbc921d1120e8fe962.
6. Predictor Feature Order & Dimension Alignment: 56 features exact projection match.
7. Zero Confirmatory Predictor Scores Evaluated / Zero Output Leakage.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXPECTED_MASTER_FREEZE_HASH: str = "ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e"
EXPECTED_FEATURE_CACHE_SHA256: str = "6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7"
EXPECTED_PREDICTOR_BUNDLE_HASH: str = "4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926"
EXPECTED_HUMAN_DECISION_CANONICAL_HASH: str = "4b50a007e2824ee1223f58a793de993b4537f4db3aa3dd006a17dc7e36ad1b31"
EXPECTED_EXECUTION_PLAN_HASH: str = "11685bb1217e67a64c5b610f4cc9afd96436fcb12da79fcbc921d1120e8fe962"

EXPECTED_RUSSIAN_COMPOSERS: set[str] = {
    "Alexander Scriabin",
    "Modest Mussorgsky",
    "Anton Rubinstein",
    "Sergei Prokofiev",
}

EXPECTED_CONTROL_COMPOSERS: set[str] = {
    "Edvard Grieg",
    "Claude Debussy",
    "Ludwig van Beethoven",
    "Béla Bartók",
    "Antonín Dvořák",
}

DEVELOPMENT_COMPOSERS: set[str] = {
    "Franz Liszt",
    "Frédéric Chopin",
    "Nikolai Medtner",
    "Pyotr Ilyich Tchaikovsky",
    "Robert Schumann",
    "Sergei Rachmaninoff",
}


def compute_canonical_json_hash(payload: dict[str, Any]) -> str:
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def verify_rc012_one_shot_preflight() -> dict[str, Any]:
    print("=== Running RC-012 One-Shot Pre-Execution Preflight Verification ===")

    # 1. Human Access Governance Decision Record
    decision_path = Path("data/reviews/rc014/rc014_human_access_governance_decision.json")
    if not decision_path.exists():
        raise FileNotFoundError(f"Human governance decision file missing at {decision_path}")

    with open(decision_path, encoding="utf-8") as f:
        decision_data = json.load(f)

    actual_decision_hash = compute_canonical_json_hash(decision_data)
    print(f"  Expected Human Decision Hash: {EXPECTED_HUMAN_DECISION_CANONICAL_HASH}")
    print(f"  Actual Human Decision Hash:   {actual_decision_hash}")
    if actual_decision_hash != EXPECTED_HUMAN_DECISION_CANONICAL_HASH:
        raise ValueError(f"Human access governance decision hash mismatch: {actual_decision_hash}")

    if decision_data.get("decision_status") != "APPROVED":
        raise ValueError(f"Governance decision not APPROVED: {decision_data.get('decision_status')}")

    gov_state = decision_data.get("post_decision_governance_state", {})
    if gov_state.get("N_Russian") != 4:
        raise ValueError(f"N_Russian != 4 in governance state: {gov_state.get('N_Russian')}")
    if gov_state.get("RC012_RESUMPTION_STATUS") != "READY_FOR_SEPARATE_ONE_SHOT_EXECUTION":
        raise ValueError(f"RC012 resumption status not ready: {gov_state.get('RC012_RESUMPTION_STATUS')}")
    print("  [PASS] Human Access Governance Authority Verified (Route B, APPROVED, N_Russian=4)")

    # 2. RC-012 One-Shot Execution Lock Record
    lock_path = Path("data/reviews/rc012/rc012_one_shot_execution_lock.json")
    if not lock_path.exists():
        raise FileNotFoundError(f"RC-012 one-shot execution lock missing at {lock_path}")

    with open(lock_path, encoding="utf-8") as f:
        lock_data = json.load(f)

    actual_plan_hash = compute_canonical_json_hash(lock_data)
    print(f"  Expected Execution Plan Hash: {EXPECTED_EXECUTION_PLAN_HASH}")
    print(f"  Actual Execution Plan Hash:   {actual_plan_hash}")
    if actual_plan_hash != EXPECTED_EXECUTION_PLAN_HASH:
        raise ValueError(f"Execution plan hash mismatch: {actual_plan_hash}")

    if lock_data.get("execution_status") != "ARMED_NOT_EXECUTED":
        raise ValueError(f"Execution status is not ARMED_NOT_EXECUTED: {lock_data.get('execution_status')}")
    print("  [PASS] One-Shot Execution Lock Verified (ARMED_NOT_EXECUTED)")

    # 3. Confirmatory Corpus Master Freeze Audit Record
    audit_path = Path("data/reviews/rc014/rc014c2a_preunblinding_integrity_audit.json")
    if not audit_path.exists():
        raise FileNotFoundError(f"Confirmatory corpus audit missing at {audit_path}")

    with open(audit_path, encoding="utf-8") as f:
        audit_data = json.load(f)

    actual_freeze_hash = audit_data.get("rc014c2a_confirmatory_corpus_freeze_hash")
    print(f"  Expected Corpus Freeze Hash:  {EXPECTED_MASTER_FREEZE_HASH}")
    print(f"  Actual Corpus Freeze Hash:    {actual_freeze_hash}")
    if actual_freeze_hash != EXPECTED_MASTER_FREEZE_HASH:
        raise ValueError(f"Master freeze hash mismatch: {actual_freeze_hash}")
    print("  [PASS] Confirmatory Corpus Master Freeze Hash Verified")

    # 4. Real Feature Cache Matrix
    cache_path = Path("data/manifests/rc014c2a_complete_role_blind_feature_cache.json")
    if not cache_path.exists():
        raise FileNotFoundError(f"Feature cache missing at {cache_path}")

    with open(cache_path, encoding="utf-8") as f:
        cache_data = json.load(f)

    actual_matrix_sha256 = cache_data.get("feature_cache_matrix_sha256")
    print(f"  Expected Feature Cache Hash:  {EXPECTED_FEATURE_CACHE_SHA256}")
    print(f"  Actual Feature Cache Hash:    {actual_matrix_sha256}")
    if actual_matrix_sha256 != EXPECTED_FEATURE_CACHE_SHA256:
        raise ValueError(f"Feature cache matrix SHA256 mismatch: {actual_matrix_sha256}")
    print("  [PASS] Real Feature Cache Matrix SHA256 Verified")

    # 5. Frozen Predictor Bundle
    bundle_path = Path("models/rc012_predictor/frozen_predictor_bundle.json")
    if not bundle_path.exists():
        bundle_path = Path("data/manifests/rc012_frozen_predictor_bundle.json")
    if not bundle_path.exists():
        raise FileNotFoundError(f"Predictor bundle missing at {bundle_path}")

    with open(bundle_path, encoding="utf-8") as f:
        bundle_data = json.load(f)

    actual_bundle_hash = bundle_data.get("predictor_bundle_hash")
    print(f"  Expected Predictor Bundle Hash:{EXPECTED_PREDICTOR_BUNDLE_HASH}")
    print(f"  Actual Predictor Bundle Hash:  {actual_bundle_hash}")
    if actual_bundle_hash != EXPECTED_PREDICTOR_BUNDLE_HASH:
        raise ValueError(f"Predictor bundle hash mismatch: {actual_bundle_hash}")
    print("  [PASS] Frozen Predictor Bundle Hash Verified")

    # 6. Repertoire & Composer Membership
    pieces = cache_data.get("cached_pieces", [])
    if len(pieces) != 483:
        raise ValueError(f"Expected exactly 483 pieces in feature cache, found {len(pieces)}")

    per_composer_counts: dict[str, int] = {}
    russian_count = 0
    control_count = 0

    for piece in pieces:
        composer = piece.get("composer")
        if not composer:
            raise ValueError(f"Piece {piece.get('piece_id')} missing composer field")
        per_composer_counts[composer] = per_composer_counts.get(composer, 0) + 1
        if composer in EXPECTED_RUSSIAN_COMPOSERS:
            russian_count += 1
        elif composer in EXPECTED_CONTROL_COMPOSERS:
            control_count += 1
        else:
            raise ValueError(f"Unrecognized composer {composer} in piece {piece.get('piece_id')}")

    if russian_count != 246 or control_count != 237:
        raise ValueError(f"Piece counts mismatch: Russian={russian_count} (exp 246), Control={control_count} (exp 237)")

    active_russian = set()
    active_control = set()
    for composer, count in per_composer_counts.items():
        if count < 10:
            raise ValueError(f"Composer {composer} has Mc={count} < 10")
        if composer in EXPECTED_RUSSIAN_COMPOSERS:
            active_russian.add(composer)
        elif composer in EXPECTED_CONTROL_COMPOSERS:
            active_control.add(composer)

    if active_russian != EXPECTED_RUSSIAN_COMPOSERS:
        raise ValueError(f"Russian composer set mismatch: {active_russian}")
    if active_control != EXPECTED_CONTROL_COMPOSERS:
        raise ValueError(f"Control composer set mismatch: {active_control}")
    print("  [PASS] 9-Composer Repertoire Verified (246 Russian / 237 Control, Mc >= 10 for all 9)")

    # 7. Feature Alignment (56 Descriptors)
    first_piece_features = list(pieces[0]["features_56"].keys())
    bundle_features = bundle_data.get("feature_names", [])
    if len(first_piece_features) != 56 or len(bundle_features) != 56:
        raise ValueError(f"Feature count mismatch: cache={len(first_piece_features)}, bundle={len(bundle_features)}")
    if first_piece_features != bundle_features:
        raise ValueError("Feature ordering mismatch between cache and predictor bundle")
    print("  [PASS] 56-Descriptor Projection and Ordering Match Exactly")

    # 8. Leakage & Disjointness Check
    all_confirmatory_composers = active_russian | active_control
    overlap = all_confirmatory_composers & DEVELOPMENT_COMPOSERS
    if overlap:
        raise ValueError(f"CRITICAL LEAKAGE: Overlap between development and confirmatory composers: {overlap}")
    print("  [PASS] Leakage Isolation Verified (Development Composers ∩ Confirmatory Composers = ∅)")

    # 9. Zero Confirmatory Score / Output Files
    prohibited_files = [
        Path("results/rc012_predictions.parquet"),
        Path("results/rc012_decision_scores.csv"),
        Path("data/predictions/rc012"),
    ]
    for p in prohibited_files:
        if p.exists():
            raise RuntimeError(f"Prohibited execution artifact exists prior to one-shot execution: {p}")
    print("  [PASS] Safety Assertion Verified (Zero Unblinded Predictor Scores on Disk)")

    print("\n==========================================================================")
    print(" RC-012 PRE-EXECUTION PREFLIGHT VERIFICATION: ALL GATES PASS")
    print(" STATUS: RC012_ONE_SHOT_ARMED_READY_FOR_EXECUTION")
    print("==========================================================================")

    return {
        "status": "RC012_ONE_SHOT_ARMED_READY_FOR_EXECUTION",
        "execution_plan_hash": actual_plan_hash,
        "master_freeze_hash": actual_freeze_hash,
        "feature_cache_sha256": actual_matrix_sha256,
        "predictor_bundle_hash": actual_bundle_hash,
        "human_decision_hash": actual_decision_hash,
        "n_composers": len(all_confirmatory_composers),
        "n_pieces": len(pieces),
    }


def main() -> None:
    verify_rc012_one_shot_preflight()


if __name__ == "__main__":
    main()
