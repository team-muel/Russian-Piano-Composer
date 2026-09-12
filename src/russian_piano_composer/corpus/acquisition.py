"""
Verifiable raw corpus acquisition module.

Manages idempotent git clone, exact commit pinning verification, SHA-256 receipt generation,
and fail-closed integrity checks for raw corpus sources.
"""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from russian_piano_composer.corpus.hashing import sha256_file
from russian_piano_composer.corpus.ingestion_models import AcquisitionReceipt, ArtifactReceipt
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.corpus import CorpusSource

EXPECTED_MANIFEST_HASH = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"

GitRunner = Callable[[list[str], Path], str]


def _default_git_runner(args: list[str], cwd: Path) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout.strip()


@dataclass(frozen=True, slots=True)
class AcquisitionResult:
    """
    Result report for a corpus acquisition operation.
    """

    corpus_id: str
    status: Literal["ACQUIRED", "VERIFIED", "SKIPPED_ALREADY_VERIFIED", "FAILED"]
    receipt: AcquisitionReceipt | None
    message: str = ""


def acquire_corpus_source(
    source: CorpusSource,
    manifest_hash: str,
    raw_base_dir: Path = Path("data/raw"),
    verify_only: bool = False,
    git_runner: GitRunner = _default_git_runner,
) -> AcquisitionResult:
    """
    Acquire or verify a single raw corpus source at its exact pinned commit.
    """

    if source.source_commit is None:
        return AcquisitionResult(
            corpus_id=source.corpus_id,
            status="FAILED",
            receipt=None,
            message="Source has no pinned source_commit",
        )

    target_dir = raw_base_dir / source.corpus_id / source.source_commit
    repo_dir = target_dir / "repository"
    receipt_path = target_dir / "acquisition_receipt.json"

    # Check existing acquisition
    if receipt_path.exists() and repo_dir.exists():
        try:
            receipt = AcquisitionReceipt.load_json(receipt_path)
            if receipt.manifest_hash != manifest_hash:
                return AcquisitionResult(
                    corpus_id=source.corpus_id,
                    status="FAILED",
                    receipt=None,
                    message=f"Manifest hash mismatch in receipt: got {receipt.manifest_hash}, expected {manifest_hash}",
                )
            if receipt.source_commit != source.source_commit:
                return AcquisitionResult(
                    corpus_id=source.corpus_id,
                    status="FAILED",
                    receipt=None,
                    message=f"Source commit mismatch in receipt: got {receipt.source_commit}, expected {source.source_commit}",
                )

            # Check Git HEAD in repo_dir
            head_commit = git_runner(["rev-parse", "HEAD"], repo_dir)
            if head_commit != source.source_commit:
                return AcquisitionResult(
                    corpus_id=source.corpus_id,
                    status="FAILED",
                    receipt=None,
                    message=f"Repository HEAD {head_commit} does not match pinned commit {source.source_commit}",
                )

            # Verify artifact SHAs
            for art in receipt.artifacts:
                art_path = repo_dir / art.relative_path
                if not art_path.exists():
                    return AcquisitionResult(
                        corpus_id=source.corpus_id,
                        status="FAILED",
                        receipt=None,
                        message=f"Artifact missing during verification: {art.relative_path}",
                    )
                if art_path.stat().st_size != art.size_bytes:
                    return AcquisitionResult(
                        corpus_id=source.corpus_id,
                        status="FAILED",
                        receipt=None,
                        message=f"Artifact size mismatch for {art.relative_path}",
                    )
                if sha256_file(art_path) != art.sha256:
                    return AcquisitionResult(
                        corpus_id=source.corpus_id,
                        status="FAILED",
                        receipt=None,
                        message=f"Artifact SHA-256 mismatch for {art.relative_path}",
                    )

            return AcquisitionResult(
                corpus_id=source.corpus_id,
                status="SKIPPED_ALREADY_VERIFIED" if not verify_only else "VERIFIED",
                receipt=receipt,
                message="Existing acquisition verified cleanly.",
            )
        except Exception as e:
            return AcquisitionResult(
                corpus_id=source.corpus_id,
                status="FAILED",
                receipt=None,
                message=f"Failed to verify existing acquisition: {e}",
            )

    if verify_only:
        return AcquisitionResult(
            corpus_id=source.corpus_id,
            status="FAILED",
            receipt=None,
            message=f"Acquisition directory missing or incomplete: {target_dir}",
        )

    # Perform fresh clone
    repo_url = source.source_repository
    if not repo_url.startswith("http://") and not repo_url.startswith("https://"):
        repo_url = f"https://github.com/{source.source_repository}.git"

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        # Clone repo
        print(f"Cloning {repo_url} into {repo_dir}...")
        git_runner(["clone", repo_url, "repository"], target_dir)

        # Checkout pinned commit
        print(f"Checking out pinned commit {source.source_commit}...")
        git_runner(["checkout", source.source_commit], repo_dir)

        head_commit = git_runner(["rev-parse", "HEAD"], repo_dir)
        if head_commit != source.source_commit:
            raise RuntimeError(
                f"Checkout HEAD {head_commit} does not match pinned commit {source.source_commit}"
            )

        # Inventory relevant artifacts
        artifacts: list[ArtifactReceipt] = []
        for path in repo_dir.rglob("*"):
            if path.is_file() and not any(part.startswith(".git") for part in path.parts):
                rel_path = path.relative_to(repo_dir).as_posix()
                size = path.stat().st_size
                digest = sha256_file(path)
                artifacts.append(
                    ArtifactReceipt(relative_path=rel_path, size_bytes=size, sha256=digest)
                )

        artifacts_tuple = tuple(sorted(artifacts, key=lambda a: a.relative_path))
        receipt = AcquisitionReceipt(
            corpus_id=source.corpus_id,
            source_repository=source.source_repository,
            source_commit=source.source_commit,
            meta_repository_commit=source.meta_repository_commit or "",
            manifest_hash=manifest_hash,
            acquired_at=datetime.now(UTC).isoformat(),
            verification_status="VERIFIED",
            artifact_count=len(artifacts_tuple),
            artifacts=artifacts_tuple,
        )
        receipt.save_json(receipt_path)
        return AcquisitionResult(
            corpus_id=source.corpus_id,
            status="ACQUIRED",
            receipt=receipt,
            message="Fresh acquisition cloned and verified successfully.",
        )

    except Exception as e:
        return AcquisitionResult(
            corpus_id=source.corpus_id,
            status="FAILED",
            receipt=None,
            message=f"Acquisition failed: {e}",
        )


def acquire_all_corpora(
    manifest_path: Path = Path("data/manifests/corpus_manifest.yaml"),
    raw_base_dir: Path = Path("data/raw"),
    verify_only: bool = False,
) -> list[AcquisitionResult]:
    """
    Acquire and verify all registered corpus sources in the manifest.
    """
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    if manifest_hash != EXPECTED_MANIFEST_HASH:
        raise ValueError(
            f"Manifest hash mismatch: expected {EXPECTED_MANIFEST_HASH}, got {manifest_hash}"
        )

    results: list[AcquisitionResult] = []
    for src in manifest.sources:
        print(f"\nProcessing acquisition for {src.corpus_id}...")
        res = acquire_corpus_source(
            source=src,
            manifest_hash=manifest_hash,
            raw_base_dir=raw_base_dir,
            verify_only=verify_only,
        )
        print(f"  Result: {res.status} — {res.message}")
        results.append(res)
    return results
