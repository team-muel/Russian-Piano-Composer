"""
Family B: Sonority & Harmonic Motion for RC-011.

Implements sounding pitch-class simultaneity analysis, interval class vectors,
bass-relative intervals, sonority transitions, and harmonic rhythm volatility.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue

if TYPE_CHECKING:
    from fractions import Fraction


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

    # Group notes by unique onset timepoint
    # Timepoint sorting by (measure_index, offset_in_measure)
    onsets_map: dict[tuple[int, Fraction], list[CanonicalScoreEvent]] = {}
    for n in notes:
        key = (n.measure_index, n.offset_in_measure)
        onsets_map.setdefault(key, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())
    n_onsets = len(sorted_onsets)

    # 1. Pitch-class cardinalities and vertical dyads
    cardinalities: list[int] = []
    total_dyads = 0
    ic1_count = 0
    ic6_count = 0
    bass_rel_intervals: set[int] = set()

    onset_pc_sets: list[tuple[frozenset[int], float, float]] = []  # (pc_set, dur_quarters, measure_float)

    for onset_k in sorted_onsets:
        m_idx, offset = onset_k

        onset_notes = onsets_map[onset_k]
        pitches = sorted([n.midi for n in onset_notes if n.midi is not None])
        pcs = frozenset(p % 12 for p in pitches)
        cardinalities.append(len(pcs))

        # Bass-relative intervals
        if pitches:
            bass_pitch = pitches[0]
            for p in pitches[1:]:
                bass_rel_intervals.add(interval_class(p - bass_pitch))

        # Vertical dyads across all sounding notes at this onset
        for idx1 in range(len(pitches)):
            for idx2 in range(idx1 + 1, len(pitches)):
                ic = interval_class(pitches[idx2] - pitches[idx1])
                total_dyads += 1
                if ic == 1:
                    ic1_count += 1
                elif ic == 6:
                    ic6_count += 1

        # Calculate onset duration until next onset (or note duration if last)
        onset_dur = float(max(n.duration * 4 for n in onset_notes))

        measure_pos = float(m_idx) + float(offset)
        onset_pc_sets.append((pcs, onset_dur, measure_pos))

    card_mean = sum(cardinalities) / float(len(cardinalities))
    if len(cardinalities) > 1:
        card_var = sum((x - card_mean) ** 2 for x in cardinalities) / float(len(cardinalities) - 1)
        card_std = math.sqrt(card_var)
    else:
        card_std = 0.0

    ic1_share = (ic1_count / float(total_dyads)) if total_dyads > 0 else 0.0
    ic6_share = (ic6_count / float(total_dyads)) if total_dyads > 0 else 0.0
    bass_variety = (len(bass_rel_intervals) / float(n_onsets)) if n_onsets > 0 else 0.0

    # 2. Sonority transitions & Harmonic rhythm
    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1

    distinct_transitions = 0
    pc_set_durations: dict[frozenset[int], float] = {}
    total_sounding_dur = 0.0

    measures_between_changes: list[float] = []
    last_change_measure = onset_pc_sets[0][2]
    prev_set = onset_pc_sets[0][0]
    pc_set_durations[prev_set] = pc_set_durations.get(prev_set, 0.0) + onset_pc_sets[0][1]
    total_sounding_dur += onset_pc_sets[0][1]

    for i in range(1, len(onset_pc_sets)):
        curr_set, dur, m_pos = onset_pc_sets[i]
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
    stable_share = (top_dur / total_sounding_dur) if total_sounding_dur > 0 else 0.0

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
