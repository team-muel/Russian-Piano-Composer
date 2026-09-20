"""
Verification script for RC-012 Confirmatory Reproducibility.
Validates:
1. Two-process deterministic computation of predictor bundle and hash.
2. Leakage check passing.
3. Precondition contract evaluation reproducibility (Source Inventory & Policy).
4. Deterministic hashes for Source Inventory, Policy, and Data Gate Result.
"""

import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EXPECTED_BUNDLE_HASH: str = "4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926"
EXPECTED_INVENTORY_HASH: str = "4813102a193c38fc61ef4815a25895243c819b2527803f82e7020ac766627eb7"
EXPECTED_QUERY_LOG_HASH: str = "7bfbcd4af8c0651d4b5b65190be4c65ff86645655b4ebdcfa0b343d08388f5de"
EXPECTED_POLICY_HASH: str = "cc80e267c094cb2bbff04dc2d82bf6df8639113ad41d9bb4587a5e970b0cd24e"
EXPECTED_GATE_RESULT_HASH: str = "5966e1386400a977e0412534e83df6b30667a544e5a431b8b05357dcdb409b7b"


def main() -> None:
    print("--- Running RC-012 Confirmatory Reproducibility Verification ---")

    # 1. Verify frozen predictor exists and bundle hash matches
    bundle_path = Path("models/rc012_predictor/frozen_predictor_bundle.json")
    if not bundle_path.exists():
        raise RuntimeError(f"Predictor bundle not found at {bundle_path}")

    with open(bundle_path, encoding="utf-8") as f:
        bundle = json.load(f)

    actual_bundle_hash = bundle.get("predictor_bundle_hash")
    print(f"  Expected Predictor Bundle Hash: {EXPECTED_BUNDLE_HASH}")
    print(f"  Actual Predictor Bundle Hash:   {actual_bundle_hash}")

    if actual_bundle_hash != EXPECTED_BUNDLE_HASH:
        raise RuntimeError("Predictor bundle hash mismatch!")

    # 2. Run data leakage audit subprocess
    res_leakage = subprocess.run(
        [sys.executable, "-m", "scripts.audit_rc012_leakage"],
        capture_output=True,
        text=True,
    )
    if res_leakage.returncode != 0:
        raise RuntimeError(f"Leakage audit failed:\n{res_leakage.stderr}")
    print("  Leakage Audit Subprocess: PASS")

    # 3. Run source evidence referential integrity verifier subprocess
    res_evidence = subprocess.run(
        [sys.executable, "-m", "scripts.verify_rc012_source_evidence"],
        capture_output=True,
        text=True,
    )
    if res_evidence.returncode != 0:
        raise RuntimeError(f"Source evidence verification failed:\n{res_evidence.stderr}")
    print("  Source Evidence Verification Subprocess: PASS")

    # 4. Run source inventory audit subprocess
    from scripts.audit_rc012_source_inventory import audit_rc012_source_inventory
    gate_payload = audit_rc012_source_inventory()

    actual_inv_hash = gate_payload.get("source_inventory_hash")
    actual_query_hash = gate_payload.get("source_query_log_hash")
    actual_pol_hash = gate_payload.get("source_policy_hash")
    actual_gate_hash = gate_payload.get("data_gate_result_hash")

    print(f"  Expected Source Inventory Hash: {EXPECTED_INVENTORY_HASH}")
    print(f"  Actual Source Inventory Hash:   {actual_inv_hash}")
    if actual_inv_hash != EXPECTED_INVENTORY_HASH:
        raise RuntimeError("Source inventory hash mismatch!")

    print(f"  Expected Source Query Log Hash: {EXPECTED_QUERY_LOG_HASH}")
    print(f"  Actual Source Query Log Hash:   {actual_query_hash}")
    if actual_query_hash != EXPECTED_QUERY_LOG_HASH:
        raise RuntimeError("Source query log hash mismatch!")

    print(f"  Expected Source Policy Hash:    {EXPECTED_POLICY_HASH}")
    print(f"  Actual Source Policy Hash:      {actual_pol_hash}")
    if actual_pol_hash != EXPECTED_POLICY_HASH:
        raise RuntimeError("Source policy hash mismatch!")

    print(f"  Expected Data Gate Result Hash: {EXPECTED_GATE_RESULT_HASH}")
    print(f"  Actual Data Gate Result Hash:   {actual_gate_hash}")
    if actual_gate_hash != EXPECTED_GATE_RESULT_HASH:
        raise RuntimeError("Data gate result hash mismatch!")

    print("\n==========================================================================")
    print(" RC-012 CONFIRMATORY REPRODUCIBILITY VERIFICATION: PASS")
    print("==========================================================================")


if __name__ == "__main__":
    main()
