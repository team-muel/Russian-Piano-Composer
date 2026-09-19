"""
Family G: Normalized Temporal Trajectories for RC-011.

Implements 8-bin normalized score-position binning, linear trajectory slopes,
second-order polynomial curvatures, early-vs-late contrast, and trajectory volatility.
Strictly respects availability contract without silent imputation.
"""

import hashlib
import json
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from russian_piano_composer.domain.score import CanonicalScore, CanonicalScoreEvent, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue
from russian_piano_composer.structure_analysis.tonal import (
    MAJOR_SCALE_PCS,
    MINOR_SCALE_PCS,
    estimate_key_from_pc_distribution,
)

if TYPE_CHECKING:
    from fractions import Fraction


@dataclass(frozen=True, slots=True)
class TrajectoryPolicy:
    """Frozen policy parameters for Family G extraction."""

    bin_count: int = 8

    def compute_policy_hash(self) -> str:
        canonical = {"bin_count": self.bin_count}
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _linear_regression_slope(y_vals: list[float]) -> float:
    """Compute OLS linear slope against normalized x in [0, 1]."""
    n = len(y_vals)
    if n < 2:
        return 0.0
    x_vals = [i / float(n - 1) for i in range(n)]
    mean_x = sum(x_vals) / float(n)
    mean_y = sum(y_vals) / float(n)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_vals, y_vals, strict=True))
    den = sum((x - mean_x) ** 2 for x in x_vals)
    if den <= 1e-12:
        return 0.0
    return num / den


def _quadratic_curvature(y_vals: list[float]) -> float:
    """
    Compute quadratic curvature coefficient (second-order orthogonal polynomial).
    Positive = U-shaped (ends high, middle low), Negative = inverted-U (arch shape).
    """
    n = len(y_vals)
    if n < 3:
        return 0.0
    x_centered_sq = [((i / float(n - 1)) - 0.5) ** 2 for i in range(n)]
    mean_q = sum(x_centered_sq) / float(n)
    mean_y = sum(y_vals) / float(n)
    num = sum((q - mean_q) * (y - mean_y) for q, y in zip(x_centered_sq, y_vals, strict=True))
    den = sum((q - mean_q) ** 2 for q in x_centered_sq)
    if den <= 1e-12:
        return 0.0
    return num / den


def extract_trajectory_features(
    score: CanonicalScore,
    policy: TrajectoryPolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 8 Family G features for a canonical score."""
    if policy is None:
        policy = TrajectoryPolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1
    min_m_idx = min(m.measure_index for m in measures) if measures else 0

    if not notes:
        return {
            "traj_register_center_slope": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_register_span_slope": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_attack_density_slope": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_attack_density_curvature": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_chromaticity_slope": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_sonority_cardinality_slope": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_density_early_late_contrast": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "traj_register_volatility": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
        }

    # Partition notes into 8 normalized score-position bins
    n_bins = policy.bin_count
    bin_notes: list[list[CanonicalScoreEvent]] = [[] for _ in range(n_bins)]

    for n in notes:
        m_offset = n.measure_index - min_m_idx + float(n.offset_in_measure)
        norm_pos = min(0.999999, max(0.0, m_offset / float(span_measures)))
        b_idx = int(norm_pos * n_bins)
        bin_notes[b_idx].append(n)

    populated_bins_count = sum(1 for b in bin_notes if b)

    # If not all 8 bins are populated, return STRUCTURAL_ZERO explicitly without silent imputation
    if populated_bins_count < n_bins:
        reason = f"Only {populated_bins_count}/{n_bins} bins populated"
        return {
            "traj_register_center_slope": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_register_span_slope": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_attack_density_slope": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_attack_density_curvature": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_chromaticity_slope": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_sonority_cardinality_slope": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_density_early_late_contrast": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
            "traj_register_volatility": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, reason),
        }

    # Global key for chromaticity
    global_pc = [0.0] * 12
    for n in notes:
        if n.midi is not None:
            global_pc[n.midi % 12] += float(n.duration * 4)
    g_tonic, g_mode, _ = estimate_key_from_pc_distribution(global_pc)
    scale_set = MAJOR_SCALE_PCS if g_mode == "major" else MINOR_SCALE_PCS
    diatonic_pcs = {(p + g_tonic) % 12 for p in scale_set}

    # Compute base metrics per bin
    bin_reg_centers: list[float] = []
    bin_reg_spans: list[float] = []
    bin_attack_densities: list[float] = []
    bin_chromatic_shares: list[float] = []
    bin_pc_cardinalities: list[float] = []

    measures_per_bin = float(span_measures) / float(n_bins)

    for b_idx in range(n_bins):
        b_notes = bin_notes[b_idx]
        b_pitches = [n.midi for n in b_notes if n.midi is not None]
        bin_reg_centers.append(sum(b_pitches) / float(len(b_pitches)))

        # Onset grouping within bin
        b_onsets: dict[Fraction, list[CanonicalScoreEvent]] = {}
        for n in b_notes:
            b_onsets.setdefault(n.global_onset, []).append(n)

        onset_spans = []
        for on in b_onsets.values():
            on_pitches = [n.midi for n in on if n.midi is not None]
            if on_pitches:
                onset_spans.append(max(on_pitches) - min(on_pitches))

        bin_reg_spans.append((sum(onset_spans) / float(len(onset_spans))) if onset_spans else 0.0)
        bin_attack_densities.append(len(b_notes) / max(0.1, measures_per_bin))

        total_b_dur = sum(float(n.duration * 4) for n in b_notes)
        chrom_b_dur = sum(
            float(n.duration * 4)
            for n in b_notes
            if (n.midi is not None and (n.midi % 12) not in diatonic_pcs)
        )
        bin_chromatic_shares.append((chrom_b_dur / total_b_dur) if total_b_dur > 0 else 0.0)

        onset_cards = [
            len(set((n.midi % 12) for n in on if n.midi is not None))
            for on in b_onsets.values()
        ]
        bin_pc_cardinalities.append((sum(onset_cards) / float(len(onset_cards))) if onset_cards else 1.0)

    reg_slope = _linear_regression_slope(bin_reg_centers)
    span_slope = _linear_regression_slope(bin_reg_spans)
    dens_slope = _linear_regression_slope(bin_attack_densities)
    dens_curvature = _quadratic_curvature(bin_attack_densities)
    chrom_slope = _linear_regression_slope(bin_chromatic_shares)
    card_slope = _linear_regression_slope(bin_pc_cardinalities)

    # Early vs late contrast (bins 6-7 minus bins 0-1)
    late_dens = (bin_attack_densities[6] + bin_attack_densities[7]) / 2.0
    early_dens = (bin_attack_densities[0] + bin_attack_densities[1]) / 2.0
    contrast = late_dens - early_dens

    # Register volatility (std across the 8 bin centroids)
    mean_reg = sum(bin_reg_centers) / float(n_bins)
    var_reg = sum((x - mean_reg) ** 2 for x in bin_reg_centers) / float(n_bins - 1)
    reg_volatility = math.sqrt(var_reg)

    return {
        "traj_register_center_slope": FeatureValue(round(reg_slope, 6), AvailabilityStatus.AVAILABLE),
        "traj_register_span_slope": FeatureValue(round(span_slope, 6), AvailabilityStatus.AVAILABLE),
        "traj_attack_density_slope": FeatureValue(round(dens_slope, 6), AvailabilityStatus.AVAILABLE),
        "traj_attack_density_curvature": FeatureValue(round(dens_curvature, 6), AvailabilityStatus.AVAILABLE),
        "traj_chromaticity_slope": FeatureValue(round(chrom_slope, 6), AvailabilityStatus.AVAILABLE),
        "traj_sonority_cardinality_slope": FeatureValue(round(card_slope, 6), AvailabilityStatus.AVAILABLE),
        "traj_density_early_late_contrast": FeatureValue(round(contrast, 6), AvailabilityStatus.AVAILABLE),
        "traj_register_volatility": FeatureValue(round(reg_volatility, 6), AvailabilityStatus.AVAILABLE),
    }
