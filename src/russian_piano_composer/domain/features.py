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

FEATURE_SCHEMA_VERSION: int = 2


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
    comparison_ready: bool = True
    validity_category: str = "A"
    observation_unit: str = "note_attack"
    definition_id: str = "v2.0"

    def __post_init__(self) -> None:
        if not self.feature_id or not self.feature_id.strip():
            raise ValueError("FeatureDefinition.feature_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("FeatureDefinition.name cannot be empty.")
        if not isinstance(self.provenance, FeatureProvenance):
            raise TypeError(
                f"provenance must be a FeatureProvenance enum, got {type(self.provenance).__name__}."
            )

    def compute_semantic_hash(self) -> str:
        """Deterministic SHA-256 hash of descriptor scientific semantics."""
        canonical = {
            "feature_id": self.feature_id,
            "name": self.name,
            "description": self.description,
            "definition_id": self.definition_id,
            "provenance": self.provenance.value,
            "unit": self.unit,
            "dtype": self.dtype,
            "comparison_ready": self.comparison_ready,
            "validity_category": self.validity_category,
            "observation_unit": self.observation_unit,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def compute_schema_semantic_hash(registry: tuple[FeatureDefinition, ...]) -> str:
    """
    Deterministic SHA-256 hash of the complete feature schema registry descriptors.
    """
    sorted_reg = sorted(registry, key=lambda f: f.feature_id)
    canonical = {
        "version": FEATURE_SCHEMA_VERSION,
        "descriptors": [
            {
                "feature_id": fd.feature_id,
                "name": fd.name,
                "description": fd.description,
                "definition_id": fd.definition_id,
                "provenance": fd.provenance.value,
                "unit": fd.unit,
                "dtype": fd.dtype,
                "comparison_ready": fd.comparison_ready,
                "validity_category": fd.validity_category,
                "observation_unit": fd.observation_unit,
            }
            for fd in sorted_reg
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
    feature_policy_hash: str = ""

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
    feature_policy_hash: str = ""

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
        Includes feature extraction policy identity and schema semantic fingerprint.
        """
        sorted_pieces = sorted(self.pieces, key=lambda p: p.piece_id)
        schema_hash = compute_schema_semantic_hash(self.feature_registry)

        canonical: dict[str, Any] = {
            "manifest_hash": self.manifest_hash,
            "feature_schema_version": self.feature_schema_version,
            "feature_schema_semantic_hash": schema_hash,
            "feature_policy_hash": self.feature_policy_hash,
            "registry": [
                {
                    "feature_id": fd.feature_id,
                    "provenance": fd.provenance.value,
                    "dtype": fd.dtype,
                    "validity_category": fd.validity_category,
                    "comparison_ready": fd.comparison_ready,
                    "observation_unit": fd.observation_unit,
                }
                for fd in sorted(self.feature_registry, key=lambda f: f.feature_id)
            ],
            "pieces": [
                {
                    "piece_id": p.piece_id,
                    "corpus_id": p.corpus_id,
                    "corpus_role": p.corpus_role,
                    "canonical_piece_hash": p.canonical_piece_hash,
                    "feature_policy_hash": p.feature_policy_hash,
                    "features": {
                        k: v for k, v in sorted(p.features.items())
                    },
                }
                for p in sorted_pieces
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
