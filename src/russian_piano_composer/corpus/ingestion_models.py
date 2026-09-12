"""
Dataclasses for raw corpus acquisition and canonical symbolic score ingestion receipts.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ArtifactReceipt:
    """
    Provenance receipt for an individual acquired raw artifact file.
    """

    relative_path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class AcquisitionReceipt:
    """
    Receipt recording the verified local acquisition of a single corpus source.
    """

    corpus_id: str
    source_repository: str
    source_commit: str
    meta_repository_commit: str
    manifest_hash: str
    acquired_at: str
    verification_status: str
    artifact_count: int
    artifacts: tuple[ArtifactReceipt, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save_json(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, source: Path) -> "AcquisitionReceipt":
        with open(source, encoding="utf-8") as f:
            data = json.load(f)
        artifacts = tuple(ArtifactReceipt(**art) for art in data["artifacts"])
        data["artifacts"] = artifacts
        return cls(**data)


@dataclass(frozen=True, slots=True)
class IngestionReceipt:
    """
    Receipt recording symbolic score ingestion metrics and semantic hashes for a corpus.
    """

    corpus_id: str
    source_commit: str
    manifest_hash: str
    canonical_schema_version: int
    parser: str
    parser_version: str
    expected_score_entries: int
    ingested_score_entries: int
    failed_score_entries: int
    status: str
    warnings: tuple[str, ...]
    piece_hashes: dict[str, str]
    corpus_canonical_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save_json(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, source: Path) -> "IngestionReceipt":
        with open(source, encoding="utf-8") as f:
            data = json.load(f)
        data["warnings"] = tuple(data["warnings"])
        return cls(**data)
