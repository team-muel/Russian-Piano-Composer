"""Regression Safety Tests for RC-014A External Corpus Qualification & Gate Safety.

Enforces:
1. Raw file count != automatic Mc qualification (must meet deduplication, validity, solo piano criteria).
2. License-unresolved status prevents premature confirmatory promotion without legal audit.
3. Parse success alone != confirmatory eligibility.
4. Mc >= 10 alone != composer qualification (must have verified source authority and rights).
5. Immutable fail-closed gate: live N_Russian remains 2 (Scriabin + Mussorgsky) until formal vendoring freeze.
"""

import json
from pathlib import Path

from russian_piano_composer.corpus.rc013_composer_pool import (
    derive_russian_composer_pool,
)


def test_live_production_pool_remains_fail_closed() -> None:
    """Verify production pool derivation remains N_Russian = 2 without unreviewed additions."""
    pool_res = derive_russian_composer_pool()
    assert pool_res.n_russian == 2
    assert "Alexander Scriabin" in pool_res.qualified_russian_composers
    assert "Modest Mussorgsky" in pool_res.qualified_russian_composers
    assert pool_res.rc012_resumption_status == "BLOCKED"


def test_rc014a_inventory_manifest_structure_and_completeness() -> None:
    """Verify RC-014A inventory manifest exists and contains exact audited counts."""
    manifest_path = Path("data/manifests/rc014a_tonal_piano_corpus_inventory.json")
    assert manifest_path.exists(), "Inventory manifest missing"

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["corpus_repository"] == "hectorbellmann-art/Tonal-Piano-Corpus"
    assert data["corpus_commit"] == "3f5a08e9b2360c11aea5d6d384eb84e7845b793c"

    # Prokofiev counts
    prok = data["prokofiev"]
    assert prok["raw_xml_count"] == 12
    assert len(prok["works"]) == 12
    assert all(w["rc011_56_descriptor_compatible"] for w in prok["works"])
    assert all(w["source_tiff_count"] > 0 for w in prok["works"])

    # Rubinstein counts
    rub = data["rubinstein"]
    assert rub["raw_xml_count"] == 11
    assert len(rub["works"]) == 11
    assert all(w["rc011_56_descriptor_compatible"] for w in rub["works"])
    assert all(w["source_tiff_count"] > 0 for w in rub["works"])


def test_rc014a_compatibility_manifest_verdict() -> None:
    """Verify all 23 works across both composers extracted 56 RC-011 features."""
    comp_path = Path("data/manifests/rc014a_rc011_compatibility_audit.json")
    assert comp_path.exists(), "Compatibility manifest missing"

    with open(comp_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["feature_catalog_descriptor_count"] == 56
    assert data["prokofiev_summary"]["files_passing_56_descriptors"] == 12
    assert data["prokofiev_summary"]["files_failing"] == 0
    assert data["rubinstein_summary"]["files_passing_56_descriptors"] == 11
    assert data["rubinstein_summary"]["files_failing"] == 0


def test_rc014a_rights_audit_distinguishes_jurisdictions() -> None:
    """Verify rights audit enforces strict US vs EU distinction for Prokofiev."""
    rights_path = Path("data/manifests/rc014a_rights_and_license_audit.json")
    assert rights_path.exists(), "Rights manifest missing"

    with open(rights_path, encoding="utf-8") as f:
        data = json.load(f)

    prok_legal = data["legal_analysis"]["Sergei_Prokofiev"]
    assert prok_legal["pre_1929_eligible_count"] == 8
    assert prok_legal["post_1928_count"] == 4
    assert prok_legal["qualification_verdict"].startswith("PARTIALLY_PUBLIC_DOMAIN")

    rub_legal = data["legal_analysis"]["Anton_Rubinstein"]
    assert rub_legal["public_domain_status"] == "PUBLIC_DOMAIN_WORLDWIDE"
    assert rub_legal["qualification_verdict"] == "RIGHTS_CLEAR_FOR_SCIENTIFIC_EVALUATION"


def test_rc014a_source_authority_symmetry() -> None:
    """Verify source authority comparison maintains symmetric standards."""
    auth_path = Path("data/manifests/rc014a_source_authority_comparison.json")
    assert auth_path.exists(), "Source authority manifest missing"

    with open(auth_path, encoding="utf-8") as f:
        data = json.load(f)

    tpc_eval = data["comparison_targets"]["Tonal_Piano_Corpus"]["symmetry_assessment"]
    assert "MEETS_SOURCE_LINKED_STANDARD" in tpc_eval


def test_rc014b_external_access_policy_manifest_safety() -> None:
    """Verify RC-014B non-vendored policy enforces fail-closed redistribution constraints."""
    policy_path = Path("data/manifests/rc014b_external_access_policy.json")
    assert policy_path.exists(), "RC-014B policy manifest missing"

    with open(policy_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["access_mode"] == "NON_VENDORED_REFERENCE_ACCESS"
    assert data["license_status"] == "UNDECLARED"
    assert data["policy_verdict"] == "RC014B_NONVENDORED_REFERENCE_PATH_VALID"
    assert data["raw_file_redistribution_permitted"] is False
    assert data["derived_feature_extraction_permitted"] is True
    assert data["corpus_root_tree"] == "2e86805f11040570d1f2f45bc0f03be408ca4997"
    assert len(data["reference_manifest"]) == 23


def test_rc014b_source_authority_dimensional_assessment() -> None:
    """Verify multidimensional authority evaluation separates scans from license clarity."""
    auth_dim_path = Path("data/manifests/rc014b_source_authority_dimensions.json")
    assert auth_dim_path.exists(), "RC-014B source authority dimensional manifest missing"

    with open(auth_dim_path, encoding="utf-8") as f:
        data = json.load(f)

    tpc_eval = data["corpora_evaluations"]["Tonal_Piano_Corpus"]
    assert "VERY_HIGH" in tpc_eval["SOURCE_SCAN_TRANSPARENCY"]
    assert "UNDECLARED" in tpc_eval["LICENSE_CLARITY"]


def test_rc014b_license_undeclared_disallows_ready_for_vendoring() -> None:
    """Verify that undeclared digital license strictly prevents READY_FOR_VENDORING status."""
    policy_path = Path("data/manifests/rc014b_external_access_policy.json")
    with open(policy_path, encoding="utf-8") as f:
        data = json.load(f)

    # When license is UNDECLARED, raw redistribution cannot be permitted
    if data["license_status"] == "UNDECLARED":
        assert data["raw_file_redistribution_permitted"] is False
        assert data["policy_verdict"] != "READY_FOR_VENDORING"
        assert data["policy_verdict"] == "RC014B_NONVENDORED_REFERENCE_PATH_VALID"


def test_rc014b_technical_compatibility_distinct_from_redistribution() -> None:
    """Verify 56-feature extraction success does not imply redistribution rights."""
    comp_path = Path("data/manifests/rc014a_rc011_compatibility_audit.json")
    policy_path = Path("data/manifests/rc014b_external_access_policy.json")

    with open(comp_path, encoding="utf-8") as f:
        comp_data = json.load(f)
    with open(policy_path, encoding="utf-8") as f:
        policy_data = json.load(f)

    # 100% technical compatibility
    assert comp_data["prokofiev_summary"]["files_passing_56_descriptors"] == 12
    assert comp_data["rubinstein_summary"]["files_passing_56_descriptors"] == 11

    # But redistribution is strictly false
    assert policy_data["raw_file_redistribution_permitted"] is False


def test_rc014b_prokofiev_symbolic_coverage_audit() -> None:
    """Verify Visions Fugitives full 20-piece coverage audit is recorded and verified."""
    cov_path = Path("data/manifests/rc014b_prokofiev_symbolic_coverage.json")
    assert cov_path.exists(), "Prokofiev coverage manifest missing"

    with open(cov_path, encoding="utf-8") as f:
        data = json.load(f)

    vf_audit = data["visions_fugitives_op22_full_cycle_audit"]
    assert len(vf_audit["availability_matrix"]) == 20
    assert vf_audit["global_public_domain"] is True
    assert data["confirmatory_supplementation_path"]["target_pieces_count"] == 10



