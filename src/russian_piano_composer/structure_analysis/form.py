"""
Family D: Formal Recurrence & Sectional Architecture for RC-011.

Implements measure-level Self-Similarity Matrices (SSM), Foote novelty curves,
recapitulation return proxies, and CTU-derived positional recurrence features.
"""

import hashlib
import json
import math
from dataclasses import dataclass

from russian_piano_composer.ctu.models import CTUCandidate
from russian_piano_composer.domain.score import CanonicalScore, EventKind
from russian_piano_composer.structure_analysis.schema import AvailabilityStatus, FeatureValue


@dataclass(frozen=True, slots=True)
class FormPolicy:
    """Frozen policy parameters for Family D extraction."""

    similarity_threshold: float = 0.80
    novelty_kernel_size: int = 4
    late_return_start_fraction: float = 0.70
    exposition_end_fraction: float = 0.20

    def compute_policy_hash(self) -> str:
        canonical = {
            "similarity_threshold": self.similarity_threshold,
            "novelty_kernel_size": self.novelty_kernel_size,
            "late_return_start_fraction": self.late_return_start_fraction,
            "exposition_end_fraction": self.exposition_end_fraction,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Cosine similarity between two non-negative vectors."""
    dot = sum(x * y for x, y in zip(v1, v2, strict=True))
    norm1 = math.sqrt(sum(x * x for x in v1))
    norm2 = math.sqrt(sum(y * y for y in v2))
    if norm1 <= 1e-12 or norm2 <= 1e-12:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


def extract_form_features(
    score: CanonicalScore,
    retained_ctus: tuple[CTUCandidate, ...] = (),
    policy: FormPolicy | None = None,
) -> dict[str, FeatureValue]:
    """Extract the 8 Family D features for a canonical score."""
    if policy is None:
        policy = FormPolicy()

    notes = [
        ev for ev in score.events
        if ev.event_kind == EventKind.NOTE and ev.pitch is not None and ev.midi is not None
    ]

    measures = score.measures
    span_measures = max(1, max(m.measure_index for m in measures) - min(m.measure_index for m in measures) + 1) if measures else 1
    measure_indices = sorted({m.measure_index for m in measures}) if measures else []

    if not notes or not measure_indices:
        return {
            "form_ssm_recurrence_density": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "form_novelty_peak_rate": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "form_novelty_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "form_return_late_strength": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "form_recurrence_distance_mean": FeatureValue(0.0, AvailabilityStatus.UNAVAILABLE, "No sounding notes"),
            "form_ctu_first_occurrence_mean": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, "No CTUs"),
            "form_ctu_recurrence_dispersion": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, "No CTUs"),
            "form_ctu_late_return_presence": FeatureValue(0.0, AvailabilityStatus.STRUCTURAL_ZERO, "No CTUs"),
        }

    # 1. Build measure-level feature embeddings (12-PC duration vector + density)
    measure_embeddings: dict[int, list[float]] = {m: [0.0] * 13 for m in measure_indices}
    for n in notes:
        m_idx = n.measure_index
        if m_idx in measure_embeddings and n.midi is not None:
            pc = n.midi % 12
            dur = float(n.duration * 4)
            measure_embeddings[m_idx][pc] += dur
            measure_embeddings[m_idx][12] += 1.0  # note attack count

    ordered_embeddings = [measure_embeddings[m] for m in measure_indices]
    n_embeds = len(ordered_embeddings)

    # 2. Build Self-Similarity Matrix (SSM)
    ssm: list[list[float]] = [[0.0] * n_embeds for _ in range(n_embeds)]
    recurrence_count = 0
    recurrence_distances: list[int] = []
    total_off_diag = 0

    for i in range(n_embeds):
        for j in range(n_embeds):
            sim = _cosine_similarity(ordered_embeddings[i], ordered_embeddings[j])
            ssm[i][j] = sim
            if abs(i - j) > 1:
                total_off_diag += 1
                if sim >= policy.similarity_threshold:
                    recurrence_count += 1
                    recurrence_distances.append(abs(i - j))

    rec_density = (recurrence_count / float(total_off_diag)) if total_off_diag > 0 else 0.0
    rec_dist_mean = (sum(recurrence_distances) / float(len(recurrence_distances))) if recurrence_distances else 0.0

    # 3. Late Formal Return Strength (ABA return proxy)
    n_expo = max(1, int(n_embeds * policy.exposition_end_fraction))
    n_recap_start = int(n_embeds * policy.late_return_start_fraction)
    late_return_sims = []
    for i in range(min(n_expo, n_embeds)):
        for j in range(max(0, n_recap_start), n_embeds):
            late_return_sims.append(ssm[i][j])

    late_return_strength = max(late_return_sims) if late_return_sims else 0.0

    # 4. Foote Novelty Curve using checkerboard kernel
    k_size = policy.novelty_kernel_size
    novelty_curve: list[float] = []
    if 2 * k_size <= n_embeds:
        for i in range(k_size, n_embeds - k_size):
            # Compute cross-similarity vs within-similarity across kernel quadrants
            quad1 = sum(ssm[i - k][i - q] for k in range(1, k_size + 1) for q in range(1, k_size + 1))
            quad2 = sum(ssm[i + k][i + q] for k in range(1, k_size + 1) for q in range(1, k_size + 1))
            cross1 = sum(ssm[i - k][i + q] for k in range(1, k_size + 1) for q in range(1, k_size + 1))
            cross2 = sum(ssm[i + k][i - q] for k in range(1, k_size + 1) for q in range(1, k_size + 1))
            nov = (quad1 + quad2 - cross1 - cross2) / float(2 * k_size * k_size)
            novelty_curve.append(max(0.0, nov))

    novelty_mean = (sum(novelty_curve) / float(len(novelty_curve))) if novelty_curve else 0.0

    # Novelty peaks (simple local maxima above mean)
    novelty_peaks = 0
    for idx in range(1, len(novelty_curve) - 1):
        if (
            novelty_curve[idx] > novelty_curve[idx - 1]
            and novelty_curve[idx] > novelty_curve[idx + 1]
            and novelty_curve[idx] > novelty_mean
        ):
            novelty_peaks += 1
    novelty_peak_rate = novelty_peaks / float(span_measures)

    # 5. CTU-derived formal features
    if retained_ctus:
        first_positions = [
            float(c.span.start.measure_index - min(measure_indices)) / float(max(1, span_measures))
            for c in retained_ctus
        ]
        first_occ_mean = sum(first_positions) / float(len(first_positions))

        # Check late return in final 30% of piece
        has_late_return = 1.0 if any(pos >= policy.late_return_start_fraction for pos in first_positions) else 0.0

        if len(first_positions) > 1:
            mean_pos = sum(first_positions) / float(len(first_positions))
            pos_var = sum((x - mean_pos) ** 2 for x in first_positions) / float(len(first_positions) - 1)
            pos_disp = math.sqrt(pos_var)
        else:
            pos_disp = 0.0
    else:
        first_occ_mean = 0.0
        pos_disp = 0.0
        has_late_return = 0.0

    return {
        "form_ssm_recurrence_density": FeatureValue(round(rec_density, 6), AvailabilityStatus.AVAILABLE),
        "form_novelty_peak_rate": FeatureValue(round(novelty_peak_rate, 6), AvailabilityStatus.AVAILABLE),
        "form_novelty_mean": FeatureValue(round(novelty_mean, 6), AvailabilityStatus.AVAILABLE),
        "form_return_late_strength": FeatureValue(round(late_return_strength, 6), AvailabilityStatus.AVAILABLE),
        "form_recurrence_distance_mean": FeatureValue(
            round(rec_dist_mean, 6),
            AvailabilityStatus.AVAILABLE if recurrence_distances else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "form_ctu_first_occurrence_mean": FeatureValue(
            round(first_occ_mean, 6),
            AvailabilityStatus.AVAILABLE if retained_ctus else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "form_ctu_recurrence_dispersion": FeatureValue(
            round(pos_disp, 6),
            AvailabilityStatus.AVAILABLE if len(retained_ctus) > 1 else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
        "form_ctu_late_return_presence": FeatureValue(
            round(has_late_return, 6),
            AvailabilityStatus.AVAILABLE if retained_ctus else AvailabilityStatus.STRUCTURAL_ZERO,
        ),
    }
