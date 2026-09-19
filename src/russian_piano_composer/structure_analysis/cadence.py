"""
Family C: Cadential & Boundary Proxies for RC-011.

Implements observable boundary candidate detection (rhythmic elongation, rests, metric weight),
bass-scale degree resolutions (5->1, 4->1, 5->6), and composite cadential strength scoring.
"""

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue
from russian_piano_composer.structure_analysis.tonal import estimate_key_from_pc_distribution


@dataclass(frozen=True, slots=True)
class CadencePolicy:
    """Frozen policy parameters for Family C extraction."""

    boundary_ioi_ratio_threshold: float = 1.5
    min_measure_boundary_gap: float = 2.0

    def compute_policy_hash(self) -> str:
        canonical = {
            "boundary_ioi_ratio_threshold": self.boundary_ioi_ratio_threshold,
            "min_measure_boundary_gap": self.min_measure_boundary_gap,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class BoundaryCandidate:
    """A detected score location with structural boundary characteristics."""

    measure_index: int
    offset_fraction: Fraction
    duration_quarters: float
    strength_score: float
    bass_pitch: int
    pc_set: frozenset[int]
    is_downbeat: bool


def extract_cadence_features(
    score: CanonicalScore,
    policy: CadencePolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 6 Family C features for a canonical score."""
    if policy is None:
        policy = CadencePolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1

    if not notes:
        return {
            "cadence_boundary_candidate_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "cadence_boundary_strength_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "cadence_tonic_resolution_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "cadence_dominant_tonic_proxy_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "cadence_deceptive_proxy_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "cadence_resolution_strength_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # Group notes by unique onset timepoint
    onsets_map: dict[tuple[int, Fraction], list[CanonicalScoreEvent]] = {}
    for n in notes:
        key = (n.measure_index, n.offset_in_measure)
        onsets_map.setdefault(key, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())

    # Calculate global/local key for tonic relative pitch degree checks
    global_pc = [0.0] * 12
    for n in notes:
        if n.midi is not None:
            global_pc[n.midi % 12] += float(n.duration * 4)
    g_tonic, _, _ = estimate_key_from_pc_distribution(global_pc)

    # 1. Identify boundary candidates based on duration lengthening & metric position
    durations = [float(max(n.duration * 4 for n in onsets_map[k])) for k in sorted_onsets]
    median_dur = sorted(durations)[len(durations) // 2] if durations else 1.0

    boundary_candidates: list[BoundaryCandidate] = []
    tonic_resolutions = 0
    dominant_tonic_proxies = 0
    deceptive_proxies = 0
    resolution_scores: list[float] = []

    for i in range(len(sorted_onsets)):
        onset_k = sorted_onsets[i]
        m_idx, off_frac = onset_k
        onset_notes = onsets_map[onset_k]
        dur = durations[i]
        pitches = sorted([n.midi for n in onset_notes if n.midi is not None])
        if not pitches:
            continue
        bass_p = pitches[0]
        pcs = frozenset(p % 12 for p in pitches)
        is_downbeat = (off_frac == Fraction(0, 1))

        # Check boundary cue: duration lengthening or end of score
        is_lengthened = (dur >= median_dur * policy.boundary_ioi_ratio_threshold)
        is_final_event = (i == len(sorted_onsets) - 1)

        if is_lengthened or is_final_event or (is_downbeat and dur > median_dur):
            # Compute boundary strength
            strength = 0.3 * (1.0 if is_downbeat else 0.5)
            strength += 0.4 * min(2.0, dur / max(0.1, median_dur)) / 2.0
            if is_final_event:
                strength += 0.3
            strength = min(1.0, strength)

            bc = BoundaryCandidate(
                measure_index=m_idx,
                offset_fraction=off_frac,
                duration_quarters=dur,
                strength_score=round(strength, 6),
                bass_pitch=bass_p,
                pc_set=pcs,
                is_downbeat=is_downbeat,
            )
            boundary_candidates.append(bc)

            # Evaluate harmonic resolution at boundary if preceding onset exists
            res_score = 0.0
            if i > 0:
                prev_k = sorted_onsets[i - 1]
                prev_notes = onsets_map[prev_k]
                prev_pitches = sorted([n.midi for n in prev_notes if n.midi is not None])
                if prev_pitches:
                    prev_bass = prev_pitches[0]
                    prev_pcs = frozenset(p % 12 for p in prev_pitches)

                    bass_motion = (bass_p - prev_bass) % 12
                    # Tonic relative scale degrees
                    curr_bass_deg = (bass_p - g_tonic) % 12
                    prev_bass_deg = (prev_bass - g_tonic) % 12

                    # 5 -> 1 or 7 -> 1 resolution
                    if prev_bass_deg == 7 and curr_bass_deg == 0:
                        tonic_resolutions += 1
                        res_score += 0.6
                    elif prev_bass_deg == 11 and curr_bass_deg == 0:
                        tonic_resolutions += 1
                        res_score += 0.5
                    elif bass_motion == 5 or bass_motion == 7:  # Fourth up / Fifth down
                        tonic_resolutions += 1
                        res_score += 0.4

                    # Dominant-type to Tonic-type sonority proxy
                    # Dominant-type: contains (g_tonic + 7)%12 or (g_tonic + 11)%12
                    # Tonic-type: contains g_tonic and (g_tonic + 4 or 3)%12
                    has_dom_element = ((g_tonic + 7) % 12 in prev_pcs) or ((g_tonic + 11) % 12 in prev_pcs)
                    has_tonic_element = (g_tonic in pcs) and (((g_tonic + 4) % 12 in pcs) or ((g_tonic + 3) % 12 in pcs))

                    if has_dom_element and has_tonic_element:
                        dominant_tonic_proxies += 1
                        res_score += 0.4

                    # Deceptive motion: 5 -> 6 (prev bass deg == 7, curr bass deg == 8 or 9)
                    if prev_bass_deg == 7 and (curr_bass_deg in {8, 9}):
                        deceptive_proxies += 1
                        res_score += 0.5

            resolution_scores.append(min(1.0, res_score))

    candidate_rate = len(boundary_candidates) / float(span_measures)
    mean_strength = (sum(bc.strength_score for bc in boundary_candidates) / float(len(boundary_candidates))) if boundary_candidates else 0.0

    tonic_rate = tonic_resolutions / float(span_measures)
    dom_tonic_rate = dominant_tonic_proxies / float(span_measures)
    deceptive_rate = deceptive_proxies / float(span_measures)
    mean_res_score = (sum(resolution_scores) / float(len(resolution_scores))) if resolution_scores else 0.0

    return {
        "cadence_boundary_candidate_rate": FeatureValue(round(candidate_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_boundary_strength_mean": FeatureValue(
            round(mean_strength, 6),
            AvailabilityStatus.AVAILABLE if boundary_candidates else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "cadence_tonic_resolution_rate": FeatureValue(round(tonic_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_dominant_tonic_proxy_rate": FeatureValue(round(dom_tonic_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_deceptive_proxy_rate": FeatureValue(round(deceptive_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_resolution_strength_mean": FeatureValue(
            round(mean_res_score, 6),
            AvailabilityStatus.AVAILABLE if resolution_scores else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
