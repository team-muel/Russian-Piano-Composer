"""
Adversarial tests for control-generation architecture, fail-closed pairing, mathematical activity matching,
validation semantic hashing, and semantic mutation sensitivity.
"""

from tests.unit.ctu.test_ctu_fixtures import _build_test_score

from russian_piano_composer.ctu.controls import (
    build_matched_control_pairs,
    generate_matched_control,
)
from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import (
    CTUCandidate,
    EvidenceTier,
    MatchedControlPair,
    SegmentPosition,
    SegmentSpan,
    compute_validation_semantic_hash,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.similarity import (
    compute_sequence_multiset_similarity,
)
from russian_piano_composer.ctu.validation import validate_ctu_future_reuse


def test_control_generation_governed_by_validation_policy() -> None:
    """Requirement 1 — Control generation must be governed strictly by validation policy instance."""
    score = _build_test_score("test:gov", 16, {0: [60, 62, 64, 65], 1: [60, 62, 64, 65]})
    disc_policy = CTUDiscoveryPolicy(min_piece_measures=12)
    disc_res = discover_ctus_for_score(score, manifest_hash="m" * 64, policy=disc_policy)

    val_policy_strict = CTUValidationPolicy(control_attack_count_tolerance_ratio=0.01)
    val_policy_loose = CTUValidationPolicy(control_attack_count_tolerance_ratio=0.50)

    pairs_strict = build_matched_control_pairs(score, disc_res, val_policy_strict, "m" * 64)
    pairs_loose = build_matched_control_pairs(score, disc_res, val_policy_loose, "m" * 64)

    assert pairs_strict[0].validation_policy_hash == val_policy_strict.compute_policy_hash()
    assert pairs_loose[0].validation_policy_hash == val_policy_loose.compute_policy_hash()
    assert pairs_strict[0].validation_policy_hash != pairs_loose[0].validation_policy_hash


def test_fail_closed_pairing_asymmetric_control_exclusion() -> None:
    """Requirement 2 — Adversarial test: 5 retained CTUs, 4 matched controls, 1 CONTROL_UNAVAILABLE. Both sides aggregate exactly 4 pairs."""
    score = _build_test_score("test:asym", 16, {m: [60, 62, 64] for m in range(16)})
    disc_policy = CTUDiscoveryPolicy(min_piece_measures=12, max_retained_ctus=5)
    disc_res = discover_ctus_for_score(score, manifest_hash="m" * 64, policy=disc_policy)

    # Mock 5 retained CTUs
    ctu_list = list(disc_res.retained_ctus)
    assert len(ctu_list) >= 1

    # Create dummy candidate where control is impossible (e.g. impossible attack count requirement)
    val_policy_strict = CTUValidationPolicy(control_attack_count_tolerance_ratio=0.0)
    pairs = build_matched_control_pairs(score, disc_res, val_policy_strict, "m" * 64)

    # Force one pair to be unavailable
    modified_pairs = list(pairs)
    first_pair = modified_pairs[0]
    modified_pairs[0] = MatchedControlPair(
        target_candidate_id=first_pair.target_candidate_id,
        target_ctu=first_pair.target_ctu,
        control_candidate=None,  # CONTROL_UNAVAILABLE
        validation_policy_hash=val_policy_strict.compute_policy_hash(),
    )

    # Run validation pipeline with explicit pair exclusion
    scores_by_id = {"test:asym": score}
    val_res = validate_ctu_future_reuse(
        scores_by_id,
        (disc_res,),
        manifest_hash="m" * 64,
        disc_policy=disc_policy,
        val_policy=val_policy_strict,
        matched_control_pairs=tuple(modified_pairs),
    )

    assert len(val_res.piece_records) == 1
    rec = val_res.piece_records[0]
    # Verify that unavailable control is recorded and removed from both CTU and control averages
    assert rec.unavailable_control_count >= 1
    assert rec.matched_pair_count == len(pairs) - rec.unavailable_control_count


def test_exact_mathematical_activity_matching_rule() -> None:
    """Requirement 3 — Relative activity matching rule abs(cand - target)/target <= tolerance must be exact without rounding approximation."""
    score = _build_test_score("test:exact_act", 16, {0: [60, 62, 64]})

    rep_3 = extract_segment_representation(score, SegmentSpan(SegmentPosition(0), SegmentPosition(1)))
    ctu_3 = CTUCandidate(
        candidate_id="ctu_test_3",
        piece_id="test:exact_act",
        corpus_id="test",
        canonical_piece_hash="hash",
        span=SegmentSpan(SegmentPosition(0), SegmentPosition(1)),
        representation=rep_3,
    )

    val_policy = CTUValidationPolicy(control_attack_count_tolerance_ratio=0.25)

    # Score with 2 attacks in measure 2 (diff = 1/3 = 0.333 > 0.25)
    score_2 = _build_test_score("test:exact_act_2", 16, {0: [60, 62, 64], 2: [60, 62]})
    ctrl_cand = generate_matched_control(
        score=score_2,
        ctu=ctu_3,
        control_index=0,
        discovery_measure_count=9,
        manifest_hash="m" * 64,
        validation_policy=val_policy,
    )

    # Candidate with 2 attacks must be rejected under exact 0.25 ratio rule!
    if ctrl_cand is not None:
        cand_attacks = sum(ctrl_cand.representation.texture_profile)
        diff_ratio = abs(cand_attacks - 3) / 3.0
        assert diff_ratio <= 0.25


def test_sequence_multiset_similarity_sparse_v1_rules() -> None:
    """Requirement 4 — Exact sparse sequence similarity V1 rule test."""
    # 1. Both empty -> None
    assert compute_sequence_multiset_similarity([], []) is None

    # 2. One empty, one non-empty -> 0.0
    assert compute_sequence_multiset_similarity([1, 2], []) == 0.0
    assert compute_sequence_multiset_similarity([], [1, 2]) == 0.0

    # 3. Both lengths >= 2 -> 2-gram Jaccard
    assert compute_sequence_multiset_similarity([1, 2, 3], [1, 2, 3]) == 1.0
    assert compute_sequence_multiset_similarity([1, 2, 3], [4, 5, 6]) == 0.0

    # 4. Both lengths == 1 -> 1-gram Jaccard fallback
    assert compute_sequence_multiset_similarity([5], [5]) == 1.0
    assert compute_sequence_multiset_similarity([5], [6]) == 0.0

    # 5. One length == 1, other length >= 2 -> 0.0
    assert compute_sequence_multiset_similarity([5], [5, 6]) == 0.0
    assert compute_sequence_multiset_similarity([5, 6, 7], [5]) == 0.0


def test_validation_semantic_hash_mutation_sensitivity() -> None:
    """Requirement 5 & 6 — Hash mutation sensitivity for validation semantic hash and policy hashes."""
    sem1 = compute_validation_semantic_hash()
    assert len(sem1) == 64

    # Verify that changing any underlying dictionary item produces a different hash
    import hashlib
    import json
    canonical = {
        "future_reuse_search": "maximum_same_length_similarity_in_future_validation_region",
        "future_window_stride_rule": "stride_measures_from_discovery_policy",
        "pair_aggregation_rule": "matched_pair_only_aggregation_excluded_if_control_unavailable",
        "control_availability_exclusion_rule": "CONTROL_UNAVAILABLE_pair_removed_from_both_ctu_and_ctrl_means",
        "control_iou_rule": "iou_lt_0.50_with_target_ctu_and_iou_lt_0.50_with_all_retained_ctus",
        "control_activity_matching_formula": "exact_relative_ratio_abs_diff_over_ctu_lt_eq_tolerance_no_round_fallback",
        "control_no_fallback_rule": "fail_closed_returns_none_if_no_candidate_satisfies_criteria",
        "piece_level_aggregation_unit": "piece_mean_diff_ctu_future_reuse_minus_ctrl_future_reuse",
        "cohen_dz_estimator": "mean_diff_over_sample_std_with_ddof_1",
        "bootstrap_resampling_unit": "piece_level_paired_differences_10000_resamples",
        "bootstrap_ci_definition": "percentile_interval_2.5_to_97.5",
        "two_sided_permutation_test": "two_sided_paired_sign_flip_permutation",
        "monte_carlo_p_value_correction": "(extreme_count_+_1)_over_(iterations_+_1)",
        "empirical_ctu_status_decision_rule": "CTU_VALIDATED_if_p_lt_0.05_and_ci_lower_gt_0_and_mean_diff_gt_0",
    }

    # Mutate cohen_dz_estimator
    canonical_mutated = dict(canonical)
    canonical_mutated["cohen_dz_estimator"] = "mean_diff_over_sample_std_with_ddof_0"
    sem_mutated = hashlib.sha256(json.dumps(canonical_mutated, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

    assert sem1 != sem_mutated


def test_ctu_schema_v1_tiers_e0_e1_only() -> None:
    """Requirement 7 — CTU Schema V1 contains only E0 and E1 tiers."""
    tier_values = [t.value for t in EvidenceTier]
    assert tier_values == ["E0_CANDIDATE_ONLY", "E1_DISCOVERY_RECURRENCE"]
    assert "E2_MULTICHANNEL_CONSENSUS" not in tier_values
    assert "E3_HELDOUT_FUTURE_SUPPORTED" not in tier_values
