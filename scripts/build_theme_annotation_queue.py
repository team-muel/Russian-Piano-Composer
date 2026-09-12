"""
CLI tool to construct deterministic theme annotation work queues and report annotation coverage progress.
"""
import argparse
import io
import sys
from pathlib import Path

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import load_theme_annotation_manifest
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.annotations import PieceReviewStatus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic theme annotation queues and report progress."
    )
    parser.add_argument(
        "--role",
        choices=["russian", "control", "all"],
        default="all",
        help="Filter corpus role for the queue.",
    )
    parser.add_argument(
        "--corpus-manifest",
        default="data/manifests/corpus_manifest.yaml",
        help="Path to corpus manifest YAML file.",
    )
    parser.add_argument(
        "--annotation-manifest",
        default="data/annotations/theme_v1/manifest.yaml",
        help="Path to theme annotation manifest YAML file.",
    )
    return parser


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args()

    corpus_manifest_path = Path(args.corpus_manifest)
    if not corpus_manifest_path.exists():
        print(f"Error: Corpus manifest not found: {corpus_manifest_path}", file=sys.stderr)
        return 1

    try:
        corpus_manifest = load_manifest(corpus_manifest_path)
    except Exception as e:
        print(f"Error loading corpus manifest: {e}", file=sys.stderr)
        return 1

    annotation_manifest_path = Path(args.annotation_manifest)
    annotation_set = None
    if annotation_manifest_path.exists():
        try:
            annotation_set = load_theme_annotation_manifest(annotation_manifest_path)
        except Exception as e:
            print(f"Warning: Failed loading annotation manifest ({e}). Operating with empty annotation state.")

    annotated_piece_ids = set()
    piece_records_map = {}
    if annotation_set:
        for ann in annotation_set.annotations:
            annotated_piece_ids.add(ann.piece_id)
        for rec in annotation_set.piece_records:
            piece_records_map[rec.piece_id] = rec.status

    target_sources = []
    if args.role in ("russian", "all"):
        target_sources.extend(corpus_manifest.generative_sources())
    if args.role in ("control", "all"):
        target_sources.extend(corpus_manifest.control_sources())

    target_sources.sort(key=lambda s: s.corpus_id)

    print("=" * 70)
    print("THEME ANNOTATION PROGRESS REPORT & WORK QUEUE")
    print("=" * 70)
    print(f"Corpus Manifest Hash: {corpus_manifest.compute_manifest_hash()}")
    if annotation_set:
        print(f"Annotation Set Hash:  {annotation_set.compute_set_hash()}")
        print(f"Total Annotations:    {len(annotation_set.annotations)}")
    print("-" * 70)

    queue = []
    tot_pieces = 0
    tot_unreviewed = 0
    tot_reviewed = 0
    tot_no_clear_theme = 0

    for source in target_sources:
        russian_label = "[RUSSIAN]" if source.role == CorpusRole.GENERATIVE_RUSSIAN else "[CONTROL]"
        print(f"\nCorpus: {source.corpus_id} {russian_label} ({source.composer})")

        for score_entry_id in source.score_entry_ids:
            tot_pieces += 1
            piece_id = f"{source.corpus_id}::{score_entry_id}"
            rec_status = piece_records_map.get(piece_id, PieceReviewStatus.UNREVIEWED)

            has_annos = piece_id in annotated_piece_ids

            if rec_status == PieceReviewStatus.NO_CLEAR_THEME:
                tot_no_clear_theme += 1
                tot_reviewed += 1
                status_str = "NO_CLEAR_THEME"
            elif has_annos or rec_status == PieceReviewStatus.REVIEWED:
                tot_reviewed += 1
                status_str = "REVIEWED"
            else:
                tot_unreviewed += 1
                status_str = "UNREVIEWED (QUEUED)"
                queue.append((source.corpus_id, score_entry_id, piece_id))

            print(f"  - {score_entry_id:<30} [{status_str}]")

    print("\n" + "=" * 70)
    print("SUMMARY METRICS")
    print("=" * 70)
    print(f"Total Pieces Analyzed:    {tot_pieces}")
    print(f"Pieces Reviewed:          {tot_reviewed}")
    print(f"Pieces Unreviewed (Queue):{tot_unreviewed}")
    print(f"No Clear Theme Pieces:    {tot_no_clear_theme}")
    print(f"Next Queued Piece:        {queue[0][2] if queue else 'None (Queue Empty)'}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
