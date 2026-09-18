"""
Validate discovered CTUs against held-out future validation regions using matched negative controls.
"""

import json
from pathlib import Path

from scripts.build_theme_pilot import load_canonical_score_from_parquet

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse


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

    disc_policy = CTUDiscoveryPolicy()
    val_policy = CTUValidationPolicy()

    out_dir = Path("data/interim/ctu")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Running Held-Out Future-Reuse Validation (Manifest Hash: {manifest_hash[:16]}...) ---")

    scores_by_id = {}
    discovery_results = []

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
            scores_by_id[piece_id] = score
            disc_res = discover_ctus_for_score(score, manifest_hash=manifest_hash, policy=disc_policy)
            discovery_results.append(disc_res)

    if len(discovery_results) != 141:
        raise RuntimeError(f"FAIL CLOSED: Processed {len(discovery_results)} pieces, expected exactly 141")

    val_result = validate_ctu_future_reuse(
        scores_by_id=scores_by_id,
        discovery_results=tuple(discovery_results),
        manifest_hash=manifest_hash,
        disc_policy=disc_policy,
        val_policy=val_policy,
    )

    report_data = {
        "manifest_hash": val_result.manifest_hash,
        "discovery_policy_hash": val_result.discovery_policy_hash,
        "validation_policy_hash": val_result.validation_policy_hash,
        "candidate_set_hash": val_result.candidate_set_hash,
        "validation_result_hash": val_result.compute_validation_result_hash(),
        "total_pieces": val_result.total_pieces,
        "eligible_pieces": val_result.eligible_pieces,
        "ineligible_pieces": val_result.ineligible_pieces,
        "mean_ctu_future_score": val_result.mean_ctu_future_score,
        "mean_control_future_score": val_result.mean_control_future_score,
        "mean_difference": val_result.mean_difference,
        "cohens_d": val_result.cohens_d,
        "bootstrap_ci_95": [val_result.bootstrap_ci_lower, val_result.bootstrap_ci_upper],
        "permutation_p_value": val_result.permutation_p_value,
        "positive_effect_fraction": val_result.positive_effect_fraction,
        "empirical_status": val_result.empirical_status.value,
    }

    with open(out_dir / "validation_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print("\n--- HELD-OUT VALIDATION RESULTS ---")
    print(f"Total Pieces:                 {val_result.total_pieces}")
    print(f"Eligible Pieces (>=12 m):     {val_result.eligible_pieces}")
    print(f"Ineligible Pieces (<12 m):   {val_result.ineligible_pieces}")
    print(f"Mean CTU Future Reuse:        {val_result.mean_ctu_future_score:.4f}")
    print(f"Mean Control Future Reuse:    {val_result.mean_control_future_score:.4f}")
    print(f"Mean Paired Difference:       {val_result.mean_difference:.4f}")
    print(f"Effect Size (Cohen's d):      {val_result.cohens_d:.4f}")
    print(f"95% Bootstrap CI:             [{val_result.bootstrap_ci_lower:.4f}, {val_result.bootstrap_ci_upper:.4f}]")
    print(f"Permutation p-value:          {val_result.permutation_p_value:.4f}")
    print(f"Positive Effect Fraction:     {val_result.positive_effect_fraction:.4f}")
    print(f"EMPIRICAL CTU STATUS:         {val_result.empirical_status.value}")
    print(f"\nSaved validation report to {out_dir / 'validation_results.json'}")


if __name__ == "__main__":
    main()
