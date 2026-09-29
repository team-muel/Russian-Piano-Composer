"""Deterministic Source Materializer for PF-001B Physical Classical Corpus.

Reproduces the required physical score hierarchy from immutable remote source identities
and exact revisions bound in data/reviews/pf001/pf001_physical_corpus_inventory.json.

Requirements:
1. For every external source family, retrieve the exact immutable revision bound in the inventory.
2. Materialize only the required score artifacts into their authorized relative paths.
3. Verify file path, exact bytes, and SHA-256 hash against declared values.
4. Fail closed on any mismatch or retrieval error.
5. Never silently substitute another edition, repository, revision, or encoding.
6. Support caching while guaranteeing hash verification.
7. Strictly firewall external-test composers (Taneyev, Bortkiewicz, Blumenfeld, Catoire).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

FIREWALLED_EXTERNAL_COMPOSERS = {
    "CMP-TANEYEV",
    "CMP-BORTKIEWICZ",
    "CMP-BLUMENFELD",
    "CMP-CATOIRE",
}

# Authoritative remote source repositories and raw base URLs
SOURCE_BASE_URLS = {
    "https://github.com/DCMLab/tchaikovsky_seasons": (
        "https://raw.githubusercontent.com/DCMLab/tchaikovsky_seasons"
    ),
    "https://github.com/DCMLab/rachmaninoff_piano": (
        "https://raw.githubusercontent.com/DCMLab/rachmaninoff_piano"
    ),
    "https://github.com/DCMLab/medtner_tales": (
        "https://raw.githubusercontent.com/DCMLab/medtner_tales"
    ),
}


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def materialize_score(
    score_entry: dict[str, Any],
    repo_root: Path,
    cache_dir: Path | None = None,
) -> tuple[bool, str]:
    """Materializes a single score from its immutable source identity and validates its SHA-256."""
    wid = score_entry.get("work_id", "UNKNOWN")
    cid = score_entry.get("composer_id", "")
    if cid in FIREWALLED_EXTERNAL_COMPOSERS:
        return False, f"Score '{wid}' belongs to firewalled composer '{cid}'. Refusing to materialize."

    rel_path_str = score_entry.get("physical_file_path")
    if not rel_path_str:
        return False, f"Score '{wid}' lacks physical_file_path."

    target_path = repo_root / rel_path_str
    expected_sha = score_entry.get("source_sha256")
    if not expected_sha:
        return False, f"Score '{wid}' lacks source_sha256."

    # If the file already exists on disk and matches hash, we are good
    if target_path.exists():
        existing_bytes = target_path.read_bytes()
        if compute_sha256(existing_bytes) == expected_sha:
            return True, f"Score '{wid}' already present and verified at {rel_path_str}."

    # Check cache if available
    cache_file: Path | None = None
    if cache_dir is not None:
        cache_file = cache_dir / expected_sha
        if cache_file.exists():
            cached_bytes = cache_file.read_bytes()
            if compute_sha256(cached_bytes) == expected_sha:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(cached_bytes)
                return True, f"Score '{wid}' materialized from cache for {rel_path_str}."

    # External materialization via immutable URL
    repo_url = score_entry.get("source_repository")
    commit = score_entry.get("source_revision_or_commit")

    # If tracked inside repository (e.g. RC-013 canonical MusicXML), must already exist
    if "team-muel/Russian-Piano-Composer" in str(repo_url):
        return False, f"Tracked canonical score '{wid}' missing from repository tree: {rel_path_str}"

    if repo_url not in SOURCE_BASE_URLS:
        return False, f"No remote source provider registered for repository: {repo_url}"

    base_raw_url = SOURCE_BASE_URLS[repo_url]
    # In DCML repos, physical_file_path is data/raw/.../repository/MS3/<filename>
    # The remote relative path in DCML is MS3/<filename>
    filename = Path(rel_path_str).name
    download_url = f"{base_raw_url}/{commit}/MS3/{filename}"

    req = urllib.request.Request(
        download_url,
        headers={"User-Agent": "Russian-Piano-Composer-PF001B-Materializer/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            downloaded_bytes = resp.read()
    except urllib.error.HTTPError as e:
        return False, f"HTTP error {e.code} fetching {download_url} for '{wid}'."
    except Exception as e:
        return False, f"Network error fetching {download_url} for '{wid}': {e}"

    # Verify upstream raw hash if declared
    expected_upstream_sha = score_entry.get("upstream_raw_sha256")
    actual_upstream_sha = compute_sha256(downloaded_bytes)
    if expected_upstream_sha and actual_upstream_sha != expected_upstream_sha:
        return False, (
            f"Upstream raw SHA-256 mismatch for '{wid}' from {download_url}! "
            f"Expected {expected_upstream_sha}, got {actual_upstream_sha}."
        )

    # Apply declared canonicalization policy
    policy = score_entry.get("canonicalization_policy", "IDENTITY")
    if policy == "IDENTITY":
        candidate_bytes = downloaded_bytes
    elif policy == "LF_TO_CRLF":
        candidate_bytes = downloaded_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    elif policy == "CRLF_TO_LF":
        candidate_bytes = downloaded_bytes.replace(b"\r\n", b"\n")
    else:
        return False, f"Unknown canonicalization policy '{policy}' for score '{wid}'."

    # Verify canonical materialized hash
    actual_materialized_sha = compute_sha256(candidate_bytes)
    if actual_materialized_sha != expected_sha:
        return False, (
            f"Canonical materialized SHA-256 mismatch for '{wid}' after policy {policy}! "
            f"Expected {expected_sha}, got {actual_materialized_sha}."
        )

    # Write target file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(candidate_bytes)

    # Update cache
    if cache_file is not None:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file.write_bytes(candidate_bytes)
        except Exception:
            pass


    return True, f"Successfully materialized '{wid}' -> {rel_path_str}"


def materialize_all_scores(
    inventory_path: Path,
    repo_root: Path,
    cache_dir: Path | None = None,
) -> tuple[bool, str, list[str]]:
    """Materializes all verified scores in the inventory."""
    if not inventory_path.exists():
        return (
            False,
            "PF001B_SOURCE_MATERIALIZATION_FAILED",
            [f"Inventory not found: {inventory_path}"],
        )

    with open(inventory_path, encoding="utf-8") as f:
        data = json.load(f)

    scores = data.get("scores", [])
    if not scores:
        return (
            False,
            "PF001B_SOURCE_MATERIALIZATION_FAILED",
            ["No scores found in inventory."],
        )

    errors: list[str] = []
    success_count = 0

    for score in scores:
        ok, msg = materialize_score(score, repo_root, cache_dir)
        if not ok:
            errors.append(msg)
        else:
            success_count += 1

    if errors:
        return False, "PF001B_SOURCE_MATERIALIZATION_FAILED", errors

    return (
        True,
        "PF001B_SOURCE_MATERIALIZATION_SUCCESS",
        [f"Materialized and verified {success_count} / {len(scores)} scores."],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic Source Materializer for PF-001B Physical Classical Corpus."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root directory.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("data/reviews/pf001/pf001_physical_corpus_inventory.json"),
        help="Path to physical corpus inventory JSON.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Optional local cache directory.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    inv_path = (repo_root / args.inventory) if not args.inventory.is_absolute() else args.inventory
    cache_dir = (
        (repo_root / args.cache_dir)
        if args.cache_dir and not args.cache_dir.is_absolute()
        else args.cache_dir
    )

    print("=" * 70)
    print("PF-001B DETERMINISTIC SOURCE MATERIALIZATION")
    print("=" * 70)
    print(f"Repository Root: {repo_root}")
    print(f"Inventory Path:  {inv_path}")

    ok, token, logs = materialize_all_scores(inv_path, repo_root, cache_dir)

    for line in logs:
        if ok:
            print(f"  [OK] {line}")
        else:
            print(f"  [ERROR] {line}")

    print("=" * 70)
    print(f"Outcome Token: {token}")
    print("=" * 70)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
