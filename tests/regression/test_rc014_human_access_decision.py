"""Regression tests for RC-014 Human Access Governance Decision Record."""

from __future__ import annotations

import json
from pathlib import Path

FROZEN_RC014C2A_MASTER_FREEZE_HASH = "ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e"
FROZEN_RC014C2A_FEATURE_CACHE_MATRIX_SHA256 = "6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7"
FROZEN_RC012_PREDICTOR_BUNDLE_HASH = "4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926"


def test_human_access_governance_decision_record_integrity() -> None:
    json_path = Path("data/reviews/rc014/rc014_human_access_governance_decision.json")
    assert json_path.exists(), f"Missing {json_path}"

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-014"
    assert data["document_type"] == "HUMAN_ACCESS_GOVERNANCE_DECISION_RECORD"
    assert data["decision_status"] == "APPROVED"

    signatory = data["authorized_signatory"]
    assert signatory["reviewer_identifier"] == "Human Research Director / Principal Investigator"
    assert "Project Lead" in signatory["reviewer_role"]
    assert signatory["decision_date"] == "2026-09-28"

    route = data["selected_governance_route"]
    assert "Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE" in route["route_identifier"]

    decisions = data["per_composer_decisions"]
    assert decisions["Anton Rubinstein"]["access_decision"] == "APPROVED"
    assert decisions["Anton Rubinstein"]["eligible_piece_count"] == 11
    assert decisions["Anton Rubinstein"]["raw_redistribution"] == "DISALLOWED"

    assert decisions["Sergei Prokofiev"]["access_decision"] == "APPROVED"
    assert decisions["Sergei Prokofiev"]["eligible_piece_count"] == 10
    assert decisions["Sergei Prokofiev"]["raw_redistribution"] == "DISALLOWED"

    rights = data["rights_axes_policy"]
    assert rights["raw_source_redistribution_authority"] == "DISALLOWED"
    assert rights["local_ephemeral_materialization_authority"] == "AUTHORIZED"
    assert rights["derived_numerical_feature_extraction_authority"] == "AUTHORIZED"
    assert rights["derived_numerical_feature_retention_authority"] == "AUTHORIZED"
    assert rights["derived_research_output_distribution_authority"] == "AUTHORIZED"

    bindings = data["frozen_scientific_hash_bindings"]
    assert bindings["RC014C2A_CONFIRMATORY_CORPUS_FREEZE_HASH"] == FROZEN_RC014C2A_MASTER_FREEZE_HASH
    assert bindings["RC014C2A_REAL_FEATURE_CACHE_SHA256"] == FROZEN_RC014C2A_FEATURE_CACHE_MATRIX_SHA256
    assert bindings["RC012_FROZEN_PREDICTOR_BUNDLE_HASH"] == FROZEN_RC012_PREDICTOR_BUNDLE_HASH

    gov = data["post_decision_governance_state"]
    assert gov["N_Russian"] == 4
    assert len(gov["qualified_russian_composers"]) == 4
    assert "Alexander Scriabin" in gov["qualified_russian_composers"]
    assert "Modest Mussorgsky" in gov["qualified_russian_composers"]
    assert "Anton Rubinstein" in gov["qualified_russian_composers"]
    assert "Sergei Prokofiev" in gov["qualified_russian_composers"]

    assert gov["total_confirmatory_pieces"] == 483
    assert gov["russian_pieces_count"] == 246
    assert gov["control_pieces_count"] == 237
    assert gov["preregistration_composer_count_gate_satisfied"] is True
    assert gov["RC012_RESUMPTION_STATUS"] == "READY_FOR_SEPARATE_ONE_SHOT_EXECUTION"
    assert gov["rc012_execution_in_current_milestone"] is False
    assert gov["confirmatory_predictor_evaluations_count"] == 0


def test_human_access_governance_decision_markdown_report_exists() -> None:
    doc_path = Path("docs/research/RC014_HUMAN_ACCESS_GOVERNANCE_DECISION.md")
    assert doc_path.exists()
    content = doc_path.read_text(encoding="utf-8")
    assert "Route B: AUTHORIZED_NON_VENDORED_RESEARCH_USE" in content
    assert "APPROVED" in content
    assert "Anton Rubinstein" in content
    assert "Sergei Prokofiev" in content
    assert "READY_FOR_SEPARATE_ONE_SHOT_EXECUTION" in content
