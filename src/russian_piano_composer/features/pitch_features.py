"""
Pitch statistics feature extractor (v2 polyphonic-audited).

Computes per-piece pitch distribution features from non-grace note attack events.
Excludes tie continuations and grace notes from core pitch statistics.
All features are OBSERVED provenance.
"""
import math
from collections import Counter

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

PITCH_FEATURE_DEFINITIONS: tuple[FeatureDefinition, ...] = (
    FeatureDefinition(
        feature_id="pitch_range_semitones",
        name="Pitch Range (semitones)",
        description="max(midi) - min(midi) across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="semitones",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_mean_midi",
        name="Mean MIDI Pitch",
        description="Arithmetic mean of MIDI note numbers across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="midi",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_std_midi",
        name="Pitch Std Dev (MIDI)",
        description="Population standard deviation of MIDI note numbers across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="midi",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_median_midi",
        name="Median MIDI Pitch",
        description="Median MIDI note number across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="midi",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_class_entropy",
        name="Pitch Class Entropy",
        description="Shannon entropy of the 12-bin pitch-class attack histogram (base-2 logarithm)",
        provenance=FeatureProvenance.OBSERVED,
        unit="bits",
        dtype="float",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_class_count",
        name="Pitch Class Count",
        description="Number of distinct pitch classes (0-11) used",
        provenance=FeatureProvenance.OBSERVED,
        unit="count",
        dtype="int",
        comparison_ready=False,
        validity_category="B",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_lowest_midi",
        name="Lowest MIDI Pitch",
        description="Minimum MIDI note number across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="midi",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
    FeatureDefinition(
        feature_id="pitch_highest_midi",
        name="Highest MIDI Pitch",
        description="Maximum MIDI note number across non-grace NOTE attacks",
        provenance=FeatureProvenance.OBSERVED,
        unit="midi",
        dtype="int",
        comparison_ready=True,
        validity_category="A",
        observation_unit="note_attack",
    ),
)


def extract_pitch_features(
    score: CanonicalScore,
    policy: FeatureExtractionPolicy | None = None,
) -> dict[str, float | int | None]:
    """
    Extract pitch statistics from a canonical score using FeatureExtractionPolicy.
    """
    if policy is None:
        policy = FeatureExtractionPolicy()

    events: list[CanonicalScoreEvent] = list(score.events)
    if policy.grace_policy == GraceNotePolicy.EXCLUDE:
        events = [e for e in events if not e.is_grace]

    if policy.tie_policy == TieAttackPolicy.EXCLUDE_CONTINUATIONS:
        events = [e for e in events if e.tie_state not in (TieState.CONTINUE, TieState.STOP)]

    midi_values = [
        e.midi for e in events
        if e.event_kind == EventKind.NOTE
        and e.midi is not None
    ]

    if not midi_values:
        return {fd.feature_id: None for fd in PITCH_FEATURE_DEFINITIONS}

    n = len(midi_values)
    lowest = min(midi_values)
    highest = max(midi_values)
    mean = sum(midi_values) / n

    # Population standard deviation
    variance = sum((v - mean) ** 2 for v in midi_values) / n
    std = math.sqrt(variance)

    # Median
    sorted_vals = sorted(midi_values)
    if n % 2 == 1:
        median = float(sorted_vals[n // 2])
    else:
        median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

    # Pitch class histogram and Shannon entropy (base 2)
    pc_counts = Counter(v % 12 for v in midi_values)
    pc_total = sum(pc_counts.values())
    entropy = 0.0
    for count in pc_counts.values():
        if count > 0:
            p = count / pc_total
            entropy -= p * math.log2(p)

    return {
        "pitch_range_semitones": highest - lowest,
        "pitch_mean_midi": round(mean, 4),
        "pitch_std_midi": round(std, 4),
        "pitch_median_midi": round(median, 4),
        "pitch_class_entropy": round(entropy, 4),
        "pitch_class_count": len(pc_counts),
        "pitch_lowest_midi": lowest,
        "pitch_highest_midi": highest,
    }
