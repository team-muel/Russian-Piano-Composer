"""Regression tests for PF-001C1.3a Cross-Document Autonomous Stage-0 Semantic Closure.

Verifies:
1. scripts/validate_pf001c1_autonomous_policy.py succeeds and confirms AUTONOMOUS_STAGE0_POLICY_SYNCHRONIZED.
2. Human validation is strictly defined as OPTIONAL_EXTERNAL_HUMAN_VALIDATION across all documents.
3. No mandatory held-out human listener requirement remains in active Stage-0 policy.
4. Stage-0 predictive validity is corpus-based with non-neural baselines (no human behavioral distributions).
5. Temporal validity is multi-scale temporal structural modeling, not biological real-time auditory cognition.
6. Intervention validity matches PF-001C1 counterfactual contract (cadential disruption, surprise, recurrence cues).
7. COMPOSER_GENERALIZATION_GATE remains NOT_READY_FOR_CALIBRATION.
8. Stage-0 split manifest hash remains exactly 2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab.
9. External test candidate firewall (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remains strictly firewalled.
10. Lineage immutability for RC-012, PF-001B, and PF-001C1 is strictly preserved.
11. Report Section 7 active Stage-0 gates contain no mandatory human noise ceiling or biological lag.
12. Fail-closed negative tests: validator fails when active Stage-0 text introduces mandatory human gates.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

POLICY_PATH = REPO_ROOT / "docs" / "research" / "PF001_GENERALIZATION_AND_SPLIT_POLICY.md"
REPORT_PATH = REPO_ROOT / "docs" / "research" / "PF001_MEASUREMENT_OPERATIONALIZATION_REPORT.md"
GRAPH_PATH = REPO_ROOT / "docs" / "research" / "PF001_MEASUREMENT_DEPENDENCY_GRAPH.md"
CONTRACT_DOC_PATH = REPO_ROOT / "docs" / "research" / "PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
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
    assert "Cross-document autonomous policy validation SUCCESSFUL." in result.stdout
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


def test_report_autonomous_stage0_gating_consistency():
    """Verifies PF001_MEASUREMENT_OPERATIONALIZATION_REPORT Section 7 active gates are autonomous."""
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    m = re.search(r"### 7\. Prospective Validation Categories & Gating Criteria(.*?)(?=#### 7\.1|\Z)", report_text, re.DOTALL)
    assert m is not None, "Could not extract Section 7 active gating from report"
    active_sec7 = m.group(1)

    # Active Section 7 must NOT mandate human noise ceilings or biological lag
    assert not re.search(r"human noise ceiling benchmark", active_sec7, re.IGNORECASE)
    assert not re.search(r"biologically plausible cognitive lag", active_sec7, re.IGNORECASE)
    assert not re.search(r"match human shift sign in", active_sec7, re.IGNORECASE)
    assert not re.search(r"stability across held-out listeners", active_sec7, re.IGNORECASE)

    # Must specify autonomous gates
    assert "PREDICTIVE_VALIDITY" in active_sec7
    assert "STRUCTURAL_TEMPORAL_VALIDITY" in active_sec7
    assert "INTERVENTION_VALIDITY" in active_sec7
    assert "GENERALIZATION_VALIDITY" in active_sec7
    assert "COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION" in active_sec7

    # Optional section must be present and marked OPTIONAL_EXTERNAL_HUMAN_VALIDATION_ONLY
    assert "#### 7.1 Optional External Human Validation Benchmarks" in report_text
    assert "OPTIONAL_EXTERNAL_HUMAN_VALIDATION_ONLY" in report_text


def test_dependency_graph_consistency():
    """Verifies PF001_MEASUREMENT_DEPENDENCY_GRAPH.md does not mandate human noise ceiling for Stage 0->1."""
    graph_text = GRAPH_PATH.read_text(encoding="utf-8")
    assert "OPTIONAL_EXTERNAL_VALIDATION" in graph_text or "OPTIONAL_EXTERNAL_HUMAN_VALIDATION" in graph_text

    sec4_match = re.search(r"### 4\. Stage Progression Rules.*?(?=\Z)", graph_text, re.DOTALL)
    assert sec4_match is not None
    sec4_text = sec4_match.group(0)
    assert not re.search(r"EXP-001 through EXP-005 protocols pass noise ceiling checks on `development` cohort", sec4_text)


def test_fail_closed_negative_mutations(monkeypatch, tmp_path):
    """Negative tests: mutating active Stage-0 definitions to inject mandatory human requirements fails validation."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("val_module", str(VALIDATOR_PATH))
    assert spec is not None and spec.loader is not None
    val_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(val_mod)

    # 1. Mutate report active Section 7 to re-inject biological lag
    orig_report = REPORT_PATH.read_text(encoding="utf-8")
    bad_report = orig_report.replace(
        "Stage-0 does not claim biological real-time auditory cognition or neural lag replication.",
        "Dynamic trajectory of model predictions must track human response latency with biologically plausible cognitive lag (200 <= lag <= 1200 ms).",
    )
    bad_report_file = tmp_path / "bad_report.md"
    bad_report_file.write_text(bad_report, encoding="utf-8")

    monkeypatch.setattr(val_mod, "REPORT_PATH", bad_report_file)
    assert val_mod.validate_autonomous_policy() != 0, "Validator failed to reject biological cognitive lag in active Section 7"

    # 2. Mutate report active Section 7 to re-inject human noise ceiling
    bad_report2 = orig_report.replace(
        "No human behavioral distribution is required for PF-002A Stage-0 training",
        "Distributional distance must meet or exceed the human noise ceiling benchmark",
    )
    bad_report2_file = tmp_path / "bad_report2.md"
    bad_report2_file.write_text(bad_report2, encoding="utf-8")

    monkeypatch.setattr(val_mod, "REPORT_PATH", bad_report2_file)
    assert val_mod.validate_autonomous_policy() != 0, "Validator failed to reject human noise ceiling in active Section 7"

    # 3. Clean report passes
    monkeypatch.setattr(val_mod, "REPORT_PATH", REPORT_PATH)
    assert val_mod.validate_autonomous_policy() == 0
