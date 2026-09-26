"""Strengthened regression tests for reviewer independence, SHA binding, and composer pool."""

from __future__ import annotations

import json
from pathlib import Path

from russian_piano_composer.corpus.rc013_composer_pool import (
    derive_russian_composer_pool,
)
from russian_piano_composer.corpus.rc013_review_ingestion import (
    validate_and_ingest_human_review_packet,
)


def test_composer_pool_derivation_baseline() -> None:
    """Proves that baseline N_Russian = 2 is strictly Scriabin + Mussorgsky."""
    res = derive_russian_composer_pool(
        arensky_verified_count=0,
        lyapunov_verified_count=0,
        lyadov_verified_count=0,
    )
    assert res.n_russian == 2
    assert res.n_control == 5
    assert res.qualified_russian_composers == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert res.unqualified_russian_composers == ["Anatoly Lyadov", "Anton Arensky", "Sergei Lyapunov"]
    assert res.rc012_resumption_status == "BLOCKED"
    assert "N_Russian = 2 < 4" in res.rc012_resumption_reason


def test_composer_pool_cannot_claim_lyadov_or_lyapunov_as_baseline() -> None:
    """Proves that Lyadov and Lyapunov cannot be claimed as qualified without verified scores."""
    res = derive_russian_composer_pool(
        arensky_verified_count=0,
        lyapunov_verified_count=0,
        lyadov_verified_count=0,
    )
    rec_lyadov = res.composer_records["Anatoly Lyadov"]
    rec_lyap = res.composer_records["Sergei Lyapunov"]
    assert rec_lyadov.qualification_status == "UNQUALIFIED"
    assert rec_lyap.qualification_status == "UNQUALIFIED"
    assert "Anatoly Lyadov" not in res.qualified_russian_composers
    assert "Sergei Lyapunov" not in res.qualified_russian_composers


def test_composer_pool_arensky_qualification_requires_three_scores() -> None:
    """Proves that Arensky requires >= 3 verified scores to establish pilot source fidelity, while N_Russian remains 2 without M_c >= 10."""
    # 2 verified scores -> pilot unvalidated, confirmatory ineligible
    res_partial = derive_russian_composer_pool(arensky_verified_count=2)
    assert res_partial.n_russian == 2
    assert "Anton Arensky" not in res_partial.qualified_russian_composers
    assert res_partial.composer_records["Anton Arensky"].pilot_status == "PILOT_UNVALIDATED"
    assert res_partial.composer_records["Anton Arensky"].confirmatory_status == "CONFIRMATORY_INELIGIBLE"
    assert res_partial.rc012_resumption_status == "BLOCKED"

    # 3 verified scores -> PILOT_SOURCE_FIDELITY_ESTABLISHED, but N_Russian remains 2 because M_c = 3 < 10
    res_full = derive_russian_composer_pool(arensky_verified_count=3)
    assert res_full.n_russian == 2
    assert "Anton Arensky" not in res_full.qualified_russian_composers
    assert res_full.composer_records["Anton Arensky"].pilot_status == "PILOT_SOURCE_FIDELITY_ESTABLISHED"
    assert res_full.composer_records["Anton Arensky"].confirmatory_status == "CONFIRMATORY_INELIGIBLE"
    assert res_full.composer_records["Anton Arensky"].qualification_status == "UNQUALIFIED"
    assert res_full.rc012_resumption_status == "BLOCKED"



def test_all_nine_pilot_review_packets_exist_and_are_blank() -> None:
    """Verifies that all 9 pilot scores have blank review packets with status PENDING_INDEPENDENT_HUMAN_REVIEW."""
    packet_files = [
        ("anton_arensky_op36_no01.review_packet.json", 36),
        ("anton_arensky_op36_no02.review_packet.json", 102),
        ("anton_arensky_op36_no13.review_packet.json", 60),
        ("anatoly_lyadov_op40_no02.review_packet.json", 32),
        ("anatoly_lyadov_op40_no03.review_packet.json", 23),
        ("anatoly_lyadov_op46_no04.review_packet.json", 45),
        ("sergei_lyapunov_op11_no01.review_packet.json", 64),
        ("sergei_lyapunov_op11_no02.review_packet.json", 168),
        ("sergei_lyapunov_op11_no03.review_packet.json", 114),
    ]
    packets_dir = Path("data/reviews/rc013/packets")
    for filename, expected_mm in packet_files:
        p = packets_dir / filename
        assert p.exists(), f"Missing review packet: {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["packet_status"] == "PENDING_INDEPENDENT_HUMAN_REVIEW"
        assert data["header"]["total_measures"] == expected_mm
        assert len(data["measures"]) == expected_mm
        assert data["reviewer_declaration"]["reviewer_identifier"] is None


def test_review_packet_ingestion_rejects_ai_or_agent_reviewer(tmp_path: Path) -> None:
    """Proves that AI or Agent cannot be an authorized human reviewer."""
    packet_path = Path("data/reviews/rc013/packets/anton_arensky_op36_no01.review_packet.json")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    # Attempt to set AI / Agent reviewer
    packet["reviewer_declaration"]["reviewer_identifier"] = "Antigravity_AI"
    packet["reviewer_declaration"]["reviewer_role"] = "AI_REVIEWER"
    packet["reviewer_declaration"]["review_completion_timestamp"] = "2026-09-21T00:00:00Z"

    mutated = tmp_path / "ai_packet.json"
    mutated.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    res = validate_and_ingest_human_review_packet(
        str(mutated),
        canonical_source_sha=packet["header"]["source_file_sha256"],
        current_symbolic_sha=packet["header"]["candidate_symbolic_sha256"],
    )
    assert res.valid is False
    assert any("cannot be an AI/automated agent" in e or "DISALLOWED_REVIEWER_TYPE" in e for e in res.errors)


def test_review_packet_ingestion_rejects_self_certification(tmp_path: Path) -> None:
    """Proves that reviewer == transcriber fails closed."""
    packet_path = Path("data/reviews/rc013/packets/anton_arensky_op36_no01.review_packet.json")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    packet["reviewer_declaration"]["reviewer_identifier"] = "same_person"
    packet["reviewer_declaration"]["transcriber_identifier"] = "same_person"
    packet["reviewer_declaration"]["reviewer_role"] = "INDEPENDENT_HUMAN_REVIEWER"
    packet["reviewer_declaration"]["review_completion_timestamp"] = "2026-09-21T00:00:00Z"

    mutated = tmp_path / "self_cert.json"
    mutated.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    res = validate_and_ingest_human_review_packet(
        str(mutated),
        canonical_source_sha=packet["header"]["source_file_sha256"],
        current_symbolic_sha=packet["header"]["candidate_symbolic_sha256"],
        transcriber_identifier="same_person",
    )
    assert res.valid is False
    assert any("SELF_CERTIFICATION_DISALLOWED" in e for e in res.errors)


def test_review_packet_ingestion_invalidated_by_symbolic_sha_drift(tmp_path: Path) -> None:
    """Proves that changing even one byte of symbolic MusicXML invalidates review packet."""
    packet_path = Path("data/reviews/rc013/packets/anton_arensky_op36_no01.review_packet.json")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    mutated = tmp_path / "drift.json"
    mutated.write_text(json.dumps(packet, indent=2), encoding="utf-8")

    res = validate_and_ingest_human_review_packet(
        str(mutated),
        canonical_source_sha=packet["header"]["source_file_sha256"],
        current_symbolic_sha="0" * 64,  # Live MusicXML changed after review
    )
    assert res.valid is False
    assert res.status == "STALE_AFTER_SYMBOLIC_CHANGE"
    assert any("STALE_AFTER_SYMBOLIC_CHANGE" in e for e in res.errors)
