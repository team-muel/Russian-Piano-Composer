"""PF-001B.2 Physical Classical Corpus Feasibility & Canonical Parser Regression Test Suite.

Verifies:
1. Physical existence and non-emptiness of all scores in pf001_physical_corpus_inventory.json.
2. Dual-hash provenance: upstream_raw_sha256 and canonical_materialized_sha256 are verified and distinct when transformed.
3. Separation of XML well-formedness from canonical music parsing.
4. Parsing into canonical event structures via ms3 (for DCML MSCX) and RC013ScoreValidator (for MusicXML).
5. Fail-closed behavior: fails if ElementTree alone is used to grant parser verification.
6. Fail-closed behavior: fails if a transform is applied without declared canonicalization_policy.
7. External test cohort composers (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain strictly firewalled.
8. Scriabin is strictly described with lineage policy (PREVIOUSLY_EXPOSED_IN_RC012) and not as currently blinded.
9. Contract thresholds remain PROVISIONAL_UNCALIBRATED_TARGET.
10. Full validator pipeline passes with token PF001B_CANONICAL_PARSE_AND_PROVENANCE_CLOSED_READY_FOR_PF001C1.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_pf001b_physical_corpus import (
    FIREWALLED_EXTERNAL_COMPOSERS,
    run_all_pf001b_validations,
    validate_contract_thresholds_deprovisionalization,
    validate_materialization_receipt,
    validate_physical_corpus_inventory,
    validate_rc012_strict_immutability,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "data/reviews/pf001/pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data/reviews/pf001/pf001b_remote_materialization_receipt.json"
CONTRACT_PATH = REPO_ROOT / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
AUDIT_REPORT_PATH = REPO_ROOT / "docs/research/PF001B_PHYSICAL_CORPUS_FEASIBILITY_AUDIT.md"


def test_physical_inventory_file_exists_and_valid() -> None:
    assert INVENTORY_PATH.exists(), f"Physical inventory missing: {INVENTORY_PATH}"
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("milestone") in {"PF-001B", "PF-001B.2"}
    assert data.get("status") == "PHYSICAL_CORPUS_INVENTORY_AUDITED"
    scores = data.get("scores", [])
    assert len(scores) == 62, f"Expected 62 physical scores, found {len(scores)}"


def test_zero_placeholder_and_physical_file_integrity() -> None:
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for s in data["scores"]:
        wid = s["work_id"]
        rel_path = s["physical_file_path"]
        assert "placeholder" not in rel_path.lower(), f"Placeholder in path: {rel_path}"
        assert "synthetic" not in rel_path.lower(), f"Synthetic in path: {rel_path}"

        fpath = REPO_ROOT / rel_path
        assert fpath.exists(), f"Physical score file missing on disk: {fpath} for {wid}"
        assert fpath.stat().st_size > 0, f"Score file is empty: {fpath}"
        assert s["inventory_status"] == "VERIFIED_USABLE"
        assert s["xml_well_formed_status"] == "XML_WELL_FORMED_VERIFIED"
        assert s["canonical_parser_status"] == "CANONICAL_PARSE_PASS"
        assert s["is_solo_piano"] is True


def test_dual_hash_provenance_and_policy() -> None:
    """Verifies that upstream_raw_sha256 and canonical_materialized_sha256 are distinct when LF_TO_CRLF occurs."""
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for s in data["scores"]:
        wid = s["work_id"]
        policy = s.get("canonicalization_policy")
        assert policy in {"IDENTITY", "LF_TO_CRLF", "CRLF_TO_LF"}
        mat_sha = s.get("canonical_materialized_sha256")
        assert mat_sha is not None and len(mat_sha) == 64

        if "DCMLab" in s["source_repository"]:
            up_sha = s.get("upstream_raw_sha256")
            assert up_sha is not None and len(up_sha) == 64
            if policy == "LF_TO_CRLF":
                assert up_sha != mat_sha, f"Score '{wid}' has identical upstream and materialized hash despite LF_TO_CRLF!"
        else:
            assert s.get("repository_blob_or_commit_identity") is not None


def test_canonical_parser_metrics_present() -> None:
    """Verifies that every score has nonzero musical metrics recorded from canonical parsers."""
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for s in data["scores"]:
        wid = s["work_id"]
        p_name = s.get("canonical_parser_name")
        assert p_name in {"ms3", "music21"}
        metrics = s.get("canonical_parser_metrics")
        assert isinstance(metrics, dict), f"Score '{wid}' missing canonical_parser_metrics"
        assert metrics["num_measures"] > 0, f"Score '{wid}' has 0 measures"
        assert metrics["num_notes"] > 0, f"Score '{wid}' has 0 notes"
        if p_name == "ms3":
            assert metrics["canonical_score_events"] > 0
            assert metrics["canonical_score_measures"] > 0


def test_elementtree_alone_cannot_grant_parser_verified() -> None:
    """Validator must reject scores where canonical_parser_status is missing or not PASS."""
    fake_entry = {
        "work_id": "test_fake",
        "composer_id": "CMP-TEST",
        "composer_name": "Test Composer",
        "work_title": "Test Title",
        "source_repository": "https://github.com/DCMLab/test",
        "source_revision_or_commit": "123456",
        "physical_file_path": "data/scores/rc013/canonical/anatoly_lyadov_op40_no02.musicxml",
        "raw_format": "MusicXML",
        "is_solo_piano": True,
        "rights_access_status": "PUBLIC_DOMAIN",
        "upstream_raw_sha256": "0fc25451fa355a46b04598ae80c48f79acc33af5b06e6f60f7b12f1d6e481adb",
        "canonical_materialized_sha256": "0fc25451fa355a46b04598ae80c48f79acc33af5b06e6f60f7b12f1d6e481adb",
        "canonicalization_policy": "IDENTITY",
        "xml_well_formed_status": "XML_WELL_FORMED_VERIFIED",
        # Missing canonical_parser_name and canonical_parser_status
    }

    tmp_inv = REPO_ROOT / "data/reviews/pf001/tmp_fake_inv.json"
    try:
        tmp_inv.write_text(json.dumps({
            "milestone": "PF-001B.2",
            "status": "PHYSICAL_CORPUS_INVENTORY_AUDITED",
            "scores": [fake_entry]
        }), encoding="utf-8")
        ok, errors, _ = validate_physical_corpus_inventory(tmp_inv, REPO_ROOT)
        assert not ok
        assert any("lacks canonical parser metadata" in e for e in errors)
    finally:
        if tmp_inv.exists():
            tmp_inv.unlink()


def test_missing_canonicalization_policy_rejected() -> None:
    """Validator must reject scores lacking declared canonicalization_policy."""
    fake_entry = {
        "work_id": "test_fake",
        "composer_id": "CMP-TEST",
        "composer_name": "Test Composer",
        "work_title": "Test Title",
        "source_repository": "https://github.com/DCMLab/test",
        "source_revision_or_commit": "123456",
        "physical_file_path": "data/scores/rc013/canonical/anatoly_lyadov_op40_no02.musicxml",
        "raw_format": "MusicXML",
        "is_solo_piano": True,
        "rights_access_status": "PUBLIC_DOMAIN",
        "canonical_materialized_sha256": "0fc25451fa355a46b04598ae80c48f79acc33af5b06e6f60f7b12f1d6e481adb",
        # Missing canonicalization_policy
        "xml_well_formed_status": "XML_WELL_FORMED_VERIFIED",
        "canonical_parser_name": "music21",
        "canonical_parser_version": "10.5.0",
        "canonical_parser_status": "CANONICAL_PARSE_PASS",
    }
    tmp_inv = REPO_ROOT / "data/reviews/pf001/tmp_fake_inv_policy.json"
    try:
        tmp_inv.write_text(json.dumps({
            "milestone": "PF-001B.2",
            "status": "PHYSICAL_CORPUS_INVENTORY_AUDITED",
            "scores": [fake_entry]
        }), encoding="utf-8")
        ok, errors, _ = validate_physical_corpus_inventory(tmp_inv, REPO_ROOT)
        assert not ok
        assert any("canonicalization_policy" in e for e in errors)
    finally:
        if tmp_inv.exists():
            tmp_inv.unlink()


def test_external_test_cohort_strictly_firewalled() -> None:
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for s in data["scores"]:
        cid = s["composer_id"]
        assert cid not in FIREWALLED_EXTERNAL_COMPOSERS, (
            f"External cohort composer '{cid}' leaked into physical inventory!"
        )


def test_scriabin_wording_strictly_lineage_governed() -> None:
    """Verifies that active PF documents do not describe Scriabin as currently blinded."""
    for doc in [CONTRACT_PATH, AUDIT_REPORT_PATH]:
        text = doc.read_text(encoding="utf-8")
        # Ensure active wording uses PREVIOUSLY_EXPOSED_IN_RC012 / EXCLUDED_FROM_PF_DEVELOPMENT_BY_LINEAGE_POLICY
        assert "PREVIOUSLY_EXPOSED_IN_RC012" in text
        assert "EXCLUDED_FROM_PF_DEVELOPMENT_BY_LINEAGE_POLICY" in text


def test_materialization_receipt_valid() -> None:
    ok, errors = validate_materialization_receipt(RECEIPT_PATH)
    assert ok, f"Materialization receipt validation failed: {errors}"


def test_autonomous_contract_numerical_thresholds_deprovisionalized() -> None:
    ok, errors = validate_contract_thresholds_deprovisionalization(CONTRACT_PATH)
    assert ok, f"Threshold deprovisionalization validation failed: {errors}"


def test_rc012_strict_immutability_preserved() -> None:
    ok, errors = validate_rc012_strict_immutability(REPO_ROOT)
    assert ok, f"RC-012 immutability violated: {errors}"


def test_full_pf001b_validator_pipeline_passes() -> None:
    res = run_all_pf001b_validations(REPO_ROOT)
    assert res["passed"] is True, f"Validation pipeline failed: {res['errors']}"
    assert (
        res["outcome_token"]
        == "PF001B_CANONICAL_PARSE_AND_PROVENANCE_CLOSED_READY_FOR_PF001C1"
    )
    assert res["calibration_scope"]["readiness"] == "METRIC_DEFINITION_AND_CALIBRATION_PROCEDURE_FREEZE"
    assert res["calibration_scope"]["composer_generalization_gate"] == "NOT_READY_FOR_CALIBRATION"
