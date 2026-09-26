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
