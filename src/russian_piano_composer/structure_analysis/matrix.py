"""
Role-Blind Structural Representation Matrix for RC-011.

Contains the 56-feature structural representation across all canonical pieces.
Strictly excludes all metadata, composer names, titles, paths, and class labels.
"""

import hashlib
import json
from dataclasses import dataclass

from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    AvailabilityStatus,
    FeatureValue,
    compute_structural_schema_hash,
)

FORBIDDEN_METADATA_TERMS: set[str] = {
    "composer",
    "composer_name",
    "corpus_role",
    "corpus_id",
    "GENERATIVE_RUSSIAN",
    "CONTROL_NON_RUSSIAN",
    "source_repository",
    "source_relative_path",
    "title",
    "rights_status",
    "generative_eligible",
}


@dataclass(frozen=True, slots=True)
class StructuralRepresentationMatrix:
    """
    Immutable, role-blind 56-feature structural representation matrix.
    """

    piece_ids: tuple[str, ...]
    feature_names: tuple[str, ...]
    data: tuple[tuple[float, ...], ...]
    availability_matrix: tuple[tuple[AvailabilityStatus, ...], ...]
    manifest_hash: str
    schema_hash: str

    def __post_init__(self) -> None:
        if not self.piece_ids:
            raise ValueError("StructuralRepresentationMatrix must contain piece_ids.")
        if not self.feature_names:
            raise ValueError("StructuralRepresentationMatrix must contain feature_names.")
        if len(self.data) != len(self.piece_ids):
            raise ValueError("data row count must match piece_ids length.")
        if len(self.availability_matrix) != len(self.piece_ids):
            raise ValueError("availability_matrix row count must match piece_ids length.")

        for col_name in self.feature_names:
            for term in FORBIDDEN_METADATA_TERMS:
                if term in col_name:
                    raise ValueError(f"Metadata term '{term}' forbidden in structural column '{col_name}'.")

    def compute_matrix_hash(self) -> str:
        """
        Deterministic SHA-256 hash of complete structural matrix and availability state.
        """
        canonical = {
            "version": "STRUCTURAL_REPRESENTATION_MATRIX_V1",
            "manifest_hash": self.manifest_hash,
            "schema_hash": self.schema_hash,
            "feature_names": list(self.feature_names),
            "rows": [
                {
                    "piece_id": pid,
                    "values": list(row),
                    "availability": [st.value for st in avail_row],
                }
                for pid, row, avail_row in zip(
                    self.piece_ids, self.data, self.availability_matrix, strict=True
                )
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def build_structural_representation_matrix(
    piece_representations: dict[str, dict[str, FeatureValue]],
    manifest_hash: str,
) -> StructuralRepresentationMatrix:
    """
    Construct the immutable StructuralRepresentationMatrix from extracted piece features.
    """
    sorted_piece_ids = tuple(sorted(piece_representations.keys()))
    sorted_feature_names = tuple(sorted(d.feature_id for d in STRUCTURAL_FEATURE_CATALOG))

    data_rows: list[tuple[float, ...]] = []
    avail_rows: list[tuple[AvailabilityStatus, ...]] = []

    for pid in sorted_piece_ids:
        p_feats = piece_representations[pid]
        row_vals: list[float] = []
        row_avail: list[AvailabilityStatus] = []

        for fname in sorted_feature_names:
            fv = p_feats.get(fname)
            if fv is None:
                raise ValueError(f"Missing feature '{fname}' in piece '{pid}'.")
            row_vals.append(fv.value)
            row_avail.append(fv.status)

        data_rows.append(tuple(row_vals))
        avail_rows.append(tuple(row_avail))

    return StructuralRepresentationMatrix(
        piece_ids=sorted_piece_ids,
        feature_names=sorted_feature_names,
        data=tuple(data_rows),
        availability_matrix=tuple(avail_rows),
        manifest_hash=manifest_hash,
        schema_hash=compute_structural_schema_hash(),
    )
