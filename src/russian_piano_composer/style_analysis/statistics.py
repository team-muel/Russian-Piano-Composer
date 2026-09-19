"""
Feature-level descriptive statistics, coefficient stability, and piece-level effect size estimation for RC-010.

Computes composer-level medians (3 Russian vs 3 Control), exact 20-permutation feature contrasts,
raw exact p-values, Benjamini-Hochberg FDR q-values, logistic coefficient stability across 9 outer folds,
and descriptive piece-level effect sizes.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from russian_piano_composer.style_analysis.evaluation import ComposerHeldOutEvaluation
from russian_piano_composer.style_analysis.features import RoleBlindFeatureMatrix
from russian_piano_composer.style_analysis.permutation import (
    generate_all_composer_label_permutations,
)
from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    CONTROL_COMPOSERS,
    RUSSIAN_COMPOSERS,
)


@dataclass(frozen=True, slots=True)
class FeatureStatisticRecord:
    """
    Descriptive statistics and exact permutation test for a single predictor feature.
    """

    feature_id: str
    feature_family: str  # 'MODEL_A' or 'MODEL_B'
    russian_composer_mean: float
    control_composer_mean: float
    observed_contrast: float
    exact_p_value: float
    fdr_q_value: float
    median_coefficient: float
    min_coefficient: float
    max_coefficient: float
    positive_sign_count: int
    negative_sign_count: int
    is_directionally_stable: bool
    cliffs_delta_descriptive: float
    hedges_g_descriptive: float


def _median(vals: Sequence[float]) -> float:
    if not vals:
        return 0.0
    sorted_v = sorted(vals)
    n = len(sorted_v)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_v[mid])
    return (float(sorted_v[mid - 1]) + float(sorted_v[mid])) / 2.0


def compute_cliffs_delta(x_pos: Sequence[float], x_neg: Sequence[float]) -> float:
    """Compute Cliff's delta effect size between two samples."""
    if not x_pos or not x_neg:
        return 0.0
    more = 0
    less = 0
    for p in x_pos:
        for n in x_neg:
            if p > n:
                more += 1
            elif p < n:
                less += 1
    total = len(x_pos) * len(x_neg)
    return (more - less) / float(total) if total > 0 else 0.0


def compute_hedges_g(x_pos: Sequence[float], x_neg: Sequence[float]) -> float:
    """Compute Hedges' g standardized mean difference."""
    n1, n2 = len(x_pos), len(x_neg)
    if n1 < 2 or n2 < 2:
        return 0.0

    m1 = sum(x_pos) / float(n1)
    m2 = sum(x_neg) / float(n2)

    var1 = sum((x - m1) ** 2 for x in x_pos) / float(n1 - 1)
    var2 = sum((x - m2) ** 2 for x in x_neg) / float(n2 - 1)

    s_pooled = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / float(n1 + n2 - 2))
    if s_pooled <= 1e-12:
        return 0.0

    d = (m1 - m2) / s_pooled
    # J correction factor for small samples
    j_factor = 1.0 - (3.0 / float(4 * (n1 + n2) - 9))
    return d * j_factor


def compute_feature_statistics(
    matrix: RoleBlindFeatureMatrix,
    piece_composers: dict[str, str],
    evaluation_c: ComposerHeldOutEvaluation,
) -> tuple[FeatureStatisticRecord, ...]:
    """
    Compute comprehensive feature-level descriptive statistics, exact 20-permutation contrasts,
    FDR q-values, fold coefficient stability, and piece-level descriptive effect sizes.
    """
    n_features = len(matrix.feature_names)
    pid_to_comp = {pid: piece_composers[pid] for pid in matrix.piece_ids}

    # Pre-organize feature values by composer
    comp_feature_vals: dict[str, list[list[float]]] = {
        comp: [[] for _ in range(n_features)]
        for comp in ALL_COMPOSERS
    }

    for pid, row in zip(matrix.piece_ids, matrix.data, strict=True):
        comp = pid_to_comp[pid]
        for col_idx, val in enumerate(row):
            comp_feature_vals[comp][col_idx].append(val)

    # Compute composer-level medians for each feature
    comp_medians: list[dict[str, float]] = []
    for col_idx in range(n_features):
        meds = {}
        for comp in ALL_COMPOSERS:
            vals = comp_feature_vals[comp][col_idx]
            meds[comp] = _median(vals)
        comp_medians.append(meds)

    # Enumerate all 20 exact composer-label assignments
    assignments = generate_all_composer_label_permutations()

    raw_records: list[dict[str, Any]] = []

    for col_idx, feat_name in enumerate(matrix.feature_names):
        meds = comp_medians[col_idx]

        obs_rus_m = sum(meds[c] for c in RUSSIAN_COMPOSERS) / 3.0
        obs_ctrl_m = sum(meds[c] for c in CONTROL_COMPOSERS) / 3.0
        obs_diff = obs_rus_m - obs_ctrl_m

        # Compute exact contrast across all 20 assignments
        perm_diffs = []
        for assign in assignments:
            r_mean = sum(meds[c] for c in assign.russian_composers) / 3.0
            c_mean = sum(meds[c] for c in assign.control_composers) / 3.0
            perm_diffs.append(r_mean - c_mean)

        obs_abs_diff = abs(obs_diff)
        extreme_cnt = sum(1 for d in perm_diffs if abs(d) >= obs_abs_diff - 1e-12)
        exact_p = extreme_cnt / 20.0

        # Coefficient stability across 9 folds
        fold_coefs = [fr.coefs[col_idx] for fr in evaluation_c.fold_results]
        med_coef = _median(fold_coefs)
        min_coef = min(fold_coefs)
        max_coef = max(fold_coefs)
        pos_cnt = sum(1 for c in fold_coefs if c > 0)
        neg_cnt = sum(1 for c in fold_coefs if c < 0)
        is_stable = (pos_cnt >= 8 or neg_cnt >= 8)

        # Piece-level descriptive effect sizes
        rus_piece_vals = [
            val for pid, row in zip(matrix.piece_ids, matrix.data, strict=True)
            if pid_to_comp[pid] in RUSSIAN_COMPOSERS
            for val in [row[col_idx]]
        ]
        ctrl_piece_vals = [
            val for pid, row in zip(matrix.piece_ids, matrix.data, strict=True)
            if pid_to_comp[pid] in CONTROL_COMPOSERS
            for val in [row[col_idx]]
        ]

        c_delta = compute_cliffs_delta(rus_piece_vals, ctrl_piece_vals)
        h_g = compute_hedges_g(rus_piece_vals, ctrl_piece_vals)

        family = "MODEL_B" if feat_name.startswith("ctu_") else "MODEL_A"

        raw_records.append(
            {
                "feature_id": feat_name,
                "feature_family": family,
                "russian_composer_mean": round(obs_rus_m, 6),
                "control_composer_mean": round(obs_ctrl_m, 6),
                "observed_contrast": round(obs_diff, 6),
                "exact_p_value": round(exact_p, 4),
                "median_coefficient": round(med_coef, 6),
                "min_coefficient": round(min_coef, 6),
                "max_coefficient": round(max_coef, 6),
                "positive_sign_count": pos_cnt,
                "negative_sign_count": neg_cnt,
                "is_directionally_stable": is_stable,
                "cliffs_delta_descriptive": round(c_delta, 6),
                "hedges_g_descriptive": round(h_g, 6),
            }
        )

    # Benjamini-Hochberg FDR q-value adjustment
    sorted_by_p = sorted(enumerate(raw_records), key=lambda x: x[1]["exact_p_value"])
    m = float(len(raw_records))
    q_vals = [0.0] * len(raw_records)

    cum_min = 1.0
    for rank_idx, (orig_idx, rec) in reversed(list(enumerate(sorted_by_p, start=1))):
        p_val = rec["exact_p_value"]
        q_raw = (p_val * m) / float(rank_idx)
        cum_min = min(cum_min, q_raw)
        q_vals[orig_idx] = round(min(1.0, cum_min), 4)

    final_records: list[FeatureStatisticRecord] = []
    for idx, rec in enumerate(raw_records):
        final_records.append(
            FeatureStatisticRecord(
                feature_id=rec["feature_id"],
                feature_family=rec["feature_family"],
                russian_composer_mean=rec["russian_composer_mean"],
                control_composer_mean=rec["control_composer_mean"],
                observed_contrast=rec["observed_contrast"],
                exact_p_value=rec["exact_p_value"],
                fdr_q_value=q_vals[idx],
                median_coefficient=rec["median_coefficient"],
                min_coefficient=rec["min_coefficient"],
                max_coefficient=rec["max_coefficient"],
                positive_sign_count=rec["positive_sign_count"],
                negative_sign_count=rec["negative_sign_count"],
                is_directionally_stable=rec["is_directionally_stable"],
                cliffs_delta_descriptive=rec["cliffs_delta_descriptive"],
                hedges_g_descriptive=rec["hedges_g_descriptive"],
            )
        )

    return tuple(final_records)
