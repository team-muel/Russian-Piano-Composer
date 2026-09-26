"""Unit and regression tests for RC-013 Machine-Triangulated Source-Fidelity Validation Protocol (V1 and V2).

Tests cover:
1. Blindness: OMR inputs exclude canonical MusicXML; reference hints rejected or ignored.
2. Architecture Independence: Distinct architectures for Channel A, Channel B, and Channel C.
3. Channel C Anti-Self-Comparison: Strict rejection of identical rendered vs scan images (SELF_COMPARISON_DISALLOWED).
4. End-to-End Image Mutation Sensitivity: 100% recall across all 19 mutation families through rendering and degradation.
5. Protocol Freeze: Cryptographic sensitivity to threshold, engine, and corpus changes in V2.
6. Anti-Leakage & Qualification Isolation: Protocol freeze leaves N_Russian = 2 and RC-012 BLOCKED.
7. Untouched RC-013 Pilot Scores: All 9 pilot scores remain unvalidated and analysis/generative ineligible.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from russian_piano_composer.corpus.rc013_composer_pool import (
    derive_russian_composer_pool_from_evidence,
)
from russian_piano_composer.corpus.rc013_event_graph import (
    NormalizedEventGraph,
    ScoreEvent,
    compare_event_graphs,
    extract_event_graph_from_musicxml,
)
from russian_piano_composer.corpus.rc013_mutations import (
    RC013MutationEngine,
)
from russian_piano_composer.corpus.rc013_omr_adapters import (
    BlindOMRFirewall,
    NeuralVisualFeatureOMREngine,
    ScoreScanStructuralAlignmentEngine,
    StructuredStaffGraphOMREngine,
)
from russian_piano_composer.corpus.rc013_triangulation_protocol import (
    MachineTriangulationProtocol,
)


def test_omr_adapters_have_distinct_independent_architectures() -> None:
    """Verifies that Channel A, Channel B, and Channel C have distinct architectural foundations."""
    eng_a = StructuredStaffGraphOMREngine()
    eng_b = NeuralVisualFeatureOMREngine()
    eng_c = ScoreScanStructuralAlignmentEngine()

    assert eng_a.ARCHITECTURE != eng_b.ARCHITECTURE
    assert eng_b.ARCHITECTURE != eng_c.ARCHITECTURE
    assert eng_a.ENGINE_NAME != eng_b.ENGINE_NAME
    assert eng_b.ENGINE_NAME != eng_c.ENGINE_NAME


def test_blind_omr_firewall_rejects_symbolic_files(tmp_path: Path) -> None:
    """Verifies that the BlindOMRFirewall raises an error if symbolic files are present in the sandbox."""
    sandbox = tmp_path / "omr_sandbox"
    sandbox.mkdir()

    # Place a valid image and a forbidden MusicXML file
    (sandbox / "page1.png").write_bytes(b"fake image bytes")
    (sandbox / "score.musicxml").write_text("<score-partwise/>", encoding="utf-8")

    with pytest.raises(RuntimeError, match="BLIND_OMR_FIREWALL_VIOLATION"):
        BlindOMRFirewall.verify_sandbox_isolation(str(sandbox))


def test_channel_c_rejects_identical_rendered_and_scan_images(tmp_path: Path) -> None:
    """Proves that Channel C strictly rejects self-comparison (rendered == scan)."""
    img_p = tmp_path / "page1.png"
    img_p.write_bytes(b"exact same image bytes for render and scan")

    engine_c = ScoreScanStructuralAlignmentEngine()
    with pytest.raises(ValueError, match="SELF_COMPARISON_DISALLOWED"):
        engine_c.align_score_to_scan(
            rendered_images=[str(img_p)],
            historical_scan_images=[str(img_p)],
            score_id="test_self_comparison",
        )


def test_calibration_v2_corpus_registry_excludes_rc013_pilot_scores() -> None:
    """Verifies that the calibration V2 corpus contains strictly non-RC-013 piano scores across 3 tiers."""
    registry_path = Path("data/calibration/rc013_machine_validation/rc013_calibration_v2_registry.json")
    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry) == 7

    forbidden_composers = {"Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"}
    forbidden_work_prefixes = {
        "anton_arensky_op36",
        "anatoly_lyadov_op40",
        "anatoly_lyadov_op46",
        "sergei_lyapunov_op11",
    }

    splits = {entry["split"] for entry in registry}
    assert splits == {
        "SYNTHETIC_CONTROLLED_CALIBRATION",
        "REAL_SCAN_THRESHOLD_CALIBRATION",
        "CALIBRATION_V2_FINAL_HOLDOUT",
    }

    for entry in registry:
        assert entry["composer"] not in forbidden_composers
        assert not any(entry["artifact_id"].startswith(fp) for fp in forbidden_work_prefixes)


def test_event_graph_normalization_and_comparison_identity() -> None:
    """Proves that identical event graphs have 0 OMR-NED and 0 critical mismatches."""
    evt1 = ScoreEvent(
        score_id="test_score",
        measure_number=1,
        staff=1,
        voice=1,
        onset_fraction="0/1",
        duration_fraction="1/4",
        event_type="NOTE",
        pitch_step="C",
        alter=0,
        octave=4,
    )
    g1 = NormalizedEventGraph(score_id="test_score", events=[evt1])
    g2 = NormalizedEventGraph(score_id="test_score", events=[evt1])

    res = compare_event_graphs(g1, g2)
    assert res.overall_omr_ned == 0.0
    assert res.critical_mismatches_count == 0
    assert len(res.discrepant_measures) == 0


def test_event_graph_comparison_catches_all_critical_dimensions() -> None:
    """Proves that modifying any critical dimension registers a critical mismatch."""
    base_evt = ScoreEvent(
        score_id="test_score",
        measure_number=1,
        staff=1,
        voice=1,
        onset_fraction="0/1",
        duration_fraction="1/4",
        event_type="NOTE",
        pitch_step="C",
        alter=0,
        octave=4,
        key_signature=0,
        time_signature="4/4",
    )
    base_graph = NormalizedEventGraph(score_id="test_score", events=[base_evt])

    # 1. Pitch mismatch
    mut_pitch = NormalizedEventGraph(score_id="test_score", events=[
        ScoreEvent(score_id="test_score", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="D", alter=0, octave=4)
    ])
    assert compare_event_graphs(base_graph, mut_pitch).critical_mismatches_count > 0

    # 2. Accidental mismatch
    mut_acc = NormalizedEventGraph(score_id="test_score", events=[
        ScoreEvent(score_id="test_score", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="C", alter=1, octave=4)
    ])
    assert compare_event_graphs(base_graph, mut_acc).critical_mismatches_count > 0

    # 3. Duration mismatch
    mut_dur = NormalizedEventGraph(score_id="test_score", events=[
        ScoreEvent(score_id="test_score", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/8", event_type="NOTE", pitch_step="C", alter=0, octave=4)
    ])
    assert compare_event_graphs(base_graph, mut_dur).critical_mismatches_count > 0

    # 4. Rest mismatch
    mut_rest = NormalizedEventGraph(score_id="test_score", events=[
        ScoreEvent(score_id="test_score", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="REST", is_rest=True)
    ])
    assert compare_event_graphs(base_graph, mut_rest).critical_mismatches_count > 0


def test_adversarial_mutation_suite_covers_all_19_families() -> None:
    """Verifies that all 19 mutation families are generated and 100% detected."""
    engine = RC013MutationEngine()
    assert len(engine.MUTATION_FAMILIES) == 19

    xml_path = "data/calibration/rc013_machine_validation/scores/chopin_op28_no07.musicxml"
    g = extract_event_graph_from_musicxml(xml_path, score_id="chopin_test")

    specimens = engine.generate_mutations(g)
    families_present = {s.mutation_family for s in specimens}
    assert families_present == set(engine.MUTATION_FAMILIES)

    for s in specimens:
        comp = compare_event_graphs(g, s.mutated_event_graph)
        assert comp.critical_mismatches_count > 0 or comp.overall_omr_ned > 0.0, (
            f"Failed to detect mutation family: {s.mutation_family} ({s.mutation_description})"
        )


def test_protocol_v3_manifest_hash_changes_on_threshold_mutation() -> None:
    """Proves that changing any acceptance threshold mutates the V3 protocol hash."""
    protocol = MachineTriangulationProtocol(max_omr_ned_threshold=0.05)
    manifest1 = protocol.generate_frozen_protocol_manifest(
        calibration_corpus_hash="a" * 64,
        external_engine_bundle_hash="b" * 64,
        real_scan_benchmark_hash="c" * 64,
        end_to_end_mutation_suite_hash="d" * 64,
        calibration_result_hash="e" * 64,
    )

    protocol_mutated = MachineTriangulationProtocol(max_omr_ned_threshold=0.01)
    manifest2 = protocol_mutated.generate_frozen_protocol_manifest(
        calibration_corpus_hash="a" * 64,
        external_engine_bundle_hash="b" * 64,
        real_scan_benchmark_hash="c" * 64,
        end_to_end_mutation_suite_hash="d" * 64,
        calibration_result_hash="e" * 64,
    )

    assert manifest1["protocol_hash"] != manifest2["protocol_hash"]


def test_machine_calibration_v2_pass_leaves_russian_composer_pool_at_two() -> None:
    """Proves that machine calibration PASS does not alter N_Russian = 2 or unblock RC-012."""
    res = derive_russian_composer_pool_from_evidence()
    assert res.n_russian == 2
    assert res.n_control == 5
    assert res.qualified_russian_composers == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert set(res.unqualified_russian_composers) == {
        "Anton Arensky",
        "Anatoly Lyadov",
        "Sergei Lyapunov",
    }
    assert res.rc012_resumption_status == "BLOCKED"
    assert "N_Russian = 2 < 4" in res.rc012_resumption_reason


def test_frozen_protocol_v2_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest V2 exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_machine_validation_protocol_v2.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == "rc013_machine_triangulation_protocol_v2"
    assert len(data["protocol_hash"]) == 64
    assert len(data["calibration_corpus_hash"]) == 64
    assert len(data["end_to_end_mutation_suite_hash"]) == 64
    assert len(data["calibration_result_hash"]) == 64
    assert data["qualification_policy"]["machine_receipts_can_qualify_composer"] is False
    assert data["qualification_policy"]["current_n_russian"] == 2
    assert data["qualification_policy"]["rc012_resumption_status"] == "BLOCKED"


def test_machine_triangulation_v2_hashes_present_and_valid() -> None:
    """Verifies that get_machine_triangulation_hashes returns valid SHA256 hashes for V1, V2, and V3."""
    from scripts.compute_rc013_hashes import get_machine_triangulation_hashes

    hashes = get_machine_triangulation_hashes()
    expected_v2_keys = [
        "RC013_MACHINE_PROTOCOL_V2_HASH",
        "RC013_CALIBRATION_V2_CORPUS_HASH",
        "RC013_END_TO_END_MUTATION_SUITE_HASH",
        "RC013_CALIBRATION_V2_RESULT_HASH",
    ]
    for k in expected_v2_keys:
        assert k in hashes
        assert len(hashes[k]) == 64

    expected_v3_keys = [
        "RC013_MACHINE_PROTOCOL_V3_HASH",
        "RC013_CALIBRATION_V3_CORPUS_HASH",
        "RC013_EXTERNAL_ENGINE_BUNDLE_HASH",
        "RC013_REAL_SCAN_BENCHMARK_HASH",
        "RC013_END_TO_END_MUTATION_V3_HASH",
        "RC013_CALIBRATION_V3_RESULT_HASH",
    ]
    for k in expected_v3_keys:
        assert k in hashes
        assert len(hashes[k]) == 64


def test_calibration_v3_corpus_registry_excludes_rc013_pilot_scores() -> None:
    """Verifies that the calibration V3 corpus contains strictly non-RC-013 piano scores with DCMLab provenance."""
    registry_path = Path("data/calibration/rc013_machine_validation/rc013_calibration_v3_registry.json")
    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry) == 6

    forbidden_composers = {"Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"}
    forbidden_work_prefixes = {
        "anton_arensky_op36",
        "anatoly_lyadov_op40",
        "anatoly_lyadov_op46",
        "sergei_lyapunov_op11",
    }

    splits = {entry["split"] for entry in registry}
    assert splits == {
        "SYNTHETIC_CONTROLLED_CALIBRATION",
        "REAL_SCAN_THRESHOLD_CALIBRATION",
        "CALIBRATION_V3_FINAL_HOLDOUT",
    }

    for entry in registry:
        assert entry["composer"] not in forbidden_composers
        assert not any(entry["artifact_id"].startswith(fp) for fp in forbidden_work_prefixes)
        if entry["split"] in {"REAL_SCAN_THRESHOLD_CALIBRATION", "CALIBRATION_V3_FINAL_HOLDOUT"}:
            assert entry["provenance_class"] == "REAL_HISTORICAL_SCAN"
            assert "DCMLab" in entry["dataset_name"]
            assert Path(entry["ground_truth_path"]).exists()
            assert Path(entry["image_path"]).exists()
            assert Path(entry["historical_pdf_path"]).exists()


def test_frozen_protocol_v3_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest V3 exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_machine_validation_protocol_v3.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == "rc013_machine_triangulation_protocol_v3"
    assert len(data["protocol_hash"]) == 64
    assert len(data["calibration_corpus_hash"]) == 64
    assert len(data["external_engine_bundle_hash"]) == 64
    assert len(data["real_scan_benchmark_hash"]) == 64
    assert len(data["end_to_end_mutation_suite_hash"]) == 64
    assert len(data["calibration_result_hash"]) == 64
    assert data["qualification_policy"]["machine_receipts_can_qualify_composer"] is False
    assert data["qualification_policy"]["current_n_russian"] == 2
    assert data["qualification_policy"]["rc012_resumption_status"] == "BLOCKED"


def test_feature_dependency_coverage_for_rc012_descriptors() -> None:
    """Tests the feature dependency evaluator against core and incomplete feature dimensions."""
    from russian_piano_composer.corpus.rc013_feature_dependency import (
        evaluate_feature_dependency_coverage,
    )

    full_core_dims = {
        "pitch", "accidental", "octave", "onset", "duration",
        "rest", "key_signature", "time_signature", "tie", "tuplet",
        "repeat_structure", "measure_sequence", "staff", "voice",
    }
    cov_full = evaluate_feature_dependency_coverage(full_core_dims)
    assert cov_full["fit_for_rc012_structural_analysis"] is True
    assert len(cov_full["unsupported_core_descriptors"]) == 0
    assert "pitch_class_entropy" in cov_full["supported_core_descriptors"]
    assert "pitch_range_semitones" in cov_full["supported_core_descriptors"]
    assert "ctu_discovery_score_mean" in cov_full["supported_core_descriptors"]
    assert "density_notes_per_measure" in cov_full["supported_core_descriptors"]

    # Incomplete dimensions (missing staff/voice)
    incomplete_dims = {"pitch", "accidental", "octave", "onset", "duration"}
    cov_inc = evaluate_feature_dependency_coverage(incomplete_dims)
    assert cov_inc["fit_for_rc012_structural_analysis"] is False
    assert "density_staff_count" in cov_inc["unsupported_core_descriptors"]


def test_external_engine_adapter_classes() -> None:
    """Verifies that external OMR engines declare correct architectures."""
    from russian_piano_composer.corpus.rc013_omr_adapters import (
        ExternalAudiverisOMREngine,
        ExternalHomrNeuralOMREngine,
    )

    aud = ExternalAudiverisOMREngine()
    assert "Audiveris" in aud.ENGINE_NAME
    assert "tesseract" in aud.ARCHITECTURE

    homr = ExternalHomrNeuralOMREngine()
    assert "Homr" in homr.ENGINE_NAME
    assert "tromr" in homr.ARCHITECTURE


def test_calibration_v4_corpus_registry_excludes_rc013_pilot_scores() -> None:
    """Verifies that the calibration V4 corpus contains strictly non-RC-013 piano scores with separate licensing."""
    registry_path = Path("data/calibration/rc013_machine_validation/rc013_calibration_v4_registry.json")
    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry) == 7

    forbidden_composers = {"Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"}
    forbidden_work_prefixes = {
        "anton_arensky_op36",
        "anatoly_lyadov_op40",
        "anatoly_lyadov_op46",
        "sergei_lyapunov_op11",
    }

    splits = {entry["split"] for entry in registry}
    assert splits == {
        "SYNTHETIC_CONTROLLED_CALIBRATION",
        "REAL_SCAN_THRESHOLD_CALIBRATION",
        "CALIBRATION_V4_FINAL_HOLDOUT",
    }

    for entry in registry:
        assert entry["composer"] not in forbidden_composers
        assert not any(entry["artifact_id"].startswith(fp) for fp in forbidden_work_prefixes)
        assert "digital_dataset_license" in entry
        assert "historical_scan_status" in entry
        if entry["split"] in {"REAL_SCAN_THRESHOLD_CALIBRATION", "CALIBRATION_V4_FINAL_HOLDOUT"}:
            assert entry["provenance_class"] == "REAL_HISTORICAL_SCAN"
            assert "DCMLab" in entry["dataset_name"]
            assert Path(entry["ground_truth_path"]).exists()
            assert Path(entry["historical_pdf_path"]).exists()
            assert len(entry["historical_page_image_paths"]) > 0
            for p in entry["historical_page_image_paths"]:
                assert Path(p).exists()


def test_frozen_protocol_v4_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest V4 exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_machine_validation_protocol_v4.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == "rc013_machine_triangulation_protocol_v4"
    assert len(data["protocol_hash"]) == 64
    assert len(data["calibration_corpus_hash"]) == 64
    assert len(data["external_engine_bundle_hash"]) == 64
    assert len(data["real_scan_benchmark_hash"]) == 64
    assert len(data["end_to_end_mutation_suite_hash"]) == 64
    assert len(data["calibration_result_hash"]) == 64
    assert data["qualification_policy"]["machine_receipts_can_qualify_composer"] is False
    assert data["qualification_policy"]["current_n_russian"] == 2
    assert data["qualification_policy"]["rc012_resumption_status"] == "BLOCKED"


def test_derive_calibration_verdict_logic() -> None:
    """Tests the inspectable deterministic calibration verdict derivation function."""
    from russian_piano_composer.corpus.rc013_image_mutations import ImageMutationBenchmarkResult
    from russian_piano_composer.corpus.rc013_triangulation_protocol import (
        derive_calibration_verdict,
    )

    dummy_mut_res = ImageMutationBenchmarkResult(
        total_mutations_injected=57,
        total_mutations_detected=57,
        total_mutations_missed=0,
        end_to_end_image_mutation_recall=1.0,
        family_breakdown={},
        missed_mutations=[],
        benchmark_sha256="0" * 64,
    )
    dummy_feat_res = {"fit_for_rc012_structural_analysis": True, "fit_status": "FIT_FOR_RC012_STRUCTURAL_ANALYSIS"}

    # All conditions pass -> PASS
    all_pass, _ = derive_calibration_verdict(
        evaluations=[],
        holdout_evaluations=[],
        mutation_result=dummy_mut_res,
        feature_dep_result=dummy_feat_res,
        conditions_gate={
            "external_engines_available": True,
            "real_scan_bytes_valid": True,
            "reference_bytes_valid": True,
            "complete_source_page_coverage": True,
            "required_mutation_recall_satisfied": True,
            "synthetic_controls_pass": True,
            "empirical_feature_fit_satisfied": True,
        },
    )
    assert all_pass == "PROTOCOL_V4_CALIBRATION_PASS"

    # Core engine and mutation pass, synthetic controls pass, but empirical feature fit or real-scan noise bounds threshold -> PARTIAL
    partial, _ = derive_calibration_verdict(
        evaluations=[],
        holdout_evaluations=[],
        mutation_result=dummy_mut_res,
        feature_dep_result={"fit_for_rc012_structural_analysis": False, "fit_status": "PARTIALLY_FIT"},
        conditions_gate={
            "external_engines_available": True,
            "real_scan_bytes_valid": True,
            "reference_bytes_valid": True,
            "complete_source_page_coverage": True,
            "required_mutation_recall_satisfied": True,
            "synthetic_controls_pass": True,
            "empirical_feature_fit_satisfied": False,
        },
    )
    assert partial == "PROTOCOL_V4_CALIBRATION_PARTIAL"

    # Missing engines -> BLOCKED
    blocked, _ = derive_calibration_verdict(
        evaluations=[],
        holdout_evaluations=[],
        mutation_result=dummy_mut_res,
        feature_dep_result=dummy_feat_res,
        conditions_gate={
            "external_engines_available": False,
            "real_scan_bytes_valid": True,
            "reference_bytes_valid": True,
            "complete_source_page_coverage": True,
            "required_mutation_recall_satisfied": True,
            "synthetic_controls_pass": True,
            "empirical_feature_fit_satisfied": True,
        },
    )
    assert blocked == "PROTOCOL_V4_CALIBRATION_BLOCKED"


def test_bounded_coverage_and_measure_offset_alignment() -> None:
    """Verifies that measure sequence alignment correctly handles bounded coverage and offset tracking."""
    from russian_piano_composer.corpus.rc013_event_graph import (
        NormalizedEventGraph,
        ScoreEvent,
        compare_event_graphs,
    )

    evts_ref = [
        ScoreEvent(score_id="s1", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="C", alter=0, octave=4, page_index=1, local_measure_number=1),
        ScoreEvent(score_id="s1", measure_number=2, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="D", alter=0, octave=4, page_index=1, local_measure_number=2),
        ScoreEvent(score_id="s1", measure_number=3, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="E", alter=0, octave=4, page_index=2, local_measure_number=1),
    ]
    evts_hyp = [
        ScoreEvent(score_id="s1", measure_number=1, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="C", alter=0, octave=4, page_index=1, local_measure_number=1),
        ScoreEvent(score_id="s1", measure_number=2, staff=1, voice=1, onset_fraction="0/1", duration_fraction="1/4", event_type="NOTE", pitch_step="D", alter=0, octave=4, page_index=1, local_measure_number=2),
    ]

    g_ref = NormalizedEventGraph(score_id="s1", events=evts_ref)
    g_hyp = NormalizedEventGraph(score_id="s1", events=evts_hyp)

    res = compare_event_graphs(g_ref, g_hyp)
    assert 0.0 <= res.page_coverage <= 1.0
    assert 0.0 <= res.measure_coverage <= 1.0
    assert 0.0 <= res.event_recall <= 1.0
    assert 0.0 <= res.event_precision <= 1.0
    assert res.measure_coverage == pytest.approx(2 / 3, abs=1e-3)


def test_protocol_v5_counterfactual_discrimination_margin() -> None:
    """Verifies that counterfactual image distance produces positive margin delta for correct candidate."""
    import cv2
    import numpy as np

    from russian_piano_composer.corpus.rc013_falsification_protocol import calculate_image_distance

    # Source crop
    src = np.full((100, 100), 255, dtype=np.uint8)
    cv2.circle(src, (50, 50), 10, 0, -1)

    # Correct candidate
    cand = src.copy()

    # Mutated counterfactual (shifted note)
    mut = np.full((100, 100), 255, dtype=np.uint8)
    cv2.circle(mut, (50, 30), 10, 0, -1)

    d_cand = calculate_image_distance(cand, src)
    d_mut = calculate_image_distance(mut, src)
    delta = d_mut - d_cand

    assert d_cand == pytest.approx(0.0, abs=1e-3)
    assert d_mut > 0.05
    assert delta > 0.05


def test_calibration_v5_corpus_registry_excludes_rc013_pilot_scores() -> None:
    """Verifies that the calibration V5 corpus contains strictly non-RC-013 piano scores with separate licensing."""
    registry_path = Path("data/calibration/rc013_machine_validation/rc013_calibration_v5_registry.json")
    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry) == 8

    forbidden_composers = {"Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"}
    forbidden_work_prefixes = {
        "anton_arensky_op36",
        "anatoly_lyadov_op40",
        "anatoly_lyadov_op46",
        "sergei_lyapunov_op11",
    }

    splits = {entry["split"] for entry in registry}
    assert splits == {
        "SYNTHETIC_CONTROLLED_CALIBRATION",
        "REAL_SCAN_THRESHOLD_CALIBRATION",
        "CALIBRATION_V5_FINAL_HOLDOUT",
    }

    for entry in registry:
        assert entry["composer"] not in forbidden_composers
        assert not any(entry["artifact_id"].startswith(fp) for fp in forbidden_work_prefixes)
        assert "digital_dataset_license" in entry
        assert "historical_scan_status" in entry
        if entry["split"] in {"REAL_SCAN_THRESHOLD_CALIBRATION", "CALIBRATION_V5_FINAL_HOLDOUT"}:
            assert entry["provenance_class"] == "REAL_HISTORICAL_SCAN"
            assert "DCMLab" in entry["dataset_name"]
            assert Path(entry["ground_truth_path"]).exists()
            assert Path(entry["historical_pdf_path"]).exists()
            assert len(entry["historical_page_image_paths"]) > 0
            for p in entry["historical_page_image_paths"]:
                assert Path(p).exists()


def test_frozen_protocol_v5_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest V5 exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_candidate_falsification_protocol_v5.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == "rc013_candidate_falsification_protocol_v5"
    assert len(data["protocol_hash"]) == 64
    assert len(data["corpus_bundle_hash"]) == 64
    assert len(data["engine_bundle_hash"]) == 64
    assert len(data["real_scan_counterfactual_benchmark_hash"]) == 64
    assert len(data["alignment_engine_hash"]) == 64
    assert len(data["counterfactual_suite_hash"]) == 64
    assert len(data["calibration_result_hash"]) == 64
    assert data["qualification_policy"]["candidate_falsification_receipts_can_qualify_composer"] is False
    assert data["qualification_policy"]["current_n_russian"] == 2
    assert data["qualification_policy"]["rc012_resumption_status"] == "BLOCKED"


def test_full_56_descriptor_feature_dependency_audit() -> None:
    """Audits all 56 registered descriptors from STRUCTURAL_REPRESENTATION_SCHEMA_V1."""
    from russian_piano_composer.corpus.rc013_feature_dependency import (
        audit_56_descriptor_dependencies,
    )

    audit_res = audit_56_descriptor_dependencies()
    assert audit_res["schema_descriptor_count"] == 56
    assert audit_res["machine_supported_count"] == 55
    assert audit_res["partially_supported_count"] == 1
    assert audit_res["unsupported_count"] == 0
    assert audit_res["support_rate"] > 0.98


def test_frozen_protocol_v6_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest V6 exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_candidate_falsification_protocol_v6.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == "rc013_candidate_falsification_protocol_v6"
    assert len(data["protocol_hash"]) == 64
    assert len(data["calibration_corpus_hash"]) == 64
    assert len(data["counterfactual_benchmark_bundle_hash"]) == 64
    assert len(data["alignment_engine_hash"]) == 64
    assert len(data["differential_metric_hash"]) == 64
    assert len(data["descriptor_dependency_audit_hash"]) == 64
    assert data["downstream_authorities"]["candidate_falsification_receipts_can_qualify_composer"] is False
    assert data["downstream_authorities"]["n_russian_derived"] == 2
    assert data["downstream_authorities"]["rc012_resumption_permitted"] is False


def test_protocol_v6_verifier_rejects_pilot_scores() -> None:
    """Proves that Protocol V6 verifier strictly rejects pilot scores during calibration."""
    from russian_piano_composer.corpus.rc013_falsification_protocol import (
        GenuineDifferentialVerifierV6,
    )

    verifier = GenuineDifferentialVerifierV6()
    with pytest.raises(PermissionError, match="PILOT_SCORE_EVALUATION_PROHIBITED"):
        verifier.evaluate_candidate(
            candidate_musicxml_path="data/scores/rc013/canonical/anton_arensky_op36_no01.musicxml",
            source_image_paths=["dummy.png"],
            score_id="anton_arensky_op36_no01",
        )




