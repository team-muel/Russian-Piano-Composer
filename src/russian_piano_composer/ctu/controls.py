"""
Deterministic matched negative control generator for CTU validation.
"""

import hashlib
from fractions import Fraction

from russian_piano_composer.ctu.models import (
    CTUCandidate,
    SegmentPosition,
    SegmentRepresentation,
    SegmentSpan,
)
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
    policy_hash: str,
    min_event_count: int = 3,
    existing_ctus: tuple[CTUCandidate, ...] = (),
    attack_count_tolerance_ratio: float = 0.25,
    onset_count_tolerance_ratio: float = 0.25,
) -> CTUCandidate | None:
    """
    Generate a matched random negative control segment from the discovery region.

    Controls MUST strictly satisfy:
      1. Same piece as CTU.
      2. Same measure length as CTU.
      3. Same discovery region.
      4. min_event_count satisfied.
      5. IoU < 0.50 with target CTU.
      6. IoU < 0.50 with EVERY retained CTU in existing_ctus.
      7. Activity matching: attack count and distinct onset count within tolerance.
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

    attack_tol = max(1, round(target_attacks * attack_count_tolerance_ratio))
    onset_tol = max(1, round(target_onsets * onset_count_tolerance_ratio))

    min_attacks_allowed = max(min_event_count, target_attacks - attack_tol)
    max_attacks_allowed = target_attacks + attack_tol
    min_onsets_allowed = max(1, target_onsets - onset_tol)
    max_onsets_allowed = target_onsets + onset_tol

    # Initialize deterministic RandomContext for control generation
    seed_str = f"ctu_control_{score.piece_id}_{ctu.candidate_id}_{control_index}"
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

        # 3. Extract representation & verify activity matching
        rep = extract_segment_representation(score, span)
        cand_attacks = sum(rep.texture_profile)
        cand_onsets = len(rep.texture_profile)

        if not (min_attacks_allowed <= cand_attacks <= max_attacks_allowed):
            continue
        if not (min_onsets_allowed <= cand_onsets <= max_onsets_allowed):
            continue

        valid_candidates.append((span, rep))

    if not valid_candidates:
        return None

    # Sort for determinism before rng.choice
    valid_candidates.sort(key=lambda item: item[0].start.measure_index)
    ctrl_span, ctrl_rep = rng.choice(valid_candidates)

    rep_hash = ctrl_rep.compute_content_hash()
    ctrl_id = f"ctrl_{hashlib.sha256(f'{ctu.candidate_id}_ctrl'.encode()).hexdigest()[:16]}"

    return CTUCandidate(
        candidate_id=ctrl_id,
        piece_id=score.piece_id,
        corpus_id=score.corpus_id,
        canonical_piece_hash=score.compute_piece_hash(),
        span=ctrl_span,
        representation=ctrl_rep,
        discovery_score=0.0,
        tier=ctu.tier,
        ctu_schema_version=ctu.ctu_schema_version,
        representation_hash=rep_hash,
        discovery_policy_hash=policy_hash,
        manifest_hash=manifest_hash,
    )
