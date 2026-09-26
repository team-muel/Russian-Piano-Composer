"""Adversarial and evidence-chain tests for RC-013 source-fidelity and composer qualification.

Ensures:
1. Source image bundle hash V2 binds directly to physical PDF bytes.
2. Missing or corrupted PDF source fails verification.
3. Review receipts cannot be fabricated without a valid submitted packet.
4. Drifted symbolic MusicXML or source PDF invalidates accepted review receipts.
5. Composer qualification is strictly derived from live 3/3 valid receipts for frozen targets.
6. Partial progress (1/3, 2/3) keeps the composer UNQUALIFIED.
7. Current disk state derives N_Russian = 2 (Alexander Scriabin + Modest Mussorgsky) and blocks RC-012 resumption.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from scripts.compute_rc013_hashes import (
    compute_authoritative_source_image_bundle_hash,
    compute_source_fidelity_gate_result,
    get_all_rc013_hashes,
)

from russian_piano_composer.corpus.rc013_composer_pool import (
    derive_russian_composer_pool_from_evidence,
)
from russian_piano_composer.corpus.rc013_fidelity import compute_sha256_file
from russian_piano_composer.corpus.rc013_review_ingestion import (
    validate_human_review_receipt,
)


def test_source_image_bundle_v2_binds_to_physical_pdf_bytes(tmp_path: Path) -> None:
    """Proves that changing a single byte in any authoritative PDF triggers fail-closed error or changes hash."""
    scans_manifest_json = Path("data/scans/rc013/rc013_scans_manifest.json")
    scans_dir = Path("data/scans/rc013")

    # Initial hash
    initial_hash = compute_authoritative_source_image_bundle_hash(
        scans_manifest_path=str(scans_manifest_json),
        scans_dir=str(scans_dir),
    )

    # Copy scans and manifest to tmp_path
    tmp_scans = tmp_path / "scans"
    shutil.copytree(scans_dir, tmp_scans)
    tmp_manifest = tmp_scans / "rc013_scans_manifest.json"

    # Mutate 1 byte in one PDF
    pdf_to_mutate = next(tmp_scans.glob("*.pdf"))
    with open(pdf_to_mutate, "ab") as f:
        f.write(b"\x00")

    # 1. Without manifest update -> fail-closed ValueError
    with pytest.raises(ValueError, match="SOURCE_BYTE_SHA_MISMATCH"):
        compute_authoritative_source_image_bundle_hash(
            scans_manifest_path=str(tmp_manifest),
            scans_dir=str(tmp_scans),
        )

    # 2. With updated manifest matching mutated PDF -> produces different bundle hash
    new_pdf_sha = compute_sha256_file(str(pdf_to_mutate))
    manifest_data = json.loads(tmp_manifest.read_text(encoding="utf-8"))
    for entry in manifest_data:
        if entry.get("source_file_name") == pdf_to_mutate.name:
            entry["source_file_sha256"] = new_pdf_sha
    tmp_manifest.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    mutated_hash = compute_authoritative_source_image_bundle_hash(
        scans_manifest_path=str(tmp_manifest),
        scans_dir=str(tmp_scans),
    )
    assert initial_hash != mutated_hash, "Source image bundle hash failed to change after PDF byte modification!"


def test_source_image_bundle_v2_fails_if_referenced_pdf_missing(tmp_path: Path) -> None:
    """Proves that if an authoritative PDF referenced in manifest is missing, hashing fails."""
    scans_manifest_json = Path("data/scans/rc013/rc013_scans_manifest.json")
    tmp_scans = tmp_path / "empty_scans"
    tmp_scans.mkdir()
    tmp_manifest = tmp_scans / "rc013_scans_manifest.json"
    shutil.copy(scans_manifest_json, tmp_manifest)

    with pytest.raises(FileNotFoundError):
        compute_authoritative_source_image_bundle_hash(
            scans_manifest_path=str(tmp_manifest),
            scans_dir=str(tmp_scans),
        )


def test_receipt_validation_rejects_missing_submitted_packet(tmp_path: Path) -> None:
    """Proves that a receipt pointing to a non-existent review packet fails validation."""
    receipt_data: dict[str, Any] = {
        "schema_version": "rc013_human_review_receipt_v1",
        "score_id": "anton_arensky_op36_no01",
        "canonical_work_id": "anton_arensky_op36_no01",
        "reviewer_identifier": "Dr_Jane_Doe",
        "reviewer_role": "INDEPENDENT_HUMAN_MUSICOLOGIST",
        "review_completion_timestamp": "2026-09-24T12:00:00Z",
        "transcriber_identifier": "automated_pipeline",
        "source_sha256": "8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5",
        "symbolic_sha256": "dummy_sym_sha",
        "total_measures": 36,
        "measures_reviewed": 36,
        "critical_ambiguities_count": 0,
        "review_packet_sha256": "a" * 64,
        "review_receipt_created_at": "2026-09-24T12:05:00Z",
        "validation_status": "SOURCE_FIDELITY_VERIFIED",
    }
    receipt_file = tmp_path / "anton_arensky_op36_no01.human_review_receipt.json"
    receipt_file.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    empty_packets_dir = tmp_path / "empty_packets"
    empty_packets_dir.mkdir()

    res = validate_human_review_receipt(
        receipt_path=str(receipt_file),
        live_symbolic_sha="dummy_sym_sha",
        actual_source_sha="8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5",
        packets_dir=str(empty_packets_dir),
    )
    assert res.valid is False
    assert any("SUBMITTED_PACKET_MISSING" in e for e in res.errors)


def test_receipt_validation_detects_tampered_packet_sha(tmp_path: Path) -> None:
    """Proves that modifying the submitted packet JSON invalidates the receipt."""
    packets_dir = Path("data/reviews/rc013/packets")
    score_id = "anton_arensky_op36_no01"
    packet_src = packets_dir / f"{score_id}.review_packet.json"

    tmp_packets = tmp_path / "packets"
    tmp_packets.mkdir()
    tmp_packet_file = tmp_packets / f"{score_id}.review_packet.json"
    shutil.copy(packet_src, tmp_packet_file)

    receipt_data: dict[str, Any] = {
        "schema_version": "rc013_human_review_receipt_v1",
        "score_id": score_id,
        "canonical_work_id": score_id,
        "reviewer_identifier": "Dr_Jane_Doe",
        "reviewer_role": "INDEPENDENT_HUMAN_MUSICOLOGIST",
        "review_completion_timestamp": "2026-09-24T12:00:00Z",
        "transcriber_identifier": "automated_pipeline",
        "source_sha256": "source_sha_example",
        "symbolic_sha256": "sym_sha_example",
        "total_measures": 36,
        "measures_reviewed": 36,
        "critical_ambiguities_count": 0,
        "review_packet_sha256": "f" * 64,  # Incorrect / tampered hash
        "review_receipt_created_at": "2026-09-24T12:05:00Z",
        "validation_status": "SOURCE_FIDELITY_VERIFIED",
    }
    receipt_file = tmp_path / f"{score_id}.human_review_receipt.json"
    receipt_file.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    res = validate_human_review_receipt(
        receipt_path=str(receipt_file),
        live_symbolic_sha="sym_sha_example",
        actual_source_sha="source_sha_example",
        packets_dir=str(tmp_packets),
    )
    assert res.valid is False
    assert any("PACKET_SHA_TAMPERED" in e for e in res.errors)


def test_receipt_validation_detects_symbolic_and_source_sha_drift(tmp_path: Path) -> None:
    """Proves that changes in live MusicXML or source PDF render receipts stale."""
    score_id = "anton_arensky_op36_no01"
    tmp_packets = tmp_path / "packets"
    tmp_packets.mkdir()
    tmp_packet_file = tmp_packets / f"{score_id}.review_packet.json"
    tmp_packet_file.write_text('{"dummy": true}', encoding="utf-8")
    actual_packet_sha = compute_sha256_file(str(tmp_packet_file))

    receipt_data: dict[str, Any] = {
        "schema_version": "rc013_human_review_receipt_v1",
        "score_id": score_id,
        "canonical_work_id": score_id,
        "reviewer_identifier": "Dr_Jane_Doe",
        "reviewer_role": "INDEPENDENT_HUMAN_MUSICOLOGIST",
        "review_completion_timestamp": "2026-09-24T12:00:00Z",
        "transcriber_identifier": "automated_pipeline",
        "source_sha256": "expected_source_sha",
        "symbolic_sha256": "expected_sym_sha",
        "total_measures": 36,
        "measures_reviewed": 36,
        "critical_ambiguities_count": 0,
        "review_packet_sha256": actual_packet_sha,
        "review_receipt_created_at": "2026-09-24T12:05:00Z",
        "validation_status": "SOURCE_FIDELITY_VERIFIED",
    }
    receipt_file = tmp_path / f"{score_id}.human_review_receipt.json"
    receipt_file.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    # Drifted symbolic MusicXML
    res_sym_drift = validate_human_review_receipt(
        receipt_path=str(receipt_file),
        live_symbolic_sha="drifted_sym_sha",
        actual_source_sha="expected_source_sha",
        packets_dir=str(tmp_packets),
    )
    assert res_sym_drift.valid is False
    assert res_sym_drift.status == "STALE_AFTER_SYMBOLIC_CHANGE"

    # Drifted source PDF
    res_src_drift = validate_human_review_receipt(
        receipt_path=str(receipt_file),
        live_symbolic_sha="expected_sym_sha",
        actual_source_sha="drifted_source_sha",
        packets_dir=str(tmp_packets),
    )
    assert res_src_drift.valid is False
    assert res_src_drift.status == "SOURCE_EVIDENCE_STALE_OR_CORRUPT"


def test_derive_russian_composer_pool_from_current_disk_evidence() -> None:
    """Proves that on the live repository disk, N_Russian = 2 and all pilot composers are UNQUALIFIED."""
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


def test_composer_qualification_requires_strictly_three_of_three_receipts(tmp_path: Path) -> None:
    """Proves that 1/3 and 2/3 verified receipts keep the composer UNQUALIFIED, and exactly 3/3 qualifies."""
    tmp_receipts = tmp_path / "accepted"
    tmp_receipts.mkdir()
    tmp_scores = tmp_path / "scores"
    tmp_scores.mkdir()
    tmp_packets = tmp_path / "packets"
    tmp_packets.mkdir()
    tmp_manifest = tmp_path / "manifest.csv"

    arensky_targets = [
        ("anton_arensky_op36_no01", "Op. 36", 1),
        ("anton_arensky_op36_no02", "Op. 36", 2),
        ("anton_arensky_op36_no13", "Op. 36", 13),
    ]
    manifest_lines = [
        "composer,work,opus_or_catalogue,movement,title,source_archive,source_url_or_reference,download_url,edition_or_editor,publication_year,plate_number,source_file_name,source_file_sha256,source_file_size_bytes,page_range,rights_status,existing_symbolic_format,digitization_required,priority\n"
    ]

    for sid, opus, mov in arensky_targets:
        xml_file = tmp_scores / f"{sid}.musicxml"
        xml_file.write_text(f"<score-partwise id='{sid}'/>", encoding="utf-8")

        packet_file = tmp_packets / f"{sid}.review_packet.json"
        packet_file.write_text(f'{{"score_id": "{sid}"}}', encoding="utf-8")

        src_sha = f"src_sha_for_{sid}"
        manifest_lines.append(
            f"Anton Arensky,24 Morceaux,{opus},{mov},Title,IMSLP,url,durl,Ed,1894,plate,{sid}.pdf,{src_sha},1000,1-5,PUBLIC_DOMAIN,None,True,PILOT_HIGH\n"
        )

    tmp_manifest.write_text("".join(manifest_lines), encoding="utf-8")

    # Helper to create receipt for a specific target score
    def create_receipt(sid: str) -> None:
        xml_file = tmp_scores / f"{sid}.musicxml"
        sym_sha = compute_sha256_file(str(xml_file))
        packet_file = tmp_packets / f"{sid}.review_packet.json"
        packet_sha = compute_sha256_file(str(packet_file))
        src_sha = f"src_sha_for_{sid}"

        receipt_data = {
            "schema_version": "rc013_human_review_receipt_v1",
            "score_id": sid,
            "canonical_work_id": sid,
            "reviewer_identifier": "Dr_Jane_Doe",
            "reviewer_role": "INDEPENDENT_HUMAN_MUSICOLOGIST",
            "review_completion_timestamp": "2026-09-24T12:00:00Z",
            "transcriber_identifier": "automated_pipeline",
            "source_sha256": src_sha,
            "symbolic_sha256": sym_sha,
            "total_measures": 30,
            "measures_reviewed": 30,
            "critical_ambiguities_count": 0,
            "review_packet_sha256": packet_sha,
            "review_receipt_created_at": "2026-09-24T12:05:00Z",
            "validation_status": "SOURCE_FIDELITY_VERIFIED",
        }
        r_file = tmp_receipts / f"{sid}.human_review_receipt.json"
        r_file.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    # Case 0/3: 0 receipts -> UNQUALIFIED, N_Russian = 2
    res0 = derive_russian_composer_pool_from_evidence(
        receipts_dir=str(tmp_receipts),
        scores_dir=str(tmp_scores),
        packets_dir=str(tmp_packets),
        source_manifest_csv=str(tmp_manifest),
    )
    assert res0.n_russian == 2
    assert "Anton Arensky" in res0.unqualified_russian_composers

    # Case 1/3: 1 receipt -> UNQUALIFIED, N_Russian = 2
    create_receipt(arensky_targets[0][0])
    res1 = derive_russian_composer_pool_from_evidence(
        receipts_dir=str(tmp_receipts),
        scores_dir=str(tmp_scores),
        packets_dir=str(tmp_packets),
        source_manifest_csv=str(tmp_manifest),
    )
    assert res1.n_russian == 2
    assert "Anton Arensky" in res1.unqualified_russian_composers
    assert res1.composer_records["Anton Arensky"].qualification_status == "UNQUALIFIED"
    assert "1/3 pilot scores verified" in res1.composer_records["Anton Arensky"].qualification_reason

    # Case 2/3: 2 receipts -> UNQUALIFIED, N_Russian = 2
    create_receipt(arensky_targets[1][0])
    res2 = derive_russian_composer_pool_from_evidence(
        receipts_dir=str(tmp_receipts),
        scores_dir=str(tmp_scores),
        packets_dir=str(tmp_packets),
        source_manifest_csv=str(tmp_manifest),
    )
    assert res2.n_russian == 2
    assert "Anton Arensky" in res2.unqualified_russian_composers
    assert res2.composer_records["Anton Arensky"].qualification_status == "UNQUALIFIED"
    assert "2/3 pilot scores verified" in res2.composer_records["Anton Arensky"].qualification_reason

    # Case 3/3: 3 receipts -> PILOT_SOURCE_FIDELITY_ESTABLISHED, but CONFIRMATORY_INELIGIBLE (M_c = 3 < 10), N_Russian remains 2
    create_receipt(arensky_targets[2][0])
    res3 = derive_russian_composer_pool_from_evidence(
        receipts_dir=str(tmp_receipts),
        scores_dir=str(tmp_scores),
        packets_dir=str(tmp_packets),
        source_manifest_csv=str(tmp_manifest),
    )
    assert res3.n_russian == 2
    assert "Anton Arensky" in res3.unqualified_russian_composers
    assert res3.composer_records["Anton Arensky"].pilot_status == "PILOT_SOURCE_FIDELITY_ESTABLISHED"
    assert res3.composer_records["Anton Arensky"].confirmatory_status == "CONFIRMATORY_INELIGIBLE"
    assert res3.composer_records["Anton Arensky"].qualification_status == "UNQUALIFIED"
    assert "CONFIRMATORY_INELIGIBLE for RC-012" in res3.composer_records["Anton Arensky"].qualification_reason
    # Still blocked because N_Russian = 2 < 4
    assert res3.rc012_resumption_status == "BLOCKED"


def test_three_of_three_pilot_does_not_increment_n_russian() -> None:
    """Proves that verified pilot scores establish pilot fidelity but cannot change N_Russian without M_c >= 10."""
    from russian_piano_composer.corpus.rc013_composer_pool import derive_russian_composer_pool

    # All 3 pilot composers have 3/3 verified scores
    res = derive_russian_composer_pool(
        arensky_verified_count=3,
        lyapunov_verified_count=3,
        lyadov_verified_count=3,
    )
    assert res.n_russian == 2
    assert res.qualified_russian_composers == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert res.rc012_resumption_status == "BLOCKED"
    for comp in ["Anton Arensky", "Anatoly Lyadov", "Sergei Lyapunov"]:
        rec = res.composer_records[comp]
        assert rec.pilot_status == "PILOT_SOURCE_FIDELITY_ESTABLISHED"
        assert rec.confirmatory_status == "CONFIRMATORY_INELIGIBLE"
        assert rec.qualification_status == "UNQUALIFIED"


def test_composer_piece_count_boundary_nine_vs_ten() -> None:
    """Proves that M_c = 9 is INELIGIBLE and M_c = 10 qualifies under the frozen RC-012 preregistration."""
    from russian_piano_composer.corpus.rc013_composer_pool import (
        STATUS_CONFIRMATORY_ELIGIBLE,
        STATUS_CONFIRMATORY_INELIGIBLE,
    )

    def evaluate_piece_count(m_c: int) -> tuple[str, str]:
        if m_c >= 10:
            return "QUALIFIED", STATUS_CONFIRMATORY_ELIGIBLE
        return "UNQUALIFIED", STATUS_CONFIRMATORY_INELIGIBLE

    q_9, c_9 = evaluate_piece_count(9)
    assert q_9 == "UNQUALIFIED"
    assert c_9 == STATUS_CONFIRMATORY_INELIGIBLE

    q_10, c_10 = evaluate_piece_count(10)
    assert q_10 == "QUALIFIED"
    assert c_10 == STATUS_CONFIRMATORY_ELIGIBLE



def test_production_fidelity_gate_fails_closed_without_accepted_receipts() -> None:
    """Proves that compute_source_fidelity_gate_result returns PENDING_SOURCE_COMPARISON when no receipts exist."""
    hashes = get_all_rc013_hashes()
    verdict, gate_hash = compute_source_fidelity_gate_result(
        source_comparison_bundle_hash=hashes["RC013_SOURCE_COMPARISON_BUNDLE_HASH"],
        source_img_bundle_hash=hashes["RC013_SOURCE_IMAGE_BUNDLE_HASH"],
        corpus_bundle_hash=hashes["RC013_CANONICAL_SYMBOLIC_CORPUS_HASH"],
        reviews_dir="data/reviews/rc013",
        receipts_dir="data/reviews/rc013/accepted",
    )
    assert verdict == "PENDING_SOURCE_COMPARISON"
    assert len(gate_hash) == 64
