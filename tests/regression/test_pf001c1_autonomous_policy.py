"""Regression tests for PF-001C1.3 Autonomous Stage-0 Policy Synchronization.

Verifies:
1. scripts/validate_pf001c1_autonomous_policy.py succeeds and confirms AUTONOMOUS_STAGE0_POLICY_SYNCHRONIZED.
2. Human validation is strictly defined as OPTIONAL_EXTERNAL_HUMAN_VALIDATION.
3. No mandatory held-out human listener requirement remains in active Stage-0 policy.
4. Stage-0 predictive validity is corpus-based with non-neural baselines (no human behavioral distributions).
5. Temporal validity is multi-scale temporal structural modeling, not biological real-time auditory cognition.
6. Intervention validity matches PF-001C1 counterfactual contract (cadential disruption, surprise, recurrence cues).
7. COMPOSER_GENERALIZATION_GATE remains NOT_READY_FOR_CALIBRATION.
8. Stage-0 split manifest hash remains exactly 2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab.
9. External test candidate firewall (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remains strictly firewalled.
10. Lineage immutability for RC-012, PF-001B, and PF-001C1 is strictly preserved.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

POLICY_PATH = REPO_ROOT / "docs" / "research" / "PF001_GENERALIZATION_AND_SPLIT_POLICY.md"
SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_pf001c1_autonomous_policy.py"

EXPECTED_SPLIT_HASH = "2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab"


def test_autonomous_policy_validator_script_succeeds():
    """Runs scripts/validate_pf001c1_autonomous_policy.py and asserts success."""
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"
    assert "Autonomous policy validation SUCCESSFUL." in result.stdout
    assert "STATUS: AUTONOMOUS_STAGE0_POLICY_SYNCHRONIZED" in result.stdout


def test_optional_external_human_validation_layer():
    """Confirms human validation is optional external validation only."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    assert "OPTIONAL_EXTERNAL_HUMAN_VALIDATION" in text
    assert "Human studies are not used for Stage-0 model fitting" in text
    assert "checkpoint selection, threshold selection, or PF-002A pass/fail" in text
    assert "Human validation must not retroactively redefine autonomous metrics" in text

    # Confirm no mandatory requirement on held-out listeners remains
    assert not re.search(r"Models must be tested on held-out human listeners", text, re.IGNORECASE)
    assert not re.search(r"to evaluate population-level calibration", text, re.IGNORECASE)


def test_predictive_validity_definition():
    """Confirms predictive validity is corpus-supervised and requires no human distribution."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    assert "No human behavioral distribution is required for PF-002A" in text
    assert "predictive agreement with held-out symbolic corpus targets" in text.lower() or "Predictive agreement with held-out symbolic corpus targets" in text
    assert not re.search(r"human behavioral choice distributions", text, re.IGNORECASE)


def test_structural_temporal_validity_definition():
    """Confirms temporal validity is structural, not biological auditory cognition."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    assert "STRUCTURAL_TEMPORAL_VALIDITY" in text
    assert "multi-scale temporal structural modeling" in text
    assert "Stage-0 does not claim biological real-time auditory cognition" in text
    assert not re.search(r"Preservation of biological,\s*real-time causal constraints", text, re.IGNORECASE)


def test_intervention_validity_counterfactuals():
    """Confirms intervention validity covers PF-001C1 counterfactual targets."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    assert "INTERVENTION_VALIDITY" in text
    assert "cadential disruption" in text
    assert "controlled surprise perturbation" in text
    assert "source-segment recurrence-cue disruption" in text


def test_composer_generalization_gate_remains_not_ready():
    """Confirms composer generalization gate is preserved as NOT_READY_FOR_CALIBRATION."""
    text = POLICY_PATH.read_text(encoding="utf-8")
    assert "COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION" in text
    assert "NOT_READY_FOR_CALIBRATION" in text


def test_split_manifest_hash_and_roles_immutable():
    """Confirms split manifest hash and exact role distribution are unchanged."""
    import hashlib

    manifest_bytes = SPLIT_MANIFEST_PATH.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    assert manifest_hash == EXPECTED_SPLIT_HASH

    manifest_data = json.loads(manifest_bytes.decode("utf-8"))
    role_counts = manifest_data.get("piece_count_by_role", {})
    assert role_counts == {
        "DEVELOPMENT": 37,
        "VALIDATION": 22,
        "BENCHMARK_PILOT_ONLY": 3,
        "TOTAL": 62,
    }
