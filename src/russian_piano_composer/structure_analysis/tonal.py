"""
Family A: Tonal / Harmonic Center Proxies for RC-011.

Implements duration-weighted pitch-class distributions, Krumhansl-Kessler key correlations,
local sliding window estimations, circle-of-fifths metrics, and diatonic/chromatic ratios.
"""

import hashlib
import json
import math
from dataclasses import dataclass

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue

# Standard Krumhansl-Kessler 12-PC Profiles
KRUMHANSL_MAJOR_PROFILE: tuple[float, ...] = (
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88
)
KRUMHANSL_MINOR_PROFILE: tuple[float, ...] = (
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17
)

# Major scale interval pattern from tonic: 0, 2, 4, 5, 7, 9, 11
MAJOR_SCALE_PCS: set[int] = {0, 2, 4, 5, 7, 9, 11}
# Harmonic/Natural minor combined diatonic set: 0, 2, 3, 5, 7, 8, 10, 11
MINOR_SCALE_PCS: set[int] = {0, 2, 3, 5, 7, 8, 10, 11}


@dataclass(frozen=True, slots=True)
class TonalPolicy:
    """Frozen policy parameters for Family A extraction."""

    local_window_measures: int = 8
    local_window_stride: int = 1
    major_profile: tuple[float, ...] = KRUMHANSL_MAJOR_PROFILE
    minor_profile: tuple[float, ...] = KRUMHANSL_MINOR_PROFILE

    def compute_policy_hash(self) -> str:
        canonical = {
            "local_window_measures": self.local_window_measures,
            "local_window_stride": self.local_window_stride,
            "major_profile": list(self.major_profile),
            "minor_profile": list(self.minor_profile),
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _pearson_correlation(v1: list[float], v2: tuple[float, ...]) -> float:
    """Compute Pearson correlation between two 12-dimensional vectors."""
    n = len(v1)
    m1 = sum(v1) / float(n)
    m2 = sum(v2) / float(n)
    num = sum((x - m1) * (y - m2) for x, y in zip(v1, v2, strict=True))
    den1 = sum((x - m1) ** 2 for x in v1)
    den2 = sum((y - m2) ** 2 for y in v2)
    if den1 <= 1e-12 or den2 <= 1e-12:
        return 0.0
    return num / math.sqrt(den1 * den2)


def estimate_key_from_pc_distribution(
    pc_dist: list[float],
    major_prof: tuple[float, ...] = KRUMHANSL_MAJOR_PROFILE,
    minor_prof: tuple[float, ...] = KRUMHANSL_MINOR_PROFILE,
) -> tuple[int, str, float]:
    """
    Returns (best_tonic_pc, 'major'|'minor', best_correlation).
    """
    if sum(pc_dist) <= 1e-12:
        return (0, "major", 0.0)

    best_corr = -2.0
    best_tonic = 0
    best_mode = "major"

    for tonic in range(12):
        # Rotate distribution so tonic aligns with index 0
        rotated = [pc_dist[(i + tonic) % 12] for i in range(12)]
        corr_maj = _pearson_correlation(rotated, major_prof)
        if corr_maj > best_corr:
            best_corr = corr_maj
            best_tonic = tonic
            best_mode = "major"

        corr_min = _pearson_correlation(rotated, minor_prof)
        if corr_min > best_corr:
            best_corr = corr_min
            best_tonic = tonic
            best_mode = "minor"

    return (best_tonic, best_mode, round(best_corr, 6))


def circle_of_fifths_distance(pc1: int, pc2: int) -> int:
    """Distance along the circle of fifths (0 to 6)."""
    # Fifth step: (pc * 7) % 12
    pos1 = (pc1 * 7) % 12
    pos2 = (pc2 * 7) % 12
    diff = abs(pos1 - pos2)
    return min(diff, 12 - diff)


def extract_tonal_features(
    score: CanonicalScore,
    policy: TonalPolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 8 Family A features for a canonical score."""
    if policy is None:
        policy = TonalPolicy()

    # Collect note events
    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    if not notes:
        return {
            "tonal_global_confidence": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_local_confidence_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_local_confidence_std": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_center_change_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_circle5_distance_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_circle5_distance_max": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_chromatic_duration_share": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "tonal_mode_switch_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # 1. Global duration-weighted PC distribution
    global_pc = [0.0] * 12
    total_duration = 0.0
    for n in notes:
        assert n.midi is not None
        pc = n.midi % 12
        dur = float(n.duration * 4)
        global_pc[pc] += dur
        total_duration += dur

    g_tonic, g_mode, g_corr = estimate_key_from_pc_distribution(
        global_pc, policy.major_profile, policy.minor_profile
    )

    # 2. Local measure-based sliding windows
    measures = score.measures
    measure_indices = sorted({m.measure_index for m in measures}) if measures else []
    max_m_idx = max(measure_indices) if measure_indices else 0
    min_m_idx = min(measure_indices) if measure_indices else 0
    span_measures = max(1, max_m_idx - min_m_idx + 1)

    # Group notes by measure
    notes_by_measure: dict[int, list[CanonicalScoreEvent]] = {}
    for n in notes:
        m_idx = n.measure_index
        notes_by_measure.setdefault(m_idx, []).append(n)

    local_windows_keys: list[tuple[int, str, float]] = []
    win_size = policy.local_window_measures
    stride = policy.local_window_stride

    if span_measures <= win_size:
        # Use single whole-piece window
        local_windows_keys.append((g_tonic, g_mode, g_corr))
    else:
        for start_m in range(min_m_idx, max_m_idx - win_size + 2, stride):
            end_m = start_m + win_size
            win_pc = [0.0] * 12
            for m in range(start_m, end_m):
                for n in notes_by_measure.get(m, []):
                    assert n.midi is not None
                    pc = n.midi % 12
                    dur = float(n.duration * 4)
                    win_pc[pc] += dur
            l_tonic, l_mode, l_corr = estimate_key_from_pc_distribution(
                win_pc, policy.major_profile, policy.minor_profile
            )
            local_windows_keys.append((l_tonic, l_mode, l_corr))

    # Calculate statistics across local windows
    l_corrs = [k[2] for k in local_windows_keys]
    l_corr_mean = sum(l_corrs) / float(len(l_corrs))
    if len(l_corrs) > 1:
        l_corr_var = sum((x - l_corr_mean) ** 2 for x in l_corrs) / float(len(l_corrs) - 1)
        l_corr_std = math.sqrt(l_corr_var)
    else:
        l_corr_std = 0.0

    # Key changes and circle of fifths transitions
    key_changes = 0
    mode_switches = 0
    c5_distances: list[int] = []

    for i in range(1, len(local_windows_keys)):
        prev_tonic, prev_mode, _ = local_windows_keys[i - 1]
        curr_tonic, curr_mode, _ = local_windows_keys[i]
        if prev_tonic != curr_tonic:
            key_changes += 1
            dist = circle_of_fifths_distance(prev_tonic, curr_tonic)
            c5_distances.append(dist)
        if prev_mode != curr_mode:
            mode_switches += 1

    change_rate = key_changes / float(span_measures)
    mode_rate = mode_switches / float(span_measures)

    if c5_distances:
        c5_mean = sum(c5_distances) / float(len(c5_distances))
        c5_max = max(c5_distances)
    else:
        c5_mean = 0.0
        c5_max = 0

    # Diatonic vs chromatic duration share relative to global key
    scale_set = MAJOR_SCALE_PCS if g_mode == "major" else MINOR_SCALE_PCS
    diatonic_pcs = {(p + g_tonic) % 12 for p in scale_set}
    chromatic_dur = sum(
        float(n.duration * 4)
        for n in notes
        if (n.midi is not None and (n.midi % 12) not in diatonic_pcs)
    )
    chromatic_share = (chromatic_dur / total_duration) if total_duration > 0 else 0.0

    return {
        "tonal_global_confidence": FeatureValue(round(g_corr, 6), AvailabilityStatus.AVAILABLE),
        "tonal_local_confidence_mean": FeatureValue(round(l_corr_mean, 6), AvailabilityStatus.AVAILABLE),
        "tonal_local_confidence_std": FeatureValue(
            round(l_corr_std, 6),
            AvailabilityStatus.AVAILABLE if len(l_corrs) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "tonal_center_change_rate": FeatureValue(
            round(change_rate, 6),
            AvailabilityStatus.AVAILABLE if len(local_windows_keys) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "tonal_circle5_distance_mean": FeatureValue(
            round(c5_mean, 6),
            AvailabilityStatus.AVAILABLE if c5_distances else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "tonal_circle5_distance_max": FeatureValue(
            round(float(c5_max), 6),
            AvailabilityStatus.AVAILABLE if c5_distances else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "tonal_chromatic_duration_share": FeatureValue(round(chromatic_share, 6), AvailabilityStatus.AVAILABLE),
        "tonal_mode_switch_rate": FeatureValue(
            round(mode_rate, 6),
            AvailabilityStatus.AVAILABLE if len(local_windows_keys) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
