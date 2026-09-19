"""
Family C: Cadential & Boundary Proxies for RC-011.

Implements observable boundary candidate detection based on inter-onset interval (IOI) lengthening,
rest presence, metric position, local key estimation, bass scale degree resolutions (5->1, 5->6),
and cadential resolution strength scoring.
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
    min_measure_boundary_gap: float = 1.0
    local_window_measures: int = 4

    def compute_policy_hash(self) -> str:
        canonical = {
            "boundary_ioi_ratio_threshold": self.boundary_ioi_ratio_threshold,
            "min_measure_boundary_gap": self.min_measure_boundary_gap,
            "local_window_measures": self.local_window_measures,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class BoundaryCandidate:
    """A detected score location with structural boundary characteristics."""

    measure_index: int
    offset_fraction: Fraction
    global_onset: Fraction
    ioi_quarters: float
    strength_score: float
    bass_pitch: int
    pc_set: frozenset[int]
    is_downbeat: bool


def _estimate_local_key_at_measure(
    notes: list[CanonicalScoreEvent],
    target_measure: int,
    window_measures: int = 4,
) -> int:
    """Estimate local tonic pitch class in the preceding window [target_measure - window, target_measure]."""
    local_notes = [
        n for n in notes
        if (target_measure - window_measures) <= n.measure_index <= target_measure
        and n.midi is not None
    ]
    if not local_notes:
        local_notes = [n for n in notes if n.measure_index <= target_measure and n.midi is not None]
    if not local_notes:
        local_notes = [n for n in notes if n.midi is not None]

    pc_dist = [0.0] * 12
    for n in local_notes:
        if n.midi is not None:
            pc_dist[n.midi % 12] += float(n.duration * 4)

    tonic, _, _ = estimate_key_from_pc_distribution(pc_dist)
    return tonic


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

    # Group notes by unique global onset
    onsets_map: dict[Fraction, list[CanonicalScoreEvent]] = {}
    for n in notes:
        onsets_map.setdefault(n.global_onset, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())
    n_onsets = len(sorted_onsets)

    # 1. Compute exact Inter-Onset Intervals (IOI) in quarter notes
    iois: list[float] = []
    for i, t in enumerate(sorted_onsets):
        if i + 1 < n_onsets:
            ioi_q = float((sorted_onsets[i + 1] - t) * 4)
        else:
            max_dur = max(float(n.duration * 4) for n in onsets_map[t])
            ioi_q = max_dur
        iois.append(ioi_q)

    # 2. Detect boundary candidates using local median IOI and rest evidence
    raw_candidates: list[tuple[int, BoundaryCandidate]] = []  # (onset_index, candidate)

    for i, t in enumerate(sorted_onsets):
        onset_notes = onsets_map[t]
        m_idx = onset_notes[0].measure_index
        off_frac = onset_notes[0].offset_in_measure
        ioi = iois[i]

        pitches = sorted({n.midi for n in onset_notes if n.midi is not None})
        if not pitches:
            continue
        bass_p = pitches[0]
        pcs = frozenset(p % 12 for p in pitches)
        is_downbeat = (off_frac == Fraction(0, 1))

        # Local window for median IOI (+/- 4 measures or 8 surrounding onsets)
        local_iois = [
            iois[j] for j in range(max(0, i - 4), min(n_onsets, i + 5))
            if j != i
        ]
        if not local_iois:
            local_iois = [iois[i]]
        sorted_local = sorted(local_iois)
        local_median_ioi = sorted_local[len(sorted_local) // 2]

        is_lengthened = (ioi >= local_median_ioi * policy.boundary_ioi_ratio_threshold)
        is_final_event = (i == n_onsets - 1)

        # Rest evidence: release before next onset
        max_release = max(n.global_onset + n.duration for n in onset_notes)
        has_rest = (i + 1 < n_onsets) and (max_release < sorted_onsets[i + 1])

        if is_lengthened or is_final_event or (is_downbeat and ioi > local_median_ioi) or has_rest:
            strength = 0.25 * (1.0 if is_downbeat else 0.5)
            strength += 0.35 * min(2.0, ioi / max(0.25, local_median_ioi)) / 2.0
            if has_rest:
                strength += 0.2
            if is_final_event:
                strength += 0.2
            strength = min(1.0, max(0.0, strength))

            bc = BoundaryCandidate(
                measure_index=m_idx,
                offset_fraction=off_frac,
                global_onset=t,
                ioi_quarters=round(ioi, 6),
                strength_score=round(strength, 6),
                bass_pitch=bass_p,
                pc_set=pcs,
                is_downbeat=is_downbeat,
            )
            raw_candidates.append((i, bc))

    # 3. Filter candidates by min_measure_boundary_gap
    filtered_candidates: list[tuple[int, BoundaryCandidate]] = []
    for idx_i, cand in raw_candidates:
        if not filtered_candidates:
            filtered_candidates.append((idx_i, cand))
        else:
            _prev_idx, prev_cand = filtered_candidates[-1]
            measure_diff = float(cand.measure_index - prev_cand.measure_index) + float(cand.offset_fraction - prev_cand.offset_fraction)
            if measure_diff < policy.min_measure_boundary_gap:
                if cand.strength_score > prev_cand.strength_score:
                    filtered_candidates[-1] = (idx_i, cand)
            else:
                filtered_candidates.append((idx_i, cand))

    # 4. Evaluate harmonic resolution using LOCAL key proxy
    tonic_resolutions = 0
    dominant_tonic_proxies = 0
    deceptive_proxies = 0
    resolution_scores: list[float] = []

    for onset_idx, cand in filtered_candidates:
        res_score = 0.0
        if onset_idx > 0:
            prev_t = sorted_onsets[onset_idx - 1]
            prev_notes = onsets_map[prev_t]
            prev_pitches = sorted({n.midi for n in prev_notes if n.midi is not None})

            if prev_pitches:
                prev_bass = prev_pitches[0]
                prev_pcs = frozenset(p % 12 for p in prev_pitches)

                # Local key estimation
                local_tonic = _estimate_local_key_at_measure(
                    notes, cand.measure_index, policy.local_window_measures
                )

                curr_bass_deg = (cand.bass_pitch - local_tonic) % 12
                prev_bass_deg = (prev_bass - local_tonic) % 12
                bass_interval = (cand.bass_pitch - prev_bass) % 12

                # Authentic resolution: 5 -> 1 or 7 -> 1
                if prev_bass_deg == 7 and curr_bass_deg == 0:
                    tonic_resolutions += 1
                    res_score += 0.6
                elif prev_bass_deg == 11 and curr_bass_deg == 0:
                    tonic_resolutions += 1
                    res_score += 0.5
                elif bass_interval == 5 or bass_interval == 7:  # Fourth up / Fifth down
                    tonic_resolutions += 1
                    res_score += 0.4

                # Dominant-to-Tonic chord type proxy relative to local tonic
                has_dom_element = ((local_tonic + 7) % 12 in prev_pcs) or ((local_tonic + 11) % 12 in prev_pcs)
                has_tonic_element = (local_tonic in cand.pc_set) and (
                    ((local_tonic + 4) % 12 in cand.pc_set) or ((local_tonic + 3) % 12 in cand.pc_set)
                )
                if has_dom_element and has_tonic_element:
                    dominant_tonic_proxies += 1
                    res_score += 0.4

                # Deceptive motion: 5 -> 6 (prev degree 7, curr degree 8 or 9)
                if prev_bass_deg == 7 and (curr_bass_deg in {8, 9}):
                    deceptive_proxies += 1
                    res_score += 0.5

        resolution_scores.append(min(1.0, res_score))

    candidate_rate = len(filtered_candidates) / float(span_measures)
    mean_strength = (
        sum(c.strength_score for _, c in filtered_candidates) / float(len(filtered_candidates))
    ) if filtered_candidates else 0.0

    tonic_rate = tonic_resolutions / float(span_measures)
    dom_tonic_rate = dominant_tonic_proxies / float(span_measures)
    deceptive_rate = deceptive_proxies / float(span_measures)
    mean_res_score = (sum(resolution_scores) / float(len(resolution_scores))) if resolution_scores else 0.0

    return {
        "cadence_boundary_candidate_rate": FeatureValue(round(candidate_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_boundary_strength_mean": FeatureValue(
            round(mean_strength, 6),
            AvailabilityStatus.AVAILABLE if filtered_candidates else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "cadence_tonic_resolution_rate": FeatureValue(round(tonic_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_dominant_tonic_proxy_rate": FeatureValue(round(dom_tonic_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_deceptive_proxy_rate": FeatureValue(round(deceptive_rate, 6), AvailabilityStatus.AVAILABLE),
        "cadence_resolution_strength_mean": FeatureValue(
            round(mean_res_score, 6),
            AvailabilityStatus.AVAILABLE if resolution_scores else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
