"""
Core schema, descriptor types, and registry for RC-011 Structural Music Representation.
"""

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


class FeatureFamily(StrEnum):
    """The 7 structural music representation families for RC-011."""

    TONAL = "TONAL"
    SONORITY = "SONORITY"
    CADENCE = "CADENCE"
    FORM = "FORM"
    VOICE_LEADING = "VOICE_LEADING"
    TEXTURE_REGISTER = "TEXTURE_REGISTER"
    TEMPORAL_TRAJECTORY = "TEMPORAL_TRAJECTORY"


class Provenance(StrEnum):
    """Epistemological classification of structural descriptors."""

    OBSERVED = "OBSERVED"
    LITERATURE = "LITERATURE"
    HYPOTHESIS = "HYPOTHESIS"
    ENGINEERING_HEURISTIC = "ENGINEERING_HEURISTIC"


class InvarianceClass(StrEnum):
    """Transformation behavior of structural features under musical mappings."""

    INVARIANT = "INVARIANT"
    EQUIVARIANT = "EQUIVARIANT"
    SENSITIVE_BY_DESIGN = "SENSITIVE_BY_DESIGN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class TransformationType(StrEnum):
    """Transformation types evaluated in metamorphic invariance testing."""

    TRANSPOSITION = "TRANSPOSITION"
    TIME_DILATION = "TIME_DILATION"
    PIECE_ID_RENAME = "PIECE_ID_RENAME"
    SOURCE_PATH_RENAME = "SOURCE_PATH_RENAME"
    VOICE_ID_RENAME = "VOICE_ID_RENAME"
    STAFF_SWAP = "STAFF_SWAP"


class AvailabilityStatus(StrEnum):
    """Explicit availability status distinguishing valid zeros from missing preconditions."""

    AVAILABLE = "AVAILABLE"
    STRUCTURAL_ZERO = "STRUCTURAL_ZERO"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class FeatureValue:
    """A computed feature value with explicit availability tracking."""

    value: float
    status: AvailabilityStatus
    reason: str = ""

    def __post_init__(self) -> None:
        if self.status == AvailabilityStatus.UNAVAILABLE and self.value != 0.0:
            raise ValueError(f"UNAVAILABLE feature must have value 0.0, got {self.value}")


@dataclass(frozen=True, slots=True)
class StructuralFeatureDefinition:
    """Full descriptor metadata for a structural feature in RC-011."""

    feature_id: str
    family: FeatureFamily
    formula: str
    observation_unit: str
    aggregation: str
    normalization: str
    availability_rule: str
    missing_value_rule: str
    invariance_class: InvarianceClass
    provenance: Provenance
    known_confounds: str
    interpretation_limitations: str
    semantic_version: str = "v1.0"


# Frozen 56-feature catalog for RC-011 Structural Music Representation V1
STRUCTURAL_FEATURE_CATALOG: tuple[StructuralFeatureDefinition, ...] = (
    # FAMILY A: TONAL (8 features)
    StructuralFeatureDefinition(
        feature_id="tonal_global_confidence",
        family=FeatureFamily.TONAL,
        formula="max_k(corr(pitch_class_duration_dist, krumhansl_profile_k))",
        observation_unit="entire_score",
        aggregation="max",
        normalization="none",
        availability_rule="available if >= 1 sounding note",
        missing_value_rule="UNAVAILABLE if 0 sounding notes",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="piece duration, extreme chromaticism",
        interpretation_limitations="Correlation to static profile, not perceptual cognitive key",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_local_confidence_mean",
        family=FeatureFamily.TONAL,
        formula="mean(max_k(corr(window_pc_dist, krumhansl_profile_k)))",
        observation_unit="8_measure_window",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="window size boundary effects",
        interpretation_limitations="Smooths over rapid intra-window modulations",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_local_confidence_std",
        family=FeatureFamily.TONAL,
        formula="std(max_k(corr(window_pc_dist, krumhansl_profile_k)))",
        observation_unit="8_measure_window",
        aggregation="std",
        normalization="none",
        availability_rule="available if >= 2 windows",
        missing_value_rule="STRUCTURAL_ZERO if 1 window",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="piece length",
        interpretation_limitations="Measures tonal stability variance across windows",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_center_change_rate",
        family=FeatureFamily.TONAL,
        formula="count(local_key_changes) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 2 windows",
        missing_value_rule="STRUCTURAL_ZERO if < 2 windows",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="window stride, ambiguity in minor keys",
        interpretation_limitations="Proxy for modulation tempo",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_circle5_distance_mean",
        family=FeatureFamily.TONAL,
        formula="mean(circle_of_fifths_distance(key_t, key_{t-1}))",
        observation_unit="key_transition",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 key change",
        missing_value_rule="STRUCTURAL_ZERO if 0 key changes",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="enharmonic equivalence assumption",
        interpretation_limitations="Assumes 12-TET circle of fifths geometry",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_circle5_distance_max",
        family=FeatureFamily.TONAL,
        formula="max(circle_of_fifths_distance(key_t, key_{t-1}))",
        observation_unit="key_transition",
        aggregation="max",
        normalization="none",
        availability_rule="available if >= 1 key change",
        missing_value_rule="STRUCTURAL_ZERO if 0 key changes",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="enharmonic spelling ambiguities",
        interpretation_limitations="Captures tritone/distant excursions",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_chromatic_duration_share",
        family=FeatureFamily.TONAL,
        formula="duration(non_diatonic_pcs_rel_global_key) / total_sounding_duration",
        observation_unit="pitch_event",
        aggregation="sum_ratio",
        normalization="total_duration",
        availability_rule="available if >= 1 sounding note",
        missing_value_rule="UNAVAILABLE if 0 sounding notes",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="inferred global key accuracy",
        interpretation_limitations="Sensitive to global key estimation errors",
    ),
    StructuralFeatureDefinition(
        feature_id="tonal_mode_switch_rate",
        family=FeatureFamily.TONAL,
        formula="count(major_minor_mode_switches) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 2 windows",
        missing_value_rule="STRUCTURAL_ZERO if < 2 windows",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="parallel/relative mode ambiguity",
        interpretation_limitations="Captures modal interchange frequency",
    ),
    # FAMILY B: SONORITY & HARMONIC MOTION (8 features)
    StructuralFeatureDefinition(
        feature_id="sonority_pc_cardinality_mean",
        family=FeatureFamily.SONORITY,
        formula="mean(len(distinct_sounding_pitch_classes_at_onset))",
        observation_unit="onset_timepoint",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="pedal point / sustain overlap",
        interpretation_limitations="Measures vertical harmonic thickness",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_pc_cardinality_std",
        family=FeatureFamily.SONORITY,
        formula="std(len(distinct_sounding_pitch_classes_at_onset))",
        observation_unit="onset_timepoint",
        aggregation="std",
        normalization="none",
        availability_rule="available if >= 2 onsets",
        missing_value_rule="STRUCTURAL_ZERO if 1 onset",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="texture variety",
        interpretation_limitations="Measures vertical complexity variation",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_change_rate",
        family=FeatureFamily.SONORITY,
        formula="count(distinct_pc_set_transitions) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="non-harmonic passing tones",
        interpretation_limitations="Harmonic rhythm proxy without functional reduction",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_stable_duration_share",
        family=FeatureFamily.SONORITY,
        formula="sum(duration(top_3_most_frequent_pc_sets)) / total_sounding_duration",
        observation_unit="entire_score",
        aggregation="sum_ratio",
        normalization="total_duration",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="piece length",
        interpretation_limitations="Harmonic vocabulary concentration proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_ic1_semitone_share",
        family=FeatureFamily.SONORITY,
        formula="count(sounding_dyads_with_ic_1) / total_sounding_dyads",
        observation_unit="sounding_dyad",
        aggregation="sum_ratio",
        normalization="total_dyads",
        availability_rule="available if >= 1 vertical dyad",
        missing_value_rule="STRUCTURAL_ZERO if 0 dyads",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="cluster voicing density",
        interpretation_limitations="Dissonance intensity indicator",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_ic6_tritone_share",
        family=FeatureFamily.SONORITY,
        formula="count(sounding_dyads_with_ic_6) / total_sounding_dyads",
        observation_unit="sounding_dyad",
        aggregation="sum_ratio",
        normalization="total_dyads",
        availability_rule="available if >= 1 vertical dyad",
        missing_value_rule="STRUCTURAL_ZERO if 0 dyads",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="dominant seventh chord frequency",
        interpretation_limitations="Tritone tension indicator",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_bass_interval_variety",
        family=FeatureFamily.SONORITY,
        formula="count(distinct(bass_relative_intervals)) / max(1, count(onsets))",
        observation_unit="onset_timepoint",
        aggregation="ratio",
        normalization="onset_count",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="voicing span",
        interpretation_limitations="Harmonic color diversity over bass note",
    ),
    StructuralFeatureDefinition(
        feature_id="sonority_harmonic_rhythm_volatility",
        family=FeatureFamily.SONORITY,
        formula="std(measures_between_pc_set_changes)",
        observation_unit="harmonic_interval",
        aggregation="std",
        normalization="none",
        availability_rule="available if >= 2 pc set changes",
        missing_value_rule="STRUCTURAL_ZERO if < 2 changes",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="rubato / tempo markings",
        interpretation_limitations="Irregularity of harmonic pacing",
    ),
    # FAMILY C: CADENTIAL & BOUNDARY PROXIES (6 features)
    StructuralFeatureDefinition(
        feature_id="cadence_boundary_candidate_rate",
        family=FeatureFamily.CADENCE,
        formula="count(boundary_candidates) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="fermatas, rest patterns",
        interpretation_limitations="Rhythmic boundary proxy, not syntactic phrase end",
    ),
    StructuralFeatureDefinition(
        feature_id="cadence_boundary_strength_mean",
        family=FeatureFamily.CADENCE,
        formula="mean(boundary_strength_scores)",
        observation_unit="boundary_candidate",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 boundary candidate",
        missing_value_rule="STRUCTURAL_ZERO if 0 candidates",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="texture shifts",
        interpretation_limitations="Acoustic boundary salience",
    ),
    StructuralFeatureDefinition(
        feature_id="cadence_tonic_resolution_rate",
        family=FeatureFamily.CADENCE,
        formula="count(boundary_5_to_1_resolutions) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="bass voice identification accuracy",
        interpretation_limitations="Syntactic closure proxy relative to local key",
    ),
    StructuralFeatureDefinition(
        feature_id="cadence_dominant_tonic_proxy_rate",
        family=FeatureFamily.CADENCE,
        formula="count(dominant_to_tonic_sonority_transitions_at_boundary) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="inversions, embellishments",
        interpretation_limitations="Heuristic V-I progression proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="cadence_deceptive_proxy_rate",
        family=FeatureFamily.CADENCE,
        formula="count(boundary_5_to_6_resolutions) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="submediant chord inversions",
        interpretation_limitations="Deceptive cadence motion proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="cadence_resolution_strength_mean",
        family=FeatureFamily.CADENCE,
        formula="mean(cadential_resolution_scores)",
        observation_unit="boundary_candidate",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 boundary candidate",
        missing_value_rule="STRUCTURAL_ZERO if 0 candidates",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="harmonic ambiguity",
        interpretation_limitations="Mean tonal/metric closure score",
    ),
    # FAMILY D: FORMAL RECURRENCE & SECTIONAL ARCHITECTURE (8 features)
    StructuralFeatureDefinition(
        feature_id="form_ssm_recurrence_density",
        family=FeatureFamily.FORM,
        formula="count(ssm[i,j] > 0.80, |i-j| > 1) / total_off_diagonal_pairs",
        observation_unit="measure_pair",
        aggregation="density",
        normalization="off_diagonal_count",
        availability_rule="available if >= 4 measures",
        missing_value_rule="STRUCTURAL_ZERO if < 4 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="piece length, ostinato patterns",
        interpretation_limitations="Overall motivic/harmonic repetition density",
    ),
    StructuralFeatureDefinition(
        feature_id="form_novelty_peak_rate",
        family=FeatureFamily.FORM,
        formula="count(foote_novelty_peaks) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 8 measures",
        missing_value_rule="STRUCTURAL_ZERO if < 8 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="kernel width",
        interpretation_limitations="Section boundary candidate density",
    ),
    StructuralFeatureDefinition(
        feature_id="form_novelty_mean",
        family=FeatureFamily.FORM,
        formula="mean(foote_novelty_curve)",
        observation_unit="measure",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 8 measures",
        missing_value_rule="STRUCTURAL_ZERO if < 8 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="kernel size",
        interpretation_limitations="Average formal contrast across score",
    ),
    StructuralFeatureDefinition(
        feature_id="form_return_late_strength",
        family=FeatureFamily.FORM,
        formula="max(ssm[i, j] for i in first_20pct, j in last_30pct)",
        observation_unit="measure_region",
        aggregation="max",
        normalization="none",
        availability_rule="available if >= 10 measures",
        missing_value_rule="STRUCTURAL_ZERO if < 10 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="monothematic pieces",
        interpretation_limitations="ABA / recapitulation thematic return proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="form_recurrence_distance_mean",
        family=FeatureFamily.FORM,
        formula="mean(|i - j| for ssm[i,j] > 0.80, |i-j| > 1)",
        observation_unit="recurrence_event",
        aggregation="mean",
        normalization="measure_count",
        availability_rule="available if >= 1 recurrence",
        missing_value_rule="STRUCTURAL_ZERO if 0 recurrences",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="piece length",
        interpretation_limitations="Mean temporal span between repeated blocks",
    ),
    StructuralFeatureDefinition(
        feature_id="form_ctu_first_occurrence_mean",
        family=FeatureFamily.FORM,
        formula="mean(ctu.span.normalized_start for ctu in retained_ctus)",
        observation_unit="ctu_candidate",
        aggregation="mean",
        normalization="piece_length",
        availability_rule="available if >= 1 retained CTU",
        missing_value_rule="STRUCTURAL_ZERO if 0 retained CTUs",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="discovery window threshold",
        interpretation_limitations="Thematic exposition location proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="form_ctu_recurrence_dispersion",
        family=FeatureFamily.FORM,
        formula="std(ctu_match_positions_across_piece)",
        observation_unit="ctu_candidate",
        aggregation="std",
        normalization="piece_length",
        availability_rule="available if >= 2 CTU recurrences",
        missing_value_rule="STRUCTURAL_ZERO if < 2 recurrences",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="number of CTUs discovered",
        interpretation_limitations="Structural distribution of thematic material",
    ),
    StructuralFeatureDefinition(
        feature_id="form_ctu_late_return_presence",
        family=FeatureFamily.FORM,
        formula="1.0 if any(ctu_match_in_last_30pct) else 0.0",
        observation_unit="entire_score",
        aggregation="indicator",
        normalization="none",
        availability_rule="available if >= 1 retained CTU",
        missing_value_rule="STRUCTURAL_ZERO if 0 retained CTUs",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="piece form",
        interpretation_limitations="Thematic recapitulation binary indicator",
    ),
    # FAMILY E: VOICE-LEADING GEOMETRY (8 features)
    StructuralFeatureDefinition(
        feature_id="vl_outer_parallel_motion_share",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(parallel_soprano_bass_motions) / total_outer_voice_motions",
        observation_unit="outer_voice_step",
        aggregation="sum_ratio",
        normalization="total_motions",
        availability_rule="available if >= 1 outer voice motion",
        missing_value_rule="STRUCTURAL_ZERO if 0 motions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="parallel octaves/thirds texture",
        interpretation_limitations="Parallel outer-voice tendency",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_outer_contrary_motion_share",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(contrary_soprano_bass_motions) / total_outer_voice_motions",
        observation_unit="outer_voice_step",
        aggregation="sum_ratio",
        normalization="total_motions",
        availability_rule="available if >= 1 outer voice motion",
        missing_value_rule="STRUCTURAL_ZERO if 0 motions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="contrapuntal texture density",
        interpretation_limitations="Classical contrapuntal independence proxy",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_outer_oblique_motion_share",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(oblique_soprano_bass_motions) / total_outer_voice_motions",
        observation_unit="outer_voice_step",
        aggregation="sum_ratio",
        normalization="total_motions",
        availability_rule="available if >= 1 outer voice motion",
        missing_value_rule="STRUCTURAL_ZERO if 0 motions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="pedal points",
        interpretation_limitations="Static harmony / pedal note prevalence",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_soprano_step_resolution_share",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(|delta_p_soprano| in [1, 2]) / total_soprano_motions",
        observation_unit="soprano_step",
        aggregation="sum_ratio",
        normalization="total_motions",
        availability_rule="available if >= 1 soprano motion",
        missing_value_rule="STRUCTURAL_ZERO if 0 motions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="melodic leaps",
        interpretation_limitations="Stepwise melodic smoothness in upper line",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_bass_step_motion_share",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(|delta_p_bass| in [1, 2]) / total_bass_motions",
        observation_unit="bass_step",
        aggregation="sum_ratio",
        normalization="total_motions",
        availability_rule="available if >= 1 bass motion",
        missing_value_rule="STRUCTURAL_ZERO if 0 motions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="root movement by fourth/fifth",
        interpretation_limitations="Stepwise bass line / passacaglia tendency",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_semitone_approach_rate",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(|delta_p_outer| == 1) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="chromatic scales",
        interpretation_limitations="Leading-tone / chromatic approach rate",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_common_tone_retention_rate",
        family=FeatureFamily.VOICE_LEADING,
        formula="count(len(pc_set_t intersect pc_set_{t-1}) >= 1) / count(transitions)",
        observation_unit="sonority_transition",
        aggregation="ratio",
        normalization="transition_count",
        availability_rule="available if >= 1 transition",
        missing_value_rule="STRUCTURAL_ZERO if 0 transitions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="harmonic pacing",
        interpretation_limitations="Harmonic connection smoothness",
    ),
    StructuralFeatureDefinition(
        feature_id="vl_min_voice_leading_distance_mean",
        family=FeatureFamily.VOICE_LEADING,
        formula="mean(minimal_bipartite_matching_distance(pc_set_t, pc_set_{t-1}))",
        observation_unit="sonority_transition",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 transition",
        missing_value_rule="STRUCTURAL_ZERO if 0 transitions",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.LITERATURE,
        known_confounds="chord cardinality differences",
        interpretation_limitations="Geometric voice-leading distance (Tymoczko metric)",
    ),
    # FAMILY F: PIANO TEXTURE & REGISTRAL ARCHITECTURE (10 features)
    StructuralFeatureDefinition(
        feature_id="texture_register_centroid_mean",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="mean(sounding_midi_pitch)",
        observation_unit="sounding_attack",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 attack",
        missing_value_rule="UNAVAILABLE if 0 attacks",
        invariance_class=InvarianceClass.EQUIVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="keyboard range",
        interpretation_limitations="Absolute center of acoustic mass (shifts by +N semitones under transposition)",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_register_centroid_std",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="std(measure_mean_pitch)",
        observation_unit="measure",
        aggregation="std",
        normalization="none",
        availability_rule="available if >= 2 measures",
        missing_value_rule="STRUCTURAL_ZERO if 1 measure",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="piece length",
        interpretation_limitations="Registral wander / mobility across piece",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_register_span_mean",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="mean(max_pitch(t) - min_pitch(t))",
        observation_unit="onset_timepoint",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="monophonic passages",
        interpretation_limitations="Mean keyboard spatial layout width",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_register_span_max",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="max(max_pitch(t) - min_pitch(t))",
        observation_unit="onset_timepoint",
        aggregation="max",
        normalization="none",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="extreme hand extensions",
        interpretation_limitations="Maximum spatial expansion across piano",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_interstaff_gap_mean",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="mean(min_pitch_staff1(t) - max_pitch_staff2(t))",
        observation_unit="onset_timepoint",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 two-staff onset",
        missing_value_rule="STRUCTURAL_ZERO if 0 two-staff onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="hand crossings (negative values)",
        interpretation_limitations="Spatial clearance between right and left hand layers",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_simultaneity_attack_mean",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="mean(count(attacks_at_onset))",
        observation_unit="onset_timepoint",
        aggregation="mean",
        normalization="none",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="grace notes",
        interpretation_limitations="Chordal vs linear density per strike",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_block_chord_share",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="count(attacks_at_onset >= 3) / count(onsets)",
        observation_unit="onset_timepoint",
        aggregation="sum_ratio",
        normalization="onset_count",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="arpeggiated figurations",
        interpretation_limitations="Homophonic chordal texture share",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_arpeggiation_proxy_rate",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="count(detected_arpeggio_runs) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.HYPOTHESIS,
        known_confounds="scale runs (filtered by interval span and step uniformity)",
        interpretation_limitations="Pianistic figurative sweep rate",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_octave_doubling_share",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="count(onsets_with_octave_doubled_pcs) / count(onsets)",
        observation_unit="onset_timepoint",
        aggregation="sum_ratio",
        normalization="onset_count",
        availability_rule="available if >= 1 onset",
        missing_value_rule="UNAVAILABLE if 0 onsets",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="unisons",
        interpretation_limitations="Grand/orchestral octave reinforcement share",
    ),
    StructuralFeatureDefinition(
        feature_id="texture_repeated_note_attack_rate",
        family=FeatureFamily.TEXTURE_REGISTER,
        formula="count(immediate_pitch_repetitions) / measure_count",
        observation_unit="measure",
        aggregation="rate",
        normalization="measure_count",
        availability_rule="available if >= 1 measure",
        missing_value_rule="UNAVAILABLE if 0 measures",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.OBSERVED,
        known_confounds="trills, tremolos",
        interpretation_limitations="Pianistic motoric / repeated note rate",
    ),
    # FAMILY G: NORMALIZED TEMPORAL TRAJECTORIES (8 features)
    StructuralFeatureDefinition(
        feature_id="traj_register_center_slope",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="linear_regression_slope(bin_mean_pitches_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="slope",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="piece length",
        interpretation_limitations="Directional registral ascent/descent across piece",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_register_span_slope",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="linear_regression_slope(bin_mean_spans_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="slope",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="piece length",
        interpretation_limitations="Spatial expansion/contraction trend",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_attack_density_slope",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="linear_regression_slope(bin_attack_densities_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="slope",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="piece length",
        interpretation_limitations="Rhythmic acceleration / accumulation across piece",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_attack_density_curvature",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="polynomial_curvature_coef(bin_attack_densities_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="curvature",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="climax location",
        interpretation_limitations="Arch-like vs U-shaped density profile",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_chromaticity_slope",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="linear_regression_slope(bin_chromatic_shares_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="slope",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="developmental harmonic shifts",
        interpretation_limitations="Progressive chromatic intensification trend",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_sonority_cardinality_slope",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="linear_regression_slope(bin_pc_cardinalities_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="slope",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="texture shifts",
        interpretation_limitations="Harmonic thickening/thinning trend",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_density_early_late_contrast",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="mean(density[bins_6_7]) - mean(density[bins_0_1])",
        observation_unit="8_bin_series",
        aggregation="contrast",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="climax location",
        interpretation_limitations="Coda vs exposition energy difference",
    ),
    StructuralFeatureDefinition(
        feature_id="traj_register_volatility",
        family=FeatureFamily.TEMPORAL_TRAJECTORY,
        formula="std(bin_mean_pitches_over_8_bins)",
        observation_unit="8_bin_series",
        aggregation="std",
        normalization="none",
        availability_rule="available if >= 8 bins populated",
        missing_value_rule="STRUCTURAL_ZERO if < 8 bins",
        invariance_class=InvarianceClass.INVARIANT,
        provenance=Provenance.ENGINEERING_HEURISTIC,
        known_confounds="register jumps",
        interpretation_limitations="Macro-level registral instability",
    ),
)


def get_feature_invariance_contract(
    feature_id: str,
    transformation: TransformationType,
) -> InvarianceClass:
    """Return the expected invariance behavior for a feature under a specific transformation."""
    if transformation == TransformationType.TRANSPOSITION:
        if feature_id == "texture_register_centroid_mean":
            return InvarianceClass.EQUIVARIANT
        return InvarianceClass.INVARIANT

    if transformation == TransformationType.TIME_DILATION:
        return InvarianceClass.INVARIANT

    if transformation in (
        TransformationType.PIECE_ID_RENAME,
        TransformationType.SOURCE_PATH_RENAME,
        TransformationType.VOICE_ID_RENAME,
    ):
        return InvarianceClass.INVARIANT

    if transformation == TransformationType.STAFF_SWAP:
        if feature_id == "texture_interstaff_gap_mean":
            return InvarianceClass.SENSITIVE_BY_DESIGN
        return InvarianceClass.INVARIANT

    return InvarianceClass.NOT_APPLICABLE


def compute_invariance_contract_hash(
    catalog: tuple[StructuralFeatureDefinition, ...] = STRUCTURAL_FEATURE_CATALOG,
) -> str:
    """Deterministic SHA-256 hash of the complete metamorphic invariance contract across all features."""
    transformations = sorted(t.value for t in TransformationType)
    canonical = {
        "version": "INVARIANCE_CONTRACT_V1",
        "feature_count": len(catalog),
        "contracts": [
            {
                "feature_id": d.feature_id,
                "behaviors": {
                    t: get_feature_invariance_contract(d.feature_id, TransformationType(t)).value
                    for t in transformations
                },
            }
            for d in sorted(catalog, key=lambda x: x.feature_id)
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def compute_structural_schema_hash(
    catalog: tuple[StructuralFeatureDefinition, ...] = STRUCTURAL_FEATURE_CATALOG,
) -> str:
    """Deterministic SHA-256 hash of the complete Structural Feature Schema V1."""
    canonical = {
        "version": "STRUCTURAL_REPRESENTATION_SCHEMA_V1",
        "feature_count": len(catalog),
        "descriptors": [
            {
                "feature_id": d.feature_id,
                "family": d.family.value,
                "formula": d.formula,
                "observation_unit": d.observation_unit,
                "aggregation": d.aggregation,
                "normalization": d.normalization,
                "availability_rule": d.availability_rule,
                "missing_value_rule": d.missing_value_rule,
                "invariance_class": d.invariance_class.value,
                "provenance": d.provenance.value,
                "known_confounds": d.known_confounds,
                "interpretation_limitations": d.interpretation_limitations,
                "semantic_version": d.semantic_version,
            }
            for d in sorted(catalog, key=lambda x: x.feature_id)
        ],
    }
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
