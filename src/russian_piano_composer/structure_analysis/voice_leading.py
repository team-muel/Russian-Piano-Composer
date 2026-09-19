"""
Family E: Voice-Leading Geometry for RC-011.

Implements outer-voice contrapuntal motion classification (parallel, contrary, oblique),
stepwise resolution rates in soprano/bass, semitone approaches, common tone retention,
and minimal bipartite matching voice-leading distance.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue

if TYPE_CHECKING:
    from fractions import Fraction


@dataclass(frozen=True, slots=True)
class VoiceLeadingPolicy:
    """Frozen policy parameters for Family E extraction."""

    step_interval_max: int = 2

    def compute_policy_hash(self) -> str:
        canonical = {"step_interval_max": self.step_interval_max}
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _minimal_voice_leading_distance(pc_set1: frozenset[int], pc_set2: frozenset[int]) -> float:
    """
    Compute minimal total semitone displacement between two pitch-class sets (Tymoczko metric).
    Maps each pitch class in smaller set to closest pitch class in larger set.
    """
    if not pc_set1 or not pc_set2:
        return 0.0

    s1, s2 = list(pc_set1), list(pc_set2)
    # Distance between two pitch classes on circle of 12
    def pc_dist(a: int, b: int) -> int:
        d = abs(a - b) % 12
        return min(d, 12 - d)

    total_dist = 0
    for a in s1:
        min_d = min(pc_dist(a, b) for b in s2)
        total_dist += min_d
    return float(total_dist) / float(len(s1))


def extract_voice_leading_features(
    score: CanonicalScore,
    policy: VoiceLeadingPolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 8 Family E features for a canonical score."""
    if policy is None:
        policy = VoiceLeadingPolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1

    if not notes:
        return {
            "vl_outer_parallel_motion_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_outer_contrary_motion_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_outer_oblique_motion_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_soprano_step_resolution_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_bass_step_motion_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_semitone_approach_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_common_tone_retention_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "vl_min_voice_leading_distance_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # Group notes by unique onset timepoint
    onsets_map: dict[tuple[int, Fraction], list[CanonicalScoreEvent]] = {}
    for n in notes:
        key = (n.measure_index, n.offset_in_measure)
        onsets_map.setdefault(key, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())

    outer_motions_total = 0
    parallel_motions = 0
    contrary_motions = 0
    oblique_motions = 0

    soprano_motions_total = 0
    soprano_step_motions = 0

    bass_motions_total = 0
    bass_step_motions = 0

    semitone_approaches = 0
    common_tone_retained = 0
    vl_distances: list[float] = []

    for i in range(1, len(sorted_onsets)):
        prev_k = sorted_onsets[i - 1]
        curr_k = sorted_onsets[i]

        prev_pitches = sorted([n.midi for n in onsets_map[prev_k] if n.midi is not None])
        curr_pitches = sorted([n.midi for n in onsets_map[curr_k] if n.midi is not None])

        if not prev_pitches or not curr_pitches:
            continue

        prev_soprano, prev_bass = prev_pitches[-1], prev_pitches[0]
        curr_soprano, curr_bass = curr_pitches[-1], curr_pitches[0]

        delta_sop = curr_soprano - prev_soprano
        delta_bass = curr_bass - prev_bass

        # Soprano & Bass step motions
        if delta_sop != 0:
            soprano_motions_total += 1
            if abs(delta_sop) <= policy.step_interval_max:
                soprano_step_motions += 1

        if delta_bass != 0:
            bass_motions_total += 1
            if abs(delta_bass) <= policy.step_interval_max:
                bass_step_motions += 1

        # Semitone approach in outer voices
        if abs(delta_sop) == 1 or abs(delta_bass) == 1:
            semitone_approaches += 1

        # Outer voice motion classification
        if delta_sop != 0 or delta_bass != 0:
            outer_motions_total += 1
            if delta_sop == 0 or delta_bass == 0:
                oblique_motions += 1
            elif (delta_sop > 0 and delta_bass < 0) or (delta_sop < 0 and delta_bass > 0):
                contrary_motions += 1
            elif delta_sop == delta_bass:
                parallel_motions += 1

        # Common tone retention & Minimal voice leading distance
        prev_pcs = frozenset(p % 12 for p in prev_pitches)
        curr_pcs = frozenset(p % 12 for p in curr_pitches)

        if len(prev_pcs.intersection(curr_pcs)) >= 1:
            common_tone_retained += 1

        vl_dist = _minimal_voice_leading_distance(prev_pcs, curr_pcs)
        vl_distances.append(vl_dist)

    parallel_share = (parallel_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0
    contrary_share = (contrary_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0
    oblique_share = (oblique_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0

    soprano_step_share = (soprano_step_motions / float(soprano_motions_total)) if soprano_motions_total > 0 else 0.0
    bass_step_share = (bass_step_motions / float(bass_motions_total)) if bass_motions_total > 0 else 0.0

    semitone_rate = semitone_approaches / float(span_measures)
    common_tone_rate = (common_tone_retained / float(len(sorted_onsets) - 1)) if len(sorted_onsets) > 1 else 0.0
    vl_dist_mean = (sum(vl_distances) / float(len(vl_distances))) if vl_distances else 0.0

    return {
        "vl_outer_parallel_motion_share": FeatureValue(
            round(parallel_share, 6),
            AvailabilityStatus.AVAILABLE if outer_motions_total > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_outer_contrary_motion_share": FeatureValue(
            round(contrary_share, 6),
            AvailabilityStatus.AVAILABLE if outer_motions_total > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_outer_oblique_motion_share": FeatureValue(
            round(oblique_share, 6),
            AvailabilityStatus.AVAILABLE if outer_motions_total > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_soprano_step_resolution_share": FeatureValue(
            round(soprano_step_share, 6),
            AvailabilityStatus.AVAILABLE if soprano_motions_total > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_bass_step_motion_share": FeatureValue(
            round(bass_step_share, 6),
            AvailabilityStatus.AVAILABLE if bass_motions_total > 0 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_semitone_approach_rate": FeatureValue(round(semitone_rate, 6), AvailabilityStatus.AVAILABLE),
        "vl_common_tone_retention_rate": FeatureValue(
            round(common_tone_rate, 6),
            AvailabilityStatus.AVAILABLE if len(sorted_onsets) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "vl_min_voice_leading_distance_mean": FeatureValue(
            round(vl_dist_mean, 6),
            AvailabilityStatus.AVAILABLE if vl_distances else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
