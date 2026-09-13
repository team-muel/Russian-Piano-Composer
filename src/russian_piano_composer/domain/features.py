"""
Domain models for objective descriptive music features.

Every feature is classified by provenance (OBSERVED, LITERATURE, HYPOTHESIS,
ENGINEERING_HEURISTIC) per the project's scientific integrity rules.
"""
import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

FEATURE_SCHEMA_VERSION: int = 1


class FeatureProvenance(StrEnum):
    """Provenance classification for a stylistic or descriptive feature."""

    OBSERVED = "OBSERVED"
    LITERATURE = "LITERATURE"
    HYPOTHESIS = "HYPOTHESIS"
    ENGINEERING_HEURISTIC = "ENGINEERING_HEURISTIC"


@dataclass(frozen=True, slots=True)
class FeatureDefinition:
    """
    Metadata describing a single named feature.
    """

    feature_id: str
    name: str
    description: str
    provenance: FeatureProvenance
    unit: str
    dtype: str

    def __post_init__(self) -> None:
        if not self.feature_id or not self.feature_id.strip():
            raise ValueError("FeatureDefinition.feature_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("FeatureDefinition.name cannot be empty.")
        if not isinstance(self.provenance, FeatureProvenance):
            raise TypeError(
                f"provenance must be a FeatureProvenance enum, got {type(self.provenance).__name__}."
            )


@dataclass(frozen=True, slots=True)
class PieceFeatureSet:
    """
    Immutable feature vector for a single canonical piece.
    """

    piece_id: str
    corpus_id: str
    corpus_role: str
    features: dict[str, float | int | None]
    manifest_hash: str
    canonical_piece_hash: str
    feature_schema_version: int = FEATURE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.piece_id or not self.piece_id.strip():
            raise ValueError("PieceFeatureSet.piece_id cannot be empty.")
        if not self.corpus_id or not self.corpus_id.strip():
            raise ValueError("PieceFeatureSet.corpus_id cannot be empty.")
        if not self.corpus_role or not self.corpus_role.strip():
            raise ValueError("PieceFeatureSet.corpus_role cannot be empty.")
        if self.feature_schema_version != FEATURE_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported feature_schema_version {self.feature_schema_version}. "
                f"Expected {FEATURE_SCHEMA_VERSION}."
            )


@dataclass(frozen=True, slots=True)
class CorpusFeatureMatrix:
    """
    Ordered collection of per-piece feature sets with a deterministic hash.
    """

    pieces: tuple[PieceFeatureSet, ...]
    manifest_hash: str
    feature_registry: tuple[FeatureDefinition, ...]
    feature_schema_version: int = FEATURE_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.pieces:
            raise ValueError("CorpusFeatureMatrix must contain at least one PieceFeatureSet.")
        if not self.feature_registry:
            raise ValueError("CorpusFeatureMatrix must have a non-empty feature_registry.")

        # Verify all pieces share the same manifest_hash
        for pfs in self.pieces:
            if pfs.manifest_hash != self.manifest_hash:
                raise ValueError(
                    f"PieceFeatureSet '{pfs.piece_id}' manifest_hash '{pfs.manifest_hash}' "
                    f"does not match matrix manifest_hash '{self.manifest_hash}'."
                )

        # Verify unique piece_ids
        ids = [pfs.piece_id for pfs in self.pieces]
        if len(ids) != len(set(ids)):
            raise ValueError("CorpusFeatureMatrix contains duplicate piece_ids.")

    def compute_matrix_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the feature matrix for reproducibility tracking.
        """
        sorted_pieces = sorted(self.pieces, key=lambda p: p.piece_id)
        sorted_registry = sorted(self.feature_registry, key=lambda f: f.feature_id)

        canonical: dict[str, Any] = {
            "manifest_hash": self.manifest_hash,
            "feature_schema_version": self.feature_schema_version,
            "registry": [
                {
                    "feature_id": fd.feature_id,
                    "provenance": fd.provenance.value,
                    "dtype": fd.dtype,
                }
                for fd in sorted_registry
            ],
            "pieces": [
                {
                    "piece_id": p.piece_id,
                    "corpus_id": p.corpus_id,
                    "corpus_role": p.corpus_role,
                    "canonical_piece_hash": p.canonical_piece_hash,
                    "features": {
                        k: v for k, v in sorted(p.features.items())
                    },
                }
                for p in sorted_pieces
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
