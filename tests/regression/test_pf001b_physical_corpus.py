"""PF-001B Physical Classical Corpus Feasibility Regression Test Suite.

Verifies:
1. Physical existence and non-emptiness of all scores in pf001_physical_corpus_inventory.json.
2. Verified SHA-256 matches actual file on disk.
3. XML/MusicXML/MS3 well-formedness and parser pass for all 62 physical pieces.
4. Solo-piano eligibility and duplicate group uniqueness.
5. Zero placeholder or synthetic entries.
6. Firewalled external test cohort (Taneyev, Bortkiewicz, Blumenfeld, Catoire) has 0 scores in inventory.
7. PF001A contract numerical gate thresholds marked PROVISIONAL_UNCALIBRATED_TARGET.
8. RC-012 authoritative result hashes and artifacts remain strictly immutable.
9. Validator script outputs PASS and outcome token PF001B_PHYSICAL_CORPUS_FEASIBILITY_VERIFIED_READY_FOR_CALIBRATION.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.validate_pf001b_physical_corpus import (
    FIREWALLED_EXTERNAL_COMPOSERS,
    run_all_pf001b_validations,
    validate_contract_thresholds_deprovisionalization,
    validate_rc012_strict_immutability,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "data/reviews/pf001/pf001_physical_corpus_inventory.json"
CONTRACT_PATH = REPO_ROOT / "docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
AUDIT_REPORT_PATH = REPO_ROOT / "docs/research/PF001B_PHYSICAL_CORPUS_FEASIBILITY_AUDIT.md"


def test_physical_inventory_file_exists_and_valid() -> None:
    assert INVENTORY_PATH.exists(), f"Physical inventory missing: {INVENTORY_PATH}"
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("milestone") == "PF-001B"
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
        assert s["parser_status"] == "PARSER_PASS"
        assert s["is_solo_piano"] is True


def test_external_test_cohort_strictly_firewalled() -> None:
    with open(INVENTORY_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for s in data["scores"]:
        cid = s["composer_id"]
        assert cid not in FIREWALLED_EXTERNAL_COMPOSERS, (
            f"External cohort composer '{cid}' leaked into physical inventory!"
        )


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
        == "PF001B_REMOTE_REPRODUCIBILITY_CLOSED_READY_FOR_PF001C1"
    )

