"""
Script to build the full 56-feature Structural Representation Matrix across 141 canonical scores.
"""

import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest

if TYPE_CHECKING:
    from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.structure_analysis.extractor import (
    StructuralExtractionPolicy,
    extract_structural_representation,
)
from russian_piano_composer.structure_analysis.lineage import (
    compute_structural_representation_lineage,
)
from russian_piano_composer.structure_analysis.matrix import (
    build_structural_representation_matrix,
)
from russian_piano_composer.structure_analysis.validation import (
    run_synthetic_validation_suite,
)


def main() -> None:
    print("==========================================================================")
    print(" RUSSIAN PIANO COMPOSER -- RC-011 STRUCTURAL MUSIC REPRESENTATION")
    print("==========================================================================")

    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    print(f"Loaded Manifest Hash: {manifest_hash}")

    interim_base = Path("data/interim/canonical") / manifest_hash
    if not interim_base.exists():
        print(f"Error: Parquet directory not found at {interim_base}")
        sys.exit(1)

    # 1. Run Synthetic Fixture Suite & Metamorphic Invariance Validation
    print("\n--- Running Synthetic Fixture Suite & Metamorphic Invariance ---")
    val_result = run_synthetic_validation_suite()
    print(f"  Assertions Passed:  {val_result.passed_assertions} / {val_result.total_assertions}")
    print(f"  Metamorphic Passed: {val_result.metamorphic_checks_passed} / {val_result.metamorphic_checks_total}")
    print(f"  Overall Status:     {val_result.overall_status}")

    # 2. Load 141 Canonical Scores
    print("\n--- Loading Canonical Scores ---")
    scores_by_id: dict[str, CanonicalScore] = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    n_scores = len(scores_by_id)
    print(f"Loaded {n_scores} canonical scores.")
    if n_scores != 141:
        raise RuntimeError(f"Expected 141 canonical scores, found {n_scores}.")

    # 3. Extract 56 Structural Features
    print("\n--- Extracting 56 Structural Features across 141 Pieces ---")
    t0 = time.time()
    policy = StructuralExtractionPolicy()
    piece_representations = {}

    for idx, (pid, score) in enumerate(sorted(scores_by_id.items()), start=1):
        if idx == 1 or idx % 5 == 0 or idx == n_scores:
            print(f"  Progress: {idx}/{n_scores} pieces processed... ({time.time() - t0:.1f}s elapsed)")
            sys.stdout.flush()
        rep = extract_structural_representation(score, manifest_hash=manifest_hash, policy=policy)
        piece_representations[pid] = rep.features

    elapsed = time.time() - t0
    print(f"Extraction completed in {elapsed:.1f}s.")

    # 4. Build Role-Blind Matrix & Lineage
    matrix = build_structural_representation_matrix(piece_representations, manifest_hash=manifest_hash)
    lineage = compute_structural_representation_lineage(manifest_hash, matrix, val_result, policy)
    bundle_hash = lineage.compute_bundle_hash()

    print("\n--- RC-011 Final Lineage Registry ---")
    print(f"  Master Baseline SHA:         {lineage.master_baseline_sha}")
    print(f"  Preregistration Commit SHA:  {lineage.preregistration_commit_sha}")
    print(f"  Canonical Manifest Hash:     {lineage.manifest_hash}")
    print(f"  Structural Schema Hash:      {lineage.structural_schema_hash}")
    print(f"  Structural Matrix Hash:      {lineage.structural_matrix_hash}")
    print(f"  Validation Result Hash:      {lineage.validation_result_hash}")
    print(f"  Lineage Bundle Hash:         {bundle_hash}")

    print("\n==========================================================================")
    print(f" STRUCTURAL REPRESENTATION STATUS = {val_result.overall_status}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
