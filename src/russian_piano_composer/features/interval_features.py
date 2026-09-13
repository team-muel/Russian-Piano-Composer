"""
Melodic interval statistics feature extractor.

Computes successive interval features from staff-1/voice-1 NOTE events.
All features are OBSERVED provenance.
"""
import math

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore, EventKind

INTERVAL_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="interval_mean_abs_semitones",
        name="Mean Absolute Interval (semitones)",
        description="Mean of |semitone interval| between successive staff-1/voice-1 notes",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="interval_std_abs_semitones",
        name="Interval Std Dev (semitones)",
        description="Population std dev of |semitone interval| between successive melody notes",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="interval_max_abs_semitones",
        name="Largest Absolute Interval",
        description="Maximum |semitone interval| in melody voice",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="interval_leap_ratio",
        name="Leap Ratio",
        description="Fraction of melodic intervals with |semitones| > 2",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="interval_step_ratio",
        name="Step Ratio",
        description="Fraction of melodic intervals with |semitones| <= 2",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="interval_direction_change_ratio",
        name="Direction Change Ratio",
        description="Fraction of consecutive interval pairs where direction changes",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="interval_unison_ratio",
        name="Unison Ratio",
        description="Fraction of melodic intervals with semitones == 0",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
)


def _extract_melody_notes(score: CanonicalScore) -> list[int]:
    """
    Extract MIDI values from staff-1/voice-1 NOTE events, sorted by onset.
    """
    melody_events = [
        e for e in score.events
        if e.event_kind == EventKind.NOTE
        and e.staff == 1
        and e.voice == 1
        and e.midi is not None
    ]
    # Events are already sorted by the CanonicalScore invariant, but
    # we sort explicitly to be safe for melody extraction.
    melody_events.sort(key=lambda e: (e.global_onset, e.event_index))
    # midi is guaranteed non-None by the filter above
    return [e.midi for e in melody_events if e.midi is not None]


def extract_interval_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract melodic interval statistics from staff-1/voice-1."""
    midi_seq = _extract_melody_notes(score)

    if len(midi_seq) < 2:
        return {fd.feature_id: None for fd in INTERVAL_FEATURE_DEFINITIONS}

    intervals = [midi_seq[i + 1] - midi_seq[i] for i in range(len(midi_seq) - 1)]
    abs_intervals = [abs(iv) for iv in intervals]

    n = len(abs_intervals)
    mean_abs = sum(abs_intervals) / n
    variance = sum((v - mean_abs) ** 2 for v in abs_intervals) / n
    std_abs = math.sqrt(variance)
    max_abs = max(abs_intervals)

    leaps = sum(1 for v in abs_intervals if v > 2)
    steps = sum(1 for v in abs_intervals if v <= 2)
    unisons = sum(1 for v in abs_intervals if v == 0)

    # Direction changes: count consecutive interval pairs with opposing signs
    direction_changes = 0
    if len(intervals) >= 2:
        for i in range(len(intervals) - 1):
            # Direction change: one positive and one negative (excluding zero)
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
