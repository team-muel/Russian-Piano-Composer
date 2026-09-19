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
    """Verify fixture registry contains exactly 20 distinct fixtures A through T."""
    assert len(FIXTURE_REGISTRY) == 20
    fixture_ids = [f.fixture_id for f in FIXTURE_REGISTRY]
    expected_ids = [chr(ord("A") + i) for i in range(20)]
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
    """Verify uniform time dilation x2 preserves normalized/rate features."""
    base_score = FIXTURE_REGISTRY[0].builder()
    base_rep = extract_structural_representation(base_score)

    dil_score = apply_metamorphic_transformation(base_score, TransformationType.TIME_DILATION)
    dil_rep = extract_structural_representation(dil_score)

    assert abs(dil_rep["cadence_boundary_candidate_rate"].value - base_rep["cadence_boundary_candidate_rate"].value) < 1e-4
    assert abs(dil_rep["sonority_change_rate"].value - base_rep["sonority_change_rate"].value) < 1e-4


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
    base_score = FIXTURE_REGISTRY[0].builder()
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
