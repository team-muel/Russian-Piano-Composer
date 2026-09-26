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


def test_rc014a_rights_audit_marked_superseded() -> None:
    """Verify historical RC-014A rights manifest is explicitly marked as superseded by RC-014B."""
    rights_path = Path("data/manifests/rc014a_rights_and_license_audit.json")
    assert rights_path.exists(), "Rights manifest missing"

    with open(rights_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("artifact_status") == "SUPERSEDED_BY_RC014B"
    assert "data/manifests/rc014b_external_access_policy.json" in data.get("superseded_by", "")


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
    assert data["legal_governance_axes"]["technical_reproducibility"] == "TECHNICALLY_VALID"
    assert data["legal_governance_axes"]["legal_redistribution_authority"] == "LEGAL_AUTHORITY_PENDING"
    assert data["legal_governance_axes"]["composite_policy_verdict"] == "RC014B_NONVENDORED_REFERENCE_PATH_TECHNICALLY_VALID_LEGAL_AUTHORITY_PENDING"
    assert data["raw_file_redistribution_permitted"] is False
    assert data["derived_feature_extraction_technically_supported"] is True
    assert data["derived_feature_retention_authority"] == "PENDING"
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
        assert "READY_FOR_VENDORING" not in data["legal_governance_axes"]["composite_policy_verdict"]


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

    # Guard against false availability claims
    asap_claims = [row for row in vf_audit["availability_matrix"] if "PRESENT" in row["asap_status"]]
    assert len(asap_claims) == 0, "ASAP must not be claimed to contain Op.22 scores without proof"

    # Craig Humdrum verified supplements
    verified_supps = data["verified_supplement_records"]
    assert len(verified_supps) == 2
    assert verified_supps[0]["piece_identifier"] == "prokofiev_op22_no02"
    assert verified_supps[1]["piece_identifier"] == "prokofiev_op22_no03"
    assert all("PASS" in s["rc011_compatibility"] for s in verified_supps)


def test_rc014b_unicode_paths_roundtrip_integrity() -> None:
    """Verify all 23 manifest entries preserve valid Unicode paths without question marks."""
    policy_path = Path("data/manifests/rc014b_external_access_policy.json")
    with open(policy_path, encoding="utf-8") as f:
        data = json.load(f)

    for entry in data["reference_manifest"]:
        rel = entry["relative_path"]
        assert "?" not in rel, f"Path {rel} contains corrupted Unicode replacement character '?'"
        assert len(entry["sha256"]) == 64
        assert len(entry["git_blob_sha"]) == 40


def test_rc014b2_humdrum_supplement_receipts_and_invariants() -> None:
    """Verify persisted technical receipts for Prokofiev Op.22 Nos. 2 & 3 supplements."""
    r2_path = Path("data/reviews/rc014/prokofiev_op22_no02_technical_receipt.json")
    r3_path = Path("data/reviews/rc014/prokofiev_op22_no03_technical_receipt.json")

    assert r2_path.exists(), "Op. 22 No. 2 technical receipt missing"
    assert r3_path.exists(), "Op. 22 No. 3 technical receipt missing"

    with open(r2_path, encoding="utf-8") as f:
        r2 = json.load(f)
    with open(r3_path, encoding="utf-8") as f:
        r3 = json.load(f)

    # Check repository identity and frozen commit
    for r in [r2, r3]:
        assert r["source_repository"] == "automata/ana-music"
        assert r["source_commit"] == "335cbdc617c919d29e9384c4e490cabca5736f73"
        assert r["root_tree"] == "a7f14da4844b47ac3484b01d5d3da2a0029e4b6a"
        assert r["converter"] == "music21"
        assert r["rc011_56_descriptor_extraction_status"] == "PASS"
        assert r["schema_hash"] == "924a19913f831c4f0ffba2dfa88188b88e598af635046b05e580e5b807355282"

    # Check Op. 22 No. 2 invariants
    assert r2["canonical_measure_count"] == 24
    assert r2["git_blob_sha"] == "8ecec739bc4c7f561e2c7c141aff1cf40d9d3c0d"
    assert r2["sha256"] == "944d176184b7311f3a9faee8726fb2583287fce0caf984e7118d37c4c37d71a3"
    assert r2["source_metadata"]["OMD"] == "Andante"
    assert r2["source_metadata"]["ENC"] == "Craig Stuart Sapp"

    # Check Op. 22 No. 3 invariants
    assert r3["canonical_measure_count"] == 28
    assert r3["git_blob_sha"] == "d7554373b3d67e4606f9f2f5f79b34608a000b12"
    assert r3["sha256"] == "5d8d2a84e7b39df25553c4175fdf56ea52a655fa1ca58abc9aaf68db30848399"
    assert r3["source_metadata"]["OMD"] == "Allegretto"
    assert r3["source_metadata"]["ENC"] == "Craig Stuart Sapp"





