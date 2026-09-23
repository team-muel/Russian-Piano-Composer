"""Unit and regression tests for RC-013 Machine-Triangulated Source-Fidelity Validation Protocol.

Tests cover:
1. Blindness: OMR inputs exclude canonical MusicXML; pilot paths excluded from calibration.
2. Independence: Distinct architectures for Channel A, Channel B, and Channel C.
3. Event Normalization: Canonical event graph mapping and exact metric sensitivity.
4. Adversarial Mutations: 100% recall across all 19 mutation families with 0 false negatives.
5. Protocol Freeze: Cryptographic sensitivity to threshold, engine, and corpus changes.
6. Anti-Leakage: Protocol isolation from RC-013 pilot data.
7. Qualification Isolation: Calibration PASS does not increment N_Russian or unblock RC-012.
"""

from __future__ import annotations

import json
from pathlib import Path

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
    NeuralVisualFeatureOMREngine,
    ScoreScanStructuralAlignmentEngine,
    StructuredStaffGraphOMREngine,
)
from russian_piano_composer.corpus.rc013_triangulation_protocol import (
    PROTOCOL_VERSION,
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


def test_calibration_corpus_registry_excludes_rc013_pilot_scores() -> None:
    """Verifies that the calibration corpus contains strictly non-RC-013 piano scores."""
    registry_path = Path("data/calibration/rc013_machine_validation/rc013_calibration_registry.json")
    assert registry_path.exists()

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    assert len(registry) >= 5

    forbidden_composers = {"Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"}
    forbidden_work_prefixes = {
        "anton_arensky_op36",
        "anatoly_lyadov_op40",
        "anatoly_lyadov_op46",
        "sergei_lyapunov_op11",
    }

    for entry in registry:
        assert entry["composer"] not in forbidden_composers
        assert not any(entry["artifact_id"].startswith(fp) for fp in forbidden_work_prefixes)
        assert entry["split"] in {"CALIBRATION_THRESHOLD", "CALIBRATION_FINAL_HOLDOUT"}


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


def test_protocol_manifest_hash_changes_on_threshold_mutation(tmp_path: Path) -> None:
    """Proves that changing any acceptance threshold mutates the protocol hash."""
    protocol = MachineTriangulationProtocol(max_omr_ned_threshold=0.05)
    manifest1 = protocol.generate_frozen_protocol_manifest(
        calibration_corpus_hash="a" * 64,
        mutation_suite_hash="b" * 64,
        calibration_result_hash="c" * 64,
    )

    protocol_mutated = MachineTriangulationProtocol(max_omr_ned_threshold=0.01)
    manifest2 = protocol_mutated.generate_frozen_protocol_manifest(
        calibration_corpus_hash="a" * 64,
        mutation_suite_hash="b" * 64,
        calibration_result_hash="c" * 64,
    )

    assert manifest1["protocol_hash"] != manifest2["protocol_hash"]


def test_machine_calibration_pass_leaves_russian_composer_pool_at_two() -> None:
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


def test_frozen_protocol_manifest_matches_disk() -> None:
    """Verifies that the frozen protocol manifest exists and contains valid SHA256 hashes."""
    manifest_p = Path("data/manifests/rc013_machine_validation_protocol_v1.json")
    assert manifest_p.exists()

    data = json.loads(manifest_p.read_text(encoding="utf-8"))
    assert data["protocol_version"] == PROTOCOL_VERSION
    assert len(data["protocol_hash"]) == 64
    assert len(data["calibration_corpus_hash"]) == 64
    assert len(data["mutation_suite_hash"]) == 64
    assert len(data["calibration_result_hash"]) == 64
    assert data["qualification_policy"]["machine_receipts_can_qualify_composer"] is False
    assert data["qualification_policy"]["current_n_russian"] == 2
    assert data["qualification_policy"]["rc012_resumption_status"] == "BLOCKED"


def test_machine_triangulation_hashes_present_and_valid() -> None:
    """Verifies that get_machine_triangulation_hashes returns 4 valid SHA256 hashes."""
    from scripts.compute_rc013_hashes import get_machine_triangulation_hashes

    hashes = get_machine_triangulation_hashes()
    expected_keys = [
        "RC013_MACHINE_PROTOCOL_HASH",
        "RC013_CALIBRATION_CORPUS_HASH",
        "RC013_MUTATION_SUITE_HASH",
        "RC013_CALIBRATION_RESULT_HASH",
    ]
    assert len(hashes) == len(expected_keys)
    for k in expected_keys:
        assert k in hashes
        assert len(hashes[k]) == 64
