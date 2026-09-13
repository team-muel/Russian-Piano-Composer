"""Script to verify end-to-end reproducibility of feature extraction across independent runs.

This script executes two completely independent feature extraction runs starting from
fresh process calls / fresh canonical corpus loads, writes output to isolated temporary
directories, and compares all piece IDs, canonical piece hashes, column IDs, feature values,
policy hashes, and scientific matrix semantic hashes.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Add src and scripts to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from compute_corpus_features import reconstruct_score_from_parquet

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.features import CorpusFeatureMatrix
from russian_piano_composer.features import FEATURE_REGISTRY, extract_piece_features
from russian_piano_composer.features.policy import FeatureExtractionPolicy


def run_extraction(output_dir: Path) -> dict:
    """Run independent feature extraction pipeline and save output json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical")

    policy = FeatureExtractionPolicy()
    piece_features_list = []

    for source in manifest.sources:
        corpus_dir = interim_base / manifest_hash / source.corpus_id
        if not corpus_dir.exists():
            continue

        pieces_df = pd.read_parquet(corpus_dir / "pieces.parquet")
        measures_df = pd.read_parquet(corpus_dir / "measures.parquet")
        events_df = pd.read_parquet(corpus_dir / "events.parquet")

        piece_ids = sorted(pieces_df["piece_id"].unique())
        for pid in piece_ids:
            score = reconstruct_score_from_parquet(
                pieces_df, measures_df, events_df, str(pid), source
            )
            features = extract_piece_features(score, manifest_hash=manifest_hash, policy=policy)
            piece_features_list.append(features)

    matrix = CorpusFeatureMatrix(
        pieces=tuple(piece_features_list),
        manifest_hash=manifest_hash,
        feature_registry=FEATURE_REGISTRY,
        feature_policy_hash=policy.compute_policy_hash(),
    )

    summary = {
        "manifest_hash": matrix.manifest_hash,
        "feature_schema_version": matrix.feature_schema_version,
        "feature_policy_hash": matrix.feature_policy_hash,
        "matrix_hash": matrix.compute_matrix_hash(),
        "piece_count": len(matrix.pieces),
        "piece_ids": [pf.piece_id for pf in matrix.pieces],
        "canonical_piece_hashes": [pf.canonical_piece_hash for pf in matrix.pieces],
        "feature_names": [fd.feature_id for fd in matrix.feature_registry],
        "rows": [pf.features for pf in matrix.pieces]
    }

    out_file = output_dir / "summary.json"
    out_file.write_text(json.dumps(summary, indent=2))
    return summary


def main():
    print("--- Running Feature Reproducibility Verification ---")
    tmp_run1 = Path(tempfile.mkdtemp(prefix="repro_run1_"))
    tmp_run2 = Path(tempfile.mkdtemp(prefix="repro_run2_"))

    try:
        print(f"Run 1 output destination: {tmp_run1}")
        res1 = run_extraction(tmp_run1)
        print(f"Run 1 Policy Hash: {res1['feature_policy_hash']}")
        print(f"Run 1 Matrix Hash: {res1['matrix_hash']}")

        print(f"Run 2 output destination: {tmp_run2}")
        res2 = run_extraction(tmp_run2)
        print(f"Run 2 Policy Hash: {res2['feature_policy_hash']}")
        print(f"Run 2 Matrix Hash: {res2['matrix_hash']}")

        # Audit checks
        row_mismatch = 0
        col_mismatch = 0
        val_mismatch = 0

        if res1["piece_ids"] != res2["piece_ids"]:
            row_mismatch += 1
            print("ERROR: Piece IDs mismatch")

        if res1["canonical_piece_hashes"] != res2["canonical_piece_hashes"]:
            row_mismatch += 1
            print("ERROR: Canonical piece hashes mismatch")

        if res1["feature_names"] != res2["feature_names"]:
            col_mismatch += 1
            print("ERROR: Feature names mismatch")

        if res1["rows"] != res2["rows"]:
            val_mismatch += 1
            print("ERROR: Feature values mismatch")

        policy_mismatch = 1 if res1["feature_policy_hash"] != res2["feature_policy_hash"] else 0
        matrix_mismatch = 1 if res1["matrix_hash"] != res2["matrix_hash"] else 0

        print("\n--- Reproducibility Comparison Results ---")
        print(f"Row mismatches: {row_mismatch}")
        print(f"Column mismatches: {col_mismatch}")
        print(f"Value mismatches: {val_mismatch}")
        print(f"Policy hash mismatches: {policy_mismatch}")
        print(f"Matrix hash mismatches: {matrix_mismatch}")

        if any([row_mismatch, col_mismatch, val_mismatch, policy_mismatch, matrix_mismatch]):
            print("\nResult: REPRODUCIBILITY FAILED")
            sys.exit(1)
        else:
            print("\nResult: 100% PERFECT REPRODUCIBILITY VERIFIED")
            sys.exit(0)
    finally:
        shutil.rmtree(tmp_run1, ignore_errors=True)
        shutil.rmtree(tmp_run2, ignore_errors=True)


if __name__ == "__main__":
    main()
