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
EXPECTED_V1_MANIFEST_HASH = "a6ba879b19b248582aaf73147241bc464125235bdd391fb93c5128c616da922e"


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


def test_license_claims_and_non_commercial():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    medtner_src = manifest.get_source("dcml_medtner_tales")

    assert medtner_src.license == "CC BY-NC-SA 4.0"
    assert medtner_src.is_non_commercial is True
    assert len(medtner_src.license_claims) == 3

    claim_types = {claim.source_type for claim in medtner_src.license_claims}
    assert claim_types == {"README", "CITATION_CFF", "ZENODO"}


def test_rachmaninoff_coverage_and_split_files():
    manifest = load_manifest(CANONICAL_MANIFEST_PATH)
    rach_src = manifest.get_source("dcml_rachmaninoff_op42")

    assert rach_src.work_count == 1
    assert rach_src.piece_count == 20
    assert rach_src.source_file_count == 24
    assert rach_src.representative_of_full_composer_output is False


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

    # Modify source commit SHA
    raw_data["sources"][0]["source_commit"] = "0000000000000000000000000000000000000000"
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
