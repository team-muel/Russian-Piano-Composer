"""
Metric and meter feature extractor.

Computes time-signature and structural metric features per piece.
All features are OBSERVED provenance.
"""
from collections import Counter

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore

METER_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="meter_primary_numerator",
        name="Primary Time Signature Numerator",
        description="Numerator of the most common time signature",
        provenance=FeatureProvenance.OBSERVED,
        unit="beats",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="meter_primary_denominator",
        name="Primary Time Signature Denominator",
        description="Denominator of the most common time signature",
        provenance=FeatureProvenance.OBSERVED,
        unit="beat_unit",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="meter_change_count",
        name="Meter Change Count",
        description="Number of time-signature changes throughout the piece",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="meter_has_pickup",
        name="Has Pickup Measure",
        description="1 if the first measure is a pickup (anacrusis), 0 otherwise",
        provenance=FeatureProvenance.OBSERVED,
        unit="boolean",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="meter_total_measures",
        name="Total Measure Count",
        description="Total number of measures in the piece",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
    ),
)


def extract_meter_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract metric and meter features from a canonical score."""
    if not score.measures:
        return {fd.feature_id: None for fd in METER_FEATURE_DEFINITIONS}

    # Count time signatures by (numerator, denominator)
    ts_counts: Counter[tuple[int, int]] = Counter()
    for m in score.measures:
        ts_counts[(m.time_signature.numerator, m.time_signature.denominator)] += 1

    # Most common time signature
    (primary_num, primary_den), _ = ts_counts.most_common(1)[0]

    # Count meter changes (transitions between different time signatures)
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
