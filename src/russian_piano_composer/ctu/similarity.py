"""
Symbolic similarity metrics and recurrence evidence calculation.
"""

import math
from typing import Any

from russian_piano_composer.ctu.models import SegmentRepresentation, SegmentSpan
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy


def _sequence_jaccard_similarity(seq1: tuple[Any, ...], seq2: tuple[Any, ...]) -> float:
    """Compute Jaccard similarity over n-gram multiset tokens."""
    if not seq1 and not seq2:
        return 1.0
    if not seq1 or not seq2:
        return 0.0

    s1 = set(seq1)
    s2 = set(seq2)
    intersection = len(s1 & s2)
    union = len(s1 | s2)
    return intersection / union if union > 0 else 0.0


def _cosine_similarity(vec1: tuple[int, ...], vec2: tuple[int, ...]) -> float:
    """Compute cosine similarity between two equal-length numeric vectors."""
    if len(vec1) != len(vec2) or not vec1:
        return 0.0

    dot = sum(v1 * v2 for v1, v2 in zip(vec1, vec2, strict=True))
    norm1 = math.sqrt(sum(v1 * v1 for v1 in vec1))
    norm2 = math.sqrt(sum(v2 * v2 for v2 in vec2))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


def compute_segment_similarity(
    rep1: SegmentRepresentation,
    rep2: SegmentRepresentation,
    policy: CTUDiscoveryPolicy | None = None,
) -> float:
    """
    Compute multi-channel symbolic similarity between two segment representations.

    Weights are classified as ENGINEERING_HEURISTIC.
    """
    if policy is None:
        policy = CTUDiscoveryPolicy()

    # 1. Melodic channel similarity (average best stream match)
    melodic_sim = 0.0
    if rep1.melodic_intervals and rep2.melodic_intervals:
        stream_sims = []
        for s1 in rep1.melodic_intervals:
            best_stream_sim = max(
                (_sequence_jaccard_similarity(s1, s2) for s2 in rep2.melodic_intervals),
                default=0.0,
            )
            stream_sims.append(best_stream_sim)
        melodic_sim = sum(stream_sims) / len(stream_sims) if stream_sims else 0.0
    elif not rep1.melodic_intervals and not rep2.melodic_intervals:
        melodic_sim = 1.0

    # 2. Rhythmic channel similarity
    rhythmic_sim = _sequence_jaccard_similarity(rep1.rhythmic_ratios, rep2.rhythmic_ratios)

    # 3. Texture & Pitch profile similarity
    texture_sim = _cosine_similarity(
        rep1.pitch_class_counts,
        rep2.pitch_class_counts,
    )

    composite = (
        policy.weight_melodic * melodic_sim
        + policy.weight_rhythmic * rhythmic_sim
        + policy.weight_texture * texture_sim
    )
    return round(composite, 4)


def spans_overlap(span1: SegmentSpan, span2: SegmentSpan) -> bool:
    """Check if two measure spans overlap temporally."""
    return not (
        span1.end.measure_index <= span2.start.measure_index
        or span2.end.measure_index <= span1.start.measure_index
    )


def compute_span_jaccard_overlap(span1: SegmentSpan, span2: SegmentSpan) -> float:
    """Compute measure-level Jaccard overlap ratio between two spans."""
    start_max = max(span1.start.measure_index, span2.start.measure_index)
    end_min = min(span1.end.measure_index, span2.end.measure_index)

    intersection = max(0, end_min - start_max)
    if intersection == 0:
        return 0.0

    len1 = span1.end.measure_index - span1.start.measure_index
    len2 = span2.end.measure_index - span2.start.measure_index
    union = len1 + len2 - intersection

    return intersection / union if union > 0 else 0.0
