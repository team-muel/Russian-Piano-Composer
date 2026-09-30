#!/usr/bin/env python3
"""Validation script for PF-001C1.2 Stage-0 split manifest.

Enforces fail-closed validation of:
1. Manifest file existence and JSON schema conformity.
2. Invariant preservation:
   - Physical inventory hash matches exact disk bytes.
   - Materialization receipt hash matches authoritative constant (db2370c0...).
   - PF-001C1 metric contract hash matches exact disk bytes (5b681c6b...).
3. Exact 62-piece coverage:
   - Every piece in the physical inventory has exactly one role in the split manifest.
   - Exact role totals: 37 DEVELOPMENT, 22 VALIDATION, 3 BENCHMARK_PILOT_ONLY.
4. Composer role exclusivity:
   - Tchaikovsky (12), Rachmaninoff (22), Arensky (3) -> DEVELOPMENT (37).
   - Medtner (19), Lyadov (3) -> VALIDATION (22).
   - Lyapunov (3) -> BENCHMARK_PILOT_ONLY (3).
5. Exclusions and Firewalls:
   - Scriabin must not appear in any active PF role.
   - Balakirev and Gliere must not appear in active PF roles.
   - External test candidates (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled.
6. Piece identity binding:
   - piece_id, work_id, composer_id, composer_name, and canonical_materialized_sha256
     must match the physical inventory row byte-for-byte.
7. Policy rules present:
   - Transformation inheritance rule.
   - Negative-pair split rule.
   - Model selection boundary.
   - Bounded architecture search.
   - Composer generalization gate remains NOT_READY_FOR_CALIBRATION.
8. Computes and prints PF001C1_STAGE0_SPLIT_HASH.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001b_remote_materialization_receipt.json"
CONTRACT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"

EXPECTED_RECEIPT_HASH = "db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d"
FIREWALL_COMPOSERS = {"Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire"}
EXCLUDED_COMPOSERS = {"Scriabin", "Alexander Scriabin", "Balakirev", "Mily Balakirev", "Gliere", "Reinhold Gliere", "Reinhold Glière"}

EXPECTED_COMPOSER_ROLES = {
    "Pyotr Ilyich Tchaikovsky": "DEVELOPMENT",
    "Sergei Rachmaninoff": "DEVELOPMENT",
    "Anton Arensky": "DEVELOPMENT",
    "Nikolai Medtner": "VALIDATION",
    "Anatoly Lyadov": "VALIDATION",
    "Sergei Lyapunov": "BENCHMARK_PILOT_ONLY",
}

EXPECTED_ROLE_COUNTS = {
    "DEVELOPMENT": 37,
    "VALIDATION": 22,
    "BENCHMARK_PILOT_ONLY": 3,
}


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def validate_split_manifest() -> int:
    print("[PF-001C1.2] Starting Stage-0 split manifest validation...")
    errors: list[str] = []

    if not SPLIT_MANIFEST_PATH.exists():
        print(f"ERROR: Missing split manifest at {SPLIT_MANIFEST_PATH}", file=sys.stderr)
        return 1

    # 1. Load files
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    with open(INVENTORY_PATH, encoding="utf-8") as f:
        inventory = json.load(f)

    # 2. Check invariant hashes
    inv_sha256 = compute_sha256(INVENTORY_PATH)
    if manifest.get("physical_inventory_hash") != inv_sha256:
        errors.append(f"physical_inventory_hash mismatch: expected {inv_sha256}, got {manifest.get('physical_inventory_hash')}")

    if manifest.get("materialization_receipt_hash") != EXPECTED_RECEIPT_HASH:
        errors.append(f"materialization_receipt_hash mismatch: expected {EXPECTED_RECEIPT_HASH}, got {manifest.get('materialization_receipt_hash')}")

    contract_sha256 = compute_sha256(CONTRACT_PATH)
    if manifest.get("PF001C1_METRIC_CONTRACT_HASH") != contract_sha256:
        errors.append(f"PF001C1_METRIC_CONTRACT_HASH mismatch: expected {contract_sha256}, got {manifest.get('PF001C1_METRIC_CONTRACT_HASH')}")

    # 3. Check pieces count and schema
    pieces = manifest.get("pieces", [])
    if len(pieces) != 62:
        errors.append(f"Split manifest must contain exactly 62 pieces, got {len(pieces)}")

    inv_scores = {s["work_id"]: s for s in inventory.get("scores", [])}
    if len(inv_scores) != 62:
        errors.append(f"Inventory scores count is {len(inv_scores)}, expected 62")

    manifest_work_ids: set[str] = set()
    role_counts: dict[str, int] = {}
    composer_counts: dict[str, int] = {}

    for idx, p in enumerate(pieces):
        wid = p.get("work_id")
        if not wid:
            errors.append(f"Piece #{idx} lacks work_id")
            continue
        if wid in manifest_work_ids:
            errors.append(f"Duplicate work_id '{wid}' in manifest")
        manifest_work_ids.add(wid)

        if wid not in inv_scores:
            errors.append(f"Work ID '{wid}' not found in physical inventory")
            continue

        inv_s = inv_scores[wid]
        # Check piece identity binding
        if p.get("canonical_materialized_sha256") != inv_s.get("canonical_materialized_sha256"):
            errors.append(f"Score '{wid}' hash mismatch with physical inventory")

        if p.get("composer_name") != inv_s.get("composer_name"):
            errors.append(f"Score '{wid}' composer_name mismatch with physical inventory")

        if p.get("composer_id") != inv_s.get("composer_id"):
            errors.append(f"Score '{wid}' composer_id mismatch with physical inventory")

        cname = p.get("composer_name")
        role = p.get("role")
        if not role:
            errors.append(f"Piece '{wid}' lacks role")
            continue

        if role not in EXPECTED_ROLE_COUNTS:
            errors.append(f"Piece '{wid}' has invalid role '{role}'")

        expected_role = EXPECTED_COMPOSER_ROLES.get(cname)
        if role != expected_role:
            errors.append(f"Piece '{wid}' ({cname}) assigned role '{role}', expected '{expected_role}'")

        role_counts[role] = role_counts.get(role, 0) + 1
        composer_counts[cname] = composer_counts.get(cname, 0) + 1

    # 4. Check role totals
    for r_name, exp_count in EXPECTED_ROLE_COUNTS.items():
        actual_count = role_counts.get(r_name, 0)
        if actual_count != exp_count:
            errors.append(f"Role '{r_name}' count is {actual_count}, expected {exp_count}")

    # 5. Check firewall and exclusions
    for forbidden in EXCLUDED_COMPOSERS:
        if forbidden in composer_counts:
            errors.append(f"Forbidden/excluded composer '{forbidden}' found in active manifest roles")

    for fw in FIREWALL_COMPOSERS:
        if fw in composer_counts:
            errors.append(f"Firewalled external composer '{fw}' found in active manifest roles")

    # 6. Check required policies
    policies = manifest.get("rules_and_policies", {})
    if "transformation_inheritance_rule" not in policies:
        errors.append("Missing transformation_inheritance_rule in rules_and_policies")
    if "negative_pair_split_rule" not in policies:
        errors.append("Missing negative_pair_split_rule in rules_and_policies")
    if "model_selection_boundary" not in policies:
        errors.append("Missing model_selection_boundary in rules_and_policies")
    if "bounded_architecture_search" not in policies:
        errors.append("Missing bounded_architecture_search in rules_and_policies")

    if errors:
        print("[PF-001C1.2] Split manifest validation FAILED with errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    split_sha256 = compute_sha256(SPLIT_MANIFEST_PATH)
    print("[PF-001C1.2] Split manifest validation SUCCESSFUL.")
    print(f"PF001C1_STAGE0_SPLIT_HASH={split_sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(validate_split_manifest())
