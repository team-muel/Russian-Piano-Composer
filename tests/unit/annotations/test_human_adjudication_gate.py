"""
Unit tests for RC-008C Human Theme Adjudication Gate (Phase A).
Validates role blindness, AI verdict blindness, blank template completeness,
packet hash determinism, importer validation rules, and revision provenance.
"""
from pathlib import Path

import yaml
from scripts.import_human_theme_adjudication import (
    process_adjudicated_annotations,
    validate_human_decision_file,
)
from scripts.prepare_blind_human_review_packet import (
    PILOT_CANDIDATE_HASH,
    PILOT_SELECTION_HASH,
    PROTOCOL_VERSION,
    compute_human_review_packet_hash,
    derive_candidate_digest,
)

from russian_piano_composer.corpus.theme_annotations import load_theme_annotation_manifest
from russian_piano_composer.domain.annotations import AnnotatorType, ThemeRole

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RC008C_DIR = REPO_ROOT / "data/annotations/theme_v1/pilots/rc008c"
DOCS_DIR = REPO_ROOT / "docs/research"


def test_blank_template_has_20_uncompleted_items() -> None:
    template_path = RC008C_DIR / "human_review_template_v1.yaml"
    assert template_path.exists(), "human_review_template_v1.yaml does not exist."

    with open(template_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data.get("human_review_schema_version") == 1
    assert data.get("protocol_version") == 1
    assert data.get("pilot_candidate_annotation_hash") == PILOT_CANDIDATE_HASH
    assert data.get("role_blind") is True
    assert data.get("ai_verdict_blind") is True

    prov = data.get("reviewer_provenance", {})
    assert prov.get("reviewer_id") is None
    assert prov.get("reviewer_type") == "HUMAN"
    assert prov.get("review_completed_at") is None
    assert prov.get("declaration") is None

    decisions = data.get("candidate_decisions", [])
    assert len(decisions) == 20, f"Expected 20 candidate decisions, got {len(decisions)}"

    for dec in decisions:
        d = dec.get("decision", {})
        assert d.get("is_thematic_statement") is None
        assert d.get("start_boundary") is None
        assert d.get("revised_start_measure") is None
        assert d.get("end_boundary") is None
        assert d.get("revised_end_measure") is None
        assert d.get("theme_role") is None
        assert d.get("confidence") is None

    piece_evals = data.get("piece_evaluations", [])
    assert len(piece_evals) == 18, f"Expected 18 piece evaluations, got {len(piece_evals)}"
    for pe in piece_evals:
        assert pe.get("missing_thematic_statement") is None


def test_role_blindness_in_human_artifacts() -> None:
    forbidden_terms = ["GENERATIVE_RUSSIAN", "CONTROL_NON_RUSSIAN"]

    files_to_check = [
        RC008C_DIR / "human_review_template_v1.yaml",
        RC008C_DIR / "human_review_mapping_v1.yaml",
        DOCS_DIR / "THEME_PILOT_V1_HUMAN_REVIEW_FORM.md",
    ]

    for path in files_to_check:
        assert path.exists(), f"File missing: {path}"
        content = path.read_text(encoding="utf-8")
        for term in forbidden_terms:
            assert term not in content, f"Role leak detected in {path.name}: '{term}' found."


def test_ai_verdict_blindness_in_human_artifacts() -> None:
    template_path = RC008C_DIR / "human_review_template_v1.yaml"
    form_path = DOCS_DIR / "THEME_PILOT_V1_HUMAN_REVIEW_FORM.md"

    template_content = template_path.read_text(encoding="utf-8")
    form_content = form_path.read_text(encoding="utf-8")

    # In template, no prefilled AI verdicts or rationale should exist
    assert "ai_music_theory_reviewer" not in template_content
    assert "APPROVE" not in template_content

    # In human review form items, no Pass-A/Pass-B rationale or preselected APPROVE decisions should appear
    assert "Pass A proposal" not in form_content
    assert "Pass B rationale" not in form_content
    assert "ai_music_theory_reviewer" not in form_content


def test_deterministic_order_and_packet_hash_reproducibility() -> None:
    candidates_path = REPO_ROOT / "data/annotations/theme_v1/pilots/rc008b/candidates.yaml"
    annotation_set = load_theme_annotation_manifest(candidates_path)

    digests_1 = [
        derive_candidate_digest(PILOT_SELECTION_HASH, PROTOCOL_VERSION, ann.annotation_id)
        for ann in annotation_set.annotations
    ]
    digests_2 = [
        derive_candidate_digest(PILOT_SELECTION_HASH, PROTOCOL_VERSION, ann.annotation_id)
        for ann in annotation_set.annotations
    ]

    assert digests_1 == digests_2, "Derived candidate digests are not deterministic."

    mapping_path = RC008C_DIR / "human_review_mapping_v1.yaml"
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = yaml.safe_load(f)

    packet_hash_1 = compute_human_review_packet_hash(
        PROTOCOL_VERSION, PILOT_CANDIDATE_HASH, mapping_data["mappings"]
    )
    packet_hash_2 = compute_human_review_packet_hash(
        PROTOCOL_VERSION, PILOT_CANDIDATE_HASH, mapping_data["mappings"]
    )

    assert packet_hash_1 == packet_hash_2
    assert mapping_data["human_review_packet_hash"] == packet_hash_1


def test_importer_rejects_incomplete_template() -> None:
    template_path = RC008C_DIR / "human_review_template_v1.yaml"
    mapping_path = RC008C_DIR / "human_review_mapping_v1.yaml"

    with open(template_path, encoding="utf-8") as f:
        decision_data = yaml.safe_load(f)
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = yaml.safe_load(f)

    valid, errors = validate_human_decision_file(decision_data, mapping_data)
    assert not valid, "Blank template must be rejected by decision importer."
    assert len(errors) > 0

    error_str = " ".join(errors)
    assert "Missing Reviewer ID" in error_str
    assert "Missing Timestamp" in error_str
    assert "Missing Declaration" in error_str
    assert "is_thematic_statement" in error_str


def test_importer_rejects_packet_hash_mismatch() -> None:
    mapping_path = RC008C_DIR / "human_review_mapping_v1.yaml"
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = yaml.safe_load(f)

    fake_decision = {
        "human_review_packet_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "reviewer_provenance": {
            "reviewer_id": "test_human",
            "reviewer_type": "HUMAN",
            "review_completed_at": "2026-09-13T00:00:00Z",
            "declaration": "I certify this is genuine human review.",
        },
        "candidate_decisions": [],
    }

    valid, errors = validate_human_decision_file(fake_decision, mapping_data)
    assert not valid
    assert any("Packet Hash Mismatch" in e for e in errors)


def test_human_revision_provenance_preserves_parent_candidate() -> None:
    candidates_path = REPO_ROOT / "data/annotations/theme_v1/pilots/rc008b/candidates.yaml"
    mapping_path = RC008C_DIR / "human_review_mapping_v1.yaml"

    baseline_manifest = load_theme_annotation_manifest(candidates_path)
    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = yaml.safe_load(f)

    packet_hash = mapping_data["human_review_packet_hash"]

    # Construct synthetic valid decision for all 20 candidates
    synthetic_decisions = []
    for idx, m in enumerate(mapping_data["mappings"]):
        h_id = m["review_id"]
        cand_id = m["candidate_id"]
        orig_ann = next(a for a in baseline_manifest.annotations if a.annotation_id == cand_id)

        if idx == 0:
            # Revised start boundary and revised role for first candidate
            dec = {
                "review_id": h_id,
                "candidate_id": cand_id,
                "piece_id": m["piece_id"],
                "decision": {
                    "is_thematic_statement": "YES",
                    "start_boundary": "CHANGE",
                    "revised_start_measure": 2,
                    "revised_start_offset": "0",
                    "end_boundary": "ACCEPT",
                    "revised_end_measure": None,
                    "revised_end_offset": None,
                    "theme_role": "MOTTO",
                    "confidence": 3,
                    "notes": "Synthetic test revision.",
                },
            }
        else:
            # Accepted candidate matching original role
            dec = {
                "review_id": h_id,
                "candidate_id": cand_id,
                "piece_id": m["piece_id"],
                "decision": {
                    "is_thematic_statement": "YES",
                    "start_boundary": "ACCEPT",
                    "revised_start_measure": None,
                    "revised_start_offset": None,
                    "end_boundary": "ACCEPT",
                    "revised_end_measure": None,
                    "revised_end_offset": None,
                    "theme_role": orig_ann.theme_role.value,
                    "confidence": 3,
                    "notes": "Synthetic test acceptance.",
                },
            }
        synthetic_decisions.append(dec)

    synthetic_data = {
        "human_review_packet_hash": packet_hash,
        "reviewer_provenance": {
            "reviewer_id": "expert_human_01",
            "reviewer_type": "HUMAN",
            "review_completed_at": "2026-09-13T00:00:00Z",
            "declaration": "I certify this is an independent human review.",
        },
        "candidate_decisions": synthetic_decisions,
    }

    valid, errors = validate_human_decision_file(synthetic_data, mapping_data)
    assert valid, f"Synthetic decision failed validation: {errors}"

    adjudicated_set = process_adjudicated_annotations(synthetic_data, mapping_data, baseline_manifest)

    # Total annotations should now be 21 (20 original + 1 revised child annotation)
    assert len(adjudicated_set.annotations) == 21

    # Original AI candidate must remain intact
    target_cand_id = mapping_data["mappings"][0]["candidate_id"]
    orig_matches = [a for a in adjudicated_set.annotations if a.annotation_id == target_cand_id]
    assert len(orig_matches) == 1
    assert orig_matches[0].annotator_type == AnnotatorType.ALGORITHM_CANDIDATE

    # Child annotation should exist with revised start measure 2 and role MOTTO
    child_matches = [a for a in adjudicated_set.annotations if a.annotator_type == AnnotatorType.HUMAN]
    assert len(child_matches) == 1
    child_ann = child_matches[0]
    assert child_ann.span.start.measure_index == 2
    assert child_ann.theme_role == ThemeRole.MOTTO
    assert child_ann.annotator_id == "expert_human_01"
