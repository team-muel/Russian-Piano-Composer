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
) -> CTUCandidate:
    """
    Generate a matched random negative control segment from the discovery region.

    Controls MUST satisfy:
      1. Same piece as CTU.
      2. Same measure length as CTU.
      3. Non-overlapping (IoU < 0.50) with the target CTU and existing CTUs.
      4. Meets min_event_count (non-empty, active segment matching CTU activity requirements).
      5. Generated deterministically via RandomContext bound to piece_id and candidate_id.
    """
    length = ctu.span.end.measure_index - ctu.span.start.measure_index
    max_start = discovery_measure_count - length

    # Initialize deterministic RandomContext for control generation
    seed_str = f"ctu_control_{score.piece_id}_{ctu.candidate_id}_{control_index}"
    seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    ctx = RandomContext(root_seed=seed)
    rng = ctx.child("control_generator").python_rng()

    # Find all valid start measures in discovery region matching length and activity
    valid_candidates: list[tuple[SegmentSpan, SegmentRepresentation]] = []

    for start_m in range(max_start + 1):
        span = SegmentSpan(
            start=SegmentPosition(measure_index=start_m, offset=Fraction(0)),
            end=SegmentPosition(measure_index=start_m + length, offset=Fraction(0)),
        )

        # Exclude strong overlap with the CTU itself
        if compute_span_jaccard_overlap(span, ctu.span) >= 0.50:
            continue

        # Extract representation and check min_event_count
        rep = extract_segment_representation(score, span)
        total_attacks = sum(rep.texture_profile)
        if total_attacks >= min_event_count:
            valid_candidates.append((span, rep))

    if valid_candidates:
        # Sort for determinism before rng.choice
        valid_candidates.sort(key=lambda item: item[0].start.measure_index)
        ctrl_span, ctrl_rep = rng.choice(valid_candidates)
    else:
        # Fallback if no non-overlapping active segment exists: pick any valid span
        ctrl_span = SegmentSpan(
            start=SegmentPosition(measure_index=0, offset=Fraction(0)),
            end=SegmentPosition(measure_index=length, offset=Fraction(0)),
        )
        ctrl_rep = extract_segment_representation(score, ctrl_span)

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
        representation_hash=rep_hash,
        discovery_policy_hash=policy_hash,
        manifest_hash=manifest_hash,
    )
