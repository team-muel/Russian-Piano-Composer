"""
Comprehensive Unit Tests for RC-011 Structural Music Representation.
"""

from russian_piano_composer.structure_analysis.extractor import extract_structural_representation
from russian_piano_composer.structure_analysis.schema import (
    STRUCTURAL_FEATURE_CATALOG,
    AvailabilityStatus,
    compute_structural_schema_hash,
)
from russian_piano_composer.structure_analysis.validation import (
    SyntheticFixtureFactory,
    build_synthetic_score,
    run_synthetic_validation_suite,
)


def test_structural_schema_hash_determinism() -> None:
    """Verify compute_structural_schema_hash is deterministic and ordering-invariant."""
    h1 = compute_structural_schema_hash()
    h2 = compute_structural_schema_hash(tuple(reversed(STRUCTURAL_FEATURE_CATALOG)))
    assert len(h1) == 64
    assert h1 == h2


def test_synthetic_validation_suite_all_pass() -> None:
    """Verify synthetic fixtures and metamorphic invariance contracts pass."""
    val_res = run_synthetic_validation_suite()
    assert val_res.failed_assertions == 0
    assert val_res.metamorphic_checks_passed == val_res.metamorphic_checks_total
    assert val_res.overall_status == "STRUCTURAL_REPRESENTATION_VALIDATED"


def test_c_major_vs_transposed_harmonic_invariance() -> None:
    """Verify tonic-relative harmonic features remain invariant under transposition."""
    factory = SyntheticFixtureFactory()
    rep_a = extract_structural_representation(factory.fixture_a_c_major_progression())
    rep_b = extract_structural_representation(factory.fixture_b_transposed_progression())

    assert abs(rep_a.features["tonal_global_confidence"].value - rep_b.features["tonal_global_confidence"].value) < 1e-4
    assert abs(rep_a.features["tonal_chromatic_duration_share"].value - rep_b.features["tonal_chromatic_duration_share"].value) < 1e-4
    assert abs(rep_a.features["sonority_pc_cardinality_mean"].value - rep_b.features["sonority_pc_cardinality_mean"].value) < 1e-4


def test_block_chord_vs_arpeggio_semantic_contrast() -> None:
    """Verify block chord and arpeggio features discriminate texture despite identical PC content."""
    factory = SyntheticFixtureFactory()
    rep_g = extract_structural_representation(factory.fixture_g_block_chord())
    rep_h = extract_structural_representation(factory.fixture_h_arpeggio())

    assert rep_g.features["texture_block_chord_share"].value > 0.90
    assert rep_h.features["texture_block_chord_share"].value < 0.10
    assert rep_h.features["texture_arpeggiation_proxy_rate"].value > rep_g.features["texture_arpeggiation_proxy_rate"].value


def test_aba_formal_return_higher_than_through_composed() -> None:
    """Verify formal return proxy captures recapitulatory return."""
    factory = SyntheticFixtureFactory()
    rep_n = extract_structural_representation(factory.fixture_n_aba_recurrence())
    rep_o = extract_structural_representation(factory.fixture_o_through_composed())

    assert rep_n.features["form_return_late_strength"].value > 0.80
    assert rep_n.features["form_return_late_strength"].value > rep_o.features["form_return_late_strength"].value


def test_register_trajectory_slope_ascent_vs_descent() -> None:
    """Verify linear trajectory slope reflects registral ascent and descent."""
    factory = SyntheticFixtureFactory()
    rep_p = extract_structural_representation(factory.fixture_p_upward_register_trajectory())
    rep_q = extract_structural_representation(factory.fixture_q_downward_register_trajectory())

    assert rep_p.features["traj_register_center_slope"].value > 0
    assert rep_q.features["traj_register_center_slope"].value < 0


def test_single_note_score_handles_unavailable_structural_zero() -> None:
    """Verify sparse/minimal score returns structured statuses rather than crashing."""
    from fractions import Fraction
    minimal_score = build_synthetic_score(
        [(60, 0, Fraction(0, 1), Fraction(1, 1))],
        measure_count=1,
        entry_id="single_note",
    )

    rep = extract_structural_representation(minimal_score)
    assert rep.features["tonal_global_confidence"].status == AvailabilityStatus.AVAILABLE
    assert rep.features["tonal_center_change_rate"].status == AvailabilityStatus.STRUCTURAL_ZERO
    assert rep.features["form_ctu_first_occurrence_mean"].status == AvailabilityStatus.STRUCTURAL_ZERO

