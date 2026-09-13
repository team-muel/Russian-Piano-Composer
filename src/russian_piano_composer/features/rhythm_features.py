"""
Rhythmic duration statistics feature extractor (v2 polyphonic-audited).

Computes per-piece duration distribution features from non-grace NOTE attacks.
Excludes unsupported notation-derived dotted/tuplet ratio features.
All features are OBSERVED provenance.
"""
import math

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore, EventKind, TieState

RHYTHM_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="rhythm_duration_mean",
        name="Mean Note Duration",
        description="Arithmetic mean of non-grace note durations in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_std",
        name="Duration Std Dev",
        description="Population standard deviation of note durations in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_median",
        name="Median Note Duration",
        description="Median note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_distinct_durations",
        name="Distinct Duration Count",
        description="Number of distinct non-grace duration values observed",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
        comparison_ready=False,
        validity_category="B",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_dotted_ratio",
        name="Dotted Note Ratio (Unsupported)",
        description="Disabled: Notation dot metadata is not preserved in canonical score schema v1",
        provenance=FeatureProvenance.ENGINEERING_HEURISTIC,
        unit="ratio",
        dtype="float",
        comparison_ready=False,
        validity_category="D",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_shortest_duration",
        name="Shortest Duration",
        description="Minimum non-grace note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_longest_duration",
        name="Longest Duration",
        description="Maximum non-grace note duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="quarter_notes",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="rhythm_duration_range_ratio",
        name="Duration Range Ratio",
        description="longest_duration / shortest_duration",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
)


def extract_rhythm_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract rhythmic duration statistics from non-grace note attacks."""
    note_durations_raw = [
        e.duration for e in score.events
        if e.event_kind == EventKind.NOTE
        and not e.is_grace
        and e.tie_state not in (TieState.CONTINUE, TieState.STOP)
    ]

    if not note_durations_raw:
        res: dict[str, float | int | None] = {fd.feature_id: None for fd in RHYTHM_FEATURE_DEFINITIONS}
        res["rhythm_dotted_ratio"] = None
        return res

    # Convert whole-note Fraction to quarter-note units (* 4)
    durations = [d * 4 for d in note_durations_raw]
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
    range_ratio = longest / shortest if shortest > 0 else 0.0

    return {
        "rhythm_duration_mean": round(mean, 4),
        "rhythm_duration_std": round(std, 4),
        "rhythm_duration_median": round(median, 4),
        "rhythm_distinct_durations": distinct,
        "rhythm_dotted_ratio": None,  # Explicitly disabled Category D feature
        "rhythm_shortest_duration": round(shortest, 4),
        "rhythm_longest_duration": round(longest, 4),
        "rhythm_duration_range_ratio": round(range_ratio, 4),
    }
