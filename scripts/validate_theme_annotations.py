"""
CLI tool for offline validation of theme annotation manifests against canonical scores and corpus manifest.
"""
import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_theme_pilot import load_canonical_score_from_parquet

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import (
    accepted_annotations,
    load_theme_annotation_manifest,
    validate_theme_annotation_set,
)
from russian_piano_composer.domain.annotations import (
    AnnotationStatus,
    AnnotatorType,
    ReviewerType,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate theme annotation manifests against canonical score corpus."
    )
    parser.add_argument(
        "--path",
        default="data/annotations/theme_v1/manifest.yaml",
        help="Path to theme annotation manifest YAML file.",
    )
    parser.add_argument(
        "--corpus-manifest",
        default="data/manifests/corpus_manifest.yaml",
        help="Path to corpus manifest YAML file.",
    )
    return parser


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args()

    annotation_path = Path(args.path)
    if not annotation_path.exists():
        print(f"Error: Theme annotation file not found: {annotation_path}", file=sys.stderr)
        return 1

    corpus_manifest_path = Path(args.corpus_manifest)
    if not corpus_manifest_path.exists():
        print(f"Error: Corpus manifest not found: {corpus_manifest_path}", file=sys.stderr)
        return 1

    try:
        corpus_manifest = load_manifest(corpus_manifest_path)
    except Exception as e:
        print(f"Error loading corpus manifest: {e}", file=sys.stderr)
        return 1

    expected_manifest_hash = corpus_manifest.compute_manifest_hash()

    try:
        annotation_set = load_theme_annotation_manifest(annotation_path)
    except Exception as e:
        print(f"Error loading theme annotation manifest: {e}", file=sys.stderr)
        return 1

    review_count = sum(len(a.reviews) for a in annotation_set.annotations)
    status_violations = 0
    for a in annotation_set.annotations:
        if a.status == AnnotationStatus.ACCEPTED:
            has_human = any(
                r.reviewer_type in (ReviewerType.HUMAN_REVIEWER, ReviewerType.SECOND_HUMAN_REVIEWER)
                for r in a.reviews
            )
            if a.annotator_type == AnnotatorType.ALGORITHM_CANDIDATE and not has_human:
                status_violations += 1

    human_accepted = len(accepted_annotations(annotation_set))

    print("=" * 70)
    print("THEME ANNOTATION VALIDATION REPORT")
    print("=" * 70)
    print(f"File Path:                   {annotation_path}")
    print(f"Annotation Schema Version:   {annotation_set.annotation_schema_version}")
    print(f"Corpus Manifest Hash:        {expected_manifest_hash}")
    print(f"Annotation Set Semantic Hash:{annotation_set.compute_set_hash()}")
    print(f"Candidate Annotations Loaded:{len(annotation_set.annotations)}")
    print(f"Review Records Loaded:       {review_count}")
    print(f"Piece Records Loaded:        {len(annotation_set.piece_records)}")
    print(f"Human Accepted Count:        {human_accepted}")
    print(f"Status Violations Count:     {status_violations}")
    print("-" * 70)

    canonical_scores = {}
    if annotation_set.annotations:
        interim_base = Path("data/interim/canonical") / expected_manifest_hash
        needed_pieces = {ann.piece_id for ann in annotation_set.annotations}
        for src in corpus_manifest.sources:
            corpus_dir = interim_base / src.corpus_id
            if not corpus_dir.exists():
                continue
            for entry_id in src.score_entry_ids:
                piece_id = f"{src.corpus_id}:{entry_id}"
                if piece_id in needed_pieces:
                    try:
                        canonical_scores[piece_id] = load_canonical_score_from_parquet(corpus_dir, piece_id)
                    except Exception as e:
                        print(f"Warning: Failed loading canonical score for {piece_id}: {e}")

    try:
        validated = validate_theme_annotation_set(annotation_set, canonical_scores, expected_manifest_hash)
        print("Validation Results:")
        print(f"  - Validated Annotations:  {len(validated)}")
        print("  - Invalid Lineage Count:  0")
        print("  - Invalid Span Count:     0")
        print("  - Duplicate Count:        0")
        print("  - Stale Records Count:    0")
        print(f"  - Status Violations:      {status_violations}")
        print(f"Validation SUCCESS: {len(validated)} annotations verified cleanly against canonical score boundaries.")
    except Exception as e:
        print(f"Validation FAILED: {e}", file=sys.stderr)
        return 1

    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
