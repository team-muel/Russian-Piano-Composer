"""
Note density and texture feature extractor.

Computes per-piece density, rest ratio, and polyphonic texture metrics.
All features are OBSERVED provenance.
"""
from fractions import Fraction

from russian_piano_composer.domain.features import FeatureDefinition, FeatureProvenance
from russian_piano_composer.domain.score import CanonicalScore, EventKind

DENSITY_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="density_notes_per_measure",
        name="Notes Per Measure",
        description="Total NOTE events / total measures",
        provenance=FeatureProvenance.OBSERVED,
        unit="count/measure",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="density_events_per_measure",
        name="Events Per Measure",
        description="Total events (NOTE + REST) / total measures",
        provenance=FeatureProvenance.OBSERVED,
        unit="count/measure",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="density_notes_per_quarter",
        name="Notes Per Quarter Note",
        description="Total NOTE events / total piece duration in quarter-note units",
        provenance=FeatureProvenance.OBSERVED,
        unit="count/quarter",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="density_rest_ratio",
        name="Rest Ratio",
        description="REST events / total events",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="density_grace_note_ratio",
        name="Grace Note Ratio",
        description="Grace note count / total NOTE count",
        provenance=FeatureProvenance.OBSERVED,
        unit="ratio",
        dtype="float",
    ),
    FeatureDefinition(
        feature_id="density_staff_count",
        name="Staff Count",
        description="Number of distinct staves used",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
    ),
    FeatureDefinition(
        feature_id="density_voice_count",
        name="Voice Count",
        description="Number of distinct (staff, voice) combinations used",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
    ),
)


def extract_density_features(score: CanonicalScore) -> dict[str, float | int | None]:
    """Extract note density and texture features from a canonical score."""
    total_events = len(score.events)
    total_measures = len(score.measures)

    if total_events == 0 or total_measures == 0:
        return {fd.feature_id: None for fd in DENSITY_FEATURE_DEFINITIONS}

    note_count = sum(1 for e in score.events if e.event_kind == EventKind.NOTE)
    rest_count = sum(1 for e in score.events if e.event_kind == EventKind.REST)
    grace_count = sum(
        1 for e in score.events
        if e.event_kind == EventKind.NOTE and e.is_grace
    )

    # Total piece duration in whole-note units
    # Sum of all measure actual_durations
    total_duration_whole = sum(
        (m.actual_duration for m in score.measures),
        Fraction(0),
    )
    # Convert to quarter-note units
    total_duration_quarters = float(total_duration_whole * 4)

    notes_per_quarter = (
        note_count / total_duration_quarters if total_duration_quarters > 0 else 0.0
    )

    staves = {e.staff for e in score.events}
    voices = {(e.staff, e.voice) for e in score.events}

    grace_ratio = grace_count / note_count if note_count > 0 else 0.0

    return {
        "density_notes_per_measure": round(note_count / total_measures, 4),
        "density_events_per_measure": round(total_events / total_measures, 4),
        "density_notes_per_quarter": round(notes_per_quarter, 4),
        "density_rest_ratio": round(rest_count / total_events, 4),
        "density_grace_note_ratio": round(grace_ratio, 4),
        "density_staff_count": len(staves),
        "density_voice_count": len(voices),
    }
