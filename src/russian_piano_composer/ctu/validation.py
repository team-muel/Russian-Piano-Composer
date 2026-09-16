"""
Held-out future-reuse validation pipeline and paired statistical inference.
"""

import math
from collections.abc import Sequence
from fractions import Fraction

from russian_piano_composer.ctu.controls import build_matched_control_pairs
from russian_piano_composer.ctu.models import (
    CTUCandidate,
    CTUDiscoveryResult,
    CTUValidationResult,
    EmpiricalCTUStatus,
    MatchedControlPair,
    PieceValidationRecord,
    SegmentPosition,
    SegmentSpan,
    compute_candidate_set_hash,
    compute_control_pair_set_hash,
    compute_validation_semantic_hash,
)
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy, CTUValidationPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.similarity import compute_segment_similarity
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.runtime.random_context import RandomContext


def _compute_future_reuse_score(
    score: CanonicalScore,
    candidate: CTUCandidate,
    discovery_measures: int,
    total_measures: int,
    policy: CTUDiscoveryPolicy,
) -> float:
    """
    Search strictly within the future validation region [discovery_measures, total_measures)
    for the maximum symbolic similarity match to the given candidate.
    """
    cand_len = candidate.span.end.measure_index - candidate.span.start.measure_index
    future_len = total_measures - discovery_measures

    if future_len < cand_len:
        return 0.0

    future_sims: list[float] = []
    start_m = discovery_measures

    while start_m + cand_len <= total_measures:
        future_span = SegmentSpan(
            start=SegmentPosition(measure_index=start_m, offset=Fraction(0)),
            end=SegmentPosition(measure_index=start_m + cand_len, offset=Fraction(0)),
        )
        future_rep = extract_segment_representation(score, future_span)
        sim = compute_segment_similarity(candidate.representation, future_rep, policy=policy)
        future_sims.append(sim)
        start_m += policy.stride_measures

    return max(future_sims) if future_sims else 0.0


def validate_ctu_future_reuse(
    scores_by_id: dict[str, CanonicalScore],
    discovery_results: tuple[CTUDiscoveryResult, ...],
    manifest_hash: str,
    disc_policy: CTUDiscoveryPolicy | None = None,
    val_policy: CTUValidationPolicy | None = None,
    matched_control_pairs: Sequence[MatchedControlPair] | None = None,
) -> CTUValidationResult:
    """
    Perform held-out future-reuse validation across eligible pieces in the corpus.

    Controls are generated from val_policy via build_matched_control_pairs.
    Calculates paired future-reuse metrics only over successfully matched CTU/Control pairs.
    If a control is CONTROL_UNAVAILABLE, that exact CTU/control pair is excluded from both CTU and control averages.
    """
    if disc_policy is None:
        disc_policy = CTUDiscoveryPolicy()
    if val_policy is None:
        val_policy = CTUValidationPolicy()

    disc_hash = disc_policy.compute_policy_hash()
    val_hash = val_policy.compute_policy_hash()
    val_sem_hash = compute_validation_semantic_hash()

    total_pieces = len(discovery_results)
    eligible_records: list[PieceValidationRecord] = []
    all_control_pairs: list[MatchedControlPair] = []
    ineligible_count = 0

    total_requested = 0
    total_valid_matched = 0
    total_unavailable = 0

    for disc_res in discovery_results:
        if not disc_res.is_eligible or not disc_res.retained_ctus:
            ineligible_count += 1
            continue

        score = scores_by_id.get(disc_res.piece_id)
        if score is None:
            ineligible_count += 1
            continue

        if matched_control_pairs is not None:
            pairs = tuple(p for p in matched_control_pairs if p.target_ctu.piece_id == disc_res.piece_id)
        else:
            # Generate matched control pairs explicitly governed by val_policy
            pairs = build_matched_control_pairs(
                score=score,
                discovery_result=disc_res,
                validation_policy=val_policy,
                manifest_hash=manifest_hash,
            )
        all_control_pairs.extend(pairs)

        ctu_paired_scores: list[float] = []
        ctrl_paired_scores: list[float] = []
        unavailable_in_piece = 0

        for pair in pairs:
            total_requested += 1
            if not pair.is_available or pair.control_candidate is None:
                total_unavailable += 1
                unavailable_in_piece += 1
                continue

            total_valid_matched += 1

            ctu_fs = _compute_future_reuse_score(
                score, pair.target_ctu, disc_res.discovery_measures, disc_res.total_measures, disc_policy
            )
            ctrl_fs = _compute_future_reuse_score(
                score, pair.control_candidate, disc_res.discovery_measures, disc_res.total_measures, disc_policy
            )

            ctu_paired_scores.append(ctu_fs)
            ctrl_paired_scores.append(ctrl_fs)

        if not ctu_paired_scores:
            ineligible_count += 1
            continue

        mean_ctu_fs = sum(ctu_paired_scores) / len(ctu_paired_scores)
        mean_ctrl_fs = sum(ctrl_paired_scores) / len(ctrl_paired_scores)
        diff = mean_ctu_fs - mean_ctrl_fs

        eligible_records.append(
            PieceValidationRecord(
                piece_id=disc_res.piece_id,
                corpus_id=disc_res.corpus_id,
                ctu_mean_future_score=round(mean_ctu_fs, 4),
                control_mean_future_score=round(mean_ctrl_fs, 4),
                difference=round(diff, 4),
                matched_pair_count=len(ctu_paired_scores),
                unavailable_control_count=unavailable_in_piece,
            )
        )

    eligible_count = len(eligible_records)

    cand_set_hash = compute_candidate_set_hash(discovery_results)
    ctrl_set_hash = compute_control_pair_set_hash(all_control_pairs)

    if eligible_count == 0:
        return CTUValidationResult(
            total_pieces=total_pieces,
            eligible_pieces=0,
            ineligible_pieces=ineligible_count,
            piece_records=(),
            mean_ctu_future_score=0.0,
            mean_control_future_score=0.0,
            mean_difference=0.0,
            cohens_d=0.0,
            bootstrap_ci_lower=0.0,
            bootstrap_ci_upper=0.0,
            permutation_p_value=1.0,
            positive_effect_fraction=0.0,
            empirical_status=EmpiricalCTUStatus.CTU_INCONCLUSIVE,
            manifest_hash=manifest_hash,
            discovery_policy_hash=disc_hash,
            validation_policy_hash=val_hash,
            validation_semantic_hash=val_sem_hash,
            candidate_set_hash=cand_set_hash,
            control_pair_set_hash=ctrl_set_hash,
            permutation_iterations=val_policy.permutation_iterations,
            permutation_extreme_count=val_policy.permutation_iterations,
            total_requested_controls=total_requested,
            valid_matched_controls=total_valid_matched,
            unavailable_controls=total_unavailable,
        )

    # Calculate corpus-level paired statistics
    ctu_means = [r.ctu_mean_future_score for r in eligible_records]
    ctrl_means = [r.control_mean_future_score for r in eligible_records]
    diffs = [r.difference for r in eligible_records]

    mean_ctu = sum(ctu_means) / eligible_count
    mean_ctrl = sum(ctrl_means) / eligible_count
    mean_diff = sum(diffs) / eligible_count

    positive_count = sum(1 for d in diffs if d > 0)
    positive_fraction = positive_count / eligible_count

    # Paired Cohen's dz using sample SD (n - 1)
    if eligible_count > 1:
        var_diff = sum((d - mean_diff) ** 2 for d in diffs) / (eligible_count - 1)
        std_diff = math.sqrt(var_diff)
        cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0
    else:
        cohens_d = 0.0

    # True two-sided paired sign-flip permutation test
    ctx = RandomContext(root_seed=val_policy.random_seed)
    perm_rng = ctx.child("permutation_test").python_rng()

    observed_abs_mean = abs(mean_diff)
    extreme_count = 0
    for _ in range(val_policy.permutation_iterations):
        perm_diffs = [d if perm_rng.random() < 0.5 else -d for d in diffs]
        perm_mean = sum(perm_diffs) / eligible_count
        if abs(perm_mean) >= observed_abs_mean:
            extreme_count += 1

    # Monte Carlo correction p-value: (extreme_count + 1) / (iterations + 1)
    permutation_p = (extreme_count + 1) / (val_policy.permutation_iterations + 1)

    # Bootstrap 95% Confidence Interval for mean difference
    boot_rng = ctx.child("bootstrap_ci").python_rng()
    boot_means: list[float] = []

    for _ in range(val_policy.bootstrap_iterations):
        sample = [boot_rng.choice(diffs) for _ in range(eligible_count)]
        boot_means.append(sum(sample) / eligible_count)

    boot_means.sort()
    ci_lower = boot_means[int(0.025 * val_policy.bootstrap_iterations)]
    ci_upper = boot_means[int(0.975 * val_policy.bootstrap_iterations)]

    # Determine empirical outcome status
    if permutation_p < 0.05 and ci_lower > 0.0 and mean_diff > 0.0:
        status = EmpiricalCTUStatus.CTU_VALIDATED
    elif permutation_p >= 0.05 or ci_upper <= 0.0 or mean_diff <= 0.0:
        status = EmpiricalCTUStatus.CTU_NOT_VALIDATED
    else:
        status = EmpiricalCTUStatus.CTU_INCONCLUSIVE

    return CTUValidationResult(
        total_pieces=total_pieces,
        eligible_pieces=eligible_count,
        ineligible_pieces=ineligible_count,
        piece_records=tuple(eligible_records),
        mean_ctu_future_score=round(mean_ctu, 4),
        mean_control_future_score=round(mean_ctrl, 4),
        mean_difference=round(mean_diff, 4),
        cohens_d=round(cohens_d, 4),
        bootstrap_ci_lower=round(ci_lower, 4),
        bootstrap_ci_upper=round(ci_upper, 4),
        permutation_p_value=round(permutation_p, 4),
        positive_effect_fraction=round(positive_fraction, 4),
        empirical_status=status,
        manifest_hash=manifest_hash,
        discovery_policy_hash=disc_hash,
        validation_policy_hash=val_hash,
        validation_semantic_hash=val_sem_hash,
        candidate_set_hash=cand_set_hash,
        control_pair_set_hash=ctrl_set_hash,
        permutation_iterations=val_policy.permutation_iterations,
        permutation_extreme_count=extreme_count,
        total_requested_controls=total_requested,
        valid_matched_controls=total_valid_matched,
        unavailable_controls=total_unavailable,
    )
