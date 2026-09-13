"""
Melodic contour feature extractor (v2 polyphonic voice-aware).

Computes Parsons contour code statistics and arch-shape correlation
from voice-partitioned single-note NOTE attack sequences.
All features are OBSERVED provenance (arc_score is categorized C / ENGINEERING_HEURISTIC).
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
from russian_piano_composer.features.policy import FeatureExtractionPolicy

CONTOUR_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="contour_ascending_ratio",
        name="Ascending Contour Ratio",
        description="Fraction of Parsons U (up) transitions in eligible monophonic voice streams",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="contour_descending_ratio",
        name="Descending Contour Ratio",
        description="Fraction of Parsons D (down) transitions in eligible monophonic voice streams",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="contour_repeat_ratio",
        name="Repeat Contour Ratio",
        description="Fraction of Parsons R (repeat/same pitch) transitions in eligible monophonic voice streams",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="voice_transition",
    ),
    FeatureDefinition(
        feature_id="contour_arc_score",
        name="Arch Contour Score",
        description="Pearson correlation of top-voice pitch sequence with ideal arch shape (rise-then-fall)",
        provenance=FeatureProvenance.ENGINEERING_HEURISTIC,
        unit="correlation",
        dtype="float",
        comparison_ready=False,
        validity_category="C",
        observation_unit="whole_piece",
    ),
)


def _extract_voice_monophonic_pitch_sequence(score: CanonicalScore) -> list[int]:
    """
    Extract eligible monophonic pitch sequences across voice streams.
    """
    voice_events: dict[tuple[int, int], list[CanonicalScoreEvent]] = defaultdict(list)
    for e in score.events:
        if (
            e.event_kind == EventKind.NOTE
            and not e.is_grace
            and e.tie_state not in (TieState.CONTINUE, TieState.STOP)
            and e.midi is not None
        ):
            voice_events[(e.staff, e.voice)].append(e)

    # For arch score: extract top-voice (staff 1, lowest voice number) single-note sequence
    top_voice_key = None
    if voice_events:
        staff1_keys = [k for k in voice_events if k[0] == 1]
        if staff1_keys:
            top_voice_key = min(staff1_keys, key=lambda k: k[1])
        else:
            top_voice_key = min(voice_events.keys())

    if top_voice_key is None:
        return []

    events = voice_events[top_voice_key]
    onset_groups: dict[Fraction, list[int]] = defaultdict(list)
    for e in events:
        if e.midi is not None:
            onset_groups[e.global_onset].append(e.midi)

    sorted_onsets = sorted(onset_groups.keys())
    top_sequence = []
    for on in sorted_onsets:
        group = onset_groups[on]
        if len(group) == 1:
            top_sequence.append(group[0])

    return top_sequence


def _pearson_correlation(x: list[float], y: list[float]) -> float:
    """Compute Pearson correlation coefficient between two equal-length sequences."""
    n = len(x)
    if n < 2:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y, strict=True))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    denom = math.sqrt(var_x * var_y)
    if denom == 0.0:
        return 0.0
    return cov / denom


def extract_contour_features(
    score: CanonicalScore,
    policy: FeatureExtractionPolicy | None = None,
) -> dict[str, float | int | None]:
    """Extract melodic contour statistics using voice-aware monophonic streams and policy."""
    if policy is None:
        policy = FeatureExtractionPolicy()

    from russian_piano_composer.features.interval_features import (
        _extract_voice_monophonic_intervals,
    )

    intervals = _extract_voice_monophonic_intervals(score, policy=policy)

    if not intervals:
        return {fd.feature_id: None for fd in CONTOUR_FEATURE_DEFINITIONS}

    n_transitions = len(intervals)
    up_count = sum(1 for iv in intervals if iv > 0)
    down_count = sum(1 for iv in intervals if iv < 0)
    repeat_count = sum(1 for iv in intervals if iv == 0)

    # Arch score: correlation of top voice sequence with ideal arch shape
    top_seq = _extract_voice_monophonic_pitch_sequence(score)
    n_top = len(top_seq)

    if n_top >= 2:
        arch_template = []
        for i in range(n_top):
            t = i / (n_top - 1) if n_top > 1 else 0.5
            arch_template.append(1.0 - abs(2.0 * t - 1.0))

        arc_score = _pearson_correlation(
            [float(m) for m in top_seq],
            arch_template,
        )
    else:
        arc_score = 0.0

    return {
        "contour_ascending_ratio": round(up_count / n_transitions, 4),
        "contour_descending_ratio": round(down_count / n_transitions, 4),
        "contour_repeat_ratio": round(repeat_count / n_transitions, 4),
        "contour_arc_score": round(arc_score, 4),
    }
