"""
Unit tests for raw corpus acquisition and receipt verification (network-free).
"""

from pathlib import Path

import pytest

from russian_piano_composer.corpus.acquisition import (
    EXPECTED_MANIFEST_HASH,
    acquire_corpus_source,
)
from russian_piano_composer.domain.corpus import CorpusRole, CorpusSource


@pytest.fixture
def sample_corpus_source() -> CorpusSource:
    return CorpusSource(
        corpus_id="dcml_medtner_tales",
        title="DCML Medtner Skazki",
        role=CorpusRole.GENERATIVE_RUSSIAN,
        composer="Nikolai Medtner",
        repertoire_scope="Medtner Skazki Op. 8",
        license="CC BY-NC-SA 4.0",
        verified_at="2026-09-13",
        score_entry_count=19,
        musical_piece_count=19,
        notation_score_file_count=19,
        tabular_artifact_file_count=76,
        source_provider="DCML EPFL",
        source_repository="https://github.com/DCMLab/medtner_tales",
        meta_repository_commit="12be0d3ff7c6e0ef67c7d4e8e44541e5f288f39d",
        source_commit="1d2e58ba8d329463829e45e75900af43be4256bf",
    )


def test_acquire_corpus_source_fresh_clone_and_verify(
    sample_corpus_source: CorpusSource, tmp_path: Path
) -> None:
    raw_base = tmp_path / "data" / "raw"
    target_repo = raw_base / sample_corpus_source.corpus_id / sample_corpus_source.source_commit / "repository"

    def mock_git_runner(args: list[str], cwd: Path) -> str:
        if args == ["rev-parse", "HEAD"]:
            return sample_corpus_source.source_commit
        if args[0] == "checkout":
            return ""
        return ""

    # Pre-populate fake repo directory as if git cloned
    target_repo.mkdir(parents=True, exist_ok=True)
    (target_repo / "op08n01.mscx").write_text("<museScore version='3.01'></museScore>", encoding="utf-8")
    (target_repo / "notes.tsv").write_text("piece\tnote\n", encoding="utf-8")

    res = acquire_corpus_source(
        source=sample_corpus_source,
        manifest_hash=EXPECTED_MANIFEST_HASH,
        raw_base_dir=raw_base,
        verify_only=False,
        git_runner=mock_git_runner,
    )

    assert res.status == "ACQUIRED"
    assert res.receipt is not None
    assert res.receipt.artifact_count == 2
    assert (raw_base / sample_corpus_source.corpus_id / sample_corpus_source.source_commit / "acquisition_receipt.json").exists()

    # Re-run acquisition (idempotency check)
    res_rerun = acquire_corpus_source(
        source=sample_corpus_source,
        manifest_hash=EXPECTED_MANIFEST_HASH,
        raw_base_dir=raw_base,
        verify_only=False,
        git_runner=mock_git_runner,
    )
    assert res_rerun.status == "SKIPPED_ALREADY_VERIFIED"


def test_acquire_corpus_source_tampered_file_fails(
    sample_corpus_source: CorpusSource, tmp_path: Path
) -> None:
    raw_base = tmp_path / "data" / "raw"
    target_repo = raw_base / sample_corpus_source.corpus_id / sample_corpus_source.source_commit / "repository"

    def mock_git_runner(args: list[str], cwd: Path) -> str:
        return sample_corpus_source.source_commit

    target_repo.mkdir(parents=True, exist_ok=True)
    score_file = target_repo / "op08n01.mscx"
    score_file.write_text("<original_content/>", encoding="utf-8")

    # Perform initial valid acquisition
    res = acquire_corpus_source(
        source=sample_corpus_source,
        manifest_hash=EXPECTED_MANIFEST_HASH,
        raw_base_dir=raw_base,
        verify_only=False,
        git_runner=mock_git_runner,
    )
    assert res.status == "ACQUIRED"

    # Tamper with score file
    score_file.write_text("<TAMPERED_CONTENT/>", encoding="utf-8")

    # Verify must fail
    res_tampered = acquire_corpus_source(
        source=sample_corpus_source,
        manifest_hash=EXPECTED_MANIFEST_HASH,
        raw_base_dir=raw_base,
        verify_only=True,
        git_runner=mock_git_runner,
    )
    assert res_tampered.status == "FAILED"
    assert "SHA-256 mismatch" in res_tampered.message
