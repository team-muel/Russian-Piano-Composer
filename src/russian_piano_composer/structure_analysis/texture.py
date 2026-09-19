"""
Family F: Piano Texture & Registral Architecture for RC-011.

Implements registral centroids, registral vertical spans, interstaff clearance gaps,
attack simultaneity, block-chord tendency, figurative arpeggiation detection,
octave doubling, and motoric repeated note rates.
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
class TexturePolicy:
    """Frozen policy parameters for Family F extraction."""

    arpeggio_min_attacks: int = 4
    arpeggio_min_span_semitones: int = 12

    def compute_policy_hash(self) -> str:
        canonical = {
            "arpeggio_min_attacks": self.arpeggio_min_attacks,
            "arpeggio_min_span_semitones": self.arpeggio_min_span_semitones,
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
    onsets_map: dict[tuple[int, Fraction], list[CanonicalScoreEvent]] = {}
    for n in notes:
        key = (n.measure_index, n.offset_in_measure)
        onsets_map.setdefault(key, []).append(n)

    sorted_onsets = sorted(onsets_map.keys())
    n_onsets = len(sorted_onsets)

    spans: list[int] = []
    simultaneities: list[int] = []
    block_chord_onsets = 0
    octave_doubled_onsets = 0
    interstaff_gaps: list[int] = []

    for k in sorted_onsets:
        onset_notes = onsets_map[k]
        simultaneities.append(len(onset_notes))
        if len(onset_notes) >= 3:
            block_chord_onsets += 1

        pitches = sorted([n.midi for n in onset_notes if n.midi is not None])
        if pitches:
            span = pitches[-1] - pitches[0]
            spans.append(span)

            # Octave doubling check: same PC separated by multiple of 12
            pcs_present = [p % 12 for p in pitches]
            if len(pcs_present) != len(set(pcs_present)):
                # Potential octave doubling; verify >= 12 semitones
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

        # Interstaff gap: staff 1 (RH) min pitch minus staff 2 (LH) max pitch
        staff1_notes = [n.midi for n in onset_notes if n.staff == 1 and n.midi is not None]
        staff2_notes = [n.midi for n in onset_notes if n.staff == 2 and n.midi is not None]
        if staff1_notes and staff2_notes:
            gap = min(staff1_notes) - max(staff2_notes)
            interstaff_gaps.append(gap)

    span_mean = (sum(spans) / float(len(spans))) if spans else 0.0
    span_max = max(spans) if spans else 0
    simultaneity_mean = (sum(simultaneities) / float(len(simultaneities))) if simultaneities else 0.0
    block_share = (block_chord_onsets / float(n_onsets)) if n_onsets > 0 else 0.0
    octave_share = (octave_doubled_onsets / float(n_onsets)) if n_onsets > 0 else 0.0
    gap_mean = (sum(interstaff_gaps) / float(len(interstaff_gaps))) if interstaff_gaps else 0.0

    # 3. Arpeggiation proxy: sequential ordered attacks forming monotonic or sweeping contour
    arpeggio_runs = 0
    # Group onsets by measure and check for figurative runs
    for m in measure_indices:
        m_onsets = [k for k in sorted_onsets if k[0] == m]
        if len(m_onsets) >= policy.arpeggio_min_attacks:
            m_notes = [onsets_map[k][0] for k in m_onsets if len(onsets_map[k]) == 1]
            if len(m_notes) >= policy.arpeggio_min_attacks:
                m_pitches = [n.midi for n in m_notes if n.midi is not None]
                if len(m_pitches) >= policy.arpeggio_min_attacks:
                    m_span = max(m_pitches) - min(m_pitches)
                    if m_span >= policy.arpeggio_min_span_semitones:
                        # Check monotonicity (ascending or descending)
                        is_asc = all(m_pitches[i] < m_pitches[i + 1] for i in range(len(m_pitches) - 1))
                        is_desc = all(m_pitches[i] > m_pitches[i + 1] for i in range(len(m_pitches) - 1))
                        if is_asc or is_desc:
                            arpeggio_runs += 1

    arpeggio_rate = arpeggio_runs / float(span_measures)

    # 4. Repeated note attack rate (immediate repetition on same pitch)
    repeated_note_attacks = 0
    for i in range(1, len(sorted_onsets)):
        prev_k, curr_k = sorted_onsets[i - 1], sorted_onsets[i]
        prev_pts = set(n.midi for n in onsets_map[prev_k] if n.midi is not None)
        curr_pts = set(n.midi for n in onsets_map[curr_k] if n.midi is not None)
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
