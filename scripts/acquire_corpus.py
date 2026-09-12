#!/usr/bin/env python3
"""
CLI entry point for verified raw corpus acquisition.
Usage:
    python scripts/acquire_corpus.py --corpus dcml_medtner_tales
    python scripts/acquire_corpus.py --all
    python scripts/acquire_corpus.py --verify-only
"""

import argparse
from pathlib import Path
import sys

from russian_piano_composer.corpus.acquisition import (
    EXPECTED_MANIFEST_HASH,
    acquire_corpus_source,
    acquire_all_corpora,
)
from russian_piano_composer.corpus.manifest import load_manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verified Corpus Acquisition for Russian Piano Composer."
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
        "--corpus",
        type=str,
        help="Specific corpus_id to acquire/verify",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Acquire/verify all registered corpora in manifest",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify existing local raw acquisition without performing git clones",
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

    print("\n=== Acquisition Plan ===")
    for src in sources_to_process:
        print(f"Corpus: {src.corpus_id}")
        print(f"  Repository: {src.source_repository}")
        print(f"  Pinned Commit: {src.source_commit}")
        print(f"  Destination: {args.raw_dir / src.corpus_id / (src.source_commit or '')}")
    print("========================\n")

    results = []
    for src in sources_to_process:
        res = acquire_corpus_source(
            source=src,
            manifest_hash=manifest_hash,
            raw_base_dir=args.raw_dir,
            verify_only=args.verify_only,
        )
        results.append(res)

    print("\n=== Acquisition Summary Report ===")
    failures = 0
    for res in results:
        status_str = f"[{res.status}]"
        print(f"{res.corpus_id:30s} {status_str:25s} {res.message}")
        if res.status == "FAILED":
            failures += 1

    if failures > 0:
        print(f"\n[FAIL] {failures} corpus acquisition(s) failed integrity check.", file=sys.stderr)
        return 1

    print("\n[SUCCESS] All targeted corpus acquisitions verified successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
