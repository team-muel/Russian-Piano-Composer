"""
Rhythmic duration statistics feature extractor.

Computes per-piece duration distribution features from NOTE events.
Durations are expressed in quarter-note units (Fraction value * 4 when denominator is in whole notes).
All features are OBSERVED provenance.
"""
import math
from fractions import Fraction

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore, EventKind

# Standard simple dotted durations in quarter-note units
_DOTTED_VALUES: frozenset[Fraction] = frozenset({
    Fraction(3, 2),   # dotted quarter
    Fraction(3, 1),   # dotted half
    Fraction(3, 4),   # dotted eighth
    Fraction(3, 8),   # dotted sixteenth
    Fraction(6, 1),   # dotted whole
    Fraction(3, 16),  # dotted thirty-second
})

RHYTHM_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="rhythm_duration_mean",
        name="Mean Note Duration",
        description="Arithmetic mean of note durations in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_std",
        name="Duration Std Dev",
        description="Population standard deviation of note durations in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_median",
        name="Median Note Duration",
        description="Median note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_distinct_durations",
        name="Distinct Duration Count",
        description="Number of distinct duration values observed",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="rhythm_dotted_ratio",
        name="Dotted Note Ratio",
        description="Fraction of notes whose duration matches a standard dotted value",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_shortest_duration",
        name="Shortest Duration",
        description="Minimum note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_longest_duration",
        name="Longest Duration",
        description="Maximum note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_range_ratio",
        name="Duration Range Ratio",
        description="longest_duration / shortest_duration",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
)


def _duration_to_quarter_notes(dur: Fraction) -> Fraction:
    """
    Convert a duration from whole-note units to quarter-note units.

    In the CanonicalScore, durations are stored as fractions of a whole note.
    A quarter note = Fraction(1, 4) whole notes.
    To convert to quarter-note units: multiply by 4.
    """
    return dur * 4


def extract_rhythm_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract rhythmic duration statistics from a canonical score."""
    note_durations_raw = [
        e.duration for e in score.events
        if e.event_kind == EventKind.NOTE and not e.is_grace
    ]

    if not note_durations_raw:
        return {fd.feature_id: None for fd in RHYTHM_FEATURE_DEFINITIONS}

    # Convert to quarter-note units
    durations = [_duration_to_quarter_notes(d) for d in note_durations_raw]

    n = len(durations)
    dur_floats = [float(d) for d in durations]

    mean = sum(dur_floats) / n
    variance = sum((v - mean) ** 2 for v in dur_floats) / n
    std = math.sqrt(variance)

    sorted_floats = sorted(dur_floats)
    if n % 2 == 1:
        median = sorted_floats[n // 2]
    else:
        median = (sorted_floats[n // 2 - 1] + sorted_floats[n // 2]) / 2.0

    distinct = len(set(durations))
    shortest = min(dur_floats)
    longest = max(dur_floats)

    dotted_count = sum(1 for d in durations if d in _DOTTED_VALUES)
    range_ratio = longest / shortest if shortest > 0 else 0.0

    return {
        "rhythm_duration_mean": round(mean, 4),
        "rhythm_duration_std": round(std, 4),
        "rhythm_duration_median": round(median, 4),
        "rhythm_distinct_durations": distinct,
        "rhythm_dotted_ratio": round(dotted_count / n, 4),
        "rhythm_shortest_duration": round(shortest, 4),
        "rhythm_longest_duration": round(longest, 4),
        "rhythm_duration_range_ratio": round(range_ratio, 4),
    }
