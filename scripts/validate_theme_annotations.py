"""
CLI tool for offline validation of theme annotation manifests against canonical scores and corpus manifest.
"""
import argparse
import io
import sys
from pathlib import Path

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import (
    load_theme_annotation_manifest,
    validate_theme_annotation_set,
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

    print("=" * 70)
    print("THEME ANNOTATION VALIDATION REPORT")
    print("=" * 70)
    print(f"Manifest File:               {annotation_path.name}")
    print(f"Annotation Schema Version:   {annotation_set.annotation_schema_version}")
    print(f"Corpus Manifest Hash:        {expected_manifest_hash}")
    print(f"Annotation Set Semantic Hash:{annotation_set.compute_set_hash()}")
    print(f"Total Annotations:           {len(annotation_set.annotations)}")
    print("-" * 70)

    try:
        validated = validate_theme_annotation_set(annotation_set, {}, expected_manifest_hash)
        print(f"Validation SUCCESS: {len(validated)} annotations verified cleanly.")
    except Exception as e:
        print(f"Validation FAILED: {e}", file=sys.stderr)
        return 1

    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
