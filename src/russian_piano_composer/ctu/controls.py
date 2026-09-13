"""
Deterministic matched negative control generator for CTU validation.
"""

import hashlib
from fractions import Fraction

from russian_piano_composer.ctu.models import CTUCandidate, SegmentPosition, SegmentSpan
from russian_piano_composer.ctu.representation import extract_segment_representation
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.runtime.random_context import RandomContext


def generate_matched_control(
    score: CanonicalScore,
    ctu: CTUCandidate,
    control_index: int,
    discovery_measure_count: int,
    manifest_hash: str,
    policy_hash: str,
) -> CTUCandidate:
    """
    Generate a matched random negative control segment from the discovery region
    matching the length of the given CTU.

    Uses RandomContext with a deterministic seed bound to piece_id and candidate_id.
    """
    length = ctu.span.end.measure_index - ctu.span.start.measure_index
    max_start = discovery_measure_count - length

    # Initialize deterministic RandomContext for control generation
    seed_str = f"ctu_control_{score.piece_id}_{ctu.candidate_id}_{control_index}"
    seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:8], 16)
    ctx = RandomContext(root_seed=seed)
    rng = ctx.child("control_generator").python_rng()


    if max_start > 0:
        # Pick start measure avoiding exact CTU start if possible
        possible_starts = [m for m in range(max_start + 1) if m != ctu.span.start.measure_index]
        ctrl_start = rng.choice(possible_starts) if possible_starts else rng.randint(0, max_start)
    else:
        ctrl_start = 0

    ctrl_span = SegmentSpan(
        start=SegmentPosition(measure_index=ctrl_start, offset=Fraction(0)),
        end=SegmentPosition(measure_index=ctrl_start + length, offset=Fraction(0)),
    )

    ctrl_rep = extract_segment_representation(score, ctrl_span)
    rep_hash = ctrl_rep.compute_semantic_hash()
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
