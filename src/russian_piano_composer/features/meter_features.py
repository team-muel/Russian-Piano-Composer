"""
Metric and meter feature extractor (v2 polyphonic-audited).

Computes time-signature and structural metric features per piece.
Uses duration-weighted primary meter semantics and exact anacrusis measure checking.
All features are OBSERVED provenance.
"""
from collections import defaultdict
from fractions import Fraction

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore

METER_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="meter_primary_numerator",
        name="Primary Time Signature Numerator",
        description="Numerator of the time signature occupying the greatest cumulative metric duration",
        provenance=FeatureProvenance.OBSERVED,
        unit="beats",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="whole_piece",
    ),
    FeatureDefinition(
        feature_id="meter_primary_denominator",
        name="Primary Time Signature Denominator",
        description="Denominator of the time signature occupying the greatest cumulative metric duration",
        provenance=FeatureProvenance.OBSERVED,
        unit="beat_unit",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="whole_piece",
    ),
    FeatureDefinition(
        feature_id="meter_change_count",
        name="Meter Change Count",
        description="Number of time-signature transitions between adjacent measures",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="whole_piece",
    ),
    FeatureDefinition(
        feature_id="meter_has_pickup",
        name="Has Pickup Measure",
        description="1 if the first measure is a pickup (anacrusis), 0 otherwise",
        provenance=FeatureProvenance.OBSERVED,
        unit="boolean",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="whole_piece",
    ),
    FeatureDefinition(
        feature_id="meter_total_measures",
        name="Total Measure Count",
        description="Total number of measures in the piece",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
        comparison_ready=False,
        validity_category="B",
        observation_unit="whole_piece",
    ),
)


def extract_meter_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract metric and meter features from a canonical score."""
    if not score.measures:
        return {fd.feature_id: None for fd in METER_FEATURE_DEFINITIONS}

    # Duration-weighted primary meter calculation
    ts_durations: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for m in score.measures:
        key = (m.time_signature.numerator, m.time_signature.denominator)
        ts_durations[key] += m.actual_duration

    # Find time signature with maximum cumulative duration
    # Deterministic tie-breaking: first by duration descending, then by order of appearance
    first_seen: dict[tuple[int, int], int] = {}
    for idx, m in enumerate(score.measures):
        key = (m.time_signature.numerator, m.time_signature.denominator)
        if key not in first_seen:
            first_seen[key] = idx

    sorted_ts = sorted(
        ts_durations.keys(),
        key=lambda k: (-float(ts_durations[k]), first_seen[k]),
    )
    primary_num, primary_den = sorted_ts[0]

    # Count meter changes between adjacent measures
    changes = 0
    for i in range(1, len(score.measures)):
        prev = score.measures[i - 1]
        curr = score.measures[i]
        if (
            prev.time_signature.numerator != curr.time_signature.numerator
            or prev.time_signature.denominator != curr.time_signature.denominator
        ):
            changes += 1

    has_pickup = 1 if score.measures[0].is_pickup else 0

    return {
        "meter_primary_numerator": primary_num,
        "meter_primary_denominator": primary_den,
        "meter_change_count": changes,
        "meter_has_pickup": has_pickup,
        "meter_total_measures": len(score.measures),
    }
