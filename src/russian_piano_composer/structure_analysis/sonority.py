"""
Family B: Sonority & Harmonic Motion for RC-011.

Implements sounding pitch-class simultaneity analysis (including sustained notes),
interval class vectors, bass-relative intervals, sonority transitions, and harmonic rhythm volatility.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction

from russian_piano_composer.domain.score import CanonicalScore, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue


@dataclass(frozen=True, slots=True)
class SonorityPolicy:
    """Frozen policy parameters for Family B extraction."""

    top_pc_sets_count: int = 3

    def compute_policy_hash(self) -> str:
        canonical = {"top_pc_sets_count": self.top_pc_sets_count}
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def interval_class(semitones: int) -> int:
    """Map any semitone interval to interval class (0 to 6)."""
    diff = abs(semitones) % 12
    return min(diff, 12 - diff)


def extract_sonority_features(
    score: CanonicalScore,
    policy: SonorityPolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 8 Family B features for a canonical score."""
    if policy is None:
        policy = SonorityPolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1
    m_dur_map = {m.measure_index: m.actual_duration for m in measures}

    if not notes:
        return {
            "sonority_pc_cardinality_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_pc_cardinality_std": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_change_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_stable_duration_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_ic1_semitone_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_ic6_tritone_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_bass_interval_variety": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "sonority_harmonic_rhythm_volatility": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # Unique global onset timepoints
    sorted_unique_onsets: list[Fraction] = sorted({n.global_onset for n in notes})
    n_onsets = len(sorted_unique_onsets)

    # 1. At every onset timepoint t, construct the ACTIVE sounding note set
    # Active notes: note.global_onset <= t < note.global_onset + note.duration
    cardinalities: list[int] = []
    total_dyads = 0
    ic1_count = 0
    ic6_count = 0
    bass_rel_intervals: set[int] = set()

    # Store (pc_set, slice_duration_quarters, measure_float)
    slice_pc_sets: list[tuple[frozenset[int], float, float]] = []

    for i, t in enumerate(sorted_unique_onsets):
        active_notes = [
            n for n in notes
            if n.global_onset <= t < (n.global_onset + n.duration) and n.midi is not None
        ]

        sounding_pitches = sorted({n.midi for n in active_notes if n.midi is not None})
        sounding_pcs = frozenset(p % 12 for p in sounding_pitches)
        cardinalities.append(len(sounding_pcs))

        # Bass-relative intervals (from lowest sounding pitch)
        if sounding_pitches:
            bass_p = sounding_pitches[0]
            for p in sounding_pitches[1:]:
                bass_rel_intervals.add(interval_class(p - bass_p))

        # Vertical dyads across all active sounding pitches
        for idx1 in range(len(sounding_pitches)):
            for idx2 in range(idx1 + 1, len(sounding_pitches)):
                ic = interval_class(sounding_pitches[idx2] - sounding_pitches[idx1])
                total_dyads += 1
                if ic == 1:
                    ic1_count += 1
                elif ic == 6:
                    ic6_count += 1

        # Duration slice until next onset or end of sounding notes at this onset
        if i + 1 < n_onsets:
            slice_dur_quarters = float((sorted_unique_onsets[i + 1] - t) * 4)
        else:
            max_release = max(n.global_onset + n.duration for n in active_notes)
            slice_dur_quarters = float((max_release - t) * 4)

        # Measure float position
        # Find measure index corresponding to t
        active_m_idx = active_notes[0].measure_index if active_notes else 0
        m_dur = m_dur_map.get(active_m_idx, Fraction(1, 1))
        norm_off = float(active_notes[0].offset_in_measure / m_dur) if (active_notes and m_dur > 0) else 0.0
        measure_pos = float(active_m_idx) + norm_off

        slice_pc_sets.append((sounding_pcs, max(0.0, slice_dur_quarters), measure_pos))

    card_mean = sum(cardinalities) / float(len(cardinalities))
    if len(cardinalities) > 1:
        card_var = sum((x - card_mean) ** 2 for x in cardinalities) / float(len(cardinalities) - 1)
        card_std = math.sqrt(card_var)
    else:
        card_std = 0.0

    ic1_share = max(0.0, min(1.0, (ic1_count / float(total_dyads)) if total_dyads > 0 else 0.0))
    ic6_share = max(0.0, min(1.0, (ic6_count / float(total_dyads)) if total_dyads > 0 else 0.0))
    bass_variety = max(0.0, min(1.0, (len(bass_rel_intervals) / float(n_onsets)) if n_onsets > 0 else 0.0))

    # 2. Sonority transitions & Harmonic rhythm
    distinct_transitions = 0
    pc_set_durations: dict[frozenset[int], float] = {}
    total_sounding_dur = 0.0

    measures_between_changes: list[float] = []
    last_change_measure = slice_pc_sets[0][2]
    prev_set = slice_pc_sets[0][0]
    pc_set_durations[prev_set] = pc_set_durations.get(prev_set, 0.0) + slice_pc_sets[0][1]
    total_sounding_dur += slice_pc_sets[0][1]

    for i in range(1, len(slice_pc_sets)):
        curr_set, dur, m_pos = slice_pc_sets[i]
        pc_set_durations[curr_set] = pc_set_durations.get(curr_set, 0.0) + dur
        total_sounding_dur += dur

        if curr_set != prev_set:
            distinct_transitions += 1
            delta_m = m_pos - last_change_measure
            measures_between_changes.append(max(0.0, delta_m))
            last_change_measure = m_pos
            prev_set = curr_set

    sonority_rate = distinct_transitions / float(span_measures)

    # Stable duration share (top 3 most frequent PC sets)
    sorted_durations = sorted(pc_set_durations.items(), key=lambda item: item[1], reverse=True)
    top_3_sets = sorted_durations[:policy.top_pc_sets_count]
    top_dur = sum(cnt for _, cnt in top_3_sets)
    stable_share = max(0.0, min(1.0, (top_dur / total_sounding_dur) if total_sounding_dur > 0 else 0.0))

    # Harmonic rhythm volatility
    if len(measures_between_changes) > 1:
        hr_mean = sum(measures_between_changes) / float(len(measures_between_changes))
        hr_var = sum((x - hr_mean) ** 2 for x in measures_between_changes) / float(len(measures_between_changes) - 1)
        hr_std = math.sqrt(hr_var)
    else:
        hr_std = 0.0

    return {
        "sonority_pc_cardinality_mean": FeatureValue(round(card_mean, 6), AvailabilityStatus.AVAILABLE),
        "sonority_pc_cardinality_std": FeatureValue(
            round(card_std, 6),
            AvailabilityStatus.AVAILABLE if len(cardinalities) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "sonority_change_rate": FeatureValue(round(sonority_rate, 6), AvailabilityStatus.AVAILABLE),
        "sonority_stable_duration_share": FeatureValue(round(stable_share, 6), AvailabilityStatus.AVAILABLE),
        "sonority_ic1_semitone_share": FeatureValue(
            round(ic1_share, 6),
            AvailabilityStatus.AVAILABLE if total_dyads > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "sonority_ic6_tritone_share": FeatureValue(
            round(ic6_share, 6),
            AvailabilityStatus.AVAILABLE if total_dyads > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "sonority_bass_interval_variety": FeatureValue(round(bass_variety, 6), AvailabilityStatus.AVAILABLE),
        "sonority_harmonic_rhythm_volatility": FeatureValue(
            round(hr_std, 6),
            AvailabilityStatus.AVAILABLE if len(measures_between_changes) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
