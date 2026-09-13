"""
Melodic contour feature extractor.

Computes Parsons contour code statistics and arch-shape correlation
from staff-1/voice-1 NOTE events.
All features are OBSERVED provenance.
"""
import math

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore, EventKind

CONTOUR_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="contour_ascending_ratio",
        name="Ascending Contour Ratio",
        description="Fraction of Parsons U (up) transitions in melody",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="contour_descending_ratio",
        name="Descending Contour Ratio",
        description="Fraction of Parsons D (down) transitions in melody",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="contour_repeat_ratio",
        name="Repeat Contour Ratio",
        description="Fraction of Parsons R (repeat/same pitch) transitions in melody",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="contour_arc_score",
        name="Arch Contour Score",
        description="Pearson correlation of pitch sequence with ideal arch shape (rise-then-fall)",
        provenance=FeatureProvenance.OBSERVED,
        unit="correlation",
        dtype="float",
    ),
)


def _extract_melody_midi(score: CanonicalScore) -> list[int]:
    """Extract MIDI values from staff-1/voice-1 NOTE events, sorted by onset."""
    melody_events = [
        e for e in score.events
        if e.event_kind == EventKind.NOTE
        and e.staff == 1
        and e.voice == 1
        and e.midi is not None
    ]
    melody_events.sort(key=lambda e: (e.global_onset, e.event_index))
    # midi is guaranteed non-None by the filter above
    return [e.midi for e in melody_events if e.midi is not None]


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


def extract_contour_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract melodic contour statistics from staff-1/voice-1."""
    midi_seq = _extract_melody_midi(score)

    if len(midi_seq) < 2:
        return {fd.feature_id: None for fd in CONTOUR_FEATURE_DEFINITIONS}

    # Parsons contour code
    n_transitions = len(midi_seq) - 1
    up_count = 0
    down_count = 0
    repeat_count = 0

    for i in range(n_transitions):
        diff = midi_seq[i + 1] - midi_seq[i]
        if diff > 0:
            up_count += 1
        elif diff < 0:
            down_count += 1
        else:
            repeat_count += 1

    # Arch score: correlation with ideal arch shape
    # Ideal arch: linearly rises to midpoint then linearly falls
    n = len(midi_seq)
    arch_template = []
    for i in range(n):
        # Normalized position [0, 1]
        t = i / (n - 1) if n > 1 else 0.5
        # Arch: peaks at t=0.5
        arch_template.append(1.0 - abs(2.0 * t - 1.0))

    arc_score = _pearson_correlation(
        [float(m) for m in midi_seq],
        arch_template,
    )

    return {
        "contour_ascending_ratio": round(up_count / n_transitions, 4),
        "contour_descending_ratio": round(down_count / n_transitions, 4),
        "contour_repeat_ratio": round(repeat_count / n_transitions, 4),
        "contour_arc_score": round(arc_score, 4),
    }
