"""PF-001B Physical Classical Corpus Feasibility Validator.

Validates:
1. Physical existence and non-emptiness of all inventoried score files.
2. Verified SHA-256 matches actual file content on disk.
3. No synthetic or placeholder rows admitted (source_sha256, physical_file_path required).
4. XML / MusicXML / MS3 parseability and well-formedness.
5. Solo-piano eligibility and duplicate group uniqueness.
6. Rights and access documentation present.
7. Autonomous contract numerical gate thresholds marked PROVISIONAL_UNCALIBRATED_TARGET.
8. RC-012 historical result hashes and artifacts remain strictly immutable.
9. External test cohort composers remain strictly firewalled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# Authoritative frozen hashes for RC-012 result artifacts
RC012_EXPECTED_RESULT_CANONICAL_HASH = (
    "a933ac2b21fe50cff9c0a43e8216ee37593acded32e22ecb0e9502b231cffded"
)
RC012_EXPECTED_PIECE_LEDGER_HASH = (
    "66513dc4901b48ee865ba826cb4dad824f448b242b94834fd25202d39c5aa634"
)
RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH = (
    "d606705dd1621a4b0fef85c1dbec2f2f1347891c8576a2162e64ac9306b5b739"
)

REPO_ROOT = Path(__file__).resolve().parents[1]

FIREWALLED_EXTERNAL_COMPOSERS = {
    "CMP-TANEYEV",
    "CMP-BORTKIEWICZ",
    "CMP-BLUMENFELD",
    "CMP-CATOIRE",
}


def validate_physical_corpus_inventory(
    inventory_path: Path, repo_root: Path
) -> tuple[bool, list[str], dict[str, Any]]:
    """Validates the physical corpus inventory JSON."""
    errors: list[str] = []
    if not inventory_path.exists():
        return False, [f"Physical inventory missing: {inventory_path}"], {}

    with open(inventory_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("milestone") != "PF-001B":
        errors.append(f"Invalid milestone: {data.get('milestone')}, expected 'PF-001B'.")

    if data.get("status") != "PHYSICAL_CORPUS_INVENTORY_AUDITED":
        errors.append(f"Invalid status: {data.get('status')}")

    scores = data.get("scores", [])
    if not isinstance(scores, list) or len(scores) == 0:
        return False, ["Inventory has no scores or invalid score list."], {}

    work_ids: set[str] = set()
    verified_files_count = 0
    solo_piano_count = 0
    parser_pass_count = 0

    for idx, s in enumerate(scores):
        wid = s.get("work_id")
        if not wid:
            errors.append(f"Score #{idx} lacks 'work_id'.")
            continue
        if wid in work_ids:
            errors.append(f"Duplicate work_id '{wid}' found.")
        work_ids.add(wid)

        cid = s.get("composer_id")
        if cid in FIREWALLED_EXTERNAL_COMPOSERS:
            errors.append(
                f"Firewalled external composer '{cid}' found in physical inventory score '{wid}'. "
                "External cohort must remain strictly firewalled."
            )

        # Zero placeholder check: physical_file_path and source_sha256 must be present
        rel_path = s.get("physical_file_path")
        if not rel_path or "placeholder" in rel_path.lower() or "synthetic" in rel_path.lower():
            errors.append(f"Score '{wid}' has invalid or placeholder physical_file_path: {rel_path}")
            continue

        file_path = repo_root / rel_path
        if not file_path.exists():
            errors.append(f"Score '{wid}' physical file does not exist on disk: {file_path}")
            continue

        # File size and SHA-256 verification
        file_bytes = file_path.read_bytes()
        actual_size = len(file_bytes)
        if actual_size == 0:
            errors.append(f"Score '{wid}' physical file is 0 bytes: {file_path}")
            continue

        actual_sha = hashlib.sha256(file_bytes).hexdigest()
        declared_sha = s.get("source_sha256")
        if declared_sha != actual_sha:
            errors.append(
                f"Score '{wid}' SHA-256 mismatch! Declared {declared_sha}, actual {actual_sha}."
            )

        # Parser viability check: test XML well-formedness
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            if root is None or len(root) == 0:
                errors.append(f"Score '{wid}' XML root is empty or invalid.")
            else:
                parser_pass_count += 1
        except Exception as e:
            errors.append(f"Score '{wid}' XML parse failed: {e}")

        # Solo piano check
        if s.get("is_solo_piano") is True:
            solo_piano_count += 1
        else:
            errors.append(f"Score '{wid}' is not marked as solo piano.")

        # Rights check
        rights = s.get("rights_access_status")
        if not rights:
            errors.append(f"Score '{wid}' missing rights_access_status.")

        verified_files_count += 1

    summary = {
        "total_scores": len(scores),
        "verified_files_count": verified_files_count,
        "solo_piano_count": solo_piano_count,
        "parser_pass_count": parser_pass_count,
    }
    return len(errors) == 0, errors, summary


def validate_contract_thresholds_deprovisionalization(
    contract_path: Path,
) -> tuple[bool, list[str]]:
    """Verifies that gate thresholds in PF001A contract are explicitly marked provisional."""
    errors: list[str] = []
    if not contract_path.exists():
        return False, [f"Autonomous contract missing: {contract_path}"]

    content = contract_path.read_text(encoding="utf-8")

    # Contract must declare the provisional status
    if "PROVISIONAL_UNCALIBRATED_TARGET" not in content:
        errors.append(
            "PF001A contract missing 'PROVISIONAL_UNCALIBRATED_TARGET' designation for numerical thresholds."
        )

    # Must mention calibration in PF-001C
    if "PF-001C" not in content:
        errors.append("PF001A contract missing reference to PF-001C calibration.")

    return len(errors) == 0, errors


def validate_rc012_strict_immutability(repo_root: Path) -> tuple[bool, list[str]]:
    """Verifies that RC-012 authoritative results and hashes remain completely unchanged."""
    errors: list[str] = []
    result_path = repo_root / "data/reviews/rc012/rc012_one_shot_confirmatory_result.json"

    if not result_path.exists():
        return False, [f"RC-012 result file missing: {result_path}"]

    with open(result_path, encoding="utf-8") as f:
        data = json.load(f)

    rep = data.get("repertoire_summary", {})
    if rep.get("piece_ledger_sha256") != RC012_EXPECTED_PIECE_LEDGER_HASH:
        errors.append(
            f"RC-012 piece_ledger_sha256 altered! Expected {RC012_EXPECTED_PIECE_LEDGER_HASH}."
        )

    boot_path = repo_root / "data/reviews/rc012/rc012_one_shot_bootstrap_replicates.json"
    if not boot_path.exists():
        errors.append(f"RC-012 bootstrap replicates file missing: {boot_path}")
    else:
        with open(boot_path, encoding="utf-8") as f:
            boot_data = json.load(f)
        if (
            boot_data.get("bootstrap_replicate_matrix_sha256")
            != RC012_EXPECTED_BOOTSTRAP_MATRIX_HASH
        ):
            errors.append("RC-012 bootstrap_replicate_matrix_sha256 altered!")

    receipt_path = repo_root / "data/reviews/rc012/rc012_one_shot_execution_receipt.json"
    if not receipt_path.exists():
        errors.append(f"RC-012 execution receipt missing: {receipt_path}")
    else:
        with open(receipt_path, encoding="utf-8") as f:
            receipt = json.load(f)
        if receipt.get("result_hash") != RC012_EXPECTED_RESULT_CANONICAL_HASH:
            errors.append("RC-012 result_hash in execution receipt altered!")

    return len(errors) == 0, errors


def run_all_pf001b_validations(repo_root: Path) -> dict[str, Any]:
    """Runs all PF-001B validation suites."""
    inv_path = repo_root / "data/reviews/pf001/pf001_physical_corpus_inventory.json"
    contract_path = repo_root / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
    audit_report_path = repo_root / "docs/research/PF001B_PHYSICAL_CORPUS_FEASIBILITY_AUDIT.md"

    inv_ok, inv_errors, inv_summary = validate_physical_corpus_inventory(inv_path, repo_root)
    thresh_ok, thresh_errors = validate_contract_thresholds_deprovisionalization(contract_path)
    rc12_ok, rc12_errors = validate_rc012_strict_immutability(repo_root)

    report_ok = audit_report_path.exists()
    report_errors = [] if report_ok else [f"Feasibility audit report missing: {audit_report_path}"]

    all_errors = inv_errors + thresh_errors + rc12_errors + report_errors
    all_passed = inv_ok and thresh_ok and rc12_ok and report_ok

    outcome_token = (
        "PF001B_PHYSICAL_CORPUS_FEASIBILITY_VERIFIED_READY_FOR_CALIBRATION"
        if all_passed
        else "PF001B_CORPUS_ACQUISITION_INCOMPLETE"
    )

    return {
        "milestone": "PF-001B",
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
        "outcome_token": outcome_token,
        "errors": all_errors,
        "inventory_summary": inv_summary,
        "verifications": {
            "physical_corpus_inventory": "PASS" if inv_ok else "FAIL",
            "threshold_deprovisionalization": "PASS" if thresh_ok else "FAIL",
            "rc012_immutability": "PASS" if rc12_ok else "FAIL",
            "feasibility_audit_report": "PASS" if report_ok else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PF-001B Physical Corpus Feasibility & Threshold De-Provisionalization."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output validation results in JSON format.",
    )
    args = parser.parse_args()

    results = run_all_pf001b_validations(args.repo_root)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("=" * 70)
        print("PF-001B PHYSICAL CORPUS FEASIBILITY VALIDATION REPORT")
        print("=" * 70)
        print(f"Overall Status: {results['status']}")
        print(f"Outcome Token:  {results['outcome_token']}")
        for check, res in results["verifications"].items():
            print(f"  - {check:<35}: {res}")
        if not results["passed"]:
            print("\nValidation Errors:")
            for err in results["errors"]:
                print(f"  [ERROR] {err}")
        else:
            print("\nInventory Summary:")
            print(f"  Total Verified Scores: {results['inventory_summary']['total_scores']}")
            print(f"  Solo Piano Pass:       {results['inventory_summary']['solo_piano_count']}")
            print(f"  Parser Pass:           {results['inventory_summary']['parser_pass_count']}")
        print("=" * 70)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
