from __future__ import annotations

import json
from pathlib import Path

from russian_piano_composer.corpus.rc013_integrity import (
    load_identity_map,
    validate_canonical_score_integrity,
    validate_identity_fields,
)

IDENTITY_MAP = "data/manifests/rc013_arensky_identity_map.json"


def test_authoritative_arensky_identities_are_frozen() -> None:
    identity = load_identity_map(IDENTITY_MAP)
    assert identity["movements"]["1"]["title"] == "Prélude"
    assert identity["movements"]["1"]["key"] == "C major"
    assert identity["movements"]["1"]["tempo"] == "Adagio non troppo"
    assert identity["movements"]["2"]["title"] == "La toupie"
    assert identity["movements"]["2"]["key"] == "C minor"
    assert identity["movements"]["2"]["tempo"] == "Vivace"
    assert identity["movements"]["13"]["title"] == "Étude"
    assert identity["movements"]["13"]["key"] == "F-sharp major"
    assert identity["movements"]["13"]["tempo"] == "Moderato"


def test_score2_source_bundle_is_nos_1_6_not_nos_7_12() -> None:
    identity = load_identity_map(IDENTITY_MAP)
    no2 = identity["movements"]["2"]
    assert no2["source_file_sha256"] == (
        "d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855"
    )
    assert no2["superseded_wrong_binding"]["sha256"] == (
        "f98061b4097b216aa4fa47b985b3c8addd83218358edf1370a8748a67056a136"
    )


def test_current_arensky_candidates_satisfy_identity_integrity() -> None:
    """Verifies all recovered authentic Arensky scores pass canonical integrity and identity checks."""
    for score_id in (
        "anton_arensky_op36_no01",
        "anton_arensky_op36_no02",
        "anton_arensky_op36_no13",
    ):
        result = validate_canonical_score_integrity(score_id)
        assert result.artifact_consistent is True, (score_id, result.errors)
        assert result.identity_required is True
        assert result.identity_valid is True, (score_id, result.errors)
        assert result.status == "PASS"


def test_wrong_work_identity_cannot_pass_even_when_source_matches() -> None:
    expected = load_identity_map(IDENTITY_MAP)["movements"]["2"]
    errors = validate_identity_fields(
        expected,
        movement=2,
        title="La toupie",
        key_fifths=-4,
        source_file_sha256=expected["source_file_sha256"],
    )
    assert any(e.startswith("IDENTITY_KEY_MISMATCH") for e in errors)


def test_cross_artifact_symbolic_sha_drift_fails(tmp_path: Path) -> None:
    src = Path("data/reviews/rc013/anton_arensky_op36_no02.review.json")
    review = json.loads(src.read_text(encoding="utf-8"))
    review["symbolic_file_sha256"] = "0" * 64
    mutated = tmp_path / "review.json"
    mutated.write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    result = validate_canonical_score_integrity(
        "anton_arensky_op36_no02",
        review_path=str(mutated),
    )
    assert result.artifact_consistent is False
    assert result.status == "CROSS_ARTIFACT_INTEGRITY_FAILED"
    assert any(
        e.startswith("CROSS_SYMBOLIC_SHA_MISMATCH:review")
        for e in result.errors
    )


def test_candidate_generators_are_quarantined() -> None:
    score2 = Path("scripts/transcribe_arensky_op36_no02.py").read_text(
        encoding="utf-8"
    )
    pilot = Path("scripts/transcribe_rc013_pilot_scores.py").read_text(
        encoding="utf-8"
    )
    assert "TRANSCRIPTION_CANDIDATE_GENERATOR_ONLY = True" in score2
    assert "QUARANTINED: this candidate generator may not write" in score2
    assert "TRANSCRIPTION_CANDIDATE_GENERATOR_ONLY = True" in pilot
    assert "CANONICAL_RC013_DIR" in pilot
    assert "template-generated candidates may not be written" in pilot


def test_cross_document_identity_consistency() -> None:
    """Verifies all RC-013 manifests and docs strictly agree on frozen identity metadata."""
    # 1. Identity Map
    id_map = json.loads(Path(IDENTITY_MAP).read_text(encoding="utf-8"))
    assert id_map["first_edition"]["plate_range"] == "19599-19624"
    assert id_map["movements"]["1"]["key"] == "C major"
    assert id_map["movements"]["1"]["pdf_page_range"] == "1-4 (1-based bundle pages)"
    assert id_map["movements"]["1"]["printed_page_range"] == "4-7"
    assert id_map["movements"]["2"]["key"] == "C minor"
    assert id_map["movements"]["2"]["pdf_page_range"] == "5-12 (1-based bundle pages)"
    assert id_map["movements"]["2"]["printed_page_range"] == "8-15"
    assert id_map["movements"]["13"]["key"] == "F-sharp major"
    assert id_map["movements"]["13"]["pdf_page_range"] == "1-7 (1-based bundle pages)"
    assert id_map["movements"]["13"]["printed_page_range"] == "61-67"
    assert id_map["movements"]["13"]["boundary_audit"]["measure_count"] == 60

    # 2. Source Candidates CSV
    csv_text = Path("data/manifests/rc013_source_candidates.csv").read_text(encoding="utf-8")
    assert "Arensky_morceaux_op36-1.pdf,d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855,1506575,\"PDF 1-4 / printed 4-7\"" in csv_text
    assert "Arensky_morceaux_op36-1.pdf,d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855,1506575,\"PDF 5-12 / printed 8-15\"" in csv_text
    assert "Arensky_Morceaux_op.36_No.13-18.pdf,eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5,2571253,\"PDF 1-7 / printed 61-67\"" in csv_text

    # 3. Scans Manifest JSON
    scans_manifest = json.loads(Path("data/scans/rc013/rc013_scans_manifest.json").read_text(encoding="utf-8"))
    arensky_scans = {m["movement"]: m for m in scans_manifest if m.get("composer") == "Anton Arensky"}
    assert arensky_scans[1]["expected_key"] == "C major"
    assert arensky_scans[1]["page_range"] == "PDF 1-4 / printed 4-7"
    assert arensky_scans[2]["expected_key"] == "C minor"
    assert arensky_scans[2]["page_range"] == "PDF 5-12 / printed 8-15"
    assert arensky_scans[13]["expected_key"] == "F-sharp major"
    assert arensky_scans[13]["page_range"] == "PDF 1-7 / printed 61-67"

    # 4. Source Inventory Markdown
    inv_text = Path("docs/research/RC013_SOURCE_INVENTORY.md").read_text(encoding="utf-8")
    assert "Prélude* in C major" in inv_text
    assert "La toupie* in C minor" in inv_text
    assert "Étude* in F-sharp major" in inv_text
    assert "pp. 61\u201367 (PDF 1\u20137" in inv_text

    # 5. Final Decision Report Markdown
    dec_text = Path("docs/research/RC013_FINAL_DECISION_REPORT.md").read_text(encoding="utf-8")
    assert "C major" in dec_text
    assert "C minor" in dec_text
    assert "F-sharp major" in dec_text
    assert "NOT ACCEPTED" in dec_text
    assert "BLOCKED (N_Russian = 2 < 4)" in dec_text

