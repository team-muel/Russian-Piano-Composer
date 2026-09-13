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
      1. Melodic interval streams per (staff, voice): notes grouped by exact onset.
         Transitions are formed ONLY between consecutive single-note attacked onsets.
      2. Rhythmic IOI ratio sequence: consecutive IOI ratios r_i = IOI_{i+1} / IOI_i.
      3. Onset attack count texture profile.
      4. Sounding pitch-class distribution histogram (12-bin, midi % 12).
    """
    start_m = span.start.measure_index
    end_m = span.end.measure_index

    # Filter events within span: exclude grace notes and tie continuations/stops per V2 semantics
    events = [
        e for e in score.events
        if start_m <= e.measure_index < end_m
        and not e.is_grace
        and e.tie_state not in (TieState.CONTINUE, TieState.STOP)
    ]

    # 1. Melodic / Interval Channel (staff, voice) streams
    # Group note events by (staff, voice) and then by global_onset
    stream_onsets: dict[tuple[int, int], dict[Fraction, list[int]]] = defaultdict(lambda: defaultdict(list))
    for e in events:
        if e.event_kind == EventKind.NOTE and e.midi is not None:
            stream_onsets[(e.staff, e.voice)][e.global_onset].append(e.midi)

    melodic_streams: list[tuple[int, ...]] = []
    for _v_key in sorted(stream_onsets.keys()):
        onset_dict = stream_onsets[_v_key]
        sorted_onsets = sorted(onset_dict.keys())

        # Form melodic transitions only between consecutive onsets with exactly 1 note attack
        single_note_sequence: list[int] = []
        for on in sorted_onsets:
            notes = onset_dict[on]
            if len(notes) == 1:
                single_note_sequence.append(notes[0])

        if len(single_note_sequence) >= 2:
            intervals = tuple(single_note_sequence[i + 1] - single_note_sequence[i] for i in range(len(single_note_sequence) - 1))
            melodic_streams.append(intervals)
        elif len(single_note_sequence) == 1:
            melodic_streams.append(())

    # 2. Rhythm Channel (consecutive IOI ratios r_i = IOI_{i+1} / IOI_i)
    note_onsets = sorted({e.global_onset for e in events if e.event_kind == EventKind.NOTE})
    rhythmic_ratios: list[Fraction] = []
    if len(note_onsets) >= 3:
        iois = [note_onsets[i + 1] - note_onsets[i] for i in range(len(note_onsets) - 1)]
        for i in range(len(iois) - 1):
            prev_ioi = iois[i]
            curr_ioi = iois[i + 1]
            if prev_ioi > 0:
                rhythmic_ratios.append(curr_ioi / prev_ioi)
            else:
                rhythmic_ratios.append(Fraction(1))

    # 3. Onset / Texture Channel (attack count per onset)
    onset_counts: dict[Fraction, int] = defaultdict(int)
    for e in events:
        if e.event_kind == EventKind.NOTE:
            onset_counts[e.global_onset] += 1
    texture_profile = tuple(onset_counts[on] for on in sorted(onset_counts.keys()))

    # 4. Sounding Pitch Class Distribution Channel (12-bin histogram)
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
