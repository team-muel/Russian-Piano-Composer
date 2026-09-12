#!/usr/bin/env python3
"""
CLI entry point for verified canonical symbolic score ingestion.
Usage:
    python scripts/ingest_corpus.py --corpus dcml_medtner_tales
    python scripts/ingest_corpus.py --all
"""

import argparse
import sys
from pathlib import Path

from russian_piano_composer.corpus.ingestion import (
    EXPECTED_MANIFEST_HASH,
    ingest_corpus,
)
from russian_piano_composer.corpus.manifest import load_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical Symbolic Score Ingestion for Russian Piano Composer."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/manifests/corpus_manifest.yaml"),
        help="Path to corpus manifest YAML",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("data/raw"),
        help="Path to raw storage directory",
    )
    parser.add_argument(
        "--interim-dir",
        type=Path,
        default=Path("data/interim/canonical"),
        help="Path to interim canonical output directory",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        help="Specific corpus_id to ingest",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ingest all registered corpora in manifest",
    )

    args = parser.parse_args()

    if not args.corpus and not args.all:
        print("Error: Must specify either --corpus <corpus_id> or --all", file=sys.stderr)
        return 1

    manifest = load_manifest(args.manifest)
    manifest_hash = manifest.compute_manifest_hash()
    print(f"[OK] Manifest loaded from {args.manifest}")
    print(f"[OK] Computed Manifest Hash: {manifest_hash}")

    if manifest_hash != EXPECTED_MANIFEST_HASH:
        print(
            f"[FAIL] Manifest hash mismatch! Expected {EXPECTED_MANIFEST_HASH}, got {manifest_hash}",
            file=sys.stderr,
        )
        return 1

    sources_to_process = []
    if args.all:
        sources_to_process = list(manifest.sources)
    elif args.corpus:
        match = [s for s in manifest.sources if s.corpus_id == args.corpus]
        if not match:
            print(f"[FAIL] Corpus ID '{args.corpus}' not found in manifest.", file=sys.stderr)
            return 1
        sources_to_process = match

    results = []
    for src in sources_to_process:
        res = ingest_corpus(
            source=src,
            manifest_hash=manifest_hash,
            raw_base_dir=args.raw_dir,
            interim_base_dir=args.interim_dir,
        )
        results.append(res)

    print("\n=== Ingestion Summary Report ===")
    failures = 0
    for res in results:
        status_str = f"[{res.status}]"
        print(f"{res.corpus_id:30s} {status_str:15s} {res.message}")
        if res.receipt:
            print(f"  Canonical Corpus Hash: {res.receipt.corpus_canonical_hash}")
        if res.status != "COMPLETE":
            failures += 1

    if failures > 0:
        print(f"\n[FAIL] {failures} corpus ingestion(s) incomplete or failed.", file=sys.stderr)
        return 1

    print("\n[SUCCESS] All targeted corpus symbolic ingestions completed cleanly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
