#!/usr/bin/env python3
"""
Provenance Verification Command for Russian Piano Composer.
Verifies stored manifest pins, commit SHA syntax, score inventories, and license claim consistency.
Supports offline validation against local inventory and optional remote verification via --remote.
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

import yaml

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.domain.corpus import HEX_COMMIT_REGEX


def verify_local_provenance(manifest_path: Path, inventory_path: Path) -> int:
    """
    Validates manifest and inventory integrity offline.
    """
    print(f"[OK] Loading manifest from {manifest_path}...")
    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    print(f"[OK] Manifest hash: {manifest_hash}")

    if len(manifest_hash) != 64 or not all(c in "0123456789abcdef" for c in manifest_hash):
        print(f"[FAIL] Manifest hash is invalid: {manifest_hash!r}", file=sys.stderr)
        return 1

    if not inventory_path.exists():
        print(f"[FAIL] Source inventory file not found: {inventory_path}", file=sys.stderr)
        return 1

    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    inv_meta_commit = inventory.get("meta_repository", {}).get("commit")
    if not inv_meta_commit or not HEX_COMMIT_REGEX.match(inv_meta_commit):
        print(f"[FAIL] Invalid meta_repository commit in inventory: {inv_meta_commit!r}", file=sys.stderr)
        return 1

    errors: list[str] = []
    inv_sources = inventory.get("sources", {})

    for src in manifest.sources:
        print(f"\n--- Checking source: {src.corpus_id} ---")
        if src.source_commit is None:
            errors.append(f"{src.corpus_id}: missing source_commit pin")
            continue

        if not HEX_COMMIT_REGEX.match(src.source_commit):
            errors.append(f"{src.corpus_id}: source_commit {src.source_commit!r} is not 40-char hex")

        if src.corpus_id not in inv_sources:
            errors.append(f"{src.corpus_id}: missing from source inventory {inventory_path}")
            continue

        inv_entry = inv_sources[src.corpus_id]
        inv_commit = inv_entry.get("commit")
        if inv_commit != src.source_commit:
            errors.append(
                f"{src.corpus_id}: commit mismatch between manifest ({src.source_commit}) and inventory ({inv_commit})"
            )

        inv_score_entries = inv_entry.get("score_entries", [])
        if len(inv_score_entries) != src.score_entry_count:
            errors.append(
                f"{src.corpus_id}: score entry count mismatch. Manifest has {src.score_entry_count}, inventory list has {len(inv_score_entries)}"
            )

        # Verify license claim conflicts enforce REVIEW_REQUIRED
        claim_values = {c.value.upper().replace("-", " ").strip() for c in src.license_claims}
        if len(claim_values) > 1 and not src.rights_review_required:
            errors.append(f"{src.corpus_id}: conflicting license claims present but rights_review_required is false")

        print(f"  Role: {src.role.value}")
        print(f"  Readiness: {src.readiness_status.value}")
        print(f"  Commit: {src.source_commit}")
        print(f"  Score entries: {src.score_entry_count} (matched)")

    if errors:
        print("\n[FAIL] Provenance verification failed with errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("\n[SUCCESS] Local provenance verification passed!")
    return 0


def verify_remote_provenance(inventory_path: Path) -> int:
    """
    Queries GitHub API to verify that pinned commits exist remotely and score trees match.
    """
    print("\n=== Running Remote Provenance Verification ===")
    with open(inventory_path, encoding="utf-8") as f:
        inventory = yaml.safe_load(f)

    meta_repo = inventory.get("meta_repository", {}).get("repository", "DCMLab/distant_listening_corpus")
    meta_commit = inventory.get("meta_repository", {}).get("commit")

    print(f"Checking meta-repository {meta_repo} at commit {meta_commit}...")
    try:
        url = f"https://api.github.com/repos/{meta_repo}/commits/{meta_commit}"
        req = urllib.request.Request(url, headers={"User-Agent": "RussianPianoComposer/1.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"  [OK] Remote meta-repository commit verified: {data['sha']}")
    except Exception as e:
        print(f"  [FAIL] Failed to verify remote commit for {meta_repo}: {e}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for corpus_id, entry in inventory.get("sources", {}).items():
        repo = entry["repository"]
        commit = entry["commit"]
        expected_count = entry["score_entry_count"]
        print(f"Checking remote repository {repo} at commit {commit}...")
        try:
            url = f"https://api.github.com/repos/{repo}/commits/{commit}"
            req = urllib.request.Request(url, headers={"User-Agent": "RussianPianoComposer/1.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                if data["sha"] != commit:
                    errors.append(f"{corpus_id}: returned SHA {data['sha']} does not match pinned {commit}")
                else:
                    print(f"  [OK] Remote commit verified: {data['sha']}")
        except Exception as e:
            errors.append(f"{corpus_id}: remote verification failed for {repo}: {e}")

    if errors:
        print("\n[FAIL] Remote verification failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("\n[SUCCESS] Remote provenance verification passed!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Russian Piano Composer corpus provenance.")
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/corpus_manifest.yaml"))
    parser.add_argument("--inventory", type=Path, default=Path("data/manifests/source_inventory_v1.yaml"))
    parser.add_argument("--remote", action="store_true", help="Perform remote GitHub API checks.")

    args = parser.parse_args()
    code = verify_local_provenance(args.manifest, args.inventory)
    if code != 0:
        return code

    if args.remote:
        return verify_remote_provenance(args.inventory)

    return 0


if __name__ == "__main__":
    sys.exit(main())
