"""
Discover Candidate Thematic Units (CTUs) across all ingested canonical corpus scores.
"""

import json
from pathlib import Path

from scripts.build_theme_pilot import load_canonical_score_from_parquet

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy


def main() -> None:
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        return

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        print(f"Error: Canonical corpus parquet directory not found at {interim_base}")
        return

    policy = CTUDiscoveryPolicy()
    out_dir = Path("data/interim/ctu")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Discovering CTUs across Corpus (Manifest Hash: {manifest_hash[:16]}...) ---")

    discovery_results = []
    total_raw_candidates = 0
    total_post_dedup_candidates = 0
    total_retained_ctus = 0
    eligible_count = 0
    ineligible_count = 0

    expected_piece_count = sum(len(s.score_entry_ids) for s in manifest.sources)
    if expected_piece_count != 141:
        raise RuntimeError(f"Corpus manifest error: Expected 141 total score entries, got {expected_piece_count}")

    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        if not corpus_dir.exists():
            raise FileNotFoundError(f"Corpus directory not found for {source.corpus_id}: {corpus_dir}")

        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            disc_res = discover_ctus_for_score(score, manifest_hash=manifest_hash, policy=policy)
            discovery_results.append(disc_res)

            if disc_res.is_eligible:
                eligible_count += 1
                total_raw_candidates += disc_res.raw_candidate_count
                total_post_dedup_candidates += disc_res.post_dedup_candidate_count
                total_retained_ctus += len(disc_res.retained_ctus)
            else:
                ineligible_count += 1

    if len(discovery_results) != 141:
        raise RuntimeError(f"FAIL CLOSED: Scanned {len(discovery_results)} pieces, expected exactly 141")

    summary = {
        "manifest_hash": manifest_hash,
        "discovery_policy_hash": policy.compute_policy_hash(),
        "total_pieces_scanned": len(discovery_results),
        "eligible_pieces": eligible_count,
        "ineligible_pieces": ineligible_count,
        "raw_candidate_count": total_raw_candidates,
        "post_dedup_candidate_count": total_post_dedup_candidates,
        "retained_ctu_count": total_retained_ctus,
        "matched_control_count": total_retained_ctus,
    }

    with open(out_dir / "discovery_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Scanned Pieces:           {len(discovery_results)}")
    print(f"Eligible Pieces:          {eligible_count}")
    print(f"Ineligible Pieces:        {ineligible_count}")
    print(f"Raw Candidates:           {total_raw_candidates}")
    print(f"Post-NMS Candidates:      {total_post_dedup_candidates}")
    print(f"Retained CTUs:            {total_retained_ctus}")
    print(f"Matched Controls:         {total_retained_ctus}")
    print(f"Saved summary to {out_dir / 'discovery_summary.json'}")


if __name__ == "__main__":
    main()
