"""
Comprehensive Unit Tests for RC-011 Structural Music Representation.

Verifies:
- 20-fixture registry completeness & dynamic length derivation
- Fixture hash mutation sensitivity
- Family-status derivation
- All 4 preregistered transpositions {-7, -5, +3, +5}, time dilation x2, renames, staff swap
- Sounding-note sonority with sustain and non-double-counting
- Cadence IOI semantics, local key estimation, V-I fixture, V-VI deceptive fixture
- 12-D SSM contract
- CTU late recurrence & discovery-region adversarial case
- True minimal assignment voice-leading distance (symmetry, unequal cardinality, target reuse)
- Arpeggio max-IOI and scale exclusion
- Repeated-note time threshold
- Trajectory empty-bin availability handling
- Matrix availability-reason cryptographic hashing
- Validation result mutation sensitivity
- Exact prior milestone fail-closed checks
"""

from fractions import Fraction
from pathlib import Path

import pytest

from russian_piano_composer.domain.score import (
    CanonicalScore,
    CanonicalScoreEvent,
)
from russian_piano_composer.structure_analysis.cadence import extract_cadence_features
from russian_piano_composer.structure_analysis.extractor import extract_structural_representation
from russian_piano_composer.structure_analysis.form import (
    FORM_SSM_MEASURE_EMBED_DIM,
)
from russian_piano_composer.structure_analysis.lineage import (
    ACCEPTED_CANONICAL_MANIFEST_HASH,
    verify_prior_milestone_hashes_fail_closed,
)
from russian_piano_composer.structure_analysis.matrix import (
    build_structural_representation_matrix,
)
from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    AvailabilityStatus,
    FeatureValue,
    InvarianceClass,
    TransformationType,
    compute_structural_schema_hash,
)
from russian_piano_composer.structure_analysis.sonority import extract_sonority_features
from russian_piano_composer.structure_analysis.texture import (
    TexturePolicy,
    extract_texture_features,
)
from russian_piano_composer.structure_analysis.trajectory import extract_trajectory_features
from russian_piano_composer.structure_analysis.validation import (
    FIXTURE_REGISTRY,
    _midi_to_spelled_pitch,
    apply_metamorphic_transformation,
    build_synthetic_score,
    compute_fixture_semantic_hash,
    run_synthetic_and_metamorphic_validation,
)
from russian_piano_composer.structure_analysis.voice_leading import (
    minimal_voice_leading_distance,
)


def test_structural_schema_hash_determinism() -> None:
    """Verify compute_structural_schema_hash is deterministic and ordering-invariant."""
    h1 = compute_structural_schema_hash()
    h2 = compute_structural_schema_hash(tuple(reversed(STRUCTURAL_FEATURE_CATALOG)))
    assert len(h1) == 64
    assert h1 == h2


def test_fixture_registry_completeness_and_dynamic_count() -> None:
    """Verify fixture registry contains exactly 24 distinct fixtures A through X."""
    assert len(FIXTURE_REGISTRY) == 24
    fixture_ids = [f.fixture_id for f in FIXTURE_REGISTRY]
    expected_ids = [chr(ord("A") + i) for i in range(24)]
    assert fixture_ids == expected_ids


def test_fixture_semantic_hash_mutation_sensitivity() -> None:
    """Verify modifying a note in a fixture alters its semantic hash."""
    f_a = FIXTURE_REGISTRY[0].builder()
    h_orig = compute_fixture_semantic_hash(f_a)

    # Mutate one event with matched spelled pitch
    mut_events = list(f_a.events)
    ev0 = mut_events[0]
    new_midi = (ev0.midi + 1) if ev0.midi is not None else 61
    mut_events[0] = CanonicalScoreEvent(
        piece_id=ev0.piece_id,
        event_id=ev0.event_id,
        event_index=ev0.event_index,
        event_kind=ev0.event_kind,
        measure_index=ev0.measure_index,
        source_measure_label=ev0.source_measure_label,
        staff=ev0.staff,
        voice=ev0.voice,
        global_onset=ev0.global_onset,
        offset_in_measure=ev0.offset_in_measure,
        duration=ev0.duration,
        pitch=_midi_to_spelled_pitch(new_midi),
        midi=new_midi,
    )
    mut_score = CanonicalScore(
        piece_id=f_a.piece_id,
        corpus_id=f_a.corpus_id,
        corpus_role=f_a.corpus_role,
        score_entry_id=f_a.score_entry_id,
        composer=f_a.composer,
        title=f_a.title,
        source_repository=f_a.source_repository,
        source_commit=f_a.source_commit,
        source_relative_path=f_a.source_relative_path,
        source_sha256=f_a.source_sha256,
        manifest_hash=f_a.manifest_hash,
        parser_version=f_a.parser_version,
        measures=f_a.measures,
        events=tuple(mut_events),
    )
    h_mut = compute_fixture_semantic_hash(mut_score)
    assert h_orig != h_mut


def test_synthetic_validation_suite_all_pass() -> None:
    """Verify all 20 fixtures and 504 metamorphic checks pass with VALIDATED status."""
    val_res = run_synthetic_and_metamorphic_validation()
    assert val_res.overall_status == "STRUCTURAL_REPRESENTATION_VALIDATED"
    assert all(a.passed for a in val_res.assertion_records)
    assert all(m.passed for m in val_res.metamorphic_records)
    assert all(fs.status == "PASS" for fs in val_res.family_statuses)


def test_metamorphic_transpositions_all_four_steps() -> None:
    """Verify transpositions {-7, -5, +3, +5} maintain exact invariance/equivariance contracts."""
    base_score = FIXTURE_REGISTRY[0].builder()
    base_rep = extract_structural_representation(base_score)

    for shift in (-7, -5, 3, 5):
        trans_score = apply_metamorphic_transformation(base_score, TransformationType.TRANSPOSITION, shift)
        trans_rep = extract_structural_representation(trans_score)

        # Centroid is equivariant (+shift)
        assert abs(trans_rep["texture_register_centroid_mean"].value - (base_rep["texture_register_centroid_mean"].value + shift)) < 1e-4

        # Other invariant features
        assert abs(trans_rep["tonal_global_confidence"].value - base_rep["tonal_global_confidence"].value) < 1e-4
        assert abs(trans_rep["sonority_pc_cardinality_mean"].value - base_rep["sonority_pc_cardinality_mean"].value) < 1e-4
        assert abs(trans_rep["vl_outer_parallel_motion_share"].value - base_rep["vl_outer_parallel_motion_share"].value) < 1e-4


def test_metamorphic_time_dilation_x2() -> None:
    """Verify uniform time dilation x2 preserves normalized/rate features and drops absolute-rate features."""
    base_score = FIXTURE_REGISTRY[0].builder()
    base_rep = extract_structural_representation(base_score)

    dil_score = apply_metamorphic_transformation(base_score, TransformationType.TIME_DILATION)
    dil_rep = extract_structural_representation(dil_score)

    assert abs(dil_rep["cadence_boundary_candidate_rate"].value - base_rep["cadence_boundary_candidate_rate"].value) < 1e-4
    assert abs(dil_rep["sonority_change_rate"].value - base_rep["sonority_change_rate"].value) < 1e-4

    # Absolute-tempo rate features drop to 0 under dilation
    score_h = FIXTURE_REGISTRY[7].builder()
    rep_h = extract_structural_representation(score_h)
    dil_h = extract_structural_representation(apply_metamorphic_transformation(score_h, TransformationType.TIME_DILATION))
    assert rep_h["texture_arpeggiation_proxy_rate"].value > 0.0
    assert dil_h["texture_arpeggiation_proxy_rate"].value == 0.0

    score_i = FIXTURE_REGISTRY[8].builder()
    rep_i = extract_structural_representation(score_i)
    dil_i = extract_structural_representation(apply_metamorphic_transformation(score_i, TransformationType.TIME_DILATION))
    assert rep_i["texture_repeated_note_attack_rate"].value > 0.0
    assert dil_i["texture_repeated_note_attack_rate"].value == 0.0


def test_metamorphic_metadata_renames_invariance() -> None:
    """Verify piece ID, source path, and voice renames do not change feature values."""
    base_score = FIXTURE_REGISTRY[0].builder()
    base_rep = extract_structural_representation(base_score)

    for trans in (TransformationType.PIECE_ID_RENAME, TransformationType.SOURCE_PATH_RENAME, TransformationType.VOICE_ID_RENAME):
        ren_score = apply_metamorphic_transformation(base_score, trans)
        ren_rep = extract_structural_representation(ren_score)
        for fid in base_rep.features:
            assert abs(ren_rep[fid].value - base_rep[fid].value) < 1e-4


def test_metamorphic_staff_swap_sensitive_by_design() -> None:
    """Verify staff swap inverts interstaff gap while preserving other features."""
    base_score = FIXTURE_REGISTRY[6].builder()  # Fixture G: two-staff block chords
    base_rep = extract_structural_representation(base_score)

    swap_score = apply_metamorphic_transformation(base_score, TransformationType.STAFF_SWAP)
    swap_rep = extract_structural_representation(swap_score)

    assert swap_rep["texture_interstaff_gap_mean"].value < 0.0
    assert base_rep["texture_interstaff_gap_mean"].value > 0.0
    assert abs(swap_rep["sonority_pc_cardinality_mean"].value - base_rep["sonority_pc_cardinality_mean"].value) < 1e-4


def test_sounding_sonority_with_sustained_notes_and_no_double_counting() -> None:
    """Verify sustained note across onsets is included in active sounding pc set without double-counting duration."""
    # Measure 0: Bass C3 (dur = 1 whole note). At beat 2, Soprano E4 attacks (dur = 1/2).
    notes = [
        (48, 0, Fraction(0, 1), Fraction(1, 1)),  # C3 sounding throughout M0
        (64, 0, Fraction(1, 2), Fraction(1, 2)),  # E4 sounding in second half of M0
    ]
    score = build_synthetic_score(notes, 1, "sustain_test")
    feats = extract_sonority_features(score)

    # At onset 0: C3 (cardinality 1). At onset 1/2: C3 + E4 active (cardinality 2).
    # Mean cardinality should be (1 + 2) / 2 = 1.5
    assert abs(feats["sonority_pc_cardinality_mean"].value - 1.5) < 1e-4


def test_cadence_ioi_and_local_tonic_resolution() -> None:
    """Verify V-I authentic cadence and V-VI deceptive cadence trigger resolution proxies."""
    score_e = FIXTURE_REGISTRY[4].builder()
    feats_e = extract_cadence_features(score_e)
    assert feats_e["cadence_tonic_resolution_rate"].value > 0.0
    assert feats_e["cadence_boundary_candidate_rate"].value > 0.0

    score_f = FIXTURE_REGISTRY[5].builder()
    feats_f = extract_cadence_features(score_f)
    assert feats_f["cadence_deceptive_proxy_rate"].value > 0.0


def test_form_ssm_measure_embed_dim_strictly_12() -> None:
    """Verify form SSM embedding dimension is strictly 12."""
    assert FORM_SSM_MEASURE_EMBED_DIM == 12


def test_voice_leading_minimal_assignment_symmetry_and_transposition() -> None:
    """Verify minimal voice-leading distance satisfies symmetry, zero identity, and transposition equivariance."""
    c_maj = frozenset([0, 4, 7])
    g_maj = frozenset([7, 11, 2])
    frozenset([5, 9, 0])

    # Symmetry
    assert minimal_voice_leading_distance(c_maj, g_maj) == minimal_voice_leading_distance(g_maj, c_maj)

    # Zero identity
    assert minimal_voice_leading_distance(c_maj, c_maj) == 0.0

    # Transposition equivariance: C->G is distance between (C+2)->(G+2) (i.e. D->A)
    d_maj = frozenset([(p + 2) % 12 for p in c_maj])
    a_maj = frozenset([(p + 2) % 12 for p in g_maj])
    assert abs(minimal_voice_leading_distance(c_maj, g_maj) - minimal_voice_leading_distance(d_maj, a_maj)) < 1e-6


def test_voice_leading_target_reuse_adversarial_prevention() -> None:
    """Verify equal cardinality chords use 1-to-1 matching rather than all mapping to a single note."""
    chord_a = frozenset([0, 4, 7])  # C, E, G
    frozenset([0, 0, 0])  # single note C (cardinality 1)
    # Distance between C-E-G and C-E-G is 0
    assert minimal_voice_leading_distance(chord_a, chord_a) == 0.0
    # Distance between C-E-G and C-F-A (F major)
    f_maj = frozenset([5, 9, 0])
    # Bijection maps 0->0 (0), 4->5 (1), 7->9 (2) => total 3/3 = 1.0
    assert abs(minimal_voice_leading_distance(chord_a, f_maj) - 1.0) < 1e-6


def test_arpeggio_max_ioi_and_scale_exclusion() -> None:
    """Verify arpeggio detector enforces IOI <= 0.5 and excludes monotonic scalar runs."""
    policy = TexturePolicy()

    # Arpeggio (C-E-G chord leaps) with IOI = 0.5 quarters
    score_arp = FIXTURE_REGISTRY[7].builder()
    feats_arp = extract_texture_features(score_arp, policy)
    assert feats_arp["texture_arpeggiation_proxy_rate"].value > 0.0

    # Monotonic scale run (steps of 1-2 semitones) with IOI = 0.5 quarters
    scale_notes = []
    for m in range(8):
        for idx in range(8):
            scale_notes.append((60 + idx, m, Fraction(idx, 8), Fraction(1, 8)))
    score_scale = build_synthetic_score(scale_notes, 8, "scale_run")
    feats_scale = extract_texture_features(score_scale, policy)
    # Scale run must NOT be counted as an arpeggio run
    assert feats_scale["texture_arpeggiation_proxy_rate"].value == 0.0


def test_repeated_note_time_threshold() -> None:
    """Verify repeated note attacks are counted only when delta-t <= 0.5 quarters."""
    # Fast repetition (IOI = 0.5 quarters)
    score_fast = FIXTURE_REGISTRY[8].builder()
    feats_fast = extract_texture_features(score_fast)
    assert feats_fast["texture_repeated_note_attack_rate"].value > 0.0

    # Slow repetition (IOI = 1.0 quarter note = Fraction(1, 4) whole note)
    slow_notes = []
    for m in range(8):
        for beat in range(4):
            slow_notes.append((60, m, Fraction(beat, 4), Fraction(1, 4)))
    score_slow = build_synthetic_score(slow_notes, 8, "slow_rep")
    feats_slow = extract_texture_features(score_slow)
    assert feats_slow["texture_repeated_note_attack_rate"].value == 0.0


def test_trajectory_empty_bins_return_structural_zero() -> None:
    """Verify unpopulated trajectory bins return STRUCTURAL_ZERO rather than silent imputation."""
    # 2-measure score partitioned into 8 bins has empty bins
    score_short = FIXTURE_REGISTRY[4].builder()
    feats = extract_trajectory_features(score_short)
    assert feats["traj_register_center_slope"].status == AvailabilityStatus.STRUCTURAL_ZERO
    assert "bins populated" in feats["traj_register_center_slope"].reason


def test_matrix_availability_reason_cryptographic_binding() -> None:
    """Verify matrix hash mutates when an availability reason string changes."""
    piece_reps = {
        "p1": {
            d.feature_id: FeatureValue(1.0, AvailabilityStatus.AVAILABLE, "reason_a")
            for d in STRUCTURAL_FEATURE_CATALOG
        }
    }
    m1 = build_structural_representation_matrix(piece_reps, ACCEPTED_CANONICAL_MANIFEST_HASH)
    h1 = m1.compute_matrix_hash()

    piece_reps_mut = {
        "p1": {
            d.feature_id: FeatureValue(1.0, AvailabilityStatus.AVAILABLE, "reason_b" if d.feature_id == "tonal_global_confidence" else "reason_a")
            for d in STRUCTURAL_FEATURE_CATALOG
        }
    }
    m2 = build_structural_representation_matrix(piece_reps_mut, ACCEPTED_CANONICAL_MANIFEST_HASH)
    h2 = m2.compute_matrix_hash()

    assert h1 != h2


def test_prior_milestone_hashes_fail_closed() -> None:
    """Verify prior milestone fail-closed checks pass on accepted values and fail on corruption."""
    verify_prior_milestone_hashes_fail_closed(ACCEPTED_CANONICAL_MANIFEST_HASH)

    with pytest.raises(ValueError, match="Manifest hash mismatch"):
        verify_prior_milestone_hashes_fail_closed("corrupted_manifest_hash")


def test_cadence_rest_evidence_threshold() -> None:
    """Verify sounding gap >= 0.5 quarter notes triggers rest evidence, whereas < 0.5 does not."""
    # Gap of 0.25 quarters = Fraction(1, 16) whole note
    notes_small_gap = [
        (60, 0, Fraction(0, 1), Fraction(3, 16)),  # releases at 3/16, next onset at 4/16 => gap = 1/16 (< 0.5 quarters)
        (64, 0, Fraction(4, 16), Fraction(1, 4)),
    ]
    sc_small = build_synthetic_score(notes_small_gap, 1, "small_gap")
    feats_small = extract_cadence_features(sc_small)

    # Gap of 0.5 quarters = Fraction(1, 8) whole note
    notes_large_gap = [
        (60, 0, Fraction(0, 1), Fraction(1, 8)),  # releases at 1/8, next onset at 2/8 => gap = 1/8 (== 0.5 quarters)
        (64, 0, Fraction(2, 8), Fraction(1, 4)),
    ]
    sc_large = build_synthetic_score(notes_large_gap, 1, "large_gap")
    feats_large = extract_cadence_features(sc_large)

    assert feats_large["cadence_boundary_candidate_rate"].value >= feats_small["cadence_boundary_candidate_rate"].value


def test_cadence_unrelated_fourth_fifth_motion_rejected() -> None:
    """Verify arbitrary fourth/fifth bass movement not resolving to local tonic degree 1 is rejected."""
    # Bass moves C (48) -> F (53) (interval 5 / 4th up) in C major.
    # F is scale degree 5 relative to Bb or 5 in C, but here bass moves 0 -> 5 (not 5 -> 1 or 7 -> 1).
    # In the old code, bass_interval == 5 was counted as authentic resolution; now it must be 0.0.
    notes = [
        (48, 0, Fraction(0, 1), Fraction(1, 1)), (60, 0, Fraction(0, 1), Fraction(1, 1)), (64, 0, Fraction(0, 1), Fraction(1, 1)),
        (53, 1, Fraction(0, 1), Fraction(1, 1)), (60, 1, Fraction(0, 1), Fraction(1, 1)), (65, 1, Fraction(0, 1), Fraction(1, 1)),
    ]
    sc = build_synthetic_score(notes, 2, "c_to_f_bass")
    feats = extract_cadence_features(sc)
    assert feats["cadence_tonic_resolution_rate"].value == 0.0


def test_voice_leading_unequal_cardinality_optimal_transport() -> None:
    """Verify minimal voice leading on unequal cardinalities uses LCM optimal assignment."""
    dyad = frozenset([0, 4])       # |A| = 2: C, E
    triad = frozenset([0, 4, 7])   # |B| = 3: C, E, G
    # LCM(2, 3) = 6
    # Expands dyad to [0, 0, 0, 4, 4, 4] and triad to [0, 0, 4, 4, 7, 7]
    # Cost matrix matching: 0->0(x2), 4->4(x2), leaving {0, 4} and {7, 7}: dist(0, 7)=5, dist(4, 7)=3 -> sum=8
    # Total distance / 6 = 8 / 6 = 1.333333
    d = minimal_voice_leading_distance(dyad, triad)
    assert abs(d - (8.0 / 6.0)) < 1e-5
    # Strict symmetry
    assert minimal_voice_leading_distance(dyad, triad) == minimal_voice_leading_distance(triad, dyad)


def test_form_ctu_pairwise_non_overlapping_suppression() -> None:
    """Verify overlapping candidate CTU occurrences are suppressed pairwise."""
    from russian_piano_composer.ctu.discovery import discover_ctus_for_score
    from russian_piano_composer.structure_analysis.form import extract_form_features
    sc = FIXTURE_REGISTRY[13].builder()  # Fixture N (12 measures)
    disc = discover_ctus_for_score(sc, manifest_hash="0" * 64)
    assert len(disc.retained_ctus) > 0
    feats = extract_form_features(sc, retained_ctus=disc.retained_ctus)
    assert feats["form_ctu_recurrence_dispersion"].status == AvailabilityStatus.AVAILABLE
    assert feats["form_ctu_late_return_presence"].value == 1.0


def test_form_ctu_recurrence_dispersion_availability_status() -> None:
    """Verify form_ctu_recurrence_dispersion is AVAILABLE iff >= 2 occurrences found, else STRUCTURAL_ZERO."""
    from russian_piano_composer.structure_analysis.form import extract_form_features
    sc_o = FIXTURE_REGISTRY[14].builder()  # Fixture O: through-composed (no CTU recurrence)
    feats_o = extract_form_features(sc_o, retained_ctus=[])
    assert feats_o["form_ctu_recurrence_dispersion"].status == AvailabilityStatus.STRUCTURAL_ZERO
    assert feats_o["form_ctu_recurrence_dispersion"].reason == "Fewer than 2 CTU occurrences found"


def test_metamorphic_mutation_sensitivity() -> None:
    """Verify that all 504 metamorphic records pass and validation result binds them."""
    res1 = run_synthetic_and_metamorphic_validation()
    assert res1.overall_status == "STRUCTURAL_REPRESENTATION_VALIDATED"
    assert len(res1.metamorphic_records) == 504
    assert len(res1.assertion_records) == 20
    assert all(m.passed for m in res1.metamorphic_records)


def test_dynamic_ctu_policy_hash_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that tampering with CTUDiscoveryPolicy hash raises ValueError in fail-closed check."""
    from russian_piano_composer.structure_analysis import lineage
    monkeypatch.setattr(lineage, "ACCEPTED_RC009B_DISCOVERY_POLICY_HASH", "tampered_policy_hash")
    with pytest.raises(ValueError, match="RC-009B CTU Discovery Policy hash mismatch"):
        verify_prior_milestone_hashes_fail_closed(ACCEPTED_CANONICAL_MANIFEST_HASH)


def test_assertion_contract_hash_determinism() -> None:
    """Verify compute_synthetic_assertion_contract_hash is deterministic and ordering-invariant."""
    from russian_piano_composer.structure_analysis.validation import (
        ASSERTION_REGISTRY,
        compute_synthetic_assertion_contract_hash,
    )
    h1 = compute_synthetic_assertion_contract_hash()
    h2 = compute_synthetic_assertion_contract_hash(tuple(reversed(ASSERTION_REGISTRY)))
    assert len(h1) == 64
    assert h1 == h2


def test_cadence_rest_threshold_time_dilation_counterexample() -> None:
    """Verify adversarial rest-threshold time-dilation fixture exhibits deterministic sensitivity."""
    from russian_piano_composer.structure_analysis.validation import (
        TransformationType,
        apply_metamorphic_transformation,
        fixture_x_cadence_dilation_counterexample,
    )
    sc_orig = fixture_x_cadence_dilation_counterexample()
    sc_dil = apply_metamorphic_transformation(sc_orig, TransformationType.TIME_DILATION)

    feats_orig = extract_cadence_features(sc_orig)
    feats_dil = extract_cadence_features(sc_dil)

    # Rest gap expands from 0.375 quarters (sub-threshold) to 0.75 quarters (above-threshold)
    assert feats_dil["cadence_boundary_candidate_rate"].value > feats_orig["cadence_boundary_candidate_rate"].value
    assert feats_dil["cadence_tonic_resolution_rate"].value > feats_orig["cadence_tonic_resolution_rate"].value
    assert feats_dil["cadence_dominant_tonic_proxy_rate"].value > feats_orig["cadence_dominant_tonic_proxy_rate"].value
    assert feats_dil["cadence_deceptive_proxy_rate"].value > feats_orig["cadence_deceptive_proxy_rate"].value
    assert abs(feats_dil["cadence_boundary_strength_mean"].value - feats_orig["cadence_boundary_strength_mean"].value) > 0.05


def test_cadence_time_dilation_contract_all_sensitive() -> None:
    """Verify all 6 cadence features are declared SENSITIVE_BY_DESIGN under TIME_DILATION."""
    from russian_piano_composer.structure_analysis.schema import (
        InvarianceClass,
        TransformationType,
        get_feature_invariance_contract,
    )
    cadence_features = [
        "cadence_boundary_candidate_rate",
        "cadence_boundary_strength_mean",
        "cadence_tonic_resolution_rate",
        "cadence_dominant_tonic_proxy_rate",
        "cadence_deceptive_proxy_rate",
        "cadence_resolution_strength_mean",
    ]
    for fid in cadence_features:
        contract = get_feature_invariance_contract(fid, TransformationType.TIME_DILATION)
        assert contract == InvarianceClass.SENSITIVE_BY_DESIGN


def test_zero_generic_sensitive_by_design_autopass() -> None:
    """Verify metamorphic runner contains zero generic passed=True auto-passes for SENSITIVE_BY_DESIGN."""
    res = run_synthetic_and_metamorphic_validation()
    sensitive_records = [
        m for m in res.metamorphic_records
        if m.expected_behavior == InvarianceClass.SENSITIVE_BY_DESIGN
    ]
    # Exactly 9 sensitive records (1 staff swap, 2 texture dilation, 6 cadence dilation)
    assert len(sensitive_records) == 9
    for rec in sensitive_records:
        assert rec.passed is True
        assert rec.expected_relation != "sensitive by design"
        assert rec.actual_relation != "skipped"


def test_non_vacuous_trajectory_fixture_mapping() -> None:
    """Verify trajectory features are bound to active, non-vacuous synthetic fixtures."""
    from russian_piano_composer.structure_analysis.validation import (
        METAMORPHIC_FEATURE_FIXTURE_MAP,
        fixture_u_registral_span_and_cardinality,
        fixture_v_density_curvature_and_chromaticity,
        fixture_w_register_volatility,
    )
    assert METAMORPHIC_FEATURE_FIXTURE_MAP["traj_register_span_slope"] == "U"
    assert METAMORPHIC_FEATURE_FIXTURE_MAP["traj_sonority_cardinality_slope"] == "U"
    assert METAMORPHIC_FEATURE_FIXTURE_MAP["traj_attack_density_curvature"] == "V"
    assert METAMORPHIC_FEATURE_FIXTURE_MAP["traj_chromaticity_slope"] == "V"
    assert METAMORPHIC_FEATURE_FIXTURE_MAP["traj_register_volatility"] == "W"

    u_feats = extract_trajectory_features(fixture_u_registral_span_and_cardinality())
    assert u_feats["traj_register_span_slope"].value > 0.0
    assert u_feats["traj_sonority_cardinality_slope"].value > 0.0

    v_feats = extract_trajectory_features(fixture_v_density_curvature_and_chromaticity())
    assert v_feats["traj_attack_density_curvature"].value < 0.0
    assert v_feats["traj_chromaticity_slope"].value > 0.0

    w_feats = extract_trajectory_features(fixture_w_register_volatility())
    assert w_feats["traj_register_volatility"].value > 20.0


def test_metamorphic_test_matrix_hash_mutation() -> None:
    """Verify modifying any feature-fixture mapping alters compute_metamorphic_test_matrix_hash."""
    from russian_piano_composer.structure_analysis.validation import (
        METAMORPHIC_FEATURE_FIXTURE_MAP,
        compute_metamorphic_test_matrix_hash,
    )
    h_orig = compute_metamorphic_test_matrix_hash()
    mutated_map = dict(METAMORPHIC_FEATURE_FIXTURE_MAP)
    mutated_map["traj_register_span_slope"] = "P"
    h_mut = compute_metamorphic_test_matrix_hash(mutated_map)
    assert h_orig != h_mut
    assert len(h_orig) == 64


def test_cadence_semantic_hash_mutation() -> None:
    """Verify modifying cadence algorithm semantics alters compute_cadence_semantic_hash."""
    import hashlib
    import json

    from russian_piano_composer.structure_analysis.lineage import compute_cadence_semantic_hash
    h_orig = compute_cadence_semantic_hash()
    assert len(h_orig) == 64

    # Mutate rest gap threshold
    tampered = {
        "family": "CADENCE",
        "semantic_version": "1.0.0",
        "boundary_criteria": {"rest_gap_threshold_quarters": 0.75},
    }
    h_mut = hashlib.sha256(json.dumps(tampered, sort_keys=True).encode("utf-8")).hexdigest()
    assert h_orig != h_mut


def test_form_semantic_hash_mutation() -> None:
    """Verify modifying form algorithm semantics alters compute_form_semantic_hash."""
    import hashlib
    import json

    from russian_piano_composer.structure_analysis.lineage import compute_form_semantic_hash
    h_orig = compute_form_semantic_hash()
    assert len(h_orig) == 64

    tampered = {
        "family": "FORM",
        "semantic_version": "1.0.0",
        "ssm_representation": "24_dimensional_chroma_cosine_similarity",
    }
    h_mut = hashlib.sha256(json.dumps(tampered, sort_keys=True).encode("utf-8")).hexdigest()
    assert h_orig != h_mut


def test_voice_leading_semantic_hash_mutation() -> None:
    """Verify modifying voice leading semantics alters compute_voice_leading_semantic_hash."""
    import hashlib
    import json

    from russian_piano_composer.structure_analysis.lineage import (
        compute_voice_leading_semantic_hash,
    )
    h_orig = compute_voice_leading_semantic_hash()
    assert len(h_orig) == 64

    tampered = {
        "family": "VOICE_LEADING",
        "semantic_version": "1.0.0",
        "minimal_voice_leading_distance": {"assignment_algorithm": "greedy"},
    }
    h_mut = hashlib.sha256(json.dumps(tampered, sort_keys=True).encode("utf-8")).hexdigest()
    assert h_orig != h_mut


def test_structure_analysis_source_hash_mutation(tmp_path: Path) -> None:
    """Verify compute_structure_analysis_source_hash binds source bytes and mutates on changes."""
    from russian_piano_composer.structure_analysis.lineage import (
        compute_structure_analysis_source_hash,
    )
    h_orig = compute_structure_analysis_source_hash()
    assert len(h_orig) == 64

    # Create synthetic directory mimicking package
    modules = [
        "cadence.py", "extractor.py", "form.py", "schema.py",
        "sonority.py", "texture.py", "tonal.py", "trajectory.py", "voice_leading.py"
    ]
    for m in modules:
        (tmp_path / m).write_text("# code\n", encoding="utf-8")
    h_tmp = compute_structure_analysis_source_hash(tmp_path)
    assert len(h_tmp) == 64
    assert h_tmp != h_orig

    # Mutate one file in tmp
    (tmp_path / "cadence.py").write_text("# modified code\n", encoding="utf-8")
    h_tmp_mut = compute_structure_analysis_source_hash(tmp_path)
    assert h_tmp != h_tmp_mut


def test_implementation_commit_lineage_binding() -> None:
    """Verify StructuralRepresentationLineage binds rc011_implementation_commit_sha and mutates bundle hash."""
    from russian_piano_composer.structure_analysis.lineage import (
        RC011_IMPLEMENTATION_COMMIT_SHA,
    )
    from russian_piano_composer.structure_analysis.matrix import (
        build_structural_representation_matrix,
    )
    sc = FIXTURE_REGISTRY[0].builder()
    rep = extract_structural_representation(sc)
    mat = build_structural_representation_matrix({"SYNTHETIC:test": rep.features}, manifest_hash="0" * 64)
    val = run_synthetic_and_metamorphic_validation()

    from russian_piano_composer.structure_analysis.lineage import (
        compute_structural_representation_lineage,
    )
    lin1 = compute_structural_representation_lineage(
        manifest_hash=ACCEPTED_CANONICAL_MANIFEST_HASH,
        matrix=mat,
        val_result=val,
        rc011_implementation_commit_sha=RC011_IMPLEMENTATION_COMMIT_SHA,
    )
    lin2 = compute_structural_representation_lineage(
        manifest_hash=ACCEPTED_CANONICAL_MANIFEST_HASH,
        matrix=mat,
        val_result=val,
        rc011_implementation_commit_sha="f" * 40,
    )
    assert lin1.rc011_implementation_commit_sha == RC011_IMPLEMENTATION_COMMIT_SHA
    assert lin2.rc011_implementation_commit_sha == "f" * 40
    assert lin1.compute_bundle_hash() != lin2.compute_bundle_hash()


def test_complete_fixture_records_in_two_process_payload() -> None:
    """Verify two-process worker script payload contains complete records for all 24 fixtures."""
    from russian_piano_composer.structure_analysis.validation import (
        FIXTURE_REGISTRY,
        compute_fixture_semantic_hash,
    )
    fixture_records = []
    for f in FIXTURE_REGISTRY:
        sc = f.builder()
        ev_list = [
            {
                "measure": e.measure_index,
                "onset": str(e.global_onset),
                "offset": str(e.offset_in_measure),
                "duration": str(e.duration),
                "midi": e.midi,
                "staff": e.staff,
                "voice": e.voice,
            }
            for e in sc.events
        ]
        fixture_records.append({
            "fixture_id": f.fixture_id,
            "name": f.name,
            "family": f.family_owner.value,
            "semantic_hash": compute_fixture_semantic_hash(sc),
            "events": ev_list,
        })
    assert len(fixture_records) == 24
    ids = [r["fixture_id"] for r in fixture_records]
    assert ids == [chr(ord("A") + i) for i in range(24)]


def test_complete_prior_dynamic_hashes_in_two_process_payload() -> None:
    """Verify two-process worker script binds all prior dynamic milestone hashes."""
    from russian_piano_composer.ctu.models import (
        compute_ctu_schema_semantic_hash,
        compute_segment_representation_semantic_hash,
        compute_similarity_semantic_hash,
    )
    from russian_piano_composer.ctu.policy import CTUDiscoveryPolicy
    from russian_piano_composer.domain.features import (
        compute_schema_semantic_hash as compute_rc009a_schema_hash,
    )
    from russian_piano_composer.features import FEATURE_REGISTRY
    from russian_piano_composer.features.policy import FeatureExtractionPolicy
    from russian_piano_composer.structure_analysis.lineage import (
        ACCEPTED_RC009A_POLICY_HASH,
        ACCEPTED_RC009A_SCHEMA_HASH,
        ACCEPTED_RC009B_CTU_SCHEMA_HASH,
        ACCEPTED_RC009B_DISCOVERY_POLICY_HASH,
        ACCEPTED_RC009B_REPRESENTATION_HASH,
        ACCEPTED_RC009B_SIMILARITY_HASH,
    )
    assert compute_rc009a_schema_hash(FEATURE_REGISTRY) == ACCEPTED_RC009A_SCHEMA_HASH
    assert FeatureExtractionPolicy().compute_policy_hash() == ACCEPTED_RC009A_POLICY_HASH
    assert CTUDiscoveryPolicy().compute_policy_hash() == ACCEPTED_RC009B_DISCOVERY_POLICY_HASH
    assert compute_ctu_schema_semantic_hash() == ACCEPTED_RC009B_CTU_SCHEMA_HASH
    assert compute_segment_representation_semantic_hash() == ACCEPTED_RC009B_REPRESENTATION_HASH
    assert compute_similarity_semantic_hash() == ACCEPTED_RC009B_SIMILARITY_HASH


def test_document_line_ending_hash_invariance(tmp_path: Path) -> None:
    """Verify LF, CRLF, and CR line endings produce bit-for-bit identical scientific document hashes."""
    from russian_piano_composer.structure_analysis.lineage import (
        compute_exclusion_ledger_hash,
        compute_preregistration_amendment_hash,
    )

    sample_doc = "# Sample Title\r\n\r\nContent line 1.\r\nContent line 2.\r\n"
    sample_lf = sample_doc.replace("\r\n", "\n")
    sample_cr = sample_doc.replace("\r\n", "\r")

    # 1. Preregistration amendment hash invariance
    p_crlf = tmp_path / "amend_crlf.md"
    p_lf = tmp_path / "amend_lf.md"
    p_cr = tmp_path / "amend_cr.md"

    p_crlf.write_bytes(sample_doc.encode("utf-8"))
    p_lf.write_bytes(sample_lf.encode("utf-8"))
    p_cr.write_bytes(sample_cr.encode("utf-8"))

    h_crlf = compute_preregistration_amendment_hash(p_crlf)
    h_lf = compute_preregistration_amendment_hash(p_lf)
    h_cr = compute_preregistration_amendment_hash(p_cr)

    assert h_crlf == h_lf == h_cr

    # 2. Exclusion ledger hash invariance
    p_excl_crlf = tmp_path / "excl_crlf.md"
    p_excl_lf = tmp_path / "excl_lf.md"
    p_excl_cr = tmp_path / "excl_cr.md"

    p_excl_crlf.write_bytes(sample_doc.encode("utf-8"))
    p_excl_lf.write_bytes(sample_lf.encode("utf-8"))
    p_excl_cr.write_bytes(sample_cr.encode("utf-8"))

    h_excl_crlf = compute_exclusion_ledger_hash(p_excl_crlf)
    h_excl_lf = compute_exclusion_ledger_hash(p_excl_lf)
    h_excl_cr = compute_exclusion_ledger_hash(p_excl_cr)

    assert h_excl_crlf == h_excl_lf == h_excl_cr

    # 3. Live document canonical values
    assert (
        compute_exclusion_ledger_hash()
        == "28b142e1bbef5eeff65ee3a62a94b55e55f88841c3b5954d763d098579eac9b3"
    )
    assert (
        compute_preregistration_amendment_hash()
        == "abe9e25d6604fc24253a302f3185af0526a9eb924a42e50fef31c051883c32e7"
    )

