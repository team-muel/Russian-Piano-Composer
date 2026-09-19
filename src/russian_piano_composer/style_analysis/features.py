"""
Role-blind feature extraction and feature matrix construction for RC-010.

Implements MODEL_A (RC-009A Category A piece features), MODEL_B (CTU Style Feature Schema V1),
and MODEL_C (MODEL_A + MODEL_B combined). Feature matrices strictly exclude metadata,
composer identity, title, repository paths, and role annotations.
"""

import hashlib
import json
import math
from dataclasses import dataclass

from russian_piano_composer.ctu.discovery import discover_ctus_for_score
from russian_piano_composer.ctu.models import CTUCandidate
from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.features import FEATURE_REGISTRY, extract_piece_features
from russian_piano_composer.features.policy import FeatureExtractionPolicy

CTU_STYLE_FEATURE_SCHEMA_VERSION: int = 1

FORBIDDEN_METADATA_TERMS: set[str] = {
    "composer",
    "composer_name",
    "corpus_role",
    "corpus_id",
    "GENERATIVE_RUSSIAN",
    "CONTROL_NON_RUSSIAN",
    "source_repository",
    "source_relative_path",
    "title",
    "rights_status",
    "generative_eligible",
}


@dataclass(frozen=True, slots=True)
class CTUStyleFeatureDefinition:
    """Descriptor metadata for CTU-style structural features."""

    feature_id: str
    formula: str
    observation_unit: str
    normalization: str
    missing_value_rule: str
    provenance: str = "ENGINEERING_HEURISTIC"
    known_confounds: str = "retained CTU count"
    semantic_version: str = "v1.0"


CTU_STYLE_FEATURE_REGISTRY: tuple[CTUStyleFeatureDefinition, ...] = (
    CTUStyleFeatureDefinition(
        feature_id="ctu_discovery_score_mean",
        formula="mean(ctu.discovery_score)",
        observation_unit="ctu_candidate",
        normalization="retained_ctu_count",
        missing_value_rule="0.0 if no retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_discovery_score_std",
        formula="std(ctu.discovery_score)",
        observation_unit="ctu_candidate",
        normalization="retained_ctu_count",
        missing_value_rule="0.0 if <2 retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_discovery_score_max",
        formula="max(ctu.discovery_score)",
        observation_unit="ctu_candidate",
        normalization="none",
        missing_value_rule="0.0 if no retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_span_length_mean",
        formula="mean(ctu.span.measure_span_count)",
        observation_unit="ctu_candidate",
        normalization="retained_ctu_count",
        missing_value_rule="0.0 if no retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_span_length_std",
        formula="std(ctu.span.measure_span_count)",
        observation_unit="ctu_candidate",
        normalization="retained_ctu_count",
        missing_value_rule="0.0 if <2 retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_melodic_abs_interval_mean",
        formula="mean(|delta_pitch|)",
        observation_unit="melodic_interval_event",
        normalization="total_ctu_melodic_intervals",
        missing_value_rule="0.0 if no melodic intervals",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_melodic_interval_diversity",
        formula="count(distinct(delta_pitch)) / total(delta_pitch)",
        observation_unit="melodic_interval_event",
        normalization="total_ctu_melodic_intervals",
        missing_value_rule="0.0 if no melodic intervals",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_rhythm_ratio_abs_deviation_mean",
        formula="mean(|r_i - 1.0|)",
        observation_unit="ioi_rhythmic_ratio",
        normalization="total_ctu_rhythmic_ratios",
        missing_value_rule="0.0 if no rhythmic ratios",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_texture_attack_mean",
        formula="mean(simultaneity_attack_count)",
        observation_unit="onset_simultaneity",
        normalization="total_ctu_onsets",
        missing_value_rule="0.0 if no texture profile",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_texture_attack_std",
        formula="std(simultaneity_attack_count)",
        observation_unit="onset_simultaneity",
        normalization="total_ctu_onsets",
        missing_value_rule="0.0 if <2 texture profile onsets",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_pitchclass_entropy",
        formula="-sum(p_i * log2(p_i))",
        observation_unit="sounding_midi_pitchclass",
        normalization="total_ctu_attacks",
        missing_value_rule="0.0 if no pitch-class attacks",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_pitchclass_max_share",
        formula="max(p_i)",
        observation_unit="sounding_midi_pitchclass",
        normalization="total_ctu_attacks",
        missing_value_rule="0.0 if no pitch-class attacks",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_active_voice_stream_mean",
        formula="mean(count(active_voice_streams))",
        observation_unit="ctu_candidate",
        normalization="retained_ctu_count",
        missing_value_rule="0.0 if no retained CTUs",
    ),
    CTUStyleFeatureDefinition(
        feature_id="ctu_attack_density_per_measure_mean",
        formula="mean(total_ctu_attacks / measure_span_count)",
        observation_unit="ctu_candidate",
        normalization="measure_span_count",
        missing_value_rule="0.0 if no retained CTUs",
    ),
)


def compute_style_feature_schema_hash() -> str:
    """
    Deterministic SHA-256 hash of CTU Style Feature Schema V1.
    """
    canonical = {
        "version": CTU_STYLE_FEATURE_SCHEMA_VERSION,
        "descriptors": [
            {
                "feature_id": d.feature_id,
                "formula": d.formula,
                "observation_unit": d.observation_unit,
                "normalization": d.normalization,
                "missing_value_rule": d.missing_value_rule,
            }
            for d in sorted(CTU_STYLE_FEATURE_REGISTRY, key=lambda x: x.feature_id)
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def extract_ctu_style_features(ctus: tuple[CTUCandidate, ...]) -> dict[str, float]:
    """
    Extract 14 normalized CTU-style features from retained CTUs of a piece.
    """
    if not ctus:
        return {d.feature_id: 0.0 for d in CTU_STYLE_FEATURE_REGISTRY}

    disc_scores = [float(c.discovery_score) for c in ctus]
    spans = [float(c.span.measure_span_count) for c in ctus]

    disc_mean = sum(disc_scores) / len(disc_scores)
    disc_max = max(disc_scores)
    if len(disc_scores) > 1:
        disc_var = sum((x - disc_mean) ** 2 for x in disc_scores) / (len(disc_scores) - 1)
        disc_std = math.sqrt(disc_var)
    else:
        disc_std = 0.0

    span_mean = sum(spans) / len(spans)
    if len(spans) > 1:
        span_var = sum((x - span_mean) ** 2 for x in spans) / (len(spans) - 1)
        span_std = math.sqrt(span_var)
    else:
        span_std = 0.0

    all_intervals: list[int] = []
    for c in ctus:
        for stream in c.representation.melodic_intervals:
            all_intervals.extend(stream)

    if all_intervals:
        melodic_abs_mean = sum(abs(iv) for iv in all_intervals) / float(len(all_intervals))
        melodic_diversity = len(set(all_intervals)) / float(len(all_intervals))
    else:
        melodic_abs_mean = 0.0
        melodic_diversity = 0.0

    all_ratios: list[float] = []
    for c in ctus:
        all_ratios.extend(float(r) for r in c.representation.rhythmic_ratios)

    if all_ratios:
        rhythm_dev_mean = sum(abs(r - 1.0) for r in all_ratios) / float(len(all_ratios))
    else:
        rhythm_dev_mean = 0.0

    all_texture: list[int] = []
    for c in ctus:
        all_texture.extend(c.representation.texture_profile)

    if all_texture:
        tex_mean = sum(all_texture) / float(len(all_texture))
        if len(all_texture) > 1:
            tex_var = sum((x - tex_mean) ** 2 for x in all_texture) / float(len(all_texture) - 1)
            tex_std = math.sqrt(tex_var)
        else:
            tex_std = 0.0
    else:
        tex_mean = 0.0
        tex_std = 0.0

    summed_pc = [0] * 12
    for c in ctus:
        for i in range(12):
            summed_pc[i] += c.representation.pitch_class_counts[i]

    total_pc = sum(summed_pc)
    if total_pc > 0:
        pc_probs = [cnt / float(total_pc) for cnt in summed_pc]
        pc_entropy = -sum(p * math.log2(p) for p in pc_probs if p > 0)
        pc_max_share = max(pc_probs)
    else:
        pc_entropy = 0.0
        pc_max_share = 0.0

    active_streams = [float(len(c.representation.melodic_intervals)) for c in ctus]
    active_stream_mean = sum(active_streams) / len(active_streams)

    densities = [
        sum(c.representation.texture_profile) / float(max(1, c.span.measure_span_count))
        for c in ctus
    ]
    density_mean = sum(densities) / len(densities)

    return {
        "ctu_discovery_score_mean": round(disc_mean, 6),
        "ctu_discovery_score_std": round(disc_std, 6),
        "ctu_discovery_score_max": round(disc_max, 6),
        "ctu_span_length_mean": round(span_mean, 6),
        "ctu_span_length_std": round(span_std, 6),
        "ctu_melodic_abs_interval_mean": round(melodic_abs_mean, 6),
        "ctu_melodic_interval_diversity": round(melodic_diversity, 6),
        "ctu_rhythm_ratio_abs_deviation_mean": round(rhythm_dev_mean, 6),
        "ctu_texture_attack_mean": round(tex_mean, 6),
        "ctu_texture_attack_std": round(tex_std, 6),
        "ctu_pitchclass_entropy": round(pc_entropy, 6),
        "ctu_pitchclass_max_share": round(pc_max_share, 6),
        "ctu_active_voice_stream_mean": round(active_stream_mean, 6),
        "ctu_attack_density_per_measure_mean": round(density_mean, 6),
    }


@dataclass(frozen=True, slots=True)
class CTUStyleFeatureSchema:
    """Schema descriptor binding CTU style features for MODEL_B and MODEL_C."""

    schema_version: int = CTU_STYLE_FEATURE_SCHEMA_VERSION
    feature_definitions: tuple[CTUStyleFeatureDefinition, ...] = CTU_STYLE_FEATURE_REGISTRY


@dataclass(frozen=True, slots=True)
class RoleBlindFeatureMatrix:
    """
    Immutable role-blind feature matrix across canonical scores.
    Strictly contains no composer, title, corpus role, metadata, or path predictors.
    """

    piece_ids: tuple[str, ...]
    feature_names: tuple[str, ...]
    data: tuple[tuple[float, ...], ...]
    model_name: str
    manifest_hash: str
    schema_hash: str

    def __post_init__(self) -> None:
        if not self.piece_ids:
            raise ValueError("RoleBlindFeatureMatrix must contain piece_ids.")
        if not self.feature_names:
            raise ValueError("RoleBlindFeatureMatrix must contain feature_names.")
        if len(self.data) != len(self.piece_ids):
            raise ValueError("data row count must match piece_ids length.")
        for col_name in self.feature_names:
            for term in FORBIDDEN_METADATA_TERMS:
                if term in col_name:
                    raise ValueError(f"Metadata term '{term}' forbidden in predictor column '{col_name}'.")

    def compute_matrix_hash(self) -> str:
        """
        Deterministic SHA-256 hash of role-blind matrix contents.
        """
        canonical = {
            "model_name": self.model_name,
            "manifest_hash": self.manifest_hash,
            "schema_hash": self.schema_hash,
            "feature_names": list(self.feature_names),
            "rows": [
                {
                    "piece_id": pid,
                    "values": list(row),
                }
                for pid, row in zip(self.piece_ids, self.data, strict=True)
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def build_role_blind_feature_matrices(
    scores_by_id: dict[str, CanonicalScore],
    manifest_hash: str,
    disc_policy: CTUDiscoveryPolicy | None = None,
    feat_policy: FeatureExtractionPolicy | None = None,
) -> dict[str, RoleBlindFeatureMatrix]:
    """
    Construct role-blind feature matrices for MODEL_A, MODEL_B, and MODEL_C.
    Guaranteed role-blind: extracted strictly before composer/role labels are attached.
    """
    if disc_policy is None:
        disc_policy = CTUDiscoveryPolicy()
    if feat_policy is None:
        feat_policy = FeatureExtractionPolicy()

    cat_a_defs = tuple(fd for fd in FEATURE_REGISTRY if fd.validity_category == "A")
    cat_a_names = tuple(sorted([fd.feature_id for fd in cat_a_defs]))
    ctu_names = tuple(sorted([d.feature_id for d in CTU_STYLE_FEATURE_REGISTRY]))
    model_c_names = cat_a_names + ctu_names

    sorted_piece_ids = tuple(sorted(scores_by_id.keys()))

    model_a_rows: list[tuple[float, ...]] = []
    model_b_rows: list[tuple[float, ...]] = []
    model_c_rows: list[tuple[float, ...]] = []

    import sys
    n_total = len(sorted_piece_ids)
    for idx, pid in enumerate(sorted_piece_ids, start=1):
        if idx == 1 or idx % 20 == 0 or idx == n_total:
            print(f"  Extracting features: {idx}/{n_total} pieces processed...")
            sys.stdout.flush()
        score = scores_by_id[pid]
        pfs = extract_piece_features(score, manifest_hash=manifest_hash, policy=feat_policy)

        # MODEL_A values
        a_vals = tuple(float(pfs.features.get(name) or 0.0) for name in cat_a_names)

        # MODEL_B values (from frozen RC-009B retained CTUs)
        disc_res = discover_ctus_for_score(score, manifest_hash=manifest_hash, policy=disc_policy)
        ctu_feats = extract_ctu_style_features(disc_res.retained_ctus)
        b_vals = tuple(ctu_feats.get(name, 0.0) for name in ctu_names)

        c_vals = a_vals + b_vals

        model_a_rows.append(a_vals)
        model_b_rows.append(b_vals)
        model_c_rows.append(c_vals)

    schema_hash_ctu = compute_style_feature_schema_hash()

    matrix_a = RoleBlindFeatureMatrix(
        piece_ids=sorted_piece_ids,
        feature_names=cat_a_names,
        data=tuple(model_a_rows),
        model_name="MODEL_A",
        manifest_hash=manifest_hash,
        schema_hash=schema_hash_ctu,
    )

    matrix_b = RoleBlindFeatureMatrix(
        piece_ids=sorted_piece_ids,
        feature_names=ctu_names,
        data=tuple(model_b_rows),
        model_name="MODEL_B",
        manifest_hash=manifest_hash,
        schema_hash=schema_hash_ctu,
    )

    matrix_c = RoleBlindFeatureMatrix(
        piece_ids=sorted_piece_ids,
        feature_names=model_c_names,
        data=tuple(model_c_rows),
        model_name="MODEL_C",
        manifest_hash=manifest_hash,
        schema_hash=schema_hash_ctu,
    )

    return {
        "MODEL_A": matrix_a,
        "MODEL_B": matrix_b,
        "MODEL_C": matrix_c,
    }
