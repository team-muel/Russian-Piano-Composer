"""
Multi-scale candidate window generator and temporal split partitioner.
"""

import math
from fractions import Fraction

from russian_piano_composer.ctu.models import SegmentPosition, SegmentSpan
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.domain.score import CanonicalScore


def compute_temporal_split(score: CanonicalScore, policy: CTUDiscoveryPolicy | None = None) -> tuple[int, int, bool]:
    """
    Compute measure split boundary between discovery region and future validation region.

    Returns:
        (discovery_measure_count, total_measures, is_eligible)
    """
    if policy is None:
        policy = CTUDiscoveryPolicy()

    total = len(score.measures)
    is_eligible = total >= policy.min_piece_measures
    discovery_count = math.floor(total * policy.discovery_ratio) if is_eligible else total
    return discovery_count, total, is_eligible


def generate_candidate_spans(
    score: CanonicalScore,
    discovery_measure_count: int,
    policy: CTUDiscoveryPolicy | None = None,
) -> list[SegmentSpan]:
    """
    Generate multi-scale candidate spans strictly within the discovery region [0, discovery_measure_count).

    Anti-leakage: No window may start at or extend past discovery_measure_count.
    """
    if policy is None:
        policy = CTUDiscoveryPolicy()

    spans: list[SegmentSpan] = []

    for length in policy.window_lengths:
        start_m = 0
        while start_m + length <= discovery_measure_count:
            end_m = start_m + length
            span = SegmentSpan(
                start=SegmentPosition(measure_index=start_m, offset=Fraction(0)),
                end=SegmentPosition(measure_index=end_m, offset=Fraction(0)),
            )
            # Count NOTE events in this span
            notes_in_span = sum(
                1 for e in score.events
                if start_m <= e.measure_index < end_m and e.event_kind.value == "NOTE"
            )
            if notes_in_span >= policy.min_event_count:
                spans.append(span)

            start_m += policy.stride_measures

    return spans
