"""Regression tests for PF-001C1.2 Stage-0 Split Manifest.

Verifies:
1. Validator script succeeds and outputs valid PF001C1_STAGE0_SPLIT_HASH.
2. Invariants:
   - Physical inventory hash matches exact disk bytes.
   - Materialization receipt hash matches authoritative constant.
   - PF-001C1 metric contract hash matches exact disk bytes.
3. Exact 62-piece coverage without duplicates or missing entries.
4. Exact role totals:
   - 37 DEVELOPMENT
   - 22 VALIDATION
   - 3 BENCHMARK_PILOT_ONLY
5. Composer-to-role exclusivity:
   - Tchaikovsky, Rachmaninoff, Arensky strictly in DEVELOPMENT.
   - Medtner, Lyadov strictly in VALIDATION.
   - Lyapunov strictly in BENCHMARK_PILOT_ONLY.
6. Piece-level hash binding matches physical inventory row byte-for-byte.
7. Derivative inheritance and negative-pair leakage protection rules present.
8. Benchmark pilot one-shot isolation rule (must not influence training or threshold tuning).
9. External test firewall and Scriabin lineage exclusion enforced.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SPLIT_MANIFEST_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001c1_stage0_split_manifest.json"
INVENTORY_PATH = REPO_ROOT / "data" / "reviews" / "pf001" / "pf001_physical_corpus_inventory.json"


def test_split_validator_script_succeeds():
    """Runs scripts/validate_pf001c1_stage0_split.py and asserts returncode 0."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_pf001c1_stage0_split.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"
    assert "PF001C1_STAGE0_SPLIT_HASH=" in result.stdout
    assert "Split manifest validation SUCCESSFUL." in result.stdout


def test_exact_62_piece_coverage_and_role_totals():
    """Confirms manifest covers exactly 62 pieces with role counts 37, 22, 3."""
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    pieces = manifest.get("pieces", [])
    assert len(pieces) == 62

    role_counts: dict[str, int] = {}
    for p in pieces:
        role = p.get("role")
        role_counts[role] = role_counts.get(role, 0) + 1

    assert role_counts == {
        "DEVELOPMENT": 37,
        "VALIDATION": 22,
        "BENCHMARK_PILOT_ONLY": 3,
    }


def test_composer_role_exclusivity():
    """Verifies composers are strictly mapped to their designated role."""
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    expected_mapping = {
        "Pyotr Ilyich Tchaikovsky": "DEVELOPMENT",
        "Sergei Rachmaninoff": "DEVELOPMENT",
        "Anton Arensky": "DEVELOPMENT",
        "Nikolai Medtner": "VALIDATION",
        "Anatoly Lyadov": "VALIDATION",
        "Sergei Lyapunov": "BENCHMARK_PILOT_ONLY",
    }

    for p in manifest.get("pieces", []):
        cname = p.get("composer_name")
        assert cname in expected_mapping, f"Unexpected composer: {cname}"
        assert p.get("role") == expected_mapping[cname]


def test_piece_level_hash_binding_to_physical_inventory():
    """Confirms every piece in manifest binds to the exact physical inventory sha256."""
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    with open(INVENTORY_PATH, encoding="utf-8") as f:
        inv = json.load(f)

    inv_scores = {s["work_id"]: s for s in inv.get("scores", [])}
    assert len(inv_scores) == 62

    for p in manifest.get("pieces", []):
        wid = p["work_id"]
        assert wid in inv_scores
        inv_s = inv_scores[wid]
        assert p["canonical_materialized_sha256"] == inv_s["canonical_materialized_sha256"]
        assert p["composer_name"] == inv_s["composer_name"]
        assert p["composer_id"] == inv_s["composer_id"]


def test_derivative_inheritance_and_leakage_policy_present():
    """Verifies that split policies are explicitly encoded in the manifest."""
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    policies = manifest.get("rules_and_policies", {})
    assert "transformation_inheritance_rule" in policies
    assert "negative_pair_split_rule" in policies
    assert "model_selection_boundary" in policies
    assert "bounded_architecture_search" in policies

    # Invariants in text
    assert "strictly inherits" in policies["transformation_inheritance_rule"]
    assert "never create a pair that leaks" in policies["negative_pair_split_rule"]


def test_external_firewall_and_scriabin_exclusion():
    """Confirms firewalled and excluded composers do not appear in active pieces."""
    with open(SPLIT_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    composers_in_pieces = {p["composer_name"] for p in manifest.get("pieces", [])}
    for forbidden in ["Scriabin", "Alexander Scriabin", "Taneyev", "Bortkiewicz", "Blumenfeld", "Catoire", "Balakirev", "Gliere"]:
        assert forbidden not in composers_in_pieces
