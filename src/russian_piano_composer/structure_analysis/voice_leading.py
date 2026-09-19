"""
Family E: Voice-Leading Geometry for RC-011.

Implements outer-voice contrapuntal motion classification (parallel, contrary, oblique),
stepwise resolution rates in soprano/bass, semitone approaches, common tone retention,
and minimal assignment voice-leading distance (Tymoczko metric).
"""

import hashlib
import itertools
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


def _pc_dist(a: int, b: int) -> int:
    """Distance between two pitch classes on circle of 12."""
    d = abs(a - b) % 12
    return min(d, 12 - d)


def minimal_voice_leading_distance(pc_set1: frozenset[int], pc_set2: frozenset[int]) -> float:
    """
    Compute deterministic, symmetric minimal voice-leading displacement between two pitch-class sets.

    - For equal-cardinality sets |A| = |B| = n: finds the optimal one-to-one bijection minimizing mean step distance.
    - For unequal cardinalities: computes the symmetric assignment distance (1/2)(C(A->B) + C(B->A)).
    - Strictly symmetric: D(A, B) == D(B, A).
    - Transposition equivariant: D(A+k, B+k) == D(A, B).
    """
    if not pc_set1 or not pc_set2:
        return 0.0

    s1, s2 = list(pc_set1), list(pc_set2)
    n1, n2 = len(s1), len(s2)

    if n1 == n2:
        # Check all permutations for optimal 1-to-1 bijective matching
        min_total = float("inf")
        for perm in itertools.permutations(s2):
            total = sum(_pc_dist(a, b) for a, b in zip(s1, perm, strict=True))
            if total < min_total:
                min_total = float(total)
        return min_total / float(n1)

    # Unequal cardinality: symmetric assignment distance
    cost_1_to_2 = sum(min(_pc_dist(a, b) for b in s2) for a in s1) / float(n1)
    cost_2_to_1 = sum(min(_pc_dist(b, a) for a in s1) for b in s2) / float(n2)
    return (cost_1_to_2 + cost_2_to_1) / 2.0


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

    # Group notes by unique global onset
    onsets_map: dict[Fraction, list[CanonicalScoreEvent]] = {}
    for n in notes:
        onsets_map.setdefault(n.global_onset, []).append(n)

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
        prev_t = sorted_onsets[i - 1]
        curr_t = sorted_onsets[i]

        prev_pitches = sorted({n.midi for n in onsets_map[prev_t] if n.midi is not None})
        curr_pitches = sorted({n.midi for n in onsets_map[curr_t] if n.midi is not None})

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

        vl_dist = minimal_voice_leading_distance(prev_pcs, curr_pcs)
        vl_distances.append(vl_dist)

    parallel_share = max(0.0, min(1.0, (parallel_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0))
    contrary_share = max(0.0, min(1.0, (contrary_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0))
    oblique_share = max(0.0, min(1.0, (oblique_motions / float(outer_motions_total)) if outer_motions_total > 0 else 0.0))

    soprano_step_share = max(0.0, min(1.0, (soprano_step_motions / float(soprano_motions_total)) if soprano_motions_total > 0 else 0.0))
    bass_step_share = max(0.0, min(1.0, (bass_step_motions / float(bass_motions_total)) if bass_motions_total > 0 else 0.0))

    semitone_rate = semitone_approaches / float(span_measures)
    common_tone_rate = max(0.0, min(1.0, (common_tone_retained / float(len(sorted_onsets) - 1)) if len(sorted_onsets) > 1 else 0.0))
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
