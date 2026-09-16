"""
Deterministic matched negative control generator for CTU validation.
"""

import hashlib
from fractions import Fraction

from russian_piano_composer.ctu.models import (
    CTUCandidate,
    CTUDiscoveryResult,
    MatchedControlPair,
    SegmentPosition,
    SegmentRepresentation,
    SegmentSpan,
)
from russian_piano_composer.ctu.policy import CTUValidationPolicy
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.ctu.similarity import compute_span_jaccard_overlap
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.runtime.random_context import RandomContext


def generate_matched_control(
    score: CanonicalScore,
    ctu: CTUCandidate,
    control_index: int,
    discovery_measure_count: int,
    manifest_hash: str,
    validation_policy: CTUValidationPolicy,
    min_event_count: int = 3,
    existing_ctus: tuple[CTUCandidate, ...] = (),
) -> CTUCandidate | None:
    """
    Generate a matched random negative control segment from the discovery region.

    Governed strictly by validation_policy.

    Controls MUST strictly satisfy:
      1. Same piece as CTU.
      2. Same measure length as CTU.
      3. Same discovery region.
      4. min_event_count satisfied.
      5. IoU < 0.50 with target CTU.
      6. IoU < 0.50 with EVERY retained CTU in existing_ctus.
      7. Exact mathematical activity matching:
         abs(cand_attacks - target_attacks) / target_attacks <= control_attack_count_tolerance_ratio
         abs(cand_onsets - target_onsets) / target_onsets <= control_onset_count_tolerance_ratio
      8. Generated deterministically via RandomContext.

    Returns None (CONTROL_UNAVAILABLE) if no candidate satisfies all criteria.
    No fallback allowed.
    """
    length = ctu.span.end.measure_index - ctu.span.start.measure_index
    max_start = discovery_measure_count - length

    # Target CTU activity metrics
    ctu_rep = ctu.representation
    target_attacks = sum(ctu_rep.texture_profile)
    target_onsets = len(ctu_rep.texture_profile)

    if target_attacks == 0 or target_onsets == 0:
        return None

    policy_hash = validation_policy.compute_policy_hash()

    # Initialize deterministic RandomContext for control generation
    seed_str = f"ctu_control_{score.piece_id}_{ctu.candidate_id}_{control_index}_{policy_hash}"
    seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    ctx = RandomContext(root_seed=seed)
    rng = ctx.child("control_generator").python_rng()

    valid_candidates: list[tuple[SegmentSpan, SegmentRepresentation]] = []

    for start_m in range(max_start + 1):
        span = SegmentSpan(
            start=SegmentPosition(measure_index=start_m, offset=Fraction(0)),
            end=SegmentPosition(measure_index=start_m + length, offset=Fraction(0)),
        )

        # 1. Exclude IoU >= 0.50 with target CTU
        if compute_span_jaccard_overlap(span, ctu.span) >= 0.50:
            continue

        # 2. Exclude IoU >= 0.50 with ANY retained CTU in piece
        if any(compute_span_jaccard_overlap(span, existing.span) >= 0.50 for existing in existing_ctus):
            continue

        # 3. Extract representation & verify exact mathematical activity matching
        rep = extract_segment_representation(score, span)
        cand_attacks = sum(rep.texture_profile)
        cand_onsets = len(rep.texture_profile)

        if cand_attacks < min_event_count:
            continue

        # Exact relative difference formula
        attack_diff_ratio = abs(cand_attacks - target_attacks) / target_attacks
        if attack_diff_ratio > validation_policy.control_attack_count_tolerance_ratio:
            continue

        onset_diff_ratio = abs(cand_onsets - target_onsets) / target_onsets
        if onset_diff_ratio > validation_policy.control_onset_count_tolerance_ratio:
            continue

        valid_candidates.append((span, rep))

    if not valid_candidates:
        return None

    # Deterministically select one candidate from valid list
    chosen_span, chosen_rep = valid_candidates[rng.randrange(len(valid_candidates))]
    rep_hash = chosen_rep.compute_content_hash()
    cid_input = f"{score.piece_id}|control|{chosen_span.start.measure_index}|{chosen_span.end.measure_index}|{rep_hash}".encode()
    ctrl_id = f"ctrl_{hashlib.sha256(cid_input).hexdigest()[:16]}"

    return CTUCandidate(
        candidate_id=ctrl_id,
        piece_id=score.piece_id,
        corpus_id=score.corpus_id,
        canonical_piece_hash=score.compute_piece_hash(),
        span=chosen_span,
        representation=chosen_rep,
        discovery_score=0.0,
        tier=ctu.tier,
        ctu_schema_version=ctu.ctu_schema_version,
        representation_hash=rep_hash,
        discovery_policy_hash=ctu.discovery_policy_hash,
        manifest_hash=manifest_hash,
    )


def build_matched_control_pairs(
    score: CanonicalScore,
    discovery_result: CTUDiscoveryResult,
    validation_policy: CTUValidationPolicy,
    manifest_hash: str,
) -> tuple[MatchedControlPair, ...]:
    """
    Generate explicit, immutable MatchedControlPair objects for all retained CTUs in a discovery result.
    Controls are governed strictly by the passed CTUValidationPolicy.
    """
    pairs: list[MatchedControlPair] = []
    val_policy_hash = validation_policy.compute_policy_hash()

    for c_idx, ctu in enumerate(discovery_result.retained_ctus):
        ctrl_cand = generate_matched_control(
            score=score,
            ctu=ctu,
            control_index=c_idx,
            discovery_measure_count=discovery_result.discovery_measures,
            manifest_hash=manifest_hash,
            validation_policy=validation_policy,
            existing_ctus=discovery_result.retained_ctus,
        )

        pairs.append(
            MatchedControlPair(
                target_candidate_id=ctu.candidate_id,
                target_ctu=ctu,
                control_candidate=ctrl_cand,
                validation_policy_hash=val_policy_hash,
            )
        )

    return tuple(pairs)
