"""
Multi-channel symbolic representation extractor for score segments.
"""

from collections import defaultdict
from fractions import Fraction

from russian_piano_composer.ctu.models import SegmentRepresentation, SegmentSpan
from russian_piano_composer.domain.score import CanonicalScore, EventKind, TieState


def extract_segment_representation(
    score: CanonicalScore,
    span: SegmentSpan,
) -> SegmentRepresentation:
    """
    Extract multi-channel symbolic representation for a segment span within a score.

    Maintains separate evidence channels without polyphonic melody flattening:
      1. Melodic interval streams per (staff, voice).
      2. Rhythmic duration IOI ratios.
      3. Onset attack count texture profile.
      4. Spelled pitch-class distribution histogram.
    """
    start_m = span.start.measure_index
    end_m = span.end.measure_index

    # Filter events within span
    events = [
        e for e in score.events
        if start_m <= e.measure_index < end_m
        and not e.is_grace
        and e.tie_state not in (TieState.CONTINUE, TieState.STOP)
    ]

    # 1. Melodic / Interval Channel (staff, voice) streams
    voice_events: dict[tuple[int, int], list[int]] = defaultdict(list)
    for e in events:
        if e.event_kind == EventKind.NOTE and e.midi is not None:
            voice_events[(e.staff, e.voice)].append(e.midi)

    melodic_streams: list[tuple[int, ...]] = []
    for _v_key in sorted(voice_events.keys()):
        midis = voice_events[_v_key]
        if len(midis) >= 2:
            intervals = tuple(midis[i + 1] - midis[i] for i in range(len(midis) - 1))
            melodic_streams.append(intervals)
        elif len(midis) == 1:
            melodic_streams.append(())

    # 2. Rhythm Channel (relative onset IOI ratios)
    note_onsets = sorted({e.global_onset for e in events if e.event_kind == EventKind.NOTE})
    rhythmic_ratios: list[Fraction] = []
    if len(note_onsets) >= 2:
        iois = [note_onsets[i + 1] - note_onsets[i] for i in range(len(note_onsets) - 1)]
        first_ioi = iois[0]
        if first_ioi > 0:
            rhythmic_ratios = [ioi / first_ioi for ioi in iois]
        else:
            rhythmic_ratios = [Fraction(1)] * len(iois)

    # 3. Onset / Texture Channel (attack count per onset)
    onset_counts: dict[Fraction, int] = defaultdict(int)
    for e in events:
        if e.event_kind == EventKind.NOTE:
            onset_counts[e.global_onset] += 1
    texture_profile = tuple(onset_counts[on] for on in sorted(onset_counts.keys()))

    # 4. Pitch Class Distribution Channel (12-bin histogram)
    pc_counts = [0] * 12
    for e in events:
        if e.event_kind == EventKind.NOTE and e.midi is not None:
            pc_counts[e.midi % 12] += 1

    return SegmentRepresentation(
        melodic_intervals=tuple(melodic_streams),
        rhythmic_ratios=tuple(rhythmic_ratios),
        texture_profile=texture_profile,
        pitch_class_counts=tuple(pc_counts),
    )
