"""
Family F: Piano Texture & Registral Architecture for RC-011.

Implements registral centroids, registral vertical spans, interstaff clearance gaps,
attack simultaneity, block-chord tendency, figurative arpeggiation detection (with scale exclusion),
octave doubling, and motoric repeated note rates.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue


@dataclass(frozen=True, slots=True)
class TexturePolicy:
    """Frozen policy parameters for Family F extraction."""

    arpeggio_min_attacks: int = 4
    arpeggio_min_span_semitones: int = 12
    arpeggio_max_ioi: float = 0.5
    repeated_note_max_delta_t: float = 0.5

    def compute_policy_hash(self) -> str:
        canonical = {
            "arpeggio_max_ioi": self.arpeggio_max_ioi,
            "arpeggio_min_attacks": self.arpeggio_min_attacks,
            "arpeggio_min_span_semitones": self.arpeggio_min_span_semitones,
            "repeated_note_max_delta_t": self.repeated_note_max_delta_t,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def extract_texture_features(
    score: CanonicalScore,
    policy: TexturePolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 10 Family F features for a canonical score."""
    if policy is None:
        policy = TexturePolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1
    measure_indices = sorted({m.measure_index for m in measures}) if measures else []

    if not notes:
        return {
            "texture_register_centroid_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_register_centroid_std": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_register_span_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_register_span_max": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_interstaff_gap_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_simultaneity_attack_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_block_chord_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_arpeggiation_proxy_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_octave_doubling_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "texture_repeated_note_attack_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # 1. Registral Centroid across attacks
    all_pitches = [n.midi for n in notes if n.midi is not None]
    reg_centroid_mean = sum(all_pitches) / float(len(all_pitches))

    # Measure-level centroid std
    notes_by_m: dict[int, list[int]] = {}
    for n in notes:
        if n.midi is not None:
            notes_by_m.setdefault(n.measure_index, []).append(n.midi)

    m_centroids = [sum(pts) / float(len(pts)) for pts in notes_by_m.values() if pts]
    if len(m_centroids) > 1:
        m_cent_mean = sum(m_centroids) / float(len(m_centroids))
        m_cent_var = sum((x - m_cent_mean) ** 2 for x in m_centroids) / float(len(m_centroids) - 1)
        reg_centroid_std = math.sqrt(m_cent_var)
    else:
        reg_centroid_std = 0.0

    # 2. Onset grouping for vertical spans, simultaneity, block chords, octave doubling, interstaff gap
    onsets_map: dict[Fraction, list[CanonicalScoreEvent]] = {}
    for n in notes:
        onsets_map.setdefault(n.global_onset, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())
    n_onsets = len(sorted_onsets)

    spans: list[int] = []
    simultaneities: list[int] = []
    block_chord_onsets = 0
    octave_doubled_onsets = 0
    interstaff_gaps: list[int] = []

    for t in sorted_onsets:
        onset_notes = onsets_map[t]
        simultaneities.append(len(onset_notes))
        if len(onset_notes) >= 3:
            block_chord_onsets += 1

        pitches = sorted([n.midi for n in onset_notes if n.midi is not None])
        if pitches:
            span = pitches[-1] - pitches[0]
            spans.append(span)

            # Octave doubling check: same PC separated by multiple of 12 (>= 12 semitones)
            pcs_present = [p % 12 for p in pitches]
            if len(pcs_present) != len(set(pcs_present)):
                has_octave = False
                for idx1 in range(len(pitches)):
                    for idx2 in range(idx1 + 1, len(pitches)):
                        diff = pitches[idx2] - pitches[idx1]
                        if diff > 0 and diff % 12 == 0:
                            has_octave = True
                            break
                    if has_octave:
                        break
                if has_octave:
                    octave_doubled_onsets += 1

        # Interstaff gap: staff 1 min pitch minus staff 2 max pitch
        staff1_notes = [n.midi for n in onset_notes if n.staff == 1 and n.midi is not None]
        staff2_notes = [n.midi for n in onset_notes if n.staff == 2 and n.midi is not None]
        if staff1_notes and staff2_notes:
            gap = min(staff1_notes) - max(staff2_notes)
            interstaff_gaps.append(gap)

    span_mean = (sum(spans) / float(len(spans))) if spans else 0.0
    span_max = max(spans) if spans else 0
    simultaneity_mean = (sum(simultaneities) / float(len(simultaneities))) if simultaneities else 0.0
    block_share = max(0.0, min(1.0, (block_chord_onsets / float(n_onsets)) if n_onsets > 0 else 0.0))
    octave_share = max(0.0, min(1.0, (octave_doubled_onsets / float(n_onsets)) if n_onsets > 0 else 0.0))
    gap_mean = (sum(interstaff_gaps) / float(len(interstaff_gaps))) if interstaff_gaps else 0.0

    # 3. Arpeggiation proxy: sequential ordered attacks forming figuration run with IOI <= 0.5
    # Excluding scalar runs (where all adjacent intervals are <= 2 semitones)
    arpeggio_runs = 0
    max_arpeggio_ioi_frac = Fraction(int(policy.arpeggio_max_ioi * 100), 100)

    for m in measure_indices:
        m_onsets = [t for t in sorted_onsets if onsets_map[t][0].measure_index == m]
        # Look for consecutive single attacks with IOI <= max_arpeggio_ioi
        if len(m_onsets) >= policy.arpeggio_min_attacks:
            single_attack_onsets = [t for t in m_onsets if len(onsets_map[t]) == 1]
            if len(single_attack_onsets) >= policy.arpeggio_min_attacks:
                # Group into consecutive sub-sequences where IOI <= max_arpeggio_ioi
                current_run: list[CanonicalScoreEvent] = [onsets_map[single_attack_onsets[0]][0]]
                for i in range(1, len(single_attack_onsets)):
                    prev_t = single_attack_onsets[i - 1]
                    curr_t = single_attack_onsets[i]
                    ioi_frac = (curr_t - prev_t) * 4  # in quarter notes
                    if ioi_frac <= max_arpeggio_ioi_frac:
                        current_run.append(onsets_map[curr_t][0])
                    else:
                        # Evaluate completed run
                        if len(current_run) >= policy.arpeggio_min_attacks:
                            run_pitches = [ev.midi for ev in current_run if ev.midi is not None]
                            if len(run_pitches) >= policy.arpeggio_min_attacks:
                                r_span = max(run_pitches) - min(run_pitches)
                                if r_span >= policy.arpeggio_min_span_semitones:
                                    # Scale exclusion check: is every step <= 2 semitones?
                                    is_scale = all(
                                        abs(run_pitches[k + 1] - run_pitches[k]) <= 2
                                        for k in range(len(run_pitches) - 1)
                                    )
                                    if not is_scale:
                                        arpeggio_runs += 1
                        current_run = [onsets_map[curr_t][0]]

                # Evaluate final run in measure
                if len(current_run) >= policy.arpeggio_min_attacks:
                    run_pitches = [ev.midi for ev in current_run if ev.midi is not None]
                    if len(run_pitches) >= policy.arpeggio_min_attacks:
                        r_span = max(run_pitches) - min(run_pitches)
                        if r_span >= policy.arpeggio_min_span_semitones:
                            is_scale = all(
                                abs(run_pitches[k + 1] - run_pitches[k]) <= 2
                                for k in range(len(run_pitches) - 1)
                            )
                            if not is_scale:
                                arpeggio_runs += 1

    arpeggio_rate = arpeggio_runs / float(span_measures)

    # 4. Repeated note attack rate (immediate repetition on same pitch with delta_t <= 0.5 quarters)
    repeated_note_attacks = 0
    max_rep_delta_frac = Fraction(int(policy.repeated_note_max_delta_t * 100), 100)

    for i in range(1, len(sorted_onsets)):
        prev_t = sorted_onsets[i - 1]
        curr_t = sorted_onsets[i]
        delta_t_quarters = (curr_t - prev_t) * 4

        if delta_t_quarters <= max_rep_delta_frac:
            prev_pts = set(n.midi for n in onsets_map[prev_t] if n.midi is not None)
            curr_pts = set(n.midi for n in onsets_map[curr_t] if n.midi is not None)
            common = prev_pts.intersection(curr_pts)
            if common:
                repeated_note_attacks += len(common)

    repeated_rate = repeated_note_attacks / float(span_measures)

    return {
        "texture_register_centroid_mean": FeatureValue(round(reg_centroid_mean, 6), AvailabilityStatus.AVAILABLE),
        "texture_register_centroid_std": FeatureValue(
            round(reg_centroid_std, 6),
            AvailabilityStatus.AVAILABLE if len(m_centroids) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "texture_register_span_mean": FeatureValue(round(span_mean, 6), AvailabilityStatus.AVAILABLE),
        "texture_register_span_max": FeatureValue(round(float(span_max), 6), AvailabilityStatus.AVAILABLE),
        "texture_interstaff_gap_mean": FeatureValue(
            round(gap_mean, 6),
            AvailabilityStatus.AVAILABLE if interstaff_gaps else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "texture_simultaneity_attack_mean": FeatureValue(round(simultaneity_mean, 6), AvailabilityStatus.AVAILABLE),
        "texture_block_chord_share": FeatureValue(round(block_share, 6), AvailabilityStatus.AVAILABLE),
        "texture_arpeggiation_proxy_rate": FeatureValue(round(arpeggio_rate, 6), AvailabilityStatus.AVAILABLE),
        "texture_octave_doubling_share": FeatureValue(round(octave_share, 6), AvailabilityStatus.AVAILABLE),
        "texture_repeated_note_attack_rate": FeatureValue(round(repeated_rate, 6), AvailabilityStatus.AVAILABLE),
    }
