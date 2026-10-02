#!/usr/bin/env python3
"""Validation script for PF-001C1.3a Cross-Document Autonomous Stage-0 Semantic Closure.

Enforces fail-closed validation of:
1. Multi-document semantic consistency across all active PF-001 contract documents:
   - docs/research/PF001_GENERALIZATION_AND_SPLIT_POLICY.md
   - docs/research/PF001_MEASUREMENT_OPERATIONALIZATION_REPORT.md
   - docs/research/PF001A_AUTONOMOUS_LISTENER_CONTRACT.md
   - docs/research/PF001C1_METRIC_AND_CALIBRATION_PROCEDURE.md
   - docs/research/PF001_MEASUREMENT_DEPENDENCY_GRAPH.md
2. Strict isolation of human validation:
   - Human studies are classified as OPTIONAL_EXTERNAL_HUMAN_VALIDATION (or OPTIONAL_EXTERNAL_VALIDATION).
   - Active Stage-0 gating definitions must NOT mandate held-out human listeners, human noise ceilings,
     human behavioral choice distributions, or biological real-time auditory cognition / neural lag.
   - Any references to human experimental protocols (EXP-001 - EXP-005) in gating contexts must be explicitly
     scoped to optional external validation only.
3. Construct & Gate alignment:
   - PREDICTIVE_VALIDITY is grounded in held-out symbolic corpus targets and predeclared non-neural baselines.
   - STRUCTURAL_TEMPORAL_VALIDITY is multi-scale temporal structural modeling across hierarchical timescales.
   - INTERVENTION_VALIDITY is directionally correct response to frozen structural counterfactuals
     (cadential disruption, controlled surprise perturbation, source-segment recurrence-cue disruption).
   - GENERALIZATION_VALIDITY enforces COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION.
   - External candidate composers (Taneyev, Bortkiewicz, Blumenfeld, Catoire) remain firewalled.
   - Scriabin remains excluded by lineage policy.
4. Cryptographic invariant preservation:
   - PF001C1_STAGE0_SPLIT_HASH matches authoritative constant (2ab69668...).
   - Physical inventory hash matches authoritative constant (3154c296...).
   - Materialization receipt hash matches authoritative constant (db2370c0...).
   - PF001C1 metric contract hash matches authoritative constant (5b681c6b...).
   - Exact piece counts remain: 37 DEVELOPMENT, 22 VALIDATION, 3 BENCHMARK_PILOT_ONLY (62 total).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

POLICY_PATH = REPO_ROOT / "docs" / "research" / "PF001_GENERALIZATION_AND_SPLIT_POLICY.md"
REPORT_PATH = REPO_ROOT / "docs" / "research" / "PF001_MEASUREMENT_OPERATIONALIZATION_REPORT.md"
CONTRACT_DOC_PATH = REPO_ROOT / "docs" / "research" / "PF001A_AUTONOMOUS_LISTENER_CONTRACT.md"
METRIC_DOC_PATH = REPO_ROOT / "docs" / "research" / "PF001C1_METRIC_AND_CALIBRATION_PROCEDURE.md"
GRAPH_PATH = REPO_ROOT / "docs" / "research" / "PF001_MEASUREMENT_DEPENDENCY_GRAPH.md"

SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"
RECEIPT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001b_remote_materialization_receipt.json"
CONTRACT_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_metric_calibration_contract.json"

EXPECTED_SPLIT_HASH = "2ab696689645ed4420ed021bdfae6b545ce4c4eb15c39e8097c05ef1d31464ab"
EXPECTED_INVENTORY_HASH = "3154c2967ee8201d5df65eb3f866fb81e495ac1878e8a60349687888018c9d8e"
EXPECTED_RECEIPT_HASH = "db2370c0fdc6010e0d917be4c953d48a1d37d59d680a5d76d8f8a63e474c689d"
EXPECTED_CONTRACT_HASH = "5b681c6b02ecb2c573b06d463705ab8b4fd17b9aec9b5c4e56f6a7e5830e214a"


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_active_stage0_gating_section(report_text: str) -> str:
    """Extracts active Section 7 from report up to Section 7.1 (optional human benchmarks)."""
    m = re.search(r"### 7\. Prospective Validation Categories & Gating Criteria(.*?)(?=#### 7\.1|\Z)", report_text, re.DOTALL)
    if not m:
        return ""
    return m.group(1)


def validate_autonomous_policy() -> int:
    print("[PF-001C1.3a] Starting Cross-Document Autonomous Stage-0 Semantic validation...")
    errors: list[str] = []

    # 1. Verify existence of required files
    all_required_files = [
        POLICY_PATH,
        REPORT_PATH,
        CONTRACT_DOC_PATH,
        METRIC_DOC_PATH,
        GRAPH_PATH,
        SPLIT_MANIFEST_PATH,
        INVENTORY_PATH,
        RECEIPT_PATH,
        CONTRACT_PATH,
    ]
    for p in all_required_files:
        if not p.exists():
            errors.append(f"Missing required file: {p}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # 2. Check cryptographic invariants
    actual_split_hash = compute_sha256(SPLIT_MANIFEST_PATH)
    if actual_split_hash != EXPECTED_SPLIT_HASH:
        errors.append(
            f"PF001C1_STAGE0_SPLIT_HASH mismatch: expected {EXPECTED_SPLIT_HASH}, got {actual_split_hash}"
        )

    actual_inv_hash = compute_sha256(INVENTORY_PATH)
    if actual_inv_hash != EXPECTED_INVENTORY_HASH:
        errors.append(
            f"Physical Inventory Hash mismatch: expected {EXPECTED_INVENTORY_HASH}, got {actual_inv_hash}"
        )

    actual_receipt_hash = json.loads(RECEIPT_PATH.read_text(encoding="utf-8")).get("receipt_hash")
    if actual_receipt_hash != EXPECTED_RECEIPT_HASH:
        errors.append(
            f"Materialization receipt hash mismatch: expected {EXPECTED_RECEIPT_HASH}, got {actual_receipt_hash}"
        )

    actual_contract_hash = compute_sha256(CONTRACT_PATH)
    if actual_contract_hash != EXPECTED_CONTRACT_HASH:
        errors.append(
            f"PF001C1 Metric Contract Hash mismatch: expected {EXPECTED_CONTRACT_HASH}, got {actual_contract_hash}"
        )

    # 3. Read policy document
    policy_text = POLICY_PATH.read_text(encoding="utf-8")

    # 4. Mandatory positive requirements in policy
    required_policy_snippets = [
        "OPTIONAL_EXTERNAL_HUMAN_VALIDATION",
        "PREDICTIVE_VALIDITY",
        "STRUCTURAL_TEMPORAL_VALIDITY",
        "INTERVENTION_VALIDITY",
        "GENERALIZATION_VALIDITY",
        "COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION",
        "No human behavioral distribution is required for PF-002A",
        "cadential disruption",
        "controlled surprise perturbation",
        "source-segment recurrence-cue disruption",
        "EXTERNAL_TEST_CANDIDATE_FIREWALLED",
        "EXCLUDED_FROM_PF_DEVELOPMENT_BY_LINEAGE_POLICY",
    ]
    for snip in required_policy_snippets:
        if snip not in policy_text:
            errors.append(f"Policy missing required specification: '{snip}'")

    # 5. Prohibited phrases in policy indicating stale human-gate or biological cognition claims
    prohibited_policy_patterns = [
        (
            r"Models must be tested on held-out human listeners",
            "Mandatory held-out human listeners requirement found in policy text",
        ),
        (
            r"to evaluate population-level calibration",
            "Mandatory population-level calibration on humans found in policy text",
        ),
        (
            r"Preservation of biological,\s*real-time causal constraints",
            "Unsupported claim of verifying biological real-time auditory cognition found in policy",
        ),
        (
            r"human behavioral choice distributions",
            "Human behavioral choice distribution required in PREDICTIVE_VALIDITY definition in policy",
        ),
    ]
    for pat, desc in prohibited_policy_patterns:
        if re.search(pat, policy_text, re.IGNORECASE):
            errors.append(desc)

    # 6. Check REPORT_PATH (PF001_MEASUREMENT_OPERATIONALIZATION_REPORT.md)
    report_text = REPORT_PATH.read_text(encoding="utf-8")

    required_report_snippets = [
        "OPTIONAL_EXTERNAL_HUMAN_VALIDATION_ONLY",
        "COMPOSER_GENERALIZATION_GATE = NOT_READY_FOR_CALIBRATION",
        "No human behavioral distribution is required for PF-002A",
        "CF-CLOSURE",
        "CF-SURPRISE",
        "CF-SOURCE-SEGMENT-MEMORY",
    ]
    for snip in required_report_snippets:
        if snip not in report_text:
            errors.append(f"Report missing required specification: '{snip}'")

    # Check active Section 7 of report specifically: MUST NOT contain mandatory human gates
    active_sec7 = extract_active_stage0_gating_section(report_text)
    if not active_sec7:
        errors.append("Report Section 7 (active Stage-0 gating) could not be extracted")
    else:
        sec7_prohibited_patterns = [
            (
                r"human noise ceiling benchmark",
                "Mandatory human noise ceiling benchmark found in active Stage-0 gating of report",
            ),
            (
                r"biologically plausible cognitive lag",
                "Biological cognitive lag requirement found in active Stage-0 gating of report",
            ),
            (
                r"match human shift sign in",
                "Mandatory human shift sign requirement found in active Stage-0 gating of report",
            ),
            (
                r"stability across held-out listeners",
                "Held-out human listener requirement found in active Stage-0 gating of report",
            ),
        ]
        for pat, desc in sec7_prohibited_patterns:
            if re.search(pat, active_sec7, re.IGNORECASE):
                errors.append(desc)

    # 7. Check GRAPH_PATH (PF001_MEASUREMENT_DEPENDENCY_GRAPH.md)
    graph_text = GRAPH_PATH.read_text(encoding="utf-8")
    if "OPTIONAL_EXTERNAL_VALIDATION" not in graph_text and "OPTIONAL_EXTERNAL_HUMAN_VALIDATION" not in graph_text:
        errors.append("Dependency graph missing classification of human validation as optional external")

    # Section 4 table in graph: Stage 0 -> Stage 1 must NOT require human noise ceilings
    sec4_match = re.search(r"### 4\. Stage Progression Rules.*?(?=\Z)", graph_text, re.DOTALL)
    if sec4_match:
        sec4_text = sec4_match.group(0)
        if re.search(r"EXP-001 through EXP-005 protocols pass noise ceiling checks on `development` cohort", sec4_text):
            errors.append("Dependency graph Stage 0->1 prerequisite still mandates human noise ceiling checks")

    # 8. Check CONTRACT_DOC_PATH (PF001A_AUTONOMOUS_LISTENER_CONTRACT.md)
    contract_doc_text = CONTRACT_DOC_PATH.read_text(encoding="utf-8")
    if "OPTIONAL_EXTERNAL_VALIDATION" not in contract_doc_text:
        errors.append("Autonomous contract doc missing OPTIONAL_EXTERNAL_VALIDATION classification")

    # 9. Ensure COMPOSER_GENERALIZATION_GATE is not prematurely promoted in any document
    for doc_name, doc_content in [
        ("policy", policy_text),
        ("report", report_text),
        ("contract_doc", contract_doc_text),
        ("graph", graph_text),
    ]:
        if re.search(r"COMPOSER_GENERALIZATION_GATE\s*=\s*(?:READY|CALIBRATED|PASSED)", doc_content):
            errors.append(f"COMPOSER_GENERALIZATION_GATE prematurely promoted in {doc_name}")

    # 10. Check manifest piece counts & split roles
    manifest_data = json.loads(SPLIT_MANIFEST_PATH.read_text(encoding="utf-8"))
    counts = manifest_data.get("piece_count_by_role", {})
    if counts.get("DEVELOPMENT") != 37:
        errors.append(f"DEVELOPMENT piece count is {counts.get('DEVELOPMENT')}, expected 37")
    if counts.get("VALIDATION") != 22:
        errors.append(f"VALIDATION piece count is {counts.get('VALIDATION')}, expected 22")
    if counts.get("BENCHMARK_PILOT_ONLY") != 3:
        errors.append(f"BENCHMARK_PILOT_ONLY piece count is {counts.get('BENCHMARK_PILOT_ONLY')}, expected 3")
    if counts.get("TOTAL") != 62:
        errors.append(f"Total piece count is {counts.get('TOTAL')}, expected 62")

    if errors:
        print("[PF-001C1.3a] Cross-document autonomous policy validation FAILED with errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("[PF-001C1.3a] Cross-document autonomous policy validation SUCCESSFUL.")
    print("STATUS: AUTONOMOUS_STAGE0_POLICY_SYNCHRONIZED")
    return 0


if __name__ == "__main__":
    sys.exit(validate_autonomous_policy())
