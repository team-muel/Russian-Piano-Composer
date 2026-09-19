"""
Script to build and display role-blind feature matrices and lineage hashes for RC-010.

Loads all 141 canonical scores from interim parquet cache, builds MODEL_A, MODEL_B,
and MODEL_C role-blind feature matrices, and prints schema and matrix hashes.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest

if TYPE_CHECKING:
    from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.style_analysis.features import (
    build_role_blind_feature_matrices,
    compute_style_feature_schema_hash,
)


def main() -> None:
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        print("Error: Canonical corpus parquet cache not found.")
        sys.exit(1)

    print("--- Building Role-Blind Style Feature Matrices ---")
    print(f"Manifest Hash: {manifest_hash}")
    sys.stdout.flush()

    scores_by_id: dict[str, CanonicalScore] = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    print(f"Loaded {len(scores_by_id)} canonical scores.")
    sys.stdout.flush()

    matrices = build_role_blind_feature_matrices(scores_by_id, manifest_hash=manifest_hash)

    print(f"CTU Style Feature Schema Hash: {compute_style_feature_schema_hash()}")
    for model_name, mat in matrices.items():
        print(f"  {model_name}: {len(mat.piece_ids)} rows x {len(mat.feature_names)} features | Matrix Hash: {mat.compute_matrix_hash()}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
