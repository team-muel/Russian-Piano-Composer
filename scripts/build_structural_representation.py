"""
Script to build the full 56-feature Structural Representation Matrix across 141 canonical scores.
"""

import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import compute_candidate_set_hash
from russian_piano_composer.structure_analysis.extractor import (
    StructuralExtractionPolicy,
    extract_structural_representation,
)
from russian_piano_composer.structure_analysis.lineage import (
    compute_structural_representation_lineage,
    verify_prior_milestone_hashes_fail_closed,
)
from russian_piano_composer.structure_analysis.matrix import (
    build_structural_representation_matrix,
)
from russian_piano_composer.structure_analysis.schema import (
    AvailabilityStatus,
)
from russian_piano_composer.structure_analysis.validation import (
    run_synthetic_and_metamorphic_validation,
)

if TYPE_CHECKING:
    from russian_piano_composer.domain.score import CanonicalScore


def main() -> None:
    print("==========================================================================")
    print(" RUSSIAN PIANO COMPOSER -- RC-011 STRUCTURAL MUSIC REPRESENTATION")
    print("==========================================================================")

    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    print(f"Loaded Manifest Hash: {manifest_hash}")

    interim_base = Path("data/interim/canonical") / manifest_hash
    if not interim_base.exists():
        print(f"Error: Parquet directory not found at {interim_base}")
        sys.exit(1)

    # 1. Load 141 Canonical Scores
    print("\n--- Loading 141 Canonical Scores ---")
    scores_by_id: dict[str, CanonicalScore] = {}
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score

    n_scores = len(scores_by_id)
    print(f"Loaded {n_scores} canonical scores.")
    if n_scores != 141:
        raise RuntimeError(f"Expected 141 canonical scores, found {n_scores}.")

    policy = StructuralExtractionPolicy()

    # 2. Dynamic RC-009B Discovery Candidate Set Generation & Fail-Closed Lineage Verification
    print("\n--- Verifying Prior Milestone Hashes & RC-009B Discovery Candidate Set ---")
    t0_disc = time.time()
    discovery_results = []
    for _pid, score in sorted(scores_by_id.items()):
        disc_res = discover_ctus_for_score(
            score, manifest_hash=manifest_hash, policy=policy.ctu_discovery_policy
        )
        discovery_results.append(disc_res)

    dyn_candidate_set_hash = compute_candidate_set_hash(discovery_results)
    print(f"  Dynamic RC-009B Candidate Set Hash: {dyn_candidate_set_hash} ({time.time() - t0_disc:.1f}s)")

    verify_prior_milestone_hashes_fail_closed(
        manifest_hash=manifest_hash,
        dynamically_computed_candidate_set_hash=dyn_candidate_set_hash,
    )
    print("  Prior milestone fail-closed checks: PASS")

    # 3. Extract 56 Structural Features across 141 Scores
    print("\n--- Extracting 56 Structural Features across 141 Pieces ---")
    t0 = time.time()
    piece_representations = {}

    for idx, (disc_res, (pid, score)) in enumerate(zip(discovery_results, sorted(scores_by_id.items()), strict=True), start=1):
        if idx == 1 or idx % 10 == 0 or idx == n_scores:
            print(f"  Progress: {idx}/{n_scores} pieces processed... ({time.time() - t0:.1f}s elapsed)")
            sys.stdout.flush()
        rep = extract_structural_representation(
            score,
            manifest_hash=manifest_hash,
            policy=policy,
            retained_ctus=disc_res.retained_ctus,
        )
        piece_representations[pid] = rep.features

    elapsed = time.time() - t0
    print(f"Extraction completed in {elapsed:.1f}s.")

    # 4. Build Role-Blind Matrix & Coverage Accounting
    matrix = build_structural_representation_matrix(piece_representations, manifest_hash=manifest_hash)

    avail_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.AVAILABLE)
    sz_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.STRUCTURAL_ZERO)
    unavail_cnt = sum(1 for row in matrix.availability_matrix for st in row if st == AvailabilityStatus.UNAVAILABLE)
    tot_cells = len(matrix.piece_ids) * len(matrix.feature_names)

    print("\n--- Corpus Coverage Accounting ---")
    print(f"  Total Matrix Cells: {tot_cells}")
    print(f"  AVAILABLE:          {avail_cnt} ({avail_cnt / tot_cells * 100:.2f}%)")
    print(f"  STRUCTURAL_ZERO:    {sz_cnt} ({sz_cnt / tot_cells * 100:.2f}%)")
    print(f"  UNAVAILABLE:        {unavail_cnt} ({unavail_cnt / tot_cells * 100:.2f}%)")

    # 5. Run Synthetic Fixture Suite & Metamorphic Invariance Validation
    print("\n--- Running Synthetic Fixture Suite & Metamorphic Invariance ---")
    exclusion_ledger_path = Path("docs/research/RC011_EXCLUSION_LEDGER.md")
    import hashlib
    excl_hash = hashlib.sha256(exclusion_ledger_path.read_bytes()).hexdigest() if exclusion_ledger_path.exists() else "0" * 64

    val_result = run_synthetic_and_metamorphic_validation(
        available_cells=avail_cnt,
        structural_zero_cells=sz_cnt,
        unavailable_cells=unavail_cnt,
        exclusion_ledger_hash=excl_hash,
    )
    print(f"  Fixture Count:      {val_result.fixture_count}")
    print(f"  Assertions Passed:  {sum(1 for a in val_result.assertion_records if a.passed)} / {len(val_result.assertion_records)}")
    print(f"  Metamorphic Passed: {sum(1 for m in val_result.metamorphic_records if m.passed)} / {len(val_result.metamorphic_records)}")
    for fs in val_result.family_statuses:
        print(f"    - Family {fs.family.value:20s}: {fs.status} ({fs.passed_assertions}/{fs.total_assertions} assertions, {fs.passed_metamorphic}/{fs.total_metamorphic} metamorphic)")
    print(f"  Overall Status:     {val_result.overall_status}")

    # 6. Compute Lineage
    lineage = compute_structural_representation_lineage(
        manifest_hash=manifest_hash,
        matrix=matrix,
        val_result=val_result,
        exclusion_ledger_hash=excl_hash,
        policy=policy,
        dynamically_computed_candidate_set_hash=dyn_candidate_set_hash,
    )
    bundle_hash = lineage.compute_bundle_hash()

    print("\n--- RC-011 Final Lineage Registry ---")
    print(f"  Master Baseline SHA:                    {lineage.master_baseline_sha}")
    print(f"  Preregistration Commit SHA:             {lineage.preregistration_commit_sha}")
    print(f"  Preregistration Amendment SHA:          {lineage.preregistration_amendment_commit_sha}")
    print(f"  Canonical Manifest Hash:                {lineage.manifest_hash}")
    print(f"  RC-009A Feature Schema Hash:            {lineage.rc009a_feature_schema_semantic_hash}")
    print(f"  RC-009A Feature Policy Hash:            {lineage.rc009a_feature_policy_hash}")
    print(f"  RC-009B Discovery Policy Hash:          {lineage.rc009b_discovery_policy_hash}")
    print(f"  RC-009B Candidate Set Hash:             {lineage.rc009b_candidate_set_hash}")
    print(f"  RC-009B CTU Schema Hash:                {lineage.ctu_schema_semantic_hash}")
    print(f"  RC-009B Representation Semantics Hash:  {lineage.representation_semantic_hash}")
    print(f"  RC-009B Similarity Semantics Hash:      {lineage.similarity_semantic_hash}")
    print(f"  Structural Schema Hash:                 {lineage.structural_schema_hash}")
    print(f"  Tonal Policy Hash:                      {lineage.tonal_policy_hash}")
    print(f"  Sonority Policy Hash:                   {lineage.sonority_policy_hash}")
    print(f"  Cadence Policy Hash:                    {lineage.cadence_policy_hash}")
    print(f"  Form Policy Hash:                       {lineage.form_policy_hash}")
    print(f"  Voice-Leading Policy Hash:              {lineage.vl_policy_hash}")
    print(f"  Texture Policy Hash:                    {lineage.texture_policy_hash}")
    print(f"  Trajectory Policy Hash:                 {lineage.trajectory_policy_hash}")
    print(f"  Synthetic Fixture Suite Hash:           {lineage.synthetic_fixture_suite_hash}")
    print(f"  Assertion Contract Hash:                {lineage.assertion_contract_hash}")
    print(f"  Invariance Contract Hash:               {lineage.invariance_contract_hash}")
    print(f"  Preregistration Amendment Hash:         {lineage.preregistration_amendment_hash}")
    print(f"  Exclusion Ledger Hash:                  {lineage.exclusion_ledger_hash}")
    print(f"  Full Corpus Structural Matrix Hash:     {lineage.structural_matrix_hash}")
    print(f"  Validation Result Hash:                 {lineage.validation_result_hash}")
    print(f"  Lineage Bundle Hash:                    {bundle_hash}")

    print("\n==========================================================================")
    print(f" STRUCTURAL REPRESENTATION STATUS = {val_result.overall_status}")
    print("==========================================================================")


if __name__ == "__main__":
    main()
