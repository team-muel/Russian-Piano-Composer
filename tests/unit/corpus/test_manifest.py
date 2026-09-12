from pathlib import Path

import pytest
import yaml

from russian_piano_composer.corpus.manifest import (
    MANIFEST_SCHEMA_VERSION,
    CorpusManifest,
    load_manifest,
)
from russian_piano_composer.domain.corpus import CorpusRole

CANONICAL_MANIFEST_PATH = Path("data/manifests/corpus_manifest.yaml")
CANONICAL_INVENTORY_PATH = Path("data/manifests/source_inventory_v1.yaml")
EXPECTED_V1_MANIFEST_HASH = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"


def test_load_canonical_manifest():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    assert isinstance(manifest, CorpusManifest)
    assert manifest.manifest_version == MANIFEST_SCHEMA_VERSION
    assert len(manifest.sources) == 6


def test_generative_vs_control_isolation():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)

    gen_sources = manifest.generative_sources()
    ctrl_sources = manifest.control_sources()
    prov_sources = manifest.provisional_sources()
    excl_sources = manifest.excluded_sources()

    assert len(gen_sources) == 3
    assert len(ctrl_sources) == 3
    assert len(prov_sources) == 0
    assert len(excl_sources) == 0

    gen_ids = {s.corpus_id for s in gen_sources}
    ctrl_ids = {s.corpus_id for s in ctrl_sources}
    assert gen_ids.isdisjoint(ctrl_ids)

    # Fail closed verification: Pending rights review prevents generative eligibility
    for s in gen_sources:
        assert s.role == CorpusRole.GENERATIVE_RUSSIAN
        assert s.rights_review_required is True
        assert s.generative_eligible is False  # Fails closed until legal review

    for s in ctrl_sources:
        assert s.role == CorpusRole.CONTROL_NON_RUSSIAN
        assert s.generative_eligible is False


def test_license_claims_and_conflicts():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    medtner_src = manifest.get_source("dcml_medtner_tales")

    assert medtner_src.is_non_commercial is True
    assert len(medtner_src.license_claims) == 3

    claim_types = {claim.source_type for claim in medtner_src.license_claims}
    assert claim_types == {"README", "CITATION_CFF", "ZENODO"}

    # CITATION.cff says CC-BY-NC-4.0 while README says CC BY-NC-SA 4.0
    cff_claim = next(c for c in medtner_src.license_claims if c.source_type == "CITATION_CFF")
    readme_claim = next(c for c in medtner_src.license_claims if c.source_type == "README")
    assert cff_claim.value == "CC-BY-NC-4.0"
    assert readme_claim.value == "CC BY-NC-SA 4.0"
    assert medtner_src.rights_review_required is True


def test_medtner_pinned_inventory():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    medtner_src = manifest.get_source("dcml_medtner_tales")

    assert medtner_src.score_entry_count == 19
    assert len(medtner_src.score_entry_ids) == 19
    assert medtner_src.musical_piece_count == 19
    assert medtner_src.work_cycle_count == 7
    assert medtner_src.catalog_group_count == 7
    assert medtner_src.notation_score_file_count == 19
    assert medtner_src.tabular_artifact_file_count == 76
    assert medtner_src.source_commit == "1d2e58ba8d329463829e45e75900af43be4256bf"


def test_rachmaninoff_coverage_count_semantics():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    rach_src = manifest.get_source("dcml_rachmaninoff_op42")

    assert rach_src.score_entry_count == 22
    assert len(rach_src.score_entry_ids) == 22
    assert rach_src.variation_number_count == 20
    assert rach_src.work_cycle_count == 1
    assert rach_src.musical_piece_count is None  # Unambiguous piece mapping absent
    assert rach_src.notation_score_file_count == 24
    assert rach_src.tabular_artifact_file_count == 88
    assert rach_src.representative_of_full_composer_output is False
    assert rach_src.source_commit == "a73f3246a764215863000357c81309b210a43f15"


def test_liszt_coverage_count_semantics():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    liszt_src = manifest.get_source("dcml_liszt_annees")

    assert liszt_src.catalog_groups == ("S.160", "S.161", "S.162")
    assert liszt_src.catalog_group_count == 3
    assert liszt_src.score_entry_count == 19
    assert len(liszt_src.score_entry_ids) == 19
    assert liszt_src.musical_piece_count is None  # External 26 pieces not claimed
    assert liszt_src.work_cycle_count == 3
    assert liszt_src.notation_score_file_count == 19
    assert liszt_src.tabular_artifact_file_count == 76


def test_commit_sha_hex_validation():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    for src in manifest.sources:
        assert src.source_commit is not None
        assert len(src.source_commit) == 40
        assert all(c in "0123456789abcdef" for c in src.source_commit)
        assert src.meta_repository_commit is not None
        assert len(src.meta_repository_commit) == 40
        assert all(c in "0123456789abcdef" for c in src.meta_repository_commit)


def test_invalid_commit_sha_fails_closed(tmp_path: Path):
    with open(CANONICAL_MANIFEST_PATH, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    # Invalid pseudo-hash
    raw_data["sources"][0]["source_commit"] = "a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4"
    mod_path = tmp_path / "bad_sha.yaml"
    mod_path.write_text(yaml.dump(raw_data), encoding="utf-8")

    with pytest.raises(ValueError, match="must be a 40-character lowercase hex string"):
        load_manifest(mod_path)


def test_source_inventory_matching():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    with open(CANONICAL_INVENTORY_PATH, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    inv_sources = inventory["sources"]
    for src in manifest.sources:
        assert src.corpus_id in inv_sources
        inv_entry = inv_sources[src.corpus_id]
        assert inv_entry["commit"] == src.source_commit
        assert len(inv_entry["score_entries"]) == src.score_entry_count
        if src.score_entry_ids:
            assert tuple(inv_entry["score_entries"]) == src.score_entry_ids


def test_compute_manifest_hash_format_and_golden():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    manifest_hash = manifest.compute_manifest_hash()

    assert len(manifest_hash) == 64
    assert all(c in "0123456789abcdef" for c in manifest_hash)
    assert manifest_hash == EXPECTED_V1_MANIFEST_HASH


def test_manifest_hash_sensitivity(tmp_path: Path):
    with open(CANONICAL_MANIFEST_PATH, encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)

    base_manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    base_hash = base_manifest.compute_manifest_hash()

    # Modify source commit SHA to another valid hex string
    raw_data["sources"][0]["source_commit"] = "1d2e58ba8d329463829e45e75900af43be4256be"
    mod_path = tmp_path / "mod_commit.yaml"
    mod_path.write_text(yaml.dump(raw_data), encoding="utf-8")

    mod_manifest = load_manifest(mod_path)
    mod_hash = mod_manifest.compute_manifest_hash()

    assert mod_hash != base_hash
    assert len(mod_hash) == 64


def test_fail_closed_unsupported_version(tmp_path: Path):
    bad_manifest = tmp_path / "bad_version.yaml"
    bad_manifest.write_text(
        "manifest_version: 99\nsources: []\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Unsupported manifest_version 99"):
        load_manifest(bad_manifest)


def test_fail_closed_missing_version(tmp_path: Path):
    bad_manifest = tmp_path / "missing_version.yaml"
    bad_manifest.write_text("sources: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required key 'manifest_version'"):
        load_manifest(bad_manifest)


def test_fail_closed_unknown_top_level_key(tmp_path: Path):
    bad_manifest = tmp_path / "unknown_key.yaml"
    bad_manifest.write_text(
        "manifest_version: 1\nunknown_field: true\nsources: []\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="unknown top-level key"):
        load_manifest(bad_manifest)


def test_fail_closed_unknown_role(tmp_path: Path):
    raw_data = {
        "manifest_version": 1,
        "sources": [
            {
                "corpus_id": "test_src",
                "title": "Test Title",
                "role": "INVALID_ROLE_NAME",
                "composer": "Test Composer",
                "source_provider": "Test Provider",
                "source_repository": "https://example.com",
                "source_version": "1.0",
                "repertoire_scope": "Test Scope",
                "license": "CC0",
                "verified_at": "2026-09-13",
            }
        ],
    }
    bad_manifest = tmp_path / "unknown_role.yaml"
    bad_manifest.write_text(yaml.dump(raw_data), encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid or missing role"):
        load_manifest(bad_manifest)


def test_fail_closed_duplicate_corpus_id(tmp_path: Path):
    src_entry = {
        "corpus_id": "duplicate_id",
        "title": "Test Title",
        "role": "GENERATIVE_RUSSIAN",
        "composer": "Test Composer",
        "source_provider": "Test Provider",
        "source_repository": "https://example.com",
        "source_version": "1.0",
        "repertoire_scope": "Test Scope",
        "license": "CC0",
        "verified_at": "2026-09-13",
    }
    raw_data = {
        "manifest_version": 1,
        "sources": [src_entry, src_entry],
    }
    bad_manifest = tmp_path / "duplicate_id.yaml"
    bad_manifest.write_text(yaml.dump(raw_data), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate corpus_id detected"):
        load_manifest(bad_manifest)
