"""Executable Non-Vendored External Corpus Materialization and Verification Pipeline for RC-014.

Demonstrates reproducible, on-demand materialization of pinned external score files:
1. Reads canonical external access policy manifest.
2. Creates an isolated temporary scratch workspace.
3. Retrieves declared external files directly from immutable Git repository commit/tree using Git plumbing (git cat-file blob).
4. Verifies Git blob SHAs and canonical Git blob SHA-256 byte checksums.
5. Materializes parser inputs directly from immutable blob bytes into scratch.
6. Fails closed on any hash mismatch, path alteration, or upstream drift.
7. Evaluates RC-011 56-descriptor structural representation in-memory/in-scratch.
8. Automatically purges raw external files upon completion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.audit_tonal_piano_corpus_rc014a import parse_xml_to_canonical

from russian_piano_composer.structure_analysis.extractor import (
    PieceStructuralRepresentation,
    extract_structural_representation,
)


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def materialize_and_verify_corpus(
    manifest_path: str = "data/manifests/rc014b_external_access_policy.json",
    scratch_parent: str | None = None,
    keep_scratch: bool = False,
) -> dict[str, Any]:
    """Execute complete isolated materialization and verification round."""
    with open(manifest_path, encoding="utf-8") as f:
        policy = json.load(f)

    repo_url = policy["corpus_repository"]
    frozen_commit = policy["corpus_frozen_commit"]
    expected_tree = policy["corpus_root_tree"]
    declared_entries = policy["reference_manifest"]

    temp_dir = tempfile.mkdtemp(prefix="rc014_materialize_", dir=scratch_parent)
    results: list[dict[str, Any]] = []

    try:
        # 1. Clone repository (bare or shallow) in isolated workspace
        target_clone_dir = os.path.join(temp_dir, "repo")
        clone_cmd = ["git", "clone", "--no-checkout", f"https://github.com/{repo_url}.git", target_clone_dir]
        sub_clone = subprocess.run(clone_cmd, capture_output=True, text=True, check=False)
        if sub_clone.returncode != 0:
            raise RuntimeError(f"Failed to clone external repo {repo_url}: {sub_clone.stderr}")

        # Checkout pinned commit
        co_cmd = ["git", "checkout", frozen_commit]
        sub_co = subprocess.run(co_cmd, cwd=target_clone_dir, capture_output=True, text=True, check=False)
        if sub_co.returncode != 0:
            raise RuntimeError(f"Failed to checkout pinned commit {frozen_commit}: {sub_co.stderr}")

        # Verify root tree SHA
        tree_cmd = ["git", "log", "-1", "--format=%T"]
        actual_tree = subprocess.run(tree_cmd, cwd=target_clone_dir, capture_output=True, text=True, check=False).stdout.strip()
        if actual_tree != expected_tree:
            raise ValueError(f"Root tree SHA mismatch: expected {expected_tree}, got {actual_tree}")

        scratch_scores_dir = os.path.join(temp_dir, "scores")
        os.makedirs(scratch_scores_dir, exist_ok=True)

        # 2. Iterate through declared files, extract via git cat-file blob plumbing
        for entry in declared_entries:
            rel_path = entry["relative_path"]
            exp_blob = entry["git_blob_sha"]
            exp_sha256 = entry["sha256"]

            # Verify git blob SHA in tree
            ls_cmd = ["git", "ls-tree", "HEAD", rel_path]
            ls_out = subprocess.run(ls_cmd, cwd=target_clone_dir, capture_output=True, text=True, check=False).stdout.strip()
            if not ls_out:
                raise ValueError(f"Git tree lookup failed for {rel_path}")
            act_blob = ls_out.split()[2]
            if act_blob != exp_blob:
                raise ValueError(f"Git blob SHA mismatch for {rel_path}: expected {exp_blob}, got {act_blob}")

            # Extract exact immutable Git blob bytes
            cat_cmd = ["git", "cat-file", "blob", exp_blob]
            blob_bytes = subprocess.run(cat_cmd, cwd=target_clone_dir, capture_output=True, check=False).stdout
            act_sha256 = compute_sha256(blob_bytes)
            if act_sha256 != exp_sha256:
                raise ValueError(f"Canonical blob SHA-256 checksum mismatch for {rel_path}: expected {exp_sha256}, got {act_sha256}")

            # Materialize directly into scratch file for parser
            score_filename = os.path.basename(rel_path)
            scratch_file_path = os.path.join(scratch_scores_dir, score_filename)
            with open(scratch_file_path, "wb") as sf:
                sf.write(blob_bytes)

            # 3. Test in-memory / in-scratch RC-011 56-descriptor feature extraction
            score_id = os.path.splitext(score_filename)[0].replace(" ", "_").lower()
            piece_id = f"tonal_piano_corpus:{score_id}"
            canonical_score = parse_xml_to_canonical(
                xml_path=scratch_file_path,
                piece_id=piece_id,
                composer=entry["composer"],
                title=entry["work_title"],
            )
            rep: PieceStructuralRepresentation = extract_structural_representation(canonical_score, manifest_hash="rc014_materialize")
            feature_count = len(rep.features)
            if feature_count != 56:
                raise ValueError(f"Extracted {feature_count} features for {rel_path}, expected 56")

            results.append({
                "work": entry["work_title"],
                "composer": entry["composer"],
                "relative_path": rel_path,
                "git_blob_sha": act_blob,
                "sha256": act_sha256,
                "rc011_features_count": feature_count,
                "measures_count": len(canonical_score.measures),
                "events_count": len(canonical_score.events),
                "status": "VERIFIED",
            })

        return {
            "status": "ALL_ENTRIES_VERIFIED",
            "materialized_scores_count": len(results),
            "root_tree_verified": actual_tree,
            "commit_verified": frozen_commit,
            "entries": results,
        }
    finally:
        if not keep_scratch and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RC-014 Non-Vendored Corpus Materializer")
    parser.add_argument("--manifest", default="data/manifests/rc014b_external_access_policy.json")
    parser.add_argument("--keep-scratch", action="store_true")
    args = parser.parse_args()

    print(f"Executing non-vendored materialization and verification from {args.manifest}...")
    res = materialize_and_verify_corpus(manifest_path=args.manifest, keep_scratch=args.keep_scratch)
    print(f"Materialization Result: {res['status']} ({res['materialized_scores_count']} scores verified with 56 descriptors)")
