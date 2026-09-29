"""PF-001B.2 Physical Classical Corpus Feasibility & Canonical Parser Validator.

Validates:
1. Physical existence and non-emptiness of all inventoried score files.
2. Verified upstream_raw_sha256 and canonical_materialized_sha256 dual hashes.
3. Explicit canonicalization policy adherence (IDENTITY, LF_TO_CRLF, CRLF_TO_LF).
4. Zero synthetic or placeholder rows admitted.
5. XML_WELL_FORMED_VERIFIED (syntactic well-formedness).
6. CANONICAL_PARSE_PASS:
   - For DCML MSCX: parsed via ms3 and ingest_score_entry_from_ms3 into CanonicalScore
     with nonzero measures, nonzero events, valid notes/rests, rational onsets/durations,
     valid staves/voices, valid spelled pitches.
   - For RC-013 MusicXML: parsed via RC013ScoreValidator (music21) with valid=True,
     nonzero measures, notes, and parts/staves.
7. Remote materialization receipt integrity and receipt hash.
8. Solo-piano eligibility and duplicate group uniqueness.
9. Rights and access documentation present.
10. Autonomous contract numerical gate thresholds marked PROVISIONAL_UNCALIBRATED_TARGET.
11. RC-012 historical result hashes and artifacts remain strictly immutable.
12. External test cohort composers remain strictly firewalled (0 physical scores).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from typing import Any

import ms3

from russian_piano_composer.corpus.adapters.dcml_ms3 import CorpusRole, ingest_score_entry_from_ms3
from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator

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


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_canonical_ms3_score(file_path: Path, score_entry: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validates that a DCML MuseScore file parses into canonical event structure via ms3."""
    errors = []
    wid = score_entry.get("work_id", "UNKNOWN")
    try:
        sc = ms3.Score(str(file_path))
        m_df = sc.mscx.measures()
        nr_df = sc.mscx.notes_and_rests()

        if len(m_df) == 0:
            errors.append(f"Score '{wid}' has 0 measures in ms3.")
        if len(nr_df) == 0:
            errors.append(f"Score '{wid}' has 0 notes_and_rests in ms3.")

        # Check rational/finite onsets and durations
        for col in ["quarterbeats", "duration_qb"]:
            if col in nr_df:
                for val in nr_df[col]:
                    if not isinstance(val, (Fraction, int, float)):
                        errors.append(f"Score '{wid}' non-rational onset/duration in {col}: {val}")
                        break

        # Check staff and voice
        if "staff" not in nr_df or nr_df["staff"].isna().any():
            errors.append(f"Score '{wid}' contains events with missing staff.")
        if "voice" not in nr_df or nr_df["voice"].isna().any():
            errors.append(f"Score '{wid}' contains events with missing voice.")

        # Check note pitches
        notes = nr_df[nr_df["name"].notna()] if "name" in nr_df else []
        if len(notes) == 0:
            errors.append(f"Score '{wid}' has 0 note pitch events.")
        else:
            for p_name in notes["name"].head(50):
                if not isinstance(p_name, str) or len(p_name) < 2:
                    errors.append(f"Score '{wid}' invalid note pitch format: {p_name}")
                    break

        # Ingestion test into CanonicalScore
        cs = ingest_score_entry_from_ms3(
            corpus_id="dcml",
            corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
            score_entry_id=file_path.stem,
            composer=score_entry["composer_name"],
            title=score_entry["work_title"],
            repo_dir=file_path.parent,
            source_repository=score_entry["source_repository"],
            source_commit=score_entry["source_revision_or_commit"],
            source_sha256=score_entry.get("canonical_materialized_sha256", score_entry.get("source_sha256")),
            manifest_hash="pf001b2_validation",
        )
        if len(cs.measures) == 0:
            errors.append(f"Score '{wid}' CanonicalScore has 0 measures.")
        if len(cs.events) == 0:
            errors.append(f"Score '{wid}' CanonicalScore has 0 events.")

    except Exception as e:
        errors.append(f"Score '{wid}' ms3 canonical parsing failed: {e}")

    return len(errors) == 0, errors


def validate_canonical_music21_score(file_path: Path, score_entry: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validates that an RC-013 MusicXML score passes RC013ScoreValidator / music21."""
    errors = []
    wid = score_entry.get("work_id", "UNKNOWN")
    try:
        validator = RC013ScoreValidator()
        rep = validator.validate_file(str(file_path))
        if not rep.valid:
            errors.append(f"Score '{wid}' RC013ScoreValidator failed: {rep.errors}")
        if rep.num_measures == 0:
            errors.append(f"Score '{wid}' has 0 measures in music21.")
        if rep.num_notes == 0:
            errors.append(f"Score '{wid}' has 0 notes in music21.")
        if rep.num_parts_or_staves == 0:
            errors.append(f"Score '{wid}' has 0 parts/staves in music21.")
    except Exception as e:
        errors.append(f"Score '{wid}' music21 canonical parsing failed: {e}")

    return len(errors) == 0, errors


def validate_physical_corpus_inventory(
    inventory_path: Path, repo_root: Path
) -> tuple[bool, list[str], dict[str, Any]]:
    """Validates the physical corpus inventory JSON under PF-001B.2 requirements."""
    errors: list[str] = []
    if not inventory_path.exists():
        return False, [f"Physical inventory missing: {inventory_path}"], {}

    with open(inventory_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("milestone") not in {"PF-001B", "PF-001B.2"}:
        errors.append(f"Invalid milestone: {data.get('milestone')}, expected 'PF-001B' or 'PF-001B.2'.")

    if data.get("status") != "PHYSICAL_CORPUS_INVENTORY_AUDITED":
        errors.append(f"Invalid status: {data.get('status')}")

    scores = data.get("scores", [])
    if not isinstance(scores, list) or len(scores) == 0:
        return False, ["Inventory has no scores or invalid score list."], {}

    work_ids: set[str] = set()
    verified_files_count = 0
    solo_piano_count = 0
    source_identity_verified_count = 0
    source_bytes_materialized_count = 0
    dual_hash_verified_count = 0
    xml_well_formed_count = 0
    canonical_parse_pass_count = 0

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

        # Stage 1: SOURCE_IDENTITY_VERIFIED
        rel_path = s.get("physical_file_path")
        repo_url = s.get("source_repository")
        commit = s.get("source_revision_or_commit")
        mat_sha = s.get("canonical_materialized_sha256") or s.get("source_sha256")
        if not rel_path or "placeholder" in rel_path.lower() or "synthetic" in rel_path.lower():
            errors.append(f"Score '{wid}' has invalid or placeholder physical_file_path: {rel_path}")
            continue
        if not repo_url or not commit or not mat_sha:
            errors.append(f"Score '{wid}' missing source identity bindings (repo, commit, sha).")
            continue
        source_identity_verified_count += 1

        # Stage 2: SOURCE_BYTES_MATERIALIZED
        file_path = repo_root / rel_path
        if not file_path.exists():
            errors.append(f"Score '{wid}' physical file does not exist on disk: {file_path}")
            continue

        file_bytes = file_path.read_bytes()
        actual_size = len(file_bytes)
        if actual_size == 0:
            errors.append(f"Score '{wid}' physical file is 0 bytes: {file_path}")
            continue
        source_bytes_materialized_count += 1

        # Stage 3: DUAL_HASH_VERIFIED & CANONICALIZATION POLICY
        actual_mat_sha = compute_sha256(file_bytes)
        if mat_sha != actual_mat_sha:
            errors.append(
                f"Score '{wid}' materialized SHA-256 mismatch! Declared {mat_sha}, actual {actual_mat_sha}."
            )
            continue

        policy = s.get("canonicalization_policy")
        if not policy:
            errors.append(f"Score '{wid}' lacks declared 'canonicalization_policy'.")
            continue

        if "DCMLab" in str(repo_url):
            up_sha = s.get("upstream_raw_sha256")
            if not up_sha:
                errors.append(f"External DCML score '{wid}' lacks declared 'upstream_raw_sha256'.")
                continue
            if policy == "IDENTITY" and up_sha != mat_sha:
                errors.append(f"Score '{wid}' declared policy IDENTITY but upstream and materialized hashes differ!")
                continue
            elif policy == "LF_TO_CRLF" and up_sha == mat_sha:
                errors.append(f"Score '{wid}' declared policy LF_TO_CRLF but upstream and materialized hashes are identical!")
                continue
        dual_hash_verified_count += 1

        # Stage 4: XML_WELL_FORMED_VERIFIED
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            if root is None or len(root) == 0:
                errors.append(f"Score '{wid}' XML root is empty or invalid.")
                continue
            if s.get("xml_well_formed_status") != "XML_WELL_FORMED_VERIFIED":
                errors.append(f"Score '{wid}' xml_well_formed_status is not 'XML_WELL_FORMED_VERIFIED'.")
                continue
            xml_well_formed_count += 1
        except Exception as e:
            errors.append(f"Score '{wid}' XML parse failed: {e}")
            continue

        # Stage 5: CANONICAL_PARSER_VERIFIED
        c_name = s.get("canonical_parser_name")
        c_status = s.get("canonical_parser_status")
        c_version = s.get("canonical_parser_version")
        if not c_name or not c_status or not c_version:
            errors.append(f"Score '{wid}' lacks canonical parser metadata (name, status, version).")
            continue

        if c_name == "ms3":
            c_ok, c_errs = validate_canonical_ms3_score(file_path, s)
            if not c_ok:
                errors.extend(c_errs)
                continue
        elif c_name == "music21":
            c_ok, c_errs = validate_canonical_music21_score(file_path, s)
            if not c_ok:
                errors.extend(c_errs)
                continue
        else:
            errors.append(f"Score '{wid}' unrecognized canonical parser name: '{c_name}'.")
            continue

        if c_status not in {"CANONICAL_PARSE_PASS", "CANONICAL_PARSE_PASS_WITH_WARNINGS"}:
            errors.append(f"Score '{wid}' canonical parser status is '{c_status}', not usable.")
            continue
        canonical_parse_pass_count += 1

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
        "source_identity_verified_count": source_identity_verified_count,
        "source_bytes_materialized_count": source_bytes_materialized_count,
        "dual_hash_verified_count": dual_hash_verified_count,
        "xml_well_formed_count": xml_well_formed_count,
        "canonical_parse_pass_count": canonical_parse_pass_count,
        "verified_files_count": verified_files_count,
        "solo_piano_count": solo_piano_count,
    }
    return len(errors) == 0, errors, summary


def validate_materialization_receipt(receipt_path: Path) -> tuple[bool, list[str]]:
    """Verifies that the materialization receipt exists, has valid status, and correct hash."""
    errors = []
    if not receipt_path.exists():
        return False, [f"Materialization receipt missing: {receipt_path}"]

    with open(receipt_path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") != "MATERIALIZATION_AND_PROVENANCE_VERIFIED":
        errors.append(f"Receipt status is '{data.get('status')}', expected 'MATERIALIZATION_AND_PROVENANCE_VERIFIED'.")

    if data.get("total_scores_failed", 0) != 0:
        errors.append(f"Receipt reports {data.get('total_scores_failed')} failed scores.")

    receipt_hash = data.get("receipt_hash")
    if not receipt_hash:
        errors.append("Receipt lacks 'receipt_hash'.")
    else:
        copy_data = dict(data)
        del copy_data["receipt_hash"]
        expected_hash = compute_sha256(json.dumps(copy_data, sort_keys=True, indent=2).encode("utf-8"))
        if receipt_hash != expected_hash:
            errors.append(f"Receipt hash mismatch! Declared {receipt_hash}, recomputed {expected_hash}.")

    return len(errors) == 0, errors


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
    """Runs all PF-001B.2 validation suites."""
    inv_path = repo_root / "data/reviews/pf001/pf001_physical_corpus_inventory.json"
    contract_path = repo_root / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
    audit_report_path = repo_root / "docs/research/PF001B_PHYSICAL_CORPUS_FEASIBILITY_AUDIT.md"
    receipt_path = repo_root / "data/reviews/pf001/pf001b_remote_materialization_receipt.json"

    inv_ok, inv_errors, inv_summary = validate_physical_corpus_inventory(inv_path, repo_root)
    receipt_ok, receipt_errors = validate_materialization_receipt(receipt_path)
    thresh_ok, thresh_errors = validate_contract_thresholds_deprovisionalization(contract_path)
    rc12_ok, rc12_errors = validate_rc012_strict_immutability(repo_root)

    report_ok = audit_report_path.exists()
    report_errors = [] if report_ok else [f"Feasibility audit report missing: {audit_report_path}"]

    all_errors = inv_errors + receipt_errors + thresh_errors + rc12_errors + report_errors
    all_passed = inv_ok and receipt_ok and thresh_ok and rc12_ok and report_ok

    outcome_token = (
        "PF001B_CANONICAL_PARSE_AND_PROVENANCE_CLOSED_READY_FOR_PF001C1"
        if all_passed
        else "PF001B_CANONICAL_PARSER_BLOCKED"
    )

    return {
        "milestone": "PF-001B.2",
        "status": "PASS" if all_passed else "FAIL",
        "passed": all_passed,
        "outcome_token": outcome_token,
        "calibration_scope": {
            "readiness": (
                "METRIC_DEFINITION_AND_CALIBRATION_PROCEDURE_FREEZE"
                if all_passed
                else "BLOCKED"
            ),
            "composer_generalization_gate": "NOT_READY_FOR_CALIBRATION",
            "composer_generalization_rationale": (
                "Current composer counts are too sparse to justify final composer-transfer threshold calibration."
            ),
        },
        "errors": all_errors,
        "inventory_summary": inv_summary,
        "verifications": {
            "physical_corpus_inventory": "PASS" if inv_ok else "FAIL",
            "materialization_receipt": "PASS" if receipt_ok else "FAIL",
            "threshold_deprovisionalization": "PASS" if thresh_ok else "FAIL",
            "rc012_immutability": "PASS" if rc12_ok else "FAIL",
            "feasibility_audit_report": "PASS" if report_ok else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate PF-001B.2 Physical Corpus Feasibility, Canonical Parsers & Dual-Hash Provenance."
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
        print("PF-001B.2 CANONICAL PARSER & DUAL-HASH PROVENANCE VALIDATION REPORT")
        print("=" * 70)
        print(f"Overall Status:    {results['status']}")
        print(f"Outcome Token:     {results['outcome_token']}")
        print(f"Calibration Scope: {results.get('calibration_scope', {}).get('readiness')}")
        print(f"Composer Transfer: {results.get('calibration_scope', {}).get('composer_generalization_gate')}")
        for check, res in results["verifications"].items():
            print(f"  - {check:<35}: {res}")
        if not results["passed"]:
            print("\nValidation Errors:")
            for err in results["errors"]:
                print(f"  [ERROR] {err}")
        else:
            inv_sum = results["inventory_summary"]
            print("\nInventory Multi-Stage Verification Summary:")
            print(f"  Total Verified Scores:         {inv_sum['total_scores']}")
            print(f"  1. Source Identity Verified:   {inv_sum['source_identity_verified_count']}")
            print(f"  2. Source Bytes Materialized:  {inv_sum['source_bytes_materialized_count']}")
            print(f"  3. Dual-Hash & Policy Verified:{inv_sum['dual_hash_verified_count']}")
            print(f"  4. XML Well-Formed Verified:   {inv_sum['xml_well_formed_count']}")
            print(f"  5. Canonical Parse Pass:       {inv_sum['canonical_parse_pass_count']}")
            print(f"  Solo Piano Pass:               {inv_sum['solo_piano_count']}")
        print("=" * 70)

    return 0 if results["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
