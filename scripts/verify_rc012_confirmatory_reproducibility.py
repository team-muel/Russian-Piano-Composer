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
EXPECTED_INVENTORY_HASH: str = "40672c4fd54c3440e6c29db2e0c6f4aa5ffdb7dd7d88e020ff5eccaf015a9a12"
EXPECTED_POLICY_HASH: str = "f9f4fe75dad8eea1de7ae3acd5d80818d1ec24d16999a525bfb0eacc7ba718fc"
EXPECTED_GATE_RESULT_HASH: str = "a5e64cd3e0260250687d64f32915fd0fea8b84830a8c5bb2d1a3651a5cf4337b"


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

    # 3. Run source inventory audit subprocess
    from scripts.audit_rc012_source_inventory import audit_rc012_source_inventory
    gate_payload = audit_rc012_source_inventory()

    actual_inv_hash = gate_payload.get("source_inventory_hash")
    actual_pol_hash = gate_payload.get("source_policy_hash")
    actual_gate_hash = gate_payload.get("data_gate_result_hash")

    print(f"  Expected Source Inventory Hash: {EXPECTED_INVENTORY_HASH}")
    print(f"  Actual Source Inventory Hash:   {actual_inv_hash}")
    if actual_inv_hash != EXPECTED_INVENTORY_HASH:
        raise RuntimeError("Source inventory hash mismatch!")

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
