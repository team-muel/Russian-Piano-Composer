"""
Melodic interval statistics feature extractor (v2 polyphonic voice-aware).

Computes voice-aware melodic transition features independently for each (staff, voice) stream.
Filters out simultaneous chord-attack transitions and tie continuations.
All features are OBSERVED provenance.
"""
import math
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fractions import Fraction

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import (
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.features.policy import (
    FeatureExtractionPolicy,
    GraceNotePolicy,
    TieAttackPolicy,
)

INTERVAL_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="interval_mean_abs_semitones",
        name="Mean Absolute Interval (semitones)",
        description="Mean |semitone interval| across eligible voice-aware single-note monophonic transitions",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_std_abs_semitones",
        name="Interval Std Dev (semitones)",
        description="Population std dev of |semitone interval| across eligible monophonic transitions",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_max_abs_semitones",
        name="Largest Absolute Interval",
        description="Maximum |semitone interval| across eligible monophonic transitions",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_leap_ratio",
        name="Leap Ratio",
        description="Fraction of eligible melodic transitions with |semitones| > 2",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_step_ratio",
        name="Step Ratio",
        description="Fraction of eligible melodic transitions with |semitones| <= 2",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_direction_change_ratio",
        name="Direction Change Ratio",
        description="Fraction of consecutive eligible interval pairs with opposing signs",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="interval_unison_ratio",
        name="Unison Ratio",
        description="Fraction of eligible melodic transitions with semitones == 0",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
)


def _extract_voice_monophonic_intervals(
    score: CanonicalScore,
    policy: FeatureExtractionPolicy | None = None,
) -> list[int]:
    """
    Extract eligible monophonic melodic interval semitones from note streams per policy.
    """
    if policy is None:
        policy = FeatureExtractionPolicy()

    events: list[CanonicalScoreEvent] = list(score.events)
    if policy.grace_policy == GraceNotePolicy.EXCLUDE:
        events = [e for e in events if not e.is_grace]

    if policy.tie_policy == TieAttackPolicy.EXCLUDE_CONTINUATIONS:
        events = [e for e in events if e.tie_state not in (TieState.CONTINUE, TieState.STOP)]

    # Group events by (staff, voice) stream
    voice_events: dict[tuple[int, int], list[CanonicalScoreEvent]] = defaultdict(list)
    for e in events:
        if e.event_kind == EventKind.NOTE and e.midi is not None:
            voice_events[(e.staff, e.voice)].append(e)

    all_intervals: list[int] = []

    for _stream_key, stream_events in voice_events.items():
        # Group events by onset within this stream
        onset_groups: dict[Fraction, list[int]] = defaultdict(list)
        for e in stream_events:
            if e.midi is not None:
                onset_groups[e.global_onset].append(e.midi)

        sorted_onsets = sorted(onset_groups.keys())

        # Extract transitions between consecutive single-note onsets
        for i in range(len(sorted_onsets) - 1):
            on1 = sorted_onsets[i]
            on2 = sorted_onsets[i + 1]

            group1 = onset_groups[on1]
            group2 = onset_groups[on2]

            if len(group1) == 1 and len(group2) == 1:
                all_intervals.append(group2[0] - group1[0])

    return all_intervals



def extract_interval_features(
    score: CanonicalScore,
    policy: FeatureExtractionPolicy | None = None,
) -> dict[str, float | int | None]:
    """Extract voice-aware melodic interval statistics across eligible transitions using policy."""
    if policy is None:
        policy = FeatureExtractionPolicy()

    intervals = _extract_voice_monophonic_intervals(score, policy=policy)

    if not intervals:
        return {fd.feature_id: None for fd in INTERVAL_FEATURE_DEFINITIONS}

    abs_intervals = [abs(iv) for iv in intervals]

    n = len(abs_intervals)
    mean_abs = sum(abs_intervals) / n
    variance = sum((v - mean_abs) ** 2 for v in abs_intervals) / n
    std_abs = math.sqrt(variance)
    max_abs = max(abs_intervals)

    leaps = sum(1 for v in abs_intervals if v > 2)
    steps = sum(1 for v in abs_intervals if v <= 2)
    unisons = sum(1 for v in abs_intervals if v == 0)

    # Direction changes: count consecutive interval pairs with opposing signs (excluding zero)
    direction_changes = 0
    if len(intervals) >= 2:
        for i in range(len(intervals) - 1):
            if (intervals[i] > 0 and intervals[i + 1] < 0) or (intervals[i] < 0 and intervals[i + 1] > 0):
                direction_changes += 1
        direction_change_ratio = direction_changes / (len(intervals) - 1)
    else:
        direction_change_ratio = 0.0

    return {
        "interval_mean_abs_semitones": round(mean_abs, 4),
        "interval_std_abs_semitones": round(std_abs, 4),
        "interval_max_abs_semitones": max_abs,
        "interval_leap_ratio": round(leaps / n, 4),
        "interval_step_ratio": round(steps / n, 4),
        "interval_direction_change_ratio": round(direction_change_ratio, 4),
        "interval_unison_ratio": round(unisons / n, 4),
    }
