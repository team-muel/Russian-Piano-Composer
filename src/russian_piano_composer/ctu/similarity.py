"""
Symbolic similarity metrics and recurrence evidence calculation.
"""

import math
from collections import Counter
from collections.abc import Sequence
from typing import TypeVar

from russian_piano_composer.ctu.models import SegmentRepresentation, SegmentSpan
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy

T = TypeVar("T")


def compute_ordered_ngram_multiset_similarity[T](
    seq1: Sequence[T],
    seq2: Sequence[T],
    n: int = 2,
) -> float | None:
    """
    Compute multiset Jaccard similarity over ordered n-gram tuple tokens.
    Returns None if neither sequence has enough elements to form an n-gram.
    """
    if len(seq1) < n and len(seq2) < n:
        return None

    if len(seq1) < n or len(seq2) < n:
        return 0.0

    ngrams1 = [tuple(seq1[i : i + n]) for i in range(len(seq1) - n + 1)]
    ngrams2 = [tuple(seq2[i : i + n]) for i in range(len(seq2) - n + 1)]

    c1 = Counter(ngrams1)
    c2 = Counter(ngrams2)

    all_keys = set(c1.keys()) | set(c2.keys())
    intersection_count = sum(min(c1[k], c2[k]) for k in all_keys)
    union_count = sum(max(c1[k], c2[k]) for k in all_keys)

    return intersection_count / union_count if union_count > 0 else 0.0


def compute_sequence_multiset_similarity[T](
    seq1: Sequence[T],
    seq2: Sequence[T],
) -> float | None:
    """
    Compute multiset Jaccard similarity over sequence elements.

    V1 Sparse Sequence Rules:
      - Both empty: return None (channel unavailable)
      - One empty, one non-empty: return 0.0
      - Both lengths >= 2: ordered 2-gram multiset Jaccard
      - Both lengths == 1: ordered 1-gram multiset Jaccard fallback
      - One length == 1, other length >= 2: return 0.0
    """
    if not seq1 and not seq2:
        return None

    if not seq1 or not seq2:
        return 0.0

    len1 = len(seq1)
    len2 = len(seq2)

    if len1 >= 2 and len2 >= 2:
        return compute_ordered_ngram_multiset_similarity(seq1, seq2, n=2)

    if len1 == 1 and len2 == 1:
        c1 = Counter(seq1)
        c2 = Counter(seq2)
        all_keys = set(c1.keys()) | set(c2.keys())
        intersection_count = sum(min(c1[k], c2[k]) for k in all_keys)
        union_count = sum(max(c1[k], c2[k]) for k in all_keys)
        return intersection_count / union_count if union_count > 0 else 0.0

    # Length mismatch (e.g. one length == 1, other >= 2)
    return 0.0


def _cosine_similarity(vec1: Sequence[int], vec2: Sequence[int]) -> float | None:
    """Compute cosine similarity between two numeric vectors. Returns None if both are empty/zero."""
    if len(vec1) != len(vec2) or not vec1:
        return None

    dot = sum(v1 * v2 for v1, v2 in zip(vec1, vec2, strict=True))
    norm1 = math.sqrt(sum(v1 * v1 for v1 in vec1))
    norm2 = math.sqrt(sum(v2 * v2 for v2 in vec2))

    if norm1 == 0.0 and norm2 == 0.0:
        return None
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

    Integrates 4 separate evidence channels:
      1. Melodic Interval Channel (weight_melodic = 0.40): Symmetric stream bipartite matching using
         ordered 2-gram multiset Jaccard (with single-element 1-gram fallback).
      2. Rhythmic IOI Ratio Channel (weight_rhythmic = 0.30): Ordered 2-gram multiset Jaccard
         (with single-element 1-gram fallback).
      3. Texture Profile Channel (weight_texture = 0.15): Note attack simultaneity sequence ordered 2-gram
         multiset Jaccard (with single-element 1-gram fallback).
      4. Sounding Pitch-Class Channel (weight_pitchclass = 0.15): 12-bin pitch-class attack cosine similarity.

    Missing/empty evidence channels return None and the composite score is normalized
    across available evidence channels. Returns 0.0 if total available weight < 0.20.
    Sim(A, B) == Sim(B, A) is strictly enforced.
    """
    if policy is None:
        policy = CTUDiscoveryPolicy()

    available_weights: float = 0.0
    weighted_scores: float = 0.0

    # 1. Melodic channel (Symmetric average best stream match)
    streams1 = [s for s in rep1.melodic_intervals if s]
    streams2 = [s for s in rep2.melodic_intervals if s]

    melodic_sim: float | None = None
    if streams1 or streams2:
        if not streams1 or not streams2:
            melodic_sim = 0.0
        else:
            # Pairwise stream similarities
            sim_matrix = [
                [compute_sequence_multiset_similarity(s1, s2) or 0.0 for s2 in streams2]
                for s1 in streams1
            ]
            # Forward best matches
            forward_avg = sum(max(row) for row in sim_matrix) / len(streams1)
            # Backward best matches
            backward_avg = sum(max(sim_matrix[i][j] for i in range(len(streams1))) for j in range(len(streams2))) / len(streams2)
            melodic_sim = (forward_avg + backward_avg) / 2.0

    if melodic_sim is not None:
        weighted_scores += policy.weight_melodic * melodic_sim
        available_weights += policy.weight_melodic

    # 2. Rhythmic channel
    rhythmic_sim = compute_sequence_multiset_similarity(rep1.rhythmic_ratios, rep2.rhythmic_ratios)
    if rhythmic_sim is not None:
        weighted_scores += policy.weight_rhythmic * rhythmic_sim
        available_weights += policy.weight_rhythmic

    # 3. Texture channel (weight_texture = 0.15: attack simultaneity sequence ordered 2-gram multiset Jaccard with 1-gram fallback)
    texture_sim = compute_sequence_multiset_similarity(rep1.texture_profile, rep2.texture_profile)
    if texture_sim is not None:
        weighted_scores += policy.weight_texture * texture_sim
        available_weights += policy.weight_texture

    # 4. Sounding Pitch-class channel (using pitch_class_counts cosine similarity)
    pc_sim = _cosine_similarity(rep1.pitch_class_counts, rep2.pitch_class_counts)
    if pc_sim is not None:
        weighted_scores += policy.weight_pitchclass * pc_sim
        available_weights += policy.weight_pitchclass

    if available_weights < 0.20:
        return 0.0

    composite = weighted_scores / available_weights
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
